# JOSS Exemplar Paper Review

Date: 2026-06-28

Related issue: #65

Branch: `feature/p9-joss-manuscript-draft`

## Purpose

Review a small set of published JOSS papers to align the `figrecover`
manuscript draft with the structure, tone, and level of content commonly used
in accepted software papers.

Downloaded PDFs were stored under ignored local path:

```text
tmp/joss_exemplars/
```

No exemplar PDFs are tracked.

## Exemplars Reviewed

- TextDescriptives: a Python package for corpus metrics.
- PDF Entity Annotation Tool (PEAT): a PDF-native annotation tool.
- RT-utils: a Python library for RT-struct manipulation.
- EMGFlow: a Python package for signal preprocessing and feature extraction.

## Observed Structure

Published JOSS papers generally use:

- concise title and author metadata;
- Summary as the opening section;
- Statement of need with direct comparison to related tools;
- one or more software-description sections such as Features, Functionality,
  Overview, Technical Overview, or Key Features;
- application, limitation, or real-world-example material when relevant;
- Acknowledgements;
- References.

The papers do not read like project plans. They describe present software,
target users, concrete capabilities, and field context. Future work is used
sparingly and only after current functionality is clear.

## Tone Guidance For figrecover

The `figrecover` manuscript should:

- lead with the software purpose, not the roadmap;
- use active, concrete statements about current package capabilities;
- compare against manual chart digitizers, PDF/document tools, and VLM-only
  approaches without overstating novelty;
- include a Features/Functionality-style section;
- include an Applications and limitations section;
- keep TFL 6 as gated deployment evidence until provenance and reuse rights are
  resolved;
- avoid making the paper a user guide;
- avoid claims of fully automatic or exact arbitrary figure recovery.

## Draft Changes Made

- Removed internal draft-comment block from `paper/paper.md`.
- Added a `Functionality` section.
- Added an `Applications and limitations` section.
- Reworked the research-impact language to reduce internal roadmap tone.
- Added a PEAT reference for document/PDF workflow context.
- Kept TFL 6 evidence explicitly gated and absent from results claims.

## Remaining Manuscript Gaps

- Replace lab-level placeholder author metadata.
- Add ORCIDs and final affiliations.
- Add archive DOI and reviewed package version.
- Resolve TFL 6 publication gate before adding case-study results or figures.
- Add JOSS build/check workflow once tooling is available.
- Expand references for chart digitization and VLM chart understanding.
