"""Tests for the toolchain diagnostic engine."""

from neurolab.core.doctor import DiagnosticCheck, run_diagnostics


def test_run_diagnostics_returns_checks():
    checks = run_diagnostics()
    assert checks
    assert all(isinstance(c, DiagnosticCheck) for c in checks)


def test_every_check_has_valid_status():
    for check in run_diagnostics():
        assert check.status in {"OK", "WARN", "FAIL"}
        assert check.name
        assert check.category
        assert check.details


def test_python_runtime_always_reported():
    names = {c.name for c in run_diagnostics()}
    assert "Python Runtime" in names
    assert "C/C++ Compiler" in names


def test_neuroscience_frameworks_present_in_report():
    categories = {c.category for c in run_diagnostics()}
    assert "Neuroscience Toolchain" in categories
    assert "Core Scientific Stack" in categories
