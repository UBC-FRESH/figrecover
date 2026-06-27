CLI Reference
=============

The CLI is intentionally thin. Command behavior should stay close to the Python
API and should emit files and summaries that can be consumed by automation.

Image Digitization
------------------

Calibrated image-crop digitization:

.. code-block:: bash

   figrecover digitize-image --help

PDF Rendering
-------------

Render selected one-based PDF pages to image files:

.. code-block:: bash

   figrecover pdf render report.pdf --out-dir tmp/pages --pages 1,3-5 --dpi 200

The command prints a JSON summary with rendered page records, including source
PDF path, page number, DPI, image dimensions, output path, and renderer
metadata.

Figure Manifests
----------------

List a JSONL figure candidate manifest:

.. code-block:: bash

   figrecover figures list tmp/manifests/figures.jsonl --json

Crop candidates from source page images:

.. code-block:: bash

   figrecover figures crop tmp/manifests/figures.jsonl \
      --out-dir tmp/crops \
      --out-manifest tmp/manifests/cropped-figures.jsonl

Manifest entries preserve candidate provenance. Source PDFs, rendered pages,
crops, and private-document manifests should remain under ignored local output
directories unless explicitly sanitized for tracking.

Review
------

Generate visual and tabular review artifacts from digitization JSON results:

.. code-block:: bash

   figrecover review bundle tmp/results/fig-001.json --out-dir tmp/review

Summarize review status counts and low-confidence entries:

.. code-block:: bash

   figrecover review summarize tmp/review/review.jsonl --json

Export accepted or manually corrected tables only:

.. code-block:: bash

   figrecover review export-accepted tmp/review/review.jsonl \
      --out-dir tmp/accepted-tables

Corpus
------

Initialize a corpus output root and config:

.. code-block:: bash

   figrecover corpus init tmp/corpus \
      --pdf report.pdf \
      --config-path tmp/corpus-config.json \
      --dpi 200

Run a configured corpus:

.. code-block:: bash

   figrecover corpus run tmp/corpus-config.json

Summarize a run manifest:

.. code-block:: bash

   figrecover corpus summarize tmp/corpus/manifests/run-manifest.json

Export accepted review tables:

.. code-block:: bash

   figrecover corpus export tmp/review/review.jsonl \
      --out-dir tmp/corpus/tables/accepted
