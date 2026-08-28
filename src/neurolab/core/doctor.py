"""Environment and toolchain diagnostic engine."""

import shutil
import sys
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DiagnosticCheck:
    name: str
    category: str
    status: str  # "OK", "WARN", "FAIL"
    version: Optional[str]
    details: str


def run_diagnostics() -> List[DiagnosticCheck]:
    checks = []

    # 1. Python Environment
    is_venv = sys.prefix != sys.base_prefix
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(DiagnosticCheck(
        name="Python Runtime",
        category="Environment",
        status="OK" if sys.version_info >= (3, 10) else "WARN",
        version=py_ver,
        details=f"Executable: {sys.executable} (Virtualenv: {'Active' if is_venv else 'Inactive'})"
    ))

    # 2. C / C++ Compilers (for Brian2 / NEURON nrnivmodl)
    cc_path = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
    if cc_path:
        checks.append(DiagnosticCheck(
            name="C/C++ Compiler",
            category="System Toolchain",
            status="OK",
            version=cc_path,
            details="Ready for Brian2 Cython/C++ codegen and NEURON nrnivmodl compilation"
        ))
    else:
        checks.append(DiagnosticCheck(
            name="C/C++ Compiler",
            category="System Toolchain",
            status="WARN",
            version=None,
            details="No gcc/clang found in PATH. Native compilation will fall back to numpy"
        ))

    # 3. Scientific Python Ecosystem
    for pkg_name, label in [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("matplotlib", "Matplotlib"),
        ("sympy", "SymPy"),
    ]:
        try:
            mod = __import__(pkg_name)
            ver = getattr(mod, "__version__", "Available")
            checks.append(DiagnosticCheck(
                name=label,
                category="Core Scientific Stack",
                status="OK",
                version=ver,
                details=f"Core library available"
            ))
        except ImportError:
            checks.append(DiagnosticCheck(
                name=label,
                category="Core Scientific Stack",
                status="FAIL",
                version=None,
                details=f"Missing. Run `pip install {pkg_name}`"
            ))

    # 4. Computational Neuroscience Frameworks
    neuro_packages = [
        ("brian2", "Brian 2", "ODE spiking neural networks and biophysics"),
        ("neuron", "NEURON", "Multicompartment 3D cable simulation"),
        ("nengo", "Nengo", "Neural Engineering Framework cognitive models"),
        ("nengo_gui", "Nengo GUI", "Browser-based interactive architecture builder"),
        ("snntorch", "snnTorch", "PyTorch-based spiking neural network training"),
        ("neo", "Neo", "Electrophysiology multi-format data structures"),
        ("elephant", "Elephant", "Cellular spike-train and LFP analysis"),
        ("jupyterlab", "JupyterLab", "Interactive computational notebook environment"),
    ]

    for pkg_name, label, desc in neuro_packages:
        try:
            mod = __import__(pkg_name)
            ver = getattr(mod, "__version__", "Available")
            checks.append(DiagnosticCheck(
                name=label,
                category="Neuroscience Toolchain",
                status="OK",
                version=ver,
                details=desc
            ))
        except ImportError:
            checks.append(DiagnosticCheck(
                name=label,
                category="Neuroscience Toolchain",
                status="WARN",
                version=None,
                details=f"Not installed ({desc}). Install with `pip install {pkg_name}`"
            ))

    # 5. Hardware Acceleration (CUDA / PyTorch)
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        cuda_dev = torch.cuda.get_device_name(0) if cuda_ok else "None"
        checks.append(DiagnosticCheck(
            name="PyTorch & CUDA",
            category="Acceleration",
            status="OK" if cuda_ok else "WARN",
            version=f"PyTorch {torch.__version__}",
            details=f"CUDA Acceleration: {'Enabled (' + cuda_dev + ')' if cuda_ok else 'CPU Mode only'}"
        ))
    except ImportError:
        checks.append(DiagnosticCheck(
            name="PyTorch & CUDA",
            category="Acceleration",
            status="WARN",
            version=None,
            details="PyTorch not installed. Needed for snnTorch and GPU acceleration"
        ))

    return checks
