"""Modal screen to pick an existing workspace file."""

from pathlib import Path
from typing import Dict, Any, Optional
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, OptionList, Static
from textual.widgets.option_list import Option
from ...core.workspace import TOOLS, list_tool_files


class FilePickerModal(ModalScreen[Optional[Dict[str, Any]]]):
    """Modal dialog to select an existing workspace file."""

    def __init__(self, tool_id: str, workspace: Path, **kwargs):
        super().__init__(**kwargs)
        self.tool_id = tool_id
        self.tool = TOOLS[tool_id]
        self.workspace = workspace
        self.files = list_tool_files(tool_id, workspace)

    def compose(self):
        with Vertical(classes="modal-dialog"):
            yield Label(f"📂 Select Existing {self.tool.name} File", classes="modal-title")
            yield Static(f"Found [bold green]{len(self.files)}[/bold green] matching file(s) in workspace:\n")

            options = []
            for f in self.files:
                try:
                    rel_path = f.relative_to(self.workspace)
                except ValueError:
                    rel_path = f
                options.append(Option(prompt=f"📄 {rel_path}", id=str(f)))

            yield OptionList(*options, id="file-option-list")

            with Horizontal(classes="modal-buttons"):
                if self.tool_id == "jupyter":
                    yield Button("🪐 Open in JupyterLab", variant="primary", id="btn-open-jupyter")
                elif self.tool_id == "nengo":
                    yield Button("🧠 Open in Nengo GUI", variant="primary", id="btn-open-nengo")
                    yield Button("✏️ Edit", variant="default", id="btn-open-edit")
                else:
                    yield Button("⚡ Run in Terminal", variant="primary", id="btn-open-run")
                    yield Button("✏️ Edit", variant="default", id="btn-open-edit")

                yield Button("❌ Cancel", variant="error", id="btn-cancel")

    def _get_selected_file(self) -> Optional[Path]:
        opt_list = self.query_one("#file-option-list", OptionList)
        if opt_list.highlighted is None or not self.files:
            return None
        selected_option = opt_list.get_option_at_index(opt_list.highlighted)
        return Path(selected_option.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return

        selected = self._get_selected_file()
        if not selected:
            return

        mode = "edit"
        if event.button.id == "btn-open-jupyter":
            mode = "jupyter"
        elif event.button.id == "btn-open-nengo":
            mode = "nengo"
        elif event.button.id == "btn-open-run":
            mode = "run"
        elif event.button.id == "btn-open-edit":
            mode = "edit"

        self.dismiss({
            "tool_id": self.tool_id,
            "file_path": selected,
            "mode": mode
        })

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
