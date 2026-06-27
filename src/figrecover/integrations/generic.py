"""Generic modelling export contract for recovered figure data."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from figrecover.models import DigitizeResult
from figrecover.review import ReviewEntry, ReviewManifest

ACCEPTED_REVIEW_STATUSES = {"accepted", "manually_corrected"}


class GenericModellingExport(BaseModel):
    """Paths and row count for a modelling export."""

    table_path: Path
    sidecar_path: Path
    row_count: int = Field(ge=0)


def build_modelling_dataframe(
    results: Iterable[DigitizeResult],
    *,
    review_manifest: ReviewManifest | None = None,
    accepted_only: bool = True,
    x_units: str | None = None,
    y_units: str | None = None,
) -> pd.DataFrame:
    """Build a long modelling table from digitization results.

    When ``review_manifest`` is supplied and ``accepted_only`` is true, only
    results with ``accepted`` or ``manually_corrected`` review entries are
    exported.
    """

    review_index = _review_index(review_manifest)
    rows: list[dict[str, object]] = []
    for result in results:
        review = _match_review(result, review_index)
        review_status = review.status if review is not None else "unreviewed"
        if (
            review_manifest is not None
            and accepted_only
            and review_status not in ACCEPTED_REVIEW_STATUSES
        ):
            continue
        accepted = review_status in ACCEPTED_REVIEW_STATUSES
        for series_result in result.series:
            for point in series_result.points:
                rows.append(
                    {
                        "document_id": result.spec.source_document_id,
                        "source_pdf": (
                            str(result.spec.source_pdf) if result.spec.source_pdf else None
                        ),
                        "page_number": result.spec.source_page,
                        "figure_id": result.spec.source_figure_id,
                        "image_id": result.spec.image_id,
                        "figure_label": result.spec.figure_label,
                        "series": point.series,
                        "x": point.x,
                        "y": point.y,
                        "x_units": x_units,
                        "y_units": y_units,
                        "confidence": point.confidence,
                        "review_status": review_status,
                        "review_id": review.review_id if review is not None else None,
                        "accepted": accepted,
                        "extraction_tool": result.spec.extraction_tool,
                        "extraction_tool_version": result.spec.extraction_tool_version,
                        "source_image_path": str(result.image_path),
                        "table_path": (
                            str(review.table_path)
                            if review is not None and review.table_path is not None
                            else None
                        ),
                        "overlay_path": (
                            str(review.overlay_path)
                            if review is not None and review.overlay_path is not None
                            else None
                        ),
                    }
                )
    return pd.DataFrame.from_records(rows, columns=_generic_columns())


def write_modelling_export(
    results: Iterable[DigitizeResult],
    table_path: Path,
    *,
    sidecar_path: Path | None = None,
    review_manifest: ReviewManifest | None = None,
    accepted_only: bool = True,
    x_units: str | None = None,
    y_units: str | None = None,
) -> GenericModellingExport:
    """Write a generic modelling CSV and JSON provenance sidecar."""

    result_list = list(results)
    frame = build_modelling_dataframe(
        result_list,
        review_manifest=review_manifest,
        accepted_only=accepted_only,
        x_units=x_units,
        y_units=y_units,
    )
    table_path = Path(table_path)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(table_path, index=False)
    sidecar = Path(sidecar_path) if sidecar_path is not None else table_path.with_suffix(".json")
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(
        json.dumps(
            _sidecar_payload(
                result_list,
                row_count=len(frame),
                review_manifest=review_manifest,
                table_path=table_path,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return GenericModellingExport(
        table_path=table_path,
        sidecar_path=sidecar,
        row_count=len(frame),
    )


def _generic_columns() -> list[str]:
    return [
        "document_id",
        "source_pdf",
        "page_number",
        "figure_id",
        "image_id",
        "figure_label",
        "series",
        "x",
        "y",
        "x_units",
        "y_units",
        "confidence",
        "review_status",
        "review_id",
        "accepted",
        "extraction_tool",
        "extraction_tool_version",
        "source_image_path",
        "table_path",
        "overlay_path",
    ]


def _sidecar_payload(
    results: list[DigitizeResult],
    *,
    row_count: int,
    review_manifest: ReviewManifest | None,
    table_path: Path,
) -> dict[str, object]:
    return {
        "export_kind": "figrecover.generic_modelling_export",
        "table_path": str(table_path),
        "row_count": row_count,
        "review_summary": review_manifest.summary() if review_manifest is not None else None,
        "results": [
            {
                "image_path": str(result.image_path),
                "image_id": result.spec.image_id,
                "document_id": result.spec.source_document_id,
                "figure_id": result.spec.source_figure_id,
                "source_pdf": str(result.spec.source_pdf) if result.spec.source_pdf else None,
                "source_page": result.spec.source_page,
                "calibration": result.spec.calibration.model_dump(mode="json"),
                "extraction_tool": result.spec.extraction_tool,
                "extraction_tool_version": result.spec.extraction_tool_version,
                "extraction_settings": result.spec.extraction_settings,
                "diagnostics": [
                    diagnostic.model_dump(mode="json")
                    for diagnostic in result.diagnostics
                ],
                "series": [
                    {
                        "name": series.spec.name,
                        "mode": series.spec.mode,
                        "diagnostics": [
                            diagnostic.model_dump(mode="json")
                            for diagnostic in series.diagnostics
                        ],
                    }
                    for series in result.series
                ],
            }
            for result in results
        ],
    }


def _review_index(review_manifest: ReviewManifest | None) -> dict[str, ReviewEntry]:
    if review_manifest is None:
        return {}
    index: dict[str, ReviewEntry] = {}
    for entry in review_manifest.entries:
        for key in (entry.figure_id, entry.extraction_run_id, entry.review_id):
            if key:
                index[key] = entry
    return index


def _match_review(
    result: DigitizeResult,
    review_index: dict[str, ReviewEntry],
) -> ReviewEntry | None:
    for key in (
        result.spec.source_figure_id,
        result.spec.image_id,
    ):
        if key and key in review_index:
            return review_index[key]
    return None


__all__ = [
    "ACCEPTED_REVIEW_STATUSES",
    "GenericModellingExport",
    "build_modelling_dataframe",
    "write_modelling_export",
]
