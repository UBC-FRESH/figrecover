Workflow Boundaries
===================

``figrecover`` is designed around auditable approximate recovery, not silent
fully automatic reconstruction.

Current durable boundary:

* users supply a cropped chart image;
* users supply plot-frame pixel bounds and axis data bounds;
* deterministic extractors recover coloured line, scatter, or bar series;
* filled area charts can be treated as line extraction using the top or bottom
  edge of a coloured region;
* outputs include recovered values, pixel coordinates, confidence, and
  diagnostics.

Current diagnostic codes include:

* ``no_pixels_matched`` when a series colour is not found;
* ``matched_pixels_clipped_to_plot`` when matching pixels fall outside the
  calibrated plot frame;
* ``low_confidence_extraction`` when an extractor produces sparse or empty
  results;
* ``ambiguous_components_filtered`` when small scatter components or bar runs
  are filtered;
* ``calibration_plot_bounds_missing`` when extraction falls back to the full
  image because no plot-frame bounds were supplied.

Planned optional layers:

* PDF page rendering and figure manifests;
* document parser adapters for candidate figures and captions;
* local VLM assistance for chart type, labels, legends, series colours, and
  calibration proposals;
* QA overlays and review manifests;
* FEMIC/FHOPS export adapters.

VLM outputs are proposals. They should help reduce manual work, but calibrated
geometry remains the preferred numeric source whenever it is feasible.
