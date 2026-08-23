from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import (
    AnswerResponse,
    QuestionRequest,
    SourceResponse,
)

from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.pipeline import RAGPipeline


app = FastAPI(
    title="ResearchPilot AI",
    description="AI-powered research assistant",
    version="0.1.0",
)


# CORS MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize pipeline
try:
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(
        documents
    )

    pipeline = RAGPipeline(
        chunks=chunks
    )

    print(">>> RAG Pipeline Ready <<<")

except Exception as e:
    pipeline = None

    print(
        f"Pipeline initialization failed: {e}"
    )


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "researchpilot",
    }


@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(
    request: QuestionRequest
):

    if pipeline is None:
        return {
            "answer": "RAG pipeline is not initialized.",
            "sources": [],
        }

    result = pipeline.answer(
        query=request.question,
        retrieval_k=10,
        final_k=5,
    )

    sources = [
        SourceResponse(
            page_number=chunk.metadata.page_number,
            chunk_index=chunk.metadata.chunk_index,
            score=float(score),
            content=chunk.content,
        )
        for chunk, score in result["sources"]
    ]

    return AnswerResponse(
        answer=result["answer"],
        sources=sources,
    )