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
