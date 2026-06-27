"""Public record types for figure recovery workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from figrecover.calibration import AxisCalibration, Calibration, CalibrationProposal
from figrecover.models import (
    CropBoundingBox,
    DataPoint,
    Diagnostic,
    DigitizeResult,
    DigitizeSpec,
    LineAggregation,
    SeriesResult,
    SeriesSpec,
)

ChartType = Literal[
    "line",
    "scatter",
    "bar",
    "histogram",
    "boxplot",
    "heatmap",
    "unknown",
]


class SourceDocument(BaseModel):
    """A source document that may contain recoverable figures."""

    document_id: str
    path: Path | None = None
    title: str | None = None
    sha256: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class RenderedPage(BaseModel):
    """A rendered page image derived from a source document."""

    document_id: str
    page_number: int = Field(ge=1)
    image_path: Path
    width_px: int = Field(ge=1)
    height_px: int = Field(ge=1)
    dpi: int = Field(ge=1)
    renderer: str = "manual"
    metadata: dict[str, object] = Field(default_factory=dict)


class BoundingBox(BaseModel):
    """Pixel-space rectangle in left, top, right, bottom order."""

    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        """Rectangle width in pixels."""

        return self.right - self.left

    @property
    def height(self) -> float:
        """Rectangle height in pixels."""

        return self.bottom - self.top


class FigureCandidate(BaseModel):
    """Candidate figure crop and provenance."""

    figure_id: str
    document_id: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    image_path: Path
    bbox: BoundingBox | None = None
    label: str | None = None
    caption: str | None = None
    source: str = "manual"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class AxisMetadata(BaseModel):
    """Human-facing axis metadata from manual review, OCR, or VLM proposals."""

    label: str | None = None
    units: str | None = None
    scale: str = "linear"
    tick_labels: list[str] = Field(default_factory=list)
    source: str = "manual"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ChartMetadata(BaseModel):
    """Chart-level metadata used to guide extraction and QA."""

    chart_type: ChartType = "unknown"
    title: str | None = None
    x_axis: AxisMetadata = Field(default_factory=AxisMetadata)
    y_axis: AxisMetadata = Field(default_factory=AxisMetadata)
    legend: dict[str, str] = Field(default_factory=dict)
    source: str = "manual"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class ExtractionToolchain(BaseModel):
    """Tools and settings used to recover data from a figure."""

    extractor: str
    extractor_version: str | None = None
    parser: str | None = None
    renderer: str | None = None
    vlm_model: str | None = None
    settings: dict[str, object] = Field(default_factory=dict)


class ExtractionRun(BaseModel):
    """A complete auditable extraction record for one figure."""

    run_id: str
    figure: FigureCandidate
    chart: ChartMetadata = Field(default_factory=ChartMetadata)
    calibration: Calibration | None = None
    toolchain: ExtractionToolchain
    result: DigitizeResult | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class ExportRecord(BaseModel):
    """Metadata for a recovered-data export artifact."""

    export_id: str
    path: Path
    format: Literal["csv", "json", "jsonl", "parquet"]
    row_count: int = Field(ge=0)
    source_run_ids: list[str] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


__all__ = [
    "AxisCalibration",
    "AxisMetadata",
    "BoundingBox",
    "Calibration",
    "CalibrationProposal",
    "ChartMetadata",
    "ChartType",
    "CropBoundingBox",
    "DataPoint",
    "Diagnostic",
    "DigitizeResult",
    "DigitizeSpec",
    "ExportRecord",
    "ExtractionRun",
    "ExtractionToolchain",
    "FigureCandidate",
    "LineAggregation",
    "RenderedPage",
    "SeriesResult",
    "SeriesSpec",
    "SourceDocument",
]
