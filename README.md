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

## Live Demo

### Frontend

https://research-pilot-ai-navy.vercel.app

### Backend

https://researchpilotai-production.up.railway.app

### API Documentation

https://researchpilotai-production.up.railway.app/docs

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

# Key Features

## 1. PDF Research Paper Upload

Users can upload research papers directly through the web interface.

The backend processes the uploaded PDF and converts it into searchable document chunks.

The ingestion pipeline follows:

```text
PDF
 │
 ▼
Document Parsing
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
Metadata Extraction
 │
 ▼
Embedding Generation
 │
 ▼
Qdrant Indexing
```

Once indexing is complete, the document becomes available for semantic question answering.

---

## 2. Semantic Search

ResearchPilot AI uses dense vector embeddings to represent document chunks.

The current embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Each chunk is converted into a:

```text
384-dimensional vector
```

This allows the system to retrieve semantically relevant content rather than depending only on exact keyword matches.

For example, a user can ask:

```text
How does self-attention connect different tokens?
```

and the system can retrieve relevant passages even if the exact wording does not appear in the document.

---

## 3. Retrieval-Augmented Generation

ResearchPilot AI uses a Retrieval-Augmented Generation architecture.

Instead of asking the language model to answer solely from its pretrained knowledge, the system first retrieves relevant passages from the uploaded document.

The simplified pipeline is:

```text
User Question
      │
      ▼
Question Processing
      │
      ▼
Query Embedding
      │
      ▼
Qdrant Vector Search
      │
      ▼
Relevant Document Chunks
      │
      ▼
Context Construction
      │
      ▼
Gemini
      │
      ▼
Generated Answer
      │
      ▼
Retrieved Sources
```

This allows the generation stage to operate using information retrieved from the user's document.

---

## 4. Document-Specific Retrieval

Every document chunk contains metadata identifying the document from which it originated.

Example:

```json
{
  "document_id": "044b8388-7d4d-41ca-bdca-e385f7007b75",
  "filename": "sample_paper.pdf",
  "page_number": 2,
  "chunk_index": 7
}
```

When a question is asked about a specific document, the retrieval layer can restrict the vector search to chunks belonging to that document.

The primary filtering field is:

```text
document_id
```

A Qdrant payload index is used for this field to support filtered retrieval.

---

## 5. Source-Aware Answers

ResearchPilot AI does not only return the generated answer.

It also returns the retrieved document sources used during the retrieval process.

Retrieved source information can include:

- Filename
- Page number
- Chunk index
- Source content
- Retrieval score
- Document ID

The frontend displays these sources alongside the generated response.

Example:

```text
Retrieved Sources

Page 2 · Chunk 7
Page 6 · Chunk 25
...
```

This allows users to inspect the document context behind the answer.

---

## 6. Conversation History

ResearchPilot AI stores conversations associated with uploaded documents.

Users can:

- Create a new conversation
- Ask multiple questions
- View previous questions
- Retrieve conversation history
- Delete conversations

This allows users to maintain separate research sessions for a document.

---

## 7. PostgreSQL Persistence

PostgreSQL is used for persistent application-level data.

The database stores entities such as:

- Documents
- Conversations
- Messages
- Related metadata

This separates application persistence from vector retrieval.

---

## 8. Qdrant Vector Database

Qdrant is used as the vector database.

It stores:

- Document embeddings
- Chunk content
- Document metadata
- Retrieval metadata

A vector point contains payload information similar to:

```json
{
  "content": "...",
  "source": "...",
  "filename": "sample_paper.pdf",
  "page_number": 2,
  "document_id": "...",
  "chunk_id": "...",
  "chunk_index": 7
}
```

---

# Architecture

ResearchPilot AI consists of a frontend, backend, persistence layer, vector retrieval layer, and LLM generation layer.

