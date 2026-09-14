# heartcare-ai-service/document_parser.py
"""
Document parsing module.
Supports: PDF (.pdf), Word (.docx), Plain Text (.txt)
Returns raw text content as a single string.
"""

import os
from pathlib import Path
from typing import Optional


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    text_parts: list[str] = []

    for page_num, page in enumerate(reader.pages):
        extracted = page.extract_text()
        if extracted and extracted.strip():
            # Add page marker for traceability
            text_parts.append(f"\n--- Halaman {page_num + 1} ---\n{extracted.strip()}")

    return "\n".join(text_parts)


def parse_docx(file_path: str) -> str:
    """Extract text from a .docx file using python-docx."""
    from docx import Document

    doc = Document(file_path)
    text_parts: list[str] = []

    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text.strip())

    # Also extract from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells if cell.text.strip()
            )
            if row_text:
                text_parts.append(row_text)

    return "\n\n".join(text_parts)


def parse_txt(file_path: str) -> str:
    """Read a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_document(file_path: str) -> Optional[str]:
    """
    Auto-detect file type and parse accordingly.
    Returns extracted text or None on failure.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    parsers = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".txt": parse_txt,
    }

    parser = parsers.get(ext)
    if parser is None:
        raise ValueError(
            f"Tipe file '{ext}' tidak didukung. "
            f"File yang didukung: {list(parsers.keys())}"
        )

    text = parser(file_path)
    if not text or not text.strip():
        raise ValueError(f"File '{path.name}' tidak mengandung teks yang dapat dibaca.")

    return text.strip()
