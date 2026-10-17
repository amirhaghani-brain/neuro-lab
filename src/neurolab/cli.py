"""Neuro-Lab: Terminal-native computational neuroscience CLI command center."""

import os
import sys
import shutil
import time
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from .core.workspace import (
    TOOLS,
    ToolDefinition,
    resolve_workspace_root,
    ensure_workspace_dirs,
    create_file_from_template,
    list_tool_files,
    list_workspace_registry,
    find_all_workspace_files,
    discover_projects,
    scaffold_new_project,
)
from .core.doctor import run_diagnostics
from .core.telemetry import get_system_telemetry, get_daily_concept
from .core.launcher import (
    launch_jupyter,
    launch_nengo_gui,
    run_script_interactive,
    open_in_editor,
    get_default_editor,
    get_editor_name,
)

console = Console()


def get_terminal_width() -> int:
    """Get current active terminal width with sensible defaults."""
    try:
        if console and hasattr(console, "width") and console.width:
            return max(40, console.width)
        cols, _ = shutil.get_terminal_size((80, 24))
        return max(40, cols)
    except Exception:
        return 80


def print_section_divider(title: str, width: int):
    """Print an adaptive horizontal divider line that scales to terminal width."""
    prefix = f"─── {title} " if title else "───"
    dash_count = max(0, width - len(prefix) - 1)
    console.print(f"[bold cyan]{prefix}{'─' * dash_count}[/bold cyan]")


def get_ascii_brain_text() -> Text:
    """Render 2D Anatomical ASCII Brain in clean terminal colors."""
    t = Text()
    # Superior Cortex (Magenta)
    t.append("                 ___    ___\n", style="bold magenta")
    t.append("            ..\")\" ..\" `(``..\n", style="bold magenta")
    t.append("          .'; _..=. :: `-'.' ;`.\n", style="bold magenta")
    t.append("         : ) ;\"`':._::_.      ( :.\n", style="bold magenta")
    t.append("       .:-\"   _.  `\"", style="bold magenta")
    t.append("##", style="bold white")
    t.append("\"` \"._   `-:\\\n", style="bold magenta")
    
    # Mid/Temporal Cortex (Cyan)
    t.append("      /.\"   -\"`  ._.::._. .'\"-   \".:\n", style="bold cyan")
    t.append("     : :    ( -: `\" :: \"` :- )    : )\n", style="bold cyan")
    t.append("    ( .\":==._' `'=._", style="bold cyan")
    t.append("##", style="bold white")
    t.append("_.='` '_.==: .'\n", style="bold cyan")
    t.append("    (:  `, `\"`    `\"", style="bold cyan")
    t.append("##", style="bold white")
    t.append("\"`    `\"` .'`\".)\n", style="bold cyan")
    t.append("     \\`'  `\"--.  \"- )( -\" ..--\"`  `-/\n", style="bold cyan")
    t.append('     (" (_." =""-..."`...-""= "._) ")\n', style="bold cyan")
    
    # Cerebellar Base (Yellow)
    t.append("      \"..__..-\"  )%", style="bold yellow")
    t.append("`..'", style="bold white")
    t.append("%(  \"-..__..\"\n", style="bold yellow")
    t.append("           (#\"...'\\", style="bold yellow")
    t.append("%%%%", style="bold white")
    t.append("/`...\"#)\n", style="bold yellow")
    t.append("            `######`--'######\"\n", style="bold yellow")
    
    # Brainstem (Green)
    t.append("              \"###\")@@(`###\"\n", style="bold green")
    t.append("                   \\@@/\n", style="bold green")
    t.append("                    )(", style="bold green")
    return t


