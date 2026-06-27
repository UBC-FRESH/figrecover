from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from figrecover.calibration import Calibration
from figrecover.digitize import digitize_image
from figrecover.documents import crop_figure_candidates, render_pdf_pages
from figrecover.io import read_result_json, write_points_csv, write_result
from figrecover.manifest import FigureManifest
from figrecover.models import DigitizeSpec, SeriesSpec
from figrecover.qa import compute_quality_metrics, render_overlay, write_quality_metrics
from figrecover.review import ReviewEntry, ReviewManifest

app = typer.Typer(help="Recover approximate source tables from calibrated figure images.")
pdf_app = typer.Typer(help="Render PDF pages for figure recovery workflows.")
figures_app = typer.Typer(help="List and crop figure candidate manifests.")
review_app = typer.Typer(help="Generate and summarize human review artifacts.")
app.add_typer(pdf_app, name="pdf")
app.add_typer(figures_app, name="figures")
app.add_typer(review_app, name="review")
console = Console()


@app.callback()
def main() -> None:
    """Recover approximate source tables from calibrated figure images."""


@app.command(name="digitize-image")
def digitize_image_command(
    image: Annotated[Path, typer.Argument(exists=True, readable=True, help="Cropped plot image.")],
    out: Annotated[Path, typer.Option(help="Output .csv or .json path.")],
    mode: Annotated[str, typer.Option(help="Extraction mode: line, scatter, or bar.")] = "line",
    series_name: Annotated[str, typer.Option(help="Series name for output rows.")] = "series",
    series_color: Annotated[str, typer.Option(help="Series colour as #RRGGBB.")] = "#1f77b4",
    tolerance: Annotated[float, typer.Option(help="Euclidean RGB colour tolerance.")] = 40.0,
    plot_left: Annotated[float, typer.Option(help="Left plot-frame pixel x coordinate.")] = 0.0,
    plot_right: Annotated[float, typer.Option(help="Right plot-frame pixel x coordinate.")] = 1.0,
    plot_top: Annotated[float, typer.Option(help="Top plot-frame pixel y coordinate.")] = 0.0,
    plot_bottom: Annotated[float, typer.Option(help="Bottom plot-frame pixel y coordinate.")] = 1.0,
    x_min: Annotated[float, typer.Option(help="Data value at left plot boundary.")] = 0.0,
    x_max: Annotated[float, typer.Option(help="Data value at right plot boundary.")] = 1.0,
    y_min: Annotated[float, typer.Option(help="Data value at bottom plot boundary.")] = 0.0,
    y_max: Annotated[float, typer.Option(help="Data value at top plot boundary.")] = 1.0,
    x_log10: Annotated[bool, typer.Option(help="Use log10 x-axis calibration.")] = False,
    y_log10: Annotated[bool, typer.Option(help="Use log10 y-axis calibration.")] = False,
    sample_every_px: Annotated[
        int, typer.Option(help="Line extraction sample stride in pixels.")
    ] = 1,
    min_component_pixels: Annotated[
        int, typer.Option(help="Minimum component size for scatter/bar extraction.")
    ] = 4,
) -> None:
    """Digitize one coloured series from a calibrated image crop."""

    calibration = Calibration.from_plot_bounds(
        plot_left=plot_left,
        plot_right=plot_right,
        plot_top=plot_top,
        plot_bottom=plot_bottom,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        x_scale="log10" if x_log10 else "linear",
        y_scale="log10" if y_log10 else "linear",
    )
    series = SeriesSpec(
        name=series_name,
        color=series_color,
        mode=mode,  # type: ignore[arg-type]
        tolerance=tolerance,
        sample_every_px=sample_every_px,
        min_component_pixels=min_component_pixels,
    )
    result = digitize_image(image, DigitizeSpec(calibration=calibration, series=[series]))
    frame = result.to_dataframe()

    write_result(result, out)

    warnings = sum(
        1
        for series_result in result.series
        for diagnostic in series_result.diagnostics
        if diagnostic.level in {"warning", "error"}
    )
    console.print(f"Wrote {len(frame)} rows to {out} ({warnings} warnings).")


