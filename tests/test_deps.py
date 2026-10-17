"""Tests for pre-flight dependency detection used by ``neurolab run``."""

from pathlib import Path

from neurolab.core import launcher
from neurolab.core.deps import (
    format_missing_report,
    install_hint,
    missing_imports,
    script_imports,
)


def test_script_imports_collects_top_level_modules(tmp_path: Path):
    script = tmp_path / "model.py"
    script.write_text(
        "import math\n"
        "import numpy as np\n"
        "from brian2 import *\n"
        "from neuron import h, gui\n"
        "from .relative import thing\n",
        encoding="utf-8",
    )
    assert script_imports(script) == ["brian2", "math", "neuron", "numpy"]


def test_script_imports_handles_syntax_error(tmp_path: Path):
    script = tmp_path / "broken.py"
    script.write_text("this is not (valid python\n", encoding="utf-8")
    assert script_imports(script) == []


def test_script_imports_handles_missing_file(tmp_path: Path):
    assert script_imports(tmp_path / "nope.py") == []


def test_missing_imports_flags_unknown_module(tmp_path: Path):
    script = tmp_path / "model.py"
    script.write_text("import math\nimport definitely_not_a_real_module_xyz\n", encoding="utf-8")
    assert missing_imports(script) == ["definitely_not_a_real_module_xyz"]


def test_missing_imports_ignores_stdlib(tmp_path: Path):
    script = tmp_path / "model.py"
    script.write_text("import math\nimport json\nfrom pathlib import Path\n", encoding="utf-8")
    assert missing_imports(script) == []


def test_install_hint_maps_known_packages():
    assert install_hint("brian2") == "pip install brian2"
    assert install_hint("torch") == "pip install torch"
    assert install_hint("neuron") == "pip install neuron"


def test_install_hint_falls_back_to_module_name():
    assert install_hint("some_unknown_pkg") == "pip install some_unknown_pkg"


def test_format_missing_report_lists_hints_and_extra(tmp_path: Path):
    report = format_missing_report(tmp_path / "model.py", ["brian2", "numpy"])
    assert "model.py" in report
    assert "pip install brian2" in report
    assert 'pip install -e ".[all]"' in report


def test_format_missing_report_omits_extra_for_non_framework(tmp_path: Path):
    report = format_missing_report(tmp_path / "model.py", ["some_unknown_pkg"])
    assert "pip install some_unknown_pkg" in report
    assert 'pip install -e ".[all]"' not in report


def test_run_script_skips_when_dependencies_missing(tmp_path: Path, monkeypatch, capsys):
    """A missing framework should abort with a hint, not a child traceback."""
    marker = tmp_path / "ran.txt"
    script = tmp_path / "model.py"
    script.write_text(
        "import definitely_not_a_real_module_xyz\n"
        f"open({str(marker)!r}, 'w').write('ran')\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(launcher.sys.stdin, "isatty", lambda: False)
    exit_code = launcher.run_script_interactive(script)

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "not installed" in out
    assert "pip install definitely_not_a_real_module_xyz" in out
    assert not marker.exists()


def test_run_script_proceeds_when_dependencies_present(tmp_path: Path, monkeypatch):
    marker = tmp_path / "ran.txt"
    script = tmp_path / "model.py"
    script.write_text(
        "import math\n"
        f"open({str(marker)!r}, 'w').write('ran')\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(launcher.sys.stdin, "isatty", lambda: False)
    exit_code = launcher.run_script_interactive(script)

    assert exit_code == 0
    assert marker.read_text() == "ran"
