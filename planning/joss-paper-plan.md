# JOSS Paper Plan

Date: 2026-06-28

Phase: Phase 9 Scholarly Publication And Peer Review

Current package release: `0.1.0a1`

Target paper timing: after pyOpenSci acceptance or when the pyOpenSci/JOSS
pathway requirements are clearly satisfied.

## Positioning

The JOSS paper should be a concise scholarly companion to the package, not a
replacement for the user guide. It should explain why `figrecover` matters,
what scientific workflow gap it addresses, how the software is designed, and
how it can support reproducible technical-document data recovery.

The package docs should remain the source of truth for installation, API usage,
CLI details, examples, and workflow instructions.

## Repository Paper Files

Do not create paper files during the Phase 9 launch tranche. When the project
is ready for paper drafting, add:

- `paper/paper.md`
- `paper/paper.bib`
- publication-safe figures under `paper/` only if needed

Paper files must live in the software repository. Any figures must be synthetic
or explicitly public-safe.

## Expected Sections

Planned paper structure:

- Summary.
- Statement of need.
- State of the field.
- Software design.
- Research impact statement.
- AI usage disclosure.
- Acknowledgements.
- References.

The paper should stay within the JOSS expected length range and focus on
software purpose, research application, scholarly significance, and field
context.

## Statement Of Need Direction

Candidate statement-of-need points:

- Many scientific and professional technical documents publish figures without
  the original source tables.
- Reusing those figures as model inputs requires approximate recovery with
  provenance, diagnostics, and review, not unsupported numeric guesses.
- Existing tools cover manual chart digitization, document parsing, or VLM
  chart understanding, but `figrecover` combines calibrated deterministic
  extraction, PDF preparation, QA/review manifests, corpus workflows, and
  modelling export contracts in an open Python package.
- Forestry and operations-modelling workflows such as FEMIC/FHOPS provide
  motivating use cases, but the package should be presented as general
  technical-document recovery software.

## State Of Field Direction

The field context should compare against:

- manual chart digitization tools;
- computer-vision chart extraction approaches;
- document parsing/layout extraction tools;
- VLM-assisted chart understanding;
- reproducibility and provenance requirements for scientific data recovery.

Avoid overstating novelty. Emphasize the specific open, auditable,
Python-integrated workflow gap.

## AI Usage Disclosure

The paper must disclose AI assistance accurately. At minimum:

- local/open VLMs are optional package components for chart metadata proposals;
- VLM outputs are not authoritative numeric recovered data by default;
- AI coding assistance was used in package development and should be disclosed
  according to the final journal policy and lab practice.

## Publication-Safe Figures

Potential figures:

- synthetic chart extraction workflow diagram;
- QA overlay example from a synthetic chart;
- corpus artifact layout schematic;
- review-gated export workflow.

Do not use private forestry PDFs, private crops, private extracted values, or
generated artifacts derived from unpublished documents.

## References To Prepare

Reference groups to collect later:

- chart digitization and plot data extraction methods;
- document parsing and layout analysis tools;
- VLM chart/document understanding research;
- reproducible scientific software and data provenance sources;
- FEMIC/FHOPS papers or public documentation only if appropriate and public.

## Submission Path

- [ ] Complete pyOpenSci readiness and review first.
- [ ] Add paper files only when the package is close to or past v1.0.0 review
  readiness.
- [ ] Build/check the paper locally with recommended JOSS tooling.
- [ ] Submit to JOSS with the pyOpenSci review context.
- [ ] Track JOSS reviewer feedback as GitHub issues/PRs.
- [ ] Add DOI and citation metadata after acceptance.