def print_banner(workspace: Path):
    """Adaptive dashboard banner responsive to any terminal window dimensions."""
    width = get_terminal_width()
    telemetry = get_system_telemetry(workspace)
    concept = get_daily_concept()
    brain_text = get_ascii_brain_text()
    editor_name = get_editor_name()

    # Build Telemetry Panel
    tele_table = Table.grid(padding=(0, 1))
    tele_table.add_column("Key", style="bold cyan", no_wrap=True)
    tele_table.add_column("Val", style="bold white")
    tele_table.add_row("Workspace", str(workspace))
    tele_table.add_row("Python", f"v{telemetry['python_version']} (Virtualenv)")
    tele_table.add_row("Editor", f"[green]{editor_name}[/green]")
    tele_table.add_row("Compute", f"[green]{telemetry['cuda_status']}[/green]   [bold cyan]RAM:[/bold cyan] {telemetry['ram_usage']}")
    tele_table.add_row("Models", f"{telemetry['model_count']} scripts / {telemetry['notebook_count']} notebooks")

    telemetry_panel = Panel(
        tele_table,
        title="[bold magenta]NEURO-LAB // TELEMETRY[/bold magenta]",
        border_style="magenta",
        padding=(0, 1),
        expand=True
    )

    # Build Daily Foundation Panel
    daily_text = Text()
    daily_text.append(f"[*] {concept['title']}\n", style="bold yellow")
    daily_text.append(f"    {concept['formula']}\n", style="bold white")
    daily_text.append(f"    {concept['desc']}", style="dim")

    daily_panel = Panel(
        daily_text,
        title="[bold yellow]DAILY NEUROSCIENCE FOUNDATION[/bold yellow]",
        border_style="yellow",
        padding=(0, 1),
        expand=True
    )

    # Adaptive Layout Selection
    if width >= 94:
        # Side-by-side Hero Layout on wide terminals
        side_table = Table.grid(padding=(0, 2), expand=True)
        side_table.add_column("Brain", width=42, no_wrap=True)
        side_table.add_column("Info", ratio=1)

        info_stack = Table.grid(padding=(0, 0), expand=True)
        info_stack.add_row(telemetry_panel)
        info_stack.add_row(daily_panel)

        side_table.add_row(brain_text, info_stack)
        console.print(side_table)
    else:
        # Stacked Responsive Layout on compact terminals
        console.print(brain_text)
        console.print()
        console.print(telemetry_panel)
        console.print(daily_panel)

    console.print()

    # Adaptive Toolchains Table
    print_section_divider("TOOLCHAINS & WORKSPACE BRIDGES", width)

    tool_table = Table(box=None, expand=True, padding=(0, 1), show_header=False)
    tool_table.add_column("Key", style="bold yellow", width=5, no_wrap=True)
    tool_table.add_column("Name", style="bold white", width=14, no_wrap=True)
    tool_table.add_column("Description", style="dim")
    tool_table.add_column("Folder", style="dim cyan", justify="right", no_wrap=True)
    tool_table.add_column("Files", style="green", justify="right", width=10, no_wrap=True)

    tool_keys = [
        ("1", "jupyter", "JupyterLab", "Interactive computational notebooks (.ipynb)", "notebooks/"),
        ("2", "brian2", "Brian 2", "ODE point biophysics & spiking networks (.py)", "models/"),
        ("3", "neuron", "NEURON", "Multicompartment 3D cable simulation (.py, .hoc, .mod)", "models/"),
        ("4", "nengo", "Nengo & GUI", "Cognitive architectures & NEF representations (.py)", "models/"),
        ("5", "snntorch", "snnTorch", "PyTorch spiking neural network training (.py)", "models/"),
        ("6", "neo", "Neo / Elephant", "Electrophysiology I/O & spike train statistics (.py)", "analysis/"),
    ]

    for key, tool_id, name, desc, dir_path in tool_keys:
        files = list_tool_files(tool_id, workspace, include_unclassified=False)
        cnt_str = f"[{len(files)} file{'s' if len(files) != 1 else ''}]"
        tool_table.add_row(f"[{key}]", name, desc, dir_path, cnt_str)

    console.print(tool_table)
    console.print()

    # Adaptive Command Matrix (Including [f] Find File, [p] Projects, [e] LazyVim)
    print_section_divider("SHORTCUTS & COMMANDS", width)

    cmd_grid = Table.grid(padding=(0, 1), expand=True)
    if width >= 100:
        cmd_grid.add_column("C1", ratio=1)
        cmd_grid.add_column("C2", ratio=1)
        cmd_grid.add_column("C3", ratio=1)
        cmd_grid.add_column("C4", ratio=1)
        cmd_grid.add_row(
            "[[bold yellow]1-6[/bold yellow]] Tool bridge",
            "[[bold yellow]f[/bold yellow]]   Find file",
            "[[bold yellow]p[/bold yellow]]   Projects manager",
            "[[bold yellow]e[/bold yellow]]   Editor (LazyVim)"
        )
        cmd_grid.add_row(
            "[[bold yellow]r[/bold yellow]]   Run script",
            "[[bold yellow]n[/bold yellow]]   New template",
            "[[bold yellow]d[/bold yellow]]   Doctor diag",
            "[[bold yellow]q[/bold yellow]]   Quit to shell"
        )
    else:
        cmd_grid.add_column("C1", ratio=1)
        cmd_grid.add_column("C2", ratio=1)
        cmd_grid.add_row(
            "[[bold yellow]1-6[/bold yellow]] Tool bridge",
            "[[bold yellow]f[/bold yellow]] Find file"
        )
        cmd_grid.add_row(
            "[[bold yellow]p[/bold yellow]]   Projects manager",
            "[[bold yellow]e[/bold yellow]] Editor (LazyVim)"
        )
        cmd_grid.add_row(
            "[[bold yellow]r[/bold yellow]]   Run script",
            "[[bold yellow]n[/bold yellow]] New template"
        )
        cmd_grid.add_row(
            "[[bold yellow]d[/bold yellow]]   Doctor diag",
            "[[bold yellow]q[/bold yellow]] Quit to shell"
        )

    console.print(cmd_grid)
    dash_line = "─" * max(0, width - 1)
    console.print(f"[dim]{dash_line}[/dim]")


