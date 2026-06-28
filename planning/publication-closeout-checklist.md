# Publication Closeout Checklist

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Related issue: #66

Current package release: `0.1.0a1`

Target closeout state: pyOpenSci-reviewed package and, if accepted, JOSS
companion paper with synchronized citation and release metadata.

## Status

This is a closeout-readiness plan, not a closeout record. Phase 9 cannot close
until pyOpenSci review, JOSS paper handling if pursued, release/archive
metadata, badges, citation instructions, roadmap, changelog, issues, and PRs
are synchronized.

## Closeout Gate

Before closing Phase 9, confirm:

- pyOpenSci review outcome is recorded.
- JOSS submission or deferral decision is recorded.
- v1.0.0 release and archive/DOI links are recorded if the package reached
  stable reviewed-release status.
- JOSS DOI is recorded if the paper is accepted.
- README badges reflect only actual achieved statuses.
- `CITATION.cff` matches the final citation state.
- Sphinx citation/support docs match README and release metadata.
- `ROADMAP.md`, `CHANGE_LOG.md`, GitHub issues, and PR closeout notes agree.
- No private PDFs, generated private crops, prompt logs, recovered private
  tables, or unapproved TFL 6 derivatives are tracked.

## Citation Metadata Checklist

At final closeout, update or verify:

- `CITATION.cff` version and release date.
- archive DOI for the reviewed software release.
- JOSS paper DOI if accepted.
- software title and abstract.
- authors and maintainers.
- repository URL.
- documentation URL.
- license.
- preferred citation message.
- README citation section.
- Sphinx citation/support guide.

If JOSS acceptance has not happened, do not include a JOSS DOI or paper badge.
If pyOpenSci acceptance has not happened, do not include a pyOpenSci acceptance
badge.

## Badge And Link Checklist

Add badges only when truthful and stable:

- CI status.
- PyPI version.
- docs deployment status or docs URL if useful.
- pyOpenSci accepted badge after acceptance.
- JOSS DOI badge after JOSS acceptance.
- archive DOI badge after archive DOI is minted.

Record durable links for:

- GitHub release;
- PyPI release;
- archive/DOI record;
- pyOpenSci review issue;
- JOSS paper page if accepted;
- JOSS review issue if applicable;
- live Sphinx docs.

## Documentation Synchronization

Closeout docs should include:

- installation instructions for the reviewed release;
- limitations current at closeout;
- citation instructions;
- support/maintenance expectations;
- links to review and publication records;
- case-study provenance and reuse notes if TFL 6 artifacts are included;
- explicit warnings against using recovered values without review.

## GitHub Issue And PR Closeout

Before closing the Phase 9 parent issue:

1. Confirm child issues #61-#66 are closed or have a documented deferral.
2. Add final verification evidence to each child issue.
3. Add final closeout note to parent issue #60.
4. Update PR #67 description or closeout comment with the final artifact list.
5. Merge only after roadmap, changelog, docs, citation metadata, and checks are
   synchronized.

If Phase 9 is split into additional PRs before final publication, record those
PR links in `ROADMAP.md` and the parent issue.

## Verification Commands

Run these before final closeout:

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

Also validate `CITATION.cff` with a suitable CFF validation tool if one is
added to the project tooling before closeout.

## Private-Data Hygiene

Final publication artifacts must remain public-safe. Do not track private
technical documents, private extracted tables, prompt logs, raw VLM responses,
review bundles, or unapproved TFL 6 derivatives. If TFL 6 evidence is used,
record the public source, citation, reuse decision, and allowed derivative
artifact scope.

## Closeout Record Template

Use this structure for the eventual Phase 9 closeout note:

```markdown
# Phase 9 Closeout

Status:

Reviewed package version:

GitHub release:

PyPI release:

Archive DOI:

pyOpenSci review:

JOSS paper:

JOSS DOI:

Docs:

Verification:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Private-data hygiene:

Deferred work:
```

## Closeout Requirements For P9.6

Issue #66 should remain open until publication closeout is actually complete.
This planning tranche completes only the closeout checklist and synchronization
workflow definition.