```text
┌─────────────────────────────────────────────┐
│                  Frontend                   │
│                React + Vite                 │
└──────────────────────┬──────────────────────┘
                       │
                       │ HTTP / REST
                       ▼
┌─────────────────────────────────────────────┐
│                  Backend                    │
│                  FastAPI                    │
│                                             │
│   Upload │ Documents │ Conversations │ Ask │
└───────────────┬─────────────────┬───────────┘
                │                 │
                │                 │
                ▼                 ▼
       ┌────────────────┐  ┌─────────────────┐
       │   PostgreSQL   │  │   RAG Pipeline  │
       │                │  │                 │
       │ Application    │  │ Retrieval       │
       │ Persistence    │  │ Embeddings      │
       │                │  │ Generation      │
       └────────────────┘  └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │     Qdrant      │
                           │                 │
                           │ Vector Storage  │
                           │ + Metadata      │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │     Gemini      │
                           │                 │
                           │ Answer          │
                           │ Generation      │
                           └─────────────────┘
```

---

# RAG Pipeline

## Step 1: Document Upload

The frontend sends the PDF to:

```http
POST /upload
```

The backend receives the file and creates the corresponding document record.

---

## Step 2: Document Processing

The uploaded PDF is processed into smaller chunks.

Current configuration:

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

Chunk overlap helps preserve context when a concept spans multiple chunks.

Conceptually:

```text
Chunk 1
████████████████████

        Chunk 2
        ████████████████████

                Chunk 3
                ████████████████████
```

---

## Step 3: Embedding Generation

Each document chunk is converted into a vector embedding using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Vector dimension:

```text
384
```

The same embedding model is used for both document chunks and user queries.

---

## Step 4: Vector Storage

The generated embeddings are stored in Qdrant.

The collection used by the application is:

```text
researchpilot_chunks
```

Each chunk is represented as a Qdrant point containing:

```text
Vector
+
Document Content
+
Document Metadata
```

---

## Step 5: Query Embedding

When a user asks a question, the question is converted into a vector embedding using the same embedding model.

This places the query and document chunks into the same vector space.

---

## Step 6: Retrieval

The query vector is sent to Qdrant for similarity search.

The retrieval layer can optionally restrict results by:

```text
document_id
```

Current retrieval configuration:

```python
RETRIEVAL_TOP_K = 5
MIN_RETRIEVAL_TOP_K = 3
FINAL_TOP_K = 5
HYBRID_TOP_K = 10
MIN_RELEVANCE_SCORE = 0.0
```

---

## Step 7: Context Construction

The retrieved chunks are converted into context for the generation stage.

The system preserves the associated metadata so the retrieved sources can be displayed to the user.

---

## Step 8: Answer Generation

The retrieved context is passed to the Gemini generation layer.

Configured generation model:

```text
gemini-3.6-flash
```

The model generates an answer based on the retrieved document context.

---

## Step 9: Source Presentation

The backend returns:

```text
Answer
+
Retrieved Sources
```

The frontend displays the generated answer and the relevant document chunks.

Example:

```text
Answer

Self-attention is ...

Retrieved Sources

Page 2 · Chunk 7
Page 6 · Chunk 25
...
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Backend | FastAPI |
| API Server | Uvicorn |
| Programming Language | Python 3.11+ |
| Relational Database | PostgreSQL |
| Vector Database | Qdrant |
| Embedding Framework | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Reranker | ms-marco-MiniLM-L-6-v2 |
| LLM | Gemini |
| Containerization | Docker |
| Local Orchestration | Docker Compose |
| Backend Deployment | Railway |
| Frontend Deployment | Vercel |

---

# Project Structure

```text
ResearchPilotAI/
│
├── backend/
│   ├── api/
│   │   └── main.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   │   └── schemas.py
│   │   │
│   │   ├── retrieval/
│   │   │   └── vector_store.py
│   │   │
│   │   ├── pipeline.py
│   │   └── ...
│   │
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── ...
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── datasets/
│   ├── raw/
│   └── ...
│
├── data/
│   └── qdrant/
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

> The exact directory structure may evolve as development continues.

---

# API

The backend is implemented using FastAPI.

## Health Check

```http
GET /health
```

Returns application health information.

Example:

```json
{
  "status": "healthy",
  "service": "researchpilot",
  "documents": 1
}
```

---

## Upload PDF

