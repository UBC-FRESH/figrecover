"""Batch corpus pipeline records and helpers."""

from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

from figrecover.documents import OptionalDependencyError, crop_figure_candidates, render_pdf_pages
from figrecover.manifest import FigureManifest
from figrecover.models import Diagnostic
from figrecover.records import FigureCandidate, RenderedPage
from figrecover.review import ReviewManifest

CorpusStep = Literal["config", "render", "crop", "review", "export"]
CorpusStatus = Literal["pending", "completed", "skipped", "failed"]

ARTIFACT_DIRECTORIES = ("pages", "crops", "overlays", "tables", "manifests", "logs")
T = TypeVar("T")


class CorpusInput(BaseModel):
    """PDF input selection for a corpus run."""

    pdfs: list[Path] = Field(default_factory=list)
    input_dir: Path | None = None
    pdf_glob: str = "*.pdf"

    @model_validator(mode="after")
    def _validate_inputs(self) -> CorpusInput:
        if not self.pdfs and self.input_dir is None:
            raise ValueError("provide at least one PDF path or input_dir")
        return self

    def discover_pdfs(self) -> list[Path]:
        """Return sorted, de-duplicated PDF paths from explicit and directory inputs."""

        discovered = [Path(pdf) for pdf in self.pdfs]
        if self.input_dir is not None:
            discovered.extend(sorted(Path(self.input_dir).glob(self.pdf_glob)))
        normalized: list[Path] = []
        seen: set[Path] = set()
        for pdf in discovered:
            key = pdf.expanduser()
            if key not in seen:
                normalized.append(pdf)
                seen.add(key)
        return normalized


class CorpusRenderOptions(BaseModel):
    """PDF rendering options for a corpus run."""

    dpi: int = Field(default=300, ge=1)
    pages: str | None = None
    image_format: str = "png"

    @field_validator("image_format")
    @classmethod
    def _validate_image_format(cls, value: str) -> str:
        text = value.strip().lower().lstrip(".")
        if not text:
            raise ValueError("image_format must not be empty")
        return text


class CorpusWorkerOptions(BaseModel):
    """Worker settings for workstation corpus execution."""

    max_workers: int = Field(default=1, ge=1)
    use_processes: bool = True
    vlm_max_workers: int = Field(default=1, ge=1)


