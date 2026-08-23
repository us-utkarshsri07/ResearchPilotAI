from backend.llm.ollama_client import OllamaClient
from backend.rag.embeddings.embedding_model import EmbeddingModel
from backend.rag.reranking.cross_encoder import CrossEncoderReranker
from backend.rag.retrieval.bm25_search import BM25Search
from backend.rag.retrieval.hybrid_search import HybridSearch
from backend.rag.retrieval.vector_store import VectorStore


class RAGPipeline:
    def __init__(self, chunks):
        self.chunks = chunks

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()

        self.bm25_search = BM25Search(
            chunks=self.chunks
        )

        self.hybrid_search = HybridSearch()

        self.reranker = CrossEncoderReranker()

        self.llm = OllamaClient()

    def build_context(self, results):
        context_parts = []

        for index, (chunk, score) in enumerate(
            results,
            start=1,
        ):
            context_parts.append(
                f"""
[Source {index}]
Page: {chunk.metadata.page_number}
Chunk: {chunk.metadata.chunk_index}

Content:
{chunk.content}
"""
            )

        return "\n".join(context_parts)

    def answer(
        self,
        query: str,
        retrieval_k: int = 10,
        final_k: int = 5,
    ):
        # Step 1: Convert query into embedding
        query_embedding = (
            self.embedding_model.embed_query(query)
        )

        # Step 2: Semantic search
        semantic_results = (
            self.vector_store.search_chunks(
                query_embedding=query_embedding,
                top_k=retrieval_k,
            )
        )

        # Step 3: BM25 search
        bm25_results = (
            self.bm25_search.search(
                query=query,
                top_k=retrieval_k,
            )
        )

        # Step 4: Hybrid search
        hybrid_results = (
            self.hybrid_search.fuse(
                semantic_results=semantic_results,
                bm25_results=bm25_results,
                top_k=retrieval_k,
            )
        )

        # Step 5: Cross-encoder reranking
        reranked_results = (
            self.reranker.rerank(
                query=query,
                candidates=hybrid_results,
                top_k=final_k,
            )
        )

        # Step 6: Build context
        context = self.build_context(
            reranked_results
        )

        # Step 7: Create grounded prompt
        prompt = f"""
You are ResearchPilot AI, a research assistant.

Answer the user's question using ONLY the provided
research context.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information,
   explicitly say that the information is not available.
3. Cite claims using the source number format [1], [2].
4. Do not invent citations.
5. Be clear, accurate, and concise.

Research Context:
{context}

User Question:
{query}

Answer:
"""

        # Step 8: Generate answer
        response = self.llm.generate(
            prompt
        )

        return {
            "answer": response,
            "sources": reranked_results,
        }