from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = BASE_DIR / "datasets"

RAW_DATA_DIR = DATASET_DIR / "raw"


# Retrieval configuration
RETRIEVAL_TOP_K = 10
FINAL_TOP_K = 5


# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# Model configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

LLM_MODEL = "qwen3:4b"


# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"