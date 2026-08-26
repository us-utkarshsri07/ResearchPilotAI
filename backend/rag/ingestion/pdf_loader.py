from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pymupdf

from backend.rag.ingestion.schemas import (
    Document,
    DocumentMetadata,
    ExtractedDocumentMetadata,
)

from backend.rag.ingestion.text_cleaner import clean_text


class PDFLoader:

    def load(
        self,
        file_path: str,
        original_filename: str | None = None,
    ) -> tuple[
        list[Document],
        ExtractedDocumentMetadata,
    ]:

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

        filename = (
            original_filename
            if original_filename
            else path.name
        )

        pdf_metadata = pdf.metadata or {}

        extracted_metadata = ExtractedDocumentMetadata(
            document_id=document_id,
            filename=filename,
            source=str(path),
            page_count=len(pdf),
            file_size=path.stat().st_size,
            title=pdf_metadata.get("title") or None,
            author=pdf_metadata.get("author") or None,
            creation_date=(
                pdf_metadata.get("creationDate")
                or None
            ),
            upload_time=datetime.now(),
        )

        documents = []

        for page_number, page in enumerate(
            pdf,
            start=1,
        ):

            text = clean_text(
                page.get_text()
            )

            if not text:
                continue

            metadata = DocumentMetadata(
                source=str(path),
                filename=filename,
                page_number=page_number,
                document_id=document_id,
            )

            document = Document(
                content=text.strip(),
                metadata=metadata,
            )

            documents.append(document)

        pdf.close()

        return documents, extracted_metadata