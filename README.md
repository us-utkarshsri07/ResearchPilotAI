# ResearchPilot AI

> An AI-powered research assistant for interrogating research papers with grounded, source-traceable answers.

[![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/us-utkarshsri07/ResearchPilotAI/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20Database-D04A02.svg)](https://qdrant.tech/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

---

## Overview

ResearchPilot AI is a full-stack Retrieval-Augmented Generation (RAG) application designed to help users understand dense research papers through natural-language questions.

Instead of sending an entire document directly to an LLM, ResearchPilot AI:

1. Accepts a research PDF.
2. Extracts and processes its contents.
3. Splits the document into overlapping chunks.
4. Generates vector embeddings for each chunk.
5. Stores the embeddings and metadata in Qdrant.
6. Retrieves the most relevant sections for a question.
7. Uses the retrieved context to generate a grounded answer.
8. Returns the answer together with the retrieved source chunks.
9. Persists documents and conversations using PostgreSQL.

The goal is not simply to generate an answer, but to make the answer **traceable back to the source document**.

---

## Demo

### Production

**Frontend**

https://research-pilot-ai-navy.vercel.app

**Backend**

https://researchpilotai-production.up.railway.app

**API Documentation**

https://researchpilotai-production.up.railway.app/docs

---

## Key Features

### 1. PDF Research Paper Upload

Users can upload research papers directly through the web interface.

The backend processes the document and extracts the information required for retrieval.

Supported workflow:

```text
PDF
 ↓
Document parsing
 ↓
Chunking
 ↓
Metadata extraction
 ↓
Embedding generation
 ↓
Qdrant indexing
