# figrecover

`figrecover` is a public-alpha Python package for recovering approximate source
tables from published figures when the original data were not released. It is
designed for technical PDF workflows such as FEMIC timber-supply-review
ingestion, FHOPS reference-document digitisation, and other modelling pipelines
that need auditable figure-derived data.

The package uses a hybrid model:

1. Deterministic PDF and manifest tools prepare auditable figure crops.
2. Optional local VLM tools propose chart type, labels, legends, tick labels,
   calibration hints, and likely series colours.
3. Deterministic calibration maps figure pixels back into data coordinates.
4. Extractors emit auditable CSV/JSON tables with diagnostics.
5. QA/review tools generate overlays, metrics, review manifests, and
   accepted-table exports.
6. Integration adapters export reviewed recovered data for FEMIC, FHOPS, and
   generic modelling workflows.

`figrecover` is pre-release research software. It does not provide a fully
automatic PDF-to-table pipeline or precision guarantees for arbitrary charts.
Recovered values are approximate and should be reviewed before they become
scientific or operational model inputs.

## Current Alpha Scope

Supported in `0.1.0a1`:

- manual calibrated extraction from prepared image crops;
- linear and log axis transforms;
- colour-based line, scatter, and bar extraction;
- simple filled-area top-edge or bottom-edge recovery;
- deterministic PDF page rendering and figure-candidate manifests;
- QA overlays, quality metrics, JSONL review manifests, and accepted-table
  export;
- corpus artifact layout and deterministic batch preparation;
- local VLM metadata proposal records and OpenAI-compatible backend boundary;
- generic, FEMIC, and FHOPS-oriented modelling exports;
- Sphinx docs, public-safe examples, CI, and release checks.

Not supported as reliable alpha functionality:

- fully automatic arbitrary PDF-to-table recovery;
- authoritative VLM-only numeric extraction;
- low-quality scanned document OCR workflows;
- 3D charts, maps, diagrams, heatmaps, boxplots, stacked/grouped bars, contour
  plots, ternary plots, and other complex chart classes.

## Repository Conventions

This package is intended to live as a public UBC-FRESH repository under
`UBC-FRESH/figrecover` with an MIT license.

Development follows the same phase/task/subtask discipline used in
`modelwright`:

- `ROADMAP.md` maps phases and tasks to GitHub issues.
- `CHANGE_LOG.md` records the dated project narrative.
- `planning/` stores focused design notes and evidence records.
- one feature branch and one parent issue should govern each active phase.
- private PDFs, rendered pages, crops, VLM outputs, and recovered private data
  stay under ignored local paths such as `tmp/`.

## Install For Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .[dev]
pytest
```

Optional extras:

```bash
python -m pip install -e .[cv,pdf,parsers,vlm,docs,dev]
```

Run the default checks:

```bash
python -m pytest
python -m ruff check .
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

## Examples

The `examples/` directory contains publication-safe scripts that generate their
own synthetic inputs and write outputs under `tmp/examples/`:

```bash
python examples/synthetic_chart_extraction.py
python examples/synthetic_pdf_corpus.py
python examples/mocked_vlm_metadata.py
```

## CLI Example

For a cropped plot image where the plot frame spans pixels `(80, 40)` to
`(520, 360)`, and a blue line is `#1f77b4`:

```bash
figrecover digitize-image crop.png \
  --mode line \
  --series-name harvest \
  --series-color '#1f77b4' \
  --plot-left 80 --plot-right 520 --plot-top 40 --plot-bottom 360 \
  --x-min 0 --x-max 100 --y-min 0 --y-max 250 \
  --out harvest.csv
```

JSON output preserves metadata and diagnostics:

```bash
figrecover digitize-image crop.png \
  --mode scatter \
  --series-name observations \
  --series-color '#d62728' \
  --plot-left 80 --plot-right 520 --plot-top 40 --plot-bottom 360 \
  --x-min 0 --x-max 100 --y-min 0 --y-max 250 \
  --out observations.json
```

## Python Example

```python
from pathlib import Path

from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image

spec = DigitizeSpec(
    calibration=Calibration.from_plot_bounds(
        plot_left=80,
        plot_right=520,
        plot_top=40,
        plot_bottom=360,
        x_min=0,
        x_max=100,
        y_min=0,
        y_max=250,
    ),
    series=[
        SeriesSpec(name="harvest", color="#1f77b4", mode="line", tolerance=45),
    ],
)

result = digitize_image(Path("crop.png"), spec)
print(result.to_dataframe())
```

## Roadmap

Near-term phases are tracked in `ROADMAP.md`:

- Phase 0: governance and public repo bootstrap.
- Phase 1: architecture and dependency research.
- Phase 2: core records, calibration, and extraction API.
- Phase 3: document ingestion and figure cropping.
- Phase 4: local VLM assistance layer.
- Phase 5: QA, review, and human-in-the-loop workflows.
- Phase 6: batch corpus pipeline.
- Phase 7: FEMIC/FHOPS integration adapters.
- Phase 8: documentation, examples, and public alpha.
- Phase 9: scholarly publication and peer review.

## Private-Data Hygiene

Do not commit private PDFs, rendered pages, crops, overlays, review manifests,
prompt logs, VLM responses, generated corpus outputs, or recovered private
tables. Keep them under ignored local paths such as `tmp/` unless explicitly
sanitized and approved for public release.
