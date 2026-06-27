from __future__ import annotations

from figrecover.records import ChartMetadata, FigureCandidate


def load_docling_figures(*_: object, **__: object) -> list[FigureCandidate]:
    """Placeholder adapter for future Docling figure extraction."""

    raise NotImplementedError(
        "Docling figure extraction is planned for the document-layout layer. "
        "Use manually cropped figures or render_pdf_page() for the deterministic core today."
    )


__all__ = ["ChartMetadata", "FigureCandidate", "load_docling_figures"]
