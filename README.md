# ResearchPilot AI

AI-powered research assistant built around advanced RAG, agentic workflows, evaluation, and production AI engineering.

## Goals

- Advanced RAG
- Hybrid retrieval
- Cross-encoder reranking
- Agentic research with LangGraph
- Citation-backed generation
- RAG evaluation
- Hallucination verification
- ML/DL components
- Production deployment

## Architecture

Document ingestion
→ Chunking
→ Embeddings
→ Hybrid retrieval
→ Reranking
→ LLM
→ Verification
→ Cited response

## Tech Stack

- Python
- PyTorch
- Hugging Face
- Qdrant
- FastAPI
- PostgreSQL
- Redis
- LangGraph
- React
- Docker
- MLflow

## Running

Start the API from the repository root with one worker when using the embedded Qdrant store:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

The application shares one Qdrant client per process and closes it during shutdown. For multiple API workers or multiple API instances, run Qdrant as a server and set `QDRANT_URL` before starting the API:

```powershell
$env:QDRANT_URL = "http://127.0.0.1:6333"
```