def safe_prompt(prompt_text: str = "") -> str:
    """Safe input prompt handling EOF and interrupts cleanly."""
    try:
        return input(prompt_text).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def handle_tool_interactive(tool_id: str, workspace: Path):
    """Interactive bridge flow for a chosen tool."""
    if tool_id not in TOOLS:
        console.print(f"[bold red][-] Unknown tool: {tool_id}[/bold red]")
        return

    tool = TOOLS[tool_id]
    files = list_tool_files(tool_id, workspace)
    editor_name = get_editor_name()

    console.print(f"\n[bold cyan]=== [ {tool.name} Bridge ] ===[/bold cyan]")
    console.print(f"[dim]Description :[/dim] {tool.description}")
    console.print(f"[dim]Directory   :[/dim] {tool.target_dir}/")
    console.print(f"[dim]Template    :[/dim] {tool.template_name}")
    console.print(f"[dim]Found files :[/dim] {len(files)}")
    console.print()

    console.print("  [1] Create new file from standard template")
    if files:
        console.print(f"  [2] Select existing file ({len(files)} available)")
    else:
        console.print("  [2] Select existing file (None found)")
    console.print("  [b] Back to main prompt")
    console.print()

    choice = safe_prompt("Select option [1/2/b]: ").lower()
    if choice in ("b", "back", "q", "exit", ""):
        return

    if choice == "1":
        # Create new file
        default_name = tool.default_filename
        name_input = safe_prompt(f"Enter filename [{default_name}]: ")
        filename = name_input if name_input else default_name

        created = create_file_from_template(tool.id, filename, workspace)
        console.print(f"[bold green][+] Created:[/bold green] {created.relative_to(workspace) if created.is_relative_to(workspace) else created}")

        if tool_id == "jupyter":
            action = safe_prompt("Launch in JupyterLab? [Y/n]: ").lower()
            if action not in ("n", "no"):
                console.print(f"[bold cyan][>] Starting JupyterLab...[/bold cyan]")
                launch_jupyter(created)
                console.print(f"[bold green][+] JupyterLab running in background for {created.name}[/bold green]")
        elif tool_id == "nengo":
            console.print("\nLaunch action:")
            console.print("  [1] Launch in Nengo GUI (Browser: http://localhost:8080)")
            console.print(f"  [2] Open in {editor_name}")
            console.print("  [3] Return to prompt")
            act = safe_prompt("Action [1/2/3]: ")
            if act == "1":
                launch_nengo_gui(created)
                console.print(f"[bold green][+] Nengo GUI started at http://localhost:8080[/bold green]")
            elif act == "2":
                open_in_editor(created)
        else:
            console.print("\nLaunch action:")
            console.print("  [1] Run in terminal")
            console.print(f"  [2] Open in {editor_name}")
            console.print("  [3] Return to prompt")
            act = safe_prompt("Action [1/2/3]: ")
            if act == "1":
                run_script_interactive(created)
            elif act == "2":
                open_in_editor(created)

    elif choice == "2":
        if not files:
            console.print("[yellow][!] No matching files found in workspace.[/yellow]")
            return

        console.print(f"\n[bold cyan]Existing {tool.name} Files:[/bold cyan]")
        for idx, f in enumerate(files, 1):
            rel = f.relative_to(workspace) if f.is_relative_to(workspace) else f
            console.print(f"  [{idx}] {rel}")
        console.print()

        f_choice = safe_prompt(f"Select file [1-{len(files)}/b]: ")
        if f_choice.lower() in ("b", "back", ""):
            return

        try:
            f_idx = int(f_choice) - 1
            if 0 <= f_idx < len(files):
                selected_file = files[f_idx]
            else:
                console.print("[bold red][-] Invalid selection.[/bold red]")
                return
        except ValueError:
            matched = [f for f in files if f_choice in f.name]
            if matched:
                selected_file = matched[0]
            else:
                console.print("[bold red][-] File not found.[/bold red]")
                return

        if tool_id == "jupyter":
            console.print(f"[bold cyan][>] Opening {selected_file.name} in JupyterLab...[/bold cyan]")
            launch_jupyter(selected_file)
            console.print("[bold green][+] JupyterLab process launched.[/bold green]")
        elif tool_id == "nengo":
            console.print("\nAction:")
            console.print("  [1] Launch Nengo GUI")
            console.print(f"  [2] Open in {editor_name}")
            console.print("  [3] Run headless")
            act = safe_prompt("Select [1-3]: ")
            if act == "1":
                launch_nengo_gui(selected_file)
                console.print(f"[bold green][+] Nengo GUI started at http://localhost:8080[/bold green]")
            elif act == "2":
                open_in_editor(selected_file)
            elif act == "3":
                run_script_interactive(selected_file)
        else:
            console.print("\nAction:")
            console.print("  [1] Run in terminal")
            console.print(f"  [2] Open in {editor_name}")
            act = safe_prompt("Select [1/2]: ")
            if act == "1":
                run_script_interactive(selected_file)
            elif act == "2":
                open_in_editor(selected_file)


