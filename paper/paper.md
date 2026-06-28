---
title: "figrecover: Auditable recovery of approximate source tables from published technical figures"
tags:
  - Python
  - chart digitization
  - data recovery
  - PDF
  - scientific computing
  - provenance
authors:
  - name: UBC FRESH Lab
    affiliation: "1"
affiliations:
  - name: University of British Columbia, FRESH Lab
    index: 1
date: 28 June 2026
bibliography: paper.bib
---

# Summary

`figrecover` is an open-source Python package [@ubcfresh2026figrecover] for
recovering approximate tabular data from figures in scientific and professional
documents when the original source tables were not published. The package
targets charts embedded in technical PDFs, including line plots, scatter
plots, bar charts, and simple filled-area plots. Its purpose is not to promise
exact reconstruction of hidden data or fully automatic PDF-to-table
conversion. Instead, `figrecover` provides an auditable workflow for rendering
pages, isolating figure candidates, calibrating chart axes, extracting
approximate values with deterministic methods, and reviewing recovered data
before they are used in downstream research or operational models.

The package is designed for power users working with document corpora where
figures contain important quantitative evidence. Example motivating workflows
include forest-management planning, operations modelling, and historical
technical-report review. `figrecover` exposes both a Python API and a command
line interface, making it usable as a standalone recovery tool or as a
component in larger modelling systems.

# Software availability

The source repository is hosted at
`https://github.com/UBC-FRESH/figrecover`, and the current documentation is
published at `https://ubc-fresh.github.io/figrecover/`. The package is
distributed on PyPI at `https://pypi.org/project/figrecover/`. The current
public alpha release is `v0.1.0a1`; the corresponding GitHub prerelease is
available at `https://github.com/UBC-FRESH/figrecover/releases/tag/v0.1.0a1`.

This manuscript draft cites the alpha software release. Before JOSS
submission, this section and the bibliography should be updated to cite the
reviewed `v1.0.0` release and its archive DOI.

# Statement of need

Published scientific and professional reports often include figures without
the tables used to generate them. This is a practical barrier for researchers
and analysts who need to reuse older technical evidence in reproducible
modelling workflows. A chart in a report may encode values needed for scenario
comparison, calibration, validation, or metadata extraction, but manually
copying points from figures is slow and difficult to audit. The problem becomes
larger when analysts must review many reports rather than a single figure.

Existing tools address parts of this problem. Manual digitizers such as
WebPlotDigitizer provide interactive point extraction from chart images
[@rohatgi2024webplotdigitizer]. Scientific Python libraries provide numerical
arrays, tables, image processing, and computer-vision primitives
[@harris2020array; @mckinney2010data; @vanderwalt2014scikitimage; @bradski2000opencv].
PDF and document-analysis systems can preserve document layout and support
annotation or extraction workflows [@stahl2025peat]. Vision-language models
can help describe chart types, read labels, and propose legends, but current
general-purpose models should not be treated as authoritative sources of
pixel-accurate numeric data.

`figrecover` fills a workflow gap between these categories. It provides a
Python-native, provenance-preserving package for calibrated figure recovery
from technical documents. Numeric extraction is deterministic where feasible,
while optional local vision-language-model outputs are treated as metadata or
calibration proposals rather than source data. The resulting records can be
exported as tables with diagnostics, review status, and source-document
provenance.

# State of the field

Manual chart digitization remains useful because human judgment is often
needed to identify axes, legends, and ambiguous graphical elements. However,
manual workflows are hard to scale across corpora, and they often separate the
recovered values from the provenance and review decisions that produced them.
General computer-vision libraries provide the low-level building blocks for
masking, connected-component analysis, and image measurement, but they do not
provide an end-to-end scientific-document recovery workflow. Document parsers
can help with page rendering, layout segmentation, and candidate figure
discovery, but they generally do not solve calibrated data extraction from the
chart itself.

Recent vision-language models have improved chart and document understanding,
and they are useful for triage and metadata extraction. For `figrecover`,
however, the central design choice is that approximate numeric values should be
computed from pixels and calibration transforms whenever that is practical.
This deterministic-first approach is important for reviewability: users should
be able to inspect a crop, a calibration frame, extracted points, and
diagnostics before accepting a recovered table.

# Software design

