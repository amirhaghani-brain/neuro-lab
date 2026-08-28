"""Daily Neuroscience Foundation Widget."""

from textual.widgets import Static
from rich.text import Text
from rich.panel import Panel
from ...core.telemetry import get_daily_concept


class DailyTheoryWidget(Static):
    """Renders rotating daily neuroscience biophysical concepts."""

    def render(self) -> Panel:
        concept = get_daily_concept()

        t = Text()
        t.append(f"⚡ {concept['title']}\n", style="bold yellow")
        t.append(f"   {concept['formula']}\n", style="bold white")
        t.append(f"   {concept['desc']}", style="italic dim white")

        return Panel(
            t,
            title="[bold yellow]Daily Neuroscience Foundation[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
