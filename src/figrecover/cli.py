from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from figrecover.calibration import Calibration
from figrecover.digitize import digitize_image
from figrecover.io import write_result
from figrecover.models import DigitizeSpec, SeriesSpec

app = typer.Typer(help="Recover approximate source tables from calibrated figure images.")
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


if __name__ == "__main__":
    app()
