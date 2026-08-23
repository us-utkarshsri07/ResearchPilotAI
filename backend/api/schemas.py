from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    page_number: int
    chunk_index: int
    score: float
    content: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]