import io
import logging
from typing import Union

logger = logging.getLogger(__name__)


def extract_text(source: Union[bytes, str]) -> str:
    """
    Extract plain text from a PDF.

    Args:
        source: Raw PDF bytes, or a file-system path string to a PDF file.

    Returns:
        Concatenated plain text from all pages. Empty string on failure.
    """
    try:
        import pdfplumber  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pdfplumber is required for PDF parsing. "
            "Install it with: pip install pdfplumber"
        ) from exc

    try:
        if isinstance(source, bytes):
            pdf_stream = io.BytesIO(source)
            return _read_pdf(pdfplumber, pdf_stream)
        else:
            with pdfplumber.open(source) as pdf:
                return _extract_pages(pdf)
    except Exception as exc:
        logger.error("pdf_parser.extract_text failed: %s", exc)
        return ""


def _read_pdf(pdfplumber, stream: io.BytesIO) -> str:
    with pdfplumber.open(stream) as pdf:
        return _extract_pages(pdf)


def _extract_pages(pdf) -> str:
    pages_text = []
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text).strip()
