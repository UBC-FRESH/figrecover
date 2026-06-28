Statement Of Need
=================

Scientific and professional technical documents often publish figures without
the original source tables used to generate them. Those figures may still
contain useful quantitative evidence for modelling, review, meta-analysis, or
historical reconstruction, but copying approximate values by hand is slow,
inconsistent, and hard to audit.

``figrecover`` addresses this gap by providing an open Python workflow for
recovering approximate tabular data from chart images while preserving
provenance, calibration decisions, diagnostics, and review status. The package
is designed for power users who need repeatable recovery workflows across
technical PDFs, not for silent fully automatic reconstruction.

The core design principle is conservative: deterministic algorithms should own
numeric extraction whenever they can work. Optional local VLMs can propose chart
metadata, legend entries, axis labels, series colours, and calibration hints,
but those proposals are not authoritative recovered data by default.

The intended use cases include:

* recovering modelling metadata from historical technical reports;
* extracting approximate line, scatter, bar, or simple area-chart values from
  prepared figure crops;
* reviewing recovered values with overlays and diagnostics before downstream
  use;
* processing larger PDF corpora into auditable page, crop, result, and review
  artifacts;
* exporting accepted recovered values into modelling workflows such as FEMIC
  and FHOPS.

``figrecover`` should be understood as data recovery and evidence management
software. It does not recreate hidden source tables perfectly, and it does not
make arbitrary PDF-to-table recovery automatic. Its purpose is to make the
recoverable portion of figure-derived data explicit, reviewable, and reusable.
