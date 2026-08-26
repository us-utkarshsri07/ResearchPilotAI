from contextlib import asynccontextmanager

from pathlib import Path

from uuid import uuid4

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from backend.api.schemas import (
    AnswerResponse,
    QuestionRequest,
    SourceResponse,
)

from backend.core.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)

from backend.rag.chunking.text_chunker import (
    TextChunker,
)

from backend.rag.ingestion.pdf_loader import (
    PDFLoader,
)

from backend.rag.pipeline import (
    RAGPipeline,
)

from backend.rag.retrieval.vector_store import (
    close_qdrant_client,
)


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
):

    yield

    close_qdrant_client()


app = FastAPI(

    title="ResearchPilot AI",

    description=(
        "AI-powered research assistant"
    ),

    version="0.3.0",

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


UPLOAD_DIR = Path(
    "datasets/uploads"
)

UPLOAD_DIR.mkdir(

    parents=True,

    exist_ok=True,

)


# One pipeline indexes all uploaded documents.
pipeline = RAGPipeline()


# Stores uploaded document metadata.
documents = {}


# Conversation history is scoped to the
# selected document set.
conversation_histories = {}


@app.get("/health")
def health_check():

    return {

        "status": "healthy",

        "service": "researchpilot",

        "documents": len(documents),

    }


@app.post("/upload")
async def upload_pdf(

    file: UploadFile = File(...),

):

    if not file.filename:

        raise HTTPException(

            status_code=400,

            detail=(
                "No file was provided."
            ),

        )


    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "Only PDF files are supported."
            ),

        )


    original_filename = file.filename


    unique_filename = (

        f"{uuid4()}_{original_filename}"

    )


    file_path = (

        UPLOAD_DIR /
        unique_filename

    )


    try:

        # Save uploaded PDF.
        content = await file.read()

        with open(
            file_path,
            "wb",
        ) as buffer:

            buffer.write(content)


        # Load PDF and extract metadata.
        loader = PDFLoader()

        (
            documents_from_pdf,
            document_metadata,
        ) = loader.load(

            file_path=str(file_path),

            original_filename=(
                original_filename
            ),

        )


        if not documents_from_pdf:

            raise HTTPException(

                status_code=400,

                detail=(

                    "No readable text was found "
                    "in the PDF."

                ),

            )


        # Chunk PDF.
        chunker = TextChunker(

            chunk_size=CHUNK_SIZE,

            chunk_overlap=(
                CHUNK_OVERLAP
            ),

        )


        chunks = (
            chunker.chunk_documents(
                documents_from_pdf
            )
        )


        if not chunks:

            raise HTTPException(

                status_code=400,

                detail=(

                    "No chunks could be created "
                    "from the PDF."

                ),

            )


        # Add this document to the existing
        # shared RAG pipeline.
        pipeline.add_chunks(
            chunks
        )


        # Store metadata for the document.
        document_id = (
            document_metadata.document_id
        )


        documents[document_id] = {

            "document_id":
                document_id,

            "filename":
                document_metadata.filename,

            "source":
                document_metadata.source,

            "page_count":
                document_metadata.page_count,

            "file_size":
                document_metadata.file_size,

            "title":
                document_metadata.title,

            "author":
                document_metadata.author,

            "creation_date":
                document_metadata.creation_date,

            "upload_time":
                document_metadata
                .upload_time
                .isoformat(),

            "chunks":
                len(chunks),

        }


        return {

            "message": (

                "PDF uploaded and processed "
                "successfully."

            ),

            "filename":
                original_filename,

            "pages":
                document_metadata.page_count,

            "chunks":
                len(chunks),

            "document_metadata": (

                documents[document_id]

            ),

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


@app.get("/documents")
def get_documents():

    return {

        "documents": list(
            documents.values()
        )

    }


@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(

    request: QuestionRequest,

):

    if not documents:

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


    # If document IDs were specified,
    # validate them.
    if request.document_id:

        invalid_document_ids = [

            document_id

            for document_id
            in request.document_id

            if document_id not in documents

        ]


        if invalid_document_ids:

            raise HTTPException(

                status_code=400,

                detail=(

                    "One or more selected "
                    "documents do not exist."

                ),

            )


    # Create a stable key for the current
    # document selection.
    #
    # [] means all documents.
    if request.document_id:

        conversation_key = (
            "|".join(
                sorted(
                    request.document_id
                )
            )
        )

    else:

        conversation_key = (
            "__all_documents__"
        )


    conversation_history = (

        conversation_histories.get(
            conversation_key,
            [],
        )

    )


    # Keep only the latest 10 messages.
    recent_history = (
        conversation_history[-10:]
    )


    result = pipeline.answer(

        query=request.question,

        document_ids=(
            request.document_id
            if request.document_id
            else None
        ),

        conversation_history=(
            recent_history
        ),

    )


    # Store user question.
    conversation_history.append(

        {

            "role": "user",

            "content":
                request.question,

        }

    )


    # Store assistant answer.
    conversation_history.append(

        {

            "role": "assistant",

            "content":
                result["answer"],

        }

    )


    conversation_histories[
        conversation_key
    ] = conversation_history


    sources = [

        SourceResponse(

            document_id=(
                chunk.metadata.document_id
            ),

            filename=(
                chunk.metadata.filename
            ),

            page_number=(

                chunk.metadata
                .page_number

            ),

            chunk_index=(

                chunk.metadata
                .chunk_index

            ),

            score=float(score),

            content=chunk.content,

        )

        for chunk, score
        in result["sources"]

    ]


    return AnswerResponse(

        answer=result["answer"],

        sources=sources,

    )