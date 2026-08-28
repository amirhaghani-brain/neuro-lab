# Neuro-Lab

```
                 ___    ___
            ..")" .." `(``..
          .'; _..=. :: `-'.' ;`.
         : ) ;"`':._::_.      ( :.
       .:-"   _.  `"##"` "._   `-:\
      /."   -"`  ._.::._. .'"-   ".:
     : :    ( -: `" :: "` :- )    : )
    ( .":==._' `'=._##_.='` '_.==: .'
    (:  `, `"`    `"##"`    `"` .'`".)
     \`'  `"--.  "- )( -" ..--"`  `-/
     (" (_." =""-..."`...-""= "._) ")
      "..__..-"  )%`..'%(  "-..__.."
           (#"...'\%%%%/`..."#)
            `######`--'######"
              "###")@@(`###"
                   \@@/
                    )(
```

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CLI](https://img.shields.io/badge/Interface-Interactive%20CLI-magenta.svg)](https://github.com/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Arch-lightgrey.svg)](https://archlinux.org/)

> **A terminal-native workspace, interactive command center, and toolchain orchestrator for computational neuroscience.**

Neuro-Lab bridges standard computational neuroscience simulation frameworks, scientific notebooks, data analysis pipelines, and terminal editors into a single command center.

---

## Key Features

- **Unified Toolchain Bridges**: Direct scaffold and launch bridges for **JupyterLab**, **Brian 2**, **NEURON**, **Nengo & Nengo GUI**, **snnTorch**, and **Neo / Elephant**.
- **Interactive Developer CLI Shell (`neurolab > `)**: Fast, prompt-toolkit powered REPL with autocompletion, command history, and single-character triggers.
- **Adaptive Window Sizing**: Dynamic terminal geometry detection that scales from compact split-panes to multi-column widescreen hero layouts.
- **LazyVim / Neovim Workspace Integration**: Launch full IDE mode on project root (`nvim .`) with Neo-tree, Telescope, and LSP support, or jump directly to target scripts.
- **Fuzzy File Finder (`[f]`)**: Instantly locate, inspect, edit, or run any model script, notebook, or dataset in the workspace.
- **Multi-Project Workspace Manager (`[p]`)**: Seamlessly switch between research workspaces, scaffold new project directory trees, and inspect code analytics.
- **Hardware & Environment Telemetry**: Real-time tracking of Python virtualenvs, RAM usage, CUDA acceleration, and active model metrics.
- **Toolchain Diagnostics (`doctor`)**: Comprehensive diagnostic check for gcc/clang compilers, `nrnivmodl`, CUDA, and scientific packages.
- **Daily Biophysical Foundations**: Rotating theoretical neuroscience principles (Hodgkin-Huxley kinetics, cable theory, STDP, Wilson-Cowan oscillators).

---

## Supported Toolchains & Standard Templates

| Key | Toolchain | Target Folder | Description & Capabilities |
| :---: | :--- | :--- | :--- |
| `[1]` | **JupyterLab** | `notebooks/` | Interactive computational notebooks (`.ipynb`) with standard scientific imports |
| `[2]` | **Brian 2** | `models/` | ODE-based spiking neuron dynamics & biophysical networks (`.py`) |
| `[3]` | **NEURON** | `models/` | Multicompartmental 3D cable simulation & `.mod` ion channel compilation |
| `[4]` | **Nengo & GUI** | `models/` | Neural Engineering Framework (NEF) cognitive models & browser GUI |
| `[5]` | **snnTorch** | `models/` | PyTorch surrogate gradient deep Spiking Neural Networks (`.py`) |
| `[6]` | **Neo / Elephant** | `analysis/` | Electrophysiology multi-format I/O, spike train statistics, and PSTH/ISI |

---

## Installation

### Prerequisites
- Linux (Arch, Debian/Ubuntu, Fedora)
- Python 3.10+
- GCC / Clang (for NEURON and Brian2 C++ codegen)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/amirhaghani/neuro-lab.git
cd neuro-lab

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode
pip install -e .
```

To install with complete neuroscience dependencies:
```bash
pip install -e ".[all]"
```

---

## Usage

### Interactive Command Center

Launch the main command shell:
```bash
lab
# or
neurolab
```

#### Interactive Prompt Shortcuts

| Shortcut | Command | Action |
| :---: | :--- | :--- |
| `1` - `6` | `jupyter`, `brian2`, `neuron`, `nengo`, `snntorch`, `neo` | Open interactive toolchain bridge |
| `e` | `editor [file]`, `lazyvim`, `nvim` | Open **LazyVim / Neovim** on workspace or specific script |
| `f` | `find`, `search` | Interactive **fuzzy file finder** across all project directories |
| `p` | `projects`, `proj` | **Multi-project manager** (switch or scaffold research workspaces) |
| `r` | `run [file]` | Execute a simulation script in terminal |
| `n` | `new <tool> [name]` | Scaffold a new model from standard template |
| `d` | `doctor` | Run toolchain and compiler diagnostic check |
| `l` | `list`, `ls` | List all workspace models and notebooks |
| `t` | `theory` | Display today's computational neuroscience principle |
| `c` | `clear` | Clear terminal screen and redraw dashboard |
| `q` | `quit`, `exit` | Exit Neuro-Lab |

---

### Non-Interactive Headless Commands

Neuro-Lab can also be executed directly from bash scripts or CLI automation:

```bash
# Run system diagnostics
neurolab doctor

# List project file registry
neurolab list

# Fuzzy search files
neurolab find

# Execute a simulation
neurolab run models/purkinje.py

# Scaffold a new Brian 2 model
neurolab new brian2 cortex_sim.py

# Open workspace in LazyVim
neurolab editor

# Manage projects
neurolab projects
```

---

## Workspace Architecture

A standard Neuro-Lab research workspace follows a clean scientific structure:

```
neuro-lab/
├── models/             # Spiking neuron models (Brian2, NEURON, Nengo, snnTorch)
│   ├── basal_ganglia.py
│   ├── cortex_sim.py
│   └── purkinje.py
├── notebooks/          # Interactive JupyterLab research notebooks (.ipynb)
│   └── experiment_01.ipynb
├── analysis/           # Electrophysiology pipelines (Neo / Elephant)
│   └── spike_stats.py
├── data/               # Recordings, spike trains, stimulus datasets
├── results/            # Figures, raster plots, traces, and metrics
├── pyproject.toml      # Package configuration
└── README.md           # Project documentation
```

---

## Diagnostics (`doctor`)

Run `neurolab doctor` at any time to verify system health:

```
=== [ Toolchain Diagnostics ] ===

  Status    Component         Category          Version         Details
  [PASS]    Python Runtime    Environment       3.14.7          Virtualenv: Active
  [PASS]    C/C++ Compiler    System            /usr/bin/gcc    Ready for codegen & nrnivmodl
  [PASS]    NumPy             Core Scientific   2.5.2           Core library available
  [PASS]    SciPy             Core Scientific   1.18.1          Core library available
  [PASS]    Matplotlib        Core Scientific   3.11.1          Core library available
  [PASS]    Brian 2           Neuroscience      2.10.1          ODE spiking dynamics
  [PASS]    NEURON            Neuroscience      9.0.2           Multicompartment 3D cable
  [PASS]    Nengo             Neuroscience      4.1.0           Neural Engineering Framework
  [PASS]    Nengo GUI         Neuroscience      0.6.0           Browser-based visualizer
  [PASS]    Neo               Neuroscience      0.14.5          Electrophysiology data I/O
  [PASS]    Elephant          Neuroscience      1.2.1           Spike-train metrics & ISI
  [PASS]    JupyterLab        Neuroscience      4.6.3           Interactive notebooks
```

---

## Contributing

Contributions from computational neuroscientists, biophysicists, and scientific Python developers are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/biophysical-mechanism`)
3. Commit your changes (`git commit -m 'Add new synapse template'`)
4. Push to branch (`git push origin feature/biophysical-mechanism`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
