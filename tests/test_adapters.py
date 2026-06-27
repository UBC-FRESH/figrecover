from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from figrecover.adapters import (
    ManualCandidateAdapter,
    extract_pymupdf_image_candidates,
)
from figrecover.documents import crop_figure_candidates, render_pdf_pages
from figrecover.manifest import FigureManifest
from figrecover.records import BoundingBox, FigureCandidate


def test_manual_candidate_adapter_returns_supplied_candidates(tmp_path: Path):
    candidate = FigureCandidate(
        figure_id="manual-1",
        image_path=tmp_path / "page.png",
        bbox=BoundingBox(left=1, top=2, right=10, bottom=12),
    )

    discovered = ManualCandidateAdapter([candidate]).discover()

    assert discovered == [candidate]


def test_pymupdf_image_block_adapter_discovers_embedded_images(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    embedded_image = tmp_path / "chart.png"
    Image.new("RGB", (100, 60), "#1f77b4").save(embedded_image)
    pdf_path = tmp_path / "embedded-image.pdf"

    document = fitz.open()
    page = document.new_page(width=200, height=160)
    page.insert_image(fitz.Rect(20, 30, 120, 90), filename=str(embedded_image))
    document.save(pdf_path)
    document.close()

    rendered = render_pdf_pages(pdf_path, tmp_path / "pages", pages="1", dpi=72)
    candidates = extract_pymupdf_image_candidates(pdf_path, rendered)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.figure_id == "embedded-image-p0001-img001"
    assert candidate.document_id == "embedded-image"
    assert candidate.page_number == 1
    assert candidate.source == "pymupdf-image-block"
    assert candidate.source_image_path == rendered[0].image_path
    assert candidate.bbox is not None
    assert candidate.bbox.left == pytest.approx(20)
    assert candidate.bbox.top == pytest.approx(30)
    assert candidate.bbox.right == pytest.approx(120)
    assert candidate.bbox.bottom == pytest.approx(90)

    manifest_path = tmp_path / "figures.jsonl"
    FigureManifest.from_candidates(candidates).write_jsonl(manifest_path)
    loaded = FigureManifest.read_jsonl(manifest_path)
    cropped = crop_figure_candidates(loaded.candidates, tmp_path / "crops")

    assert cropped[0].image_path.exists()
    with Image.open(cropped[0].image_path) as crop:
        assert crop.size == (100, 60)
