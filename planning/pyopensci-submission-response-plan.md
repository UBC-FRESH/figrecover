# pyOpenSci Submission And Review-Response Plan

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Related issue: #64

Current package release: `0.1.0a1`

Target reviewed release: `v1.0.0`

## Status

This is a readiness and operating plan, not a submission record. `figrecover`
should not be submitted to pyOpenSci until the v1.0.0 release candidate,
archive/DOI path, documentation, examples, tests, and public-evidence strategy
are ready for external review.

## Source References

- pyOpenSci author guide:
  `https://www.pyopensci.org/software-peer-review/how-to/author-guide.html`
- pyOpenSci review timeline:
  `https://www.pyopensci.org/software-peer-review/our-process/review-timeline.html`
- pyOpenSci software-submission repository:
  `https://github.com/pyOpenSci/software-submission`
- pyOpenSci reviewer guide:
  `https://www.pyopensci.org/software-peer-review/how-to/reviewer-guide.html`
- pyOpenSci/JOSS partnership:
  `https://www.pyopensci.org/software-peer-review/partners/joss.html`

## Submission Gate

Before opening a pyOpenSci review issue, confirm:

- `planning/pyopensci-readiness-checklist.md` has no unresolved blockers.
- `planning/v1-readiness-gap-analysis.md` has all required gaps closed or
  explicitly deferred.
- `planning/v1-release-archive-plan.md` has been executed through at least a
  release-candidate check.
- The submitted package version is installable from PyPI or another public
  community package repository.
- The reviewed version has an archive/DOI record if required by the submission
  materials.
- README, Sphinx docs, examples, API reference, CLI reference, citation docs,
  and support docs match the submitted version.
- Public examples and case-study artifacts are synthetic or explicitly
  publication-safe.
- The TFL 6 case-study publication gate has been resolved before using any TFL
  6 content as review evidence.
- Maintainers have committed review-response time for the expected review
  window.

## Submission Metadata Checklist

Prepare the submission issue with:

- package name: `figrecover`;
- package repository: `https://github.com/UBC-FRESH/figrecover`;
- documentation URL: `https://ubc-fresh.github.io/figrecover/`;
- package manager URL: `https://pypi.org/project/figrecover/`;
- submitted version;
- archive/DOI for the submitted version;
- license: MIT;
- submitting author;
- maintainers;
- one-line package description;
- longer statement of need;
- scope-fit summary;
- related packages and overlap statement;
- test command summary;
- installation instructions;
- link to contribution/support guidance;
- link to code of conduct;
- optional JOSS interest flag if the project is ready to pursue the
  pyOpenSci/JOSS path.

## Internal Tracking Workflow

Once a pyOpenSci submission issue exists:

1. Add the review issue link to `ROADMAP.md`,
   `planning/pyopensci-readiness-checklist.md`, and issue #64.
2. Create a local tracking issue for each editor or reviewer action item.
3. Link each local issue back to the pyOpenSci review issue.
4. Address each action item through a pull request.
5. Include tests, docs, or release-note updates in the same PR when relevant.
6. Post concise review-thread responses linking to completed PRs and issues.
7. Keep the pyOpenSci thread as the central public review record.

Do not make ad hoc local changes without linked issues when they are triggered
by formal review feedback.

## Reviewer Feedback Labels

Use labels that make review work easy to query:

- `pyopensci-review`
- `docs`
- `tests`
- `api`
- `packaging`
- `examples`
- `question`
- `blocked`

If these labels do not exist when review starts, create them before triaging
feedback.

## Response Standards

Each review-response PR should include:

- linked pyOpenSci comment or local review issue;
- summary of the requested change;
- implementation notes;
- tests or explanation for no test change;
- docs updates or explanation for no docs change;
- private-data hygiene confirmation;
- verification commands and results.

Responses in the pyOpenSci review issue should be short and link to the
repository evidence rather than duplicating full diffs.

## Verification Expectations

Default review-response PR checks:

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
```

For packaging, release, metadata, citation, or archive changes, also run:

```bash
python -m build
twine check dist/*
```

For case-study or example changes, verify that no private PDFs, private crops,
prompt logs, recovered private tables, or unapproved TFL 6 derivatives are
tracked.

## Acceptance And Badge Handling

After pyOpenSci acceptance:

- record the acceptance link in `ROADMAP.md`, `CHANGE_LOG.md`, README, and
  planning notes;
- add the pyOpenSci badge only after acceptance;
- add any accepted-package metadata requested by pyOpenSci;
- decide whether the JOSS companion-paper submission should proceed immediately
  through the pyOpenSci/JOSS path;
- keep the JOSS paper and package docs synchronized without turning the paper
  into a user guide.

## Closeout Requirements For P9.4

Issue #64 should remain open until the pyOpenSci submission is actually opened,
review feedback is tracked and addressed, and acceptance or another explicit
outcome is recorded. This planning tranche completes only the submission and
review-response workflow definition.