`figrecover` is organized around explicit records and workflow boundaries.
Document tools render PDF pages and produce figure-candidate manifests. Record
models describe source documents, pages, figures, chart metadata, calibration
frames, recovered series, diagnostics, review decisions, and export outputs.
Calibration tools map between image pixels and data coordinates for linear and
log axes. Extraction tools recover line, scatter, bar, and simple area-series
values from prepared image crops using deterministic image processing built on
the Python scientific stack [@harris2020array; @mckinney2010data;
@vanderwalt2014scikitimage; @bradski2000opencv].

Quality-assurance tools generate overlays, summarize diagnostics, and preserve
review decisions. Corpus pipeline tools define a reproducible artifact layout
for larger document collections. Optional VLM interfaces support chart
triage, legend proposals, axis-label interpretation, and calibration hints, but
their outputs are stored as proposals rather than accepted numeric data by
default. Integration adapters export accepted recovered tables into generic
long-table formats and modelling-oriented formats for systems such as FEMIC
and FHOPS.

This architecture deliberately separates document preparation, chart
calibration, numeric extraction, review, and export. That separation makes the
software easier to test with synthetic fixtures, easier to integrate into
larger systems, and easier to audit when recovered values are used as research
inputs.

# Functionality

`figrecover` provides user-facing commands and Python APIs for several common
figure-recovery tasks:

- rendering PDF pages and recording page provenance;
- creating and loading figure-candidate manifests;
- defining manual chart calibrations for linear and log axes;
- extracting line, scatter, bar, and simple filled-area series from prepared
  crops;
- exporting recovered series as JSON, CSV, or modelling-oriented long tables;
- rendering QA overlays that compare recovered data with the source crop;
- recording accepted, rejected, or needs-review decisions in review manifests;
- processing larger document collections through a resumable corpus artifact
  layout;
- storing optional VLM chart descriptions, legend proposals, and calibration
  hints as auditable proposals.

These features are intended to keep numerical recovery, provenance, and review
state together. A recovered table can therefore be traced back to a source
document, page, crop, calibration frame, extractor, diagnostic record, and
review decision.

# Research impact statement

`figrecover` supports research workflows where previously published figures are
evidence but the original source tables are unavailable. By making calibration,
diagnostics, overlays, and review decisions explicit, the package helps users
separate accepted recovered values from unsupported or ambiguous cases. This is
important for modelling workflows that need to cite the source document,
explain how derived values were produced, and revisit those decisions later.

The package is especially relevant to technical-document corpora in which
figures encode scenario trajectories, historical conditions, cost curves,
productivity relationships, or other model inputs. Forestry and operations
modelling provide motivating examples, but the workflow is general: identify
candidate figures, recover the portion that is technically supportable, and
carry provenance and uncertainty forward with the extracted table.

# Applications and limitations

The primary planned deployment case study is a public-safe review of figures
from a TFL 6 Management Plan PDF. That case study is expected to report
relevant figures inventoried, crops produced, chart classes encountered,
deterministic extraction successes, manual review requirements, diagnostics,
and accepted recovered-table summaries. These results are not included in this
draft until document provenance and reuse permissions are resolved.

`figrecover` does not recover exact hidden source tables, and it is not a
general solution for arbitrary figures. Current deterministic extractors are
most suitable for prepared chart crops with visible axes, calibratable scales,
and graphical marks that can be isolated by colour or image structure. Complex
stacked charts, maps, dense scans, ambiguous legends, and low-quality raster
documents may require manual review, custom extractors, or may remain
unsupported. The package is therefore best understood as auditable recovery
software rather than fully automatic chart understanding software.


# AI usage disclosure

`figrecover` includes optional interfaces for local or self-hosted
vision-language models. These interfaces are designed to propose chart
metadata, legends, labels, and calibration hints. By default, VLM outputs are
not treated as authoritative recovered numeric data.

Generative AI coding assistance was used during package development and in the
preparation of this draft manuscript. Human maintainers reviewed and edited
the resulting code, documentation, planning notes, and manuscript text. Package
verification uses tests, documentation builds, package metadata checks, and
public review workflows rather than relying on generated text as evidence of
correctness.

# Acknowledgements

This work is developed by the UBC FRESH Lab. Additional funding,
collaborator, institutional, and case-study acknowledgements should be added
before submission.

# References
