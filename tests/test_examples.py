from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_example(script: str, out_dir: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "examples" / script),
            "--out-dir",
            str(out_dir),
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def test_synthetic_chart_extraction_example_runs(tmp_path: Path):
    _run_example("synthetic_chart_extraction.py", tmp_path / "chart")

    assert (tmp_path / "chart" / "synthetic-line-chart.png").exists()
    assert (tmp_path / "chart" / "synthetic-line-chart.json").exists()
    assert (tmp_path / "chart" / "synthetic-line-chart.csv").exists()
    assert (tmp_path / "chart" / "synthetic-line-chart-overlay.png").exists()


def test_mocked_vlm_metadata_example_runs(tmp_path: Path):
    _run_example("mocked_vlm_metadata.py", tmp_path / "vlm")

    assert (tmp_path / "vlm" / "chart-metadata-proposal.json").exists()


def test_synthetic_pdf_corpus_example_runs(tmp_path: Path):
    pytest.importorskip("fitz")

    _run_example("synthetic_pdf_corpus.py", tmp_path / "corpus")

    assert (tmp_path / "corpus" / "synthetic-report.pdf").exists()
    assert (tmp_path / "corpus" / "corpus" / "manifests" / "run-manifest.json").exists()
