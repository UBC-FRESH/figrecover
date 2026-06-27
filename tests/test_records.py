from pathlib import Path

from figrecover import (
    Calibration,
    DataPoint,
    DigitizeResult,
    DigitizeSpec,
    SeriesResult,
    SeriesSpec,
)
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


def test_digitize_result_dataframe_can_include_provenance():
    spec = DigitizeSpec(
        image_id="crop-1",
        source_document_id="doc-1",
        source_figure_id="fig-1",
        figure_label="Figure 1",
        source_pdf=Path("reports/source.pdf"),
        source_page=12,
        source_crop_bbox=(10.0, 20.0, 110.0, 120.0),
        extraction_tool="figrecover.digitize",
        calibration=Calibration.from_plot_bounds(
            plot_left=10,
            plot_right=110,
            plot_top=10,
            plot_bottom=110,
            x_min=0,
            x_max=100,
            y_min=0,
            y_max=100,
        ),
        series=[SeriesSpec(name="line", color="#1f77b4")],
    )
    result = DigitizeResult(
        spec=spec,
        image_path=Path("crops/crop-1.png"),
        width=120,
        height=120,
        series=[
            SeriesResult(
                spec=spec.series[0],
                points=[DataPoint(series="line", x=1.0, y=2.0, x_pixel=10, y_pixel=20)],
            )
        ],
    )

    frame = result.to_dataframe(include_provenance=True)

    assert frame.loc[0, "image_id"] == "crop-1"
    assert frame.loc[0, "source_document_id"] == "doc-1"
    assert frame.loc[0, "source_pdf"] == "reports/source.pdf"
    assert frame.loc[0, "source_crop_bbox"] == (10.0, 20.0, 110.0, 120.0)