@pdf_app.command(name="render")
def render_pdf_command(
    pdf: Annotated[Path, typer.Argument(exists=True, readable=True, help="Source PDF.")],
    out_dir: Annotated[Path, typer.Option(help="Output directory for rendered page images.")],
    pages: Annotated[
        str | None,
        typer.Option(help="One-based page selection such as '1,3-5'. Defaults to all pages."),
    ] = None,
    dpi: Annotated[int, typer.Option(help="Render DPI.")] = 300,
    image_format: Annotated[str, typer.Option(help="Rendered image format.")] = "png",
    document_id: Annotated[
        str | None, typer.Option(help="Stable document identifier for output filenames.")
    ] = None,
    overwrite: Annotated[bool, typer.Option(help="Replace existing rendered page images.")] = False,
) -> None:
    """Render selected PDF pages and emit a JSON summary."""

    rendered = render_pdf_pages(
        pdf,
        out_dir,
        pages=pages,
        dpi=dpi,
        image_format=image_format,
        document_id=document_id,
        overwrite=overwrite,
    )
    payload = {
        "pdf": str(pdf),
        "output_dir": str(out_dir),
        "page_count": len(rendered),
        "pages": [page.model_dump(mode="json") for page in rendered],
    }
    console.print(json.dumps(payload, indent=2))


@figures_app.command(name="list")
def list_figures_command(
    manifest: Annotated[
        Path, typer.Argument(exists=True, readable=True, help="Manifest JSONL path.")
    ],
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit JSON instead of a table.")
    ] = False,
) -> None:
    """List figure candidates from a JSONL manifest."""

    figure_manifest = FigureManifest.read_jsonl(manifest)
    if json_output:
        console.print(
            json.dumps(
                {
                    "manifest": str(manifest),
                    **figure_manifest.summary(),
                    "candidates": [
                        candidate.model_dump(mode="json")
                        for candidate in figure_manifest.candidates
                    ],
                },
                indent=2,
            )
        )
        return

    table = Table(title=f"Figure candidates: {manifest}")
    table.add_column("figure_id")
    table.add_column("document")
    table.add_column("page")
    table.add_column("source")
    table.add_column("confidence")
    table.add_column("image_path")
    for candidate in figure_manifest.candidates:
        table.add_row(
            candidate.figure_id,
            candidate.document_id or "",
            str(candidate.page_number or ""),
            candidate.source,
            f"{candidate.confidence:.2f}",
            str(candidate.image_path),
        )
    console.print(table)


@figures_app.command(name="crop")
def crop_figures_command(
    manifest: Annotated[
        Path, typer.Argument(exists=True, readable=True, help="Manifest JSONL path.")
    ],
    out_dir: Annotated[Path, typer.Option(help="Output directory for cropped figure images.")],
    out_manifest: Annotated[
        Path | None, typer.Option(help="Optional output JSONL manifest for cropped candidates.")
    ] = None,
    image_format: Annotated[str | None, typer.Option(help="Output crop image format.")] = None,
    overwrite: Annotated[
        bool, typer.Option(help="Replace existing cropped figure images.")
    ] = False,
) -> None:
    """Crop figure candidates from source page images and emit a JSON summary."""

    figure_manifest = FigureManifest.read_jsonl(manifest)
    cropped = crop_figure_candidates(
        figure_manifest.candidates,
        out_dir,
        overwrite=overwrite,
        image_format=image_format,
    )
    written_manifest: str | None = None
    if out_manifest is not None:
        FigureManifest.from_candidates(cropped, metadata=figure_manifest.metadata).write_jsonl(
            out_manifest
        )
        written_manifest = str(out_manifest)

    payload = {
        "manifest": str(manifest),
        "output_dir": str(out_dir),
        "out_manifest": written_manifest,
        "candidate_count": len(cropped),
        "candidates": [candidate.model_dump(mode="json") for candidate in cropped],
    }
    console.print(json.dumps(payload, indent=2))


