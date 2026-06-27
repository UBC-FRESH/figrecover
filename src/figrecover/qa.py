"""Quality-assurance helpers for recovered figure data."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw
from pydantic import BaseModel, Field

from figrecover.models import Diagnostic, DigitizeResult, SeriesResult
from figrecover.vlm import VLMEnsembleSummary


class OverlayArtifact(BaseModel):
    """Metadata for a generated review overlay image."""

    path: Path
    source_image_path: Path
    width_px: int = Field(ge=1)
    height_px: int = Field(ge=1)
    series_count: int = Field(ge=0)
    point_count: int = Field(ge=0)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class SeriesQualityMetrics(BaseModel):
    """Quality metrics for one recovered series."""

    series_name: str
    mode: str
    point_count: int = Field(ge=0)
    mean_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    diagnostics_by_level: dict[str, int] = Field(default_factory=dict)


class FigureQualityMetrics(BaseModel):
    """Quality metrics for one recovered figure result."""

    image_path: Path
    width_px: int = Field(ge=1)
    height_px: int = Field(ge=1)
    series_count: int = Field(ge=0)
    point_count: int = Field(ge=0)
    extraction_density: float = Field(default=0.0, ge=0.0)
    plot_bounds_available: bool = False
    mean_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    diagnostics_by_level: dict[str, int] = Field(default_factory=dict)
    series: list[SeriesQualityMetrics] = Field(default_factory=list)
    vlm_disagreement_count: int = Field(default=0, ge=0)
    review_priority: Literal["low", "medium", "high"] = "low"


def render_overlay(
    result: DigitizeResult,
    output_path: Path,
    *,
    source_image_path: Path | None = None,
    point_radius: int = 3,
    line_width: int = 2,
) -> OverlayArtifact:
    """Render recovered points/lines/bars over the source crop image."""

    source = Path(source_image_path or result.image_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    diagnostics: list[Diagnostic] = []
    point_count = 0

    with Image.open(source).convert("RGBA") as image:
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        _draw_plot_bounds(draw, result)
        for series_result in result.series:
            color = _hex_to_rgba(series_result.spec.color, alpha=210)
            points = [
                (point.x_pixel, point.y_pixel)
                for point in series_result.points
                if point.x_pixel is not None and point.y_pixel is not None
            ]
            skipped = len(series_result.points) - len(points)
            if skipped:
                diagnostics.append(
                    Diagnostic(
                        level="warning",
                        code="overlay_missing_pixel_coordinates",
                        message=(
                            "Some recovered points lacked pixel coordinates and were not drawn."
                        ),
                        context={"series": series_result.spec.name, "skipped_points": skipped},
                    )
                )
            point_count += len(points)
            if series_result.spec.mode == "line" and len(points) > 1:
                draw.line(points, fill=color, width=line_width)
            elif series_result.spec.mode == "bar":
                _draw_bar_overlay(draw, series_result, color, point_radius)
            for x_pixel, y_pixel in points:
                draw.ellipse(
                    (
                        x_pixel - point_radius,
                        y_pixel - point_radius,
                        x_pixel + point_radius,
                        y_pixel + point_radius,
                    ),
                    fill=color,
                    outline=(0, 0, 0, 180),
                )
        combined = Image.alpha_composite(image, overlay).convert("RGB")
        combined.save(output_path)
        width, height = combined.size

    return OverlayArtifact(
        path=output_path,
        source_image_path=source,
        width_px=width,
        height_px=height,
        series_count=len(result.series),
        point_count=point_count,
        diagnostics=diagnostics,
    )


def compute_quality_metrics(
    result: DigitizeResult,
    *,
    vlm_ensemble: VLMEnsembleSummary | None = None,
) -> FigureQualityMetrics:
    """Compute transparent QA metrics for one digitization result."""

    series_metrics = [_series_metrics(series_result) for series_result in result.series]
    point_count = sum(metric.point_count for metric in series_metrics)
    diagnostics = list(result.diagnostics)
    for series_result in result.series:
        diagnostics.extend(series_result.diagnostics)
    diagnostics_by_level = _count_diagnostic_levels(diagnostics)
    confidences = [
        point.confidence
        for series_result in result.series
        for point in series_result.points
    ]
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    vlm_disagreement_count = 0
    if vlm_ensemble is not None:
        vlm_disagreement_count = sum(
            1
            for diagnostic in vlm_ensemble.diagnostics
            if diagnostic.code == "vlm_ensemble_disagreement"
        )
    metrics = FigureQualityMetrics(
        image_path=result.image_path,
        width_px=result.width,
        height_px=result.height,
        series_count=len(result.series),
        point_count=point_count,
        extraction_density=point_count / max(result.width * result.height, 1),
        plot_bounds_available=all(
            value is not None
            for value in (
                result.spec.calibration.plot_left,
                result.spec.calibration.plot_right,
                result.spec.calibration.plot_top,
                result.spec.calibration.plot_bottom,
            )
        ),
        mean_confidence=mean_confidence,
        diagnostics_by_level=diagnostics_by_level,
        series=series_metrics,
        vlm_disagreement_count=vlm_disagreement_count,
    )
    return metrics.model_copy(update={"review_priority": _review_priority(metrics)})


def write_quality_metrics(metrics: FigureQualityMetrics, path: Path) -> Path:
    """Write figure quality metrics as JSON."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(metrics.model_dump_json(indent=2), encoding="utf-8")
    return path


