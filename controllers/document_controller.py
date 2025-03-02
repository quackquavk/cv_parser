import logging
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, File, UploadFile
from typing import List, Optional, Dict, Any
from bson.objectid import ObjectId

from models.document import Document, DocumentResponse

class DocumentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.get_collection("document")
        self.cv_collection = self.db.get_collection("cv")
        self.logger = logging.getLogger(__name__)

    def validate_document_name(self, document_name: str) -> bool:
        """Validate if the document is a PDF"""
        return document_name.lower().endswith('.pdf')

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = await self.cv_collection.find_one({"_id": ObjectId(document_id)})
            if result:
                result["id"] = str(result.pop("_id"))  # Convert _id to id
            return result
        except Exception as e:
            self.logger.error(f"Error getting document {document_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")
        
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        try:
            documents = await self.cv_collection.find({}, {"_id": 1, "parsed_cv": 1}).to_list(length=None)
            
            return [{"id": str(doc["_id"]), "parsed_cv": doc["parsed_cv"]} for doc in documents]
        except Exception as e:
            self.logger.error(f"Error getting all documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

        
    async def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search through all documents using vector search"""
        try:
            # Get all document IDs
            documents = await self.collection.find({}, {"_id": 1}).to_list(length=None)
            doc_ids = [str(doc["_id"]) for doc in documents]
            
            if not doc_ids:
                return []
            
            # Get the vector controller instance
            from database import database
            vector_controller = database.controller.vector_controller
            
            # Perform vector search
            results = await vector_controller.search(
                pdf_list=doc_ids,
                query=query
            )
            return results
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

    async def upload_document(self, database, folder_id: str, files: List[UploadFile]) -> Dict[str, Any]:
        """Upload and process documents"""
        try:
            results = []
            error_pdfs = []

            for file in files:
                try:
                    # Validate file
                    if not self.validate_document_name(file.filename):
                        error_pdfs.append(file.filename)
                        continue

                    document_id = ObjectId()
                    document_url = f"documents/{document_id}.pdf"
                    
                    # Ensure directory exists
                    os.makedirs("documents", exist_ok=True)
                    
                    # Save file permanently
                    with open(document_url, "wb") as f:
                        f.write(await file.read())

                    try:
                        # Create document record
                        document = Document(
                            id=str(document_id),
                            document_name=file.filename,
                            document_url=document_url,
                            folder_id=folder_id,
                        )

                        # Save document metadata
                        await self.collection.insert_one(document.model_dump(by_alias=True))

                        # Parse CV and save to database
                        parsed_cv = await database.controller.vector_controller.parse_pdf(document_url, str(document_id))
                        
                        # Save parsed CV and create vector embeddings
                        await database.controller.vector_controller.save_parsed_json(document_url, str(document_id))

                        # Add to results
                        results.append({
                            "filename": file.filename,
                            "document_id": str(document_id),
                            "parsed_cv": parsed_cv
                        })

                    except Exception as e:
                        # If anything fails after file creation, clean up
                        if os.path.exists(document_url):
                            os.remove(document_url)
                        await self.delete_document(str(document_id), database)
                        raise e

                except Exception as e:
                    self.logger.error(f"Error processing {file.filename}: {str(e)}")
                    error_pdfs.append(file.filename)

            if not results:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process any documents. Errors in: {', '.join(error_pdfs)}"
                )

            return {
                "results": results,
                "errors": error_pdfs if error_pdfs else None
            }

        except Exception as e:
            self.logger.error(f"Error in upload_document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_document(self, document_id: str, database) -> None:
        """Delete a document and its associated data"""
        try:
            # Delete file
            document = await self.collection.find_one({"_id": ObjectId(document_id)})
            if document and os.path.exists(document["document_url"]):
                os.remove(document["document_url"])

            # Delete from collections
            await self.collection.delete_one({"_id": ObjectId(document_id)})
            await self.cv_collection.delete_one({"_id": ObjectId(document_id)})
            
            # Delete vector embeddings
            await database.controller.vector_controller.delete_vector(document_id)

        except Exception as e:
            self.logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


