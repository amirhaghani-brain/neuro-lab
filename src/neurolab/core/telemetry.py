"""System telemetry and daily neuroscience foundation provider."""

import os
import sys
import datetime
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

from .workspace import list_workspace_registry

DAILY_CONCEPTS = [
    {
        "title": "Leaky Integrate-and-Fire (LIF)",
        "formula": "tau_m * dV/dt = -(V - V_rest) + R*I(t)",
        "desc": "Sub-threshold RC membrane charging with reset discontinuity upon threshold reach."
    },
    {
        "title": "Hodgkin-Huxley Na+ Gating",
        "formula": "I_Na = g_Na * m^3 * h * (V - E_Na)",
        "desc": "Transient depolarizing inward sodium current driving the action potential upstroke."
    },
    {
        "title": "Nernst Equilibrium Potential",
        "formula": "E_ion = (R*T / z*F) * ln([ion]_out / [ion]_in)",
        "desc": "Electrochemical potential balancing electrical gradient and chemical diffusion."
    },
    {
        "title": "Spike-Timing-Dependent Plasticity (STDP)",
        "formula": "Delta_w = A_+ * exp(-dt / tau_+)  [for dt > 0]",
        "desc": "Synaptic weight modification determined by precise millisecond spike pre/post timing."
    },
    {
        "title": "Electrotonic Cable Theory Length Constant",
        "formula": "lambda = sqrt(r_m / r_i)",
        "desc": "Spatial passive voltage attenuation distance in dendrites and unmyelinated axons."
    },
    {
        "title": "Izhikevich Spiking Dynamics",
        "formula": "dv/dt = 0.04*v^2 + 5*v + 140 - u + I",
        "desc": "Two-dimensional non-linear model reproducing 20+ biological spiking behaviors."
    },
    {
        "title": "Neural Engineering Framework (NEF)",
        "formula": "x_hat = sum_i(a_i(x) * d_i)",
        "desc": "Optimal linear decoding of distributed neural ensemble spike representations."
    }
]


def get_daily_concept() -> Dict[str, str]:
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    idx = day_of_year % len(DAILY_CONCEPTS)
    return DAILY_CONCEPTS[idx]


def get_system_telemetry(workspace_path: Path) -> Dict[str, Any]:
    # Python Version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # CUDA Status
    cuda_status = "CPU Mode"
    try:
        import torch
        if torch.cuda.is_available():
            cuda_status = f"CUDA ({torch.cuda.get_device_name(0)})"
    except Exception:
        pass

    # RAM Usage (Linux)
    ram_str = "Unknown"
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
            mem_total = 0
            mem_avail = 0
            for line in lines:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1]) # kB
                elif line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1]) # kB
            if mem_total > 0:
                used_gb = (mem_total - mem_avail) / (1024 * 1024)
                total_gb = mem_total / (1024 * 1024)
                ram_str = f"{used_gb:.1f}G / {total_gb:.1f}G"
    except Exception:
        pass

    # Model & Notebook counts. Models reuse the same framework-aware registry
    # as `neurolab list`, so the banner agrees with the registry and stray
    # scripts (tests/, data/, results/) are not counted as models.
    model_count = 0
    notebook_count = 0
    if workspace_path.exists():
        registry = list_workspace_registry(workspace_path)
        model_count = sum(
            1
            for files in registry.values()
            for f in files
            if f.suffix.lower() in (".py", ".hoc", ".mod")
        )

        ignored_dirs = {".venv", "venv", ".git", "__pycache__", ".pytest_cache", "src", "build", "dist", ".gemini", ".ipynb_checkpoints", "tests"}
        for root, dirs, files in os.walk(workspace_path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.endswith(".egg-info")]
            for f in files:
                if f.endswith(".ipynb"):
                    notebook_count += 1

    return {
        "python_version": py_ver,
        "cuda_status": cuda_status,
        "ram_usage": ram_str,
        "model_count": model_count,
        "notebook_count": notebook_count,
        "workspace": str(workspace_path),
    }
