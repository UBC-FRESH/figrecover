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

Digitization records can carry source provenance, including image ID, document
ID, figure ID, figure label, source PDF, source page, crop bounding box,
extraction tool, tool version, and extractor settings. CSV exports can include
these provenance fields when combining results across documents.

Phase 3 document preparation renders PDF pages and records candidate figure
regions before chart digitization happens. This layer remains deterministic:
PDF rendering uses PyMuPDF behind the optional ``pdf`` extra, and figure
candidates are stored as explicit manifest entries.

The first supported document-preparation workflow is:

#. Render selected PDF pages to ignored local image artifacts.
#. Create or load a JSONL figure candidate manifest.
#. Crop manifest candidates into figure images.
#. Pass prepared crops to the calibrated extraction core.

Candidate manifests can be created manually or by parser adapters. The first
adapter boundary is intentionally narrow: adapters emit canonical
``FigureCandidate`` records. The PyMuPDF image-block adapter can identify
embedded PDF images and map their page-space bounding boxes onto rendered-page
pixel coordinates. These are candidates, not guaranteed charts.

Figure candidate manifests are auditable work queues, not proof that a crop
contains a recoverable chart. Each entry should preserve source document, page
number, bounding box, candidate source, confidence, image paths, and any caption
text available from a parser or manual review.

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

Optional layers:

* heavier document parser adapters for candidate figures and captions;
* batch corpus orchestration with resumable workers;
* local VLM chart metadata proposals;
* FEMIC/FHOPS export adapters.

QA overlays, quality metrics, and review manifests are now available for
human-in-the-loop inspection after digitization. They are intentionally separate
from extraction so downstream systems can require explicit acceptance before
using recovered tables as model inputs.

Local VLM assistance can propose chart type, labels, legends, series colours,
calibration hints, and warnings. VLM outputs are proposals. They should help
reduce manual work, but calibrated
geometry remains the preferred numeric source whenever it is feasible. VLM
records preserve prompt, backend, model, raw response, parsed proposal, and
diagnostic metadata so downstream review can audit how a proposal was produced.
