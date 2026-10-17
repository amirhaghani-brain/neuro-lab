"""Headless smoke tests for the Textual TUI using its test pilot."""

import asyncio
from pathlib import Path

from neurolab.core.workspace import TOOLS
from neurolab.tui.app import NeuroLabApp
from neurolab.tui.screens.action_modal import ToolActionModal
from neurolab.tui.screens.doctor import DoctorModal
from neurolab.tui.widgets.tool_card import ToolCard


def _seed(workspace: Path) -> None:
    """Populate the workspace so widgets render their file-count branch."""
    (workspace / "models" / "cortex.py").write_text("from brian2 import *\n", encoding="utf-8")
    (workspace / "notebooks" / "exp.ipynb").write_text("{}", encoding="utf-8")


def test_tool_card_renders_with_files(workspace: Path):
    _seed(workspace)
    card = ToolCard(TOOLS["brian2"], "2", workspace)
    assert card.render() is not None


def test_every_tool_card_renders(workspace: Path):
    _seed(workspace)
    for key, (tool_id, tool) in enumerate(TOOLS.items()):
        card = ToolCard(tool, str(key + 1), workspace)
        assert card.render() is not None


def test_tui_mounts_with_tool_cards(workspace: Path):
    _seed(workspace)

    async def scenario():
        app = NeuroLabApp(workspace_path=workspace)
        async with app.run_test() as pilot:
            await pilot.pause()
            cards = [w.id for w in app.query("ToolCard")]
            assert "card-brian2" in cards
            assert len(cards) == 6

    asyncio.run(scenario())


def test_action_modal_opens_with_files(workspace: Path):
    _seed(workspace)

    async def scenario():
        app = NeuroLabApp(workspace_path=workspace)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.action_select_tool("brian2")
            await pilot.pause()
            assert isinstance(app.screen, ToolActionModal)

    asyncio.run(scenario())


def test_tui_doctor_modal_opens_and_closes(workspace: Path):
    async def scenario():
        app = NeuroLabApp(workspace_path=workspace)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("d")
            await pilot.pause()
            assert isinstance(app.screen, DoctorModal)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, DoctorModal)

    asyncio.run(scenario())


def test_tui_quit_binding(workspace: Path):
    async def scenario():
        app = NeuroLabApp(workspace_path=workspace)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")
            await pilot.pause()
            assert app._exit

    asyncio.run(scenario())
