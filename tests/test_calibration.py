import pytest

from figrecover import Calibration


def test_linear_calibration_roundtrip():
    calibration = Calibration.from_plot_bounds(
        plot_left=10,
        plot_right=110,
        plot_top=20,
        plot_bottom=220,
        x_min=0,
        x_max=100,
        y_min=-50,
        y_max=150,
    )

    x_pixel, y_pixel = calibration.data_to_pixel(25, 100)
    assert x_pixel == pytest.approx(35)
    assert y_pixel == pytest.approx(70)

    x, y = calibration.pixel_to_data(x_pixel, y_pixel)
    assert x == pytest.approx(25)
    assert y == pytest.approx(100)


def test_log_calibration_roundtrip():
    calibration = Calibration.from_plot_bounds(
        plot_left=0,
        plot_right=200,
        plot_top=0,
        plot_bottom=200,
        x_min=1,
        x_max=100,
        y_min=10,
        y_max=1000,
        x_scale="log10",
        y_scale="log10",
    )

    x_pixel, y_pixel = calibration.data_to_pixel(10, 100)
    assert x_pixel == pytest.approx(100)
    assert y_pixel == pytest.approx(100)
    x, y = calibration.pixel_to_data(x_pixel, y_pixel)
    assert x == pytest.approx(10)
    assert y == pytest.approx(100)
