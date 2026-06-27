from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, Field, model_validator

AxisScale = Literal["linear", "log10"]


class AxisCalibration(BaseModel):
    """Map a pixel interval to a data interval for one plot axis."""

    pixel_min: float
    pixel_max: float
    data_min: float
    data_max: float
    scale: AxisScale = "linear"
    inverted: bool = False

    @model_validator(mode="after")
    def _validate_interval(self) -> AxisCalibration:
        if self.pixel_min == self.pixel_max:
            raise ValueError("pixel_min and pixel_max must differ")
        if self.scale == "log10" and (self.data_min <= 0 or self.data_max <= 0):
            raise ValueError("log10 axes require positive data_min and data_max")
        return self

    def pixel_to_data(self, pixel: float) -> float:
        fraction = (pixel - self.pixel_min) / (self.pixel_max - self.pixel_min)
        if self.inverted:
            fraction = 1.0 - fraction
        if self.scale == "linear":
            return self.data_min + fraction * (self.data_max - self.data_min)
        log_min = math.log10(self.data_min)
        log_max = math.log10(self.data_max)
        return 10 ** (log_min + fraction * (log_max - log_min))

    def data_to_pixel(self, value: float) -> float:
        if self.scale == "linear":
            fraction = (value - self.data_min) / (self.data_max - self.data_min)
        else:
            if value <= 0:
                raise ValueError("log10 axes require positive values")
            log_min = math.log10(self.data_min)
            log_max = math.log10(self.data_max)
            fraction = (math.log10(value) - log_min) / (log_max - log_min)
        if self.inverted:
            fraction = 1.0 - fraction
        return self.pixel_min + fraction * (self.pixel_max - self.pixel_min)


class Calibration(BaseModel):
    """Two-axis plot calibration."""

    x: AxisCalibration
    y: AxisCalibration
    plot_left: float | None = None
    plot_right: float | None = None
    plot_top: float | None = None
    plot_bottom: float | None = None
    notes: str | None = None

    @classmethod
    def from_plot_bounds(
        cls,
        *,
        plot_left: float,
        plot_right: float,
        plot_top: float,
        plot_bottom: float,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        x_scale: AxisScale = "linear",
        y_scale: AxisScale = "linear",
        notes: str | None = None,
    ) -> Calibration:
        return cls(
            x=AxisCalibration(
                pixel_min=plot_left,
                pixel_max=plot_right,
                data_min=x_min,
                data_max=x_max,
                scale=x_scale,
                inverted=False,
            ),
            y=AxisCalibration(
                pixel_min=plot_top,
                pixel_max=plot_bottom,
                data_min=y_min,
                data_max=y_max,
                scale=y_scale,
                inverted=True,
            ),
            plot_left=plot_left,
            plot_right=plot_right,
            plot_top=plot_top,
            plot_bottom=plot_bottom,
            notes=notes,
        )

    def pixel_to_data(self, x_pixel: float, y_pixel: float) -> tuple[float, float]:
        return self.x.pixel_to_data(x_pixel), self.y.pixel_to_data(y_pixel)

    def data_to_pixel(self, x: float, y: float) -> tuple[float, float]:
        return self.x.data_to_pixel(x), self.y.data_to_pixel(y)

    def contains_pixel(self, x_pixel: float, y_pixel: float, *, margin: float = 0) -> bool:
        if None in (self.plot_left, self.plot_right, self.plot_top, self.plot_bottom):
            return True
        assert self.plot_left is not None
        assert self.plot_right is not None
        assert self.plot_top is not None
        assert self.plot_bottom is not None
        return (
            self.plot_left - margin <= x_pixel <= self.plot_right + margin
            and self.plot_top - margin <= y_pixel <= self.plot_bottom + margin
        )

    def clipped_bounds(
        self, width: int, height: int, *, margin: int = 0
    ) -> tuple[int, int, int, int]:
        left = 0 if self.plot_left is None else math.floor(self.plot_left - margin)
        right = width if self.plot_right is None else math.ceil(self.plot_right + margin)
        top = 0 if self.plot_top is None else math.floor(self.plot_top - margin)
        bottom = height if self.plot_bottom is None else math.ceil(self.plot_bottom + margin)
        return (
            max(0, left),
            min(width, right),
            max(0, top),
            min(height, bottom),
        )


class CalibrationProposal(BaseModel):
    """Candidate calibration emitted by OCR/VLM/layout adapters."""

    calibration: Calibration
    confidence: float = Field(ge=0, le=1)
    source: str
    evidence: dict[str, object] = Field(default_factory=dict)
