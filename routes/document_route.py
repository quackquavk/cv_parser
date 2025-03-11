from http.client import responses
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Request
from typing import List, Optional
from database import database
from models.document import DocumentSearchRequest, DocumentList, Query as QueryModel
from utils.rate_limit import limiter

router = APIRouter()

@router.post("/upload")
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    files: List[UploadFile] = File(...), 
    folder_id: Optional[str] = None
):
    """Upload and parse CV documents"""
    try:
        response = await database.controller.document_controller.upload_document(database, folder_id, files)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
@limiter.limit("10/minute")
async def get_all_documents(request: Request):
    """Get all documents"""
    try:
        documents = await database.controller.document_controller.get_all_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
@limiter.limit("10/minute")
async def get_document(request: Request, document_id: str):
    """Get a specific document's parsed data"""
    try:
        document = await database.controller.document_controller.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
@limiter.limit("10/minute")
async def delete_document(request: Request, document_id: str):
    """Delete a document and its associated data"""
    try:
        await database.controller.document_controller.delete_document(document_id, database)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
