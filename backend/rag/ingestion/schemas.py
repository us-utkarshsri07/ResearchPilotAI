from pydantic import BaseModel, Field


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