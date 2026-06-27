from __future__ import annotations

from pathlib import Path


def render_pdf_page(
    pdf_path: Path,
    *,
    page_number: int,
    out_path: Path,
    dpi: int = 300,
) -> Path:
    """Render a PDF page to a PNG file using PyMuPDF when the pdf extra is installed."""

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PDF rendering requires the optional pdf dependencies: "
            "python -m pip install figrecover[pdf]"
        ) from exc

    document = fitz.open(pdf_path)
    try:
        page = document.load_page(page_number - 1)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pixmap.save(out_path)
        return out_path
    finally:
        document.close()
