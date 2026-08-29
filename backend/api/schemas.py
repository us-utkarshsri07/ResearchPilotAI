from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class QuestionRequest(BaseModel):

    question: str

    conversation_id: int | None = None

    document_id: str | None = None


# --------------------------------
# Source schemas
# --------------------------------

class SourceResponse(BaseModel):

    document_id: str

    filename: str

    page_number: int

    chunk_index: int

    score: float

    content: str


class AnswerResponse(BaseModel):

    conversation_id: int

    answer: str

    sources: list[SourceResponse]


# --------------------------------
# Conversation request schemas
# --------------------------------

class CreateConversationRequest(
    BaseModel
):

    document_id: str


# --------------------------------
# Conversation response schemas
# --------------------------------

class MessageResponse(BaseModel):

    role: str

    content: str

    sources: list[SourceResponse] = Field(
        default_factory=list
    )


class ConversationResponse(BaseModel):

    conversation_id: int

    document_id: str

    messages: list[MessageResponse]


class ConversationListItemResponse(
    BaseModel
):

    conversation_id: int

    created_at: datetime

    message_count: int

    preview: str | None = None