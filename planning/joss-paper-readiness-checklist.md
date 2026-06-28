# JOSS Paper Readiness Checklist

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Related issue: #65

Current package release: `0.1.0a1`

Target paper timing: after pyOpenSci acceptance or when the pyOpenSci/JOSS path
is clearly ready.

## Status

This is a paper-readiness plan. A preliminary manuscript draft now exists under
`paper/` by maintainer request, but it is not submission-ready. The draft must
not be treated as satisfying the paper gate until the package can describe
stable software, credible evidence, and citable release artifacts.

## Paper Gate

Before drafting repository paper files, confirm:

- pyOpenSci review is accepted or the pyOpenSci/JOSS path is otherwise clearly
  ready for use.
- The reviewed package version is stable, installable, and archived.
- `CITATION.cff`, README citation guidance, and Sphinx citation guidance match
  the reviewed release.
- The statement of need is mature and reviewers have not identified a major
  scope-fit issue.
- The TFL 6 case-study publication gate is resolved if TFL 6 evidence will be
  used.
- Any paper figures are synthetic or explicitly public-safe.
- Related-work references are collected in a draft bibliography list.
- AI usage disclosure language is accurate and consistent with lab practice.

## Planned Paper Files

Preliminary draft files:

- `paper/paper.md`
- `paper/paper.bib`
- optional publication-safe figures under `paper/`

The existing draft should remain a manuscript skeleton until the paper gate is
satisfied. It should not duplicate installation instructions, CLI reference, or
API how-to content that belongs in the Sphinx docs.

## Section-Level Readiness

### Summary

- [ ] State what `figrecover` does in one concise paragraph.
- [ ] State that recovered values are approximate and review-gated.
- [ ] Mention deterministic extraction, PDF preparation, QA/review, corpus
      workflows, optional VLM metadata proposals, and modelling exports.

### Statement Of Need

- [ ] Explain the problem of published figures without source data tables.
- [ ] Explain why auditable recovery matters for modelling workflows.
- [ ] Distinguish `figrecover` from manual digitizers, document parsers, and
      VLM-only approaches.
- [ ] Keep claims aligned with supported chart classes and limitations.

### State Of The Field

- [ ] Summarize manual chart-digitization tools.
- [ ] Summarize algorithmic chart extraction and computer-vision approaches.
- [ ] Summarize document parsing/layout extraction tools.
- [ ] Summarize VLM chart/document understanding as assistive rather than
      authoritative numeric extraction.
- [ ] Identify the specific open Python workflow gap that `figrecover` fills.

### Software Design

- [ ] Describe the module boundaries: documents, manifests, records,
      calibration, extraction, QA/review, pipeline, VLM proposals, integrations.
- [ ] Explain deterministic-first numeric extraction.
- [ ] Explain provenance and diagnostic records.
- [ ] Explain why VLM outputs are proposals by default.

### Results Or Deployment Evidence

- [ ] Use the TFL 6 Management Plan case study if the publication gate is
      complete.
- [ ] Otherwise use synthetic and public-safe examples only.
- [ ] Report recoverable, partially recoverable, and unsupported cases.
- [ ] Include summary counts and diagnostics rather than only success cases.
- [ ] Avoid publishing raw private or uncertain artifacts.

### Research Impact

- [ ] Connect package capabilities to reproducible technical-document data
      recovery.
- [ ] Explain relevance to FEMIC/FHOPS-style modelling without making the paper
      project-specific.
- [ ] State limitations honestly.

### AI Usage Disclosure

- [ ] Disclose optional package VLM use for chart metadata proposals.
- [ ] Disclose that VLMs are not authoritative numeric extractors by default.
- [ ] Disclose AI coding/writing assistance according to final journal policy
      and lab practice.

### Acknowledgements And References

- [ ] Identify funding, lab, and collaborator acknowledgements.
- [ ] Include package/software references.
- [ ] Include field-context references.
- [ ] Include case-study source citation if TFL 6 evidence is used.

## Evidence Matrix

The paper should be backed by a concise evidence matrix before drafting:

| Evidence item | Source | Public-safe status | Paper role |
| --- | --- | --- | --- |
| Synthetic extraction example | `examples/synthetic_chart_extraction.py` | safe | package capability illustration |
| Synthetic PDF corpus example | `examples/synthetic_pdf_corpus.py` | safe | corpus workflow illustration |
| Mocked VLM metadata example | `examples/mocked_vlm_metadata.py` | safe | VLM boundary illustration |
| TFL 6 figure inventory | `tmp/tfl6_case_study/` later | gated | realistic deployment results |
| TFL 6 QA overlays/tables | `tmp/tfl6_case_study/` later | gated | selected case-study evidence |
| pyOpenSci review outcome | external review issue later | public after review | package quality context |
| v1.0.0 archive DOI | archive later | public after release | citable reviewed software |

## Exemplar Review

- [x] Downloaded and reviewed representative published JOSS papers under
      ignored `tmp/joss_exemplars/`.
- [x] Recorded structure and tone findings in
      `planning/joss-exemplar-paper-review.md`.
- [x] Revised the draft toward a published-JOSS-paper pattern: Summary,
      Statement of need, State of the field, Software design, Functionality,
      Research impact statement, Applications and limitations, AI usage
      disclosure, Acknowledgements, and References.

## Paper Build And Review Workflow

When paper files exist:

1. Add paper build instructions to the docs or development guide.
2. Build/check the paper with the recommended JOSS tooling available at that
   time.
3. Keep bibliography entries minimal and relevant.
4. Track each JOSS reviewer request as a GitHub issue or PR.
5. Keep package docs as the source of detailed user guidance.
6. Add JOSS DOI and citation instructions only after acceptance.

## Private-Data Hygiene

Do not include private forestry PDFs, generated private crops, prompt logs,
raw VLM responses, recovered private tables, or unapproved TFL 6 derivatives in
the paper, paper figures, docs, release archives, or review materials.

## Draft Status

- [x] Preliminary `paper/paper.md` created.
- [x] Preliminary `paper/paper.bib` created.
- [x] Alpha software availability section added with GitHub, docs, PyPI, and
      prerelease links.
- [ ] Author list and affiliations finalized.
- [ ] Replace alpha software citation with v1.0.0 release and archive DOI.
- [ ] TFL 6 case-study evidence added only after publication gate.
- [ ] Paper build/check workflow added.
- [ ] JOSS submission timing confirmed.

## Closeout Requirements For P9.5

Issue #65 should remain open until paper files exist, the paper builds, JOSS
submission or acceptance links are recorded, and review feedback has been
handled. This draft tranche starts the manuscript but does not complete P9.5.
