# pyOpenSci Readiness Checklist

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Current package release: `0.1.0a1`

Target reviewed release: v1.0.0 or later readiness candidate

## Review Path

`figrecover` should pursue pyOpenSci software peer review before the JOSS
companion paper path. The pyOpenSci review should establish package quality,
usability, maintainability, documentation, and scientific workflow fit. JOSS
should follow through the pyOpenSci/JOSS pathway after pyOpenSci acceptance or
when the package clearly satisfies that path.

Official source references:

- pyOpenSci author guide:
  `https://www.pyopensci.org/software-peer-review/how-to/author-guide.html`
- pyOpenSci package scope:
  `https://www.pyopensci.org/software-peer-review/about/package-scope.html`
- pyOpenSci review policies:
  `https://www.pyopensci.org/software-peer-review/our-process/policies.html`
- pyOpenSci/JOSS partnership:
  `https://www.pyopensci.org/software-peer-review/partners/joss.html`

## Scope Fit

Current fit hypothesis:

- `figrecover` is scientific workflow/data-processing software.
- It supports technical-document data recovery for scientific and professional
  modelling workflows.
- It is not a one-off project script; it exposes reusable Python APIs, CLI
  commands, records, docs, examples, tests, CI, and release artifacts.
- It has a clear research application: recovering approximate tabular evidence
  from figures where source data were not released, while preserving
  provenance and review workflows.

Risks to resolve before submission:

- Current release is alpha and should not be represented as v1.0.0 review
  ready.
- Some extraction capabilities remain narrow and should be documented as
  limitations rather than oversold.
- Public benchmark examples are currently synthetic; v1.0.0 readiness should
  decide whether additional public-domain technical documents are needed.
- pyOpenSci guidance says a package should be mature enough for reviewers to
  evaluate it in its entirety and have APIs that are stable or close to
  stability before review.
- pyOpenSci policy expects accepted packages to remain maintained after review;
  the review-policy page describes a maintenance commitment of at least two
  years.

## Package Basics

- [x] Public repository exists: `UBC-FRESH/figrecover`.
- [x] Package is published to PyPI: `figrecover==0.1.0a1`.
- [x] License is MIT.
- [x] Python requirement is recorded in package metadata.
- [x] Default install avoids GPU/model dependencies.
- [x] Optional extras isolate PDF, parser, VLM, docs, dev, release, and test
  dependencies.
- [x] Sphinx docs are live on GitHub Pages.
- [x] CI runs on public GitHub-hosted runners.
- [x] Release workflow supports TestPyPI and PyPI trusted publishing.
- [ ] v1.0.0 release candidate is available.
- [ ] v1.0.0 release is archived with DOI.

## Documentation Requirements

Existing docs cover:

- [x] Quickstart.
- [x] Manual calibrated extraction.
- [x] PDF corpus workflow.
- [x] VLM-assisted workflow.
- [x] QA/review workflow.
- [x] Integration exports.
- [x] Examples.
- [x] Development checks.
- [x] Release process.
- [x] Limitations.
- [x] API reference.
- [x] CLI reference.

Pre-submission doc gaps:

- [ ] Add a statement-of-need section suitable for package review.
- [ ] Add citation instructions.
- [ ] Add maintenance/support expectations.
- [ ] Add explicit v1.0.0 API stability/deprecation policy.
- [ ] Add TFL 6 case-study documentation if source provenance and reuse rights
  are confirmed.
- [ ] Add any public benchmark or evaluation notes approved for release.

## README And Community Files

Current status:

- [x] README describes purpose, install, examples, roadmap, and private-data
  hygiene.
- [x] `CONTRIBUTING.md` exists.
- [x] `AGENTS.md` exists for coding-agent workflow.
- [x] `CHANGE_LOG.md` exists.
- [x] `ROADMAP.md` exists.
- [x] `LICENSE` exists.

Pre-submission gaps:

- [ ] Add `CITATION.cff`.
- [ ] Confirm whether a `CODE_OF_CONDUCT.md` is required by UBC-FRESH or
  pyOpenSci expectations.
- [ ] Add or refine support channels and issue templates if needed.
- [ ] Add badges only when they are truthful and maintained.

## Testing And CI

Current checks:

- [x] `python -m ruff check .`
- [x] `python -m pytest`
- [x] `sphinx-build -b html docs _build/html -W`
- [x] `python -m build`
- [x] `twine check dist/*`
- [x] CI matrix on Python 3.11 and 3.12.
- [x] Default CI does not require private data, GPU, VLM server, or large
  corpora.

Pre-submission gaps:

- [ ] Define v1.0.0 expected coverage and test-risk boundaries.
- [ ] Add public benchmark/evaluation tests only if public-safe and stable.
- [ ] Decide whether TFL 6 case-study outputs are docs-only, test fixtures, or
  ignored local evaluation artifacts.
- [ ] Confirm clean install from v1.0.0 wheel and source distribution.

## Submission Metadata To Prepare

- [x] Package name: `figrecover`.
- [x] One-line description: Recover approximate tabular data from scientific
  and professional figures.
- [x] Repository URL: `https://github.com/UBC-FRESH/figrecover`.
- [x] Documentation URL: `https://ubc-fresh.github.io/figrecover/`.
- [x] PyPI URL: `https://pypi.org/project/figrecover/`.
- [ ] Version submitted.
- [ ] Archive/DOI for submitted version.
- [ ] Submitting author.
- [ ] Maintainers.
- [ ] Maintainer availability and response plan.
- [x] License: MIT.
- [ ] Scope statement.
- [ ] Statement of need.
- [ ] Related packages/tools.
- [ ] Development status and limitations.

## Review Response Plan

- [ ] Convert reviewer/editor feedback into linked GitHub issues.
- [ ] Address feedback through PRs with tests/docs when appropriate.
- [ ] Keep `ROADMAP.md`, `CHANGE_LOG.md`, docs, and release notes synchronized.
- [ ] Record pyOpenSci review link in planning docs and issue closeout.
- [ ] Add pyOpenSci badge only after acceptance.

## Private-Data Hygiene

Submission materials must not include private PDFs, generated private crops,
prompt logs, review bundles, recovered private tables, or unpublished forestry
data. Evidence examples should be synthetic or explicitly public-safe.
