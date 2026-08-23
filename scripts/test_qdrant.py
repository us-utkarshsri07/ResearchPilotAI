from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.embeddings.embedding_model import EmbeddingModel
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.retrieval.vector_store import VectorStore


def main():
    # 1. Load PDF
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    # 2. Chunk documents
    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    # 3. Create embeddings
    embedding_model = EmbeddingModel()

    texts = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = embedding_model.embed_documents(
        texts
    )

    print(
        f"Embeddings created: {len(embeddings)}"
    )

    # 4. Store in Qdrant
    vector_store = VectorStore(
        vector_size=len(embeddings[0])
    )

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    print("Chunks stored successfully in Qdrant.")

    # 5. Search Qdrant
    query = (
        "How does multi-head attention work?"
    )

    query_embedding = embedding_model.embed_query(
        query
    )

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=5,
    )

    print(f"\nQuery: {query}")
    print("\nTop results:\n")

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("=" * 70)
        print(f"Rank: {rank}")
        print(f"Score: {result.score:.4f}")
        print(
            f"Page: "
            f"{result.payload['page_number']}"
        )
        print(
            f"Chunk Index: "
            f"{result.payload['chunk_index']}"
        )
        print()
        print(
            result.payload["content"][:600]
        )
        print()


if __name__ == "__main__":
    main()