"""Export helpers for recovered figure data."""

from __future__ import annotations

from pathlib import Path

from figrecover.models import DigitizeResult


def write_result_json(result: DigitizeResult, path: Path) -> Path:
    """Write a digitization result, including metadata and diagnostics, as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return path


def write_points_csv(
    result: DigitizeResult, path: Path, *, include_provenance: bool = False
) -> Path:
    """Write recovered points as a flat CSV table."""

    path.parent.mkdir(parents=True, exist_ok=True)
    result.to_dataframe(include_provenance=include_provenance).to_csv(path, index=False)
    return path


def write_result(result: DigitizeResult, path: Path) -> Path:
    """Write a result as JSON when the suffix is ``.json``, otherwise CSV."""

    if path.suffix.lower() == ".json":
        return write_result_json(result, path)
    return write_points_csv(result, path)


__all__ = ["write_points_csv", "write_result", "write_result_json"]
