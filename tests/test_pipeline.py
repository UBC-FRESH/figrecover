from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from figrecover.manifest import FigureManifest
from figrecover.pipeline import (
    ArtifactLayout,
    CorpusInput,
    CorpusRenderOptions,
    CorpusRunConfig,
    CorpusWorkerOptions,
    RunManifest,
    export_accepted_tables,
    run_corpus,
    safe_slug,
)
from figrecover.records import BoundingBox, FigureCandidate
from figrecover.review import ReviewEntry, ReviewManifest


def _synthetic_pdf(path: Path, *, pages: int = 1) -> Path:
    fitz = pytest.importorskip("fitz")
    document = fitz.open()
    for page_number in range(1, pages + 1):
        page = document.new_page(width=72, height=72)
        page.insert_text((12, 36), f"Page {page_number}")
    document.save(path)
    document.close()
    return path


def test_corpus_config_round_trip_json(tmp_path: Path):
    pdf_path = tmp_path / "source.pdf"
    config = CorpusRunConfig(
        run_id="run-1",
        inputs=CorpusInput(pdfs=[pdf_path]),
        output_root=tmp_path / "out",
        render=CorpusRenderOptions(dpi=100, pages="1"),
        workers=CorpusWorkerOptions(max_workers=1),
    )
    config_path = tmp_path / "config.json"

    config.write_json(config_path)
    loaded = CorpusRunConfig.read(config_path)

    assert loaded.run_id == "run-1"
    assert loaded.inputs.pdfs == [pdf_path]
    assert loaded.render.dpi == 100
    assert loaded.workers.max_workers == 1


def test_corpus_input_requires_pdf_or_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="provide at least one PDF path"):
        CorpusRunConfig(inputs=CorpusInput(), output_root=tmp_path / "out")


def test_artifact_layout_creates_stable_paths(tmp_path: Path):
    layout = ArtifactLayout(output_root=tmp_path / "corpus").initialize()

    assert all(path.exists() for path in layout.directories().values())
    assert layout.page_path("Forest Plan 1", 3).name == "Forest-Plan-1-p0003.png"
    assert layout.crop_path("Figure 1/a").name == "Figure-1-a.png"
    assert layout.overlay_path("Figure 1/a").name == "Figure-1-a-overlay.png"
    assert layout.table_path("Figure 1/a").name == "Figure-1-a.csv"
    assert safe_slug("  weird / name  ") == "weird-name"


def test_run_corpus_renders_synthetic_pdf_and_writes_manifest(tmp_path: Path):
    pdf_path = _synthetic_pdf(tmp_path / "source.pdf", pages=2)
    config = CorpusRunConfig(
        run_id="run-1",
        inputs=CorpusInput(pdfs=[pdf_path]),
        output_root=tmp_path / "corpus",
        render=CorpusRenderOptions(dpi=72, pages="1"),
    )

    manifest = run_corpus(config)

    assert manifest.summary()["document_status_counts"]["completed"] == 1
    assert (tmp_path / "corpus" / "pages" / "source-p0001.png").exists()
    manifest_path = tmp_path / "corpus" / "manifests" / "run-manifest.json"
    assert RunManifest.read_json(manifest_path).summary()["document_count"] == 1


def test_run_corpus_resume_skips_existing_rendered_pages(tmp_path: Path):
    pdf_path = _synthetic_pdf(tmp_path / "source.pdf")
    config = CorpusRunConfig(
        run_id="run-1",
        inputs=CorpusInput(pdfs=[pdf_path]),
        output_root=tmp_path / "corpus",
        render=CorpusRenderOptions(dpi=72),
    )

    first = run_corpus(config)
    second = run_corpus(config)

    assert first.summary()["document_status_counts"]["completed"] == 1
    assert second.summary()["document_status_counts"]["skipped"] == 1
    assert second.metadata["resumed"] is True


def test_run_corpus_continues_after_bad_pdf(tmp_path: Path):
    good_pdf = _synthetic_pdf(tmp_path / "good.pdf")
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_text("not a pdf", encoding="utf-8")
    config = CorpusRunConfig(
        run_id="run-1",
        inputs=CorpusInput(pdfs=[good_pdf, bad_pdf]),
        output_root=tmp_path / "corpus",
        render=CorpusRenderOptions(dpi=72),
    )

    manifest = run_corpus(config)
    summary = manifest.summary()

    assert summary["document_status_counts"]["completed"] == 1
    assert summary["document_status_counts"]["failed"] == 1
    assert summary["diagnostic_count"] >= 1


def test_run_corpus_crops_supplied_figure_manifest(tmp_path: Path):
    pdf_path = _synthetic_pdf(tmp_path / "source.pdf")
    page_path = tmp_path / "page.png"
    image = Image.new("RGB", (80, 80), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 50, 50), fill="#1f77b4")
    image.save(page_path)
    figure_manifest = tmp_path / "figures.jsonl"
    FigureManifest.from_candidates(
        [
            FigureCandidate(
                figure_id="fig-1",
                image_path=page_path,
                source_image_path=page_path,
                bbox=BoundingBox(left=10, top=10, right=50, bottom=50),
            )
        ]
    ).write_jsonl(figure_manifest)
    config = CorpusRunConfig(
        run_id="run-1",
        inputs=CorpusInput(pdfs=[pdf_path]),
        output_root=tmp_path / "corpus",
        render=CorpusRenderOptions(dpi=72),
        figure_manifest=figure_manifest,
    )

    manifest = run_corpus(config)

    assert manifest.summary()["figure_status_counts"]["completed"] == 1
    assert (tmp_path / "corpus" / "crops" / "fig-1.png").exists()
    assert (tmp_path / "corpus" / "manifests" / "cropped-figures.jsonl").exists()


def test_export_accepted_tables_copies_only_accepted_entries(tmp_path: Path):
    accepted = tmp_path / "accepted.csv"
    rejected = tmp_path / "rejected.csv"
    accepted.write_text("series,x,y\nseries,1,2\n", encoding="utf-8")
    rejected.write_text("series,x,y\nseries,3,4\n", encoding="utf-8")
    review_manifest = tmp_path / "review.jsonl"
    ReviewManifest.from_entries(
        [
            ReviewEntry(review_id="accepted", status="accepted", table_path=accepted),
            ReviewEntry(review_id="rejected", status="rejected", table_path=rejected),
        ]
    ).write_jsonl(review_manifest)

    summary = export_accepted_tables(review_manifest, tmp_path / "exports")

    assert summary["exported_count"] == 1
    assert (tmp_path / "exports" / "accepted.csv").exists()
    assert not (tmp_path / "exports" / "rejected.csv").exists()
