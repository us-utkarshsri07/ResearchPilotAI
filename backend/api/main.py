from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import (
    AnswerResponse,
    QuestionRequest,
    SourceResponse,
)

from backend.core.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)

from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.pipeline import RAGPipeline
from backend.rag.retrieval.vector_store import close_qdrant_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    close_qdrant_client()


app = FastAPI(
    title="ResearchPilot AI",
    description="AI-powered research assistant",
    version="0.2.0",
    lifespan=lifespan,
)


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


UPLOAD_DIR = Path("datasets/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


pipeline = None


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "researchpilot",
    }


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
):
    global pipeline

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    unique_filename = (
        f"{uuid4()}_{file.filename}"
    )

    file_path = (
        UPLOAD_DIR / unique_filename
    )

    try:
        # Save uploaded PDF
        content = await file.read()

        with open(
            file_path,
            "wb",
        ) as buffer:
            buffer.write(content)

        # Load PDF
        loader = PDFLoader()

        documents = loader.load(
            str(file_path)
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text was found "
                    "in the PDF."
                ),
            )

        # Chunk PDF
        chunker = TextChunker(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        chunks = chunker.chunk_documents(
            documents
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No chunks could be created "
                    "from the PDF."
                ),
            )

        # Create and index RAG pipeline
        pipeline = RAGPipeline(
            chunks=chunks
        )

        return {
            "message": (
                "PDF uploaded and processed "
                "successfully."
            ),
            "filename": file.filename,
            "pages": len(documents),
            "chunks": len(chunks),
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"Upload failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(
    request: QuestionRequest,
):
    if pipeline is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No PDF has been uploaded yet."
            ),
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "Question cannot be empty."
            ),
        )

    result = pipeline.answer(
        query=request.question,
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