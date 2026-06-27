from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from figrecover.calibration import Calibration
from figrecover.digitize import digitize_image
from figrecover.documents import crop_figure_candidates, render_pdf_pages
from figrecover.io import write_result
from figrecover.manifest import FigureManifest
from figrecover.models import DigitizeSpec, SeriesSpec

app = typer.Typer(help="Recover approximate source tables from calibrated figure images.")
pdf_app = typer.Typer(help="Render PDF pages for figure recovery workflows.")
figures_app = typer.Typer(help="List and crop figure candidate manifests.")
app.add_typer(pdf_app, name="pdf")
app.add_typer(figures_app, name="figures")
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


if __name__ == "__main__":
    app()
