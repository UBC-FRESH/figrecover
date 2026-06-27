from pathlib import Path

import pytest

from figrecover.models import Diagnostic
from figrecover.records import BoundingBox, FigureCandidate
from figrecover.vlm import (
    CHART_METADATA_PROMPT_TEMPLATE,
    AxisRangeProposal,
    CalibrationHintProposal,
    ChartMetadataProposal,
    ChartTriageRequest,
    ChartTriageResult,
    LegendProposal,
    OpenAICompatibleBackendConfig,
    OpenAICompatibleVLMBackend,
    SeriesColorProposal,
    TickLabelProposal,
    VLMBackendInfo,
    VLMPromptRecord,
    VLMRawResponse,
    parse_chart_metadata_response,
    parse_json_object_response,
    summarize_chart_metadata_ensemble,
)


def test_vlm_proposal_records_are_json_serializable():
    request = ChartTriageRequest(
        request_id="triage-1",
        image_path=Path("crops/fig-1.png"),
        figure=FigureCandidate(
            figure_id="fig-1",
            document_id="doc-1",
            page_number=3,
            image_path=Path("crops/fig-1.png"),
        ),
        context={"caption": "Figure 1. Synthetic chart."},
        prompt=VLMPromptRecord(
            task="chart_metadata",
            template_id="chart-metadata-json",
            template_version="0.1",
            text="Return chart metadata as JSON.",
        ),
    )
    proposal = ChartMetadataProposal(
        chart_type="line",
        title="Synthetic harvest forecast",
        legend=LegendProposal(entries={"blue": "Base case"}, confidence=0.7),
        tick_labels=[TickLabelProposal(axis="x", labels=["2025", "2035"], confidence=0.8)],
        series_colors=[
            SeriesColorProposal(series_name="Base case", color="#1F77B4", confidence=0.8)
        ],
        calibration=CalibrationHintProposal(
            plot_bbox=BoundingBox(left=10, top=20, right=210, bottom=120),
            x_axis=AxisRangeProposal(axis="x", data_min=2025, data_max=2055, scale="linear"),
            y_axis=AxisRangeProposal(axis="y", data_min=0, data_max=2.0, scale="linear"),
            confidence=0.55,
        ),
        warnings=["dense legend"],
        confidence=0.72,
    )
    raw_response = VLMRawResponse(
        backend=VLMBackendInfo(
            backend="openai-compatible",
            model="local-test-vlm",
            endpoint="http://127.0.0.1:8000/v1",
            parameters={"temperature": 0.0},
        ),
        prompt=request.prompt,  # type: ignore[arg-type]
        response_text='{"chart_type": "line"}',
        parsed_json={"chart_type": "line"},
        usage={"prompt_tokens": 12},
    )
    result = ChartTriageResult(request=request, proposal=proposal, raw_response=raw_response)

    payload = result.model_dump(mode="json")

    assert payload["request"]["image_path"] == "crops/fig-1.png"
    assert payload["proposal"]["source"] == "vlm"
    assert payload["proposal"]["series_colors"][0]["color"] == "#1f77b4"
    assert payload["raw_response"]["backend"]["model"] == "local-test-vlm"


def test_vlm_results_can_store_validation_diagnostics_without_a_backend():
    request = ChartTriageRequest(request_id="triage-2", image_path=Path("crops/fig-2.png"))
    result = ChartTriageResult(
        request=request,
        diagnostics=[
            Diagnostic(
                level="warning",
                code="vlm_invalid_json",
                message="The model response could not be parsed as JSON.",
                context={"template_id": "chart-metadata-json"},
            )
        ],
    )

    payload = result.model_dump(mode="json")

    assert payload["proposal"] is None
    assert payload["diagnostics"][0]["code"] == "vlm_invalid_json"


def test_vlm_records_validate_ids_and_series_colours():
    with pytest.raises(ValueError, match="request_id must not be empty"):
        ChartTriageRequest(request_id=" ", image_path=Path("crop.png"))

    with pytest.raises(ValueError, match="color must be a #RRGGBB hex string"):
        SeriesColorProposal(color="blue")


class FakeTransport:
    def __init__(self, response: dict[str, object] | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[dict[str, object]] = []

    def post_json(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_s: float,
    ) -> dict[str, object]:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout_s": timeout_s,
            }
        )
        if self.error:
            raise self.error
        assert self.response is not None
        return self.response


def test_openai_compatible_backend_returns_structured_proposal(tmp_path: Path):
    image_path = tmp_path / "chart.png"
    image_path.write_bytes(b"not-a-real-image-but-encoded-for-request")
    transport = FakeTransport(
        response={
            "id": "response-1",
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"chart_type": "line", "title": "Synthetic chart", '
                            '"series_colors": [{"color": "#1f77b4", "series_name": "A"}], '
                            '"confidence": 0.8}'
                        )
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 8},
        }
    )
    backend = OpenAICompatibleVLMBackend(
        OpenAICompatibleBackendConfig(
            model="local-vlm",
            base_url="http://127.0.0.1:8000/v1",
            api_key="test-key",
            temperature=0.1,
        ),
        transport=transport,
    )

    result = backend.describe_chart(
        ChartTriageRequest(request_id="triage-3", image_path=image_path)
    )

    assert result.proposal is not None
    assert result.proposal.chart_type == "line"
    assert result.proposal.series_colors[0].color == "#1f77b4"
    assert result.raw_response is not None
    assert result.raw_response.backend.model == "local-vlm"
    assert result.raw_response.metadata["finish_reason"] == "stop"
    assert result.diagnostics == []
    assert transport.calls[0]["url"] == "http://127.0.0.1:8000/v1/chat/completions"
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer test-key"
    payload = transport.calls[0]["payload"]
    assert payload["model"] == "local-vlm"
    assert payload["response_format"] == {"type": "json_object"}


