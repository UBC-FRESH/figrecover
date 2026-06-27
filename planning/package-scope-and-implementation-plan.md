# Figrecover Package Scope And Implementation Plan

## Summary

Build `figrecover` as a public UBC-FRESH Python package for recovering approximate source tables from figures in technical PDFs. The core rule is: use deterministic algorithms for numeric extraction whenever feasible, and use local open VLMs as assistants for figure triage, chart metadata, legends, calibration proposals, and QA, not as the default source of numeric truth.

Default project stance:
- Public GitHub repo: `UBC-FRESH/figrecover`
- License: MIT, matching `modelwright`, unless a dependency forces stricter isolation
- Python: `>=3.11`
- Package layout: `src/figrecover`
- CLI: Typer/Rich, thin wrappers over Python APIs
- Docs: Sphinx user guide plus API docstrings before phase closeout
- Workflow: one branch, parent issue, PR, and closeout note per phase

## Roadmap Workflow

Every phase uses:
- Parent GitHub issue: phase scope, branch name, child issue checklist, PR link at closeout
- Child GitHub issue per task
- Child issue body checklist items for subtasks
- Branch name: `feature/p{N}-{short-slug}`
- PR merge to `main` only after task issues, tests, docs, roadmap, changelog, and closeout note are synchronized
- Tracked planning notes under `planning/`; ignored experiments and private PDFs under `tmp/`

Initial repo governance files:
- `AGENTS.md`: agent workflow, private-data hygiene, extraction-quality principles
- `ROADMAP.md`: phase/task/issue map
- `CHANGE_LOG.md`: dated narrative
- `CONTRIBUTING.md`: local dev, issue/branch/PR rules
- `planning/README.md`: evidence-oriented design note rules

## Phase Plan

### Phase 0: Governance And Public Repo Bootstrap

Goal: establish the open-source repo contract before expanding code.

Tasks:
- P0.1 Create repo governance skeleton
  - Add `README.md`, `AGENTS.md`, `ROADMAP.md`, `CHANGE_LOG.md`, `CONTRIBUTING.md`, `LICENSE`, `.gitignore`
  - Record public/open-source stance and private-document hygiene
  - Define phase/task/subtask issue workflow
- P0.2 Normalize package metadata
  - Use `setuptools`, `src/` layout, MIT metadata, project URLs, classifiers, optional extras
  - Keep heavy dependencies out of default install
  - Add `tmp/`, build artifacts, cache dirs, and local PDF/output dirs to `.gitignore`
- P0.3 Preserve current scaffold as bootstrap seed
  - Keep the existing calibration and colour-based digitizer code only as early core
  - Move any broad claims in README into “current status” and “roadmap”
  - Verify `python -m pytest`
- P0.4 Create initial GitHub issues
  - Parent issue for Phase 0
  - Child issues P0.1-P0.3
  - Placeholder parent issues for near-term phases only

Acceptance: clean public repo skeleton, working tests, synchronized roadmap/changelog/issues, no private PDFs or generated data tracked.

### Phase 1: Architecture And Dependency Research

Goal: decide the package boundaries before adding more features.

Tasks:
- P1.1 Survey reusable open software
  - Evaluate Docling, MinerU, Surya, PyMuPDF, OpenCV/scikit-image, pytesseract/EasyOCR if useful, WebPlotDigitizer concepts, PlotDigitizer concepts, Qwen/GLM/InternVL-style local VLM backends
  - Record license, install weight, GPU needs, API maturity, and fit
  - Avoid embedding AGPL or service-only components in the MIT core
- P1.2 Define pipeline architecture
  - Separate document ingestion, figure candidates, chart metadata, calibration, extraction, QA, export, and integration adapters
  - Define which components are deterministic core versus optional assistive/model backends
  - Record failure modes and unsupported chart classes
- P1.3 Define data/provenance contract
  - JSON-serializable records for source document, page, crop, figure, chart metadata, axis calibration, recovered series, diagnostics, and extraction run
  - Include model/tool version fields and confidence fields
  - Define CSV/Parquet/JSON export expectations
- P1.4 Close architecture phase
  - Write `planning/architecture-contract.md`
  - Update README roadmap and docs stub
  - Confirm next implementation phase inputs

Acceptance: no major implementation beyond documentation/contracts; the implementer knows the module boundaries and dependency policy.

### Phase 2: Core Records, Calibration, And Extraction API

Goal: build the durable Python API for calibrated image-level extraction.

