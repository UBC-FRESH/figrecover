# TFL 6 Case Study Publication Plan

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Current package release: `0.1.0a1`

## Purpose

Use the TFL 6 Management Plan PDF as the primary realistic deployment case
study for `figrecover`, with two intended publication products:

- a Sphinx user-guide case study showing a real technical-document workflow;
- the primary empirical results/example narrative for the eventual JOSS paper.

This plan supersedes the earlier local prototype-harness framing only for
publication planning. The original local harness note remains useful for early
page/figure targeting.

## Local Source

The PDF is currently present locally at:

```text
examples/TFL6_MP_11_202606_w_Appendices_Web-compressed.pdf
```

The file is ignored by `.gitignore` through the repository-wide `*.pdf` rule,
so it is not currently tracked or included in the public package/repository
release.

This is the correct default until provenance and reuse permissions are
confirmed. Being physically under `examples/` does not by itself make the PDF a
tracked publication artifact.

## Publication Gate

Before using TFL 6 figures, crops, overlays, recovered tables, or screenshots
as tracked docs/JOSS artifacts:

- [ ] Confirm the public source URL for the exact PDF/version.
- [ ] Confirm reuse/license/citation terms for the management-plan document.
- [ ] Decide whether the raw PDF should remain untracked and be downloaded by
  users, or whether a small public-safe derivative fixture can be tracked.
- [ ] Record document citation metadata.
- [ ] Record any required acknowledgements.
- [ ] Confirm that extracted figure data can be published as derived evidence.
- [ ] Keep all private or uncertain artifacts under `tmp/` until this gate is
  complete.

## Case Study Workflow

The case study should demonstrate the package's intended realistic workflow:

1. Source-document provenance and citation.
2. PDF page rendering.
3. Figure inventory and relevance screening.
4. Figure candidate cropping.
5. Chart-type triage and calibration.
6. Deterministic extraction where supported.
7. QA overlay generation.
8. Review manifest decisions.
9. Accepted recovered-table export.
10. Summary of recoverable, partially recoverable, and unsupported figures.

The workflow should make unsupported cases visible rather than hiding them.
That is important for a credible JOSS paper: the result is an auditable
technical-document deployment, not a claim of perfect automated recovery.

## Figure Inventory Target

Initial prototype targets from `planning/tfl6-prototype-harness.md` remain the
starting set:

| PDF page | Figure | Expected chart family | Publication role |
| --- | --- | --- | --- |
| 82 | Figure 2 | line/area | simple deterministic extraction example |
| 83 | Figure 3 | line | multi-series line extraction example |
| 86 | Figure 6 | bar | age-class distribution example |
| 88 | Figure 8 | line | noisy multi-series operational example |
| 89 | Figure 9 | line | growing-stock multi-series example |
| 92 | Figure 12 | stacked area | limitation/partial-support example |
| 103 | Figure 21 | line | chart adjacent to table example |
| 115 | Figure 27 | line | grayscale scientific curve example |
| 116 | Figure 28 | line | small-multiple curve example |
| 123 | Figure 32 | line | scenario comparison example |

The full case study should later expand from this prototype set to all
relevant figures in the document. "Relevant" should be defined as figures that
contain recoverable numeric/categorical chart data useful for modelling or
metadata, excluding purely illustrative maps, diagrams, photos, and non-chart
figures unless they are useful as negative examples.

## Output Layout

Ignored local outputs should live under:

```text
tmp/tfl6_case_study/
```

Recommended subdirectories:

- `pages/` for rendered PDF pages;
- `crops/` for figure crops;
- `manifests/` for figure inventory, crop manifests, review manifests, and run
  summaries;
- `results/` for extraction JSON;
- `tables/` for recovered CSV/Parquet outputs;
- `overlays/` for QA overlays;
- `notes/` for manual calibration and review notes.

Tracked publication artifacts, once approved, should be small and deliberate:

- a source citation note;
- a figure-inventory summary table;
- selected publication-safe QA overlays or derived plots;
- summarized recovered values or diagnostics where reuse permissions allow;
- Sphinx narrative pages that link to public source and describe how to
  reproduce the ignored local outputs.

## JOSS Results Direction

The JOSS paper should present the TFL 6 case study as evidence that
`figrecover` can support realistic technical-document workflows:

- number of relevant figures inventoried;
- number of figures cropped;
- number of figures successfully extracted deterministically;
- number requiring manual calibration or review;
- number unsupported and why;
- examples of diagnostics and review decisions;
- example recovered tables/series where publication-safe.

Do not present the case study as exhaustive proof of general chart recovery
accuracy. Present it as a realistic deployment demonstrating provenance,
auditable workflows, and honest limitations.

## Sphinx User Guide Direction

The Sphinx docs should eventually include a TFL 6 case-study guide that:

- explains how to obtain or reference the source PDF;
- shows the corpus/run layout under `tmp/tfl6_case_study/`;
- walks through figure inventory and cropping;
- shows selected extraction and review examples;
- explains failure modes and unsupported chart classes;
- exports accepted tables through generic/FEMIC-compatible formats;
- keeps raw/generated artifacts out of the repository unless publication-safe.

## Required Package Work Before Full Case Study

- [ ] Add or document a figure inventory workflow for all candidate chart
  figures in a PDF.
- [ ] Add a repeatable local case-study runner or config that writes only under
  `tmp/tfl6_case_study/`.
- [ ] Add a manifest schema or convention for manual calibration decisions.
- [ ] Add a case-study summary exporter for figure status and extraction
  outcomes.
- [ ] Decide which derived artifacts can be tracked after provenance review.

## Private-Data And Public-Data Hygiene

Until reuse rights are confirmed, treat the TFL 6 PDF and all generated
artifacts as local ignored materials. Do not track the raw PDF, rendered pages,
crops, overlays, recovered tables, VLM prompts, raw model responses, or review
bundles.

If the PDF is confirmed public and reusable, prefer citing/linking the public
source over committing the large PDF. Track only compact, necessary,
publication-safe derivatives.
