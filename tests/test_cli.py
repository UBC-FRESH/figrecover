from pathlib import Path

from PIL import Image, ImageDraw
from typer.testing import CliRunner

from figrecover import (
    Calibration,
    DataPoint,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)
from figrecover.cli import app
from figrecover.io import write_points_csv


def test_digitize_image_cli_writes_csv(tmp_path: Path):
    image_path = tmp_path / "line.png"
    out_path = tmp_path / "line.csv"
    image = Image.new("RGB", (120, 120), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(10, 110), (110, 10)], fill="#1f77b4", width=3)
    image.save(image_path)

    result = CliRunner().invoke(
        app,
        [
            "digitize-image",
            str(image_path),
            "--out",
            str(out_path),
            "--series-name",
            "line",
            "--series-color",
            "#1f77b4",
            "--plot-left",
            "10",
            "--plot-right",
            "110",
            "--plot-top",
            "10",
            "--plot-bottom",
            "110",
            "--x-min",
            "0",
            "--x-max",
            "100",
            "--y-min",
            "0",
            "--y-max",
            "100",
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()
    assert out_path.read_text(encoding="utf-8").startswith("series,x,y")


def test_write_points_csv_can_include_provenance(tmp_path: Path):
    spec = DigitizeSpec(
        image_id="crop-1",
        source_document_id="doc-1",
        calibration=Calibration.from_plot_bounds(
            plot_left=0,
            plot_right=10,
            plot_top=0,
            plot_bottom=10,
            x_min=0,
            x_max=1,
            y_min=0,
            y_max=1,
        ),
        series=[SeriesSpec(name="series", color="#1f77b4")],
    )
    result = DigitizeResult(
        spec=spec,
        image_path=Path("crop.png"),
        width=10,
        height=10,
        series=[
            SeriesResult(
                spec=spec.series[0],
                points=[DataPoint(series="series", x=0.0, y=1.0)],
            )
        ],
    )
    out_path = tmp_path / "points.csv"

    write_points_csv(result, out_path, include_provenance=True)

    header = out_path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("image_path,image_id,source_document_id")
