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
