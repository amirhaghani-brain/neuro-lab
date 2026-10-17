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


def test_doctor_expands_warnings_below_the_table(capsys):
    from neurolab.cli import cmd_doctor

    checks = [
        DiagnosticCheck(
            name="Brian 2",
            category="Neuroscience Toolchain",
            status="OK",
            version="2.10.1",
            details="ODE spiking neural networks",
        ),
        DiagnosticCheck(
            name="Nengo",
            category="Neuroscience Toolchain",
            status="WARN",
            version=None,
            details="Not installed. Install with `pip install nengo`",
        ),
    ]
    cmd_doctor(checks)
    out = capsys.readouterr().out
    assert "Attention needed:" in out
    assert "pip install nengo" in out
    assert "All checks passed." not in out


def test_doctor_reports_all_clear(capsys):
    from neurolab.cli import cmd_doctor

    checks = [
        DiagnosticCheck(
            name="Brian 2",
            category="Neuroscience Toolchain",
            status="OK",
            version="2.10.1",
            details="ODE spiking neural networks",
        )
    ]
    cmd_doctor(checks)
    out = capsys.readouterr().out
    assert "All checks passed." in out
    assert "Attention needed:" not in out
