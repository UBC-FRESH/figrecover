API Stability
=============

``figrecover`` is currently alpha software. The public API is usable, tested,
and documented, but it is not yet guaranteed stable.

Current Stable-Enough Surfaces
------------------------------

The following surfaces are intended to remain coherent during alpha
development, with changes documented in ``CHANGE_LOG.md``:

* calibrated image extraction records and functions;
* PDF rendering and figure manifest helpers;
* QA overlay and review manifest workflows;
* corpus configuration and run manifests;
* VLM proposal records and local backend boundary;
* generic, FEMIC, and FHOPS export helpers;
* Typer CLI command groups.

Experimental Surfaces
---------------------

The following areas may change more substantially before v1.0.0:

* parser adapter details;
* VLM prompt templates and ensemble heuristics;
* unsupported or partial chart-class handling;
* corpus orchestration internals;
* future TFL 6 case-study workflow conventions;
* publication/review metadata.

Deprecation Policy Target
-------------------------

Before v1.0.0, the project should define:

* which modules and record fields are stable public API;
* how long deprecated CLI commands, function arguments, and record fields are
  retained;
* how migrations are documented;
* how serialization compatibility is tested.

Until that policy exists, users should pin exact package versions for
reproducible work.
