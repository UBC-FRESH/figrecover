Development Checks
==================

Default checks are designed to run without private documents, GPU access, local
VLM model servers, or workstation-specific state.

Local Checks
------------

Run these before closing implementation work:

.. code-block:: bash

   python -m ruff check .
   python -m pytest
   sphinx-build -b html docs _build/html -W
   python -m build
   twine check dist/*

For tests that exercise PDF rendering, install the optional PDF dependencies:

.. code-block:: bash

   python -m pip install -e '.[dev,pdf]'

CI Boundary
-----------

The default GitHub Actions workflow runs on public GitHub-hosted Linux runners
for Python 3.11 and 3.12. It installs development and PDF extras, then runs:

* Ruff lint checks;
* pytest;
* Sphinx documentation build with warnings as errors;
* package build;
* Twine metadata checks.

GPU, VLM, large-corpus, and private-document evaluations are intentionally kept
out of default CI. Those checks should remain local or explicitly opt-in until
the project has public fixtures and stable infrastructure for them.

Private-Data Hygiene
--------------------

Do not add private PDFs, generated private crops, review bundles, prompt logs,
or recovered private tables to CI fixtures. CI examples and tests must generate
their own synthetic inputs or use explicitly public-safe fixtures.
