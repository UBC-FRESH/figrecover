"""FHOPS-oriented projections for recovered figure exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

FHOPS_COLUMNS = [
    "fhops_reference_id",
    "fhops_source_label",
    "fhops_method",
    "fhops_predictor",
    "fhops_response",
    "x",
    "y",
    "x_units",
    "y_units",
    "confidence",
    "review_status",
    "review_id",
    "document_id",
    "source_pdf",
    "page_number",
    "figure_id",
]


def project_fhops_export(
    generic_frame: pd.DataFrame,
    *,
    reference_id: str | None = None,
    source_label: str | None = None,
    method: str = "figrecover_digitized_figure",
    predictor: str | None = None,
    response: str | None = None,
) -> pd.DataFrame:
    """Project a generic modelling export into FHOPS-facing reference rows."""

    frame = pd.DataFrame(index=generic_frame.index)
    frame["fhops_reference_id"] = reference_id
    frame["fhops_source_label"] = source_label
    frame["fhops_method"] = method
    frame["fhops_predictor"] = predictor
    frame["fhops_response"] = response
    frame["x"] = generic_frame.get("x")
    frame["y"] = generic_frame.get("y")
    frame["x_units"] = generic_frame.get("x_units")
    frame["y_units"] = generic_frame.get("y_units")
    frame["confidence"] = generic_frame.get("confidence")
    frame["review_status"] = generic_frame.get("review_status")
    frame["review_id"] = generic_frame.get("review_id")
    frame["document_id"] = generic_frame.get("document_id")
    frame["source_pdf"] = generic_frame.get("source_pdf")
    frame["page_number"] = generic_frame.get("page_number")
    frame["figure_id"] = generic_frame.get("figure_id")
    return frame.reindex(columns=FHOPS_COLUMNS)


def write_fhops_export(generic_frame: pd.DataFrame, path: Path, **kwargs: object) -> Path:
    """Write a FHOPS-projected CSV export."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    project_fhops_export(generic_frame, **kwargs).to_csv(path, index=False)
    return path


__all__ = ["FHOPS_COLUMNS", "project_fhops_export", "write_fhops_export"]
