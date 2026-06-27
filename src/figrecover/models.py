from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from figrecover.calibration import Calibration

ExtractionMode = Literal["line", "scatter", "bar"]
LineAggregation = Literal["median", "min", "max"]
CropBoundingBox = tuple[float, float, float, float]


class Diagnostic(BaseModel):
    """A structured extraction or workflow diagnostic."""

    level: Literal["info", "warning", "error"]
    code: str
    message: str
    context: dict[str, object] = Field(default_factory=dict)


class DataPoint(BaseModel):
    """One recovered data point and its source pixel coordinate."""

    series: str
    x: float
    y: float
    x_pixel: float | None = None
    y_pixel: float | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SeriesSpec(BaseModel):
    """Extraction settings for one visual series."""

    name: str
    color: str
    mode: ExtractionMode = "line"
    tolerance: float = Field(default=40.0, ge=0.0)
    min_component_pixels: int = Field(default=4, ge=1)
    sample_every_px: int = Field(default=1, ge=1)
    bar_baseline: float | None = None
    line_aggregation: LineAggregation = "median"
    plot_edge_margin_px: int = Field(default=0, ge=0)

    @field_validator("color")
    @classmethod
    def _normalize_color(cls, value: str) -> str:
        text = value.strip()
        if not text.startswith("#") or len(text) != 7:
            raise ValueError("color must be a #RRGGBB hex string")
        int(text[1:], 16)
        return text.lower()


class DigitizeSpec(BaseModel):
    """Complete settings and provenance for digitizing one image crop."""

    calibration: Calibration
    series: list[SeriesSpec]
    image_id: str | None = None
    source_document_id: str | None = None
    source_figure_id: str | None = None
    figure_label: str | None = None
    source_pdf: Path | None = None
    source_page: int | None = None
    source_crop_bbox: CropBoundingBox | None = None
    extraction_tool: str = "figrecover.digitize"
    extraction_tool_version: str | None = None
    extraction_settings: dict[str, object] = Field(default_factory=dict)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class SeriesResult(BaseModel):
    """Recovered points and diagnostics for one requested series."""

    spec: SeriesSpec
    points: list[DataPoint] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class DigitizeResult(BaseModel):
    """Result of digitizing one image crop."""

    spec: DigitizeSpec
    image_path: Path
    width: int
    height: int
    series: list[SeriesResult]
    diagnostics: list[Diagnostic] = Field(default_factory=list)

    def points(self) -> list[DataPoint]:
        """Return all recovered points from all series in output order."""

        rows: list[DataPoint] = []
        for result in self.series:
            rows.extend(result.points)
        return rows

    def to_dataframe(self, *, include_provenance: bool = False) -> pd.DataFrame:
        """Return recovered points as a pandas DataFrame.

        Set ``include_provenance`` to include image/document/figure/tool fields
        that are useful when combining results across a corpus.
        """

        rows = [point.model_dump() for point in self.points()]
        columns = ["series", "x", "y", "x_pixel", "y_pixel", "confidence"]
        if include_provenance:
            provenance = {
                "image_path": str(self.image_path),
                "image_id": self.spec.image_id,
                "source_document_id": self.spec.source_document_id,
                "source_figure_id": self.spec.source_figure_id,
                "figure_label": self.spec.figure_label,
                "source_pdf": str(self.spec.source_pdf) if self.spec.source_pdf else None,
                "source_page": self.spec.source_page,
                "source_crop_bbox": self.spec.source_crop_bbox,
                "extraction_tool": self.spec.extraction_tool,
                "extraction_tool_version": self.spec.extraction_tool_version,
            }
            rows = [{**provenance, **row} for row in rows]
            columns = list(provenance) + columns
        return pd.DataFrame(rows, columns=columns)
