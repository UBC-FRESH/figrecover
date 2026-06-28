figrecover
==========

``figrecover`` recovers approximate source tables from scientific and
professional figures when the original data were not published.

The package is pre-release. The current implementation supports deterministic
calibrated extraction from prepared image crops, deterministic PDF preparation,
review bundles, corpus orchestration, local VLM metadata proposals, and
downstream modelling exports.

The public-alpha contract is conservative: recovered values are approximate
and should be reviewed before they become scientific or operational model
inputs. Deterministic calibrated extraction is preferred for numeric recovery;
VLM outputs are metadata and calibration proposals unless a caller explicitly
chooses an experimental VLM-only path.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/quickstart
   guides/statement-of-need
   guides/manual-calibrated-extraction
   guides/workflow-boundaries
   guides/local-vlm-assistance
   guides/qa-review-workflow
   guides/corpus-workflow
   guides/integrations
   guides/examples
   guides/development-checks
   guides/release-process
   guides/citation-support
   guides/api-stability
   guides/limitations

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/api
   reference/cli
