from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from figrecover.documents import crop_figure_candidates, parse_page_selection, render_pdf_pages
from figrecover.manifest import FigureManifest
from figrecover.records import BoundingBox, FigureCandidate


def test_parse_page_selection_supports_ranges_and_deduplicates():
    assert parse_page_selection("1,3-5,3", page_count=6) == [1, 3, 4, 5]


def test_parse_page_selection_rejects_out_of_range_pages():
    with pytest.raises(ValueError, match="outside the document range"):
        parse_page_selection("1,7", page_count=6)


def test_manifest_round_trip_preserves_candidate_provenance(tmp_path: Path):
    page_path = tmp_path / "page.png"
    candidate = FigureCandidate(
        figure_id="fig-1",
        document_id="doc-1",
        page_number=2,
        image_path=page_path,
        source_image_path=page_path,
        bbox=BoundingBox(left=10, top=20, right=110, bottom=120),
        caption="Figure 1. Synthetic chart.",
        source="manual",
        confidence=0.9,
    )
    manifest_path = tmp_path / "figures.jsonl"

    FigureManifest.from_candidates([candidate]).write_jsonl(manifest_path)
    loaded = FigureManifest.read_jsonl(manifest_path)

    assert len(loaded) == 1
    assert loaded.candidates[0].figure_id == "fig-1"
    assert loaded.candidates[0].bbox is not None
    assert loaded.candidates[0].bbox.width == 100
    assert loaded.summary()["candidate_count"] == 1


def test_crop_figure_candidates_writes_crops_and_updates_manifest_records(tmp_path: Path):
    page_path = tmp_path / "page.png"
    image = Image.new("RGB", (100, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 30, 80, 90), fill="#1f77b4")
    image.save(page_path)

    candidate = FigureCandidate(
        figure_id="figure one",
        document_id="doc-1",
        page_number=1,
        image_path=page_path,
        source_image_path=page_path,
        bbox=BoundingBox(left=20, top=30, right=80, bottom=90),
    )

    cropped = crop_figure_candidates([candidate], tmp_path / "crops")

    assert len(cropped) == 1
    assert cropped[0].image_path.exists()
    assert cropped[0].source_image_path == page_path
    with Image.open(cropped[0].image_path) as crop:
        assert crop.size == (60, 60)


def test_render_pdf_pages_uses_one_based_page_numbers(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    pdf_path = tmp_path / "synthetic.pdf"
    document = fitz.open()
    for page_number in range(1, 4):
        page = document.new_page(width=144, height=72)
        page.insert_text((20, 36), f"Page {page_number}")
    document.save(pdf_path)
    document.close()

    rendered = render_pdf_pages(pdf_path, tmp_path / "pages", pages="1,3", dpi=72)

    assert [page.page_number for page in rendered] == [1, 3]
    assert [page.width_px for page in rendered] == [144, 144]
    assert [page.height_px for page in rendered] == [72, 72]
    assert all(page.image_path.exists() for page in rendered)
    assert rendered[0].metadata["page_count"] == 3
