# FEMIC/FHOPS Integration Survey

Date: 2026-06-27

## Scope And Hygiene

This survey inspected local source, tests, docs, and config conventions in:

- `~/projects/femic`
- `~/projects/fhops`

Private source PDFs, generated corpus artifacts, private extracted tables, and
large TSR metadata payloads were not copied into this note. A broad search
initially touched large FEMIC TSR metadata, so the inspection was narrowed back
to code/docs/tests/config surfaces before recording findings.

## Shared Integration Implications

`figrecover` should provide a generic long-table modelling export as the stable
handoff contract, with domain adapters as thin projections.

Required generic fields:

- `document_id`
- `source_pdf`
- `page_number`
- `figure_id`
- `image_id`
- `figure_label`
- `series`
- `x`
- `y`
- `x_units`
- `y_units`
- `confidence`
- `review_status`
- `review_id`
- `accepted`
- `extraction_tool`
- `extraction_tool_version`
- `source_image_path`
- `table_path`
- `overlay_path`

Required sidecar content:

- export metadata and row count;
- source result summaries;
- calibration settings;
- extraction diagnostics;
- review manifest summary when present;
- source artifact paths.

Review acceptance should be explicit. When a review manifest is supplied,
default modelling export should include only `accepted` and
`manually_corrected` entries unless the caller opts out.

## FEMIC Findings

Relevant conventions observed:

- FEMIC uses CSV bundle tables under `data/model_input_bundle/`:
  - `au_table.csv`
  - `curve_table.csv`
  - `curve_points_table.csv`
- Curve point tables use `x` and `y` columns, with curve identifiers linking
  point rows to model entities.
- FEMIC export surfaces include Patchworks and Woodstock outputs.
- Woodstock export writes CSV files such as:
  - `woodstock_yields.csv`
  - `woodstock_areas.csv`
  - `woodstock_actions.csv`
  - `woodstock_transitions.csv`
- Run manifests are JSON and emphasize:
  - `run_id`
  - runtime versions;
  - runtime parameters;
  - config provenance;
  - output paths;
  - checkpoint/log artifact paths.
- Run profiles and named pipelines use YAML/JSON-style config records.
- Source provenance is already a first-class idea in FEMIC workflows.

FEMIC adapter implications:

- Keep the base output as long-table CSV plus JSON sidecar.
- Include FEMIC-friendly aliases while preserving generic field names.
- Preserve `source_pdf`, page, figure, review status, and confidence.
- Include optional columns that FEMIC can map later to analysis-unit or curve
  semantics:
  - `femic_signal_family`
  - `femic_model_input_role`
  - `femic_curve_hint`
- Do not write directly into FEMIC `data/` or `output/` directories by default.

## FHOPS Findings

Relevant conventions observed:

- FHOPS scenarios are YAML metadata files that reference CSV component tables.
- Scenario inputs are typed with Pydantic models.
- Common scenario/input concepts include:
  - blocks;
  - machines;
  - landings;
  - calendars;
  - production rates;
  - harvest system IDs;
  - optional road construction and shift calendars.
- FHOPS exports solver assignments and summaries as CSV/JSON.
- Telemetry uses JSONL records with fields such as:
  - `record_type`
  - `schema_version`
  - `run_id`
  - `scenario_path`
  - `status`
  - `metrics`
  - `config`
  - `context`
  - `artifacts`
- Productivity/reference modules use typed dataclasses with source metadata,
  units, cost years, and method-specific fields.
- Documentation emphasizes units, citations/source labels, return schemas, and
  validation/range warnings.

FHOPS adapter implications:

- Keep export rows suitable as reference evidence or productivity/regression
  inputs, not as FHOPS scenarios directly.
- Preserve source/method metadata:
  - `fhops_reference_id`
  - `fhops_source_label`
  - `fhops_method`
  - `fhops_predictor`
  - `fhops_response`
- Preserve units and confidence.
- Sidecars should include source document and extraction/review provenance so
  FHOPS reference-data loaders can audit recovered values.
- Do not import FHOPS or require FHOPS runtime dependencies.

## Implementation Boundaries

P7.2 should add the generic modelling export package:

- `figrecover.integrations.generic`
- long-table DataFrame builder;
- CSV writer;
- JSON sidecar writer;
- review-gated export behavior.

P7.3 should add:

- `figrecover.integrations.femic`
- FEMIC projection over the generic export table;
- synthetic tests only.

P7.4 should add:

- `figrecover.integrations.fhops`
- FHOPS projection over the generic export table;
- synthetic tests only.

P7.5 should document:

- the generic modelling export contract;
- the explicit review gate;
- FEMIC and FHOPS adapter field mappings;
- private-data hygiene for export artifacts.
