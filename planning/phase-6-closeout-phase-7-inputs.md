# Phase 6 Closeout And Phase 7 Inputs

Date: 2026-06-27

## Completed Scope

Phase 6 added an initial workstation-scale corpus pipeline:

- `figrecover.pipeline` module.
- Corpus config records:
  - `CorpusInput`
  - `CorpusRenderOptions`
  - `CorpusWorkerOptions`
  - `CorpusRunConfig`
- Artifact layout records and helpers for:
  - `pages/`
  - `crops/`
  - `overlays/`
  - `tables/`
  - `manifests/`
  - `logs/`
- Stable path helpers for pages, crops, overlays, tables, manifests, and logs.
- Run manifest records:
  - `RunManifest`
  - `CorpusStepRecord`
  - `CorpusDocumentRecord`
  - `CorpusFigureRecord`
- Deterministic corpus execution through `run_corpus()`.
- PDF rendering for configured corpus inputs.
- Optional cropping from an explicit figure candidate manifest.
- Resume behavior that skips existing rendered pages.
- Structured failure diagnostics and run summaries.
- Accepted-table export from review manifests.
- Corpus CLI commands:
  - `figrecover corpus init`
  - `figrecover corpus run`
  - `figrecover corpus summarize`
  - `figrecover corpus export`
- Corpus workflow documentation and CLI/API reference entries.
- Synthetic tests for config round-trips, artifact layout, rendering, resume,
  failure continuation, figure cropping, export, and CLI smoke behavior.

## Deferred Or Explicitly Limited

- The corpus runner does not yet infer chart calibration or extraction settings
  for arbitrary figures.
- Numeric extraction in corpus mode remains dependent on explicit downstream
  configuration or manual calibrated image workflows.
- Optional VLM/model-server execution remains disabled by default.
- Distributed cluster orchestration is out of scope.
- Interactive review UI is out of scope.
- Domain-specific FEMIC/FHOPS export contracts are deferred to Phase 7.

## Implementation Decisions

- Corpus records use Pydantic for JSON-friendly provenance.
- JSON is the default config format.
- YAML loading is an optional boundary and raises a clear optional-dependency
  error if PyYAML is not installed.
- PDF rendering can use a process pool when `max_workers > 1`, but tests use one
  worker for deterministic CI behavior.
- Failure diagnostics store concise exception context instead of full private
  document text or stack traces.
- Accepted exports copy only `accepted` and `manually_corrected` review entries.

## Phase 7 Inputs

Phase 7 should make `figrecover` usable from FEMIC, FHOPS, and other modelling
systems without requiring those systems to understand internal extraction
details.

Recommended Phase 7 work:

- Inspect local FEMIC/FHOPS clones for ingestion conventions and metadata
  patterns.
- Define a generic long-table modelling export with:
  - document ID;
  - source PDF;
  - page number;
  - figure ID;
  - series;
  - `x`;
  - `y`;
  - units where known;
  - confidence;
  - review status;
  - calibration and extraction provenance sidecar.
- Add optional integration modules:
  - `figrecover.integrations.femic`
  - `figrecover.integrations.fhops`
- Keep integrations lightweight and dependent on public `figrecover` records.
- Use synthetic or explicitly public-safe fixtures only.
- Preserve source-document provenance so model inputs remain auditable.

Phase 7 should treat the Phase 6 corpus manifest and Phase 5 review manifest as
the primary handoff records.

## Verification

- `python -m ruff check .`
- `python -m pytest` with 58 passing tests.
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
