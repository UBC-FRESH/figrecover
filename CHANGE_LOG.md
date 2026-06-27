# Change Log

This is the append-only project narrative for `figrecover`.

## 2026-06-27

- Created the initial calibrated image-crop digitization scaffold with linear
  and log calibration, colour-based line/scatter/bar extraction, Typer CLI, and
  synthetic tests.
- Established the public UBC-FRESH package scope: deterministic numeric
  recovery first, optional local VLM assistance for chart metadata and QA.
- Added governance, roadmap, planning, and documentation scaffolding for the
  phase/task/subtask development workflow.
- Created the public GitHub repository `UBC-FRESH/figrecover`, pushed the
  bootstrap commit, created the Phase 0 issue set, and added near-term Phase 1
  and Phase 2 parent placeholders.
- Created and synchronized Phase 1 child issues, closed Phase 1, and created
  Phase 2 task issues for the first implementation lane.
- Added a local TFL 6 PDF prototype harness note and extended line extraction
  settings to support top-edge recovery from filled area charts.
- Added structured extraction diagnostics for clipped matches, sparse results,
  filtered components/runs, no-match cases, and missing plot bounds.
- Added source/crop/toolchain provenance fields to image-level digitization
  records and optional provenance columns for recovered-point exports.
- Closed the Phase 2 implementation slice locally with calibrated image-crop
  records, extraction, diagnostics, tests, docs, and Phase 3 inputs.
- Launched Phase 3 with GitHub parent and child issues for PDF rendering,
  figure manifests, optional parser adapters, CLI commands, and synthetic PDF
  tests.
- Added Phase 3 PDF rendering, JSONL figure manifests, manifest-driven cropping,
  `figrecover pdf render`, `figrecover figures list`, `figrecover figures crop`,
  synthetic PDF tests, and document-preparation docs. Parser adapter work remains
  open for P3.3.
- Completed Phase 3 with a parser adapter protocol, manual candidate adapter,
  PyMuPDF embedded image-block candidate adapter, parser deferral notes, and
  Phase 4 VLM assistance inputs.
- Added planned Phase 9 for pyOpenSci package peer review and JOSS companion
  paper publication once `figrecover` is v1.0.0 release-ready.
- Launched Phase 4 with GitHub parent and child issues for the local VLM
  assistance layer, including proposal records, local backend interface,
  structured prompts, self-ensemble utilities, and GPU/system docs.
- Added VLM proposal records for chart triage requests/results, metadata
  proposals, legend/tick/series-colour proposals, calibration hints, prompt
  provenance, raw responses, and validation diagnostics.
- Added a local VLM backend protocol and OpenAI-compatible backend boundary
  with lazy optional HTTP transport, image-plus-text request construction,
  structured proposal parsing, raw-response capture, and mocked backend tests.
- Added versioned structured VLM prompt templates and JSON response parsing
  helpers with diagnostics for markdown fences, surrounding response text,
  invalid JSON, non-object JSON, and schema validation failures.
- Added conservative VLM self-ensemble utilities that summarize repeated
  metadata proposal agreement, flag disagreements, preserve request IDs, and
  avoid numeric data-table averaging.
- Completed Phase 4 with local VLM assistance records, an OpenAI-compatible
  backend boundary, structured prompt templates, response parsing diagnostics,
  metadata self-ensemble summaries, and local VLM system documentation.
- Launched Phase 5 with GitHub parent and child issues for QA overlays,
  quality metrics, review manifests, CLI review commands, and QA workflow docs.
- Added Phase 5 QA/review workflows: visual overlays, figure quality metrics,
  JSONL review manifests, review bundle/summarize/export CLI commands, API
  reference entries, and a Sphinx guide for human-in-the-loop review.
