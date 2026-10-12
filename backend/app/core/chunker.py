"""Semantic text chunker preserving page-level citation boundaries."""

import re
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Chunk of text annotated with page number and document provenance."""
    chunk_id: str
    text: str
    page_number: int
    metadata: Dict[str, Any]


class SemanticChunker:
    """Splits document pages into semantically cohesive overlapping chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: list, doc_id: str) -> List[TextChunk]:
        """Split pages into token/word chunks tagged with exact page citation metadata."""
        chunks = []
        chunk_idx = 0

        for page in pages:
            words = page.text.split()
            if not words:
                continue

            start = 0
            while start < len(words):
                end = min(start + self.chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_str = " ".join(chunk_words)

                c_id = f"{doc_id}_p{page.page_number}_c{chunk_idx}"
                chunks.append(
                    TextChunk(
                        chunk_id=c_id,
                        text=chunk_str,
                        page_number=page.page_number,
                        metadata={
                            **page.metadata,
                            "chunk_id": c_id,
                            "doc_id": doc_id,
                            "word_count": len(chunk_words),
                        },
                    )
                )
                chunk_idx += 1

                if end == len(words):
                    break
                start += self.chunk_size - self.chunk_overlap

        logger.info("Chunked document '%s' into %d chunks.", doc_id, len(chunks))
        return chunks
