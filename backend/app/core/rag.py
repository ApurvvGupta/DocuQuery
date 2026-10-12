"""RAG generation engine enforcing citation grounding by page reference."""

import os
import time
import logging
from typing import List, Dict, Any
from .vectorstore import ChromaVectorStore
from .embeddings import EmbeddingService
from ..models.schemas import QueryResponse, Citation

logger = logging.getLogger(__name__)


RAG_SYSTEM_PROMPT = """You are DocuQuery, an enterprise document intelligence assistant.
Your job is to answer user queries based EXCLUSIVELY on the provided document excerpts.

STRICT CITATION RULES:
1. Every factual statement must cite its page reference in brackets, for example: "Revenues grew by 14% [Page 4]."
2. If multiple pages support a statement, cite them all: "[Page 2, Page 5]".
3. Do not assume or extrapolate facts not present in the excerpts.
4. If the provided excerpts do not contain the answer, reply: "I cannot find this information in the provided document."
"""


class RAGService:
    """Orchestrates retrieval and grounded response generation with page citations."""

    def __init__(
        self,
        vectorstore: ChromaVectorStore,
        embedding_service: EmbeddingService,
        model_name: str = "gpt-4o-mini",
    ):
        self.vectorstore = vectorstore
        self.embedding_service = embedding_service
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def answer_query(self, query: str, doc_id: str = None, top_k: int = 4) -> QueryResponse:
        """Retrieve relevant pages and synthesize an answer grounded with citations."""
        start_time = time.time()

        # 1. Retrieve relevant passages
        query_vec = self.embedding_service.embed_query(query)
        contexts = self.vectorstore.similarity_search(query_vec, top_k=top_k, filter_doc_id=doc_id)

        if not contexts:
            latency = (time.time() - start_time) * 1000
            return QueryResponse(
                answer="No relevant documents or pages were found matching your query.",
                citations=[],
                query_latency_ms=round(latency, 2),
            )

        # 2. Build context block with page labels
        context_str = "\n\n---\n\n".join(
            f"[Source: {c['source']} | Page: {c['page']}]\n{c['text']}"
            for c in contexts
        )

        user_prompt = f"DOCUMENT EXCERPTS:\n{context_str}\n\nUSER QUESTION:\n{query}\n\nANSWER (with [Page X] citations):"

        # 3. Call OpenAI LLM if key is present, otherwise provide structured preview
        answer_text = ""
        if self.api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                completion = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": RAG_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                )
                answer_text = completion.choices[0].message.content
            except Exception as e:
                logger.error("OpenAI LLM inference error: %s", e)

        if not answer_text:
            top_page = contexts[0]["page"]
            answer_text = (
                f"Based on the analyzed document excerpts [Page {top_page}], "
                f"relevant information was identified regarding '{query}'. "
                f"Excerpt: \"{contexts[0]['text'][:220]}...\" [Page {top_page}]."
            )

        # 4. Compile verifiable citations
        citations = [
            Citation(
                page_number=c["page"],
                source_document=c["source"],
                snippet=c["text"][:180] + "...",
                relevance_score=c["similarity_score"],
            )
            for c in contexts
        ]

        latency = (time.time() - start_time) * 1000
        return QueryResponse(
            answer=answer_text,
            citations=citations,
            query_latency_ms=round(latency, 2),
        )
