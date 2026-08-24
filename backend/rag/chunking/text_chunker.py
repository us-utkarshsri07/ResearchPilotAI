import re

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
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not text:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]


    def _get_overlap_sentences(
        self,
        sentences: list[str],
    ) -> list[str]:

        overlap = []
        total_length = 0

        for sentence in reversed(sentences):

            sentence_length = len(sentence)

            if (
                total_length + sentence_length
                > self.chunk_overlap
                and overlap
            ):
                break

            overlap.insert(
                0,
                sentence,
            )

            total_length += (
                sentence_length + 1
            )

        return overlap


    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:

        chunks = []
        chunk_index = 0

        for document in documents:

            text = document.content.strip()

            if not text:
                continue

            sentences = self._split_sentences(
                text
            )

            if not sentences:
                continue

            current_chunk = []
            current_length = 0

            for sentence in sentences:

                sentence_length = len(sentence)

                if (
                    current_chunk
                    and current_length
                    + sentence_length
                    + 1
                    > self.chunk_size
                ):

                    chunk_text = " ".join(
                        current_chunk
                    )

                    metadata = ChunkMetadata(
                        source=document.metadata.source,
                        filename=document.metadata.filename,
                        page_number=(
                            document.metadata.page_number
                        ),
                        document_id=(
                            document.metadata.document_id
                        ),
                        chunk_id=str(
                            uuid4()
                        ),
                        chunk_index=chunk_index,
                    )

                    chunks.append(
                        Chunk(
                            content=chunk_text,
                            metadata=metadata,
                        )
                    )

                    chunk_index += 1

                    current_chunk = (
                        self._get_overlap_sentences(
                            current_chunk
                        )
                    )

                    current_length = sum(
                        len(item) + 1
                        for item in current_chunk
                    )

                current_chunk.append(
                    sentence
                )

                current_length += (
                    sentence_length + 1
                )

            if current_chunk:

                chunk_text = " ".join(
                    current_chunk
                )

                metadata = ChunkMetadata(
                    source=document.metadata.source,
                    filename=document.metadata.filename,
                    page_number=(
                        document.metadata.page_number
                    ),
                    document_id=(
                        document.metadata.document_id
                    ),
                    chunk_id=str(
                        uuid4()
                    ),
                    chunk_index=chunk_index,
                )

                chunks.append(
                    Chunk(
                        content=chunk_text,
                        metadata=metadata,
                    )
                )

                chunk_index += 1

        return chunks