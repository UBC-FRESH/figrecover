# Phase 5 Closeout And Phase 6 Inputs

Date: 2026-06-27

## Completed Scope

Phase 5 added human-in-the-loop QA and review workflows:

- Overlay generation for recovered line, scatter, and bar outputs on source
  crops.
- Plot-bound rendering when calibration frame coordinates are available.
- Overlay diagnostics for recovered points that lack pixel coordinates.
- Figure-level and series-level quality metric records.
- Quality metric computation for point counts, series counts, extraction
  density, mean confidence, diagnostic severity summaries, plot-bound
  availability, and VLM ensemble disagreement.
- JSON output for quality metrics.
- Review manifest records for accepted, rejected, manually corrected,
  needs-recrop, needs-recalibration, and needs-review statuses.
- Correction records that preserve manual correction provenance separately from
  original extraction results.
- JSONL review manifest read/write helpers.
- Review CLI commands:
  - `figrecover review bundle`
  - `figrecover review summarize`
  - `figrecover review export-accepted`
- Sphinx QA/review workflow guide and CLI reference entries.
- Synthetic tests for overlay generation, quality metrics, review manifest
  serialization/status validation, and review CLI commands.

## Deferred Or Explicitly Limited

- Interactive review and manual correction UI are deferred.
- Corpus-level review orchestration, resumability, worker pools, and stable
  artifact layout are deferred to Phase 6.
- Domain-specific FEMIC/FHOPS acceptance policies are deferred to Phase 7.
- Metrics are triage aids, not correctness guarantees.
- VLM disagreement is treated as review context, not as authority over numeric
  extraction.
- Private review bundles, private crops, and recovered private data tables must
  remain under ignored local output directories unless sanitized for public use.

## Implementation Decisions

- QA overlays use Pillow to avoid adding a heavy default dependency.
- Quality metrics are Pydantic records so they remain JSON-serializable and
  compatible with future corpus manifests.
- Review manifests use JSONL to support batch workflows and append-friendly
  review queues.
- `export-accepted` only exports `accepted` and `manually_corrected` entries.
  Missing table paths are reported in JSON output rather than silently exported.
- CLI commands remain thin wrappers over Python APIs and emit JSON summaries for
  automation.

## Phase 6 Inputs

Phase 6 should turn the current document, extraction, VLM proposal, QA, and
review pieces into a resumable corpus pipeline:

- Define `CorpusRunConfig` and `RunManifest` records.
- Add YAML and JSON config loading for PDF inputs, output root, DPI, parser
  backend, VLM backend, extraction modes, worker counts, and artifact options.
- Establish stable corpus artifact directories:
  - `pages/`
  - `crops/`
  - `overlays/`
  - `tables/`
  - `manifests/`
  - `logs/`
- Use CPU parallelism for rendering, cropping, and deterministic extraction.
- Queue GPU/model-server work separately for optional VLM calls.
- Resume from manifests and skip completed artifacts.
- Continue on individual PDF/page/figure failure and emit structured
  diagnostics.
- Add corpus CLI commands:
  - `figrecover corpus init`
  - `figrecover corpus run`
  - `figrecover corpus summarize`
  - `figrecover corpus export`

Phase 6 should keep review acceptance as an explicit gate before recovered
tables are treated as downstream modelling inputs.

## Verification

- `python -m ruff check .`
- `python -m pytest` with 49 passing tests.
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