def cmd_find_file(workspace: Path):
    """Interactive fuzzy file finder across workspace."""
    editor_name = get_editor_name()
    console.print(f"\n[bold cyan]=== [ Find File in Workspace: {workspace.name} ] ===[/bold cyan]\n")
    
    query = safe_prompt("Search query (or press Enter to list all files): ")
    files = find_all_workspace_files(workspace, query)

    if not files:
        console.print(f"[yellow][!] No files matching '{query}' found in workspace.[/yellow]")
        return

    table = Table(box=None, expand=True, padding=(0, 1))
    table.add_column("#", style="bold yellow", width=4, no_wrap=True)
    table.add_column("File Path", style="bold white")
    table.add_column("Size", style="dim", justify="right", width=10, no_wrap=True)
    table.add_column("Folder", style="dim cyan", justify="right", width=12, no_wrap=True)

    for idx, f in enumerate(files, 1):
        try:
            rel = f.relative_to(workspace)
        except ValueError:
            rel = f
        size_kb = f.stat().st_size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb >= 1 else f"{f.stat().st_size} B"
        folder_str = rel.parts[0] if len(rel.parts) > 1 else "./"
        table.add_row(f"[{idx}]", str(rel), size_str, folder_str)

    console.print(table)
    console.print()

    choice = safe_prompt(f"Select file [1-{len(files)}/b]: ")
    if choice.lower() in ("b", "back", "q", "exit", ""):
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            selected = files[idx]
        else:
            console.print("[bold red][-] Invalid selection.[/bold red]")
            return
    except ValueError:
        matched = [f for f in files if choice in f.name]
        if matched:
            selected = matched[0]
        else:
            console.print("[bold red][-] File not found.[/bold red]")
            return

    console.print(f"\n[bold cyan]Action for {selected.name}:[/bold cyan]")
    console.print(f"  [1] Open in {editor_name}")
    if selected.suffix.lower() == ".py":
        console.print("  [2] Run in terminal")
    elif selected.suffix.lower() == ".ipynb":
        console.print("  [2] Open in JupyterLab")
    else:
        console.print("  [2] View contents (cat)")
    console.print("  [b] Back")

    act = safe_prompt("Select [1/2/b]: ")
    if act == "1":
        open_in_editor(selected)
    elif act == "2":
        if selected.suffix.lower() == ".py":
            run_script_interactive(selected)
        elif selected.suffix.lower() == ".ipynb":
            launch_jupyter(selected)
            console.print(f"[bold green][+] Opening {selected.name} in JupyterLab...[/bold green]")
        else:
            console.print(f"\n[bold cyan]--- Content: {selected.name} ---[/bold cyan]")
            console.print(selected.read_text(encoding="utf-8", errors="replace")[:1000])


