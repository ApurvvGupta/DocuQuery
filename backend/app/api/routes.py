"""FastAPI endpoint routes for document management and RAG Q&A."""

import os
import uuid
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..models.schemas import DocumentUploadResponse, QueryRequest, QueryResponse
from ..core.parser import DocumentParser
from ..core.chunker import SemanticChunker
from ..core.embeddings import EmbeddingService
from ..core.vectorstore import ChromaVectorStore
from ..core.rag import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Lazy-loaded singleton services
vectorstore = ChromaVectorStore()
embedding_service = EmbeddingService()
rag_service = RAGService(vectorstore, embedding_service)
chunker = SemanticChunker(chunk_size=500, chunk_overlap=80)

# In-memory document registry
DOCUMENTS_REGISTRY = {}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF or text document, chunk content, generate embeddings, and store in ChromaDB."""
    filename = file.filename
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    file_bytes = await file.read()
    doc_id = str(uuid.uuid4())[:8]

    try:
        if filename.endswith(".pdf"):
            pages = DocumentParser.parse_pdf(file_bytes, filename)
        else:
            pages = DocumentParser.parse_text(file_bytes.decode("utf-8", errors="ignore"), filename)

        if not pages:
            raise HTTPException(status_code=400, detail="Document contains no extractable text.")

        # Chunk pages while retaining page number metadata
        chunks = chunker.chunk_pages(pages, doc_id)

        # Generate embeddings
        chunk_texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)

        # Store in ChromaDB
        vectorstore.add_chunks(chunks, embeddings)

        DOCUMENTS_REGISTRY[doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "pages": len(pages),
            "chunks": len(chunks),
        }

        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=filename,
            total_pages=len(pages),
            total_chunks=len(chunks),
            message=f"Document '{filename}' successfully processed and indexed.",
        )
    except Exception as e:
        logger.error("Error processing document '%s': %s", filename, e)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query indexed documents and receive an answer grounded by page citations."""
    try:
        response = rag_service.answer_query(
            query=request.question,
            doc_id=request.doc_id,
            top_k=request.top_k
        )
        return response
    except Exception as e:
        logger.error("RAG Query failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@router.get("/list")
async def list_documents():
    """List all currently indexed documents."""
    return list(DOCUMENTS_REGISTRY.values())
