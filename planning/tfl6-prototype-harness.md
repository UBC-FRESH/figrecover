# TFL 6 Prototype Harness

Date: 2026-06-27

## Purpose

Use the locally supplied TFL 6 Management Plan PDF as a real-world development
harness for the first functional `figrecover` prototype.

The PDF itself, rendered pages, crops, and recovered data remain ignored local
artifacts. This note records only sanitized harness selection and implementation
implications.

## Local Source

Ignored local PDF:

```text
examples/TFL6_MP_11_202606_w_Appendices_Web-compressed.pdf
```

Basic structure observed locally:

- 475 PDF pages.
- Text extraction works.
- Figure captions and table-of-contents entries are extractable.
- Chart quality is generally good enough to focus on figure recovery rather
  than poor-scan restoration.

Ignored local harness outputs:

```text
tmp/tfl6_harness/contact_sheet_pages_082_126.png
tmp/tfl6_harness/prototype_pages.json
tmp/tfl6_harness/prototype_pages.csv
tmp/tfl6_harness/rendered_pages/
```

## Selected Prototype Pages

The initial prototype harness should focus on a small ladder of chart types:

| PDF page | Figure | Role | Expected chart family |
| --- | --- | --- | --- |
| 82 | Figure 2 | Simple filled harvest-level chart | line/area |
| 83 | Figure 3 | Two-series growing-stock chart | line |
| 86 | Figure 6 | Small-multiple age-class distributions | bar |
| 88 | Figure 8 | Multi-series noisy operational chart | line |
| 89 | Figure 9 | Multi-series growing-stock chart | line |
| 92 | Figure 12 | Species-composition chart | stacked area |
| 103 | Figure 21 | Line chart adjacent to summary table | line |
| 115 | Figure 27 | Grayscale scientific curve figure | line |
| 116 | Figure 28 | Small-multiple yield adjustment curves | line |
| 123 | Figure 32 | Scenario comparison chart adjacent to table | line |

## Implementation Implications

Phase 2 should use this harness to guide deterministic image-crop extraction:

- Keep synthetic tests as tracked CI fixtures.
- Use the TFL 6 PDF only for ignored local evaluation and manual review.
- Prioritize calibrated line, bar, and multi-series extraction before broad PDF
  automation.
- Record diagnostics that are useful on real charts: no pixels matched,
  ambiguous colour/series separation, low point density, and uncertain plot
  bounds.
- Do not block Phase 2 on stacked-area, small-multiple, or table-adjacent
  automation; these become acceptance pressure for later phases.

## Follow-Up

- Add a generic ignored-corpus evaluation command or script only when it can be
  useful for arbitrary PDFs, not just this document.
- Use this harness when validating Phase 3 PDF rendering and figure-crop
  manifests.
- Add public-safe synthetic fixtures that mimic these chart families without
  committing pages from the source PDF.

## Local Smoke Test

Page 82 / Figure 2 was cropped from the embedded PDF image block and evaluated
with manual calibration under ignored `tmp/tfl6_harness/` outputs.

Settings:

- crop: `tmp/tfl6_harness/crops/page_082_image_1.png`;
- plot frame: manually calibrated from the visible axes;
- series colour: bright green area fill;
- extraction mode: line extraction using the top edge of the coloured area;
- output: ignored local CSV/JSON under `tmp/tfl6_harness/recovered/`.

Observed result:

- 257 recovered samples at a 3-pixel stride;
- median recovered annual harvest was approximately 1.055 million m3;
- the result visually matches Figure 2's flat base-case harvest level.

This confirms that Phase 2 should support explicit line aggregation strategies
for median line marks and top/bottom edges of filled regions.
