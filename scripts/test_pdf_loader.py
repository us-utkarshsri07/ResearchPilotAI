from backend.rag.chunking.text_chunker import TextChunker
from backend.rag.ingestion.pdf_loader import PDFLoader


def main():
    loader = PDFLoader()

    documents = loader.load(
        "datasets/raw/sample_paper.pdf"
    )

    print(f"\nPages extracted: {len(documents)}")

    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(documents)

    print(f"Chunks created: {len(chunks)}\n")

    for chunk in chunks[:3]:
        print("=" * 70)
        print(
            f"Chunk index: "
            f"{chunk.metadata.chunk_index}"
        )
        print(
            f"Chunk ID: "
            f"{chunk.metadata.chunk_id}"
        )
        print(
            f"Page: "
            f"{chunk.metadata.page_number}"
        )
        print()
        print(chunk.content[:700])
        print()


if __name__ == "__main__":
    main()