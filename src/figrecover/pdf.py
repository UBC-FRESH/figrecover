from __future__ import annotations

from pathlib import Path

from figrecover.documents import render_pdf_pages


def render_pdf_page(
    pdf_path: Path,
    *,
    page_number: int,
    out_path: Path,
    dpi: int = 300,
) -> Path:
    """Render one one-based PDF page to an image file.

    This compatibility wrapper preserves the Phase 0 helper API. New code
    should use :func:`figrecover.documents.render_pdf_pages`.
    """

    results = render_pdf_pages(
        pdf_path,
        out_path.parent,
        pages=[page_number],
        dpi=dpi,
        image_format=out_path.suffix.lstrip(".") or "png",
        document_id=out_path.stem.rsplit("-p", 1)[0],
        overwrite=True,
    )
    rendered = results[0]
    if rendered.image_path != out_path:
        rendered.image_path.replace(out_path)
    return out_path