Public API additions:
- `figrecover.records`: typed records for documents, figures, charts, axes, calibration, series, points, diagnostics, exports
- `figrecover.calibration`: pixel/data transforms, linear/log axes, manual calibration, calibration proposals
- `figrecover.extraction`: extractor interfaces and deterministic image extractors
- `figrecover.io`: JSON/CSV/Parquet export helpers

Tasks:
- P2.1 Stabilize record model
  - Replace ad hoc early models with durable Pydantic records
  - Add provenance fields for source PDF/page/crop and extraction toolchain
  - Keep records JSON-friendly and documented
- P2.2 Implement calibrated extraction core
  - Line series by colour mask and skeleton/median sampling
  - Scatter series by connected components
  - Bar charts by component/run detection and baseline handling
  - Linear and log axis transforms
- P2.3 Add extraction diagnostics
  - No-match, low-confidence, clipped-to-plot, ambiguous-components, calibration-missing, unsupported-chart diagnostics
  - Include enough context for downstream QA
- P2.4 Add focused synthetic tests
  - Generated line, scatter, bar, multi-series, log-axis, noisy image cases
  - Assert numeric tolerances and diagnostic stability
- P2.5 Add API docstrings and first Sphinx reference pages
  - Document manual image-crop workflow
  - Include one Python API example and one CLI example

Acceptance: `python -m pytest` covers deterministic extraction; public records and functions have docstrings; docs build locally.

### Phase 3: Document Ingestion And Figure Cropping

Goal: turn PDFs into auditable figure candidates without requiring VLMs.

Public API additions:
- `figrecover.documents.render_pdf_pages`
- `figrecover.documents.extract_figure_candidates`
- `figrecover.manifest.FigureManifest`

Tasks:
- P3.1 Add PDF rendering
  - Use PyMuPDF optional extra
  - Render selected pages or whole PDFs at configurable DPI
  - Record render DPI and page image dimensions
- P3.2 Add figure candidate manifest
  - Store page, bbox, image path, caption text if available, parser source, confidence
  - Support manual manifests first
  - Export/import JSONL for batch workflows
- P3.3 Add parser adapters behind extras
  - Add Docling adapter if API fit is acceptable
  - Add MinerU/Surya notes or adapters only if local install/API proves worthwhile
  - Keep adapters optional and isolated
- P3.4 Add CLI commands
  - `figrecover pdf render`
  - `figrecover figures list`
  - `figrecover figures crop`
  - Commands emit JSON summaries and write artifacts under user-selected output dirs
- P3.5 Test with synthetic PDFs
  - Generated PDF pages with known charts and captions
  - No private technical documents in tracked tests

Acceptance: batch PDF-to-crop workflow works without VLMs; manifests preserve provenance; CLI remains thin over Python APIs.

### Phase 4: Local VLM Assistance Layer

Goal: use local open VLMs for chart understanding while keeping numeric extraction auditable.

Public API additions:
- `figrecover.vlm.ChartTriageRequest/Result`
- `figrecover.vlm.CalibrationProposal`
- `figrecover.vlm.LegendProposal`
- Backend protocol: `describe_chart(image, context) -> ChartMetadataProposal`

Tasks:
- P4.1 Define VLM boundary
  - Backends are optional extras
  - VLM outputs are proposals, never authoritative recovered data by default
  - All prompts, model names, versions, and raw structured responses are recorded
- P4.2 Add local backend interface
  - Start with an OpenAI-compatible local HTTP endpoint contract for vLLM/llama.cpp-style serving where possible
  - Add direct Transformers backend only if install complexity is manageable
  - Support Qwen/GLM/InternVL-family models through adapters, not hard dependencies
- P4.3 Add structured prompt templates
  - Chart type, axis labels, legend, series colours, tick labels, calibration hints, data-quality warnings
  - JSON schema validation and repair diagnostics
- P4.4 Add self-ensemble utilities
  - Run multiple VLM passes for metadata proposals
  - Aggregate categorical fields and flag disagreements
  - Do not average numeric data tables as a substitute for calibrated extraction unless explicitly requested
- P4.5 Add GPU/system docs
  - Document expected workstation profile
  - Document local model serving examples
  - State that Codex sandbox GPU checks may differ from user shell availability

Acceptance: VLM layer can propose chart metadata and calibration hints; deterministic extraction still owns numeric output unless user opts into VLM-only experimental mode.

### Phase 5: QA, Review, And Human-In-The-Loop Workflows

Goal: make recovered data inspectable and defensible.