def test_openai_compatible_backend_records_invalid_json_diagnostics(tmp_path: Path):
    image_path = tmp_path / "chart.png"
    image_path.write_bytes(b"image")
    backend = OpenAICompatibleVLMBackend(
        OpenAICompatibleBackendConfig(model="local-vlm"),
        transport=FakeTransport(
            response={"choices": [{"message": {"content": "not json"}, "finish_reason": "stop"}]}
        ),
    )

    result = backend.describe_chart(
        ChartTriageRequest(request_id="triage-4", image_path=image_path)
    )

    assert result.proposal is None
    assert result.raw_response is not None
    assert result.diagnostics[0].code == "vlm_invalid_json"


def test_openai_compatible_backend_records_backend_errors(tmp_path: Path):
    image_path = tmp_path / "chart.png"
    image_path.write_bytes(b"image")
    backend = OpenAICompatibleVLMBackend(
        OpenAICompatibleBackendConfig(model="local-vlm"),
        transport=FakeTransport(error=RuntimeError("server unavailable")),
    )

    result = backend.describe_chart(
        ChartTriageRequest(request_id="triage-5", image_path=image_path)
    )

    assert result.proposal is None
    assert result.raw_response is None
    assert result.diagnostics[0].code == "vlm_backend_error"


def test_prompt_template_renders_versioned_prompt_records():
    prompt = CHART_METADATA_PROMPT_TEMPLATE.render({"context": "caption text"})

    assert prompt.task == "chart_metadata"
    assert prompt.template_id == "chart-metadata-json"
    assert prompt.template_version == "0.1"
    assert "caption text" in prompt.text
    assert prompt.variables["context"] == "caption text"


def test_prompt_template_requires_declared_variables():
    with pytest.raises(ValueError, match="missing prompt variables: context"):
        CHART_METADATA_PROMPT_TEMPLATE.render({})


def test_parse_json_object_response_removes_markdown_fences():
    parsed, diagnostics = parse_json_object_response(
        '```json\n{"chart_type": "bar", "confidence": 0.5}\n```'
    )

    assert parsed == {"chart_type": "bar", "confidence": 0.5}
    assert diagnostics[0].code == "vlm_json_markdown_fence_removed"


def test_parse_json_object_response_extracts_json_from_surrounding_text():
    parsed, diagnostics = parse_json_object_response(
        'Here is the JSON: {"chart_type": "scatter", "confidence": 0.4}'
    )

    assert parsed == {"chart_type": "scatter", "confidence": 0.4}
    assert diagnostics[0].code == "vlm_json_object_extracted"


def test_parse_chart_metadata_response_reports_schema_errors():
    parsed = parse_chart_metadata_response(
        '{"chart_type": "line", "series_colors": [{"color": "blue"}]}'
    )

    assert parsed.parsed_json is not None
    assert parsed.proposal is None
    assert parsed.diagnostics[0].code == "vlm_validation_error"


def test_summarize_chart_metadata_ensemble_reports_agreement():
    results = [
        ChartTriageResult(
            request=ChartTriageRequest(request_id=f"run-{index}", image_path=Path("crop.png")),
            proposal=ChartMetadataProposal(
                chart_type="line",
                title="Harvest forecast",
                confidence=0.8,
            ),
        )
        for index in range(3)
    ]

    summary = summarize_chart_metadata_ensemble(results)

    chart_type = next(field for field in summary.fields if field.field == "chart_type")
    assert summary.valid_proposal_count == 3
    assert chart_type.winner == "line"
    assert chart_type.agreement == 1.0
    assert chart_type.needs_review is False
    assert summary.diagnostics == []


def test_summarize_chart_metadata_ensemble_flags_disagreement():
    results = [
        ChartTriageResult(
            request=ChartTriageRequest(request_id="run-1", image_path=Path("crop.png")),
            proposal=ChartMetadataProposal(chart_type="line", confidence=0.8),
        ),
        ChartTriageResult(
            request=ChartTriageRequest(request_id="run-2", image_path=Path("crop.png")),
            proposal=ChartMetadataProposal(chart_type="bar", confidence=0.7),
        ),
    ]

    summary = summarize_chart_metadata_ensemble(results)

    chart_type = next(field for field in summary.fields if field.field == "chart_type")
    assert chart_type.winner is None
    assert chart_type.needs_review is True
    assert any(diagnostic.code == "vlm_ensemble_disagreement" for diagnostic in summary.diagnostics)


def test_summarize_chart_metadata_ensemble_handles_no_valid_proposals():
    summary = summarize_chart_metadata_ensemble(
        [
            ChartTriageResult(
                request=ChartTriageRequest(request_id="run-1", image_path=Path("crop.png")),
                diagnostics=[
                    Diagnostic(
                        level="warning",
                        code="vlm_invalid_json",
                        message="Invalid JSON.",
                    )
                ],
            )
        ]
    )

    assert summary.valid_proposal_count == 0
    assert summary.diagnostics[0].code == "vlm_ensemble_no_proposals"
