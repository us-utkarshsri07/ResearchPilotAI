from rank_bm25 import BM25Okapi

from backend.rag.ingestion.schemas import Chunk


class BM25Search:
    def __init__(
        self,
        chunks: list[Chunk],
    ):
        self.chunks = chunks

        self.tokenized_chunks = [
            chunk.content.lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_chunks
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[tuple[Chunk, float]]:

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            results.append(
                (
                    self.chunks[index],
                    float(scores[index]),
                )
            )

        return results