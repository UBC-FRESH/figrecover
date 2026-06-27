# Architecture Contract

Date: 2026-06-27

## Purpose

Define the package boundaries for `figrecover` before expanding beyond the
current calibrated image-crop digitizer.

## Pipeline Boundaries

The durable pipeline is:

1. Document ingestion renders PDF pages and identifies candidate figures.
2. Figure manifests preserve source document, page, crop, caption, parser, and
   confidence metadata.
3. Chart metadata records describe chart type, labels, legends, series colours,
   units, and uncertainty.
4. Calibration records map pixel coordinates into data coordinates.
5. Deterministic extractors recover line, scatter, bar, histogram, or other
   chart-specific series where feasible.
6. VLM/OCR/layout tools emit proposals for metadata, calibration, and QA; they
   do not silently replace deterministic numeric extraction.
7. QA records and overlay artifacts allow humans and downstream systems to
   decide whether recovered tables are usable.
8. Export adapters write generic long tables plus sidecar provenance for
   FEMIC, FHOPS, and other modelling systems.

## Module Boundaries

- `figrecover.records`: JSON-serializable records for documents, figures,
  charts, extraction runs, recovered points, diagnostics, exports, and review
  state.
- `figrecover.calibration`: pixel/data transforms and calibration proposals.
- `figrecover.extraction`: deterministic image-level extractors.
- `figrecover.documents`: PDF rendering, cropping, and figure-candidate helpers.
- `figrecover.manifest`: JSONL manifests for figure candidates and extraction
  runs.
- `figrecover.vlm`: optional local model backends and structured proposal
  schemas.
- `figrecover.qa`: overlays, residual checks, and confidence summaries.
- `figrecover.integrations`: optional FEMIC/FHOPS export helpers.

## Dependency Boundary

Default runtime dependencies stay limited to typed records, array/image
handling, DataFrame export, and CLI rendering. Heavy dependencies move behind
extras:

- `pdf`: PyMuPDF and pypdf
- `cv`: OpenCV, scikit-image, scipy
- `parsers`: Docling and other document-layout systems when adopted
- `vlm`: local inference clients/backends
- `docs`, `dev`, `quality`, `release`, `test`: contributor tooling

## Provenance Contract

Every recovered value should be traceable to:

- source document path or identifier;
- page number and rendered page DPI;
- figure/crop bounding box and image dimensions;
- chart metadata source and confidence;
- calibration source and axis scales;
- extractor name/version/settings;
- optional model name/version/prompt/response identifier;
- diagnostics and confidence metrics.

## Unsupported Or Risky Cases

The package should emit explicit diagnostics instead of silently guessing for:

- missing or ambiguous axis calibration;
- unrecognized chart types;
- overlapping multi-series marks that cannot be separated by colour/geometry;
- low-resolution scans where marks and labels are not separable;
- 3D charts, heavy perspective distortion, decorative infographics, and maps;
- VLM metadata disagreement or schema-invalid model responses.

## Phase 2 Inputs

The next implementation phase should stabilize public records and deterministic
image-level extraction before adding more PDF, parser, VLM, or corpus pipeline
machinery.
