"""Workspace management, file discovery, and template instantiation."""

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set


@dataclass
class ToolDefinition:
    id: str
    name: str
    description: str
    target_dir: str
    extensions: List[str]
    template_name: str
    tag: str
    color: str
    default_filename: str


TOOLS: Dict[str, ToolDefinition] = {
    "jupyter": ToolDefinition(
        id="jupyter",
        name="JupyterLab",
        description="Interactive computational neuroscience notebooks and data exploration",
        target_dir="notebooks",
        extensions=[".ipynb"],
        template_name="jupyter_starter.ipynb",
        tag="jupyter",
        color="#f0883e",
        default_filename="experiment_01.ipynb"
    ),
    "brian2": ToolDefinition(
        id="brian2",
        name="Brian 2",
        description="ODE-based spiking neural network modeling & point biophysics",
        target_dir="models",
        extensions=[".py"],
        template_name="brian2_lif.py",
        tag="brian2",
        color="#58a6ff",
        default_filename="brian2_model.py"
    ),
    "neuron": ToolDefinition(
        id="neuron",
        name="NEURON",
        description="Detailed multicompartment morphology and 3D cable biophysics",
        target_dir="models",
        extensions=[".py", ".hoc", ".mod"],
        template_name="neuron_soma.py",
        tag="neuron",
        color="#3fb950",
        default_filename="neuron_cell.py"
    ),
    "nengo": ToolDefinition(
        id="nengo",
        name="Nengo & GUI",
        description="Large-scale cognitive architectures & Neural Engineering Framework",
        target_dir="models",
        extensions=[".py"],
        template_name="nengo_network.py",
        tag="nengo",
        color="#bc8cff",
        default_filename="nengo_circuit.py"
    ),
    "snntorch": ToolDefinition(
        id="snntorch",
        name="snnTorch",
        description="Deep spiking neural networks trained with PyTorch & surrogate gradients",
        target_dir="models",
        extensions=[".py"],
        template_name="snntorch_model.py",
        tag="snntorch",
        color="#f85149",
        default_filename="snn_classifier.py"
    ),
    "neo": ToolDefinition(
        id="neo",
        name="Neo / Elephant",
        description="Electrophysiology data analysis, spike trains, PSTH, and ISI metrics",
        target_dir="analysis",
        extensions=[".py"],
        template_name="neo_analysis.py",
        tag="neo",
        color="#e3b341",
        default_filename="electrophys_analysis.py"
    ),
}


def get_templates_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "templates"


# Directories that never contain user models and must be skipped during scans.
IGNORED_DIRS = {
    ".venv", "venv", ".git", "__pycache__", ".pytest_cache", ".mypy_cache",
    "src", "build", "dist", "egg-info", ".eggs", ".gemini", ".ipynb_checkpoints",
}

# Import signatures used to attribute a Python script in a *shared* target
# directory (e.g. models/ is shared by Brian 2, NEURON, Nengo and snnTorch) to
# the framework it actually uses, instead of reporting it under every toolchain.
TOOL_IMPORT_SIGNATURES: Dict[str, tuple] = {
    "brian2": (r"\bfrom\s+brian2\b", r"\bimport\s+brian2\b"),
    "neuron": (
        r"\bfrom\s+neuron\b",
        r"\bimport\s+neuron\b",
        r"\bfrom\s+hoc\b",
        r"\bimport\s+hoc\b",
    ),
    "nengo": (r"\bfrom\s+nengo\b", r"\bimport\s+nengo\b"),
    "snntorch": (r"\bfrom\s+snntorch\b", r"\bimport\s+snntorch\b"),
    "neo": (
        r"\bfrom\s+neo\b",
        r"\bimport\s+neo\b",
        r"\bfrom\s+elephant\b",
        r"\bimport\s+elephant\b",
    ),
}

# How many bytes of a script to read when sniffing imports.
_CLASSIFY_HEAD_BYTES = 8192


def classify_python_source(text: str) -> Set[str]:
    """Return the set of tool ids whose framework the given source imports."""
    owners: Set[str] = set()
    for tool_id, patterns in TOOL_IMPORT_SIGNATURES.items():
        for pattern in patterns:
            if re.search(pattern, text):
                owners.add(tool_id)
                break
    return owners


