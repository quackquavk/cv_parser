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

        self.embedding = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        self.vector_store = MongoDBAtlasVectorSearch(
            collection = self.collection,
            embedding = self.embedding,
            relevance_score_fn = "cosine",
            index_name = 'vector_index'
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
            imp_details = cv["all_skills"]
            if imp_details:
                splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
                pages = splitter.split_text(imp_details)
                met_pages = []
                for i, page in enumerate(pages):
                    metadata = {
                        "doc_id": document_id,
                        "length": len(page),
                        "page_no": i,
                    }
                    met_pages.append(Document(page_content = page, metadata = metadata))
                response = self.vector_store.add_documents(met_pages)
                return True
        except HTTPException as e:
            raise HTTPException(status_code= 500, detail = f"Error saving the vector. Details: {e}")


    async def search(self, pdf_list, query: str, k = 5):
        """Search through vectors using similarity search"""
        try:
            results = self.vector_store.similarity_search_with_score(
                query = query,
                k = k,
                pre_filter={"doc_id": {"$in": pdf_list}}
            )
            
            # Get full CV data for each result
            search_results = {}
            for doc, score in results:
                doc_id = doc.metadata["doc_id"]
                cv_data = await self.acollection.find_one({"_id": ObjectId(doc_id)})
                if cv_data:
                    search_results[doc_id] = {
                        "similarity_score": score,
                        "parsed_cv": cv_data.get("parsed_cv", {})
                    }
            
            return search_results
        except Exception as e:
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
            