class CorpusRunConfig(BaseModel):
    """Configuration for one batch corpus run."""

    run_id: str = "corpus-run"
    inputs: CorpusInput
    output_root: Path
    render: CorpusRenderOptions = Field(default_factory=CorpusRenderOptions)
    workers: CorpusWorkerOptions = Field(default_factory=CorpusWorkerOptions)
    figure_manifest: Path | None = None
    overwrite: bool = False
    resume: bool = True
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("run_id")
    @classmethod
    def _validate_run_id(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("run_id must not be empty")
        return text

    def write_json(self, path: Path) -> Path:
        """Write this config as formatted JSON."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return path

    @classmethod
    def read(cls, path: Path) -> CorpusRunConfig:
        """Read a corpus config from JSON or optional YAML."""

        path = Path(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            return cls.model_validate(_load_yaml(text))
        return cls.model_validate_json(text)


class ArtifactLayout(BaseModel):
    """Stable artifact paths under a corpus output root."""

    output_root: Path

    @property
    def pages_dir(self) -> Path:
        """Rendered page image directory."""

        return self.output_root / "pages"

    @property
    def crops_dir(self) -> Path:
        """Figure crop image directory."""

        return self.output_root / "crops"

    @property
    def overlays_dir(self) -> Path:
        """QA overlay image directory."""

        return self.output_root / "overlays"

    @property
    def tables_dir(self) -> Path:
        """Recovered or accepted table directory."""

        return self.output_root / "tables"

    @property
    def manifests_dir(self) -> Path:
        """Run, figure, and review manifest directory."""

        return self.output_root / "manifests"

    @property
    def logs_dir(self) -> Path:
        """Corpus log directory."""

        return self.output_root / "logs"

    def initialize(self) -> ArtifactLayout:
        """Create the standard corpus artifact directories."""

        for directory in self.directories().values():
            directory.mkdir(parents=True, exist_ok=True)
        return self

    def directories(self) -> dict[str, Path]:
        """Return standard artifact directory names and paths."""

        return {
            "pages": self.pages_dir,
            "crops": self.crops_dir,
            "overlays": self.overlays_dir,
            "tables": self.tables_dir,
            "manifests": self.manifests_dir,
            "logs": self.logs_dir,
        }

    def page_path(self, document_id: str, page_number: int, *, ext: str = "png") -> Path:
        """Return the stable rendered-page path for a document page."""

        return self.pages_dir / f"{safe_slug(document_id)}-p{page_number:04d}.{ext}"

    def crop_path(self, figure_id: str, *, ext: str = "png") -> Path:
        """Return the stable crop path for a figure."""

        return self.crops_dir / f"{safe_slug(figure_id)}.{ext}"

    def overlay_path(self, figure_id: str, *, ext: str = "png") -> Path:
        """Return the stable overlay path for a figure."""

        return self.overlays_dir / f"{safe_slug(figure_id)}-overlay.{ext}"

    def table_path(self, table_id: str, *, ext: str = "csv") -> Path:
        """Return the stable table path for a figure or export."""

        return self.tables_dir / f"{safe_slug(table_id)}.{ext}"

    def manifest_path(self, name: str, *, ext: str = "json") -> Path:
        """Return a stable manifest path."""

        return self.manifests_dir / f"{safe_slug(name)}.{ext}"

    def log_path(self, name: str, *, ext: str = "log") -> Path:
        """Return a stable log path."""

        return self.logs_dir / f"{safe_slug(name)}.{ext}"


class CorpusStepRecord(BaseModel):
    """Status record for one corpus processing step."""

    step: CorpusStep
    status: CorpusStatus
    identifier: str
    artifact_path: Path | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class CorpusDocumentRecord(BaseModel):
    """Run status for one source PDF."""

    document_id: str
    source_pdf: Path
    status: CorpusStatus
    page_count: int = Field(default=0, ge=0)
    rendered_pages: list[RenderedPage] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class CorpusFigureRecord(BaseModel):
    """Run status for one figure candidate."""

    figure_id: str
    status: CorpusStatus
    candidate: FigureCandidate | None = None
    crop_path: Path | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class RunManifest(BaseModel):
    """Manifest for a corpus run."""

    run_id: str
    output_root: Path
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    documents: list[CorpusDocumentRecord] = Field(default_factory=list)
    figures: list[CorpusFigureRecord] = Field(default_factory=list)
    steps: list[CorpusStepRecord] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    @classmethod
    def read_json(cls, path: Path) -> RunManifest:
        """Read a run manifest from JSON."""

        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def write_json(self, path: Path) -> Path:
        """Write this run manifest as formatted JSON."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return path

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly run summary."""

        document_counts = _count_statuses(document.status for document in self.documents)
        figure_counts = _count_statuses(figure.status for figure in self.figures)
        step_counts = _count_statuses(step.status for step in self.steps)
        failed = [
            step.identifier
            for step in self.steps
            if step.status == "failed"
        ]
        return {
            "run_id": self.run_id,
            "output_root": str(self.output_root),
            "document_count": len(self.documents),
            "figure_count": len(self.figures),
            "step_count": len(self.steps),
            "document_status_counts": document_counts,
            "figure_status_counts": figure_counts,
            "step_status_counts": step_counts,
            "diagnostic_count": len(self.diagnostics)
            + sum(len(document.diagnostics) for document in self.documents)
            + sum(len(figure.diagnostics) for figure in self.figures)
            + sum(len(step.diagnostics) for step in self.steps),
            "failed_identifiers": failed,
        }


def initialize_corpus(config: CorpusRunConfig) -> dict[str, object]:
    """Create a corpus output root and write an initial config and manifest."""

    layout = ArtifactLayout(output_root=config.output_root).initialize()
    config_path = layout.manifest_path("corpus-config")
    manifest_path = layout.manifest_path("run-manifest")
    config.write_json(config_path)
    manifest = RunManifest(run_id=config.run_id, output_root=config.output_root)
    manifest.write_json(manifest_path)
    return {
        "run_id": config.run_id,
        "output_root": str(config.output_root),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "directories": {name: str(path) for name, path in layout.directories().items()},
    }


def run_corpus(config: CorpusRunConfig) -> RunManifest:
    """Run a deterministic corpus workflow and return its run manifest."""

    layout = ArtifactLayout(output_root=config.output_root).initialize()
    manifest_path = layout.manifest_path("run-manifest")
    if config.resume and manifest_path.exists():
        manifest = RunManifest.read_json(manifest_path)
        manifest.metadata["resumed"] = True
    else:
        manifest = RunManifest(run_id=config.run_id, output_root=config.output_root)
    manifest.metadata["config"] = config.model_dump(mode="json")

    pdfs = config.inputs.discover_pdfs()
    manifest.steps.append(
        CorpusStepRecord(
            step="config",
            status="completed",
            identifier="discover-pdfs",
            metadata={"pdf_count": len(pdfs)},
        )
    )

    document_records = _render_documents(config, layout, pdfs)
    manifest.documents = _merge_records_by_id(
        manifest.documents,
        document_records,
        key=lambda record: record.document_id,
    )

    if config.figure_manifest is not None:
        figure_records, crop_step = _crop_manifest_figures(config, layout)
        manifest.figures = _merge_records_by_id(
            manifest.figures,
            figure_records,
            key=lambda record: record.figure_id,
        )
        manifest.steps.append(crop_step)

    manifest.completed_at = datetime.now(UTC)
    manifest.write_json(manifest_path)
    return manifest


def summarize_run(manifest_path: Path) -> dict[str, object]:
    """Read a run manifest and return its summary."""

    return RunManifest.read_json(manifest_path).summary()


def export_accepted_tables(review_manifest_path: Path, output_dir: Path) -> dict[str, object]:
    """Copy accepted review tables into a corpus export directory."""

    review_manifest = ReviewManifest.read_jsonl(review_manifest_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for entry in review_manifest.accepted():
        source = entry.table_path
        if (
            entry.status == "manually_corrected"
            and entry.correction is not None
            and entry.correction.corrected_table_path is not None
        ):
            source = entry.correction.corrected_table_path
        if source is None or not Path(source).exists():
            skipped.append({"review_id": entry.review_id, "reason": "missing_table_path"})
            continue
        target = output_dir / f"{safe_slug(entry.review_id)}{Path(source).suffix}"
        shutil.copy2(source, target)
        exported.append(
            {"review_id": entry.review_id, "source": str(source), "target": str(target)}
        )
    return {
        "review_manifest": str(review_manifest_path),
        "output_dir": str(output_dir),
        "exported_count": len(exported),
        "skipped_count": len(skipped),
        "exported": exported,
        "skipped": skipped,
    }


def safe_slug(value: str) -> str:
    """Return a filesystem-safe identifier slug."""

    import re

    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "artifact"


def _render_documents(
    config: CorpusRunConfig,
    layout: ArtifactLayout,
    pdfs: list[Path],
) -> list[CorpusDocumentRecord]:
    if config.workers.max_workers == 1:
        return [_render_document(config, layout, pdf) for pdf in pdfs]

    records: list[CorpusDocumentRecord] = []
    with ProcessPoolExecutor(max_workers=config.workers.max_workers) as executor:
        futures = {
            executor.submit(_render_document, config, layout, pdf): pdf
            for pdf in pdfs
        }
        for future in as_completed(futures):
            try:
                records.append(future.result())
            except Exception as exc:  # pragma: no cover - defensive process boundary
                pdf = futures[future]
                records.append(
                    CorpusDocumentRecord(
                        document_id=safe_slug(pdf.stem),
                        source_pdf=pdf,
                        status="failed",
                        diagnostics=[exception_diagnostic("render", pdf, exc)],
                    )
                )
    return sorted(records, key=lambda record: record.document_id)


def _render_document(
    config: CorpusRunConfig,
    layout: ArtifactLayout,
    pdf: Path,
) -> CorpusDocumentRecord:
    document_id = safe_slug(pdf.stem)
    try:
        if config.resume and not config.overwrite:
            existing = sorted(
                layout.pages_dir.glob(f"{document_id}-p*.{config.render.image_format}")
            )
            if existing:
                pages = [
                    RenderedPage(
                        document_id=document_id,
                        page_number=index,
                        image_path=path,
                        source_pdf=pdf,
                        width_px=1,
                        height_px=1,
                        dpi=config.render.dpi,
                        renderer="existing",
                        metadata={"resumed": True},
                    )
                    for index, path in enumerate(existing, start=1)
                ]
                return CorpusDocumentRecord(
                    document_id=document_id,
                    source_pdf=pdf,
                    status="skipped",
                    page_count=len(pages),
                    rendered_pages=pages,
                )
        pages = render_pdf_pages(
            pdf,
            layout.pages_dir,
            pages=config.render.pages,
            dpi=config.render.dpi,
            image_format=config.render.image_format,
            document_id=document_id,
            overwrite=config.overwrite,
        )
        return CorpusDocumentRecord(
            document_id=document_id,
            source_pdf=pdf,
            status="completed",
            page_count=len(pages),
            rendered_pages=pages,
        )
    except Exception as exc:
        return CorpusDocumentRecord(
            document_id=document_id,
            source_pdf=pdf,
            status="failed",
            diagnostics=[exception_diagnostic("render", pdf, exc)],
        )


def _crop_manifest_figures(
    config: CorpusRunConfig,
    layout: ArtifactLayout,
) -> tuple[list[CorpusFigureRecord], CorpusStepRecord]:
    assert config.figure_manifest is not None
    try:
        manifest = FigureManifest.read_jsonl(config.figure_manifest)
        cropped = crop_figure_candidates(
            manifest.candidates,
            layout.crops_dir,
            overwrite=config.overwrite,
            image_format=config.render.image_format,
        )
        out_manifest = FigureManifest.from_candidates(cropped).write_jsonl(
            layout.manifest_path("cropped-figures", ext="jsonl")
        )
        return (
            [
                CorpusFigureRecord(
                    figure_id=candidate.figure_id,
                    status="completed",
                    candidate=candidate,
                    crop_path=candidate.image_path,
                )
                for candidate in cropped
            ],
            CorpusStepRecord(
                step="crop",
                status="completed",
                identifier=str(config.figure_manifest),
                artifact_path=out_manifest,
                metadata={"figure_count": len(cropped)},
            ),
        )
    except Exception as exc:
        diagnostic = exception_diagnostic("crop", config.figure_manifest, exc)
        return (
            [],
            CorpusStepRecord(
                step="crop",
                status="failed",
                identifier=str(config.figure_manifest),
                diagnostics=[diagnostic],
            ),
        )


def exception_diagnostic(step: CorpusStep, item: Path, exc: Exception) -> Diagnostic:
    """Convert an exception into a concise structured diagnostic."""

    return Diagnostic(
        level="error",
        code=f"corpus_{step}_failed",
        message=str(exc),
        context={
            "step": step,
            "item": str(item),
            "exception_type": type(exc).__name__,
        },
    )


def _count_statuses(values: Iterable[CorpusStatus]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _merge_records_by_id(
    old_records: list[T],
    new_records: list[T],
    *,
    key: Callable[[T], str],
) -> list[T]:
    merged = {key(record): record for record in old_records}
    for record in new_records:
        merged[key(record)] = record
    return list(merged.values())


def _load_yaml(text: str) -> object:
    try:
        import yaml
    except ImportError as exc:
        raise OptionalDependencyError(
            "YAML config loading requires PyYAML. Install it separately or use JSON config."
        ) from exc
    return yaml.safe_load(text)


__all__ = [
    "ARTIFACT_DIRECTORIES",
    "ArtifactLayout",
    "CorpusDocumentRecord",
    "CorpusFigureRecord",
    "CorpusInput",
    "CorpusRenderOptions",
    "CorpusRunConfig",
    "CorpusStatus",
    "CorpusStep",
    "CorpusStepRecord",
    "CorpusWorkerOptions",
    "RunManifest",
    "exception_diagnostic",
    "export_accepted_tables",
    "initialize_corpus",
    "run_corpus",
    "safe_slug",
    "summarize_run",
]