def cmd_projects(current_workspace: Path) -> Path:
    """Multi-project workspace manager: list, switch, and scaffold research projects."""
    console.print(f"\n[bold cyan]=== [ Computational Neuroscience Projects ] ===[/bold cyan]")
    console.print(f"[dim]Active Workspace:[/dim] [bold white]{current_workspace}[/bold white]\n")

    projects = discover_projects()
    if current_workspace not in projects:
        projects.insert(0, current_workspace)

    console.print("[bold cyan]Discovered Research Workspaces:[/bold cyan]")
    for idx, p in enumerate(projects, 1):
        is_active = (p == current_workspace)
        marker = "[bold green][ACTIVE][/bold green]" if is_active else "        "
        tele = get_system_telemetry(p)
        console.print(f"  [{idx}] {marker} [bold white]{p.name:<18}[/bold white] [dim]{str(p):<36}[/dim] [{tele['model_count']} models, {tele['notebook_count']} notebooks]")

    console.print("\nActions:")
    console.print("  [1] Switch active workspace")
    console.print("  [2] Create new research project directory")
    console.print("  [3] Project statistics & overview")
    console.print("  [b] Back to main prompt\n")

    choice = safe_prompt("Select action [1/2/3/b]: ").lower()
    if choice in ("b", "back", "q", "exit", ""):
        return current_workspace

    if choice == "1":
        target = safe_prompt(f"Select project number [1-{len(projects)}] or enter custom path: ")
        if target.isdigit() and 1 <= int(target) <= len(projects):
            new_ws = projects[int(target) - 1]
            console.print(f"[bold green][+] Switched active workspace to: {new_ws}[/bold green]")
            return new_ws
        elif target:
            custom_path = Path(target).expanduser().resolve()
            if custom_path.exists() and custom_path.is_dir():
                ensure_workspace_dirs(custom_path)
                console.print(f"[bold green][+] Switched active workspace to: {custom_path}[/bold green]")
                return custom_path
            else:
                console.print(f"[bold red][-] Path does not exist: {custom_path}[/bold red]")

    elif choice == "2":
        name = safe_prompt("Enter new project name (e.g. thalamus-cortex): ")
        if not name:
            return current_workspace
        
        parent_dir = Path.home() / "Work" if (Path.home() / "Work").exists() else Path.home()
        custom_parent = safe_prompt(f"Parent directory [{parent_dir}]: ")
        if custom_parent:
            parent_dir = Path(custom_parent).expanduser().resolve()

        new_project_path = parent_dir / name
        scaffold_new_project(new_project_path, name)
        console.print(f"[bold green][+] Created new comp-neuro project at: {new_project_path}[/bold green]")
        
        switch = safe_prompt("Switch to this project now? [Y/n]: ").lower()
        if switch not in ("n", "no"):
            return new_project_path

    elif choice == "3":
        tele = get_system_telemetry(current_workspace)
        console.print(f"\n[bold cyan]=== Project Analytics: {current_workspace.name} ===[/bold cyan]")
        console.print(f"  [•] Location        : {current_workspace}")
        console.print(f"  [•] Total Models    : {tele['model_count']} Python simulation scripts")
        console.print(f"  [•] Total Notebooks : {tele['notebook_count']} JupyterLab notebooks")
        
        # Calculate approximate lines of code
        loc = 0
        for f in find_all_workspace_files(current_workspace):
            if f.suffix in (".py", ".hoc", ".mod", ".json"):
                try:
                    loc += sum(1 for _ in f.open("r", encoding="utf-8", errors="ignore"))
                except Exception:
                    pass
        console.print(f"  [•] Code Volume     : ~{loc:,} lines of model / analysis code\n")
        safe_prompt("Press Enter to return...")

    return current_workspace


def cmd_editor(workspace: Path, file_arg: Optional[str] = None):
    """Launch LazyVim / Neovim on workspace or specific file."""
    editor_name = get_editor_name()
    if file_arg:
        target = Path(file_arg)
        if not target.is_absolute():
            target = workspace / target
        if not target.exists():
            for sub in ["models", "analysis", "notebooks", ""]:
                cand = workspace / sub / file_arg
                if cand.exists():
                    target = cand
                    break
        console.print(f"[bold cyan][>] Opening {target.name} in {editor_name}...[/bold cyan]")
        open_in_editor(target)
    else:
        console.print(f"[bold cyan][>] Opening workspace in {editor_name}...[/bold cyan]")
        open_in_editor(workspace)


