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


class VLMPromptTemplate(BaseModel):
    """Versioned prompt template for structured VLM proposal requests."""

    task: VLMTask
    template_id: str
    template_version: str
    text: str
    required_variables: list[str] = Field(default_factory=list)

    def render(self, variables: dict[str, object] | None = None) -> VLMPromptRecord:
        """Render the template into a prompt record."""

        values = variables or {}
        missing = [name for name in self.required_variables if name not in values]
        if missing:
            raise ValueError(f"missing prompt variables: {', '.join(missing)}")
        text = self.text.format(**values)
        return VLMPromptRecord(
            task=self.task,
            template_id=self.template_id,
            template_version=self.template_version,
            text=text,
            variables=values,
        )


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


class VLMParsedResponse(BaseModel):
    """Parsed structured response and diagnostics from a VLM output string."""

    parsed_json: dict[str, object] | None = None
    proposal: ChartMetadataProposal | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class EnsembleFieldSummary(BaseModel):
    """Agreement summary for one VLM-proposed metadata field."""

    field: str
    winner: str | None = None
    counts: dict[str, int] = Field(default_factory=dict)
    agreement: float = Field(default=0.0, ge=0.0, le=1.0)
    mean_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    needs_review: bool = True


class VLMEnsembleSummary(BaseModel):
    """Summary of repeated VLM metadata proposal agreement."""

    input_count: int = Field(ge=0)
    valid_proposal_count: int = Field(ge=0)
    fields: list[EnsembleFieldSummary] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    proposal_request_ids: list[str] = Field(default_factory=list)


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
        parsed = parse_chart_metadata_response(response_text)

        raw_response = VLMRawResponse(
            backend=self.config.backend_info(),
            prompt=prompt,
            response_text=response_text,
            parsed_json=parsed.parsed_json,
            usage=_dict_or_empty(response.get("usage")),
            metadata={
                "response_id": response.get("id"),
                "finish_reason": _first_finish_reason(response),
            },
        )
        return ChartTriageResult(
            request=request_with_prompt,
            proposal=parsed.proposal,
            raw_response=raw_response,
            diagnostics=parsed.diagnostics,
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

    return CHART_METADATA_PROMPT_TEMPLATE.render({"context": ""})


CHART_TRIAGE_PROMPT_TEMPLATE = VLMPromptTemplate(
    task="chart_triage",
    template_id="chart-triage-json",
    template_version="0.1",
    required_variables=["context"],
    text=(
        "You are assisting an auditable chart digitization workflow. Inspect "
        "the image and return only a JSON object with proposal fields. "
        "Required keys: chart_type, warnings, confidence. Optional keys: "
        "title, x_axis, y_axis. Treat all values as uncertain proposals. "
        "Do not return a numeric data table. Context: {context}"
    ),
)


CHART_METADATA_PROMPT_TEMPLATE = VLMPromptTemplate(
    task="chart_metadata",
    template_id="chart-metadata-json",
    template_version="0.1",
    required_variables=["context"],
    text=(
        "You are assisting an auditable chart digitization workflow. Inspect "
        "the image and return only a JSON object matching this proposal shape: "
        "{{\"chart_type\": \"line|scatter|bar|histogram|boxplot|heatmap|unknown\", "
        "\"title\": string or null, "
        "\"x_axis\": {{\"label\": string or null, \"units\": string or null, "
        "\"scale\": \"linear|log10\", \"tick_labels\": [string], "
        "\"source\": \"vlm\", \"confidence\": number}}, "
        "\"y_axis\": {{\"label\": string or null, \"units\": string or null, "
        "\"scale\": \"linear|log10\", \"tick_labels\": [string], "
        "\"source\": \"vlm\", \"confidence\": number}}, "
        "\"legend\": {{\"entries\": object, \"confidence\": number}}, "
        "\"series_colors\": [{{\"series_name\": string or null, "
        "\"color\": \"#RRGGBB\", \"label\": string or null, "
        "\"confidence\": number}}], "
        "\"warnings\": [string], \"confidence\": number}}. "
        "All values are proposals for review. Do not infer a numeric data "
        "table. Context: {context}"
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


def parse_chart_metadata_response(response_text: str) -> VLMParsedResponse:
    """Parse and validate a chart metadata proposal response."""

    parsed_json, diagnostics = parse_json_object_response(response_text)
    proposal = None
    if parsed_json is not None:
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
    return VLMParsedResponse(
        parsed_json=parsed_json,
        proposal=proposal,
        diagnostics=diagnostics,
    )


def parse_json_object_response(
    response_text: str,
) -> tuple[dict[str, object] | None, list[Diagnostic]]:
    """Parse a JSON object from a VLM response string."""

    json_text, repair_diagnostics = _extract_json_object_text(response_text)
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return None, repair_diagnostics + [
            Diagnostic(
                level="warning",
                code="vlm_invalid_json",
                message="The VLM response could not be parsed as JSON.",
                context={"error": str(exc)},
            )
        ]
    if not isinstance(parsed, dict):
        return None, repair_diagnostics + [
            Diagnostic(
                level="warning",
                code="vlm_invalid_json_object",
                message="The VLM response JSON was not an object.",
                context={"parsed_type": type(parsed).__name__},
            )
        ]
    return parsed, repair_diagnostics


def _extract_json_object_text(response_text: str) -> tuple[str, list[Diagnostic]]:
    text = response_text.strip()
    diagnostics: list[Diagnostic] = []
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            diagnostics.append(
                Diagnostic(
                    level="info",
                    code="vlm_json_markdown_fence_removed",
                    message="Removed markdown code fences from the VLM response.",
                )
            )
            return "\n".join(lines[1:-1]).strip(), diagnostics
    start = text.find("{")
    end = text.rfind("}")
    if start > 0 and end > start:
        diagnostics.append(
            Diagnostic(
                level="info",
                code="vlm_json_object_extracted",
                message="Extracted the first JSON object from surrounding VLM response text.",
            )
        )
        return text[start : end + 1], diagnostics
    return text, diagnostics


def summarize_chart_metadata_ensemble(
    results: list[ChartTriageResult],
    *,
    min_agreement: float = 0.67,
) -> VLMEnsembleSummary:
    """Summarize agreement across repeated chart metadata proposals."""

    proposals = [result.proposal for result in results if result.proposal is not None]
    request_ids = [result.request.request_id for result in results]
    diagnostics: list[Diagnostic] = []
    if not proposals:
        diagnostics.append(
            Diagnostic(
                level="error",
                code="vlm_ensemble_no_proposals",
                message="No valid VLM proposals were available for ensemble summarization.",
            )
        )
        return VLMEnsembleSummary(
            input_count=len(results),
            valid_proposal_count=0,
            diagnostics=diagnostics,
            proposal_request_ids=request_ids,
        )

    fields = [
        _summarize_field(
            "chart_type",
            [(proposal.chart_type, proposal.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
        _summarize_field(
            "title",
            [(proposal.title, proposal.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
        _summarize_field(
            "x_axis.label",
            [(proposal.x_axis.label, proposal.x_axis.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
        _summarize_field(
            "y_axis.label",
            [(proposal.y_axis.label, proposal.y_axis.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
        _summarize_field(
            "x_axis.scale",
            [(proposal.x_axis.scale, proposal.x_axis.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
        _summarize_field(
            "y_axis.scale",
            [(proposal.y_axis.scale, proposal.y_axis.confidence) for proposal in proposals],
            min_agreement=min_agreement,
        ),
    ]
    for field in fields:
        if field.needs_review:
            diagnostics.append(
                Diagnostic(
                    level="warning",
                    code="vlm_ensemble_disagreement",
                    message="Repeated VLM proposals disagree on a metadata field.",
                    context={
                        "field": field.field,
                        "counts": field.counts,
                        "agreement": field.agreement,
                    },
                )
            )
    return VLMEnsembleSummary(
        input_count=len(results),
        valid_proposal_count=len(proposals),
        fields=fields,
        diagnostics=diagnostics,
        proposal_request_ids=request_ids,
    )


def _summarize_field(
    field: str,
    values: list[tuple[object, float]],
    *,
    min_agreement: float,
) -> EnsembleFieldSummary:
    normalized = [_normalize_ensemble_value(value) for value, _ in values]
    counts: dict[str, int] = {}
    for value in normalized:
        counts[value] = counts.get(value, 0) + 1
    top_count = max(counts.values()) if counts else 0
    winners = [value for value, count in counts.items() if count == top_count]
    winner = winners[0] if len(winners) == 1 and winner_is_informative(winners[0]) else None
    agreement = top_count / len(values) if values else 0.0
    mean_confidence = sum(confidence for _, confidence in values) / len(values) if values else 0.0
    all_missing = len(counts) == 1 and "<missing>" in counts
    needs_review = False if all_missing else winner is None or agreement < min_agreement
    return EnsembleFieldSummary(
        field=field,
        winner=winner,
        counts=counts,
        agreement=agreement,
        mean_confidence=mean_confidence,
        needs_review=needs_review,
    )


def _normalize_ensemble_value(value: object) -> str:
    if value is None:
        return "<missing>"
    text = str(value).strip()
    return text if text else "<missing>"


def winner_is_informative(value: str) -> bool:
    """Return whether an ensemble winner carries information."""

    return value != "<missing>"


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
    "CHART_METADATA_PROMPT_TEMPLATE",
    "CHART_TRIAGE_PROMPT_TEMPLATE",
    "ChartMetadataProposal",
    "ChartTriageRequest",
    "ChartTriageResult",
    "EnsembleFieldSummary",
    "HttpxJSONTransport",
    "JSONTransport",
    "LegendProposal",
    "OpenAICompatibleBackendConfig",
    "OpenAICompatibleVLMBackend",
    "SeriesColorProposal",
    "TickLabelProposal",
    "VLMBackend",
    "VLMBackendInfo",
    "VLMEnsembleSummary",
    "VLMParsedResponse",
    "VLMPromptRecord",
    "VLMPromptTemplate",
    "VLMRawResponse",
    "VLMTask",
    "default_chart_metadata_prompt",
    "parse_chart_metadata_response",
    "parse_json_object_response",
    "summarize_chart_metadata_ensemble",
]
