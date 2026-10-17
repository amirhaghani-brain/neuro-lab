"""Detect missing imports for a script before running it.

Running a model whose framework is not installed used to surface a raw
``ModuleNotFoundError`` traceback. This module parses a script's top-level
imports and reports which ones are not importable, together with an install
hint, so ``neurolab run`` can explain the problem instead of crashing.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List

# Import name -> pip package name, for the frameworks Neuro-Lab knows about.
PACKAGE_HINTS: Dict[str, str] = {
    "brian2": "brian2",
    "neuron": "neuron",
    "hoc": "neuron",
    "nengo": "nengo",
    "nengo_gui": "nengo-gui",
    "snntorch": "snntorch",
    "torch": "torch",
    "neo": "neo",
    "elephant": "elephant",
    "quantities": "quantities",
    "jupyterlab": "jupyterlab",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "scipy": "scipy",
    "sympy": "sympy",
}

# Frameworks that ship with the package's optional "all" extra.
NEURO_FRAMEWORKS = {
    "brian2", "neuron", "nengo", "nengo_gui", "snntorch",
    "neo", "elephant", "jupyterlab",
}


def script_imports(path: Path) -> List[str]:
    """Return the sorted set of top-level modules a script imports."""
    try:
        source = Path(path).read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return []

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                modules.add(node.module.split(".")[0])
    return sorted(modules)


def is_importable(module: str) -> bool:
    if module in sys.builtin_module_names:
        return True
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def missing_imports(path: Path) -> List[str]:
    """Return the modules a script imports that are not importable here."""
    return [m for m in script_imports(path) if not is_importable(m)]


def install_hint(module: str) -> str:
    """Return a ``pip install`` hint for a missing module."""
    package = PACKAGE_HINTS.get(module, module)
    return f"pip install {package}"


def format_missing_report(path: Path, missing: List[str]) -> str:
    """Human-readable, actionable report for missing dependencies."""
    lines = [f"[!] {Path(path).name} needs packages that are not installed:"]
    for module in missing:
        lines.append(f"      - {module}  ->  {install_hint(module)}")
    if any(m in NEURO_FRAMEWORKS for m in missing):
        lines.append('')
        lines.append('    Install the whole neuroscience stack with:  pip install -e ".[all]"')
    return "\n".join(lines)
