# TFL 6 MP11 Deployment Feedback For Figrecover

Date: 2026-06-28

## Purpose

Record action-oriented `figrecover` development feedback from the TFL 6 MP11
deployment test in `UBC-FRESH/femic-tfl6-instance`.

This note is public-safe. It intentionally summarizes package-design lessons
without tracking rendered PDF pages, crops, overlays, prompt logs, raw recovered
tables, or unpublished/private artifacts.

## Deployment Summary

The FEMIC TFL6 instance used `figrecover` and additional deployment scripts to
inventory, crop, extract, review, and classify chart evidence from the MP11
management-plan PDF.

Current reviewed evidence from that deployment:

- `10` figures accepted for comparison;
- `14` figures reviewed for planning only; and
- `0` figures accepted as model inputs.

The review-status separation was essential. It allowed useful recovered figure
evidence to inform MP11 planning without overstating numeric certainty.

## Chart Families Exercised

The deployment exercised:

- flat harvest-level line/fill charts;
- multi-series growing-stock line charts;
- cedar inventory stacked-area charts;
- age-class stacked bar charts;
- timber-supply impact/waterfall charts;
- old-seral multi-series line charts with target lines; and
- multi-panel crops containing more than one figure or chart panel.

## Key Lessons

### Calibration must become data

Most successful extractions depended on manual plot bounds, axis ranges, panel
offsets, or special y-band exclusions. These decisions should be stored in
reviewable calibration records rather than hard-coded script constants.

Needed package work:

- `FigureCrop` versus `PlotPanel` records;
- reusable calibration specs in JSON/YAML;
- calibration review status;
- axis/tick evidence fields; and
- calibration overlay diagnostics.

### Validation strength must be explicit

The deployment used multiple validation strengths:

- adjacent table cross-checks;
- printed chart labels plus geometry checks;
- internal component-sum residuals;
- nonnegative residual sanity checks; and
- overlay plus point-density review only.

Needed package work:

- standardized `validation_strength` field;
- standardized `review_basis` field;
- structured QA check records; and
- status summaries that do not conflate point count with validation strength.

### Review statuses are core API, not downstream decoration

Useful statuses from the deployment:

- `raw_extraction`;
- `reviewed_for_planning`;
- `accepted_for_comparison`;
- `accepted_for_model_input`;
- `needs_value_review`; and
- `not_model_input`.

Needed package work:

- formal status enums or constrained vocabularies;
- review manifest schema;
- CLI summary by status;
- downstream-use fields; and
- explicit model-input status.

### Chart-family extractors should be promoted from scripts

The deployment produced reusable extraction patterns that should become package
capabilities:

- `top_edge_of_fill`;
- `median_or_flat_line`;
- `multi_series_colour_line`;
- `component_sum_check`;
- `stacked_area_boundary`;
- `fixed_slot_stacked_bar`;
- `waterfall_label_geometry`; and
- `target_line_avoidance`.

### Overlay review needs first-class support

Visual overlays caught problems that summary CSVs could not:

- boundary confusion in stacked areas;
- panel-border contamination in bar charts;
- gridline/series colour confusion in old-seral charts; and
- incorrect panel offsets in multi-figure crops.

Needed package work:

- overlay contact-sheet generation;
- calibration-frame overlays;
- per-series sampled-point legends;
- warning annotations; and
- batch review bundles.

### Public-safe corpus summaries should be easy

The deployment used ignored runtime artifacts plus compact tracked summaries.
That pattern should be easy for package users.

Needed package work:

- standard artifact layout;
- `public-safe-summary` export mode;
- checks that prevent accidental tracking of raw PDF/page/crop/overlay/table
  artifacts; and
- case-study summary tables suitable for docs and papers.

## Proposed V1 Backlog Items

### F1 Calibration and panel records

Add durable records for figure crop, plot panel, axis calibration, tick
evidence, reviewer, status, and diagnostics.

Priority: high.

### F2 QA checks against tables, labels, and identities

Add helpers for adjacent-table comparison, printed-label transcription,
waterfall arithmetic, component-sum residuals, and tolerance recording.

Priority: high.

### F3 Reusable deterministic extractors

Promote deployment patterns into reusable extractor classes or strategy
functions.

Priority: high.

### F4 Review manifest schema and CLI summaries

Formalize status, downstream use, model-input status, validation strength,
review basis, reviewer, timestamp, and artifact references.

Priority: high.

### F5 Overlay contact sheets

Add per-batch visual review bundles with calibration frames and series legends.

Priority: medium-high.

### F6 Corpus-run case-study summarizer

Export figure-level status, chart family, validation strength, downstream use,
accepted/rejected counts, and unsupported reasons.

Priority: medium.

### F7 Public-safe artifact hygiene

Add commands/checks that enforce ignored runtime artifacts and compact tracked
summaries.

Priority: medium.

## Synthetic Fixture Targets

Add public-safe synthetic fixtures for:

- flat filled harvest-level chart with known expected value;
- three-series growing-stock chart with component-sum identity;
- stacked-area chart with total/lower boundary separation;
- fixed-slot stacked age-class chart with known panel totals;
- waterfall chart with printed labels and arithmetic residual;
- two-panel crop requiring separate plot panel bounds;
- multi-series line chart with target/dashed lines; and
- chart where gridline colour is close to a real series colour.

## Suggested Issue

Create or link a `figrecover` issue titled:

```text
Incorporate TFL6 MP11 deployment feedback into figrecover v1 roadmap
```

Acceptance for that issue:

- triage backlog items F1-F7 into concrete implementation issues;
- add at least one synthetic fixture per successful deployment chart family;
- update docs to explain review status, validation strength, and public-safe
  artifact handling; and
- preserve the TFL6 deployment as the motivating case study without tracking
  raw/generated document artifacts.
