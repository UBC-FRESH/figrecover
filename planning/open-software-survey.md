# Open Software Survey

Date: 2026-06-27

## Purpose

Identify reusable open software that should inform `figrecover` without forcing
the package into a poor dependency, license, or workflow fit.

## Findings

- WebPlotDigitizer is the mature reference for interactive plot digitization.
  Its workflow validates the calibration-first approach, but it is not a
  Python-first batch corpus library for technical PDFs and its AGPL licensing
  means it should not be embedded into the MIT core.
- PlotDigitizer is close to the deterministic calibration idea, but its narrow
  image assumptions and one-trajectory focus are too limited for multi-series
  professional report figures.
- PyMuPDF is a practical optional dependency for rendering pages and crops from
  PDFs. It belongs in the `pdf` extra, not the default runtime dependency set.
- Docling, MinerU, and Surya are useful upstream layout/OCR/parser candidates.
  They should be optional adapters because their install footprints and APIs
  are broader than the deterministic core.
- OpenCV, scikit-image, and scipy are appropriate optional `cv` dependencies
  for more advanced segmentation, skeletonization, morphology, and geometric
  fitting after the minimal colour/component extraction core stabilizes.
- Qwen/GLM/InternVL-family local VLMs should be treated as chart-metadata and
  QA assistants. Their outputs should be structured proposals with prompts,
  model identifiers, raw responses, and confidence diagnostics, not silent
  numeric ground truth.

## Architecture Implications

- Keep the package core small, permissively licensed, and usable without GPU.
- Keep PDF rendering, parser adapters, CV enhancements, and VLM backends behind
  optional extras.
- Build internal records around provenance and diagnostics so optional tools
  can be swapped without changing downstream FEMIC/FHOPS integration contracts.

## Phase 3 Adapter Decisions

- Implemented the first parser boundary as a small protocol that emits
  canonical `FigureCandidate` records.
- Implemented PyMuPDF embedded image-block candidate discovery behind the
  existing `pdf` extra. The adapter maps PDF page-space bboxes onto rendered
  page pixel coordinates and records source/parser metadata.
- Deferred Docling, MinerU, and Surya production adapters. They remain useful
  candidates, but their broader install footprints and layout/OCR scope should
  not enter the default package or block the deterministic PDF preparation
  workflow.
