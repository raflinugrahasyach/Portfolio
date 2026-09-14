# heartcare-ai-service/chunker.py
"""
Semantic Chunking Module.
Uses LangChain RecursiveCharacterTextSplitter tuned for Indonesian medical text.
Strategy:
  - Split on paragraph boundaries first (double newline)
  - Then on single newline, period, and space
  - chunk_size=512 tokens (~400 chars in Indonesian)
  - chunk_overlap=64 to preserve sentence continuity
  - Filters out chunks with < 30 chars (noise)
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List


# Indonesian-aware separators — try paragraph breaks before sentences
_INDONESIAN_SEPARATORS = [
    "\n\n",     # Paragraph boundary (highest priority)
    "\n",       # Line break
    ". ",       # Sentence end with period
    "! ",       # Exclamatory sentence
    "? ",       # Question sentence
    "; ",       # Semicolon
    ", ",       # Clause separator
    " ",        # Word boundary (last resort)
    "",         # Character boundary (absolute fallback)
]

_SPLITTER = RecursiveCharacterTextSplitter(
    separators=_INDONESIAN_SEPARATORS,
    chunk_size=512,       # ~350-400 Bahasa Indonesia chars
    chunk_overlap=64,     # Overlap to preserve cross-chunk context
    length_function=len,
    is_separator_regex=False,
)

MIN_CHUNK_LENGTH = 30  # Discard chunks shorter than this (headers, page numbers, etc.)


def chunk_text(text: str, document_title: str = "") -> List[dict]:
    """
    Split `text` into semantic chunks.
    Returns a list of dicts:
        {
            "chunk_index": int,
            "text": str,
            "char_count": int,
            "document_title": str,
        }
    """
    raw_chunks: List[str] = _SPLITTER.split_text(text)

    cleaned_chunks: List[dict] = []
    idx = 0
    for chunk in raw_chunks:
        stripped = chunk.strip()
        if len(stripped) < MIN_CHUNK_LENGTH:
            continue  # Skip noise (page numbers, single words, etc.)
        cleaned_chunks.append(
            {
                "chunk_index": idx,
                "text": stripped,
                "char_count": len(stripped),
                "document_title": document_title,
            }
        )
        idx += 1

    return cleaned_chunks
