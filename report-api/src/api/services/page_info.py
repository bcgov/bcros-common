"""Shared helpers for populating page numbers in WeasyPrint documents, get rid of the cyclic dependency."""

from io import BytesIO
import pikepdf


def get_pdf_page_count(pdf_content: bytes) -> int:
    """Extract total page count from PDF content."""
    try:
        with pikepdf.Pdf.open(BytesIO(pdf_content)) as pdf:
            return len(pdf.pages)
    except Exception as e:
        return 1
