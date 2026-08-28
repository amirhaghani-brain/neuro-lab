"""Workspace management, file discovery, and template instantiation."""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional


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


def list_tool_files(tool_id: str, workspace: Path) -> List[Path]:
    """Find all files in workspace matching the tool's supported extensions."""
    if tool_id not in TOOLS:
        return []
    
    tool = TOOLS[tool_id]
    results = []
    
    # Target directory for this tool (e.g. models/ or notebooks/ or analysis/)
    target_path = workspace / tool.target_dir
    search_paths = [target_path]
    if workspace != target_path:
        search_paths.append(workspace)

    seen = set()
    ignored_dirs = {
        ".venv", "venv", ".git", "__pycache__", ".pytest_cache",
        "src", "build", "dist", "egg-info", ".eggs", ".gemini", ".ipynb_checkpoints"
    }

    for search_dir in search_paths:
        if not search_dir.exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.endswith(".egg-info")]
            
            # If scanning root workspace, don't descend into other tool dirs already scanned
            rel_root = Path(root).relative_to(workspace) if Path(root) != workspace else Path(".")
            if search_dir == workspace and rel_root.parts and rel_root.parts[0] in ["src", "models", "notebooks", "analysis", "data"]:
                continue

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in tool.extensions:
                    full_path = Path(root) / file
                    if full_path not in seen and not file.startswith("."):
                        seen.add(full_path)
                        results.append(full_path)

    # Sort alphabetically by relative path
    results.sort(key=lambda p: str(p.relative_to(workspace) if p.is_relative_to(workspace) else p))
    return results


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
    ignored_dirs = {
        ".venv", "venv", ".git", "__pycache__", ".pytest_cache",
        "src", "build", "dist", "egg-info", ".eggs", ".gemini", ".ipynb_checkpoints"
    }
    
    if not workspace.exists():
        return []

    query_lower = query.lower().strip()
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.endswith(".egg-info")]
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

