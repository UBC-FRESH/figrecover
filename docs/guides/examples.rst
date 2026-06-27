Examples
========

The repository includes scriptable examples under ``examples/``. They generate
synthetic inputs and write outputs under ``tmp/examples/`` by default.

Synthetic Chart Extraction
--------------------------

Generate a simple line chart, digitize it, write JSON/CSV outputs, and render a
QA overlay:

.. code-block:: bash

   python examples/synthetic_chart_extraction.py

Synthetic PDF Corpus
--------------------

Generate a synthetic PDF and run the corpus renderer:

.. code-block:: bash

   python examples/synthetic_pdf_corpus.py

This example requires the optional PDF dependency:

.. code-block:: bash

   python -m pip install -e '.[pdf]'

Mocked VLM Metadata
-------------------

Parse a mocked VLM chart-metadata response without requiring GPU access, model
weights, or local model serving:

.. code-block:: bash

   python examples/mocked_vlm_metadata.py

Private-Data Hygiene
--------------------

Examples must remain publication-safe. Generated outputs should stay under
ignored directories such as ``tmp/`` unless explicitly sanitized for public
documentation or release artifacts.
