from pathlib import Path
from uuid import uuid4

import pymupdf

from backend.rag.ingestion.schemas import Document, DocumentMetadata
from backend.rag.ingestion.text_cleaner import clean_text

class PDFLoader:
    def load(self, file_path: str) -> list[Document]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {path.suffix}"
            )

        pdf = pymupdf.open(path)

        document_id = str(uuid4())

        documents = []

        for page_number, page in enumerate(pdf, start=1):
            text = clean_text(page.get_text())

            if not text:
                continue

            metadata = DocumentMetadata(
                source=str(path),
                filename=path.name,
                page_number=page_number,
                document_id=document_id,
            )

            document = Document(
                content=text.strip(),
                metadata=metadata,
            )

            documents.append(document)

        pdf.close()

        return documents