from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from sqlalchemy.orm import Session

from backend.database.database import (
    Base,
    engine,
    get_db,
)

from backend.database import models
from backend.database import crud

from backend.api.schemas import (
    AnswerResponse,
    ConversationResponse,
    MessageResponse,
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
async def lifespan(_app: FastAPI):

    Base.metadata.create_all(
        bind=engine
    )

    yield

    close_qdrant_client()


app = FastAPI(
    title="ResearchPilot AI",
    description="AI-powered research assistant",
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


pipeline = RAGPipeline()


@app.get("/health")
def health_check(
    db: Session = Depends(get_db),
):

    documents = crud.get_documents(
        db
    )

    return {
        "status": "healthy",
        "service": "researchpilot",
        "documents": len(documents),
    }


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
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

        content = await file.read()

        with open(
            file_path,
            "wb",
        ) as buffer:

            buffer.write(
                content
            )

        loader = PDFLoader()

        (
            documents_from_pdf,
            document_metadata,
        ) = loader.load(
            file_path=str(
                file_path
            ),
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

        chunker = TextChunker(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
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

        existing_document = (
            crud.get_document_by_document_id(
                db=db,
                document_id=(
                    document_metadata
                    .document_id
                ),
            )
        )

        if existing_document:

            raise HTTPException(
                status_code=400,
                detail=(
                    "This document already exists."
                ),
            )

        db_document = (
            crud.create_document(
                db=db,
                document_id=(
                    document_metadata
                    .document_id
                ),
                filename=(
                    document_metadata
                    .filename
                ),
                source=(
                    document_metadata
                    .source
                ),
                page_count=(
                    document_metadata
                    .page_count
                ),
                file_size=(
                    document_metadata
                    .file_size
                ),
                title=(
                    document_metadata
                    .title
                ),
                author=(
                    document_metadata
                    .author
                ),
                creation_date=(
                    document_metadata
                    .creation_date
                ),
            )
        )

        pipeline.add_chunks(
            chunks
        )

        return {
            "message": (
                "PDF uploaded and processed "
                "successfully."
            ),
            "filename": (
                db_document.filename
            ),
            "pages": (
                db_document.page_count
            ),
            "chunks": len(chunks),
            "document_metadata": {
                "document_id": (
                    db_document.document_id
                ),
                "filename": (
                    db_document.filename
                ),
                "source": (
                    db_document.source
                ),
                "page_count": (
                    db_document.page_count
                ),
                "file_size": (
                    db_document.file_size
                ),
                "title": (
                    db_document.title
                ),
                "author": (
                    db_document.author
                ),
                "creation_date": (
                    db_document.creation_date
                ),
                "upload_time": (
                    db_document
                    .upload_time
                    .isoformat()
                ),
            },
        }

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()

        print(
            f"Upload failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@app.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
):

    documents = crud.get_documents(
        db
    )

    return {
        "documents": [
            {
                "document_id": (
                    document.document_id
                ),
                "filename": (
                    document.filename
                ),
                "source": (
                    document.source
                ),
                "page_count": (
                    document.page_count
                ),
                "file_size": (
                    document.file_size
                ),
                "title": (
                    document.title
                ),
                "author": (
                    document.author
                ),
                "creation_date": (
                    document.creation_date
                ),
                "upload_time": (
                    document
                    .upload_time
                    .isoformat()
                ),
            }

            for document in documents
        ]
    }

@app.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db),
):

    conversation = (
        crud.get_conversation(
            db=db,
            conversation_id=conversation_id,
        )
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    messages = (
        crud.get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
            limit=100,
        )
    )

    return ConversationResponse(
        conversation_id=conversation.id,
        document_id=(
            conversation.document.document_id
        ),
        messages=[
            MessageResponse(
                role=message.role,
                content=message.content,
            )
            for message in messages
        ],
    )
@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Question cannot be empty."
            ),
        )

    # Get the selected document.
    if request.document_id:

        document = (
            crud.get_document_by_document_id(
                db=db,
                document_id=(
                    request.document_id
                ),
            )
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Document not found."
                ),
            )

    else:

        documents = crud.get_documents(
            db
        )

        if not documents:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No PDF has been uploaded yet."
                ),
            )

        # Current project operates with one document.
        document = documents[0]


    # --------------------------------
    # Conversation handling
    # --------------------------------

    if request.conversation_id:

        conversation = (
            crud.get_conversation(
                db=db,
                conversation_id=(
                    request.conversation_id
                ),
            )
        )

        if not conversation:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Conversation not found."
                ),
            )

        # Ensure conversation belongs
        # to the selected document.
        if (
            conversation.document_id
            != document.id
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Conversation does not belong "
                    "to this document."
                ),
            )

        messages = (
            crud.get_conversation_messages(
                db=db,
                conversation_id=(
                    conversation.id
                ),
                limit=10,
            )
        )

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }

            for message in messages
        ]

    else:

        conversation = (
            crud.create_conversation(
                db=db,
                document_id=document.id,
            )
        )

        conversation_history = []


    # --------------------------------
    # Generate RAG answer
    # --------------------------------

    result = pipeline.answer(
        query=request.question,
        document_ids=[
            document.document_id
        ],
        conversation_history=(
            conversation_history
        ),
    )


    # --------------------------------
    # Save messages
    # --------------------------------

    crud.create_message(
        db=db,
        conversation_id=(
            conversation.id
        ),
        role="user",
        content=request.question,
    )

    crud.create_message(
        db=db,
        conversation_id=(
            conversation.id
        ),
        role="assistant",
        content=(
            result["answer"]
        ),
    )


    # --------------------------------
    # Format sources
    # --------------------------------

    sources = [

        SourceResponse(
            document_id=(
                chunk.metadata
                .document_id
            ),
            filename=(
                chunk.metadata
                .filename
            ),
            page_number=(
                chunk.metadata
                .page_number
            ),
            chunk_index=(
                chunk.metadata
                .chunk_index
            ),
            score=float(
                score
            ),
            content=(
                chunk.content
            ),
        )

        for chunk, score
        in result["sources"]
    ]


    return AnswerResponse(
        conversation_id=(
            conversation.id
        ),
        answer=(
            result["answer"]
        ),
        sources=sources,
    )