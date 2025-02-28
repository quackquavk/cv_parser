from http.client import responses

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import List, Optional
from database import database
from models.document import DocumentSearchRequest, DocumentList, Query as QueryModel

router = APIRouter()

@router.post("/upload")
async def upload_document(
    files: List[UploadFile] = File(...), 
    folder_id: Optional[str] = None
):
    """Upload and parse CV documents"""
    try:
        response = await database.controller.document_controller.upload_document(database, folder_id, files)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(query: DocumentSearchRequest):
    """Search through parsed CVs using semantic search"""
    try:
        results = await database.controller.document_controller.search_documents(query.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/bulk")
async def search_documents_bulk(document_list: DocumentList, query: str = Query(...)):
    """Search through a specific list of documents"""
    try:
        results = await database.controller.vector_controller.search(
            document_list.document_ids,
            query
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get a specific document's parsed data"""
    try:
        document = await database.controller.document_controller.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated data"""
    try:
        await database.controller.document_controller.delete_document(document_id, database)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
