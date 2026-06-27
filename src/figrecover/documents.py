"""PDF rendering and figure-candidate preparation helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from pathlib import Path

from PIL import Image

from figrecover.records import FigureCandidate, RenderedPage


class OptionalDependencyError(RuntimeError):
    """Raised when an optional dependency group is required but unavailable."""


def require_pymupdf():
    """Return the PyMuPDF module or raise a helpful optional-dependency error."""

    try:
        import fitz
    except ImportError as exc:
        raise OptionalDependencyError(
            "PDF support requires the optional pdf dependencies. Install them with "
            "`python -m pip install figrecover[pdf]`."
        ) from exc
    return fitz


def parse_page_selection(pages: str | Iterable[int] | None, *, page_count: int) -> list[int]:
    """Normalize a one-based page selection.

    ``pages`` may be ``None`` for all pages, an iterable of one-based page
    numbers, or a comma-separated string with ranges such as ``"1,3-5"``.
    Returned page numbers are one-based, de-duplicated, and sorted by first
    occurrence.
    """

    if page_count < 1:
        return []

    if pages is None:
        values = list(range(1, page_count + 1))
    elif isinstance(pages, str):
        values = []
        for part in pages.split(","):
            token = part.strip()
            if not token:
                continue
            if "-" in token:
                start_text, end_text = token.split("-", 1)
                start = int(start_text)
                end = int(end_text)
                if end < start:
                    raise ValueError(f"invalid descending page range: {token}")
                values.extend(range(start, end + 1))
            else:
                values.append(int(token))
    else:
        values = [int(page) for page in pages]

    normalized: list[int] = []
    seen: set[int] = set()
    for page in values:
        if page < 1 or page > page_count:
            raise ValueError(f"page {page} is outside the document range 1-{page_count}")
        if page not in seen:
            normalized.append(page)
            seen.add(page)
    return normalized


def render_pdf_pages(
    pdf_path: Path,
    output_dir: Path,
    *,
    pages: str | Sequence[int] | None = None,
    dpi: int = 300,
    image_format: str = "png",
    document_id: str | None = None,
    overwrite: bool = False,
) -> list[RenderedPage]:
    """Render selected PDF pages to image files.

    Page numbers are one-based in the public API. PyMuPDF is loaded lazily so
    the default package installation can remain free of PDF dependencies.
    """

    if dpi < 1:
        raise ValueError("dpi must be at least 1")

    fitz = require_pymupdf()
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    ext = image_format.lower().lstrip(".")
    if not ext:
        raise ValueError("image_format must not be empty")

    doc_id = document_id or _slugify(pdf_path.stem)
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[RenderedPage] = []

    document = fitz.open(pdf_path)
    try:
        page_numbers = parse_page_selection(pages, page_count=document.page_count)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        renderer_version = _pymupdf_version(fitz)
        for page_number in page_numbers:
            out_path = output_dir / f"{doc_id}-p{page_number:04d}.{ext}"
            if out_path.exists() and not overwrite:
                raise FileExistsError(
                    f"render output already exists: {out_path}. Pass overwrite=True to replace it."
                )
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(out_path)
            rendered.append(
                RenderedPage(
                    document_id=doc_id,
                    page_number=page_number,
                    image_path=out_path,
                    source_pdf=pdf_path,
                    width_px=pixmap.width,
                    height_px=pixmap.height,
                    dpi=dpi,
                    renderer="pymupdf",
                    metadata={
                        "renderer_version": renderer_version,
                        "page_count": document.page_count,
                        "page_index": page_number - 1,
                        "image_format": ext,
                    },
                )
            )
    finally:
        document.close()

    return rendered


def crop_figure_candidate(
    candidate: FigureCandidate,
    output_dir: Path,
    *,
    source_image_path: Path | None = None,
    overwrite: bool = False,
    image_format: str | None = None,
) -> FigureCandidate:
    """Crop one figure candidate from its source image and return an updated record."""

    if candidate.bbox is None:
        raise ValueError(f"candidate {candidate.figure_id!r} has no bbox to crop")

    source_path = source_image_path or candidate.source_image_path or candidate.image_path
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ext = (image_format or source_path.suffix.lstrip(".") or "png").lower()
    out_path = output_dir / f"{_slugify(candidate.figure_id)}.{ext}"
    if out_path.exists() and not overwrite:
        raise FileExistsError(
            f"crop output already exists: {out_path}. Pass overwrite=True to replace it."
        )

    bbox = candidate.bbox
    with Image.open(source_path) as image:
        crop = image.crop((bbox.left, bbox.top, bbox.right, bbox.bottom))
        crop.save(out_path)

    metadata = dict(candidate.metadata)
    metadata.update(
        {
            "crop_width_px": bbox.width,
            "crop_height_px": bbox.height,
            "source_image_path": str(source_path),
        }
    )
    return candidate.model_copy(
        update={
            "image_path": out_path,
            "source_image_path": source_path,
            "metadata": metadata,
        }
    )


def crop_figure_candidates(
    candidates: Iterable[FigureCandidate],
    output_dir: Path,
    *,
    overwrite: bool = False,
    image_format: str | None = None,
) -> list[FigureCandidate]:
    """Crop a sequence of figure candidates from their source images."""

    return [
        crop_figure_candidate(
            candidate,
            output_dir,
            overwrite=overwrite,
            image_format=image_format,
        )
        for candidate in candidates
    ]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "document"


def _pymupdf_version(fitz: object) -> str | None:
    version = getattr(fitz, "version", None)
    if isinstance(version, tuple) and version:
        return str(version[0])
    if isinstance(version, str):
        return version
    return None


__all__ = [
    "OptionalDependencyError",
    "crop_figure_candidate",
    "crop_figure_candidates",
    "parse_page_selection",
    "render_pdf_pages",
    "require_pymupdf",
]