Public API additions:
- `figrecover.qa`: overlay rendering, residual checks, confidence summaries
- `figrecover.review`: review manifests and accepted/rejected corrections

Tasks:
- P5.1 Add overlay generation
  - Render recovered points/lines/bars over source crops
  - Include calibration frame and series colours
  - Write PNG artifacts for review
- P5.2 Add quality metrics
  - Pixel coverage, extraction density, component counts, calibration residuals, axis consistency, VLM disagreement
  - Per-series and per-figure confidence summaries
- P5.3 Add review manifest
  - Allow accepted, rejected, manually corrected, needs-recrop, needs-recalibration statuses
  - Preserve correction provenance
- P5.4 Add CLI review commands
  - Generate review bundle
  - Summarize failures and low-confidence extractions
  - Export accepted tables only
- P5.5 Document QA workflow
  - User guide for power-user batch review
  - Explain how not to over-trust recovered values

Acceptance: users can audit each recovered table visually and programmatically before using it as model input.

### Phase 6: Batch Corpus Pipeline

Goal: support large technical-document corpora on workstation hardware.

Public API additions:
- `figrecover.pipeline.CorpusRunConfig`
- `figrecover.pipeline.run_corpus`
- `figrecover.pipeline.RunManifest`

Tasks:
- P6.1 Add pipeline config
  - Input PDFs, output root, DPI, parser backend, VLM backend, extraction modes, worker counts
  - YAML and JSON config loading
- P6.2 Add multiprocessing execution
  - CPU-parallel rendering/cropping/extraction
  - GPU work queued separately for VLM calls
  - Resume from manifest and skip completed artifacts
- P6.3 Add artifact layout
  - `pages/`, `crops/`, `overlays/`, `tables/`, `manifests/`, `logs/`
  - Stable filenames derived from document/page/figure IDs
- P6.4 Add failure recovery
  - Continue on individual PDF/page/figure failure
  - Emit structured diagnostics and run summary
- P6.5 Add corpus CLI
  - `figrecover corpus init`
  - `figrecover corpus run`
  - `figrecover corpus summarize`
  - `figrecover corpus export`

Acceptance: a user can process a directory of PDFs into manifests, crops, overlays, and recovered tables with resumable runs.

### Phase 7: FEMIC/FHOPS Integration Adapters

Goal: make `figrecover` usable as a component in larger FRESH modelling systems.

Public API additions:
- `figrecover.integrations.femic`
- `figrecover.integrations.fhops`
- Stable export contracts for model metadata ingestion

Tasks:
- P7.1 Inspect FEMIC/FHOPS ingestion conventions
  - Use local clones as source of truth
  - Identify expected metadata/provenance patterns
  - Keep integrations optional and lightweight
- P7.2 Add generic modelling export
  - Long table format with document, page, figure, series, x, y, units, confidence, provenance
  - Include JSON sidecar for calibration and diagnostics
- P7.3 Add FEMIC adapter
  - Target TSR/forest-management-plan figure recovery use cases
  - Preserve source-document provenance for downstream audit
- P7.4 Add FHOPS adapter
  - Target productivity/cost/regression/reference-document digitisation use cases
  - Preserve method and confidence metadata
- P7.5 Add docs and examples
  - Use synthetic or public-safe fixtures only
  - No private forestry PDFs tracked

Acceptance: FEMIC/FHOPS can call `figrecover` as a library or consume its exported tables without knowing internal extraction details.

### Phase 8: Documentation, Examples, And Public Alpha

Goal: make the package usable by external power users.

Tasks:
- P8.1 Build full Sphinx docs
  - Quickstart
  - Manual calibrated extraction
  - PDF corpus workflow
  - VLM-assisted workflow
  - QA/review workflow
  - API reference
  - CLI reference
- P8.2 Add examples
  - Synthetic chart notebook/script
  - Synthetic PDF corpus example
  - Local VLM metadata example with backend mocked if model unavailable
- P8.3 Add CI and release checks
  - Pytest, ruff, docs build
  - No GPU or private PDF requirements in default CI
  - Optional marked tests for local GPU/VLM
- P8.4 Add release workflow
  - Build artifacts
  - Twine check
  - TestPyPI rehearsal
  - Maintainer-gated real PyPI release
- P8.5 Publish alpha
  - Version `0.1.0a1`
  - Clear limitations and unsupported chart classes
  - No claim of fully automatic precise recovery

Acceptance: public alpha can be installed, documented, tested, and cited as experimental software.

### Phase 9: Scholarly Publication And Peer Review

