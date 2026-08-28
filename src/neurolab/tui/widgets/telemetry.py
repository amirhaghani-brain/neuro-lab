"""System Telemetry Widget."""

from pathlib import Path
from textual.widgets import Static
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from ..widgets.ascii_brain import AsciiBrainWidget
from ...core.telemetry import get_system_telemetry


class TelemetryWidget(Static):
    """Renders environment, CUDA, memory, and model telemetry."""

    def __init__(self, workspace: Path, **kwargs):
        super().__init__(**kwargs)
        self.workspace = workspace

    def render(self) -> Panel:
        data = get_system_telemetry(self.workspace)

        table = Table.grid(padding=(0, 1))
        table.add_column("Key", style="bold cyan")
        table.add_column("Val", style="bold white")

        table.add_row("Python", f"v{data['python_version']} (venv)")
        table.add_row("Compute", f"[green]{data['cuda_status']}[/green]")
        table.add_row("RAM", data['ram_usage'])
        table.add_row("Models", f"{data['model_count']} scripts / {data['notebook_count']} notebooks")
        table.add_row("Workspace", f"[dim]{Path(data['workspace']).name}[/dim]")

        return Panel(
            table,
            title="[bold green]Telemetry & Environment[/bold green]",
            border_style="green",
            padding=(0, 1)
        )