def cmd_doctor(checks: Optional[List] = None):
    """Run environment and toolchain diagnostic checks."""
    console.print("\n[bold cyan]=== [ Toolchain Diagnostics ] ===[/bold cyan]\n")

    width = get_terminal_width()
    show_category = width >= 110

    table = Table(box=None, expand=True, padding=(0, 1))
    table.add_column("Status", justify="left", width=8, no_wrap=True)
    table.add_column("Component", style="bold white", width=18, no_wrap=True)
    if show_category:
        table.add_column("Category", style="dim", width=22, no_wrap=True)
    table.add_column("Version", style="green", width=16, no_wrap=True)
    # Keep each check on one line; long details are expanded in the notes below.
    table.add_column("Details", ratio=1, no_wrap=True, overflow="ellipsis")

    checks = run_diagnostics() if checks is None else checks
    for check in checks:
        status_badge = {
            "OK": "[bold green][PASS][/bold green]",
            "WARN": "[bold yellow][WARN][/bold yellow]",
            "FAIL": "[bold red][FAIL][/bold red]",
        }.get(check.status, check.status)

        row: List[str] = [status_badge, check.name]
        if show_category:
            row.append(check.category)
        row.append(check.version or "[dim]N/A[/dim]")
        row.append(check.details)
        table.add_row(*row)

    console.print(table)
    console.print()

    # Expand anything that is not OK so the actionable text is never truncated.
    problems = [c for c in checks if c.status != "OK"]
    if problems:
        console.print("[bold yellow]Attention needed:[/bold yellow]")
        for check in problems:
            badge = "[bold red]FAIL[/bold red]" if check.status == "FAIL" else "[bold yellow]WARN[/bold yellow]"
            console.print(f"  {badge} [bold white]{check.name}[/bold white] - {check.details}")
        console.print()
    else:
        console.print("[bold green]All checks passed.[/bold green]\n")


def cmd_list(workspace: Path):
    """List all computational neuroscience models and notebooks in the workspace."""
    console.print(f"\n[bold cyan]=== [ Workspace File Registry: {workspace} ] ===[/bold cyan]\n")

    registry = list_workspace_registry(workspace)

    for group, files in registry.items():
        if group == "unclassified":
            console.print("[bold white][shared][/bold white] Unclassified Python models:")
        elif group == "root":
            console.print("[bold white][root][/bold white] Workspace root scripts:")
        else:
            tool = TOOLS[group]
            console.print(f"[bold {tool.color}][{tool.tag}][/bold {tool.color}] {tool.name} ({tool.target_dir}/):")

        for f in files:
            try:
                rel = f.relative_to(workspace)
            except ValueError:
                rel = f
            console.print(f"   [•] {rel}")
        console.print()

    if not registry:
        console.print("[dim]No model or notebook files found in workspace yet.[/dim]\n")


def cmd_run(arg: str, workspace: Path) -> int:
    """Run a specified simulation file. Returns the child process exit code."""
    p = Path(arg)
    if not p.is_absolute():
        p = workspace / p
    
    if not p.exists():
        for sub in ["models", "analysis", ""]:
            cand = workspace / sub / arg
            if cand.exists():
                p = cand
                break

    if not p.exists():
        console.print(f"[bold red][-] File not found: {arg}[/bold red]")
        return 1

    return run_script_interactive(p)


