# Figrecover Examples

These examples generate their own synthetic inputs and write outputs under
`tmp/examples/` by default. They do not require private PDFs, private recovered
tables, GPU access, or local VLM serving.

Run from the repository root after installing a development checkout:

```bash
python examples/synthetic_chart_extraction.py
python examples/synthetic_pdf_corpus.py
python examples/mocked_vlm_metadata.py
```

The synthetic PDF corpus example requires the optional PDF dependency:

```bash
python -m pip install -e '.[pdf]'
```

Generated example outputs should stay under ignored local directories unless
they are explicitly sanitized for documentation or publication.
