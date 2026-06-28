Release Process
===============

Alpha releases are maintainer-gated. Ordinary pushes and pull requests must not
publish packages.

Release Checklist
-----------------

Before publishing an alpha:

* confirm the roadmap and changelog describe the release scope;
* confirm all public examples are synthetic or explicitly public-safe;
* confirm private PDFs, crops, overlays, review manifests, prompt logs, and
  recovered private tables are not tracked;
* confirm the version in ``pyproject.toml`` matches the intended release;
* run the local release checks;
* run the release workflow with ``skip-publish`` enabled;
* publish to TestPyPI first when credentials or trusted publishing are ready;
* publish to PyPI only after maintainer approval.

Local Release Checks
--------------------

.. code-block:: bash

   rm -rf dist build
   python -m ruff check .
   python -m pytest
   sphinx-build -b html docs _build/html -W
   python -m build
   twine check dist/*

Clean Wheel Install
-------------------

For release candidates, verify the built wheel in a fresh environment:

.. code-block:: bash

   python -m venv tmp/release-check-venv
   . tmp/release-check-venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install dist/figrecover-*.whl
   figrecover --help
   deactivate

GitHub Release Workflow
-----------------------

The release workflow is manually triggered with two controls:

* ``target`` selects ``testpypi`` or ``pypi``;
* ``skip-publish`` defaults to true and performs build verification without
  publishing.

Publishing jobs use GitHub environments named ``testpypi`` and ``pypi`` so the
repository can require maintainer approval and trusted-publishing configuration
before upload.

Version Policy
--------------

The Phase 8 alpha target is ``0.1.0a1``. Later alpha releases should increment
the alpha suffix. Stable ``1.0.0`` release work is reserved for Phase 9
publication and peer-review readiness.
