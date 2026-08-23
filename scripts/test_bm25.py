from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.ingestion.pdf_loader import PDFLoader
from backend.rag.retrieval.bm25_search import BM25Search


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

    print(f"\nChunks available: {len(chunks)}")

    # Create BM25 index
    bm25_search = BM25Search(
        chunks=chunks
    )

    # Search
    # query = "positional encoding"
    query = "scaled dot-product attention"

    results = bm25_search.search(
        query=query,
        top_k=5,
    )

    print(f"\nQuery: {query}")
    print("\nTop BM25 results:\n")

    for rank, (chunk, score) in enumerate(
        results,
        start=1,
    ):
        print("=" * 70)
        print(f"Rank: {rank}")
        print(f"BM25 Score: {score:.4f}")
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