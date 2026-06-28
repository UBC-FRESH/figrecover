# Contributing To Figrecover

`figrecover` is pre-release research software for recovering approximate source
tables from figures in technical documents.

The project values auditable provenance, deterministic extraction where
possible, explicit uncertainty, and clean separation between public code and
private/generated document artifacts.

## Development Environment

Use a repo-local virtual environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]'
```

Run checks from the repo root:

```bash
python -m pytest
python -m ruff check .
sphinx-build -b html docs _build/html -W
```

## Workflow

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before project-shaping
  changes.
- Keep the active roadmap phase, GitHub issues, branch, changelog, docs, and
  planning notes synchronized.
- Prefer focused package-backed changes with tests.
- Keep CLI commands thin wrappers over Python APIs.
- Keep generated outputs, private PDFs, rendered pages, crops, and model
  responses out of tracked files.
- Do not add GPU/VLM requirements to default tests or CI.

## Private Document Hygiene

Use ignored local paths for private or generated material:

```text
tmp/private-pdfs/
tmp/rendered-pages/
tmp/figure-crops/
tmp/recovered-tables/
tmp/vlm-runs/
tmp/review-bundles/
```

Tracked notes about private evaluations must be sanitized and should focus on
counts, unsupported chart categories, diagnostics, stop conditions, and
follow-up priorities.

## Documentation

Sphinx docs live under `docs/`.

Build docs locally with warnings as errors:

```bash
sphinx-build -b html docs _build/html -W
```

Before closing a phase, update relevant API docstrings and user-facing docs.

## Pull Requests

Before opening or merging a phase PR:

- run local checks;
- update `ROADMAP.md` and `CHANGE_LOG.md`;
- update relevant planning notes;
- close or update corresponding child issue checklist items;
- keep the PR scoped to the active phase branch.

Do not add fully automatic recovery claims, stable API guarantees, or precision
claims until the roadmap phase records evidence for them.

## Community Conduct

This project follows the expectations in `CODE_OF_CONDUCT.md`. Keep technical
discussion professional, preserve private-data hygiene, and treat recovered
values as approximate unless separately validated.
