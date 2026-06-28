"""Render the draft JOSS paper to ignored local artifacts.

This helper intentionally writes under ``tmp/`` so rendered PDFs and HTML files
do not become repository artifacts before publication review.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _pandoc() -> object:
    try:
        import pypandoc
    except ImportError as exc:  # pragma: no cover - exercised by users without extra
        raise SystemExit(
            "Missing paper rendering dependency. Install with:\n"
            "  python -m pip install -e .[paper]\n"
            "or install pandoc/pypandoc manually."
        ) from exc
    return pypandoc


def render_paper(output_dir: Path, *, pdf: bool = True, html: bool = True) -> list[Path]:
    """Render ``paper/paper.md`` using ``paper/paper.bib``.

    Parameters
    ----------
    output_dir:
        Directory where rendered artifacts should be written.
    pdf:
        Whether to render ``paper.pdf``.
    html:
        Whether to render ``paper.html``.

    Returns
    -------
    list[pathlib.Path]
        Paths to rendered artifacts.
    """

    pypandoc = _pandoc()
    paper = Path("paper/paper.md")
    bibliography = Path("paper/paper.bib")
    output_dir.mkdir(parents=True, exist_ok=True)

    common_args = [
        "--standalone",
        "--citeproc",
        f"--bibliography={bibliography}",
        "--resource-path=paper",
    ]

    rendered: list[Path] = []
    if html:
        html_path = output_dir / "paper.html"
        pypandoc.convert_file(
            str(paper),
            "html",
            outputfile=str(html_path),
            extra_args=common_args,
        )
        rendered.append(html_path)

    if pdf:
        pdf_path = output_dir / "paper.pdf"
        pypandoc.convert_file(
            str(paper),
            "pdf",
            outputfile=str(pdf_path),
            extra_args=common_args + ["--pdf-engine=pdflatex"],
        )
        rendered.append(pdf_path)

    return rendered


def main() -> None:
    """Run the command line renderer."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/joss_render"),
        help="Directory for rendered artifacts. Defaults to tmp/joss_render.",
    )
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF rendering.")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML rendering.")
    args = parser.parse_args()

    if args.no_pdf and args.no_html:
        raise SystemExit("Nothing to render: both --no-pdf and --no-html were provided.")

    rendered = render_paper(args.output_dir, pdf=not args.no_pdf, html=not args.no_html)
    for path in rendered:
        print(path)


if __name__ == "__main__":
    main()
