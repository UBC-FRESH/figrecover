from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class FigureCandidate(BaseModel):
    """A figure crop emitted by a document-layout parser."""

    image_path: Path
    source_pdf: Path | None = None
    page_number: int | None = None
    label: str | None = None
    bbox: tuple[float, float, float, float] | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    source: str = "manual"
    metadata: dict[str, object] = Field(default_factory=dict)


class ChartMetadata(BaseModel):
    """Chart metadata that can be supplied manually, by OCR, or by a VLM."""

    chart_type: str | None = None
    title: str | None = None
    x_label: str | None = None
    y_label: str | None = None
    legend: dict[str, str] = Field(default_factory=dict)
    notes: str | None = None
    source: str = "manual"
    confidence: float = Field(default=1.0, ge=0, le=1)


def load_docling_figures(*_: object, **__: object) -> list[FigureCandidate]:
    """Placeholder adapter for future Docling figure extraction."""

    raise NotImplementedError(
        "Docling figure extraction is planned for the document-layout layer. "
        "Use manually cropped figures or render_pdf_page() for the deterministic core today."
    )
