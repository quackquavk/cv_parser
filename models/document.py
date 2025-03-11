from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from bson import ObjectId


class Document(BaseModel):
    """Base document model"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    document_name: str
    document_url: str
    folder_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        populate_by_name = True


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    document_id: str
    document_name: str
    document_url: str
    parsed_cv: Optional[Dict[str, Any]] = None


class DocumentSearchRequest(BaseModel):
    """Request model for document search"""
    query: str = Field(..., description="Search query string")
    limit: Optional[int] = Field(default=5, ge=1, le=20, description="Number of results to return")


class DocumentSearchResponse(BaseModel):
    """Response model for document search"""
    document_id: str
    similarity_score: float
    parsed_cv: Optional[Dict[str, Any]] = None


class DocumentList(BaseModel):
    """Request model for bulk document operations"""
    document_ids: List[str] = Field(..., description="List of document IDs to process")


class Query(BaseModel):
    address: Optional[str] | None = ""
    attribute: Optional[List[str]] | None = [""]
    prompt: Optional[str] | None = ""
    foldersToSearch: List[str] | None = [""]
    sort_order: Optional[str] = None  # Add this field (asc/desc)


class AvailabilityRequest(BaseModel):
    document_id: Optional[str] | None = ""


class Availability(BaseModel):
    document_id: str
    availability: Optional[str] | None = ""
    time_of_day: Optional[str] | None = ""
    star_rating: Optional[int] | None = None
    current_salary: Optional[float] | None = None
    estimated_salary: Optional[float] | None = None
    paid_by: Optional[str] | None = None
    vote: Optional[bool] | None = None
    note: Optional[str] | None = None


