from pathlib import Path

from PIL import Image, ImageDraw
from typer.testing import CliRunner

from figrecover.cli import app


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
