"""PDF text ingestion using PyMuPDF."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vectormind.documents import ParsedDocument, ParsedPage


class PDFParseError(Exception):
    """Raised when a PDF cannot be parsed."""


class PDFDependencyError(PDFParseError):
    """Raised when the PyMuPDF dependency is unavailable."""


class PDFUnsupportedFileError(PDFParseError):
    """Raised when a path is not a readable PDF file."""


class PDFEncryptedError(PDFParseError):
    """Raised when a PDF requires a password."""


class PDFParser:
    """Extract text and page metadata from digitally generated PDFs."""

    def parse(self, path: str | Path) -> ParsedDocument:
        pdf_path = Path(path).expanduser()

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.is_file():
            raise PDFUnsupportedFileError(f"PDF path is not a file: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise PDFUnsupportedFileError(f"Unsupported file type for PDF parser: {pdf_path}")

        try:
            import fitz
        except ImportError as exc:  # pragma: no cover - exercised only without dependency.
            raise PDFDependencyError("PyMuPDF is required to parse PDFs. Install `pymupdf`.") from exc

        try:
            with fitz.open(pdf_path) as document:
                if document.needs_pass:
                    raise PDFEncryptedError(f"Encrypted PDF requires a password: {pdf_path}")

                pages = tuple(self._parse_page(page) for page in document)
                metadata = self._clean_metadata(document.metadata or {})

                return ParsedDocument(
                    source_path=pdf_path,
                    file_name=pdf_path.name,
                    page_count=document.page_count,
                    pages=pages,
                    metadata=metadata,
                )
        except PDFParseError:
            raise
        except Exception as exc:
            raise PDFParseError(f"Failed to parse PDF {pdf_path}: {exc}") from exc

    @staticmethod
    def _parse_page(page: Any) -> ParsedPage:
        rect = page.rect
        return ParsedPage(
            page_number=page.number + 1,
            text=page.get_text("text") or "",
            metadata={
                "width": float(rect.width),
                "height": float(rect.height),
                "rotation": int(page.rotation),
            },
        )

    @staticmethod
    def _clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in metadata.items() if value not in (None, "")}
