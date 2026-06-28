Citation, Support, And Maintenance
==================================

Citation
--------

The repository includes ``CITATION.cff`` for software citation metadata. Until
a reviewed paper and DOI exist, cite the software release used in your work and
include the version number.

For the public alpha:

.. code-block:: text

   UBC FRESH Lab. figrecover: Auditable recovery of approximate source tables
   from published figures. Version 0.1.0a1. 2026.
   https://github.com/UBC-FRESH/figrecover

Future pyOpenSci, archive, and JOSS citation details should replace this
temporary alpha citation once available.

Publication Closeout
--------------------

Phase 9 tracks the final publication closeout workflow in
``planning/publication-closeout-checklist.md``. That checklist defines how
archive DOI, pyOpenSci review links, JOSS paper links, badges, README citation
text, Sphinx citation guidance, and ``CITATION.cff`` should be synchronized
once those records exist.

Badges and DOI citations should be added only after the relevant acceptance or
archive event has actually happened.

Support
-------

Use the GitHub issue tracker for public bug reports, documentation issues,
feature requests, and reproducible public examples. Do not attach private PDFs,
private recovered tables, prompt logs, review bundles, or unpublished document
outputs to public issues.

When reporting extraction issues, include:

* package version;
* operating system and Python version;
* command or Python API call;
* chart type and extraction mode;
* public-safe crop or synthetic reproduction where possible;
* diagnostics emitted by ``figrecover``.

Maintenance Commitment
----------------------

UBC-FRESH intends to maintain ``figrecover`` through the package review and
publication path. Accepted scholarly review will require a clear post-review
maintenance commitment, issue response process, and release/archive trail.

The current alpha is maintained as experimental research software. API changes
may occur before v1.0.0, but changes should be reflected in the roadmap,
changelog, docs, and tests.

Private-Data Hygiene
--------------------

Do not share private technical documents or recovered private data in public
support channels. If a bug depends on private material, create a synthetic or
public-safe reproducer first.
