# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Project Purpose

`figrecover` exists to recover approximate tabular data from figures in
scientific, engineering, forestry, and professional technical documents when
the original source data tables were not published.

The package should use deterministic image-processing and calibration
algorithms for numeric extraction whenever those algorithms can work. Local
open VLMs may assist with chart triage, axis labels, legends, series colours,
calibration proposals, and QA, but VLM guesses must not silently become the
default numeric source of truth.

## Current Repo State

This repository is an early bootstrap. It contains:

- `README.md`: concise public overview and current status.
- `ROADMAP.md`: phase/task roadmap and issue tracker map.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: focused design notes and research records.
- `pyproject.toml`: package metadata and optional dependency groups.
- `src/figrecover/`: importable package code.
- `tests/`: package-backed synthetic tests.
- `docs/`: Sphinx documentation skeleton.
- `tmp/`: ignored local working area for private PDFs, crops, model outputs,
  generated artifacts, and experiments.

Do not claim that `figrecover` provides fully automatic, precise recovery from
arbitrary PDFs. The current durable implementation is calibrated extraction
from prepared image crops.

## Private Documents And Generated Outputs

Technical PDFs, rendered pages, cropped figures, VLM outputs, review bundles,
and recovered data from private or unpublished sources are local working
material unless the maintainer explicitly asks to track a sanitized artifact.

Rules:

- Keep private source PDFs and generated outputs under ignored paths such as
  `tmp/`, `local/`, `data/private/`, or `outputs/`.
- Do not commit raw private PDFs, rendered pages, cropped figures, recovered
  private tables, prompt transcripts, model responses, or large generated
  review bundles.
- Tracked examples and tests must use synthetic or public-safe fixtures.
- Record provenance for every interpreted document, page, crop, figure, axis,
  calibration, extraction method, and model/tool version.

## Working Principles

- Keep CLI commands thin wrappers over Python APIs.
- Keep dependency-heavy PDF, parser, CV, and VLM integrations behind optional
  extras.
- Prefer structured records and parsers over ad hoc string or pixel handling.
- Emit explicit diagnostics for unsupported chart types, uncertain calibration,
  low-confidence extraction, missing pixels, and VLM disagreement.
- Preserve uncertainty. Recovered values are approximate unless validated by a
  separate source.
- Keep public repo content clean of private forestry or client material.

## Planning Workflow

This repo follows the UBC-FRESH phase/task/subtask workflow:

- `ROADMAP.md` is the current plan and issue tracker map.
- One roadmap phase maps to one GitHub parent issue and one feature branch.
- One roadmap task maps to one child issue linked from the parent issue body.
- Subtasks usually stay as checklist items inside the child issue body.
- Use at most three issue levels: phase, task, implementation subtask.
- Record issue numbers beside roadmap phases and tasks once created.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue bodies, and PR
  descriptions synchronized.
- Open a PR from the phase branch to `main` only after phase tasks, tests, docs,
  and closeout notes are complete or explicitly deferred.

## Verification

Default local checks:

```bash
python -m pytest
python -m ruff check .
sphinx-build -b html docs _build/html -W
```

Default CI must not require GPU access, private PDFs, local VLM servers, or
network downloads beyond package installation.
