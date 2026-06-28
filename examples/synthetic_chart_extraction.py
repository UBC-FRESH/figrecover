"""Generate and digitize a synthetic line chart.

This example is publication-safe: it creates a simple synthetic image and
writes recovered outputs under ``tmp/examples/synthetic-chart`` by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image
from figrecover.io import write_points_csv, write_result_json
from figrecover.qa import render_overlay


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("tmp/examples/synthetic-chart"),
        help="Directory for generated inputs and outputs.",
    )
    args = parser.parse_args()

    paths = run_example(args.out_dir)
    for name, path in paths.items():
        print(f"{name}: {path}")


def run_example(out_dir: Path) -> dict[str, Path]:
    """Run the synthetic chart extraction example."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_path = out_dir / "synthetic-line-chart.png"
    result_path = out_dir / "synthetic-line-chart.json"
    table_path = out_dir / "synthetic-line-chart.csv"
    overlay_path = out_dir / "synthetic-line-chart-overlay.png"

    calibration = Calibration.from_plot_bounds(
        plot_left=80,
        plot_right=560,
        plot_top=40,
        plot_bottom=340,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=250,
    )
    _write_synthetic_line_chart(image_path, calibration)

    spec = DigitizeSpec(
        image_id="synthetic-line-chart",
        source_document_id="synthetic-example",
        source_figure_id="figure-1",
        figure_label="Synthetic line chart",
        calibration=calibration,
        series=[
            SeriesSpec(
                name="projection",
                color="#1f77b4",
                mode="line",
                line_aggregation="median",
            )
        ],
    )
    result = digitize_image(image_path, spec)
    write_result_json(result, result_path)
    write_points_csv(result, table_path, include_provenance=True)
    render_overlay(result, overlay_path)

    return {
        "image": image_path,
        "result": result_path,
        "table": table_path,
        "overlay": overlay_path,
    }


def _write_synthetic_line_chart(path: Path, calibration: Calibration) -> None:
    image = Image.new("RGB", (640, 400), "white")
    draw = ImageDraw.Draw(image)
    assert calibration.plot_left is not None
    assert calibration.plot_right is not None
    assert calibration.plot_top is not None
    assert calibration.plot_bottom is not None
    draw.rectangle(
        (
            calibration.plot_left,
            calibration.plot_top,
            calibration.plot_right,
            calibration.plot_bottom,
        ),
        outline="black",
        width=2,
    )

    points: list[tuple[float, float]] = []
    for x in range(0, 101):
        y = 35 + 1.65 * x
        px, py = calibration.data_to_pixel(float(x), float(y))
        points.append((px, py))
    draw.line(points, fill="#1f77b4", width=4)
    image.save(path)


if __name__ == "__main__":
    main()
