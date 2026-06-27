# figrecover

`figrecover` is a Python package for recovering approximate source tables from
published figures when the original data were not released. It is designed for
technical PDF workflows such as FEMIC timber-supply-review ingestion and FHOPS
reference-document digitisation.

The package uses a hybrid model:

1. Document parsers isolate candidate figures from large PDFs.
2. OCR/VLM tools identify chart type, labels, legends, and likely series colours.
3. Deterministic calibration maps figure pixels back into data coordinates.
4. Extractors emit auditable CSV/JSON tables with diagnostics.

The current implementation is the deterministic core: calibrated line, scatter,
and bar extraction from image crops. Heavy PDF, layout, and VLM stacks are kept
behind optional extras so FEMIC/FHOPS can depend on the core package without
installing GPU inference dependencies.

`figrecover` is pre-release research software. It does not yet provide a fully
automatic PDF-to-table pipeline or precision guarantees for arbitrary charts.

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
