# v1.0.0 Readiness Gap Analysis

Date: 2026-06-28

Current release: `0.1.0a1`

Target: v1.0.0 review-ready release for pyOpenSci and downstream JOSS
publication path.

## Summary

`figrecover` has a strong public-alpha foundation: installable package,
documented workflows, synthetic examples, CI, release workflow, PyPI release,
GitHub Pages docs, deterministic extraction core, QA/review tools, corpus
scaffolding, local VLM proposal boundary, and modelling export adapters.

It is not yet v1.0.0 review-ready. The main gaps are API stability policy,
broader evaluation evidence, citation/release archival metadata, community
readiness, and a mature public statement of need.

This conclusion matches pyOpenSci author guidance that packages should be
mature enough for complete review and have stable or close-to-stable APIs
before submission.

## Current Strengths

- Public GitHub repository under `UBC-FRESH/figrecover`.
- MIT license.
- PyPI alpha release: `figrecover==0.1.0a1`.
- GitHub Pages documentation.
- Synthetic examples and tests.
- CI for Python 3.11 and 3.12.
- Trusted-publishing release workflow.
- Deterministic calibrated extraction for selected chart classes.
- PDF rendering and figure candidate manifests.
- QA overlays, metrics, and review manifests.
- Corpus artifact layout and run manifests.
- Optional VLM proposal layer.
- Generic, FEMIC, and FHOPS modelling exports.

## API Stability And Deprecation

Current gap:

- Public API exists but is still alpha.
- No explicit API stability/deprecation policy is documented.
- Records and CLI commands may still change while extraction coverage matures.

v1.0.0 expectation:

- Define stable public modules and records.
- Identify experimental modules or APIs.
- Document deprecation policy.
- Add tests that protect stable records, serialization, and CLI contracts.

## Extraction Coverage And Failure Reporting

Current gap:

- Supported chart classes are intentionally narrow.
- Complex charts remain unsupported or experimental.
- Public evidence is mostly synthetic.

v1.0.0 expectation:

- Maintain honest limitations.
- Strengthen diagnostics for unsupported and low-confidence cases.
- Add public-safe evaluation cases beyond trivial synthetic examples if
  feasible.
- Use the TFL 6 Management Plan PDF as the preferred realistic deployment case
  study if provenance and reuse rights allow publication of derived artifacts.
- Avoid claiming arbitrary PDF-to-table automation.

## Documentation Completeness

Current status:

- Public alpha docs cover quickstart, manual extraction, corpus workflow, VLM,
  QA/review, integrations, examples, development checks, release process,
  limitations, API reference, and CLI reference.

v1.0.0 gaps:

- Expand the new statement of need if reviewers request more context.
- Replace alpha citation instructions with archive/JOSS DOI instructions.
- Refine support and maintenance expectations for accepted-review status.
- Finalize API stability/deprecation policy.
- Add public benchmark/evaluation notes if available.

## Public Examples And Benchmarks

Current status:

- Examples are synthetic and safe.

v1.0.0 gaps:

- Decide whether synthetic examples are sufficient for review.
- Identify public-domain or permissively reusable technical figures if stronger
  evaluation evidence is needed.
- Complete the TFL 6 case-study publication gate and decide which outputs can
  become tracked docs/JOSS artifacts.
- Keep private FEMIC/FHOPS documents out of public examples.

## Citation Metadata

Current gap:

- `CITATION.cff` exists for the alpha release.
- No archive DOI yet.
- No paper DOI yet.

v1.0.0 expectation:

- Add `CITATION.cff`.
- Create archive/DOI for reviewed release.
- Add citation docs and README citation section.
- Add JOSS DOI only after acceptance.

## Release, Archive, And DOI Process

Current status:

- Alpha release process works through GitHub Actions, TestPyPI, and PyPI.
- GitHub prerelease artifacts exist.
- `planning/v1-release-archive-plan.md` defines the intended v1.0.0 release
  candidate, final release, and archive/DOI path.

v1.0.0 gaps:

- Execute the release candidate process after readiness gates are satisfied.
- Confirm archive/DOI integration.
- Verify final v1.0.0 install from PyPI and archive.
- Record release and archive links in roadmap/changelog/docs.

## Community And Maintenance

Current status:

- `CONTRIBUTING.md`, issue templates, roadmap, changelog, and AGENTS workflow
  exist.
- `CODE_OF_CONDUCT.md` exists.
- Citation/support docs exist for alpha users.

v1.0.0 gaps:

- Confirm maintainer commitment and response expectations.
- Add or confirm code of conduct if expected.
- Add support channels and review-response plan.
- Ensure issue templates support user bug reports and feature requests well
  enough for public alpha users.

## Known Limitations To Keep Explicit

- Recovered values are approximate.
- Human review is required before downstream use.
- VLM outputs are proposals, not authoritative numeric data by default.
- Fully automatic arbitrary PDF-to-table recovery is not supported.
- Low-quality scanned documents, complex chart classes, and unsupported
  diagrams remain outside reliable scope.

## Recommended Next Work

- [x] Complete initial pyOpenSci/JOSS scope and readiness scan for P9.1.
- [ ] Add citation metadata plan.
- [ ] Add statement-of-need documentation.
- [ ] Decide public benchmark/evaluation evidence strategy.
- [ ] Build the TFL 6 case-study workflow under ignored `tmp/tfl6_case_study/`
  before selecting publication artifacts.
- [ ] Define API stability/deprecation policy.
- [x] Define v1.0.0 release-candidate and archive plan.
- [ ] Track each v1.0.0 gap as linked GitHub issues before submission.
