"""Shared pytest fixtures for the Neuro-Lab test suite."""

from pathlib import Path

import pytest

from neurolab.core.workspace import ensure_workspace_dirs


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """An empty, correctly structured Neuro-Lab workspace."""
    ensure_workspace_dirs(tmp_path)
    return tmp_path


def write(path: Path, content: str = "") -> Path:
    """Create a file (and its parents) and return it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
