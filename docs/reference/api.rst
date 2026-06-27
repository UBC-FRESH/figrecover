API Reference
=============

The package root exposes a small convenience facade for the most common
calibration and digitization records. Implementation code should prefer the
module-level imports documented below while the package remains pre-release.

Calibration
-----------

.. automodule:: figrecover.calibration
   :members:

Digitization Models
-------------------

.. automodule:: figrecover.models
   :members:

Extraction diagnostics are structured records with a severity level, stable
code, human-readable message, and context dictionary. Downstream workflows
should use diagnostic codes rather than parsing messages.

``DigitizeResult.to_dataframe(include_provenance=True)`` returns a long table
with document, figure, crop, and extraction-tool metadata suitable for
combining recovered points from many figures.

Workflow Records
----------------

.. automodule:: figrecover.records
   :members:
   :no-index:

Digitization
------------

.. automodule:: figrecover.digitize
   :members:

Extraction Boundary
-------------------

.. automodule:: figrecover.extraction
   :members:

Export Helpers
--------------

.. automodule:: figrecover.io
   :members:

PDF Helpers
-----------

.. automodule:: figrecover.pdf
   :members:
