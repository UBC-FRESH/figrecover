# Release Notes

## 0.1.0a1

Public-alpha release.

### Added

- Calibrated image-crop digitization for line, scatter, bar, and simple filled
  area chart workflows.
- Pydantic records for provenance, diagnostics, calibration, extraction
  results, figure candidates, review manifests, VLM proposals, corpus runs, and
  integration exports.
- Deterministic PDF rendering, figure candidate manifests, and manifest-driven
  cropping behind optional PDF dependencies.
- Local VLM assistance boundary for chart metadata proposals, calibration
  hints, structured JSON parsing, and self-ensemble summaries.
- QA overlays, quality metrics, JSONL review manifests, and accepted-table
  export.
- Corpus configuration, artifact layout, resumable deterministic processing,
  and corpus CLI commands.
- Generic modelling export plus FEMIC and FHOPS projections.
- Sphinx documentation, public-safe examples, CI, release workflow, and package
  metadata checks.

### Limitations

- `figrecover` is alpha research software.
- Recovered data are approximate and should be reviewed before downstream use.
- VLM outputs are proposals, not authoritative numeric data by default.
- Fully automatic arbitrary PDF-to-table recovery is not supported.
- Complex chart classes such as 3D charts, heatmaps, boxplots, stacked/grouped
  bars, maps, diagrams, contour plots, and ternary plots are not reliable alpha
  targets.
- Private technical documents and recovered private values must not be tracked
  in the public repository.

### Verification Target

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- Clean install from the built wheel in a fresh environment.
