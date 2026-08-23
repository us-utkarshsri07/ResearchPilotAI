from backend.rag.chunking.text_chunker import TextChunker

from backend.rag.ingestion.pdf_loader import PDFLoader

from backend.rag.pipeline import RAGPipeline


def main():

    # Load the PDF
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    # Create chunks
    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(
        documents
    )

    # Initialize the complete RAG pipeline
    rag_pipeline = RAGPipeline(
        chunks=chunks
    )

    # Ask a question
    query = (
        "How does multi-head attention work "
        "in the Transformer?"
    )

    print("\nQuestion:")
    print(query)

    print("\nGenerating answer...\n")

    # Generate grounded answer
    result = rag_pipeline.answer(
        query=query,
        retrieval_k=10,
        final_k=5,
    )

    print("=" * 70)

    print("RESEARCHPILOT ANSWER")

    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)

    print("SOURCES USED")

    print("=" * 70)

    for index, (chunk, score) in enumerate(
        result["sources"],
        start=1,
    ):

        print(
            f"\n[{index}] "
            f"Page {chunk.metadata.page_number} | "
            f"Chunk {chunk.metadata.chunk_index}"
        )

        print(
            f"Reranker Score: {score:.4f}"
        )

        print(
            chunk.content[:300]
        )


if __name__ == "__main__":
    main()