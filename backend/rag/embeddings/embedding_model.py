from sentence_transformers import SentenceTransformer

from backend.core.config import EMBEDDING_MODEL


class EmbeddingModel:
    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
    ):
        self.model = SentenceTransformer(
            model_name,
            device="cpu",
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str,
    ) -> list[float]:

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()