def print_help():
    """Print command reference."""
    editor_name = get_editor_name()
    console.print("\n[bold cyan]=== [ Neuro-Lab Command Reference ] ===[/bold cyan]")
    console.print("  [bold yellow]1[/bold yellow] | [bold white]jupyter[/bold white]         Open JupyterLab bridge (.ipynb)")
    console.print("  [bold yellow]2[/bold yellow] | [bold white]brian2[/bold white]          Open Brian 2 biophysics bridge (.py)")
    console.print("  [bold yellow]3[/bold yellow] | [bold white]neuron[/bold white]          Open NEURON cable morphology bridge (.py, .hoc, .mod)")
    console.print("  [bold yellow]4[/bold yellow] | [bold white]nengo[/bold white]           Open Nengo & GUI bridge (.py)")
    console.print("  [bold yellow]5[/bold yellow] | [bold white]snntorch[/bold white]        Open snnTorch deep SNN bridge (.py)")
    console.print("  [bold yellow]6[/bold yellow] | [bold white]neo[/bold white]             Open Neo / Elephant electrophysiology bridge (.py)")
    console.print(f"  [bold yellow]e[/bold yellow] | [bold white]editor [f][/bold white]     Open {editor_name} on workspace or specific file")
    console.print("  [bold yellow]f[/bold yellow] | [bold white]find[/bold white]           Search and locate any file across workspace")
    console.print("  [bold yellow]p[/bold yellow] | [bold white]projects[/bold white]       Switch workspace or scaffold new research project")
    console.print("  [bold yellow]d[/bold yellow] | [bold white]doctor[/bold white]         Run system & toolchain diagnostic check")
    console.print("  [bold yellow]l[/bold yellow] | [bold white]list[/bold white] | [bold white]ls[/bold white]       List all workspace models and notebooks")
    console.print("  [bold yellow]r[/bold yellow] | [bold white]run <file>[/bold white]     Execute a Python simulation script in terminal")
    console.print("  [bold yellow]n[/bold yellow] | [bold white]new <tool> [f][/bold white] Scaffold a new model or notebook from template")
    console.print("  [bold yellow]t[/bold yellow] | [bold white]theory[/bold white]         Display today's computational neuroscience principle")
    console.print("  [bold yellow]c[/bold yellow] | [bold white]clear[/bold white]          Clear screen and redraw dashboard")
    console.print("  [bold yellow]q[/bold yellow] | [bold white]quit[/bold white] | [bold white]exit[/bold white]     Exit Neuro-Lab")
    console.print()


def interactive_repl(workspace: Path):
    """Main interactive developer CLI prompt."""
    ensure_workspace_dirs(workspace)
    print_banner(workspace)

    completer = WordCompleter([
        "1", "2", "3", "4", "5", "6",
        "jupyter", "brian2", "neuron", "nengo", "snntorch", "neo",
        "editor", "nvim", "lazyvim", "find", "projects",
        "doctor", "list", "ls", "run", "edit", "new", "theory", "clear", "help", "quit", "exit"
    ], ignore_case=True)

    session = PromptSession(completer=completer)

    tool_shortcuts = {
        "1": "jupyter",
        "2": "brian2",
        "3": "neuron",
        "4": "nengo",
        "5": "snntorch",
        "6": "neo",
    }

    current_ws = workspace

    while True:
        try:
            line = session.prompt([("class:prompt", f"\nneurolab [{current_ws.name}] > ")]).strip()
        except KeyboardInterrupt:
            console.print()
            continue
        except EOFError:
            console.print("\nExiting Neuro-Lab.")
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        # Number shortcuts
        if cmd in tool_shortcuts:
            handle_tool_interactive(tool_shortcuts[cmd], current_ws)
        elif cmd in TOOLS:
            handle_tool_interactive(cmd, current_ws)
        elif cmd in ("f", "find", "search"):
            cmd_find_file(current_ws)
        elif cmd in ("p", "proj", "projects", "workspace"):
            current_ws = cmd_projects(current_ws)
        elif cmd in ("e", "edit", "editor", "nvim", "lazyvim", "vim"):
            cmd_editor(current_ws, arg if arg else None)
        elif cmd in ("d", "doctor", "diag", "check"):
            cmd_doctor()
        elif cmd in ("l", "ls", "list"):
            cmd_list(current_ws)
        elif cmd in ("r", "run"):
            if arg:
                cmd_run(arg, current_ws)
            else:
                files = list_tool_files("brian2", current_ws) + list_tool_files("neuron", current_ws) + list_tool_files("nengo", current_ws)
                if not files:
                    console.print("[yellow][!] No Python model scripts found to run.[/yellow]")
                else:
                    console.print("\nAvailable scripts:")
                    for idx, f in enumerate(files, 1):
                        console.print(f"  [{idx}] {f.relative_to(current_ws) if f.is_relative_to(current_ws) else f}")
                    f_choice = safe_prompt(f"\nSelect script to run [1-{len(files)}/b]: ")
                    if f_choice.isdigit() and 1 <= int(f_choice) <= len(files):
                        run_script_interactive(files[int(f_choice) - 1])
        elif cmd in ("n", "new"):
            if arg:
                sub_parts = arg.split(maxsplit=1)
                t_id = sub_parts[0].lower()
                fname = sub_parts[1] if len(sub_parts) > 1 else None
                if t_id in TOOLS:
                    tool = TOOLS[t_id]
                    target_name = fname or tool.default_filename
                    created = create_file_from_template(tool.id, target_name, current_ws)
                    console.print(f"[bold green][+] Created {tool.name} template:[/bold green] {created}")
                else:
                    console.print(f"[bold red][-] Unknown tool '{t_id}'. Choose from: {', '.join(TOOLS.keys())}[/bold red]")
            else:
                console.print("Available templates: " + ", ".join(TOOLS.keys()))
                t_id = safe_prompt("Choose tool template: ").lower()
                if t_id in TOOLS:
                    handle_tool_interactive(t_id, current_ws)
        elif cmd in ("t", "theory", "concept"):
            concept = get_daily_concept()
            console.print(f"\n[bold cyan]=== [ Daily Neuroscience Foundation ] ===[/bold cyan]")
            console.print(f" [*] [bold yellow]{concept['title']}[/bold yellow]")
            console.print(f"     [bold white]{concept['formula']}[/bold white]")
            console.print(f"     [dim]{concept['desc']}[/dim]\n")
        elif cmd in ("c", "clear", "cls"):
            os.system("clear" if os.name == "posix" else "cls")
            print_banner(current_ws)
        elif cmd in ("h", "help", "?"):
            print_help()
        elif cmd in ("q", "quit", "exit", "bye"):
            console.print("Exiting Neuro-Lab. Goodbye.\n")
            break
        else:
            console.print(f"[dim]Unknown command '{cmd}'. Type [/dim][bold white]help[/bold white][dim] or press [/dim][bold yellow]1-6[/bold yellow][dim].[/dim]")


