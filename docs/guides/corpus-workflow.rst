Corpus Workflow
===============

The corpus pipeline coordinates deterministic document preparation and review
artifacts across many PDFs. It is designed for workstation-scale runs where a
user wants stable artifact paths, resumability, and structured failure
summaries.

Current Boundary
----------------

The Phase 6 pipeline provides:

* corpus configuration records;
* standard artifact directories;
* rendered-page generation for source PDFs;
* optional cropping from an explicit figure candidate manifest;
* run manifests with document, figure, step, status, and diagnostic records;
* resume behavior that skips already rendered page artifacts;
* accepted-table export from review manifests.

The pipeline does not yet infer chart calibration or extraction settings for
arbitrary figures. Numeric extraction remains a calibrated image-level step
unless a later workflow supplies explicit extraction settings.

Artifact Layout
---------------

Every corpus run writes under a caller-selected output root:

* ``pages/`` for rendered PDF pages;
* ``crops/`` for cropped figure candidates;
* ``overlays/`` for QA overlays;
* ``tables/`` for recovered or accepted tables;
* ``manifests/`` for configs, run manifests, figure manifests, and review
  manifests;
* ``logs/`` for future run logs.

Keep output roots under ignored local directories such as ``tmp/`` when working
with private documents.

CLI Example
-----------

Initialize a run:

.. code-block:: bash

   figrecover corpus init tmp/corpus \
      --pdf report.pdf \
      --config-path tmp/corpus-config.json \
      --dpi 200 \
      --max-workers 4

Run it:

.. code-block:: bash

   figrecover corpus run tmp/corpus-config.json

Summarize the run manifest:

.. code-block:: bash

   figrecover corpus summarize tmp/corpus/manifests/run-manifest.json

Export accepted tables after review:

.. code-block:: bash

   figrecover corpus export tmp/review/review.jsonl \
      --out-dir tmp/corpus/tables/accepted

Python Example
--------------

.. code-block:: python

   from pathlib import Path

   from figrecover.pipeline import (
       CorpusInput,
       CorpusRenderOptions,
       CorpusRunConfig,
       CorpusWorkerOptions,
       run_corpus,
   )

   config = CorpusRunConfig(
       run_id="forest-plan-batch",
       inputs=CorpusInput(input_dir=Path("tmp/pdfs")),
       output_root=Path("tmp/corpus"),
       render=CorpusRenderOptions(dpi=200, pages="1-10"),
       workers=CorpusWorkerOptions(max_workers=8),
   )

   manifest = run_corpus(config)
   print(manifest.summary())

Failure Recovery
----------------

Corpus runs continue after individual PDF rendering or figure-cropping failures
where possible. Failures are recorded as structured diagnostics with the step,
item path, exception type, and concise message. This is enough to triage common
problems without storing full private document text in public-facing records.

Private-Data Hygiene
--------------------

Do not commit private PDFs, rendered pages, crops, overlays, review manifests,
logs, or recovered private tables. Sanitized examples should use synthetic or
explicitly public-safe fixtures only.
