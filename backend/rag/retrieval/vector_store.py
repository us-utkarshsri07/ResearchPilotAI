from threading import Lock

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

from backend.rag.ingestion.schemas import Chunk

from backend.core.config import (
    QDRANT_PATH,
    QDRANT_URL,
)


_client = None

_client_lock = Lock()


def get_qdrant_client() -> QdrantClient:

    global _client

    if _client is None:

        with _client_lock:

            if _client is None:

                if QDRANT_URL:

                    _client = QdrantClient(
                        url=QDRANT_URL
                    )

                else:

                    QDRANT_PATH.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    _client = QdrantClient(
                        path=str(QDRANT_PATH)
                    )

    return _client


def close_qdrant_client() -> None:

    global _client

    with _client_lock:

        if _client is not None:

            _client.close()

            _client = None


class VectorStore:

    def __init__(
        self,
        collection_name: str = (
            "researchpilot_chunks"
        ),
        vector_size: int = 384,
    ):

        self.collection_name = (
            collection_name
        )

        self.vector_size = vector_size

        self.client = (
            get_qdrant_client()
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
                collection_name=(
                    self.collection_name
                ),
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )


    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:

        points = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            point = PointStruct(

                # Use the globally unique chunk ID.
                # This prevents collisions between
                # multiple uploaded documents.
                id=chunk.metadata.chunk_id,

                vector=embedding,

                payload={

                    "content":
                        chunk.content,

                    "source":
                        chunk.metadata.source,

                    "filename":
                        chunk.metadata.filename,

                    "page_number":
                        chunk.metadata.page_number,

                    "document_id":
                        chunk.metadata.document_id,

                    "chunk_id":
                        chunk.metadata.chunk_id,

                    "chunk_index":
                        chunk.metadata.chunk_index,

                },

            )

            points.append(point)

        if points:

            self.client.upsert(
                collection_name=(
                    self.collection_name
                ),
                points=points,
            )


    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ):

        query_filter = None

        if document_ids:

            query_filter = Filter(
                must=[

                    FieldCondition(
                        key="document_id",

                        match=MatchAny(
                            any=document_ids
                        ),
                    )

                ]
            )

        results = self.client.query_points(

            collection_name=(
                self.collection_name
            ),

            query=query_embedding,

            query_filter=query_filter,

            limit=top_k,

        )

        return results.points


    def search_chunks(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        document_ids: list[str] | None = None,
    ) -> list[tuple[Chunk, float]]:

        results = self.search(

            query_embedding=query_embedding,

            top_k=top_k,

            document_ids=document_ids,

        )

        chunks = []

        for result in results:

            payload = result.payload

            chunk = Chunk(

                content=payload[
                    "content"
                ],

                metadata={

                    "source":
                        payload["source"],

                    "filename":
                        payload["filename"],

                    "page_number":
                        payload[
                            "page_number"
                        ],

                    "document_id":
                        payload[
                            "document_id"
                        ],

                    "chunk_id":
                        payload[
                            "chunk_id"
                        ],

                    "chunk_index":
                        payload[
                            "chunk_index"
                        ],

                },

            )

            chunks.append(

                (
                    chunk,
                    float(result.score),
                )

            )

        return chunks