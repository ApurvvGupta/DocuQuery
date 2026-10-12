# DocuQuery — AI-Powered Document Intelligence Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-blue.svg)](https://www.trychroma.com/)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI%20API-412991.svg?logo=openai)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-stack **Retrieval-Augmented Generation (RAG)** platform enabling users to upload enterprise documents (PDFs, reports, manuals) and query them in natural language. Generates hallucination-resistant answers strictly grounded in source content and cited by precise page reference numbers.

---

## 🌟 Key Features

- **Multi-Page Text Extraction & Parsing:** Structured document parsing preserving exact page offsets and document metadata.
- **Semantic Chunking:** Context-aware text segmentation preventing boundary context loss across paragraphs and headings.
- **Dense Vector Search:** High-dimensional vector indexing using ChromaDB with cosine similarity retrieval.
- **Page-Level Grounded Citations:** RAG response synthesizer enforcing verifiable page citations for every factual statement.
- **Modern Full-Stack Stack:** Next.js 14 + TypeScript frontend paired with an asynchronous FastAPI backend.
- **Dockerized Architecture:** Multi-service orchestration for frontend, backend API, ChromaDB vector store, and PostgreSQL.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([User / Browser]) -->|Upload PDF / Query| NextUI[Next.js 14 Frontend]
    NextUI -->|REST API| APIServer[FastAPI Backend]
    
    subgraph "Document Processing Pipeline"
        APIServer -->|Upload Stream| Parser[PDF Parser & Page Extractor]
        Parser -->|Pages & Metadata| Chunker[Semantic Chunker]
        Chunker -->|Text Chunks| Embedder[OpenAI Embedding Generator]
        Embedder -->|Dense Vectors| VectorDB[(ChromaDB)]
    end

    subgraph "Grounded Retrieval & Generation"
        APIServer -->|Natural Language Query| VectorDB
        VectorDB -->|Top-K Context Chunks| Synthesizer[Grounded LLM Synthesizer]
        Synthesizer -->|Cited Answers + Page Ref| NextUI
    end
```

---

## 📂 Project Structure

```
DocuQuery/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # Upload, Query & Document Endpoints
│   │   ├── core/
│   │   │   ├── parser.py          # PDF text extraction with page tracking
│   │   │   ├── chunker.py         # Semantic chunking engine
│   │   │   ├── embeddings.py      # OpenAI vector embedding generation
│   │   │   ├── vectorstore.py     # ChromaDB collection management
│   │   │   └── rag.py             # Grounded response synthesis & citations
│   │   ├── models/schemas.py      # Pydantic data schemas
│   │   ├── config.py              # Application settings
│   │   └── main.py                # FastAPI entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx           # Document intelligence dashboard
│   │   └── components/            # Upload widget & cited Q&A interface
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIR=./data/chroma
UPLOAD_DIR=./data/uploads
```

### 2. Launch with Docker Compose
```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- FastAPI Docs: `http://localhost:8000/docs`

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for details.
