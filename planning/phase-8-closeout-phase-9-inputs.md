# Phase 8 Closeout And Phase 9 Inputs

Date: 2026-06-28

## Phase

Phase 8: Documentation, Examples, And Public Alpha

Parent issue: #53

Pull request: #59

GitHub prerelease: `v0.1.0a1`

TestPyPI release: `figrecover==0.1.0a1`

PyPI release: `figrecover==0.1.0a1`

## Completed Scope

Phase 8 made `figrecover` usable as a public alpha package.

Completed work:

- expanded public-alpha Sphinx docs;
- added manual calibrated extraction and limitations guides;
- added publication-safe synthetic examples;
- added example smoke tests;
- added GitHub Actions CI for Python 3.11 and 3.12;
- added maintainer-gated release workflow;
- refreshed README and release notes;
- published GitHub prerelease `v0.1.0a1`;
- published `figrecover==0.1.0a1` to TestPyPI and PyPI.

## Verification

Local checks passed:

- `python -m ruff check .`
- `python -m pytest` (`66 passed`)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- clean install from the built wheel;
- `figrecover --help` from the built-wheel environment.

Remote checks passed:

- PR #59 CI passed on Python 3.11 and 3.12;
- release workflow run `28306201578` published to TestPyPI;
- release workflow run `28306235391` published to PyPI;
- clean install from real PyPI with
  `python -m pip install --pre figrecover==0.1.0a1`;
- installed PyPI version reported `0.1.0a1`.

## Private-Data Hygiene

The alpha release contains synthetic examples only. No private PDFs, generated
private crops, prompt logs, review bundles, corpus outputs, or recovered private
tables are tracked.

## Remaining Risks

- `figrecover` is alpha research software.
- Recovered data are approximate and require review.
- VLM outputs remain proposals unless explicitly used otherwise.
- Complex chart classes and arbitrary PDF-to-table automation remain outside
  the reliable alpha scope.

## Phase 9 Inputs

Phase 9 should prepare the project for scholarly publication and peer review
once the package matures toward v1.0.0.

Recommended Phase 9 work:

- create Phase 9 GitHub parent and child issues;
- audit pyOpenSci package-readiness requirements;
- audit JOSS paper requirements;
- add citation metadata when appropriate;
- plan a v1.0.0 readiness checklist distinct from alpha release checks;
- keep pyOpenSci review first and JOSS companion paper second.
