from pathlib import Path

import fitz
import pytest

from vectormind import (
    PDFEncryptedError,
    PDFParseError,
    PDFParser,
    PDFUnsupportedFileError,
)


def _write_pdf(path: Path, page_texts: list[str], *, title: str = "VectorMind Test PDF") -> None:
    document = fitz.open()
    document.set_metadata({"title": title})

    for text in page_texts:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)

    document.save(path)
    document.close()


def test_parse_text_pdf_preserves_pages_and_metadata(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    _write_pdf(pdf_path, ["First page text", "Second page text"], title="Ingestion Fixture")

    parsed = PDFParser().parse(pdf_path)

    assert parsed.source_path == pdf_path
    assert parsed.file_name == "sample.pdf"
    assert parsed.page_count == 2
    assert parsed.metadata["title"] == "Ingestion Fixture"
    assert [page.page_number for page in parsed.pages] == [1, 2]
    assert "First page text" in parsed.pages[0].text
    assert "Second page text" in parsed.pages[1].text
    assert parsed.pages[0].metadata["width"] > 0
    assert parsed.pages[0].metadata["height"] > 0
    assert parsed.pages[0].metadata["rotation"] == 0


def test_parse_empty_text_page_without_ocr(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty-page.pdf"
    _write_pdf(pdf_path, [""])

    parsed = PDFParser().parse(pdf_path)

    assert parsed.page_count == 1
    assert parsed.pages[0].page_number == 1
    assert parsed.pages[0].text == ""


def test_missing_pdf_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        PDFParser().parse(tmp_path / "missing.pdf")


def test_non_pdf_path_is_rejected(tmp_path: Path) -> None:
    text_path = tmp_path / "notes.txt"
    text_path.write_text("not a pdf")

    with pytest.raises(PDFUnsupportedFileError, match="Unsupported file type"):
        PDFParser().parse(text_path)


def test_encrypted_pdf_is_rejected(tmp_path: Path) -> None:
    pdf_path = tmp_path / "encrypted.pdf"
    document = fitz.open()
    document.new_page().insert_text((72, 72), "Secret text")
    document.save(
        pdf_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="owner-pass",
        user_pw="user-pass",
    )
    document.close()

    with pytest.raises(PDFEncryptedError, match="requires a password"):
        PDFParser().parse(pdf_path)


def test_invalid_pdf_content_is_wrapped(tmp_path: Path) -> None:
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_text("not actually a PDF")

    with pytest.raises(PDFParseError, match="Failed to parse PDF"):
        PDFParser().parse(pdf_path)
