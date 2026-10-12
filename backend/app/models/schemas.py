"""Pydantic data schemas for DocuQuery API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    page_number: int = Field(..., description="1-indexed document page number")
    source_document: str = Field(..., description="Original filename")
    snippet: str = Field(..., description="Supporting excerpt from the page")
    relevance_score: float = Field(..., description="Cosine similarity score")


class QueryRequest(BaseModel):
    question: str = Field(..., example="What were the total Q3 revenues reported?")
    doc_id: Optional[str] = Field(None, description="Optional target document filter")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of passages to retrieve")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Grounded answer cited with page numbers")
    citations: List[Citation] = Field(default=[], description="List of verified page references")
    query_latency_ms: float = Field(..., description="Execution time in milliseconds")


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    total_chunks: int
    message: str


class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    total_pages: int
    uploaded_at: str
