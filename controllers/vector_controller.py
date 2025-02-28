from fastapi import HTTPException

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import config
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId

from llm import LLMGenerator

#TODO: parse the pdf; save the full json and add some insights as the vector_db

class VectorController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.client = MongoClient(config.MONGODB_URI)
        self.db = self.client[config.DATABASE]
        self.adb = db
        self.acollection = self.adb.get_collection("cv")
        self.collection = self.db.get_collection("vectorstore")

        self.embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Initialize vector store with proper configuration
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embedding,
            index_name="default",  # Make sure this matches your Atlas search index
            embedding_key="embedding",  # The field name for the embedding vector
            text_key="text",  # The field name for the text content
            metadata_key="metadata"  # The field name for metadata
        )

    #load the pdf
    def load_pdf(self, document_url: str):
        pdf_loader = PyPDFLoader(document_url)
        splitter = RecursiveCharacterTextSplitter()
        pdf_text = pdf_loader.load_and_split()
        final_text = "\n".join([p.page_content for p in pdf_text])
        
        if len(final_text) < 100:
            raise HTTPException(status_code=500, detail=f"Document is too short to Read. Please upload a document that contains text material.")
        
        return final_text

    def save_vector(self, cv, document_id: str):
        try:
            # Extract skills and experience for vector search
            content = cv.get("all_skills", "") + "\n"
            if "work_experience" in cv:
                for exp in cv["work_experience"]:
                    content += f"Experience: {exp.get('job_title', '')} at {exp.get('company_name', '')}\n"
                    if "responsibilities" in exp:
                        content += "Responsibilities:\n" + "\n".join(exp["responsibilities"]) + "\n"

            # Split content into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_text(content)

            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": document_id,
                        "chunk_id": i,
                        "source": "cv"
                    }
                )
                documents.append(doc)

            # Add documents to vector store
            self.vector_store.add_documents(documents)
            return True
        except Exception as e:
            print(f"Error saving vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving vector: {str(e)}")


    async def search(self, pdf_list, query: str, k=5):
        """Search through vectors using similarity search"""
        try:
            # Perform vector search with increased k if filtering will be applied
            k_search = k * 3 if pdf_list else k  # Get more results if we need to filter
            
            # Perform vector search
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k_search
            )
            
            # Process results
            search_results = {}
            for doc, score in results:
                doc_id = doc.metadata.get("doc_id")
                if not doc_id:
                    continue
                
                # Filter by pdf_list if provided
                if pdf_list and doc_id not in pdf_list:
                    continue
                
                try:
                    # Get full CV data
                    cv_data = await self.acollection.find_one({"_id": ObjectId(doc_id)})
                    if cv_data:
                        if doc_id not in search_results:
                            search_results[doc_id] = {
                                "similarity_score": float(score),
                                "parsed_cv": cv_data.get("parsed_cv", {}),
                                "matching_content": []
                            }
                        
                        # Add matching content
                        search_results[doc_id]["matching_content"].append({
                            "content": doc.page_content,
                            "score": float(score)
                        })
                        
                        # Break if we have enough results
                        if len(search_results) >= k:
                            break
                except Exception as e:
                    print(f"Error processing document {doc_id}: {str(e)}")
                    continue
            
            return search_results
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


    #parse the pdf and save the json in the database
    async def parse_pdf(self, document_url: str, document_id: str = None):
        """Parse PDF and return the structured data"""
        try:
            pdf_text = self.load_pdf(document_url)
            pdf_text = "<CV>" + pdf_text + "</CV>"
            result = await LLMGenerator().generate_parsed_cv(llm_type="cv_parser", cv=pdf_text, llm_name='gemini')
            
            # If document_id is provided, save vector embeddings
            if document_id:
                self.save_vector(result, document_id)
                
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing the PDF: {str(e)}")

    
    #save the parsed json in the database
    async def save_parsed_json(self, document_url: str, document_id: str):
        """Save parsed CV to database"""
        try:
            # Get the parsed data if not already parsed
            parsed_json = await self.parse_pdf(document_url, document_id)
            
            # Create the document for MongoDB
            parsed_cv = {
                "_id": ObjectId(document_id),
                "parsed_cv": parsed_json
            }

            # Save to MongoDB
            result = await self.acollection.insert_one(parsed_cv)
            
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving the parsed json: {str(e)}")


    async def delete_vector(self, document_id: str):
        try:
            self.collection.delete_many({"doc_id": document_id})
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Error deleting the vector. Details: {e}")


    async def delete_all_vectors(self):
        try:
            self.collection.delete_many({})
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Error deleting all vectors. Details: {e}")

    async def debug_vector_store(self):
        """Debug method to check vector store contents"""
        try:
            # Check vector store collection
            vector_count = self.collection.count_documents({})
            print(f"Vector store documents: {vector_count}")
            
            # Get a sample document
            sample = self.collection.find_one({})
            if sample:
                # Convert ObjectId to string and remove large embedding vectors
                sample_data = {
                    k: str(v) if isinstance(v, ObjectId) else v
                    for k, v in sample.items() 
                    if k not in ['embedding']  # Exclude the embedding vector
                }
            
            # Check CV collection
            cv_count = await self.acollection.count_documents({})
            print(f"CV collection documents: {cv_count}")
            
            return {
                "vector_store_count": vector_count,
                "cv_collection_count": cv_count,
                "sample_metadata": sample_data if sample else None
            }
        except Exception as e:
            print(f"Debug error: {str(e)}")
            return {"error": str(e)}
            