@review_app.command(name="bundle")
def review_bundle_command(
    results: Annotated[
        list[Path],
        typer.Argument(
            exists=True,
            readable=True,
            help="DigitizeResult JSON files produced by figrecover.",
        ),
    ],
    out_dir: Annotated[Path, typer.Option(help="Output directory for review artifacts.")],
    manifest: Annotated[
        Path | None,
        typer.Option(help="Optional review manifest JSONL path. Defaults under out-dir."),
    ] = None,
    reviewer: Annotated[
        str | None, typer.Option(help="Reviewer name or identifier recorded in entries.")
    ] = None,
) -> None:
    """Generate overlays, metrics, tables, and a review manifest."""

    overlay_dir = out_dir / "overlays"
    metrics_dir = out_dir / "metrics"
    table_dir = out_dir / "tables"
    manifest_path = manifest or out_dir / "review.jsonl"
    entries: list[ReviewEntry] = []
    for result_path in results:
        result = read_result_json(result_path)
        stem = result_path.stem
        overlay_path = render_overlay(result, overlay_dir / f"{stem}-overlay.png").path
        metrics = compute_quality_metrics(result)
        metrics_path = write_quality_metrics(metrics, metrics_dir / f"{stem}-metrics.json")
        table_path = write_points_csv(
            result,
            table_dir / f"{stem}.csv",
            include_provenance=True,
        )
        entries.append(
            ReviewEntry(
                review_id=stem,
                figure_id=result.spec.source_figure_id,
                extraction_run_id=result.spec.image_id,
                image_path=result.image_path,
                overlay_path=overlay_path,
                table_path=table_path,
                status="needs_review",
                reviewer=reviewer,
                metrics=metrics,
                diagnostics=result.diagnostics,
                metadata={
                    "result_json": str(result_path),
                    "metrics_path": str(metrics_path),
                    "review_priority": metrics.review_priority,
                },
            )
        )
    ReviewManifest.from_entries(entries).write_jsonl(manifest_path)
    payload = {
        "result_count": len(results),
        "out_dir": str(out_dir),
        "manifest": str(manifest_path),
        "entries": [entry.model_dump(mode="json") for entry in entries],
    }
    console.print(json.dumps(payload, indent=2))


@review_app.command(name="summarize")
def review_summarize_command(
    manifest: Annotated[
        Path, typer.Argument(exists=True, readable=True, help="Review manifest JSONL path.")
    ],
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit JSON instead of a table.")
    ] = False,
) -> None:
    """Summarize review statuses and low-confidence entries."""

    review_manifest = ReviewManifest.read_jsonl(manifest)
    low_confidence = [
        entry
        for entry in review_manifest.entries
        if entry.metrics is not None
        and (
            entry.metrics.review_priority in {"medium", "high"}
            or entry.metrics.mean_confidence < 0.75
        )
    ]
    payload = {
        "manifest": str(manifest),
        **review_manifest.summary(),
        "low_confidence_count": len(low_confidence),
        "low_confidence_review_ids": [entry.review_id for entry in low_confidence],
    }
    if json_output:
        console.print(json.dumps(payload, indent=2))
        return

    table = Table(title=f"Review summary: {manifest}")
    table.add_column("status")
    table.add_column("count", justify="right")
    for status, count in payload["status_counts"].items():  # type: ignore[union-attr]
        table.add_row(str(status), str(count))
    table.add_row("low_confidence", str(len(low_confidence)))
    console.print(table)


@review_app.command(name="export-accepted")
def review_export_accepted_command(
    manifest: Annotated[
        Path, typer.Argument(exists=True, readable=True, help="Review manifest JSONL path.")
    ],
    out_dir: Annotated[Path, typer.Option(help="Output directory for accepted tables.")],
) -> None:
    """Copy accepted review tables into a downstream export directory."""

    review_manifest = ReviewManifest.read_jsonl(manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
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
        if source is None or not source.exists():
            skipped.append({"review_id": entry.review_id, "reason": "missing_table_path"})
            continue
        target = out_dir / f"{entry.review_id}{source.suffix}"
        shutil.copy2(source, target)
        exported.append(
            {"review_id": entry.review_id, "source": str(source), "target": str(target)}
        )
    payload = {
        "manifest": str(manifest),
        "out_dir": str(out_dir),
        "exported_count": len(exported),
        "skipped_count": len(skipped),
        "exported": exported,
        "skipped": skipped,
    }
    console.print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    app()
