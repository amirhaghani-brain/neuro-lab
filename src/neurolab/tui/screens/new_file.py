"""Modal screen for creating a new file from standard template."""

from pathlib import Path
from typing import Dict, Any, Optional
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Input, Button, Static, RadioSet, RadioButton
from ...core.workspace import TOOLS, create_file_from_template


class NewFileModal(ModalScreen[Optional[Dict[str, Any]]]):
    """Modal dialog to name and scaffold a new template file."""

    def __init__(self, tool_id: str, workspace: Path, **kwargs):
        super().__init__(**kwargs)
        self.tool_id = tool_id
        self.tool = TOOLS[tool_id]
        self.workspace = workspace

    def compose(self):
        with Vertical(classes="modal-dialog"):
            yield Label(f"✨ New {self.tool.name} File", classes="modal-title")
            yield Static(
                f"Location: [cyan]{self.tool.target_dir}/[/cyan]\n"
                f"Boilerplate: [dim]{self.tool.template_name}[/dim]\n"
            )

            yield Label("Enter filename:")
            yield Input(
                value=self.tool.default_filename,
                placeholder=self.tool.default_filename,
                id="input-filename"
            )

            yield Label("\nLaunch Option:", classes="launch-label")
            with RadioSet(id="radio-launch-mode"):
                if self.tool_id == "jupyter":
                    yield RadioButton("Create and launch in JupyterLab", value=True, id="mode-jupyter")
                    yield RadioButton("Create file only", id="mode-create-only")
                elif self.tool_id == "nengo":
                    yield RadioButton("Create and launch in Nengo GUI (Browser)", value=True, id="mode-nengo")
                    yield RadioButton("Create and open in Terminal Editor", id="mode-edit")
                    yield RadioButton("Create file only", id="mode-create-only")
                else:
                    yield RadioButton("Create and open in Terminal Editor", value=True, id="mode-edit")
                    yield RadioButton("Create and run in Terminal", id="mode-run")
                    yield RadioButton("Create file only", id="mode-create-only")

            with Horizontal(classes="modal-buttons"):
                yield Button("🚀 Confirm & Create", variant="primary", id="btn-create")
                yield Button("❌ Cancel", variant="error", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return

        filename_input = self.query_one("#input-filename", Input).value.strip()
        if not filename_input:
            filename_input = self.tool.default_filename

        # Determine selected mode
        radio_set = self.query_one("#radio-launch-mode", RadioSet)
        selected_btn = radio_set.pressed_button
        mode = "edit"
        if selected_btn:
            if selected_btn.id == "mode-jupyter":
                mode = "jupyter"
            elif selected_btn.id == "mode-nengo":
                mode = "nengo"
            elif selected_btn.id == "mode-run":
                mode = "run"
            elif selected_btn.id == "mode-create-only":
                mode = "none"

        # Create file from template
        created_file = create_file_from_template(self.tool_id, filename_input, self.workspace)

        self.dismiss({
            "tool_id": self.tool_id,
            "file_path": created_file,
            "mode": mode
        })

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
