Limitations And Supported Workflows
===================================

``figrecover`` is public-alpha software for approximate recovery of tabular
data from figures. It is designed for auditable workflows, not silent
fully automatic reconstruction.

Supported In The Current Alpha
------------------------------

The current package supports:

* manual calibrated extraction from prepared image crops;
* linear and log axis transforms;
* colour-based line extraction;
* top-edge or bottom-edge recovery from simple filled area charts;
* colour-based scatter extraction using connected components;
* colour-based bar extraction using contiguous runs;
* deterministic PDF page rendering with the optional ``pdf`` extra;
* figure candidate manifests and manifest-driven cropping;
* QA overlays and quality metrics;
* JSONL review manifests and accepted-table export;
* corpus artifact layout and resumable deterministic preparation;
* local VLM proposals for metadata, legends, labels, ticks, colours, and
  calibration hints;
* generic, FEMIC, and FHOPS-oriented modelling exports.

Partially Supported
-------------------

These cases may work, but usually need manual tuning or review:

* multi-series plots with similar colours;
* anti-aliased or compressed raster charts;
* filled area charts where the boundary is visually ambiguous;
* plots with dense annotations or overlapping labels;
* charts embedded in complex PDF layouts;
* log axes where tick labels are hard to read;
* charts that require parser or VLM assistance for metadata.

Unsupported Or Experimental
---------------------------

Do not treat the current alpha as a reliable solution for:

* automatic recovery from arbitrary PDFs without review;
* 3D charts, maps, diagrams, network plots, flow charts, or schematic figures;
* stacked bars, grouped bars, boxplots, violin plots, heatmaps, ternary plots,
  and contour plots;
* OCR-heavy reconstruction of low-quality scanned documents;
* hidden source-data recovery when the figure itself does not contain enough
  visual information;
* VLM-only numeric table extraction as an authoritative path.

VLM Boundary
------------

Local VLMs can reduce manual labour by proposing chart type, axis labels,
legend entries, series colours, tick labels, calibration hints, and warnings.
Those outputs are proposals. They should be validated against the source crop
and deterministic extraction diagnostics before use.

Private-Data Hygiene
--------------------

Technical documents, rendered pages, crops, overlays, review manifests, prompt
transcripts, and recovered tables can contain private or unpublished data. Keep
them under ignored directories such as ``tmp/`` unless they have been explicitly
approved for public release.

Quality Expectations
--------------------

Recovered values are approximate. Use overlays, metrics, review statuses, and
source provenance to decide whether a table is fit for a specific downstream
purpose. High-impact scientific, operational, legal, or financial decisions
should not rely on unreviewed recovered values.
