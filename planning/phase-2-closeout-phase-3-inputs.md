# Phase 2 Closeout And Phase 3 Inputs

Date: 2026-06-27

## Completed

Phase 2 established the first durable calibrated image-crop extraction API:

- Pydantic records for diagnostics, points, series specs, digitization specs,
  results, source/crop/toolchain provenance, figure metadata, extraction runs,
  and export records.
- Linear and log calibration remained stable.
- Deterministic image extraction supports line, scatter, and bar charts.
- Line extraction supports median line sampling plus top/bottom edge recovery
  for filled regions.
- Extraction diagnostics now cover no-match, clipped-to-plot,
  low-confidence/sparse extraction, filtered components/runs, missing plot
  bounds, and unsupported modes.
- JSON/CSV helpers support metadata-rich JSON and optional provenance columns
  in point CSV exports.
- Sphinx docs cover the manual calibrated image-crop workflow, CLI use,
  provenance export, diagnostics, and API reference.

## Local Real-Document Harness

The ignored TFL 6 PDF harness under `tmp/tfl6_harness/` validated the first
real-document smoke test:

- Page 82 / Figure 2 was cropped from an embedded PDF image block.
- Manual calibration plus top-edge filled-area extraction recovered a flat
  harvest level around 1.055 million m3.
- The result supports Phase 3's focus on document ingestion and crop manifests.

## Deferred Or Superseded

- Full skeletonization is deferred until the optional `cv` layer is justified.
  The Phase 2 core uses dependency-light colour masks with median or edge
  column sampling, which is sufficient for the current deterministic core.
- Stacked-area, small-multiple, table-adjacent, and automatic legend/axis
  interpretation remain future work.
- The TFL 6 PDF, crops, rendered pages, and recovered data remain ignored local
  artifacts and must not be tracked.

## Phase 3 Inputs

Phase 3 should add document ingestion and figure-crop manifests:

- Render PDF pages and/or embedded image blocks through optional PyMuPDF.
- Represent source document, rendered page, figure candidate, crop bbox,
  caption, parser source, and confidence in a JSONL manifest.
- Add CLI commands for rendering pages and listing/cropping figure candidates.
- Use synthetic public-safe PDFs in tests.
- Continue using the TFL 6 harness locally to validate real embedded image
  extraction without committing private/generated artifacts.