```http
POST /upload
```

Uploads and processes a PDF document.

Request:

```text
multipart/form-data
file=<PDF>
```

The backend:

1. Receives the PDF.
2. Extracts document content.
3. Splits the content into chunks.
4. Generates embeddings.
5. Stores vectors in Qdrant.
6. Stores document metadata.

---

## Get Documents

```http
GET /documents
```

Returns uploaded documents.

---

## Get Document Conversations

```http
GET /documents/{document_id}/conversations
```

Returns conversations associated with a document.

---

## Create Conversation

```http
POST /documents/{document_id}/conversations
```

Creates a new conversation for a document.

---

## Get Conversation

```http
GET /conversations/{conversation_id}
```

Returns conversation history.

---

## Delete Conversation

```http
DELETE /conversations/{conversation_id}
```

Deletes a conversation.

---

## Ask Question

```http
POST /ask
```

Example request:

```json
{
  "question": "What is self-attention?",
  "document_id": "044b8388-7d4d-41ca-bdca-e385f7007b75"
}
```

A conversation can optionally be included:

```json
{
  "question": "How is it different from multi-head attention?",
  "document_id": "044b8388-7d4d-41ca-bdca-e385f7007b75",
  "conversation_id": 1
}
```

The response contains the generated answer and retrieved sources.

---

# API Documentation

FastAPI automatically provides interactive API documentation.

## Local

```text
http://localhost:8000/docs
```

## Production

```text
https://researchpilotai-production.up.railway.app/docs
```

OpenAPI specification:

```text
http://localhost:8000/openapi.json
```

---

# Environment Variables

Create a `.env` file for local development.

Example:

```env
# PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/researchpilot

# Gemini
GEMINI_API_KEY=your_gemini_api_key

# Qdrant
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your_qdrant_api_key

# Frontend
VITE_API_URL=http://localhost:8000
```

---

# Environment Variable Reference

## DATABASE_URL

PostgreSQL connection string.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/researchpilot
```

---

## GEMINI_API_KEY

API key used to access Gemini.

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit this value to GitHub.

---

## QDRANT_URL

URL of the Qdrant cluster.

Example:

```env
QDRANT_URL=https://your-cluster.qdrant.io
```

---

## QDRANT_API_KEY

Authentication key for Qdrant.

```env
QDRANT_API_KEY=your_qdrant_api_key
```

---

## VITE_API_URL

Frontend API base URL.

For local development:

```env
VITE_API_URL=http://localhost:8000
```

For production:

```env
VITE_API_URL=https://researchpilotai-production.up.railway.app
```

---

# Local Development

## Prerequisites

Install the following:

- Git
- Docker
- Docker Compose
- Node.js
- Python 3.11+
- PostgreSQL, or use the Docker configuration
- Gemini API key
- Qdrant account/API key if using remote Qdrant

---

# Clone the Repository

```bash
git clone https://github.com/us-utkarshsri07/ResearchPilotAI.git
cd ResearchPilotAI
```

---

# Configure Environment

Create the environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then configure the required environment variables.

---

# Run with Docker Compose

Build and start the application:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

Expected services may include:

```text
backend
frontend
postgres
qdrant
```

---

# Stop Services

```bash
docker compose down
```

---

# Rebuild After Code Changes

```bash
docker compose down
docker compose up --build
```

---

# Local URLs

## Frontend

```text
http://localhost:5173
```

## Backend

```text
http://localhost:8000
```

## FastAPI Documentation

```text
http://localhost:8000/docs
```

## OpenAPI

```text
http://localhost:8000/openapi.json
```

---

# Production Deployment

ResearchPilot AI uses a split deployment architecture.

```text
                         Internet
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
             Vercel                  Railway
            Frontend                 Backend
                │                       │
                │                       │
                └───────────┬───────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
              PostgreSQL         Qdrant Cloud
                                      │
                                      ▼
                                    Gemini
