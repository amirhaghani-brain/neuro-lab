# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-17

Initial public release of the Neuro-Lab command center.

### Added

- Interactive **Textual TUI dashboard** with a tool-hub grid, telemetry panel,
  anatomical ASCII brain, rotating daily neuroscience foundation, toolchain
  doctor modal, file picker, and new-file scaffolding modal.
- `neurolab tui` and `neurolab shell` commands. Running `neurolab` (or `lab`)
  with no subcommand launches the TUI on a real terminal and falls back to the
  scriptable prompt shell when output is piped (CI, scripts, redirection).
- **Framework-aware file registry** (`neurolab list`): each model script is
  attributed to the framework it actually imports, so scripts sharing `models/`
  are never reported under every toolchain.
- **Pre-flight dependency check** in `neurolab run`: missing frameworks are
  reported with `pip install` hints instead of a raw `ModuleNotFoundError`
  traceback. On a TTY the run can proceed; when piped it is skipped.
- `neurolab --version`.
- Toolchain bridges for JupyterLab, Brian 2, NEURON, Nengo & Nengo GUI,
  snnTorch, and Neo / Elephant, with standard templates for each.
- Test suite covering workspace discovery, import-based classification,
  template scaffolding, diagnostics, dependency detection, telemetry, the CLI
  surface and exit codes, and headless TUI rendering (56 tests).
- GitHub Actions CI running the suite on Python 3.10–3.13.
- GitHub Actions release workflow: pushing a `v*` tag builds the sdist and
  wheel, verifies the tag matches `neurolab.__version__`, and creates a GitHub
  Release; publishing to PyPI is opt-in via the `PYPI_PUBLISH` repository
  variable.

### Changed

- `list` no longer lists the same file under multiple toolchains and no longer
  leaks workspace-root scripts into every tool's file count.
- `run` now propagates the executed script's exit code, so failures exit
  non-zero for scripts and CI.
- `doctor` adapts to narrow terminals (single-line rows, redundant column
  dropped below 110 columns) and expands the full details of every WARN/FAIL
  in an "Attention needed" section.
- Dashboard telemetry counts only real models, excluding `tests/`, `data/`,
  and `results/`, and no longer double-counts notebooks.
- The version is single-sourced from `neurolab.__version__`; `pyproject.toml`
  reads it dynamically.

### Fixed

- TUI crash: `ToolDefinition` had no `icon` attribute, so any tool card raised
  `AttributeError` as soon as it was painted.
- The TUI source was unreachable dead code — there was no command to launch it.
- `doctor` output was unreadable at 80 columns, wrapping to one word per line.
- nengo's pytest plugin is incompatible with pytest >= 8 and broke the test
  suite when nengo was installed; it is now disabled.

[Unreleased]: https://github.com/amirhaghani-brain/neuro-lab/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/amirhaghani-brain/neuro-lab/releases/tag/v0.1.0
