"""Process launcher and tool bridge execution manager."""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple


def get_default_editor() -> str:
    """Determine researcher's preferred editor, prioritizing LazyVim / Neovim."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if editor:
        return editor
    
    for candidate in ["nvim", "vim", "micro", "nano", "code", "gedit"]:
        if shutil.which(candidate):
            return candidate
    return "nano"


def get_editor_name() -> str:
    """Get friendly display name for the configured editor."""
    ed = get_default_editor()
    lazyvim_marker = Path.home() / ".config" / "nvim" / "lazyvim.json"
    if "nvim" in ed or "omarchy-launch-editor" in ed or "lazyvim" in ed.lower():
        if lazyvim_marker.exists():
            return "LazyVim"
        return "Neovim"
    return ed


def launch_jupyter(target_file: Path) -> subprocess.Popen:
    """Launch JupyterLab opening the specified notebook."""
    jupyter_cmd = shutil.which("jupyter")
    if not jupyter_cmd:
        # Try in virtualenv or sys.executable dir
        venv_jupyter = Path(sys.executable).parent / "jupyter"
        if venv_jupyter.exists():
            jupyter_cmd = str(venv_jupyter)
        else:
            jupyter_cmd = "jupyter"

    cmd = [jupyter_cmd, "lab", str(target_file)]
    # Run in detached or background process
    proc = subprocess.Popen(
        cmd,
        cwd=str(target_file.parent.parent if target_file.parent.name in ["notebooks", "models"] else target_file.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    return proc


def launch_nengo_gui(target_file: Path) -> subprocess.Popen:
    """Launch Nengo GUI web interface for model."""
    nengo_cmd = shutil.which("nengo")
    if not nengo_cmd:
        venv_nengo = Path(sys.executable).parent / "nengo"
        if venv_nengo.exists():
            nengo_cmd = str(venv_nengo)
        else:
            nengo_cmd = "nengo"

    cmd = [nengo_cmd, str(target_file)]
    proc = subprocess.Popen(
        cmd,
        cwd=str(target_file.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    return proc


def run_script_interactive(target_file: Path) -> int:
    """Execute Python script in the terminal interactively."""
    # If file is a NEURON script and directory has .mod files, check for nrnivmodl
    mod_files = list(target_file.parent.glob("*.mod"))
    if mod_files and shutil.which("nrnivmodl") and not (target_file.parent / "x86_64").exists():
        print("Compiling NEURON .mod mechanisms with nrnivmodl...")
        subprocess.run(["nrnivmodl"], cwd=str(target_file.parent))

    print(f"\n\033[1;36m=== RUNNING {target_file.name} ===\033[0m\n")
    res = subprocess.run([sys.executable, str(target_file)], cwd=str(target_file.parent))
    print(f"\n\033[1;32m=== FINISHED (Exit code {res.returncode}) ===\033[0m")
    # Only pause when attached to a terminal so scripts and CI never hang.
    if sys.stdin.isatty():
        input("\nPress Enter to return to Neuro-Lab...")
    return res.returncode


def open_in_editor(target_file: Path, editor_cmd: Optional[str] = None) -> int:
    """Open target file or directory in editor interactively."""
    editor = editor_cmd or get_default_editor()
    cmd_parts = shlex.split(editor)
    cmd = cmd_parts + [str(target_file)]
    cwd_dir = target_file if target_file.is_dir() else target_file.parent
    try:
        res = subprocess.run(cmd, cwd=str(cwd_dir))
        return res.returncode
    except Exception as e:
        print(f"\033[1;31m[-] Error launching editor ({editor}): {e}\033[0m")
        # Fallback to direct nvim or nano
        for fallback in ["nvim", "nano", "vi"]:
            if shutil.which(fallback):
                print(f"\033[1;33m[!] Falling back to {fallback}...\033[0m")
                return subprocess.run([fallback, str(target_file)], cwd=str(cwd_dir)).returncode
        return 1