# --- Click Subcommands for Direct CLI Usage ---


def launch_tui(workspace: Path):
    """Launch the full-screen Textual dashboard."""
    from .tui.app import NeuroLabApp

    NeuroLabApp(workspace_path=workspace).run()


def is_interactive_terminal() -> bool:
    """True when both stdin and stdout are attached to a real terminal."""
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except (AttributeError, ValueError):
        return False


@click.group(invoke_without_command=True)
@click.option("--workspace", "-w", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path), help="Custom workspace directory path")
@click.pass_context
def main(ctx, workspace):
    """Neuro-Lab: Terminal-native computational neuroscience workspace."""
    workspace_path = (workspace or resolve_workspace_root()).resolve()
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = workspace_path

    if ctx.invoked_subcommand is None:
        # Default to the full-screen TUI on a real terminal, and fall back to
        # the scriptable prompt shell when piped (CI, tests, redirection).
        if is_interactive_terminal():
            launch_tui(workspace_path)
        else:
            interactive_repl(workspace_path)


@main.command()
@click.pass_context
def tui(ctx):
    """Launch the full-screen Textual dashboard."""
    launch_tui(ctx.obj["workspace"])


@main.command(name="shell")
@click.pass_context
def shell(ctx):
    """Launch the classic prompt-toolkit command shell."""
    interactive_repl(ctx.obj["workspace"])


@main.command()
@click.pass_context
def doctor(ctx):
    """Run environment and toolchain diagnostic checks."""
    cmd_doctor()


@main.command(name="list")
@click.pass_context
def list_cmd(ctx):
    """List all computational models and notebooks in the workspace."""
    cmd_list(ctx.obj["workspace"])


@main.command()
@click.argument("file_path", required=False)
@click.pass_context
def find(ctx, file_path):
    """Search and locate files across workspace."""
    cmd_find_file(ctx.obj["workspace"])


@main.command()
@click.pass_context
def projects(ctx):
    """Manage computational neuroscience projects and workspaces."""
    cmd_projects(ctx.obj["workspace"])


@main.command()
@click.argument("file_path", required=False)
@click.pass_context
def editor(ctx, file_path):
    """Open LazyVim / Neovim on workspace or specific file."""
    cmd_editor(ctx.obj["workspace"], file_path)


@main.command()
@click.argument("file_path")
@click.pass_context
def run(ctx, file_path):
    """Execute a simulation script in the terminal."""
    ctx.exit(cmd_run(file_path, ctx.obj["workspace"]))


@main.command()
@click.argument("tool_id", type=click.Choice(list(TOOLS.keys()), case_sensitive=False))
@click.argument("filename", required=False)
@click.pass_context
def new(ctx, tool_id, filename):
    """Scaffold a new model or notebook from standard template."""
    ws: Path = ctx.obj["workspace"]
    tool = TOOLS[tool_id.lower()]
    target_name = filename or tool.default_filename
    
    created_path = create_file_from_template(tool.id, target_name, ws)
    console.print(f"[bold green][+] Created {tool.name} template:[/bold green] [cyan]{created_path}[/cyan]\n")


if __name__ == "__main__":
    main()
