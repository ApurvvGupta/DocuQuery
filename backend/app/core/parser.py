"""Document parsing module preserving exact page metadata for citation."""

import os
import io
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class DocumentPage:
    """Represents an extracted page with content and source offset."""
    page_number: int
    text: str
    metadata: Dict[str, Any]


class DocumentParser:
    """Extracts text and page-level metadata from multi-format enterprise files."""

    @staticmethod
    def parse_pdf(file_bytes: bytes, filename: str) -> List[DocumentPage]:
        """Extract text page-by-page from a PDF byte stream."""
        pages = []
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            logger.info("Parsing PDF '%s' with %d pages.", filename, total_pages)

            for idx, page in enumerate(reader.pages, start=1):
                raw_text = page.extract_text() or ""
                cleaned_text = " ".join(raw_text.split())

                pages.append(
                    DocumentPage(
                        page_number=idx,
                        text=cleaned_text,
                        metadata={
                            "source": filename,
                            "page": idx,
                            "total_pages": total_pages,
                        },
                    )
                )
        except Exception as e:
            logger.error("Failed to parse PDF '%s': %s", filename, e)
            raise ValueError(f"Corrupted or unsupported PDF format: {e}")

        return pages

    @staticmethod
    def parse_text(text_content: str, filename: str) -> List[DocumentPage]:
        """Wrap plaintext document into a single page container."""
        return [
            DocumentPage(
                page_number=1,
                text=text_content.strip(),
                metadata={"source": filename, "page": 1, "total_pages": 1},
            )
        ]
