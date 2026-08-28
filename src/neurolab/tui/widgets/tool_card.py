"""Tool Card Widget for the Tool Hub Grid."""

from pathlib import Path
from textual.widgets import Static
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from ...core.workspace import ToolDefinition, list_tool_files


class ToolCard(Static):
    """Interactive card representing a neuroscience tool."""

    can_focus = True

    class Selected(Message):
        """Emitted when a tool card is selected."""
        def __init__(self, tool_id: str) -> None:
            self.tool_id = tool_id
            super().__init__()

    def __init__(self, tool: ToolDefinition, key_shortcut: str, workspace: Path, **kwargs):
        super().__init__(**kwargs)
        self.tool = tool
        self.key_shortcut = key_shortcut
        self.workspace = workspace

    def render(self) -> Panel:
        files = list_tool_files(self.tool.id, self.workspace)
        file_count = len(files)

        t = Text()
        t.append(f"[{self.key_shortcut}] ", style="bold yellow")
        t.append(f"{self.tool.icon} {self.tool.name}\n", style=f"bold {self.tool.color}")
        t.append(f"{self.tool.description}\n", style="dim white")
        
        if file_count > 0:
            t.append(f"📁 {file_count} project file{'s' if file_count != 1 else ''} found in {self.tool.target_dir}/", style="green")
        else:
            t.append(f"📁 0 files in {self.tool.target_dir}/ (Ready to scaffold)", style="dim")

        border_color = self.tool.color if self.has_focus else "#30363d"
        return Panel(
            t,
            border_style=border_color,
            padding=(0, 1),
            style="on #161b22"
        )

    def on_click(self) -> None:
        self.post_message(self.Selected(self.tool.id))

    def on_key(self, event) -> None:
        if event.key in ("enter", "space"):
            self.post_message(self.Selected(self.tool.id))
