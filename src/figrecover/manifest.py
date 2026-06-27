"""Manifest records for batch figure-candidate workflows."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path

from pydantic import BaseModel, Field

from figrecover.records import FigureCandidate


class FigureManifest(BaseModel):
    """A JSONL-serializable collection of figure candidates."""

    candidates: list[FigureCandidate] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    def __iter__(self) -> Iterator[FigureCandidate]:
        return iter(self.candidates)

    def __len__(self) -> int:
        return len(self.candidates)

    @classmethod
    def from_candidates(
        cls,
        candidates: Iterable[FigureCandidate],
        *,
        metadata: dict[str, object] | None = None,
    ) -> FigureManifest:
        """Build a manifest from candidate records."""

        return cls(candidates=list(candidates), metadata=metadata or {})

    @classmethod
    def read_jsonl(cls, path: Path) -> FigureManifest:
        """Read a figure manifest from newline-delimited JSON records."""

        candidates: list[FigureCandidate] = []
        path = Path(path)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on manifest line {line_number}") from exc
            candidates.append(FigureCandidate.model_validate(payload))
        return cls(candidates=candidates, metadata={"source_path": str(path)})

    def write_jsonl(self, path: Path) -> Path:
        """Write the manifest as newline-delimited JSON candidate records."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [candidate.model_dump_json() for candidate in self.candidates]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return path

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly manifest summary."""

        return {
            "candidate_count": len(self.candidates),
            "sources": sorted({candidate.source for candidate in self.candidates}),
            "documents": sorted(
                {
                    candidate.document_id
                    for candidate in self.candidates
                    if candidate.document_id is not None
                }
            ),
        }


__all__ = ["FigureManifest"]
