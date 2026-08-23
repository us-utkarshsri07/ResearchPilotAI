from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.embeddings.embedding_model import EmbeddingModel
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.retrieval.bm25_search import BM25Search
from backend.rag.retrieval.hybrid_search import HybridSearch
from backend.rag.retrieval.vector_store import VectorStore


def main():
    # Load PDF
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    # Create chunks
    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(documents)

    # Embedding model
    embedding_model = EmbeddingModel()

    # Create query
    query = (
        "How does multi-head attention work "
        "in the Transformer?"
    )

    query_embedding = embedding_model.embed_query(
        query
    )

    # ---------------------------
    # Semantic Search
    # ---------------------------

    vector_store = VectorStore()

    semantic_results = vector_store.search_chunks(
        query_embedding=query_embedding,
        top_k=10,
    )

    # ---------------------------
    # BM25 Search
    # ---------------------------

    bm25_search = BM25Search(
        chunks=chunks
    )

    bm25_results = bm25_search.search(
        query=query,
        top_k=10,
    )

    # ---------------------------
    # Hybrid Fusion
    # ---------------------------

    hybrid_search = HybridSearch()

    results = hybrid_search.fuse(
        semantic_results=semantic_results,
        bm25_results=bm25_results,
        top_k=5,
    )

    # Display results
    print(f"\nQuery: {query}")
    print("\nHybrid Search Results:\n")

    for rank, (chunk, score) in enumerate(
        results,
        start=1,
    ):
        print("=" * 70)
        print(f"Rank: {rank}")
        print(f"RRF Score: {score:.6f}")
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