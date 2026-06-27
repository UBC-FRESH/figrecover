"""Records for local VLM-assisted chart understanding.

The VLM layer records proposals and provenance. It does not make model output
authoritative recovered data by default.
"""

from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, Field, ValidationError, field_validator

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


class VLMBackend(Protocol):
    """Protocol for local chart-understanding VLM backends."""

    def describe_chart(self, request: ChartTriageRequest) -> ChartTriageResult:
        """Return a chart metadata proposal for one prepared figure image."""


class OpenAICompatibleBackendConfig(BaseModel):
    """Configuration for an OpenAI-compatible local VLM endpoint."""

    model: str
    base_url: str = "http://127.0.0.1:8000/v1"
    endpoint_path: str = "/chat/completions"
    api_key: str | None = None
    timeout_s: float = Field(default=60.0, ge=0.0)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1)
    extra_body: dict[str, object] = Field(default_factory=dict)
    backend_name: str = "openai-compatible"

    @property
    def endpoint_url(self) -> str:
        """Return the chat-completions endpoint URL."""

        return f"{self.base_url.rstrip('/')}/{self.endpoint_path.lstrip('/')}"

    def backend_info(self) -> VLMBackendInfo:
        """Return audit-safe backend metadata without secrets."""

        return VLMBackendInfo(
            backend=self.backend_name,
            model=self.model,
            endpoint=self.endpoint_url,
            parameters={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.extra_body,
            },
        )


class JSONTransport(Protocol):
    """Small HTTP transport boundary used to keep tests backend-free."""

    def post_json(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_s: float,
    ) -> dict[str, object]:
        """Post JSON and return a decoded JSON object."""


class HttpxJSONTransport:
    """Default JSON transport using the optional ``httpx`` dependency."""

    def post_json(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_s: float,
    ) -> dict[str, object]:
        """Post JSON with ``httpx`` when the ``vlm`` extra is installed."""

        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI-compatible VLM backend requires the optional vlm "
                "dependencies: `python -m pip install figrecover[vlm]`."
            ) from exc

        response = httpx.post(url, headers=headers, json=payload, timeout=timeout_s)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise RuntimeError("VLM backend returned a non-object JSON response")
        return body


class OpenAICompatibleVLMBackend:
    """Local OpenAI-compatible backend for chart metadata proposals."""

    def __init__(
        self,
        config: OpenAICompatibleBackendConfig,
        *,
        transport: JSONTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or HttpxJSONTransport()

    def describe_chart(self, request: ChartTriageRequest) -> ChartTriageResult:
        """Request a structured chart metadata proposal from a local VLM."""

        prompt = request.prompt or default_chart_metadata_prompt()
        request_with_prompt = request.model_copy(update={"prompt": prompt})
        try:
            payload = self._build_payload(request_with_prompt)
            response = self.transport.post_json(
                url=self.config.endpoint_url,
                headers=self._headers(),
                payload=payload,
                timeout_s=self.config.timeout_s,
            )
        except Exception as exc:
            return ChartTriageResult(
                request=request_with_prompt,
                diagnostics=[
                    Diagnostic(
                        level="error",
                        code="vlm_backend_error",
                        message="The VLM backend request failed.",
                        context={"error": str(exc), "backend": self.config.backend_name},
                    )
                ],
            )

        response_text = _extract_openai_message_text(response)
        parsed_json, diagnostics = _parse_chart_metadata_json(response_text)
        proposal = None
        if isinstance(parsed_json, dict):
            try:
                proposal = ChartMetadataProposal.model_validate(parsed_json)
            except ValidationError as exc:
                diagnostics.append(
                    Diagnostic(
                        level="warning",
                        code="vlm_validation_error",
                        message="The VLM response JSON did not match the chart proposal schema.",
                        context={"errors": exc.errors()},
                    )
                )

        raw_response = VLMRawResponse(
            backend=self.config.backend_info(),
            prompt=prompt,
            response_text=response_text,
            parsed_json=parsed_json,
            usage=_dict_or_empty(response.get("usage")),
            metadata={
                "response_id": response.get("id"),
                "finish_reason": _first_finish_reason(response),
            },
        )
        return ChartTriageResult(
            request=request_with_prompt,
            proposal=proposal,
            raw_response=raw_response,
            diagnostics=diagnostics,
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _build_payload(self, request: ChartTriageRequest) -> dict[str, object]:
        assert request.prompt is not None
        payload: dict[str, object] = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt.text},
                        {
                            "type": "image_url",
                            "image_url": {"url": _image_data_url(request.image_path)},
                        },
                    ],
                }
            ],
        }
        payload.update(self.config.extra_body)
        return payload


def default_chart_metadata_prompt() -> VLMPromptRecord:
    """Return a minimal default prompt for local backend smoke tests."""

    return VLMPromptRecord(
        task="chart_metadata",
        template_id="chart-metadata-json",
        template_version="0.1",
        text=(
            "Return JSON describing this chart as proposals only. Include "
            "chart_type, title, x_axis, y_axis, legend, series_colors, "
            "warnings, and confidence when visible. Do not infer a numeric "
            "data table."
        ),
    )


def _image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _extract_openai_message_text(response: dict[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return ""


def _parse_chart_metadata_json(
    response_text: str,
) -> tuple[dict[str, object] | None, list[Diagnostic]]:
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as exc:
        return None, [
            Diagnostic(
                level="warning",
                code="vlm_invalid_json",
                message="The VLM response could not be parsed as JSON.",
                context={"error": str(exc)},
            )
        ]
    if not isinstance(parsed, dict):
        return None, [
            Diagnostic(
                level="warning",
                code="vlm_invalid_json_object",
                message="The VLM response JSON was not an object.",
                context={"parsed_type": type(parsed).__name__},
            )
        ]
    return parsed, []


def _dict_or_empty(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _first_finish_reason(response: dict[str, object]) -> object:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    return first.get("finish_reason") if isinstance(first, dict) else None


__all__ = [
    "AxisName",
    "AxisRangeProposal",
    "AxisScaleProposal",
    "CalibrationHintProposal",
    "ChartMetadataProposal",
    "ChartTriageRequest",
    "ChartTriageResult",
    "HttpxJSONTransport",
    "JSONTransport",
    "LegendProposal",
    "OpenAICompatibleBackendConfig",
    "OpenAICompatibleVLMBackend",
    "SeriesColorProposal",
    "TickLabelProposal",
    "VLMBackend",
    "VLMBackendInfo",
    "VLMPromptRecord",
    "VLMRawResponse",
    "VLMTask",
    "default_chart_metadata_prompt",
]
