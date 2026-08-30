# ResearchPilot AI

> An AI-powered research assistant for asking questions about research papers using Retrieval-Augmented Generation (RAG), semantic search, and source-aware answers.

[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/us-utkarshsri07/ResearchPilotAI/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-Build%20Tool-646CFF.svg?logo=vite&logoColor=white)](https://vite.dev/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20Database-D04A02.svg)](https://qdrant.tech/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

---

# Overview

ResearchPilot AI is a full-stack AI research assistant designed to help users understand and interact with research papers through natural-language questions.

Instead of sending an entire research paper directly to a language model, ResearchPilot AI uses a Retrieval-Augmented Generation (RAG) pipeline to retrieve the most relevant sections of the uploaded document and provide them as context to the language model.

The system combines:

- PDF document processing
- Text chunking
- Semantic embeddings
- Vector search
- Document-specific retrieval
- Retrieval-Augmented Generation
- Gemini-based answer generation
- Source-aware responses
- Conversation history
- PostgreSQL persistence
- Qdrant vector storage
- React frontend
- FastAPI backend
- Docker-based development
- Railway backend deployment
- Vercel frontend deployment


The primary goal is to make research-paper interaction more efficient while keeping generated answers grounded in the uploaded source material.

---

### Silent / Less-Obvious Features

- Globally unique chunk IDs prevent collisions between documents
- Document-level retrieval isolation
- Chunk metadata preserved inside Qdrant
- Source, page number, filename, chunk ID, and document ID retained
- Conversation context is used for follow-up questions
- Conversation history is not treated as a factual source
- Answers are restricted to retrieved research context
- Citation numbers are generated only from available sources
- Configurable retrieval and relevance thresholds
- Cross-encoder reranker support
- Local Qdrant fallback for development
- Qdrant Cloud support for production
- PostgreSQL persistence for documents and conversations
- Separate vector and relational storage
- Dockerized local development environment
- Production deployment using Railway + Vercel

---

## System Architecture

<!-- Replace with your architecture image -->

<p align="center">
  <img src="System Architecture.png" alt="ResearchPilot AI System Architecture" width="100%">
</p>

<!-- Optional SVG version -->
<!--
<p align="center">
  <img src="System Architecture.png" alt="ResearchPilot AI Architecture" width="100%">
</p>
-->

---

## Production Architecture

```text
                         Users
                           |
                           ↓
                  ┌─────────────────┐
                  │     Vercel      │
                  │ React + Vite    │
                  └────────┬────────┘
                           |
                       REST API
                           |
                           ↓
                  ┌─────────────────┐
                  │     Railway     │
                  │ FastAPI Backend │
                  └────────┬────────┘
                           |
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │ PostgreSQL │ │   Qdrant   │ │  Gemini    │
      │            │ │            │ │    API     │
      │ Documents  │ │ Embeddings │ │    LLM     │
      │ Messages   │ │ Chunks     │ │ Generation │
      │ Chats      │ │ Metadata   │ │            │
      └────────────┘ └────────────┘ └────────────┘

```

## Project Structure

| **Folder / File** | **Purpose** |
|---|---|
| `backend/` | FastAPI backend and RAG pipeline |
| `backend/api/` | API routes and application lifecycle |
| `backend/core/` | Configuration and environment settings |
| `backend/rag/` | Retrieval-Augmented Generation pipeline |
| `backend/rag/ingestion/` | PDF processing, chunking, and ingestion |
| `backend/rag/retrieval/` | Vector search and retrieval logic |
| `backend/rag/pipeline.py` | Main RAG orchestration |
| `backend/rag/retrieval/vector_store.py` | Qdrant vector storage and search |
| `frontend/` | React + Vite frontend |
| `frontend/src/` | Frontend application source |
| `datasets/` | Dataset and document-related files |
| `data/` | Local persistent application data |
| `docker-compose.yml` | Local multi-container environment |
| `.env` | Local environment configuration |
| `README.md` | Project documentation |

---

## Internal Flow Mapping

| **Component** | **Responsibility** |
|---|---|
| PDF Ingestion | Extract and process uploaded documents |
| Chunking | Split document text into searchable chunks |
| Embeddings | Convert chunks into 384-dimensional vectors |
| Vector Store | Store and retrieve embeddings using Qdrant |
| Retrieval | Find relevant document chunks |
| Reranking | Improve relevance ordering |
| Context Construction | Build grounded context for the LLM |
| LLM Generation | Generate the final answer using Gemini |
| Source Tracking | Return page and chunk information |
| Conversations | Persist research conversations |
| API Layer | Expose backend functionality |
| Frontend | Upload, ask, retrieve and display results |

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Fetch API

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy

### AI / ML

- Google Gemini
- Sentence Transformers
- MiniLM
- Cross-Encoder

### Databases

- PostgreSQL
- Qdrant

### Infrastructure

- Docker
- Docker Compose
- Railway
- Vercel
- Qdrant Cloud

---

## Execution Flow

```text
User
  ↓
React + Vite Frontend
  ↓
FastAPI Backend
  ↓
PDF Processing
  ↓
Text Extraction
  ↓
Chunking
  ↓
MiniLM Embeddings
  ↓
Qdrant Vector Database
  ↓
User Question
  ↓
Query Processing
  ↓
Query Embedding
  ↓
Document-Scoped Vector Search
  ↓
Relevant Chunks
  ↓
Reranking / Retrieval Selection
  ↓
Context Construction
  ↓
Gemini
  ↓
Answer + Sources
  ↓
Conversation Persistence
  ↓
Frontend Display

```
## RAG Configuration

| **Configuration**           | **Value / Purpose**                       |
|-----------------------------|-------------------------------------------|
| Chunk Size                  | Controls the amount of text in each chunk |
| Chunk Overlap               | Preserves context between adjacent chunks |
| Embedding Dimensions        | `384`                                     |
| Retrieval Top-K             | Number of chunks initially retrieved      |
| Final Top-K                 | Number of chunks passed to generation     |
| Minimum Relevance Score     | Filters low-quality retrieval results     |
| Vector Distance             | `Cosine`                                  |
| Collection                  | `researchpilot_chunks`                    |


## Key Design Decisions

### Why RAG?

Research papers can contain large amounts of information. RAG retrieves relevant document sections before generating an answer, allowing the LLM to work with targeted research context.

### Why Qdrant?

Qdrant provides vector similarity search together with metadata filtering. This allows ResearchPilot to retrieve semantically relevant chunks while restricting results to a specific document.

### Why PostgreSQL + Qdrant?

Each database has a separate responsibility:

```text
PostgreSQL
    ↓
Structured Application Data

Qdrant

```

### Why Page-Level Metadata?

Page and chunk metadata allow retrieved information to be traced back to the original research document.

### Why Conversation Context?

Conversation history enables natural follow-up questions while keeping factual answers grounded in retrieved research context.

---

## Important Project Characteristics

- Document-scoped RAG
- Source-aware answer generation
- Page-level traceability
- Semantic vector retrieval
- Configurable retrieval pipeline
- Reranking support
- Persistent conversations
- Globally unique chunk IDs
- Metadata-aware chunks
- Local Qdrant support
- Qdrant Cloud support
- PostgreSQL persistence
- Dockerized development
- Separate frontend and backend
- Production deployment architecture

---


## Limitations

- Answer quality depends on PDF extraction quality.
- Poorly structured PDFs may reduce retrieval accuracy.
- Embedding generation can be computationally expensive during local development.
- Answer quality depends on the relevance of retrieved context.
- External AI and cloud services require valid production credentials.
- The system is primarily designed for research documents rather than arbitrary web content.

---

## Future Improvements

- Streaming LLM responses
- User authentication
- Multi-user workspaces
- Multi-document research sessions
- Advanced hybrid retrieval
- Improved reranking
- Research paper comparison
- Automatic document summarization
- Citation highlighting
- Exact source/page preview
- Background document processing
- Async ingestion
- Retrieval evaluation benchmarks
- Answer quality evaluation
- Document-level analytics

---

## Project Status

**Version:** `v1.0.0`

ResearchPilot AI currently supports the complete research workflow:

```text
PDF Upload
    ↓
Document Processing
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Indexing
    ↓
Document-Scoped Retrieval
    ↓
Reranking
    ↓
RAG Answer Generation
    ↓
Source Attribution
    ↓
Conversation Persistence
    ↓
Semantic Vector Search

```

## Version History

### v1.0.0

- Initial production release
- PDF document ingestion
- Semantic embeddings
- Qdrant vector search
- Document-level retrieval filtering
- RAG-based question answering
- Gemini integration
- Conversation management
- Page-level source tracking
- Retrieval score display
- Production deployment support

---

## License

MIT LICENSE

---

## Author

**Utkarsh**

ResearchPilot AI is an AI-powered research assistant focused on grounded answers, semantic retrieval, source traceability, and document-aware conversations.
