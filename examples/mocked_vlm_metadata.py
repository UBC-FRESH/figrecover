"""Parse a mocked VLM chart metadata response.

This example demonstrates the VLM proposal boundary without requiring a GPU,
model weights, or a local model server.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from figrecover.vlm import parse_chart_metadata_response

MOCK_RESPONSE = """
{
  "chart_type": "line",
  "title": "Synthetic harvest forecast",
  "x_axis": {"label": "Year", "units": "year", "confidence": 0.8},
  "y_axis": {"label": "Volume", "units": "m3/ha", "confidence": 0.75},
  "series_colors": [
    {"series_name": "projection", "color": "#1f77b4", "confidence": 0.85}
  ],
  "warnings": ["mocked response for documentation example"],
  "confidence": 0.78
}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("tmp/examples/mocked-vlm"),
        help="Directory for parsed proposal output.",
    )
    args = parser.parse_args()

    path = run_example(args.out_dir)
    print(f"proposal: {path}")


def run_example(out_dir: Path) -> Path:
    """Parse mocked VLM metadata and write the structured proposal."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    parsed = parse_chart_metadata_response(MOCK_RESPONSE)
    output_path = out_dir / "chart-metadata-proposal.json"
    output_path.write_text(parsed.model_dump_json(indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    main()
