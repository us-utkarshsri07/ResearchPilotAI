print(">>> Loading RAG Pipeline <<<")

import re

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

        for message in conversation_history:

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


    def is_follow_up_question(
        self,
        query: str,
    ) -> bool:

        """
        Determines whether the current question
        likely depends on previous conversation.

        Examples of follow-up questions:

        - Explain that in simpler terms.
        - Give me an example.
        - Why is it useful?
        - How does it work?
        - Tell me more about this.

        A new explicit question such as:

        - What are applications of Attention?
        - What is positional encoding?

        should usually be retrieved independently.
        """

        normalized_query = (
            query.lower()
            .strip()
        )

        normalized_query = re.sub(
            r"\s+",
            " ",
            normalized_query,
        )

        follow_up_patterns = [

            # Direct references.
            r"\bthat\b",
            r"\bthis\b",
            r"\bit\b",
            r"\bthey\b",
            r"\bthem\b",
            r"\bthose\b",
            r"\bthese\b",

            # Explanation follow-ups.
            r"^explain\b",
            r"^explain that\b",
            r"^explain this\b",
            r"^explain it\b",

            # Example follow-ups.
            r"^give me an example",
            r"^give an example",
            r"^show me an example",
            r"^example\b",

            # Simplification follow-ups.
            r"^simplify\b",
            r"^make it simpler",
            r"^say it simply",
            r"^in simpler terms",
            r"^in simple terms",

            # Continuation follow-ups.
            r"^why\b.*\buseful\b",
            r"^why is it useful",
            r"^why is that useful",
            r"^how does it work",
            r"^how does that work",
            r"^how does this work",
            r"^tell me more",
            r"^what about\b",
            r"^can you elaborate",
            r"^elaborate\b",
            r"^more details",
            r"^go deeper",
            r"^continue\b",

            # Short context-dependent questions.
            r"^why\?$",
            r"^how\?$",
            r"^what do you mean\??$",
            r"^can you explain\??$",
        ]

        for pattern in follow_up_patterns:

            if re.search(
                pattern,
                normalized_query,
            ):

                return True

        return False


    def build_retrieval_query(
        self,
        query: str,
        conversation_history: (
            list[dict] | None
        ),
    ) -> str:

        """
        Builds a retrieval query that can handle
        both independent questions and follow-up
        questions.

        Independent question:
            "What are applications of Attention
            in our model?"

        The original question is used directly.

        Follow-up question:
            "Explain that in simpler terms."

        Recent conversation context is added so
        retrieval understands what "that" refers
        to.
        """

        if not conversation_history:

            print(
                ">>> Independent retrieval query "
                "created: no conversation history <<<"
            )

            return query


        is_follow_up = (
            self.is_follow_up_question(
                query
            )
        )

        if not is_follow_up:

            print(
                ">>> Independent retrieval query "
                "created: current question does "
                "not depend on previous context <<<"
            )

            print(
                f"Current question:\n{query}"
            )

            return query


        history_parts = []

        # Use recent messages only.
        # This prevents the retrieval query from
        # growing indefinitely.
        recent_history = (
            conversation_history[-8:]
        )

        for message in recent_history:

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

            return query


        conversation_context = (
            "\n".join(
                history_parts
            )
        )


        retrieval_query = f"""
Previous conversation:

{conversation_context}

Current question:

{query}
""".strip()


        print(
            ">>> Conversation-aware retrieval "
            "query created: follow-up detected <<<"
        )

        print(
            retrieval_query
        )

        return retrieval_query


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


        # --------------------------------
        # Step 0:
        # Build retrieval query.
        #
        # Independent questions use only
        # the current question.
        #
        # Follow-up questions include
        # recent conversation context.
        # --------------------------------

        retrieval_query = (
            self.build_retrieval_query(
                query=query,
                conversation_history=(
                    conversation_history
                ),
            )
        )


        # --------------------------------
        # Step 1:
        # Get selected document chunks.
        # --------------------------------

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


        # --------------------------------
        # Step 2:
        # Create query embedding.
        # --------------------------------

        query_embedding = (
            self.embedding_model
            .embed_query(
                retrieval_query
            )
        )


        # --------------------------------
        # Step 3:
        # Semantic search.
        # --------------------------------

        semantic_results = (
            self.vector_store.search_chunks(
                query_embedding=(
                    query_embedding
                ),
                top_k=retrieval_k,
                document_ids=document_ids,
            )
        )


        # --------------------------------
        # Step 4:
        # Create BM25 only for selected
        # documents.
        # --------------------------------

        selected_bm25 = BM25Search(
            chunks=selected_chunks
        )

        bm25_results = (
            selected_bm25.search(
                query=retrieval_query,
                top_k=retrieval_k,
            )
        )


        # --------------------------------
        # Step 5:
        # Hybrid search.
        # --------------------------------

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


        # --------------------------------
        # Step 6:
        # Rerank retrieved chunks.
        # --------------------------------

        reranked_results = (
            self.reranker.rerank(
                query=retrieval_query,
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


        # --------------------------------
        # Step 7:
        # Build research context.
        # --------------------------------

        context = self.build_context(
            reranked_results
        )


        # --------------------------------
        # Step 8:
        # Build conversation context.
        #
        # Conversation is still provided to
        # Gemini for understanding follow-up
        # references.
        # --------------------------------

        conversation_context = (
            self.build_conversation_context(
                conversation_history
            )
        )


        # --------------------------------
        # Step 9:
        # Create Gemini prompt.
        # --------------------------------

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


        # --------------------------------
        # Step 10:
        # Generate answer.
        # --------------------------------

        response = self.llm.generate(
            prompt
        )


        return {
            "answer": response,
            "sources": reranked_results,
        }