Goal: prepare the v1.0.0-ready package for pyOpenSci software peer review, then JOSS companion paper submission.

Tasks:
- P9.1 Confirm publication readiness and scope
  - Verify package is public, OSI/MIT licensed, installable, documented, tested, and actively maintained
  - Confirm pyOpenSci scope fit as scientific workflow/data processing software
  - Confirm JOSS scope fit as research software with credible scholarly significance, not a one-off utility
- P9.2 Prepare pyOpenSci review materials
  - Audit README for statement of need, installation, quickstart, badges, community guidelines, metadata, and supported Python/package versions
  - Ensure docs include quickstart, API reference, CLI reference, examples, corpus workflow, QA workflow, and publication-safe examples
  - Prepare pyOpenSci submission metadata: submitting author, maintainers, package name, one-line description, repository, docs URL, version submitted, archive/DOI, and maintenance commitment
  - Include response plan for review issues and reviewer feedback
- P9.3 Create v1.0.0 release candidate and archive
  - Cut a v1.0.0 release candidate after all functional, docs, CI, packaging, and review-readiness checks pass
  - Publish final v1.0.0 to PyPI
  - Create a GitHub release and Zenodo/archive DOI for the reviewed version
  - Verify source distribution and wheel install cleanly from PyPI
- P9.4 Submit to pyOpenSci and respond to review
  - Open a pyOpenSci software-review issue using their submission template
  - Track pyOpenSci review feedback as linked GitHub issues/PRs in `UBC-FRESH/figrecover`
  - Keep roadmap, changelog, docs, and release notes synchronized through review revisions
  - Add pyOpenSci badge after acceptance
- P9.5 Prepare and submit JOSS companion paper
  - Add `paper/paper.md`, `paper/paper.bib`, and any publication-safe figures
  - Paper sections must cover Summary, Statement of need, State of the field, Software design, Research impact statement, AI usage disclosure, Acknowledgements, and References
  - Keep the paper focused on software purpose, design, need, field context, and research impact; keep API details in package docs
  - Submit to JOSS after pyOpenSci acceptance and link the accepted pyOpenSci review for fast-track handling
- P9.6 Complete publication closeout
  - Add JOSS DOI and citation metadata after acceptance
  - Add pyOpenSci and JOSS badges to README
  - Add `CITATION.cff` or update it if already present
  - Update docs with citation instructions
  - Close Phase 9 with PR, changelog entry, release links, pyOpenSci review link, JOSS paper link, and DOI links

Acceptance: `figrecover` has passed pyOpenSci review, has a submitted or accepted JOSS companion paper, records citation metadata and badges, and preserves a clean public release/archive trail for the reviewed v1.0.0 package.

## Dependency Policy

Default runtime dependencies:
- `numpy`, `pandas`, `pydantic`, `pillow`, `typer`, `rich`

Optional extras:
- `pdf`: PyMuPDF, pypdf
- `cv`: OpenCV headless, scikit-image, scipy
- `docs`: Sphinx, sphinx-rtd-theme
- `vlm`: backend client dependencies only after Phase 4 decisions
- `dev`: pytest, ruff, build, twine, docs tools

Rules:
- Prefer permissive dependencies in the core package.
- Do not make Docling/MinerU/Surya/VLM stacks default installs.
- Do not vendor or embed AGPL components in the MIT core.
- Treat model weights separately from package licensing; document any non-OSI model-license caveats.

## Testing Strategy

Default tests:
- Synthetic image fixtures generated in tests
- Calibration roundtrips
- Line/scatter/bar extraction accuracy within explicit tolerances
- JSON serialization compatibility
- CLI smoke tests
- PDF rendering/cropping tests using generated PDFs once PDF extra is introduced
- Docs build before phase closeout once docs exist

Optional/local tests:
- Large corpus smoke tests under ignored `tmp/`
- GPU/VLM tests marked and skipped unless explicitly enabled
- Private FEMIC/FHOPS document evaluations recorded only as sanitized planning notes

## Assumptions

- Start from the existing local `figrecover` scaffold, but treat it as Phase 0 seed code rather than a settled architecture.
- Use MIT license unless UBC-FRESH policy requires another permissive license.
- Optimize for workstation-class users first: many CPU cores, high RAM, pro GPU, local model serving.
- Keep CLI JSON-friendly and thin over Python APIs, following `modelwright`.
- Prioritize auditable approximate recovery over “fully automatic” claims.
- Use VLMs to reduce manual labour, not to replace deterministic coordinate extraction when real algorithms work.
