"""Vector storage and similarity retrieval using ChromaDB."""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from .chunker import TextChunk

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Manages document collections and similarity searches in ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "docuquery_documents",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("ChromaDB initialized with collection: %s", collection_name)

    def add_chunks(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> None:
        """Upsert embedded chunks into ChromaDB collection."""
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Indexed %d chunks into ChromaDB.", len(chunks))

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_doc_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve top-K matching document chunks with page metadata."""
        where_filter = {"doc_id": filter_doc_id} if filter_doc_id else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity_score = 1.0 - dist  # Cosine distance to similarity
                retrieved.append({
                    "text": doc,
                    "metadata": meta,
                    "page": meta.get("page", 1),
                    "source": meta.get("source", "Document"),
                    "similarity_score": round(similarity_score, 4),
                })

        return retrieved
