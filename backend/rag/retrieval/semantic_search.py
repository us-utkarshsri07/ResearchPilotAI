import numpy as np

from backend.rag.ingestion.schemas import Chunk


class SemanticSearch:
    def search(
        self,
        query_embedding: list[float],
        document_embeddings: list[list[float]],
        chunks: list[Chunk],
        top_k: int = 5,
    ) -> list[tuple[Chunk, float]]:

        query_vector = np.array(query_embedding)
        document_vectors = np.array(document_embeddings)

        scores = document_vectors @ query_vector

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            results.append(
                (
                    chunks[index],
                    float(scores[index]),
                )
            )

        return results