def _series_metrics(series_result: SeriesResult) -> SeriesQualityMetrics:
    confidences = [point.confidence for point in series_result.points]
    return SeriesQualityMetrics(
        series_name=series_result.spec.name,
        mode=series_result.spec.mode,
        point_count=len(series_result.points),
        mean_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
        diagnostics_by_level=_count_diagnostic_levels(series_result.diagnostics),
    )


def _count_diagnostic_levels(diagnostics: list[Diagnostic]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for diagnostic in diagnostics:
        counts[diagnostic.level] = counts.get(diagnostic.level, 0) + 1
    return counts


def _review_priority(metrics: FigureQualityMetrics) -> Literal["low", "medium", "high"]:
    if (
        metrics.diagnostics_by_level.get("error", 0)
        or metrics.point_count == 0
        or metrics.vlm_disagreement_count > 0
    ):
        return "high"
    if metrics.diagnostics_by_level.get("warning", 0) or metrics.mean_confidence < 0.75:
        return "medium"
    return "low"


def _draw_plot_bounds(draw: ImageDraw.ImageDraw, result: DigitizeResult) -> None:
    calibration = result.spec.calibration
    if None in (
        calibration.plot_left,
        calibration.plot_right,
        calibration.plot_top,
        calibration.plot_bottom,
    ):
        return
    assert calibration.plot_left is not None
    assert calibration.plot_right is not None
    assert calibration.plot_top is not None
    assert calibration.plot_bottom is not None
    draw.rectangle(
        (
            calibration.plot_left,
            calibration.plot_top,
            calibration.plot_right,
            calibration.plot_bottom,
        ),
        outline=(20, 20, 20, 220),
        width=1,
    )


def _draw_bar_overlay(
    draw: ImageDraw.ImageDraw,
    series_result: SeriesResult,
    color: tuple[int, int, int, int],
    point_radius: int,
) -> None:
    baseline = series_result.spec.bar_baseline
    for point in series_result.points:
        if point.x_pixel is None or point.y_pixel is None:
            continue
        if baseline is None:
            continue
        draw.line(
            [(point.x_pixel, point.y_pixel), (point.x_pixel, baseline)],
            fill=color,
            width=max(point_radius * 2, 2),
        )


def _hex_to_rgba(value: str, *, alpha: int) -> tuple[int, int, int, int]:
    text = value.lstrip("#")
    return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16), alpha)


__all__ = [
    "FigureQualityMetrics",
    "OverlayArtifact",
    "SeriesQualityMetrics",
    "compute_quality_metrics",
    "render_overlay",
    "write_quality_metrics",
]
