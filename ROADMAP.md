# Roadmap

This roadmap is the current project plan and issue tracker map for
`figrecover`.

The long-form package scope and implementation plan lives in
`planning/package-scope-and-implementation-plan.md`.

The public GitHub repository is `UBC-FRESH/figrecover`.

## Phase 0: Governance And Public Repo Bootstrap

GitHub parent issue: #1

Goal: establish the open-source repo contract before expanding code.

- [x] P0.1 Create project overview and agent operating contract. Child issue: #4.
- [x] P0.2 Establish roadmap, changelog, planning area, license, and ignore rules. Child issue: #3.
- [x] P0.3 Normalize package metadata and preserve current scaffold as bootstrap seed. Child issue: #2.
- [x] P0.4 Create initial GitHub issues after the public repo exists. Child issue: #5.

Status: complete.

## Phase 1: Architecture And Dependency Research

GitHub parent issue: #6

Goal: decide package boundaries before adding more features.

- [x] P1.1 Survey reusable open software. Child issue: #9.
- [x] P1.2 Define pipeline architecture. Child issue: #10.
- [x] P1.3 Define data/provenance contract. Child issue: #8.
- [x] P1.4 Record architecture contract and Phase 2 inputs. Child issue: #11.

Status: complete.

## Phase 2: Core Records, Calibration, And Extraction API

GitHub parent issue: #7

Active branch: `feature/p2-core-records-calibration-extraction-api`

Pull request: #17

Goal: build the durable Python API for calibrated image-level extraction.

- [x] P2.1 Stabilize record model. Child issue: #14.
- [x] P2.2 Implement calibrated extraction core. Child issue: #12.
- [x] P2.3 Add extraction diagnostics. Child issue: #13.
- [x] P2.4 Add focused synthetic tests. Child issue: #15.
- [x] P2.5 Add API docstrings and first Sphinx reference pages. Child issue: #16.

Status: complete.

## Phase 3: Document Ingestion And Figure Cropping

GitHub parent issue: #18

Active branch: `feature/p3-document-ingestion-figure-cropping`

Goal: turn PDFs into auditable figure candidates without requiring VLMs.

- [x] P3.1 Add PDF rendering. Child issue: #21.
- [x] P3.2 Add figure candidate manifest. Child issue: #22.
- [x] P3.3 Add parser adapters behind extras. Child issue: #20.
- [x] P3.4 Add PDF and figure CLI commands. Child issue: #19.
- [x] P3.5 Test with synthetic PDFs. Child issue: #23.

Status: complete.

## Phase 4: Local VLM Assistance Layer

GitHub parent issue: #25

Active branch: `feature/p4-local-vlm-assistance-layer`

Goal: use local open VLMs for chart understanding while keeping numeric
extraction auditable.

- [x] P4.1 Define VLM boundary. Child issue: #26.
- [x] P4.2 Add local backend interface. Child issue: #27.
- [x] P4.3 Add structured prompt templates. Child issue: #28.
- [x] P4.4 Add self-ensemble utilities. Child issue: #29.
- [x] P4.5 Add GPU/system docs. Child issue: #30.

Status: complete.

## Phase 5: QA, Review, And Human-In-The-Loop Workflows

GitHub parent issue: #32

Active branch: `feature/p5-qa-review-human-workflows`

Pull request: TBD

Goal: make recovered data inspectable and defensible.

- [x] P5.1 Add overlay generation. Child issue: #33.
- [x] P5.2 Add quality metrics. Child issue: #34.
- [x] P5.3 Add review manifest. Child issue: #35.
- [x] P5.4 Add CLI review commands. Child issue: #36.
- [x] P5.5 Document QA workflow. Child issue: #37.

Status: complete.

## Phase 6: Batch Corpus Pipeline

GitHub parent issue: TBD

Goal: support large technical-document corpora on workstation hardware.

- [ ] P6.1 Add pipeline config. Child issue: TBD.
- [ ] P6.2 Add multiprocessing execution. Child issue: TBD.
- [ ] P6.3 Add artifact layout. Child issue: TBD.
- [ ] P6.4 Add failure recovery. Child issue: TBD.
- [ ] P6.5 Add corpus CLI. Child issue: TBD.

Status: planned.

## Phase 7: FEMIC/FHOPS Integration Adapters

GitHub parent issue: TBD

Goal: make `figrecover` usable as a component in larger FRESH modelling
systems.

- [ ] P7.1 Inspect FEMIC/FHOPS ingestion conventions. Child issue: TBD.
- [ ] P7.2 Add generic modelling export. Child issue: TBD.
- [ ] P7.3 Add FEMIC adapter. Child issue: TBD.
- [ ] P7.4 Add FHOPS adapter. Child issue: TBD.
- [ ] P7.5 Add docs and examples. Child issue: TBD.

Status: planned.

## Phase 8: Documentation, Examples, And Public Alpha

GitHub parent issue: TBD

Goal: make the package usable by external power users.

- [ ] P8.1 Build full Sphinx docs. Child issue: TBD.
- [ ] P8.2 Add examples. Child issue: TBD.
- [ ] P8.3 Add CI and release checks. Child issue: TBD.
- [ ] P8.4 Add release workflow. Child issue: TBD.
- [ ] P8.5 Publish alpha. Child issue: TBD.

Status: planned.

## Phase 9: Scholarly Publication And Peer Review

GitHub parent issue: TBD

Goal: prepare the v1.0.0-ready package for pyOpenSci software peer review,
then JOSS companion paper submission.

- [ ] P9.1 Confirm publication readiness and scope. Child issue: TBD.
- [ ] P9.2 Prepare pyOpenSci review materials. Child issue: TBD.
- [ ] P9.3 Create v1.0.0 release candidate and archive. Child issue: TBD.
- [ ] P9.4 Submit to pyOpenSci and respond to review. Child issue: TBD.
- [ ] P9.5 Prepare and submit JOSS companion paper. Child issue: TBD.
- [ ] P9.6 Complete publication closeout. Child issue: TBD.

Status: planned.
