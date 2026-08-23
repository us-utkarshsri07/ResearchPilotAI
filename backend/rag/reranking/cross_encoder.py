from sentence_transformers import CrossEncoder

from backend.rag.ingestion.schemas import Chunk

from backend.core.config import RERANKER_MODEL


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
                unique_candidates[key] = (chunk, score)

        # Convert dictionary values back to a list
        candidates = list(unique_candidates.values())

        # Create query-document pairs
        pairs = [
            (query, chunk.content)
            for chunk, _ in candidates
        ]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Combine chunks with their scores and sort
        ranked_results = sorted(
            zip(
                [chunk for chunk, _ in candidates],
                scores,
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        # Return only the top results
        return [
            (
                chunk,
                float(score),
            )
            for chunk, score in ranked_results[:top_k]
        ]