```

---

# Frontend Deployment

The frontend is deployed using Vercel.

The production API URL is configured using:

```env
VITE_API_URL=https://researchpilotai-production.up.railway.app
```

Build the frontend using:

```bash
npm run build
```

Because Vite environment variables are injected during the build process, changing `VITE_API_URL` requires a new frontend deployment.

---

# Backend Deployment

The backend is deployed using Railway.

The application listens on:

```text
0.0.0.0:8000
```

Production environment variables include:

```env
DATABASE_URL=...
GEMINI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
```

---

# Qdrant Configuration

Production vector storage uses Qdrant.

The application uses the collection:

```text
researchpilot_chunks
```

The collection stores:

```text
Embeddings
+
Chunk Content
+
Document Metadata
```

The retrieval system uses a payload filter on:

```text
document_id
```

Therefore, the Qdrant collection requires an index for this payload field.

Example:

```python
client.create_payload_index(
    collection_name="researchpilot_chunks",
    field_name="document_id",
    field_schema="keyword",
)
```

---

# Docker Architecture

Local development can be run using multiple services:

```text
┌──────────────────────┐
│      Frontend        │
│       Vite           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Backend         │
│      FastAPI         │
└──────┬────────┬──────┘
       │        │
       ▼        ▼
┌──────────┐ ┌──────────┐
│PostgreSQL│ │  Qdrant  │
└──────────┘ └──────────┘
```

---

# Configuration

## Retrieval

```python
RETRIEVAL_TOP_K = 5
MIN_RETRIEVAL_TOP_K = 3
FINAL_TOP_K = 5
HYBRID_TOP_K = 10
MIN_RELEVANCE_SCORE = 0.0
```

## Chunking

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

## Embedding Model

```text
sentence-transformers/all-MiniLM-L6-v2
```

## Embedding Dimension

```text
384
```

## Reranker

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

## Generation Model

```text
gemini-3.6-flash
```

---

# Example Workflow

Suppose a user uploads:

```text
Attention Is All You Need.pdf
```

The system processes the document:

```text
Upload PDF
     │
     ▼
Extract Document
     │
     ▼
Create Chunks
     │
     ▼
Generate Embeddings
     │
     ▼
Store Vectors in Qdrant
     │
     ▼
Document Becomes Searchable
```

For example, a document may be divided into:

```text
45 chunks
```

The user can then ask:

```text
What is self-attention?
```

The question-answering pipeline becomes:

```text
Question
   │
   ▼
Query Embedding
   │
   ▼
Qdrant Retrieval
   │
   ▼
Top Relevant Chunks
   │
   ▼
Context Construction
   │
   ▼
Gemini
   │
   ▼
Answer + Sources
```

The frontend can display:

```text
Answer

Self-attention is ...

Retrieved Sources

Page 2 · Chunk 7
Page 6 · Chunk 25
...
```

---

# Why RAG?

Large language models provide broad pretrained knowledge, but directly asking a model questions about an uploaded research paper introduces several challenges.

## Context Size

Large research papers can contain substantial amounts of text.

Sending an entire document with every question can be inefficient and unnecessarily expensive.

---

## Grounding

A language model may generate information that is not actually present in the uploaded document.

RAG provides relevant document passages as context before generation.

---

## Traceability

A generated answer without source information makes it difficult for a researcher to verify where the information came from.

ResearchPilot AI therefore returns retrieved source chunks together with the generated answer.

---

## Retrieval

Instead of processing the entire document for every question, the system retrieves the most relevant chunks.

This creates a separation between:

```text
Retrieval
```

and:

```text
Generation
```

---

# Data Flow

## Upload Flow

```text
Browser
   │
   │ POST /upload
   ▼
FastAPI
   │
   ├── Store document metadata
   │
   ├── Extract text
   │
   ├── Split into chunks
   │
   ├── Generate embeddings
   │
   └── Upsert vectors
          │
          ▼
       Qdrant
```

---

## Question Flow

```text
Browser
   │
   │ POST /ask
   ▼
FastAPI
   │
   ▼
RAG Pipeline
   │
   ├── Process question
   │
   ├── Generate query embedding
   │
   ├── Filter by document_id
   │
   ├── Search Qdrant
   │
   ├── Select relevant chunks
   │
   ├── Build context
   │
   └── Generate answer
          │
          ▼
        Gemini
          │
          ▼
    Answer + Sources
          │
          ▼
       Frontend
