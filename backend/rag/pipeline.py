print(">>> Loading NEW Pipeline <<<")

from backend.core.config import (
    FINAL_TOP_K,
    RETRIEVAL_TOP_K,
)

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
                f"""[Source {index}]
Page: {chunk.metadata.page_number}
Chunk: {chunk.metadata.chunk_index}

{chunk.content}"""
            )

        return "\n\n".join(context_parts)


    def answer(

        self,

        query: str,

        retrieval_k: int = RETRIEVAL_TOP_K,

        final_k: int = FINAL_TOP_K,

    ):

        # Step 1: Create query embedding

        query_embedding = (
            self.embedding_model.embed_query(
                query
            )
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


        # Step 5: Rerank results

        reranked_results = (
            self.reranker.rerank(
                query=query,
                candidates=hybrid_results,
                top_k=final_k,
            )
        )


        # Step 6: Build research context

        context = self.build_context(
            reranked_results
        )


        # Step 7: Create prompt

        prompt = f"""

You are ResearchPilot AI.

Answer the user's question using ONLY the research context.

Instructions:
- Give the answer directly.
- Do not explain your reasoning.
- Do not mention the research context or sources unless citing them.
- Keep the answer concise, maximum 2 short paragraphs.
- Use plain text.
- Do NOT use Markdown.
- Do NOT use bullet points unless necessary.
- Use real line breaks, not the characters \\n.
- Cite factual statements using [1], [2], etc.
- Do not invent citations.
- If the answer cannot be found in the context, say exactly:
The provided research context does not contain enough information to answer this question.

Research context:
{context}

Question:
{query}

Answer:"""
        # Step 8: Generate answer

        response = self.llm.generate(
            prompt
        )


        return {

            "answer": response,

            "sources": reranked_results,

        }