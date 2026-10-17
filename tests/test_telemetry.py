"""Tests for workspace telemetry counting and the daily concept provider."""

from pathlib import Path

from neurolab.core.telemetry import get_daily_concept, get_system_telemetry


def test_model_count_excludes_tests_data_and_notebooks(tmp_path: Path):
    for sub in ("models", "notebooks", "analysis", "tests", "data", "results"):
        (tmp_path / sub).mkdir()

    (tmp_path / "models" / "cortex.py").write_text("from brian2 import *\n", encoding="utf-8")
    (tmp_path / "analysis" / "stats.py").write_text("import neo\n", encoding="utf-8")
    (tmp_path / "sim.py").write_text("import math\n", encoding="utf-8")
    (tmp_path / "tests" / "test_x.py").write_text("import pytest\n", encoding="utf-8")
    (tmp_path / "data" / "helper.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "results" / "generated.py").write_text("y = 2\n", encoding="utf-8")
    (tmp_path / "notebooks" / "exp.ipynb").write_text("{}", encoding="utf-8")

    telemetry = get_system_telemetry(tmp_path)

    assert telemetry["model_count"] == 3
    assert telemetry["notebook_count"] == 1


def test_model_count_zero_for_empty_workspace(tmp_path: Path):
    telemetry = get_system_telemetry(tmp_path)
    assert telemetry["model_count"] == 0
    assert telemetry["notebook_count"] == 0


def test_telemetry_has_expected_keys(tmp_path: Path):
    telemetry = get_system_telemetry(tmp_path)
    for key in (
        "python_version",
        "cuda_status",
        "ram_usage",
        "model_count",
        "notebook_count",
        "workspace",
    ):
        assert key in telemetry


def test_daily_concept_shape():
    concept = get_daily_concept()
    assert set(concept) == {"title", "formula", "desc"}
    assert all(isinstance(v, str) and v for v in concept.values())