```

---

# Error Handling

Typical API errors include:

```text
400 Bad Request
404 Not Found
422 Validation Error
500 Internal Server Error
```

FastAPI provides structured validation errors through its API layer and OpenAPI documentation.

---

# Troubleshooting

## Frontend Shows "Failed to Fetch"

Check:

1. Is the backend running?
2. Is `VITE_API_URL` correct?
3. Was Vercel redeployed after changing the environment variable?
4. Is the backend CORS configuration allowing the frontend origin?
5. Check the browser developer console for the failed request.
6. Check the Railway backend logs.

---

## Qdrant Returns `403 Forbidden`

Check:

```env
QDRANT_URL=...
QDRANT_API_KEY=...
```

Make sure the API key belongs to the Qdrant cluster specified by `QDRANT_URL`.

---

## Qdrant Returns an Index Error

If Qdrant returns an error similar to:

```text
Index required but not found for "document_id"
```

the `document_id` payload field needs to be indexed.

The retrieval system uses:

```text
document_id
```

for document-specific filtering.

Create a Qdrant payload index for this field.

---

## PostgreSQL Connection Error

Check:

```env
DATABASE_URL=...
```

When using Docker Compose, containers should normally connect to PostgreSQL using the PostgreSQL service name rather than `localhost`.

For example:

```text
postgres
```

can be used as the hostname from another Docker container when the service is named `postgres`.

---

## Gemini API Errors

Check:

```env
GEMINI_API_KEY=...
```

Also verify that the configured Gemini model is available for the API account being used.

---

# Security

Never commit sensitive credentials to GitHub.

Do not commit:

```text
.env
```

Sensitive values include:

- Gemini API keys
- Qdrant API keys
- PostgreSQL passwords
- Database connection strings
- Authentication tokens
- Other private credentials

Use:

```text
.env
```

for local development.

Use the deployment platform's environment-variable management for production.

---

# Performance Considerations

Embedding generation can be one of the slower stages during document ingestion.

For example:

```text
PDF
 │
 ▼
45 Chunks
 │
 ▼
Embedding Batches
 │
 ▼
Qdrant Indexing
```

Embedding latency can depend on:

- Document size
- Number of chunks
- CPU resources
- Model loading time
- Deployment environment

The application generates embeddings during ingestion so that subsequent questions can reuse the stored vectors rather than embedding the document again.

---

# Current Limitations

ResearchPilot AI v1.0.0 is the first stable production release.

Current limitations include:

- PDF processing is the primary document workflow.
- Retrieval quality depends on chunking and embedding quality.
- Generated answers can still contain language-model errors.
- Retrieved sources do not guarantee that every generated claim is correct.
- Large documents may require significant time for embedding generation.
- Production functionality depends on external Gemini and Qdrant services.
- The current embedding model is a general-purpose sentence-transformer.
- Qdrant client and server versions should remain compatible.
- Authentication and multi-user access control are not currently implemented as the primary focus of v1.0.0.

---

# Development Workflow

A typical development cycle is:

```text
1. Modify Code
       │
       ▼
2. Run Locally
       │
       ▼
3. Test Backend
       │
       ▼
4. Test Frontend
       │
       ▼
5. Upload Test PDF
       │
       ▼
6. Ask Test Questions
       │
       ▼
7. Verify Retrieved Sources
       │
       ▼
8. Commit Changes
       │
       ▼
9. Push to GitHub
       │
       ▼
10. Deploy
       │
       ▼
