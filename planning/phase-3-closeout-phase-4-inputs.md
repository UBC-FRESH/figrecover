# Phase 3 Closeout And Phase 4 Inputs

Date: 2026-06-27

## Completed Scope

Phase 3 added deterministic document-preparation capabilities without requiring
VLMs:

- PDF page rendering through PyMuPDF behind the `pdf` optional extra.
- One-based page selection with ranges such as `1,3-5`.
- `RenderedPage` records with source PDF, page, DPI, dimensions, renderer, and
  output path provenance.
- JSONL `FigureManifest` support for figure candidate batch workflows.
- Manifest-driven crop creation from rendered page images.
- `figrecover pdf render`, `figrecover figures list`, and
  `figrecover figures crop` CLI commands.
- Synthetic PDF tests for rendering, manifest, cropping, and CLI workflows.
- Parser adapter boundary that emits canonical `FigureCandidate` records.
- PyMuPDF embedded image-block adapter for first-pass non-VLM candidate
  discovery.

## Deferred Or Explicitly Limited

- PyMuPDF image-block candidates are candidate regions, not guaranteed charts.
- Embedded image blocks do not cover vector-only plots or complex page layouts.
- Docling, MinerU, and Surya adapters remain deferred until their local install,
  license, API, and output quality are assessed against the manifest contract.
- OCR and caption association remain future parser/VLM/QA work.
- Corpus-scale multiprocessing and resumability remain Phase 6 work.

## Phase 4 Inputs

Phase 4 should add local VLM assistance as proposals only:

- Chart triage from prepared crops and page context.
- Chart type, title, axis label, legend, tick label, and series colour
  proposals.
- Calibration hints that can be accepted, rejected, or corrected by users.
- Structured prompt/response records with model name, endpoint, parameters,
  raw response, parsed result, validation diagnostics, and confidence.
- Self-ensemble support for metadata disagreements, not default averaging of
  recovered numeric data.

The deterministic extraction core and Phase 3 manifest/crop provenance should
remain the source of truth for numeric recovery unless a user explicitly opts
into experimental VLM-only output.

## Verification

- `python -m pytest`
- `python -m ruff check .`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
