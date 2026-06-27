# Phase 1 Closeout And Phase 2 Inputs

Date: 2026-06-27

## Completed Locally

- Recorded the open software survey.
- Defined module, pipeline, dependency, provenance, and unsupported-case
  boundaries.
- Confirmed the existing code should be treated as a bootstrap seed, not a
  settled architecture.

## Phase 2 Inputs

Phase 2 should focus on:

- moving ad hoc early models toward durable `figrecover.records` contracts;
- keeping existing `Calibration` behavior stable;
- exposing deterministic extraction through an `extraction` module while
  retaining backwards-compatible imports where practical;
- using stable diagnostic codes for no-match, clipped-to-plot, low-confidence,
  ambiguous-component, and missing-bounds cases;
- expanding synthetic tests for bars, multi-series charts, log axes, noisy
  images, and diagnostic stability;
- documenting the manual calibrated image-crop workflow in Sphinx.

## Deferred

- GitHub issue creation is deferred until `UBC-FRESH/figrecover` exists.
- PDF corpus processing, VLM backends, review overlays, and FEMIC/FHOPS adapters
  remain planned future phases.
