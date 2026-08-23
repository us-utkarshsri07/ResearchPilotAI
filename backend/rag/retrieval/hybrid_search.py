from collections import defaultdict

from backend.rag.ingestion.schemas import Chunk


class HybridSearch:
    def __init__(
        self,
        rrf_k: int = 60,
    ):
        self.rrf_k = rrf_k

    def fuse(
        self,
        semantic_results,
        bm25_results,
        top_k: int = 5,
    ) -> list[tuple[Chunk, float]]:

        fused_scores = defaultdict(float)
        chunks_by_id = {}

        # Semantic results
        for rank, (chunk, _) in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = chunk.metadata.chunk_id

            fused_scores[chunk_id] += (
                1 / (self.rrf_k + rank)
            )

            chunks_by_id[chunk_id] = chunk

        # BM25 results
        for rank, (chunk, _) in enumerate(
            bm25_results,
            start=1,
        ):
            chunk_id = chunk.metadata.chunk_id

            fused_scores[chunk_id] += (
                1 / (self.rrf_k + rank)
            )

            chunks_by_id[chunk_id] = chunk

        ranked_ids = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )[:top_k]

        results = []

        for chunk_id in ranked_ids:
            results.append(
                (
                    chunks_by_id[chunk_id],
                    fused_scores[chunk_id],
                )
            )

        return results