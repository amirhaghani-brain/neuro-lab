"""Tests for the Click CLI surface."""

from pathlib import Path

from click.testing import CliRunner

from neurolab.cli import main


def test_help_lists_commands():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("doctor", "list", "find", "new", "run", "tui", "shell"):
        assert command in result.output


def test_list_shows_registry(workspace: Path):
    (workspace / "models" / "cortex.py").write_text(
        "from brian2 import *\n", encoding="utf-8"
    )
    result = CliRunner().invoke(main, ["-w", str(workspace), "list"])
    assert result.exit_code == 0
    assert "Workspace File Registry" in result.output
    assert "cortex.py" in result.output


def test_new_scaffolds_template(workspace: Path):
    result = CliRunner().invoke(
        main, ["-w", str(workspace), "new", "brian2", "demo"]
    )
    assert result.exit_code == 0
    assert (workspace / "models" / "demo.py").exists()


def test_new_rejects_unknown_tool(workspace: Path):
    result = CliRunner().invoke(
        main, ["-w", str(workspace), "new", "not-a-tool", "x"]
    )
    assert result.exit_code != 0


def test_doctor_runs():
    result = CliRunner().invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "Toolchain Diagnostics" in result.output
