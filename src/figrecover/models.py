from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from figrecover.calibration import Calibration

ExtractionMode = Literal["line", "scatter", "bar"]


class Diagnostic(BaseModel):
    level: Literal["info", "warning", "error"]
    code: str
    message: str
    context: dict[str, object] = Field(default_factory=dict)


class DataPoint(BaseModel):
    series: str
    x: float
    y: float
    x_pixel: float | None = None
    y_pixel: float | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SeriesSpec(BaseModel):
    name: str
    color: str
    mode: ExtractionMode = "line"
    tolerance: float = Field(default=40.0, ge=0.0)
    min_component_pixels: int = Field(default=4, ge=1)
    sample_every_px: int = Field(default=1, ge=1)
    bar_baseline: float | None = None

    @field_validator("color")
    @classmethod
    def _normalize_color(cls, value: str) -> str:
        text = value.strip()
        if not text.startswith("#") or len(text) != 7:
            raise ValueError("color must be a #RRGGBB hex string")
        int(text[1:], 16)
        return text.lower()


class DigitizeSpec(BaseModel):
    calibration: Calibration
    series: list[SeriesSpec]
    image_id: str | None = None
    figure_label: str | None = None
    source_pdf: Path | None = None
    source_page: int | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class SeriesResult(BaseModel):
    spec: SeriesSpec
    points: list[DataPoint] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class DigitizeResult(BaseModel):
    spec: DigitizeSpec
    image_path: Path
    width: int
    height: int
    series: list[SeriesResult]
    diagnostics: list[Diagnostic] = Field(default_factory=list)

    def points(self) -> list[DataPoint]:
        rows: list[DataPoint] = []
        for result in self.series:
            rows.extend(result.points)
        return rows

    def to_dataframe(self) -> pd.DataFrame:
        rows = [point.model_dump() for point in self.points()]
        columns = ["series", "x", "y", "x_pixel", "y_pixel", "confidence"]
        return pd.DataFrame(rows, columns=columns)
