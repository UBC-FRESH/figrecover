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

## GitHub Issue And Comment Formatting

Formatting matters. GitHub issue bodies and comments must be readable as
rendered Markdown, not flattened prose.

Rules:

- Use short section labels on their own lines, such as `Roadmap task: P3.1`,
  `Parent phase issue: #18`, `Status: active`, and `Checklist:`.
- Use real GitHub task-list syntax, with one checklist item per line:

  ```markdown
  Checklist:
  - [ ] Do the first thing.
  - [ ] Do the second thing.
  ```

- Never write inline pseudo-checklists such as
  `Checklist: [ ] first. [ ] second.`
- Wrap branch names, file paths, commands, and commit hashes in backticks.
- For parent phase issues, list child issues as task-list bullets with issue
  numbers and task IDs.
- For completion comments, prefer concise structured Markdown:

  ```markdown
  Completed in commit `abc1234`.

  Verification:
  - `python -m pytest`
  - `python -m ruff check .`
  ```

- Before creating or editing several issues, prepare bodies as multi-line
  Markdown strings or temporary body files. Do not pass long single-line bodies
  to `gh issue create`, `gh issue edit`, or `gh issue comment`.

## GitHub Issue Body Quality Standard

Issue bodies are part of the project specification and onboarding material.
Write them so a new lab student, external collaborator, or coding agent can
understand the task, implement it, verify it, and close it without reading the
original chat transcript.

Parent phase issues must include:

- Phase identifier, status, branch name, and roadmap/planning links.
- A short goal statement describing the capability the phase adds.
- Scope and out-of-scope sections that set implementation boundaries.
- Architecture or workflow notes that explain how the phase fits the package.
- A child issue checklist with task IDs and issue numbers.
- Phase-level acceptance criteria.
- Verification and closeout requirements, including docs, tests, roadmap,
  changelog, issue updates, PR, and private-data hygiene.
- Completion metadata once closed, including commits and merged PRs when
  applicable.

Child task issues must include:

- Task identifier, parent phase issue, status, and related planning links.
- Goal and rationale: what user-facing or developer-facing capability this
  task provides and why it matters.
- Scope: concrete behaviours, APIs, files, CLI commands, records, docs, or
  tests expected from the task.
- Out of scope: adjacent work that should not be pulled into the task.
- Implementation notes: expected modules, public API names, dependency policy,
  compatibility constraints, provenance rules, and repo patterns to follow.
- Subtasks as real GitHub task-list items. Each item should be specific enough
  to review and check off independently.
- Acceptance criteria written as observable outcomes, not vague intentions.
- Verification commands and any local/manual checks expected before closing.
- Artifacts and documentation updates expected from the task.
- Risks, edge cases, and deferred follow-up work where relevant.
- Completion metadata once closed, including commit hashes, merged PRs, and
  intentionally deferred items.

Do not create placeholder issue bodies with only a title and a short checklist
unless the maintainer explicitly asks for a placeholder. If a placeholder is
unavoidable, label it clearly as a placeholder and replace it with a complete
body before implementation begins.

## Verification

Default local checks:

```bash
python -m pytest
python -m ruff check .
sphinx-build -b html docs _build/html -W
```

Default CI must not require GPU access, private PDFs, local VLM servers, or
network downloads beyond package installation.
