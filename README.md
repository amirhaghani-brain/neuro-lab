<p align="center">
  <img src="https://raw.githubusercontent.com/amirhaghani-brain/neuro-lab/main/assets/wordmark.png" alt="NeuroLab — Next-Gen Computational Neuroscience" width="600">
</p>

<p align="center">
  <b>A terminal-native workspace for computational neuroscience.</b><br>
  Brian 2, NEURON, Nengo, snnTorch and Neo/Elephant — behind one command.
</p>

<p align="center">
  <a href="https://pypi.org/project/neurolab-cli/"><img src="https://img.shields.io/pypi/v/neurolab-cli?color=14b8a6" alt="PyPI"></a>
  <a href="https://pypi.org/project/neurolab-cli/"><img src="https://img.shields.io/pypi/pyversions/neurolab-cli" alt="Python"></a>
  <a href="https://github.com/amirhaghani-brain/neuro-lab/actions/workflows/ci.yml"><img src="https://github.com/amirhaghani-brain/neuro-lab/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/amirhaghani-brain/neuro-lab/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-8b5cf6" alt="MIT"></a>
  <a href="https://hub.xerj.org/contributors/amirhaghani-brain"><img src="https://hub.xerj.org/contributors/amirhaghani-brain/badge.svg" alt="XERJ Corpus Hub contributor"></a>
</p>

---

NeuroLab turns a folder of simulation scripts into a research workspace. It
scaffolds models from standard templates, launches the right framework, tracks
what is installed, and tells you exactly which package is missing **before**
your simulation dies mid-run.

## Install

```bash
pip install neurolab-cli
```

Then, from any project folder:

```bash
neurolab        # or simply: lab
```

Want the whole neuroscience stack at once, instead of per-framework installs?

```bash
pip install "neurolab-cli[all]"
```

> Linux with Python 3.10+. NEURON's `.mod` compilation also needs `gcc`/`clang`
> — `neurolab doctor` will tell you if anything is missing.

## Quick start

```bash
neurolab new brian2 cortex_sim.py   # scaffold a model from a template
neurolab run models/cortex_sim.py   # run it
neurolab doctor                     # check compilers, CUDA and frameworks
```

On a real terminal, `neurolab` opens a full-screen dashboard: pick a toolchain,
browse files, run models and read today's biophysics note without leaving the
TUI. When output is piped (CI, scripts, redirection) it falls back to the
scriptable prompt shell instead — or ask for it explicitly with
`neurolab shell`.

## Toolchains

| Key | Toolchain | Folder | What it gives you |
| :-: | :--- | :--- | :--- |
| `1` | **JupyterLab** | `notebooks/` | Interactive computational notebooks |
| `2` | **Brian 2** | `models/` | ODE-based spiking neurons and networks |
| `3` | **NEURON** | `models/` | Multicompartment cable models, `.mod` compilation |
| `4` | **Nengo** | `models/` | Neural Engineering Framework models and GUI |
| `5` | **snnTorch** | `models/` | Surrogate-gradient deep spiking networks |
| `6` | **Neo / Elephant** | `analysis/` | Electrophysiology I/O, spike-train statistics |

Models sharing `models/` are attributed to the framework they actually import,
so `neurolab list` never reports one script under every toolchain.

## Commands

| Command | What it does |
| :--- | :--- |
| `neurolab` · `lab` | Full-screen TUI dashboard |
| `neurolab shell` | Classic prompt shell (`neurolab > `) with shortcuts |
| `neurolab new <tool> [name]` | Scaffold a model from a standard template |
| `neurolab run <file>` | Run a simulation, with a pre-flight import check |
| `neurolab list` | List workspace models and notebooks |
| `neurolab find` | Fuzzy-find any file in the workspace |
| `neurolab editor [file]` | Open LazyVim/Neovim on the workspace or a file |
| `neurolab projects` | Switch between workspaces, or scaffold a new one |
| `neurolab doctor` | Full toolchain and environment diagnostics |

Every command works on the current directory; pass `-w <path>` to target
another workspace.

**In the classic shell**, single keys do the work: `1`–`6` open toolchains,
`r` runs, `n` scaffolds, `f` finds, `p` switches project, `d` diagnoses,
`t` prints today's principle, `q` quits.

## Workspace layout

```
my-lab/
├── models/         # Brian 2, NEURON, Nengo, snnTorch scripts
├── notebooks/      # JupyterLab experiments (.ipynb)
├── analysis/       # Neo / Elephant pipelines
├── data/           # Recordings, spike trains, stimuli
└── results/        # Figures, rasters, traces, metrics
```

## Missing dependencies, handled

`neurolab run` reads the script's imports first, so a missing framework is a
one-line fix instead of a traceback:

```
[!] basal_ganglia.py needs packages that are not installed:
      - nengo  ->  pip install nengo

    Install the whole neuroscience stack with:  pip install "neurolab-cli[all]"
```

Piped runs skip and exit non-zero, so scripts and CI fail fast.

---

<details>
<summary><b>Diagnostics: what <code>doctor</code> checks</b></summary>

<br>

```
=== [ Toolchain Diagnostics ] ===

  Status    Component         Category          Version         Details
  [PASS]    Python Runtime    Environment       3.14.7          Virtualenv: Active
  [PASS]    C/C++ Compiler    System            /usr/bin/gcc    Ready for codegen & nrnivmodl
  [PASS]    CUDA              System            12.4            GPU acceleration available
  [PASS]    Brian 2           Neuroscience      2.10.1          ODE spiking dynamics
  [PASS]    NEURON            Neuroscience      9.0.2           Multicompartment 3D cable
  [PASS]    Nengo             Neuroscience      4.1.0           Neural Engineering Framework
  [PASS]    snnTorch          Neuroscience      0.9.4           Surrogate-gradient SNNs
  [PASS]    Neo / Elephant    Neuroscience      0.14.5 / 1.2.1  Electrophysiology I/O & metrics
```

</details>

<details>
<summary><b>Development</b></summary>

<br>

```bash
git clone https://github.com/amirhaghani-brain/neuro-lab.git
cd neuro-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest    # 57 tests: workspace, templates, doctor, deps, CLI, TUI
```

CI runs the suite on Python 3.10–3.13 for every push and pull request.

</details>

<details>
<summary><b>Releasing</b></summary>

<br>

The version lives in one place, `src/neurolab/__init__.py`; `pyproject.toml`
reads it dynamically. Bump it, add a `CHANGELOG.md` entry, then tag:

```bash
git commit -am "release: v0.1.8"
git tag -a v0.1.8 -m "v0.1.8"
git push origin main v0.1.8
```

The `Release` workflow verifies the tag against `__version__`, builds and
smoke-tests the wheel, creates the GitHub Release, and publishes to PyPI via
OIDC trusted publishing — no tokens stored.

</details>

---

## Contributing

Issues and pull requests are welcome — from neuroscientists, biophysicists and
scientific Python developers alike. Fork, branch, `pytest`, open a PR.

## License

MIT — see [LICENSE](https://github.com/amirhaghani-brain/neuro-lab/blob/main/LICENSE).
