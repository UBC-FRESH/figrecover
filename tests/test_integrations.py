from __future__ import annotations

import json
from pathlib import Path

from figrecover import (
    Calibration,
    DataPoint,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)
from figrecover.integrations.femic import project_femic_export, write_femic_export
from figrecover.integrations.fhops import project_fhops_export, write_fhops_export
from figrecover.integrations.generic import build_modelling_dataframe, write_modelling_export
from figrecover.review import ReviewEntry, ReviewManifest


def _result(*, figure_id: str = "fig-1", image_id: str = "run-1") -> DigitizeResult:
    spec = DigitizeSpec(
        image_id=image_id,
        source_document_id="doc-1",
        source_figure_id=figure_id,
        figure_label="Figure 1",
        source_pdf=Path("source.pdf"),
        source_page=3,
        calibration=Calibration.from_plot_bounds(
            plot_left=0,
            plot_right=100,
            plot_top=0,
            plot_bottom=100,
            x_min=0,
            x_max=10,
            y_min=0,
            y_max=100,
        ),
        series=[SeriesSpec(name="volume", color="#1f77b4")],
    )
    return DigitizeResult(
        spec=spec,
        image_path=Path("crop.png"),
        width=100,
        height=100,
        series=[
            SeriesResult(
                spec=spec.series[0],
                points=[
                    DataPoint(series="volume", x=1.0, y=20.0, confidence=0.9),
                    DataPoint(series="volume", x=2.0, y=30.0, confidence=0.8),
                ],
            )
        ],
    )


def test_generic_modelling_dataframe_respects_review_gate():
    accepted = _result(figure_id="accepted", image_id="run-accepted")
    rejected = _result(figure_id="rejected", image_id="run-rejected")
    review = ReviewManifest.from_entries(
        [
            ReviewEntry(review_id="review-1", figure_id="accepted", status="accepted"),
            ReviewEntry(review_id="review-2", figure_id="rejected", status="rejected"),
        ]
    )

    frame = build_modelling_dataframe(
        [accepted, rejected],
        review_manifest=review,
        x_units="years",
        y_units="m3/ha",
    )

    assert len(frame) == 2
    assert set(frame["figure_id"]) == {"accepted"}
    assert frame["review_status"].unique().tolist() == ["accepted"]
    assert frame["x_units"].unique().tolist() == ["years"]
    assert frame["y_units"].unique().tolist() == ["m3/ha"]


def test_write_modelling_export_writes_csv_and_sidecar(tmp_path: Path):
    review = ReviewManifest.from_entries(
        [ReviewEntry(review_id="review-1", figure_id="fig-1", status="accepted")]
    )
    export = write_modelling_export(
        [_result()],
        tmp_path / "model.csv",
        review_manifest=review,
        x_units="years",
        y_units="m3/ha",
    )

    assert export.row_count == 2
    assert export.table_path.exists()
    assert export.sidecar_path.exists()
    payload = json.loads(export.sidecar_path.read_text(encoding="utf-8"))
    assert payload["row_count"] == 2
    assert payload["review_summary"]["accepted_count"] == 1


def test_femic_projection_preserves_provenance_and_hints(tmp_path: Path):
    frame = build_modelling_dataframe([_result()], accepted_only=False)

    femic = project_femic_export(
        frame,
        signal_family="yield_curve",
        model_input_role="metadata",
        curve_hint="treated",
    )

    assert femic["femic_figure_id"].unique().tolist() == ["fig-1"]
    assert femic["femic_signal_family"].unique().tolist() == ["yield_curve"]
    assert femic["femic_model_input_role"].unique().tolist() == ["metadata"]
    out_path = write_femic_export(frame, tmp_path / "femic.csv", signal_family="yield_curve")
    assert out_path.exists()


def test_fhops_projection_preserves_source_method_and_units(tmp_path: Path):
    frame = build_modelling_dataframe(
        [_result()],
        accepted_only=False,
        x_units="m",
        y_units="m3/pmh",
    )

    fhops = project_fhops_export(
        frame,
        reference_id="ref-1",
        source_label="Synthetic reference",
        predictor="distance_m",
        response="productivity_m3_per_pmh",
    )

    assert fhops["fhops_reference_id"].unique().tolist() == ["ref-1"]
    assert fhops["fhops_method"].unique().tolist() == ["figrecover_digitized_figure"]
    assert fhops["fhops_predictor"].unique().tolist() == ["distance_m"]
    assert fhops["y_units"].unique().tolist() == ["m3/pmh"]
    out_path = write_fhops_export(frame, tmp_path / "fhops.csv", reference_id="ref-1")
    assert out_path.exists()


def test_adapter_projections_accept_empty_generic_frame():
    frame = build_modelling_dataframe([], accepted_only=False)

    femic = project_femic_export(frame, signal_family="yield_curve")
    fhops = project_fhops_export(frame, reference_id="ref-1")

    assert femic.empty
    assert fhops.empty
    assert list(femic.columns)[0] == "femic_source_document_id"
    assert list(fhops.columns)[0] == "fhops_reference_id"
