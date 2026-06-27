Quickstart
==========

Install a development checkout:

.. code-block:: bash

   python -m venv .venv
   . .venv/bin/activate
   python -m pip install -e '.[dev]'

Digitize a prepared image crop with known plot bounds:

.. code-block:: bash

   figrecover digitize-image crop.png \
     --mode line \
     --series-name harvest \
     --series-color '#1f77b4' \
     --plot-left 80 --plot-right 520 --plot-top 40 --plot-bottom 360 \
     --x-min 0 --x-max 100 --y-min 0 --y-max 250 \
     --out harvest.csv

Use the Python API when integrating into a larger system:

.. code-block:: python

   from pathlib import Path

   from figrecover import Calibration, DigitizeSpec, SeriesSpec, digitize_image

   spec = DigitizeSpec(
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
       series=[SeriesSpec(name="harvest", color="#1f77b4", mode="line")],
   )

   result = digitize_image(Path("crop.png"), spec)
   result.to_dataframe().to_csv("harvest.csv", index=False)
