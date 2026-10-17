"""Tests for the Click CLI surface."""

from pathlib import Path

from click.testing import CliRunner

from neurolab.cli import main


def test_help_lists_commands():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("doctor", "list", "find", "new", "run", "tui", "shell"):
        assert command in result.output


def test_version_flag_reports_package_version():
    from neurolab import __version__

    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


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


def test_run_missing_dependency_exits_nonzero(workspace: Path):
    (workspace / "models" / "needs_missing.py").write_text(
        "import definitely_not_a_real_module_xyz\n", encoding="utf-8"
    )
    result = CliRunner().invoke(main, ["-w", str(workspace), "run", "needs_missing.py"])
    assert result.exit_code != 0
    assert "not installed" in result.output
    assert "pip install definitely_not_a_real_module_xyz" in result.output


def test_run_unknown_file_exits_nonzero(workspace: Path):
    result = CliRunner().invoke(main, ["-w", str(workspace), "run", "ghost.py"])
    assert result.exit_code != 0
    assert "File not found" in result.output


def test_run_executes_script_with_deps_present(workspace: Path):
    (workspace / "models" / "ok.py").write_text(
        "import math\nprint('ran ok', math.floor(1.5))\n", encoding="utf-8"
    )
    result = CliRunner().invoke(main, ["-w", str(workspace), "run", "ok.py"])
    assert result.exit_code == 0
    # The child's stdout streams to the real terminal, so assert on the wrapper.
    assert "RUNNING ok.py" in result.output
    assert "Exit code 0" in result.output
