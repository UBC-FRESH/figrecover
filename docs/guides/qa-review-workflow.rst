QA And Review Workflow
======================

Recovered figure data should be reviewed before it becomes model input.
``figrecover`` therefore treats extraction output as an auditable work product:
each recovered table can be paired with a visual overlay, quality metrics, and a
review decision.

The Phase 5 workflow is:

#. Digitize a cropped figure to a JSON result.
#. Generate a review bundle containing overlays, metrics, tables, and a review
   manifest.
#. Inspect the overlay and metrics.
#. Mark each entry as accepted, rejected, manually corrected, needs recrop, or
   needs recalibration.
#. Export accepted tables only for downstream modelling.

Review Artifacts
----------------

The review bundle command writes three artifact classes:

* ``overlays/`` contains PNG images with recovered points, lines, bars, and the
  calibrated plot frame drawn over the source crop.
* ``metrics/`` contains JSON quality summaries with point counts, extraction
  density, confidence summaries, diagnostics, plot-bound availability, and
  review priority.
* ``tables/`` contains long CSV exports with source provenance columns.

The review manifest is newline-delimited JSON. Each entry records source paths,
review status, reviewer information, diagnostics, optional correction metadata,
and enough provenance to decide whether an extracted table can be used later.

CLI Example
-----------

Generate a review bundle from one or more digitization JSON files:

.. code-block:: bash

   figrecover review bundle tmp/results/fig-001.json \
      --out-dir tmp/review

Summarize review status and low-confidence items:

.. code-block:: bash

   figrecover review summarize tmp/review/review.jsonl --json

After review decisions have been recorded in the manifest, export accepted
tables only:

.. code-block:: bash

   figrecover review export-accepted tmp/review/review.jsonl \
      --out-dir tmp/accepted-tables

Python Example
--------------

The CLI is a thin wrapper over the Python API:

.. code-block:: python

   from pathlib import Path

   from figrecover.io import read_result_json, write_points_csv
   from figrecover.qa import compute_quality_metrics, render_overlay
   from figrecover.review import ReviewEntry, ReviewManifest

   result = read_result_json(Path("tmp/results/fig-001.json"))
   overlay = render_overlay(result, Path("tmp/review/overlays/fig-001.png"))
   metrics = compute_quality_metrics(result)
   table_path = write_points_csv(
       result,
       Path("tmp/review/tables/fig-001.csv"),
       include_provenance=True,
   )

   entry = ReviewEntry(
       review_id="fig-001",
       figure_id=result.spec.source_figure_id,
       image_path=result.image_path,
       overlay_path=overlay.path,
       table_path=table_path,
       status="needs_review",
       metrics=metrics,
   )
   ReviewManifest.from_entries([entry]).write_jsonl(
       Path("tmp/review/review.jsonl")
   )

Review Statuses
---------------

Use ``accepted`` only when the overlay and metrics support downstream use. Use
``manually_corrected`` when a corrected table is available and its provenance is
recorded. Use ``rejected``, ``needs_recrop``, or ``needs_recalibration`` when the
artifact should not be exported into modelling inputs.

Quality metrics are triage aids, not guarantees. Low point count, missing plot
bounds, warnings, errors, low confidence, or VLM disagreement should trigger
manual inspection. Even high-confidence results should be checked visually when
they will affect scientific or operational decisions.

Private-Data Hygiene
--------------------

Review bundles can contain private document content and recovered private data.
Keep them under ignored output directories such as ``tmp/`` unless they have
been explicitly sanitized for public examples, tests, or papers.
