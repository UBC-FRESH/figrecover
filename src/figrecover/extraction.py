"""Deterministic image-level extraction APIs.

This module is the public extraction boundary. It currently exposes calibrated
colour-based extraction for prepared chart crops. Future extractors should live
behind this boundary rather than being wired directly into the CLI.
"""

from pathlib import Path

from figrecover.digitize import digitize_image
from figrecover.models import DigitizeResult, DigitizeSpec


def extract_image(path: Path, spec: DigitizeSpec) -> DigitizeResult:
    """Extract calibrated series from an image crop.

    Parameters
    ----------
    path:
        Path to a prepared chart image crop.
    spec:
        Calibration and series extraction settings.

    Returns
    -------
    DigitizeResult
        Recovered points and diagnostics for each requested series.
    """

    return digitize_image(path, spec)


__all__ = ["extract_image", "digitize_image"]
