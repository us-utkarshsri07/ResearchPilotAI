from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    conversation_id: int | None = None
    document_id: str | None = None


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
# Conversation schemas
# --------------------------------

class MessageResponse(BaseModel):
    role: str
    content: str


class ConversationResponse(BaseModel):
    conversation_id: int
    document_id: str
    messages: list[MessageResponse]