11. Test Production
```

---

# Git Workflow

## Create a Feature Branch

```bash
git checkout -b feature/my-feature
```

## Stage Changes

```bash
git add .
```

## Commit Changes

```bash
git commit -m "Add my feature"
```

## Push the Branch

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

---

## Directly Push to Main

If the project workflow allows direct pushes to `main`:

```bash
git add .
git commit -m "Describe the change"
git push origin main
```

---

# Testing Checklist

Before submitting changes, verify the complete workflow.

```text
✓ Backend starts
✓ Frontend starts
✓ PostgreSQL connects
✓ Qdrant connects
✓ PDF uploads
✓ PDF is processed
✓ Chunks are created
✓ Embeddings are generated
✓ Vectors are indexed
✓ Questions return answers
✓ Retrieved sources are returned
✓ Conversations are persisted
```

For production:

```text
✓ Railway deployment succeeds
✓ Backend health endpoint works
✓ Vercel frontend loads
✓ Frontend can reach Railway
✓ PDF upload works
✓ Question answering works
✓ Sources are displayed
✓ Conversation history works
```

---

# Release History

## v1.0.0

First stable production release.

### Included

- PDF upload
- Document processing
- Text chunking
- Embedding generation
- Qdrant vector storage
- Document-specific semantic retrieval
- Retrieval-Augmented Generation
- Gemini integration
- Source retrieval
- Conversation history
- PostgreSQL persistence
- FastAPI backend
- React frontend
- Vite frontend build system
- Docker-based local development
- Railway backend deployment
- Vercel frontend deployment

### Release

https://github.com/us-utkarshsri07/ResearchPilotAI/releases/tag/v1.0.0

---

# Roadmap

## Retrieval

- [ ] Improved hybrid retrieval
- [ ] Better reranking strategies
- [ ] Retrieval evaluation
- [ ] Query expansion
- [ ] Metadata-aware retrieval
- [ ] Improved chunking strategies

## Documents

- [ ] Additional document formats
- [ ] Improved PDF parsing
- [ ] Table extraction
- [ ] Figure extraction
- [ ] OCR support
- [ ] Document summarization

## AI

- [ ] Multiple LLM providers
- [ ] Model selection
- [ ] Streaming responses
- [ ] Improved citation grounding
- [ ] Answer confidence estimation
- [ ] Structured research summaries

## User Experience

- [ ] Authentication
- [ ] Multi-user workspaces
- [ ] Improved document management
- [ ] Better conversation organization
- [ ] Search across multiple documents
- [ ] Research workspace dashboard

## Infrastructure

- [ ] Background document processing
- [ ] Job queues
- [ ] Caching
- [ ] Improved observability
- [ ] Automated testing
- [ ] CI/CD improvements
- [ ] Production metrics

---

# Contributing

Contributions are welcome.

## Development Setup

Clone the repository:

```bash
git clone https://github.com/us-utkarshsri07/ResearchPilotAI.git
cd ResearchPilotAI
```

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make your changes and test them locally.

Then:

```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Open a Pull Request and describe:

- What changed
- Why the change was made
- How it was tested
- Any known limitations

---

# License

This project currently does not specify a license.

If an open-source license is added later, this section should be updated accordingly.

For example:

```text
MIT License
```

The complete license terms should be available in:

```text
LICENSE
```

---

# Acknowledgements

ResearchPilot AI is built using the following technologies and services:

- [React](https://react.dev/)
- [Vite](https://vite.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Qdrant](https://qdrant.tech/)
- [Sentence Transformers](https://www.sbert.net/)
- [Docker](https://www.docker.com/)
- Gemini
- Railway
- Vercel

---

# Project Status

**Current Release: `v1.0.0`**

ResearchPilot AI is currently deployed as an end-to-end application.

Current production architecture:

```text
                  Vercel
                    │
                    ▼
             React Frontend
                    │
                    ▼
                 Railway
                    │
                    ▼
              FastAPI Backend
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     PostgreSQL          RAG Pipeline
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                 Qdrant              Gemini
                 Cloud                 LLM
                    │                   │
                    ▼                   ▼
               Retrieved           Generated
                Context              Answer
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                         Answer +
                          Sources
```

---

# Built for Research

ResearchPilot AI is designed around a simple principle:

> **Don't just generate an answer. Make it possible to trace the answer back to the document.**

Upload a research paper, retrieve relevant evidence, ask questions in natural language, and inspect the sources used to generate the response.

---

## Version

```text
ResearchPilot AI
v1.0.0
```
