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
  <img src="YOUR_ARCHITECTURE_IMAGE_URL" alt="ResearchPilot AI System Architecture" width="100%">
</p>

<!-- Optional SVG version -->
<!--
<p align="center">
  <img src="System Architecture.png" alt="ResearchPilot AI Architecture" width="100%">
</p>
-->

---

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
