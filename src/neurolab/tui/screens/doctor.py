"""Toolchain diagnostic doctor modal screen."""

from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, DataTable, Static
from ...core.doctor import run_diagnostics


class DoctorModal(ModalScreen):
    """Diagnostic doctor screen inspecting comp-neuro environment."""

    def compose(self):
        with Vertical(classes="modal-dialog", id="doctor-container"):
            yield Label("🩺 Computational Neuroscience Toolchain Doctor", classes="modal-title")
            yield Static("[dim]Diagnostics for C/C++ compilers, NEURON, Brian2, Nengo, snnTorch, CUDA, and JupyterLab[/dim]\n")
            
            yield DataTable(id="doctor-table")
            
            with Horizontal(classes="modal-buttons"):
                yield Button("🔄 Re-run Diagnostics", variant="default", id="btn-refresh")
                yield Button("✅ Close", variant="primary", id="btn-close")

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one("#doctor-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        
        table.add_columns("Status", "Tool / Component", "Category", "Version", "Details")
        
        checks = run_diagnostics()
        for check in checks:
            status_badge = {
                "OK": "[bold green]✔ PASS[/bold green]",
                "WARN": "[bold yellow]▲ WARN[/bold yellow]",
                "FAIL": "[bold red]✖ FAIL[/bold red]",
            }.get(check.status, check.status)

            table.add_row(
                status_badge,
                check.name,
                f"[dim]{check.category}[/dim]",
                check.version or "[dim]N/A[/dim]",
                check.details
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.refresh_table()
        else:
            self.dismiss()

    def on_key(self, event) -> None:
        if event.key in ("escape", "q", "enter"):
            self.dismiss()
