"""Records for local VLM-assisted chart understanding.

The VLM layer records proposals and provenance. It does not make model output
authoritative recovered data by default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from figrecover.models import Diagnostic
from figrecover.records import AxisMetadata, BoundingBox, ChartType, FigureCandidate

VLMTask = Literal["chart_triage", "chart_metadata", "calibration_hint"]
AxisName = Literal["x", "y"]
AxisScaleProposal = Literal["linear", "log10", "unknown"]


class VLMBackendInfo(BaseModel):
    """Model backend metadata for a local VLM request."""

    backend: str
    model: str
    endpoint: str | None = None
    parameters: dict[str, object] = Field(default_factory=dict)


class VLMPromptRecord(BaseModel):
    """Prompt text and template provenance sent to a VLM backend."""

    task: VLMTask
    template_id: str
    template_version: str
    text: str
    variables: dict[str, object] = Field(default_factory=dict)


class VLMRawResponse(BaseModel):
    """Raw VLM response and backend metadata preserved for audit."""

    backend: VLMBackendInfo
    prompt: VLMPromptRecord
    response_text: str
    parsed_json: dict[str, object] | list[object] | None = None
    usage: dict[str, object] = Field(default_factory=dict)
    latency_ms: float | None = Field(default=None, ge=0.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class SeriesColorProposal(BaseModel):
    """Candidate visual-series colour emitted by a VLM."""

    series_name: str | None = None
    color: str
    label: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: dict[str, object] = Field(default_factory=dict)

    @field_validator("color")
    @classmethod
    def _normalize_color(cls, value: str) -> str:
        text = value.strip()
        if not text.startswith("#") or len(text) != 7:
            raise ValueError("color must be a #RRGGBB hex string")
        int(text[1:], 16)
        return text.lower()


class LegendProposal(BaseModel):
    """Candidate chart legend interpretation emitted by a VLM."""

    entries: dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "vlm"
    evidence: dict[str, object] = Field(default_factory=dict)


class TickLabelProposal(BaseModel):
    """Candidate tick-label readings for one axis."""

    axis: AxisName
    labels: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: dict[str, object] = Field(default_factory=dict)


class AxisRangeProposal(BaseModel):
    """Candidate data range and scale for one chart axis."""

    axis: AxisName
    data_min: float | None = None
    data_max: float | None = None
    scale: AxisScaleProposal = "unknown"
    label: str | None = None
    units: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: dict[str, object] = Field(default_factory=dict)


class CalibrationHintProposal(BaseModel):
    """Candidate calibration hints that still require deterministic validation."""

    plot_bbox: BoundingBox | None = None
    x_axis: AxisRangeProposal | None = None
    y_axis: AxisRangeProposal | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "vlm"
    evidence: dict[str, object] = Field(default_factory=dict)


class ChartMetadataProposal(BaseModel):
    """Candidate chart metadata emitted by a VLM."""

    chart_type: ChartType = "unknown"
    title: str | None = None
    x_axis: AxisMetadata = Field(default_factory=lambda: AxisMetadata(source="vlm", confidence=0.0))
    y_axis: AxisMetadata = Field(default_factory=lambda: AxisMetadata(source="vlm", confidence=0.0))
    legend: LegendProposal = Field(default_factory=LegendProposal)
    tick_labels: list[TickLabelProposal] = Field(default_factory=list)
    series_colors: list[SeriesColorProposal] = Field(default_factory=list)
    calibration: CalibrationHintProposal | None = None
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "vlm"
    evidence: dict[str, object] = Field(default_factory=dict)


class ChartTriageRequest(BaseModel):
    """One VLM chart-understanding request for a prepared figure crop."""

    request_id: str
    image_path: Path
    figure: FigureCandidate | None = None
    context: dict[str, object] = Field(default_factory=dict)
    prompt: VLMPromptRecord | None = None

    @field_validator("request_id")
    @classmethod
    def _validate_request_id(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("request_id must not be empty")
        return text


class ChartTriageResult(BaseModel):
    """A VLM chart-understanding result with proposal and diagnostics."""

    request: ChartTriageRequest
    proposal: ChartMetadataProposal | None = None
    raw_response: VLMRawResponse | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)


__all__ = [
    "AxisName",
    "AxisRangeProposal",
    "AxisScaleProposal",
    "CalibrationHintProposal",
    "ChartMetadataProposal",
    "ChartTriageRequest",
    "ChartTriageResult",
    "LegendProposal",
    "SeriesColorProposal",
    "TickLabelProposal",
    "VLMBackendInfo",
    "VLMPromptRecord",
    "VLMRawResponse",
    "VLMTask",
]
