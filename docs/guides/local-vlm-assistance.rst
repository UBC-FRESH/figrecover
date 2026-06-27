Local VLM Assistance
====================

``figrecover`` can use local vision-language models to propose chart metadata.
These proposals can reduce manual triage work, but they are not authoritative
recovered data. Deterministic calibration and extraction remain the preferred
numeric path whenever they are feasible.

Optional Install
----------------

The core package does not require VLM dependencies. Install the optional VLM
client dependencies only in environments that will call local model servers:

.. code-block:: bash

   python -m pip install "figrecover[vlm]"

Model weights and model-serving tools are not bundled with ``figrecover``.
Model licenses are separate from the package license and should be reviewed for
each local model a user chooses to run.

Expected Workstation Profile
----------------------------

The VLM layer is designed first for workstation-class users who can run open
models locally. A useful setup typically includes:

* a modern NVIDIA GPU with enough VRAM for the selected VLM;
* enough system RAM to handle rendered pages, crops, prompts, and raw responses;
* CPU capacity for rendering, cropping, deterministic extraction, and batch
  orchestration;
* a local OpenAI-compatible HTTP endpoint for model serving.

Default tests and default package use do not require GPU access, model weights,
or a running model server.

Local Endpoint Contract
-----------------------

The first backend boundary targets OpenAI-compatible local HTTP servers. The
backend sends a chat-completions request containing prompt text and a prepared
figure image. The model is expected to return a JSON object that can validate
as a chart metadata proposal.

Example Python usage with a local endpoint:

.. code-block:: python

   from pathlib import Path

   from figrecover.vlm import (
       ChartTriageRequest,
       OpenAICompatibleBackendConfig,
       OpenAICompatibleVLMBackend,
   )

   backend = OpenAICompatibleVLMBackend(
       OpenAICompatibleBackendConfig(
           model="local-vlm-name",
           base_url="http://127.0.0.1:8000/v1",
           temperature=0.0,
       )
   )

   result = backend.describe_chart(
       ChartTriageRequest(
           request_id="crop-001-triage",
           image_path=Path("tmp/crops/crop-001.png"),
           context={"caption": "Figure 1. Harvest forecast."},
       )
   )

   proposal = result.proposal
   diagnostics = result.diagnostics

The response record preserves backend metadata, prompt provenance, raw response
text, parsed JSON, proposal fields, and diagnostics.

Proposal Boundary
-----------------

VLM outputs are stored as proposals:

* chart type;
* chart title;
* axis labels, units, scale, and tick labels;
* legend entries;
* series colours;
* calibration hints;
* data-quality warnings.

These values should be reviewed or validated before use. They should guide
deterministic extraction and QA; they should not silently replace calibrated
coordinate recovery.

Self-Ensemble Use
-----------------

Repeated VLM calls can be summarized with self-ensemble utilities. The ensemble
summary reports agreement and disagreement for metadata fields and flags fields
that need review. It does not average recovered numeric data tables as a
default behavior.

Private-Data Hygiene
--------------------

Prompts, crops, raw responses, parsed JSON, logs, and review bundles may contain
private source-document content. Keep them under ignored local directories such
as ``tmp/`` unless a sanitized artifact is explicitly approved for tracking.

Do not commit:

* private source PDFs;
* rendered pages or crops from private documents;
* prompt transcripts from private documents;
* raw model responses containing private context;
* recovered private data tables.

GPU Visibility Caveat
---------------------

GPU visibility can differ between an interactive user shell, a container, a
Jupyter service, and an AI coding-agent sandbox. A successful ``nvidia-smi`` in
one context does not guarantee the same visibility from every process. Treat
package tests and docs as GPU-independent; diagnose local model-serving issues
in the user-controlled runtime environment.
