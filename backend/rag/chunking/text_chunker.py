from uuid import uuid4

from backend.rag.ingestion.schemas import (
    Chunk,
    ChunkMetadata,
    Document,
)


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:

        chunks = []
        chunk_index = 0

        for document in documents:
            text = document.content

            start = 0

            while start < len(text):
                end = start + self.chunk_size

                chunk_text = text[start:end].strip()

                if chunk_text:
                    metadata = ChunkMetadata(
                        source=document.metadata.source,
                        filename=document.metadata.filename,
                        page_number=document.metadata.page_number,
                        document_id=document.metadata.document_id,
                        chunk_id=str(uuid4()),
                        chunk_index=chunk_index,
                    )

                    chunk = Chunk(
                        content=chunk_text,
                        metadata=metadata,
                    )

                    chunks.append(chunk)

                    chunk_index += 1

                start += (
                    self.chunk_size
                    - self.chunk_overlap
                )

        return chunks