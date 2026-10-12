"""FastAPI server entrypoint for DocuQuery."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as doc_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="DocuQuery API",
    description="Full-stack Document Intelligence & RAG Platform with page citation grounding",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doc_router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "DocuQuery API",
        "vectorstore": "ChromaDB",
        "embedding_provider": "OpenAI",
    }
