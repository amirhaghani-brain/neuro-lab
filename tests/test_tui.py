"""Headless smoke tests for the Textual TUI using its test pilot."""

import asyncio
from pathlib import Path

from neurolab.tui.app import NeuroLabApp
from neurolab.tui.screens.doctor import DoctorModal


def test_tui_mounts_with_tool_cards(workspace: Path):
    async def scenario():
        app = NeuroLabApp(workspace_path=workspace)
        async with app.run_test() as pilot:
            await pilot.pause()
            cards = [w.id for w in app.query("ToolCard")]
            assert "card-brian2" in cards
            assert len(cards) == 6

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
