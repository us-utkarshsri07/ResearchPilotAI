from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from backend.rag.ingestion.schemas import Chunk


class VectorStore:

    def __init__(
        self,
        collection_name: str = "researchpilot_chunks",
        vector_size: int = 384,
    ):
        self.collection_name = collection_name

        self.client = QdrantClient(
            path="data/qdrant"
        )

        self._create_collection(
            vector_size=vector_size
        )

    def _create_collection(
        self,
        vector_size: int,
    ) -> None:

        if not self.client.collection_exists(
            self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def clear_collection(self) -> None:

        if self.client.collection_exists(
            self.collection_name
        ):
            self.client.delete_collection(
                collection_name=self.collection_name
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )

    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:

        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            point = PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "source": chunk.metadata.source,
                    "filename": chunk.metadata.filename,
                    "page_number": chunk.metadata.page_number,
                    "document_id": chunk.metadata.document_id,
                    "chunk_id": chunk.metadata.chunk_id,
                    "chunk_index": chunk.metadata.chunk_index,
                },
            )

            points.append(point)

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
        )

        return results.points

    def search_chunks(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[tuple[Chunk, float]]:

        results = self.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        chunks = []

        for result in results:

            payload = result.payload

            chunk = Chunk(
                content=payload["content"],
                metadata={
                    "source": payload["source"],
                    "filename": payload["filename"],
                    "page_number": payload["page_number"],
                    "document_id": payload["document_id"],
                    "chunk_id": payload["chunk_id"],
                    "chunk_index": payload["chunk_index"],
                },
            )

            chunks.append(
                (
                    chunk,
                    float(result.score),
                )
            )

        return chunks