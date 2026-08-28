"""Modal screen prompting to create new file or select existing file."""

from pathlib import Path
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, Static
from ...core.workspace import TOOLS, list_tool_files


class ToolActionModal(ModalScreen[str]):
    """Modal to decide between New File and Existing File."""

    def __init__(self, tool_id: str, workspace: Path, **kwargs):
        super().__init__(**kwargs)
        self.tool_id = tool_id
        self.tool = TOOLS[tool_id]
        self.workspace = workspace

    def compose(self):
        files = list_tool_files(self.tool_id, self.workspace)
        has_files = len(files) > 0

        with Vertical(classes="modal-dialog"):
            yield Label(f"{self.tool.icon} {self.tool.name} Workspace Bridge", classes="modal-title")
            yield Static(
                f"[dim]{self.tool.description}[/dim]\n"
                f"Target Directory: [cyan]{self.tool.target_dir}/[/cyan]\n"
                f"Existing files: [bold {'green' if has_files else 'yellow'}]{len(files)}[/bold {'green' if has_files else 'yellow'}] found\n"
            )

            with Vertical():
                yield Button(
                    f"✨ Create New File from Template",
                    variant="primary",
                    id="btn-new",
                )
                if has_files:
                    yield Button(
                        f"📂 Select Existing File ({len(files)} available)",
                        variant="default",
                        id="btn-existing",
                    )
                else:
                    yield Button(
                        "📂 Select Existing File (No files found)",
                        variant="default",
                        id="btn-existing",
                        disabled=True
                    )
                yield Button("❌ Cancel", variant="error", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-new":
            self.dismiss("new")
        elif event.button.id == "btn-existing":
            self.dismiss("existing")
        else:
            self.dismiss("cancel")

    def on_key(self, event) -> None:
        if event.key in ("escape", "q"):
            self.dismiss("cancel")
        elif event.key == "n":
            self.dismiss("new")
        elif event.key == "e":
            files = list_tool_files(self.tool_id, self.workspace)
            if files:
                self.dismiss("existing")
