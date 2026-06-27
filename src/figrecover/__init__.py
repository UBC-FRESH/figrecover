"""Recover approximate tabular data from published figures."""

from figrecover.adapters import extract_pymupdf_image_candidates
from figrecover.calibration import Calibration
from figrecover.digitize import digitize_image
from figrecover.documents import crop_figure_candidates, render_pdf_pages
from figrecover.extraction import extract_image
from figrecover.manifest import FigureManifest
from figrecover.models import (
    DataPoint,
    Diagnostic,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)
from figrecover.records import BoundingBox, FigureCandidate, RenderedPage, SourceDocument

__all__ = [
    "BoundingBox",
    "Calibration",
    "DataPoint",
    "Diagnostic",
    "DigitizeResult",
    "DigitizeSpec",
    "FigureCandidate",
    "FigureManifest",
    "RenderedPage",
    "SeriesResult",
    "SeriesSpec",
    "SourceDocument",
    "crop_figure_candidates",
    "extract_pymupdf_image_candidates",
    "extract_image",
    "digitize_image",
    "render_pdf_pages",
]
