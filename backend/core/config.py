import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = BASE_DIR / "datasets"

RAW_DATA_DIR = DATASET_DIR / "raw"

QDRANT_PATH = BASE_DIR / "data" / "qdrant"

QDRANT_URL = os.getenv("QDRANT_URL")


# PostgreSQL configuration

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:0711@localhost:5432/researchpilot",
)


# Retrieval configuration

RETRIEVAL_TOP_K = 5

MIN_RETRIEVAL_TOP_K = 3

FINAL_TOP_K = 5

HYBRID_TOP_K = 10

MIN_RELEVANCE_SCORE = 0.0


# Chunking configuration

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


# Model configuration

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

GEMINI_MODEL = "gemini-3.6-flash"