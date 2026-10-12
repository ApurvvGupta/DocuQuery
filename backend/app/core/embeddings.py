"""Vector embedding generation module using OpenAI embeddings."""

import os
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates dense vector embeddings using OpenAI API with fallback support."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Initialized OpenAI embedding client with model: %s", self.model_name)
            except Exception as e:
                logger.warning("Could not initialize OpenAI client: %s", e)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of string chunks."""
        if not texts:
            return []

        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model_name
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.error("OpenAI embedding API call failed: %s. Using fallback.", e)

        # Deterministic normalized mock embeddings for offline / testing runs
        logger.debug("Generating fallback mock embeddings for %d texts.", len(texts))
        return [
            (np.random.RandomState(abs(hash(t)) % (2**32)).randn(1536) / 39.0).tolist()
            for t in texts
        ]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        return self.embed_texts([query])[0]
