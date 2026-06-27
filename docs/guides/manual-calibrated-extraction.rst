Manual Calibrated Extraction
============================

Manual calibrated extraction is the most durable ``figrecover`` workflow. A
user supplies a prepared chart crop, plot-frame pixel bounds, axis data bounds,
and series definitions. ``figrecover`` then maps detected pixels back into data
coordinates and records diagnostics for review.

When To Use It
--------------

Use manual calibrated extraction when:

* the figure is already cropped to a single chart;
* the plot frame can be identified by pixel coordinates;
* the axis scale and data bounds are known from labels or ticks;
* one or more series can be separated by colour or simple component geometry;
* recovered values need an auditable path from image pixels to table rows.

This workflow is slower than a fully automatic claim, but it is much easier to
audit and defend.

Calibration
-----------

Linear calibration maps a plot rectangle onto data-space axis bounds:

.. code-block:: python

   from figrecover import Calibration

   calibration = Calibration.from_plot_bounds(
       plot_left=80,
       plot_right=520,
       plot_top=40,
       plot_bottom=360,
       x_min=0,
       x_max=100,
       y_min=0,
       y_max=250,
   )

Log axes are represented in the calibration record and transformed before
values are written. Use log calibration only when the original chart axis is
log-scaled; do not use it as a smoothing or regression tool.

Series Definitions
------------------

Each series specifies a name, colour, and extraction mode:

.. code-block:: python

   from figrecover import SeriesSpec

   series = [
       SeriesSpec(name="observed", color="#1f77b4", mode="scatter"),
       SeriesSpec(name="projection", color="#d62728", mode="line"),
   ]

Line extraction samples coloured pixels by x-column. The default aggregation is
``median``. Filled area charts can often be recovered by using
``line_aggregation="min"`` for the top edge or ``"max"`` for the bottom edge.

Scatter extraction uses connected components. Bar extraction uses contiguous
runs and baseline handling. These are deterministic image operations, not VLM
guesses.

Python Workflow
---------------

.. code-block:: python

   from pathlib import Path

   from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image
   from figrecover.io import write_result_json, write_points_csv

   spec = DigitizeSpec(
       image_id="crop-001",
       source_document_id="report-2026",
       source_figure_id="figure-4",
       figure_label="Figure 4",
       source_page=12,
       calibration=Calibration.from_plot_bounds(
           plot_left=80,
           plot_right=520,
           plot_top=40,
           plot_bottom=360,
           x_min=0,
           x_max=100,
           y_min=0,
           y_max=250,
       ),
       series=[SeriesSpec(name="projection", color="#1f77b4", mode="line")],
   )

   result = digitize_image(Path("tmp/crops/figure-4.png"), spec)
   write_result_json(result, Path("tmp/results/figure-4.json"))
   write_points_csv(
       result,
       Path("tmp/tables/figure-4.csv"),
       include_provenance=True,
   )

CLI Workflow
------------

.. code-block:: bash

   figrecover digitize-image tmp/crops/figure-4.png \
      --mode line \
      --series-name projection \
      --series-color '#1f77b4' \
      --plot-left 80 --plot-right 520 --plot-top 40 --plot-bottom 360 \
      --x-min 0 --x-max 100 --y-min 0 --y-max 250 \
      --out tmp/tables/figure-4.csv

For batch work, keep generated crops, JSON results, overlays, review manifests,
and recovered tables under ignored output directories such as ``tmp/`` until
they have been explicitly sanitized for public release.

Diagnostics And Review
----------------------

Extraction results include diagnostics for common failure modes such as no
matched pixels, sparse results, clipped pixels, filtered components, or missing
plot bounds. Diagnostics should guide review, not replace it.

The recommended next step is to generate a QA review bundle and inspect the
overlay before accepting recovered values for modelling.
