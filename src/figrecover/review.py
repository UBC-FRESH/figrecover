"""Review manifest records for human-in-the-loop QA workflows."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from figrecover.models import DataPoint, Diagnostic
from figrecover.qa import FigureQualityMetrics

ReviewStatus = Literal[
    "accepted",
    "rejected",
    "manually_corrected",
    "needs_recrop",
    "needs_recalibration",
    "needs_review",
]


class ReviewCorrection(BaseModel):
    """Manual correction data associated with a review decision."""

    corrected_points: list[DataPoint] = Field(default_factory=list)
    corrected_table_path: Path | None = None
    notes: str | None = None
    provenance: dict[str, object] = Field(default_factory=dict)


class ReviewEntry(BaseModel):
    """One human review decision for a recovered figure/table."""

    review_id: str
    figure_id: str | None = None
    extraction_run_id: str | None = None
    image_path: Path | None = None
    overlay_path: Path | None = None
    table_path: Path | None = None
    status: ReviewStatus = "needs_review"
    reviewer: str | None = None
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None
    metrics: FigureQualityMetrics | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    correction: ReviewCorrection | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("review_id")
    @classmethod
    def _validate_review_id(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("review_id must not be empty")
        return text


class ReviewManifest(BaseModel):
    """JSONL-serializable collection of review entries."""

    entries: list[ReviewEntry] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    def __iter__(self) -> Iterator[ReviewEntry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    @classmethod
    def from_entries(
        cls,
        entries: Iterable[ReviewEntry],
        *,
        metadata: dict[str, object] | None = None,
    ) -> ReviewManifest:
        """Build a manifest from review entries."""

        return cls(entries=list(entries), metadata=metadata or {})

    @classmethod
    def read_jsonl(cls, path: Path) -> ReviewManifest:
        """Read a review manifest from newline-delimited JSON records."""

        entries: list[ReviewEntry] = []
        path = Path(path)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on review manifest line {line_number}") from exc
            entries.append(ReviewEntry.model_validate(payload))
        return cls(entries=entries, metadata={"source_path": str(path)})

    def write_jsonl(self, path: Path) -> Path:
        """Write the manifest as newline-delimited JSON review entries."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [entry.model_dump_json() for entry in self.entries]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return path

    def accepted(self) -> list[ReviewEntry]:
        """Return entries that are approved for accepted-only export."""

        return [
            entry
            for entry in self.entries
            if entry.status in {"accepted", "manually_corrected"}
        ]

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly status summary."""

        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return {
            "entry_count": len(self.entries),
            "status_counts": counts,
            "accepted_count": len(self.accepted()),
        }


__all__ = [
    "ReviewCorrection",
    "ReviewEntry",
    "ReviewManifest",
    "ReviewStatus",
]
