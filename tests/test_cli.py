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
from figrecover.io import write_points_csv, write_result_json
from figrecover.manifest import FigureManifest
from figrecover.records import BoundingBox, FigureCandidate
from figrecover.review import ReviewEntry, ReviewManifest


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


def test_figures_list_cli_emits_json(tmp_path: Path):
    page_path = tmp_path / "page.png"
    Image.new("RGB", (40, 40), "white").save(page_path)
    manifest_path = tmp_path / "figures.jsonl"
    FigureManifest.from_candidates(
        [
            FigureCandidate(
                figure_id="fig-1",
                document_id="doc-1",
                page_number=1,
                image_path=page_path,
                source_image_path=page_path,
                bbox=BoundingBox(left=1, top=2, right=30, bottom=35),
            )
        ]
    ).write_jsonl(manifest_path)

    result = CliRunner().invoke(app, ["figures", "list", str(manifest_path), "--json"])

    assert result.exit_code == 0
    assert '"candidate_count": 1' in result.stdout
    assert '"figure_id": "fig-1"' in result.stdout


def test_figures_crop_cli_writes_crops_and_manifest(tmp_path: Path):
    page_path = tmp_path / "page.png"
    image = Image.new("RGB", (60, 60), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 50, 50), fill="#1f77b4")
    image.save(page_path)
    manifest_path = tmp_path / "figures.jsonl"
    out_manifest = tmp_path / "cropped.jsonl"
    FigureManifest.from_candidates(
        [
            FigureCandidate(
                figure_id="fig-1",
                image_path=page_path,
                source_image_path=page_path,
                bbox=BoundingBox(left=10, top=10, right=50, bottom=50),
            )
        ]
    ).write_jsonl(manifest_path)

    result = CliRunner().invoke(
        app,
        [
            "figures",
            "crop",
            str(manifest_path),
            "--out-dir",
            str(tmp_path / "crops"),
            "--out-manifest",
            str(out_manifest),
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "crops" / "fig-1.png").exists()
    assert out_manifest.exists()
    loaded = FigureManifest.read_jsonl(out_manifest)
    assert loaded.candidates[0].image_path.name == "fig-1.png"


def test_pdf_render_cli_writes_json_summary(tmp_path: Path):
    fitz = __import__("pytest").importorskip("fitz")
    pdf_path = tmp_path / "synthetic.pdf"
    document = fitz.open()
    document.new_page(width=72, height=72)
    document.save(pdf_path)
    document.close()

    result = CliRunner().invoke(
        app,
        [
            "pdf",
            "render",
            str(pdf_path),
            "--out-dir",
            str(tmp_path / "pages"),
            "--pages",
            "1",
            "--dpi",
            "72",
        ],
    )

    assert result.exit_code == 0
    assert '"page_count": 1' in result.stdout
    assert (tmp_path / "pages" / "synthetic-p0001.png").exists()


def test_review_bundle_cli_writes_overlay_metrics_table_and_manifest(tmp_path: Path):
    image_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    spec = DigitizeSpec(
        image_id="run-1",
        source_figure_id="fig-1",
        calibration=Calibration.from_plot_bounds(
            plot_left=10,
            plot_right=90,
            plot_top=10,
            plot_bottom=90,
            x_min=0,
            x_max=1,
            y_min=0,
            y_max=1,
        ),
        series=[SeriesSpec(name="series", color="#1f77b4")],
    )
    result_json = tmp_path / "result.json"
    write_result_json(
        DigitizeResult(
            spec=spec,
            image_path=image_path,
            width=100,
            height=100,
            series=[
                SeriesResult(
                    spec=spec.series[0],
                    points=[
                        DataPoint(
                            series="series",
                            x=0.5,
                            y=0.5,
                            x_pixel=50,
                            y_pixel=50,
                        )
                    ],
                )
            ],
        ),
        result_json,
    )

    output = CliRunner().invoke(
        app,
        [
            "review",
            "bundle",
            str(result_json),
            "--out-dir",
            str(tmp_path / "review"),
        ],
    )

    assert output.exit_code == 0
    assert '"result_count": 1' in output.stdout
    assert (tmp_path / "review" / "review.jsonl").exists()
    assert (tmp_path / "review" / "overlays" / "result-overlay.png").exists()
    assert (tmp_path / "review" / "metrics" / "result-metrics.json").exists()
    assert (tmp_path / "review" / "tables" / "result.csv").exists()


def test_review_summarize_cli_emits_low_confidence_json(tmp_path: Path):
    manifest_path = tmp_path / "review.jsonl"
    ReviewManifest.from_entries(
        [
            ReviewEntry(
                review_id="review-1",
                status="needs_review",
                metadata={"review_priority": "high"},
            )
        ]
    ).write_jsonl(manifest_path)

    output = CliRunner().invoke(app, ["review", "summarize", str(manifest_path), "--json"])

    assert output.exit_code == 0
    assert '"entry_count": 1' in output.stdout
    assert '"needs_review": 1' in output.stdout


def test_review_export_accepted_cli_copies_only_accepted_tables(tmp_path: Path):
    accepted_table = tmp_path / "accepted.csv"
    rejected_table = tmp_path / "rejected.csv"
    accepted_table.write_text("series,x,y\nseries,1,2\n", encoding="utf-8")
    rejected_table.write_text("series,x,y\nseries,3,4\n", encoding="utf-8")
    manifest_path = tmp_path / "review.jsonl"
    ReviewManifest.from_entries(
        [
            ReviewEntry(
                review_id="accepted-1",
                status="accepted",
                table_path=accepted_table,
            ),
            ReviewEntry(
                review_id="rejected-1",
                status="rejected",
                table_path=rejected_table,
            ),
        ]
    ).write_jsonl(manifest_path)

    output = CliRunner().invoke(
        app,
        [
            "review",
            "export-accepted",
            str(manifest_path),
            "--out-dir",
            str(tmp_path / "accepted"),
        ],
    )

    assert output.exit_code == 0
    assert '"exported_count": 1' in output.stdout
    assert (tmp_path / "accepted" / "accepted-1.csv").exists()
    assert not (tmp_path / "accepted" / "rejected-1.csv").exists()
