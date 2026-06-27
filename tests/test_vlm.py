from pathlib import Path

import pytest

from figrecover.models import Diagnostic
from figrecover.records import BoundingBox, FigureCandidate
from figrecover.vlm import (
    AxisRangeProposal,
    CalibrationHintProposal,
    ChartMetadataProposal,
    ChartTriageRequest,
    ChartTriageResult,
    LegendProposal,
    SeriesColorProposal,
    TickLabelProposal,
    VLMBackendInfo,
    VLMPromptRecord,
    VLMRawResponse,
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
