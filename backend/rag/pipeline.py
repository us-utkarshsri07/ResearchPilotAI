print(">>> Loading RAG Pipeline <<<")

from backend.core.config import (
    FINAL_TOP_K,
    RETRIEVAL_TOP_K,
    HYBRID_TOP_K,
)

from backend.llm.gemini_client import (
    GeminiClient,
)

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

    def __init__(self):

        self.chunks = []

        # Initialize embedding model once.
        self.embedding_model = (
            EmbeddingModel()
        )

        # One shared vector collection
        # for all uploaded documents.
        self.vector_store = (
            VectorStore()
        )

        self.hybrid_search = (
            HybridSearch()
        )

        self.reranker = (
            CrossEncoderReranker()
        )

        self.llm = GeminiClient()

        self.bm25_search = None


    def add_chunks(
        self,
        chunks,
    ):

        if not chunks:

            raise ValueError(
                "Cannot index an empty list "
                "of chunks."
            )

        print(

            f">>> Creating embeddings for "
            f"{len(chunks)} chunks <<<"

        )

        texts = [

            chunk.content
            for chunk in chunks

        ]

        embeddings = (
            self.embedding_model
            .embed_documents(texts)
        )

        print(
            ">>> Adding embeddings to "
            "vector store <<<"
        )

        self.vector_store.add_chunks(

            chunks=chunks,

            embeddings=embeddings,

        )

        # Keep all chunks in memory so BM25
        # can search across all documents.
        self.chunks.extend(chunks)

        # Rebuild BM25 with the complete
        # document collection.
        self.bm25_search = BM25Search(

            chunks=self.chunks

        )

        print(

            f">>> Total indexed chunks: "
            f"{len(self.chunks)} <<<"

        )


    def _get_chunks_for_documents(
        self,
        document_ids: list[str] | None,
    ):

        # Empty document_ids means
        # search across every document.
        if not document_ids:

            return self.chunks

        selected_ids = set(
            document_ids
        )

        return [

            chunk

            for chunk in self.chunks

            if (
                chunk.metadata.document_id
                in selected_ids
            )

        ]


    def build_context(
        self,
        results,
    ):

        context_parts = []

        for index, (
            chunk,
            score,
        ) in enumerate(

            results,

            start=1,

        ):

            context_parts.append(

                f"""[Source {index}]

Document: {chunk.metadata.filename}

Page: {chunk.metadata.page_number}

Chunk: {chunk.metadata.chunk_index}

{chunk.content}"""

            )

        return "\n\n".join(
            context_parts
        )


    def build_conversation_context(

        self,

        conversation_history: (
            list[dict] | None
        ),

    ) -> str:

        if not conversation_history:

            return (
                "No previous conversation."
            )

        history_parts = []

        for message in (
            conversation_history
        ):

            role = message.get(
                "role"
            )

            content = message.get(
                "content"
            )

            if not role or not content:

                continue

            if role == "user":

                history_parts.append(

                    f"User: {content}"

                )

            elif role == "assistant":

                history_parts.append(

                    f"Assistant: {content}"

                )

        if not history_parts:

            return (
                "No previous conversation."
            )

        return "\n".join(
            history_parts
        )


    def answer(

        self,

        query: str,

        document_ids: (
            list[str] | None
        ) = None,

        conversation_history: (
            list[dict] | None
        ) = None,

        retrieval_k: int = (
            RETRIEVAL_TOP_K
        ),

        final_k: int = (
            FINAL_TOP_K
        ),

    ):

        if not query.strip():

            raise ValueError(
                "Question cannot be empty."
            )


        selected_chunks = (
            self._get_chunks_for_documents(
                document_ids
            )
        )


        if not selected_chunks:

            return {

                "answer": (
                    "The selected documents do "
                    "not contain enough information "
                    "to answer this question."
                ),

                "sources": [],

            }


        # Step 1:
        # Create query embedding.
        query_embedding = (

            self.embedding_model
            .embed_query(query)

        )


        # Step 2:
        # Semantic search.
        semantic_results = (

            self.vector_store.search_chunks(

                query_embedding=(
                    query_embedding
                ),

                top_k=retrieval_k,

                document_ids=document_ids,

            )

        )


        # Step 3:
        # Create BM25 only for the
        # selected documents.
        selected_bm25 = BM25Search(

            chunks=selected_chunks

        )

        bm25_results = (

            selected_bm25.search(

                query=query,

                top_k=retrieval_k,

            )

        )


        # Step 4:
        # Hybrid search.
        hybrid_results = (

            self.hybrid_search.fuse(

                semantic_results=(
                    semantic_results
                ),

                bm25_results=(
                    bm25_results
                ),

                top_k=(
                    HYBRID_TOP_K
                ),

            )

        )


        # Step 5:
        # Rerank retrieved chunks.
        reranked_results = (

            self.reranker.rerank(

                query=query,

                candidates=(
                    hybrid_results
                ),

                top_k=final_k,

            )

        )


        if not reranked_results:

            return {

                "answer": (

                    "The provided research "
                    "context does not contain "
                    "enough information to answer "
                    "this question."

                ),

                "sources": [],

            }


        # Step 6:
        # Build research context.
        context = self.build_context(

            reranked_results

        )


        # Step 7:
        # Build conversation context.
        conversation_context = (

            self.build_conversation_context(

                conversation_history

            )

        )


        # Step 8:
        # Create Gemini prompt.
        prompt = f"""

You are ResearchPilot AI.

Answer the user's question using ONLY the research context.

Previous conversation is provided only to help understand
follow-up questions and references such as "it", "that",
"this method", or "explain more".

Do not use information from the conversation as a factual
source unless it is supported by the research context.

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

Previous conversation:

{conversation_context}

Research context:

{context}

Question:

{query}

Answer:

"""


        # Step 9:
        # Generate answer.
        response = self.llm.generate(
            prompt
        )


        return {

            "answer": response,

            "sources": (
                reranked_results
            ),

        }