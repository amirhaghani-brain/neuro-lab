"""2D Anatomical ASCII Brain Widget."""

from textual.widgets import Static
from rich.text import Text


class AsciiBrainWidget(Static):
    """Renders the regional 2D anatomical ASCII brain."""

    def render(self) -> Text:
        t = Text()
        # Row 1-5: Superior Cortex (Magenta)
        t.append("                 ___    ___\n", style="bold magenta")
        t.append("            ..\")\" ..\" `(``..\n", style="bold magenta")
        t.append("          .'; _..=. :: `-'.' ;`.\n", style="bold magenta")
        t.append("         : ) ;\"`':._::_.      ( :.\n", style="bold magenta")
        t.append("       .:-\"   _.  `\"", style="bold magenta")
        t.append("##", style="bold white")
        t.append("\"` \"._   `-:\\\n", style="bold magenta")
        
        # Row 6-11: Mid/Temporal Cortex (Cyan)
        t.append("      /.\"   -\"`  ._.::._. .'\"-   \".:\n", style="bold cyan")
        t.append("     : :    ( -: `\" :: \"` :- )    : )\n", style="bold cyan")
        t.append("    ( .\":==._' `'=._", style="bold cyan")
        t.append("##", style="bold white")
        t.append("_.='` '_.==: .'\n", style="bold cyan")
        t.append("    (:  `, `\"`    `\"", style="bold cyan")
        t.append("##", style="bold white")
        t.append("\"`    `\"` .'`\".)\n", style="bold cyan")
        t.append("     \\`'  `\"--.  \"- )( -\" ..--\"`  `-/\n", style="bold cyan")
        t.append("     (\" (_.\" =\"\"-...\"`...-\"\"= \"._) \")\n", style="bold cyan")
        
        # Row 12-14: Cerebellar Base (Yellow)
        t.append("      \"..__..-\"  )%", style="bold yellow")
        t.append("`..'", style="bold white")
        t.append("%(  \"-..__..\"\n", style="bold yellow")
        t.append("           (#\"...'\\", style="bold yellow")
        t.append("%%%%", style="bold white")
        t.append("/`...\"#)\n", style="bold yellow")
        t.append("            `######`--'######\"\n", style="bold yellow")
        
        # Row 15-17: Brainstem (Green)
        t.append("              \"###\")@@(`###\"\n", style="bold green")
        t.append("                   \\@@/\n", style="bold green")
        t.append("                    )(", style="bold green")
        return t
