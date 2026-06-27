# Phase 4 Closeout And Phase 5 Inputs

Date: 2026-06-27

## Completed Scope

Phase 4 added local VLM assistance as auditable proposals:

- VLM chart triage request/result records.
- Chart metadata, legend, tick-label, series-colour, and calibration hint
  proposal records.
- Prompt, backend, raw response, parsed JSON, diagnostic, and confidence
  provenance.
- OpenAI-compatible local HTTP backend boundary with lazy optional HTTP
  dependency loading.
- Versioned chart triage and chart metadata prompt templates.
- JSON response parsing helpers for strict JSON, markdown-fenced JSON,
  surrounding prose, invalid JSON, non-object JSON, and schema validation
  failures.
- Conservative self-ensemble summaries for repeated metadata proposals.
- Local VLM assistance documentation covering optional install, workstation
  expectations, endpoint usage, proposal boundaries, self-ensemble use,
  private-data hygiene, and GPU visibility caveats.

## Deferred Or Explicitly Limited

- Direct Transformers model loading is deferred.
- Model download, serving, licensing, and benchmarking remain outside the core
  package.
- VLM outputs are proposals only and do not silently become authoritative
  recovered data.
- Self-ensemble utilities do not average numeric recovered data tables by
  default.
- GPU/model-server tests are not part of default CI.

## Phase 5 Inputs

Phase 5 should make recovered data and VLM-assisted metadata inspectable:

- Render overlays of recovered line/scatter/bar points on source crops.
- Include calibration frames and series colours in overlay outputs.
- Summarize quality metrics such as extraction density, component counts,
  calibration residuals, axis consistency, and VLM disagreement.
- Add review manifests for accepted, rejected, manually corrected,
  needs-recrop, and needs-recalibration statuses.
- Preserve correction provenance and reviewer decisions.
- Add CLI review bundle generation and low-confidence/failure summaries.

The Phase 5 QA layer should treat VLM proposals as review inputs, not ground
truth.

## Verification

- `python -m pytest`
- `python -m ruff check .`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
