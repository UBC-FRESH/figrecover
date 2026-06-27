from pathlib import Path

import pytest
from PIL import Image, ImageChops
from pydantic import ValidationError

from figrecover import (
    Calibration,
    DataPoint,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)
from figrecover.models import Diagnostic
from figrecover.qa import compute_quality_metrics, render_overlay, write_quality_metrics
from figrecover.review import ReviewCorrection, ReviewEntry, ReviewManifest
from figrecover.vlm import (
    ChartMetadataProposal,
    ChartTriageRequest,
    ChartTriageResult,
    summarize_chart_metadata_ensemble,
)


def _synthetic_result(image_path: Path) -> DigitizeResult:
    spec = DigitizeSpec(
        image_id="crop-1",
        source_document_id="doc-1",
        source_figure_id="fig-1",
        calibration=Calibration.from_plot_bounds(
            plot_left=10,
            plot_right=90,
            plot_top=10,
            plot_bottom=90,
            x_min=0,
            x_max=100,
            y_min=0,
            y_max=100,
        ),
        series=[SeriesSpec(name="line", color="#1f77b4")],
    )
    return DigitizeResult(
        spec=spec,
        image_path=image_path,
        width=100,
        height=100,
        series=[
            SeriesResult(
                spec=spec.series[0],
                points=[
                    DataPoint(series="line", x=0, y=0, x_pixel=10, y_pixel=90, confidence=0.9),
                    DataPoint(series="line", x=100, y=100, x_pixel=90, y_pixel=10, confidence=0.8),
                ],
            )
        ],
    )


def test_render_overlay_writes_visible_overlay(tmp_path: Path):
    image_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    result = _synthetic_result(image_path)
    overlay_path = tmp_path / "overlay.png"

    artifact = render_overlay(result, overlay_path)

    assert artifact.path == overlay_path
    assert artifact.point_count == 2
    assert overlay_path.exists()
    with Image.open(image_path) as source, Image.open(overlay_path) as overlay:
        diff = ImageChops.difference(source.convert("RGB"), overlay.convert("RGB"))
        assert diff.getbbox() is not None


def test_compute_quality_metrics_counts_points_and_diagnostics(tmp_path: Path):
    image_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    result = _synthetic_result(image_path)
    result.series[0].diagnostics.append(
        Diagnostic(level="warning", code="sparse", message="Sparse extraction.")
    )
    ensemble = summarize_chart_metadata_ensemble(
        [
            ChartTriageResult(
                request=ChartTriageRequest(request_id="a", image_path=image_path),
                proposal=ChartMetadataProposal(chart_type="line"),
            ),
            ChartTriageResult(
                request=ChartTriageRequest(request_id="b", image_path=image_path),
                proposal=ChartMetadataProposal(chart_type="bar"),
            ),
        ]
    )

    metrics = compute_quality_metrics(result, vlm_ensemble=ensemble)

    assert metrics.point_count == 2
    assert metrics.series_count == 1
    assert metrics.plot_bounds_available is True
    assert metrics.diagnostics_by_level["warning"] == 1
    assert metrics.vlm_disagreement_count >= 1
    assert metrics.review_priority == "high"


def test_write_quality_metrics_writes_json(tmp_path: Path):
    image_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    metrics = compute_quality_metrics(_synthetic_result(image_path))
    out_path = tmp_path / "metrics.json"

    write_quality_metrics(metrics, out_path)

    assert '"point_count": 2' in out_path.read_text(encoding="utf-8")


def test_review_manifest_round_trip_preserves_status_and_correction(tmp_path: Path):
    entry = ReviewEntry(
        review_id="review-1",
        figure_id="fig-1",
        extraction_run_id="run-1",
        image_path=Path("crops/fig-1.png"),
        overlay_path=Path("overlays/fig-1.png"),
        table_path=Path("tables/fig-1.csv"),
        status="manually_corrected",
        reviewer="tester",
        correction=ReviewCorrection(
            corrected_points=[DataPoint(series="line", x=1.0, y=2.0)],
            notes="Corrected endpoint.",
        ),
    )
    manifest_path = tmp_path / "review.jsonl"

    ReviewManifest.from_entries([entry]).write_jsonl(manifest_path)
    loaded = ReviewManifest.read_jsonl(manifest_path)

    assert len(loaded) == 1
    assert loaded.entries[0].status == "manually_corrected"
    assert loaded.entries[0].correction is not None
    assert loaded.summary()["accepted_count"] == 1
    assert loaded.accepted()[0].review_id == "review-1"


def test_review_entry_rejects_invalid_status():
    with pytest.raises(ValidationError):
        ReviewEntry(review_id="review-1", status="approved")
