from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ExtractedDocumentMetadata(BaseModel):
    document_id: str
    filename: str
    source: str
    page_count: int
    file_size: int
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    upload_time: datetime


class DocumentMetadata(BaseModel):
    source: str
    filename: str
    page_number: int
    document_id: str


class Document(BaseModel):
    content: str
    metadata: DocumentMetadata


class ChunkMetadata(DocumentMetadata):
    chunk_id: str
    chunk_index: int


class Chunk(BaseModel):
    content: str
    metadata: ChunkMetadata