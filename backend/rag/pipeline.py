print(">>> Loading RAG Pipeline <<<")

from backend.core.config import (
    FINAL_TOP_K,
    RETRIEVAL_TOP_K,
    HYBRID_TOP_K,
)

from backend.llm.gemini_client import GeminiClient

from backend.rag.embeddings.embedding_model import (
    EmbeddingModel,
)

from backend.rag.reranking.cross_encoder import (
    CrossEncoderReranker,
)

from backend.rag.retrieval.bm25_search import (
    BM25Search,
)

from backend.rag.retrieval.hybrid_search import (
    HybridSearch,
)

from backend.rag.retrieval.vector_store import (
    VectorStore,
)


class RAGPipeline:

    def __init__(self, chunks):

        if not chunks:
            raise ValueError(
                "Cannot create a RAG pipeline without chunks."
            )

        self.chunks = chunks

        # Initialize embedding model
        self.embedding_model = EmbeddingModel()

        # Initialize vector store
        self.vector_store = VectorStore()

        # Initialize BM25
        self.bm25_search = BM25Search(
            chunks=self.chunks
        )

        # Initialize hybrid search
        self.hybrid_search = HybridSearch()

        # Initialize reranker
        self.reranker = CrossEncoderReranker()

        # Initialize Gemini client
        self.llm = GeminiClient()

        # Create embeddings and store chunks
        self._index_chunks()


    def _index_chunks(self):

        print(
            f">>> Creating embeddings for "
            f"{len(self.chunks)} chunks <<<"
        )

        texts = [
            chunk.content
            for chunk in self.chunks
        ]

        embeddings = (
            self.embedding_model.embed_documents(
                texts
            )
        )

        print(
            ">>> Adding embeddings to vector store <<<"
        )

        self.vector_store.add_chunks(
            chunks=self.chunks,
            embeddings=embeddings,
        )

        print(
            ">>> Document indexing complete <<<"
        )


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

        return "\n\n".join(
            context_parts
        )


    def answer(
        self,
        query: str,
        retrieval_k: int = RETRIEVAL_TOP_K,
        final_k: int = FINAL_TOP_K,
    ):

        if not query.strip():
            raise ValueError(
                "Question cannot be empty."
            )

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
                top_k=HYBRID_TOP_K,
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


        # Handle no relevant results

        if not reranked_results:

            return {
                "answer": (
                    "The provided research context does not "
                    "contain enough information to answer "
                    "this question."
                ),
                "sources": [],
            }


        # Step 6: Build research context

        context = self.build_context(
            reranked_results
        )


        # Step 7: Create Gemini prompt

        prompt = f"""
You are ResearchPilot AI.

Answer the user's question using ONLY the research context.

Instructions:

- Give the answer directly.
- Do not explain your reasoning.
- Keep the answer concise, maximum 2 short paragraphs.
- Use plain text.
- Do not use Markdown.
- Use real line breaks.
- Cite factual statements using [1], [2], etc.
- Do not invent citations.
- Only cite source numbers that exist in the research context.

If the answer cannot be found in the context, say exactly:

The provided research context does not contain enough information to answer this question.

Research context:

{context}

Question:

{query}

Answer:
"""


        # Step 8: Generate answer using Gemini

        response = self.llm.generate(
            prompt
        )


        return {
            "answer": response,
            "sources": reranked_results,
        }