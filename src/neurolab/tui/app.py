"""Main Textual application for Neuro-Lab."""

from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding

from ..core.workspace import TOOLS, resolve_workspace_root, ensure_workspace_dirs
from ..core.launcher import launch_jupyter, launch_nengo_gui, run_script_interactive, open_in_editor
from .widgets.ascii_brain import AsciiBrainWidget
from .widgets.telemetry import TelemetryWidget
from .widgets.daily_theory import DailyTheoryWidget
from .widgets.tool_card import ToolCard
from .screens.action_modal import ToolActionModal
from .screens.new_file import NewFileModal
from .screens.file_picker import FilePickerModal
from .screens.doctor import DoctorModal


class NeuroLabApp(App):
    """Neuro-Lab Computational Neuroscience Terminal Workspace."""

    CSS_PATH = "styles.tcss"
    TITLE = "NEURO-LAB"
    SUB_TITLE = "Computational Neuroscience Workspace & Toolchain Orchestrator"

    BINDINGS = [
        Binding("1", "select_tool('jupyter')", "JupyterLab", show=True),
        Binding("2", "select_tool('brian2')", "Brian 2", show=True),
        Binding("3", "select_tool('neuron')", "NEURON", show=True),
        Binding("4", "select_tool('nengo')", "Nengo GUI", show=True),
        Binding("5", "select_tool('snntorch')", "snnTorch", show=True),
        Binding("6", "select_tool('neo')", "Neo/Elephant", show=True),
        Binding("d", "open_doctor", "Doctor", show=True),
        Binding("r", "refresh_workspace", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, workspace_path: Optional[Path] = None, **kwargs):
        super().__init__(**kwargs)
        self.workspace = (workspace_path or resolve_workspace_root()).resolve()
        ensure_workspace_dirs(self.workspace)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            # Left Panel: 2D Brain + Telemetry + Daily Theory
            with Vertical(id="left-panel"):
                yield AsciiBrainWidget(id="brain-widget")
                yield TelemetryWidget(workspace=self.workspace, id="telemetry-widget")
                yield DailyTheoryWidget(id="daily-theory-widget")

            # Right Panel: Tool Hub Cards + Action Bar
            with Vertical(id="right-panel"):
                yield Static(
                    " 🔬 [bold cyan]COMPUTATIONAL TOOLCHAINS & WORKSPACE BRIDGES[/bold cyan]\n"
                    " [dim]Select a framework to scaffold standard templates or manage existing models[/dim]",
                    id="tool-hub-header"
                )

                with Grid(id="tools-grid"):
                    tool_keys = [
                        ("jupyter", "1"),
                        ("brian2", "2"),
                        ("neuron", "3"),
                        ("nengo", "4"),
                        ("snntorch", "5"),
                        ("neo", "6"),
                    ]
                    for tool_id, key in tool_keys:
                        yield ToolCard(
                            tool=TOOLS[tool_id],
                            key_shortcut=key,
                            workspace=self.workspace,
                            classes="tool-card",
                            id=f"card-{tool_id}"
                        )

                with Horizontal(id="bottom-actions"):
                    yield Button("🩺 Toolchain Doctor [d]", variant="default", id="btn-doctor")
                    yield Button("🔄 Refresh [r]", variant="default", id="btn-refresh")
                    yield Button("🚪 Exit [q]", variant="error", id="btn-quit")

        yield Footer()

    def on_mount(self) -> None:
        self.notify(f"Workspace loaded: {self.workspace.name}", title="Neuro-Lab Ready")

    def on_tool_card_selected(self, message: ToolCard.Selected) -> None:
        self.action_select_tool(message.tool_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-doctor":
            self.action_open_doctor()
        elif event.button.id == "btn-refresh":
            self.action_refresh_workspace()
        elif event.button.id == "btn-quit":
            self.exit()

    def action_open_doctor(self) -> None:
        self.push_screen(DoctorModal())

    def action_refresh_workspace(self) -> None:
        # Refresh all tool cards and telemetry
        try:
            self.query_one("#telemetry-widget", TelemetryWidget).refresh()
            for tool_id in TOOLS:
                card = self.query_one(f"#card-{tool_id}", ToolCard)
                card.refresh()
            self.notify("Workspace re-scanned.", title="Refreshed")
        except Exception:
            pass

    def action_select_tool(self, tool_id: str) -> None:
        if tool_id not in TOOLS:
            return

        def handle_action_choice(choice: Optional[str]) -> None:
            if choice == "new":
                self.push_screen(NewFileModal(tool_id, self.workspace), self.handle_file_result)
            elif choice == "existing":
                self.push_screen(FilePickerModal(tool_id, self.workspace), self.handle_file_result)

        self.push_screen(ToolActionModal(tool_id, self.workspace), handle_action_choice)

    def handle_file_result(self, result: Optional[Dict[str, Any]]) -> None:
        if not result:
            return

        tool_id = result["tool_id"]
        file_path = Path(result["file_path"])
        mode = result["mode"]

        self.action_refresh_workspace()

        if mode == "jupyter":
            launch_jupyter(file_path)
            self.notify(
                f"Opening JupyterLab with {file_path.name}...\nCheck your browser window.",
                title="🪐 JupyterLab Launched",
                timeout=6.0
            )
        elif mode == "nengo":
            launch_nengo_gui(file_path)
            self.notify(
                f"Starting Nengo GUI on http://localhost:8080 for {file_path.name}...",
                title="🧠 Nengo GUI Launched",
                timeout=6.0
            )
        elif mode == "run":
            with self.suspend():
                run_script_interactive(file_path)
            self.action_refresh_workspace()
        elif mode == "edit":
            with self.suspend():
                open_in_editor(file_path)
            self.action_refresh_workspace()
        elif mode == "none":
            self.notify(
                f"File created: {file_path.relative_to(self.workspace) if file_path.is_relative_to(self.workspace) else file_path}",
                title="✨ Template Scaffolding Complete"
            )
