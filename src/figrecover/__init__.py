"""Recover approximate tabular data from published figures."""

from figrecover.calibration import Calibration
from figrecover.digitize import digitize_image
from figrecover.extraction import extract_image
from figrecover.models import (
    DataPoint,
    Diagnostic,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)

__all__ = [
    "Calibration",
    "DataPoint",
    "Diagnostic",
    "DigitizeResult",
    "DigitizeSpec",
    "SeriesResult",
    "SeriesSpec",
    "extract_image",
    "digitize_image",
]
