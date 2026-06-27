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
