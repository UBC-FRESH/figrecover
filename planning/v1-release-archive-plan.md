# v1.0.0 Release Candidate And Archive Plan

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Related issue: #63

Current package release: `0.1.0a1`

Target reviewed release: `v1.0.0`

## Status

This is a readiness plan, not a release record. No `v1.0.0` release candidate
is being cut during this tranche. The purpose of this document is to define the
release, verification, and archive path needed before `figrecover` can be
submitted for pyOpenSci package review and later used as the reviewed software
version for the JOSS companion-paper path.

## Pre-Release-Candidate Gates

A `v1.0.0rc1` tag should not be created until these gates are satisfied or
explicitly deferred in public planning notes:

- All v1.0.0 readiness gaps are closed or linked to accepted deferrals.
- Stable public APIs are identified in the docs.
- Experimental APIs are labelled as such.
- Deprecation and compatibility expectations are documented.
- Deterministic extraction limitations are explicit and current.
- Public examples are synthetic or approved as public-safe.
- The TFL 6 case-study publication gate is resolved before any TFL 6 artifacts
  are included in docs, tests, release archives, or paper figures.
- `CITATION.cff` is updated for the intended reviewed version.
- README, Sphinx docs, API reference, CLI reference, and examples match the
  release candidate.
- Maintainer response and support expectations are documented.
- Release workflow dry runs pass.

## Local Verification Commands

Run these checks before creating a release-candidate tag:

```bash
rm -rf dist build _build/html
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

Then verify the built wheel in a fresh environment:

```bash
python -m venv tmp/release-check-venv
. tmp/release-check-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/figrecover-*.whl
figrecover --help
python -c "from importlib.metadata import version; print(version('figrecover'))"
deactivate
```

## Release-Candidate Sequence

The first v1 release candidate should use `1.0.0rc1` in package metadata and a
matching `v1.0.0rc1` Git tag.

1. Update `pyproject.toml` and package version metadata to `1.0.0rc1`.
2. Update release notes, roadmap, changelog, citation metadata, and docs.
3. Run local verification.
4. Open a release-candidate PR and wait for CI.
5. Merge only after maintainer approval.
6. Create and push the signed or annotated `v1.0.0rc1` tag.
7. Run the release workflow in dry-run mode.
8. Publish to TestPyPI.
9. Verify install from TestPyPI in a fresh environment.
10. Publish a GitHub prerelease for `v1.0.0rc1`.
11. Record release-candidate links in the roadmap and changelog.

Additional release candidates should increment the suffix: `1.0.0rc2`,
`1.0.0rc3`, and so on.

## Final v1.0.0 Sequence

The final `v1.0.0` release should be cut only after release-candidate
validation, maintainer approval, and pyOpenSci readiness review inside the
project.

1. Update package metadata from `1.0.0rcN` to `1.0.0`.
2. Confirm no private PDFs, crops, overlays, prompt logs, recovered private
   tables, or unapproved TFL 6 derivatives are tracked.
3. Refresh release notes with supported chart classes, limitations, and known
   unsupported cases.
4. Run local verification.
5. Open and merge a final release PR after CI and maintainer approval.
6. Create and push the `v1.0.0` tag.
7. Run the release workflow in dry-run mode.
8. Publish to TestPyPI if a final rehearsal is needed.
9. Publish to PyPI through trusted publishing.
10. Verify clean install from PyPI in a fresh environment.
11. Create the GitHub release.
12. Confirm the archive/DOI record.
13. Record all release, package, and archive links in the roadmap, changelog,
    docs, and pyOpenSci submission materials.

## Archive And DOI Plan

The preferred archive path is a GitHub-release-linked scholarly archive such as
Zenodo, provided the `UBC-FRESH/figrecover` repository has the integration
enabled before final release. This plan does not claim that the archive
integration is configured yet.

Archive metadata should include:

- package name and version;
- authors and maintainers;
- MIT license;
- repository URL;
- documentation URL;
- PyPI URL;
- release notes;
- citation metadata;
- keywords for chart digitization, data recovery, PDFs, scientific computing,
  and vision-language-model assistance;
- explicit statement that recovered values are approximate and require review.

The archive DOI should be added to:

- `CITATION.cff`;
- README citation section;
- Sphinx citation/support guide;
- release notes;
- pyOpenSci submission metadata;
- later JOSS paper metadata after acceptance.

## Private-Data Hygiene

Release archives must not include private PDFs, generated private crops,
overlays, prompt logs, review bundles, or recovered private tables. The local
TFL 6 Management Plan PDF can be used as a development target only under the
case-study publication gate. No TFL 6 raw PDF or derived artifacts should be
tracked, archived, or shown in the JOSS paper until provenance and reuse rights
are reviewed and recorded.

## Closeout Requirements For P9.3

Issue #63 should remain open until the actual v1.0.0 release candidate, final
release, PyPI verification, GitHub release, and archive/DOI work are complete.
This planning tranche completes only the release-checklist subtask.
