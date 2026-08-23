from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.embeddings.embedding_model import EmbeddingModel
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.retrieval.semantic_search import SemanticSearch


def main():
    # 1. Load PDF
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    # 2. Create chunks
    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(documents)

    print(f"\nChunks available: {len(chunks)}")

    # 3. Create embeddings
    embedding_model = EmbeddingModel()

    texts = [
        chunk.content
        for chunk in chunks
    ]

    document_embeddings = embedding_model.embed_documents(
        texts
    )

    print(
        f"Embedding dimension: "
        f"{len(document_embeddings[0])}"
    )

    # 4. Create query embedding
    query = (
        "How does the Transformer model use "
        "attention mechanisms?"
    )

    query_embedding = embedding_model.embed_query(
        query
    )

    # 5. Semantic search
    search = SemanticSearch()

    results = search.search(
        query_embedding=query_embedding,
        document_embeddings=document_embeddings,
        chunks=chunks,
        top_k=5,
    )

    # 6. Display results
    print(f"\nQuery: {query}\n")
    print("Top relevant chunks:\n")

    for rank, (chunk, score) in enumerate(
        results,
        start=1,
    ):
        print("=" * 70)
        print(f"Rank: {rank}")
        print(f"Similarity Score: {score:.4f}")
        print(
            f"Page: "
            f"{chunk.metadata.page_number}"
        )
        print(
            f"Chunk Index: "
            f"{chunk.metadata.chunk_index}"
        )
        print()
        print(chunk.content[:600])
        print()


if __name__ == "__main__":
    main()