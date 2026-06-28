"""Run the corpus renderer on a generated synthetic PDF.

The example requires PyMuPDF, which is available through the optional
``figrecover[pdf]`` extra.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from figrecover.pipeline import (
    CorpusInput,
    CorpusRenderOptions,
    CorpusRunConfig,
    CorpusWorkerOptions,
    run_corpus,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("tmp/examples/synthetic-corpus"),
        help="Directory for generated PDF and corpus outputs.",
    )
    args = parser.parse_args()

    paths = run_example(args.out_dir)
    for name, path in paths.items():
        print(f"{name}: {path}")


def run_example(out_dir: Path) -> dict[str, Path]:
    """Create a synthetic PDF and run the corpus renderer."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "synthetic-report.pdf"
    output_root = out_dir / "corpus"
    config_path = out_dir / "corpus-config.json"

    _write_synthetic_pdf(pdf_path)

    config = CorpusRunConfig(
        run_id="synthetic-corpus-example",
        inputs=CorpusInput(pdfs=[pdf_path]),
        output_root=output_root,
        render=CorpusRenderOptions(dpi=100, pages="1"),
        workers=CorpusWorkerOptions(max_workers=1),
    )
    config.write_json(config_path)
    manifest = run_corpus(config)

    return {
        "pdf": pdf_path,
        "config": config_path,
        "run_manifest": output_root / "manifests" / "run-manifest.json",
        "rendered_page": output_root / "pages" / "synthetic-report-p0001.png",
        "summary": _write_summary(out_dir / "summary.txt", manifest.summary()),
    }


def _write_synthetic_pdf(path: Path) -> None:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit(
            "This example requires PyMuPDF. Install it with "
            "`python -m pip install -e '.[pdf]'` from the repository root."
        ) from exc

    document = fitz.open()
    page = document.new_page(width=432, height=288)
    page.insert_text((42, 36), "Synthetic technical report")
    page.draw_rect((72, 72, 360, 240), color=(0, 0, 0), width=1)
    page.draw_line((72, 220), (160, 180), color=(0.12, 0.47, 0.71), width=2)
    page.draw_line((160, 180), (250, 140), color=(0.12, 0.47, 0.71), width=2)
    page.draw_line((250, 140), (360, 90), color=(0.12, 0.47, 0.71), width=2)
    page.insert_text((72, 260), "Figure 1. Synthetic line chart.")
    document.save(path)
    document.close()


def _write_summary(path: Path, summary: dict[str, object]) -> Path:
    lines = [f"{key}: {value}" for key, value in sorted(summary.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    main()
