# Phase 7 Closeout And Phase 8 Inputs

Date: 2026-06-27

## Phase

Phase 7: FEMIC/FHOPS Integration Adapters

Branch: `feature/p7-femic-fhops-integrations`

Parent issue: #46

Child issues:

- #47: P7.1 Inspect FEMIC/FHOPS ingestion conventions
- #48: P7.2 Add generic modelling export
- #49: P7.3 Add FEMIC adapter
- #50: P7.4 Add FHOPS adapter
- #51: P7.5 Add integration docs and examples

## Completed Scope

Phase 7 added a lightweight integration layer for downstream modelling systems.
The durable handoff contract is a generic long-table export plus JSON sidecar.
FEMIC and FHOPS support is implemented as thin projections over that generic
table rather than as hard dependencies.

Completed work:

- added a public-safe FEMIC/FHOPS integration survey note;
- added `figrecover.integrations.generic`;
- added review-gated modelling DataFrame and CSV/JSON sidecar export helpers;
- added `figrecover.integrations.femic`;
- added `figrecover.integrations.fhops`;
- added synthetic integration tests;
- added Sphinx guide and API reference entries for integration exports.

## Public API Added

- `figrecover.integrations.generic.GenericModellingExport`
- `figrecover.integrations.generic.build_modelling_dataframe`
- `figrecover.integrations.generic.write_modelling_export`
- `figrecover.integrations.femic.project_femic_export`
- `figrecover.integrations.femic.write_femic_export`
- `figrecover.integrations.fhops.project_fhops_export`
- `figrecover.integrations.fhops.write_fhops_export`

## Private-Data Hygiene

The integration survey inspected local FEMIC and FHOPS code/docs/tests/config
surfaces only. No private PDFs, private recovered tables, generated private
outputs, or unpublished extracted values were copied into tracked files.

Integration exports may contain sensitive source paths and recovered values.
Users should keep generated CSVs and JSON sidecars under ignored output
directories such as `tmp/` until explicitly sanitized for release.

## Verification

The following checks passed:

- `python -m ruff check .`
- `python -m pytest` (`63 passed`)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`

## Phase 8 Inputs

Phase 8 should turn the current working package into a public alpha that
external power users can install, test, and understand.

Recommended Phase 8 work:

- expand Sphinx docs into a complete quickstart, user guide, CLI reference, API
  reference, QA workflow, corpus workflow, VLM-assisted workflow, and
  limitations statement;
- add public-safe examples using synthetic charts and generated PDFs;
- add CI checks for pytest, ruff, docs, and packaging;
- add optional local-only markers for GPU/VLM tests;
- add release build and TestPyPI rehearsal workflow;
- prepare `0.1.0a1` alpha release notes with clear unsupported chart classes
  and no claims of fully automatic precise recovery.