def classify_python_file(path: Path) -> Set[str]:
    """Read the head of a Python file and classify it by framework imports."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            head = handle.read(_CLASSIFY_HEAD_BYTES)
    except OSError:
        return set()
    return classify_python_source(head)


def _shared_py_target_dirs() -> Dict[str, int]:
    """Count how many tools scan .py files inside each target directory."""
    counts: Dict[str, int] = {}
    for tool in TOOLS.values():
        if ".py" in tool.extensions:
            counts[tool.target_dir] = counts.get(tool.target_dir, 0) + 1
    return counts


def list_tool_files(
    tool_id: str,
    workspace: Path,
    include_unclassified: bool = True,
) -> List[Path]:
    """Find files belonging to a tool inside its target directory.

    Unlike a naive glob this never scans the workspace root, so top-level
    scripts are not attributed to every toolchain. When a target directory is
    shared by several Python frameworks (``models/``), files are attributed by
    their imports; scripts that match no framework are only returned when
    ``include_unclassified`` is true.
    """
    if tool_id not in TOOLS:
        return []

    tool = TOOLS[tool_id]
    target_path = workspace / tool.target_dir
    if not target_path.exists():
        return []

    shared_py = _shared_py_target_dirs().get(tool.target_dir, 0) > 1
    results: List[Path] = []
    seen: Set[Path] = set()

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [
            d for d in dirs
            if d not in IGNORED_DIRS and not d.endswith(".egg-info")
        ]
        for name in files:
            if name.startswith("."):
                continue
            ext = Path(name).suffix.lower()
            if ext not in tool.extensions:
                continue

            full_path = Path(root) / name
            if full_path in seen:
                continue

            if ext == ".py" and shared_py:
                owners = classify_python_file(full_path)
                if owners:
                    if tool_id not in owners:
                        continue
                elif not include_unclassified:
                    continue

            seen.add(full_path)
            results.append(full_path)

    results.sort(
        key=lambda p: str(p.relative_to(workspace) if p.is_relative_to(workspace) else p)
    )
    return results


def list_root_scripts(workspace: Path) -> List[Path]:
    """Return Python scripts sitting directly in the workspace root."""
    if not workspace.exists():
        return []
    scripts = [
        p for p in workspace.iterdir()
        if p.is_file() and p.suffix.lower() == ".py" and not p.name.startswith(".")
    ]
    scripts.sort(key=lambda p: p.name)
    return scripts


def list_workspace_registry(workspace: Path) -> Dict[str, List[Path]]:
    """Group workspace files by owning tool for display.

    Keys are tool ids, plus two pseudo-groups: ``"unclassified"`` for Python
    files in a shared directory that import no known framework, and ``"root"``
    for scripts sitting directly in the workspace root. Every file appears at
    most once, so the registry never double-counts.
    """
    registry: Dict[str, List[Path]] = {}
    claimed: Set[Path] = set()

    def _sort(paths: List[Path]) -> List[Path]:
        return sorted(
            paths,
            key=lambda p: str(p.relative_to(workspace) if p.is_relative_to(workspace) else p),
        )

    # Files that positively match a toolchain (by extension or imports).
    for tool_id in TOOLS:
        files = list_tool_files(tool_id, workspace, include_unclassified=False)
        fresh = [f for f in files if f not in claimed]
        for f in fresh:
            claimed.add(f)
        if fresh:
            registry[tool_id] = _sort(fresh)

    # Python files in shared directories that match no known framework.
    unclassified: List[Path] = []
    for target_dir, count in _shared_py_target_dirs().items():
        if count <= 1:
            continue
        base = workspace / target_dir
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [
                d for d in dirs
                if d not in IGNORED_DIRS and not d.endswith(".egg-info")
            ]
            for name in files:
                if name.startswith(".") or Path(name).suffix.lower() != ".py":
                    continue
                full_path = Path(root) / name
                if full_path in claimed:
                    continue
                if not classify_python_file(full_path):
                    unclassified.append(full_path)
                    claimed.add(full_path)
    if unclassified:
        registry["unclassified"] = _sort(unclassified)

    root_scripts = list_root_scripts(workspace)
    if root_scripts:
        registry["root"] = root_scripts

    return registry


def resolve_workspace_root() -> Path:
    # 1. Environment variable if set
    env_root = os.environ.get("NEUROLAB_WORKSPACE")
    if env_root and Path(env_root).exists():
        return Path(env_root).resolve()
    
    # 2. Current working directory if contains workspace markers or src
    cwd = Path.cwd()
    if (cwd / "models").exists() or (cwd / "notebooks").exists() or (cwd / "pyproject.toml").exists():
        return cwd.resolve()
    
    # 3. Default to ~/neuro-lab
    default_path = Path.home() / "neuro-lab"
    if default_path.exists():
        return default_path.resolve()
        
    return cwd.resolve()


def ensure_workspace_dirs(workspace: Path):
    """Ensure standard workspace folders exist."""
    for folder in ["models", "notebooks", "data", "analysis", "results"]:
        (workspace / folder).mkdir(parents=True, exist_ok=True)


def create_file_from_template(tool_id: str, filename: str, workspace: Path) -> Path:
    """Create a new file populated with the standard template."""
    tool = TOOLS[tool_id]
    ensure_workspace_dirs(workspace)

    # Ensure appropriate extension
    target_ext = tool.extensions[0]
    if not any(filename.endswith(ext) for ext in tool.extensions):
        filename = f"{filename}{target_ext}"

    dest_dir = workspace / tool.target_dir
    dest_path = dest_dir / filename

    # Avoid accidental overwrite if file exists by finding unused name
    base_name = dest_path.stem
    counter = 1
    while dest_path.exists():
        dest_path = dest_dir / f"{base_name}_{counter}{target_ext}"
        counter += 1

    template_file = get_templates_dir() / tool.template_name
    if template_file.exists():
        shutil.copy2(template_file, dest_path)
    else:
        # Fallback to empty file if template missing
        dest_path.write_text(f"# {tool.name} Script\n# Created with Neuro-Lab\n", encoding="utf-8")

    return dest_path


def find_all_workspace_files(workspace: Path, query: str = "") -> List[Path]:
    """Find all files in workspace matching an optional query string."""
    results = []

    if not workspace.exists():
        return []

    query_lower = query.lower().strip()
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.endswith(".egg-info")]
        for file in files:
            if file.startswith("."):
                continue
            full_path = Path(root) / file
            if not query_lower or query_lower in file.lower() or query_lower in str(full_path).lower():
                results.append(full_path)

    results.sort(key=lambda p: str(p.relative_to(workspace) if p.is_relative_to(workspace) else p))
    return results


def discover_projects() -> List[Path]:
    """Discover potential computational neuroscience workspaces on system."""
    discovered = []
    seen = set()

    search_roots = [Path.home(), Path.home() / "Work", Path.cwd()]
    for search_root in search_roots:
        if not search_root.exists():
            continue
        # Direct check
        if (search_root / "models").exists() or (search_root / "notebooks").exists():
            if search_root.resolve() not in seen:
                seen.add(search_root.resolve())
                discovered.append(search_root.resolve())
        # Check subdirectories 1 level deep
        try:
            for item in search_root.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    if (item / "models").exists() or (item / "notebooks").exists() or (item / "sim.py").exists():
                        resolved = item.resolve()
                        if resolved not in seen:
                            seen.add(resolved)
                            discovered.append(resolved)
        except Exception:
            pass

    return discovered


def scaffold_new_project(project_path: Path, project_name: str) -> Path:
    """Scaffold a new computational neuroscience workspace."""
    project_path.mkdir(parents=True, exist_ok=True)
    ensure_workspace_dirs(project_path)
    
    readme = project_path / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {project_name}\n\n"
            f"Computational neuroscience research workspace created with **Neuro-Lab**.\n\n"
            f"## Directory Structure\n"
            f"- `models/` : Biophysical spiking neuron models (Brian 2, NEURON, Nengo, snnTorch)\n"
            f"- `notebooks/` : Interactive computational notebooks (.ipynb)\n"
            f"- `analysis/` : Electrophysiology data processing pipelines (Neo / Elephant)\n"
            f"- `data/` : Electrophysiology recordings, stimulus patterns, and datasets\n"
            f"- `results/` : Generated simulation traces, raster plots, and analysis outputs\n",
            encoding="utf-8"
        )
    return project_path

