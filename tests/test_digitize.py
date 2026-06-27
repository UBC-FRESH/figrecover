from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image


def test_line_digitizer_recovers_simple_line(tmp_path: Path):
    image_path = tmp_path / "line.png"
    image = Image.new("RGB", (120, 120), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(10, 110), (110, 10)], fill="#1f77b4", width=3)
    image.save(image_path)

    calibration = Calibration.from_plot_bounds(
        plot_left=10,
        plot_right=110,
        plot_top=10,
        plot_bottom=110,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=100,
    )
    spec = DigitizeSpec(
        calibration=calibration,
        series=[SeriesSpec(name="line", color="#1f77b4", mode="line", tolerance=5)],
    )

    result = digitize_image(image_path, spec)
    frame = result.to_dataframe()

    assert len(frame) >= 95
    mid = frame.iloc[(frame["x"] - 50).abs().argmin()]
    assert mid["y"] == pytest.approx(50, abs=2)


def test_scatter_digitizer_recovers_components(tmp_path: Path):
    image_path = tmp_path / "scatter.png"
    image = Image.new("RGB", (120, 120), "white")
    draw = ImageDraw.Draw(image)
    for center in [(30, 90), (60, 60), (90, 30)]:
        x, y = center
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#d62728")
    image.save(image_path)

    calibration = Calibration.from_plot_bounds(
        plot_left=10,
        plot_right=110,
        plot_top=10,
        plot_bottom=110,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=100,
    )
    spec = DigitizeSpec(
        calibration=calibration,
        series=[
            SeriesSpec(
                name="points",
                color="#d62728",
                mode="scatter",
                tolerance=5,
                min_component_pixels=8,
            )
        ],
    )

    result = digitize_image(image_path, spec)
    frame = result.to_dataframe()

    assert len(frame) == 3
    assert list(frame["x"].round()) == [20, 50, 80]
    assert list(frame["y"].round()) == [20, 50, 80]


def test_bar_digitizer_recovers_simple_bars(tmp_path: Path):
    image_path = tmp_path / "bars.png"
    image = Image.new("RGB", (120, 120), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 70, 35, 110), fill="#2ca02c")
    draw.rectangle((55, 50, 70, 110), fill="#2ca02c")
    draw.rectangle((90, 30, 105, 110), fill="#2ca02c")
    image.save(image_path)

    calibration = Calibration.from_plot_bounds(
        plot_left=10,
        plot_right=110,
        plot_top=10,
        plot_bottom=110,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=100,
    )
    spec = DigitizeSpec(
        calibration=calibration,
        series=[
            SeriesSpec(
                name="bars",
                color="#2ca02c",
                mode="bar",
                tolerance=5,
                min_component_pixels=10,
            )
        ],
    )

    result = digitize_image(image_path, spec)
    frame = result.to_dataframe()

    assert len(frame) == 3
    assert list(frame["x"].round()) == [18, 52, 88]
    assert list(frame["y"].round()) == [40, 60, 80]


def test_multi_series_line_digitizer_keeps_series_separate(tmp_path: Path):
    image_path = tmp_path / "multi.png"
    image = Image.new("RGB", (120, 120), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(10, 110), (110, 10)], fill="#1f77b4", width=3)
    draw.line([(10, 60), (110, 60)], fill="#ff7f0e", width=3)
    image.save(image_path)

    calibration = Calibration.from_plot_bounds(
        plot_left=10,
        plot_right=110,
        plot_top=10,
        plot_bottom=110,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=100,
    )
    spec = DigitizeSpec(
        calibration=calibration,
        series=[
            SeriesSpec(name="diagonal", color="#1f77b4", mode="line", tolerance=5),
            SeriesSpec(name="flat", color="#ff7f0e", mode="line", tolerance=5),
        ],
    )

    result = digitize_image(image_path, spec)
    frame = result.to_dataframe()

    assert set(frame["series"]) == {"diagonal", "flat"}
    flat = frame[frame["series"] == "flat"]
    assert flat["y"].median() == pytest.approx(50, abs=2)
