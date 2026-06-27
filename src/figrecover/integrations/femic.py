"""FEMIC-oriented projections for recovered figure exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

FEMIC_COLUMNS = [
    "femic_source_document_id",
    "femic_source_pdf",
    "femic_source_page",
    "femic_figure_id",
    "femic_series",
    "x",
    "y",
    "x_units",
    "y_units",
    "confidence",
    "review_status",
    "review_id",
    "femic_signal_family",
    "femic_model_input_role",
    "femic_curve_hint",
    "figrecover_source_image_path",
]


def project_femic_export(
    generic_frame: pd.DataFrame,
    *,
    signal_family: str | None = None,
    model_input_role: str | None = None,
    curve_hint: str | None = None,
) -> pd.DataFrame:
    """Project a generic modelling export into FEMIC-facing columns."""

    frame = pd.DataFrame(index=generic_frame.index)
    frame["femic_source_document_id"] = generic_frame.get("document_id")
    frame["femic_source_pdf"] = generic_frame.get("source_pdf")
    frame["femic_source_page"] = generic_frame.get("page_number")
    frame["femic_figure_id"] = generic_frame.get("figure_id")
    frame["femic_series"] = generic_frame.get("series")
    frame["x"] = generic_frame.get("x")
    frame["y"] = generic_frame.get("y")
    frame["x_units"] = generic_frame.get("x_units")
    frame["y_units"] = generic_frame.get("y_units")
    frame["confidence"] = generic_frame.get("confidence")
    frame["review_status"] = generic_frame.get("review_status")
    frame["review_id"] = generic_frame.get("review_id")
    frame["femic_signal_family"] = signal_family
    frame["femic_model_input_role"] = model_input_role
    frame["femic_curve_hint"] = curve_hint
    frame["figrecover_source_image_path"] = generic_frame.get("source_image_path")
    return frame.reindex(columns=FEMIC_COLUMNS)


def write_femic_export(generic_frame: pd.DataFrame, path: Path, **kwargs: object) -> Path:
    """Write a FEMIC-projected CSV export."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    project_femic_export(generic_frame, **kwargs).to_csv(path, index=False)
    return path


__all__ = ["FEMIC_COLUMNS", "project_femic_export", "write_femic_export"]
