Integration Exports
===================

``figrecover`` exports recovered figure data for downstream modelling through a
generic long-table contract. FEMIC and FHOPS adapters are thin projections over
that generic table.

Review Gate
-----------

When a review manifest is supplied, generic modelling exports include only
``accepted`` and ``manually_corrected`` entries by default. This keeps rejected
or unreviewed figure recoveries out of modelling inputs unless a caller
explicitly opts out.

Generic Export
--------------

Generic export rows include:

* source document, PDF, page, figure, and image identifiers;
* series, ``x``, ``y``, units, and point confidence;
* review status and review ID;
* extraction tool provenance;
* source image, table, and overlay artifact paths.

The CSV is paired with a JSON sidecar containing calibration, extraction
settings, diagnostics, result summaries, and review-manifest summaries.

.. code-block:: python

   from figrecover.integrations.generic import write_modelling_export

   export = write_modelling_export(
       results,
       "tmp/model-inputs/recovered-figures.csv",
       review_manifest=review_manifest,
       x_units="years",
       y_units="m3/ha",
   )

FEMIC Projection
----------------

The FEMIC adapter keeps the generic values and adds FEMIC-facing aliases and
optional hints:

* ``femic_source_document_id``
* ``femic_source_pdf``
* ``femic_source_page``
* ``femic_figure_id``
* ``femic_series``
* ``femic_signal_family``
* ``femic_model_input_role``
* ``femic_curve_hint``

The adapter does not import FEMIC and does not write into FEMIC data directories
unless the caller chooses that output path.

FHOPS Projection
----------------

The FHOPS adapter keeps rows suitable as reference evidence or
productivity/regression inputs. It adds:

* ``fhops_reference_id``
* ``fhops_source_label``
* ``fhops_method``
* ``fhops_predictor``
* ``fhops_response``

The adapter does not import FHOPS and does not create FHOPS scenarios directly.

Private-Data Hygiene
--------------------

Integration exports can contain source-document paths and recovered private
values. Keep CSVs and sidecars under ignored output directories such as
``tmp/`` until they are explicitly sanitized for public release.
