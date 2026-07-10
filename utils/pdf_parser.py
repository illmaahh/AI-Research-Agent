"""
utils/pdf_parser.py

Responsibility: Extract clean, page-aware text from an uploaded PDF file.

This module is the single place that knows about pypdf.  Nothing outside
this file should import pypdf directly.

Why pypdf instead of PyMuPDF (fitz)?
-------------------------------------
PyMuPDF ships a compiled C-extension wheel tagged ``cp310-abi3-win_amd64``.
PyMuPDF 1.28 links against internal CPython symbols removed in CPython 3.14,
causing ``ImportError: DLL load failed``.  pypdf is pure-Python
(wheel tag: ``py3-none-any``) and works on any CPython version.

Public API
----------
extract_pages(pdf_bytes: bytes) -> list[PageChunk]
    Returns one PageChunk per non-empty page.
    Raises ValueError on empty input, corrupt PDF, or image-only PDF.

extract_text(pdf_bytes: bytes) -> str
    Convenience wrapper — returns all pages joined with separators.
    Retained for backwards compatibility with the upload section.

get_page_count(pdf_bytes: bytes) -> int
    Returns total pages; returns 0 on any error.

get_statistics(pdf_bytes: bytes) -> dict
    Returns a dict of document statistics (word count, reading time, etc.)
"""

from __future__ import annotations

import io
import logging
import re
import warnings
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Suppress pypdf's internal "invalid pdf header / EOF marker" stderr chatter.
# These are emitted as Python warnings AND raw stderr writes by pypdf internals;
# we catch them here so the Streamlit log stays clean.  We still raise our own
# descriptive ValueError when the file is truly unreadable.
logging.getLogger("pypdf").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="pypdf")


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass
class PageChunk:
    """A single page extracted from the PDF, ready for embedding or display."""
    page_number: int        # 1-based page number
    text: str               # Cleaned text content of this page


# ─── Internal helpers ────────────────────────────────────────────────────────

_PAGE_SEPARATOR = "\n\n" + ("─" * 60) + "\n\n"

# Simple heuristics for structural element detection
_FIGURE_PATTERN    = re.compile(r'\bfig(?:ure)?\.?\s*\d+', re.IGNORECASE)
_TABLE_PATTERN     = re.compile(r'\btable\s*\d+', re.IGNORECASE)
_EQUATION_PATTERN  = re.compile(r'\b(?:eq(?:uation)?\.?\s*\d+|\(\d+\))', re.IGNORECASE)
_REFERENCE_PATTERN = re.compile(r'\[\d+\]')


def _open_reader(pdf_bytes: bytes) -> PdfReader:
    """Open a PdfReader from raw bytes, raising ValueError on failure."""
    if not pdf_bytes:
        raise ValueError(
            "No file content received. The uploaded file appears to be empty."
        )
    try:
        return PdfReader(io.BytesIO(pdf_bytes))
    except PdfReadError as exc:
        raise ValueError(
            "The file could not be read as a PDF. "
            "Please make sure you uploaded a valid, non-corrupted PDF."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Unexpected error while opening the PDF: {exc}") from exc


# ─── Public API ───────────────────────────────────────────────────────────────

def extract_pages(pdf_bytes: bytes) -> list[PageChunk]:
    """
    Extract text from every page and return a list of PageChunk objects.

    Each PageChunk carries the 1-based page number and the cleaned text.
    Blank pages (image-only) are silently skipped.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        List of PageChunk, one per non-empty page.

    Raises:
        ValueError: If input is empty, not a valid PDF, or has no text layer.
    """
    reader = _open_reader(pdf_bytes)
    chunks: list[PageChunk] = []

    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            chunks.append(PageChunk(page_number=i + 1, text=text))

    if not chunks:
        raise ValueError(
            "No readable text was found in this PDF. "
            "The document may be a scanned image without an OCR text layer. "
            "Please use a text-based PDF or run OCR on the file first."
        )
    return chunks


def extract_text(pdf_bytes: bytes) -> str:
    """
    Convenience wrapper: extract all pages and join with visible separators.

    Retained for backwards compatibility (upload section uses this).

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        Full text as a single string with page separators.

    Raises:
        ValueError: Same conditions as extract_pages().
    """
    chunks = extract_pages(pdf_bytes)
    return _PAGE_SEPARATOR.join(c.text for c in chunks)


def get_page_count(pdf_bytes: bytes) -> int:
    """
    Return the total number of pages in the PDF.

    Does not raise — returns 0 on any error so callers always get a safe value.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        Number of pages, or 0 if the document cannot be opened.
    """
    try:
        return len(_open_reader(pdf_bytes).pages)
    except Exception:  # noqa: BLE001
        return 0


def get_statistics(pdf_bytes: bytes) -> dict:
    """
    Compute a set of lightweight statistics about the PDF document.

    Uses heuristics (regex pattern counts) — no ML, no API calls.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        A dict with keys:
            pages           int   — total page count
            word_count      int   — approximate word count
            char_count      int   — total character count
            reading_time    int   — estimated minutes to read (@ 200 wpm)
            references      int   — count of citation patterns  e.g. [1]
            figures         int   — count of "Figure N" references
            tables          int   — count of "Table N" references
            equations       int   — count of equation references
        Returns all zeros on error.
    """
    try:
        chunks = extract_pages(pdf_bytes)
    except ValueError:
        return {k: 0 for k in ("pages", "word_count", "char_count",
                               "reading_time", "references", "figures",
                               "tables", "equations")}

    full_text = "\n".join(c.text for c in chunks)

    word_count  = len(full_text.split())
    char_count  = len(full_text)
    pages       = get_page_count(pdf_bytes)
    reading_min = max(1, round(word_count / 200))

    return {
        "pages":        pages,
        "word_count":   word_count,
        "char_count":   char_count,
        "reading_time": reading_min,
        "references":   len(_REFERENCE_PATTERN.findall(full_text)),
        "figures":      len(_FIGURE_PATTERN.findall(full_text)),
        "tables":       len(_TABLE_PATTERN.findall(full_text)),
        "equations":    len(_EQUATION_PATTERN.findall(full_text)),
    }
