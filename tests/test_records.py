from pathlib import Path

from figrecover.records import (
    BoundingBox,
    ChartMetadata,
    ExportRecord,
    ExtractionRun,
    ExtractionToolchain,
    FigureCandidate,
    SourceDocument,
)


def test_source_and_figure_records_are_json_serializable():
    document = SourceDocument(document_id="doc-1", path=Path("reports/report.pdf"))
    figure = FigureCandidate(
        figure_id="fig-1",
        document_id=document.document_id,
        page_number=4,
        image_path=Path("crops/doc-1-p004-fig-1.png"),
        bbox=BoundingBox(left=10, top=20, right=210, bottom=120),
        caption="Figure 1. Synthetic chart.",
    )

    payload = figure.model_dump(mode="json")

    assert payload["image_path"] == "crops/doc-1-p004-fig-1.png"
    assert payload["bbox"]["right"] == 210
    assert figure.bbox is not None
    assert figure.bbox.width == 200


def test_extraction_run_and_export_record_are_json_serializable():
    figure = FigureCandidate(figure_id="fig-1", image_path=Path("crop.png"))
    run = ExtractionRun(
        run_id="run-1",
        figure=figure,
        chart=ChartMetadata(chart_type="line", title="Synthetic line"),
        toolchain=ExtractionToolchain(extractor="figrecover.digitize"),
    )
    export = ExportRecord(
        export_id="export-1",
        path=Path("tables/recovered.csv"),
        format="csv",
        row_count=10,
        source_run_ids=[run.run_id],
    )

    assert run.model_dump(mode="json")["toolchain"]["extractor"] == "figrecover.digitize"
    assert export.model_dump(mode="json")["source_run_ids"] == ["run-1"]
