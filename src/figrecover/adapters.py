from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from figrecover.documents import parse_page_selection, require_pymupdf
from figrecover.records import BoundingBox, ChartMetadata, FigureCandidate, RenderedPage


class FigureCandidateAdapter(Protocol):
    """Protocol for document parsers that emit normalized figure candidates."""

    source: str

    def discover(self) -> list[FigureCandidate]:
        """Return normalized figure candidates."""


class ManualCandidateAdapter:
    """Adapter that returns user-supplied candidates unchanged."""

    source = "manual"

    def __init__(self, candidates: Sequence[FigureCandidate]) -> None:
        self.candidates = list(candidates)

    def discover(self) -> list[FigureCandidate]:
        """Return manually supplied candidate records."""

        return self.candidates


class PyMuPDFImageBlockAdapter:
    """Discover embedded PDF image blocks and normalize them as candidates.

    The adapter maps PyMuPDF page-space bounding boxes, measured in PDF points,
    to rendered-page pixel coordinates using the ``dpi`` recorded on
    :class:`figrecover.records.RenderedPage`.
    """

    source = "pymupdf-image-block"

    def __init__(
        self,
        pdf_path: Path,
        rendered_pages: Sequence[RenderedPage],
        *,
        pages: str | Sequence[int] | None = None,
        min_width_px: float = 8.0,
        min_height_px: float = 8.0,
        confidence: float = 0.65,
    ) -> None:
        self.pdf_path = Path(pdf_path)
        self.rendered_pages = list(rendered_pages)
        self.pages = pages
        self.min_width_px = min_width_px
        self.min_height_px = min_height_px
        self.confidence = confidence

    def discover(self) -> list[FigureCandidate]:
        """Return embedded image-block candidates for rendered pages."""

        fitz = require_pymupdf()
        rendered_by_page = {page.page_number: page for page in self.rendered_pages}
        if not rendered_by_page:
            return []

        candidates: list[FigureCandidate] = []
        document = fitz.open(self.pdf_path)
        try:
            page_numbers = parse_page_selection(self.pages, page_count=document.page_count)
            for page_number in page_numbers:
                rendered_page = rendered_by_page.get(page_number)
                if rendered_page is None:
                    continue
                page = document.load_page(page_number - 1)
                scale = rendered_page.dpi / 72.0
                block_index = 0
                for block in page.get_text("dict").get("blocks", []):
                    if block.get("type") != 1:
                        continue
                    bbox = _scale_bbox(block["bbox"], scale=scale)
                    if bbox.width < self.min_width_px or bbox.height < self.min_height_px:
                        continue
                    block_index += 1
                    figure_id = (
                        f"{rendered_page.document_id}-p{page_number:04d}-"
                        f"img{block_index:03d}"
                    )
                    candidates.append(
                        FigureCandidate(
                            figure_id=figure_id,
                            document_id=rendered_page.document_id,
                            page_number=page_number,
                            image_path=rendered_page.image_path,
                            source_image_path=rendered_page.image_path,
                            bbox=bbox,
                            source=self.source,
                            confidence=self.confidence,
                            metadata={
                                "source_pdf": str(self.pdf_path),
                                "renderer": rendered_page.renderer,
                                "render_dpi": rendered_page.dpi,
                                "pdf_page_index": page_number - 1,
                                "block_number": block.get("number"),
                                "block_ext": block.get("ext"),
                                "block_width_px": block.get("width"),
                                "block_height_px": block.get("height"),
                                "block_size_bytes": block.get("size"),
                            },
                        )
                    )
        finally:
            document.close()

        return candidates


def extract_pymupdf_image_candidates(
    pdf_path: Path,
    rendered_pages: Sequence[RenderedPage],
    *,
    pages: str | Sequence[int] | None = None,
    min_width_px: float = 8.0,
    min_height_px: float = 8.0,
    confidence: float = 0.65,
) -> list[FigureCandidate]:
    """Extract embedded image-block candidates using the PyMuPDF adapter."""

    return PyMuPDFImageBlockAdapter(
        pdf_path,
        rendered_pages,
        pages=pages,
        min_width_px=min_width_px,
        min_height_px=min_height_px,
        confidence=confidence,
    ).discover()


def load_docling_figures(*_: object, **__: object) -> list[FigureCandidate]:
    """Placeholder adapter for future Docling figure extraction."""

    raise NotImplementedError(
        "Docling figure extraction is planned for the document-layout layer. "
        "Use manually cropped figures or render_pdf_page() for the deterministic core today."
    )


def _scale_bbox(raw_bbox: Sequence[float], *, scale: float) -> BoundingBox:
    left, top, right, bottom = raw_bbox
    return BoundingBox(
        left=left * scale,
        top=top * scale,
        right=right * scale,
        bottom=bottom * scale,
    )


__all__ = [
    "ChartMetadata",
    "FigureCandidate",
    "FigureCandidateAdapter",
    "ManualCandidateAdapter",
    "PyMuPDFImageBlockAdapter",
    "extract_pymupdf_image_candidates",
    "load_docling_figures",
]
