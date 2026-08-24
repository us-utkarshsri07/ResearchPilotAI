from sentence_transformers import CrossEncoder
from backend.rag.ingestion.schemas import Chunk
from backend.core.config import (
    MIN_RELEVANCE_SCORE,
    RERANKER_MODEL,
)




class CrossEncoderReranker:

    def __init__(
        self,
        model_name: str = RERANKER_MODEL,
    ):
        self.model = CrossEncoder(
            model_name,
            device="cpu",
        )

    def rerank(
        self,
        query: str,
        candidates: list[tuple[Chunk, float]],
        top_k: int = 5,
    ) -> list[tuple[Chunk, float]]:

        # Remove duplicate chunks before reranking
        unique_candidates = {}

        for chunk, score in candidates:
            key = (
                chunk.metadata.source,
                chunk.metadata.page_number,
                chunk.metadata.chunk_index,
            )

            if key not in unique_candidates:
                unique_candidates[key] = (
                    chunk,
                    score,
                )

        candidates = list(
            unique_candidates.values()
        )

        # Handle empty candidates
        if not candidates:
            return []

        # Create query-document pairs
        pairs = [
            (
                query,
                chunk.content,
            )
            for chunk, _ in candidates
        ]

        # Get relevance scores
        scores = self.model.predict(
            pairs
        )

        # Combine chunks with scores
        ranked_results = sorted(
            zip(
                [
                    chunk
                    for chunk, _ in candidates
                ],
                scores,
            ),
            key=lambda item: float(
                item[1]
            ),
            reverse=True,
        )

        # Remove weak or irrelevant results
        filtered_results = [
            (
                chunk,
                float(score),
            )
            for chunk, score in ranked_results
            if float(score)
            >= MIN_RELEVANCE_SCORE
        ]

        # Return the best relevant results
        return filtered_results[:top_k]