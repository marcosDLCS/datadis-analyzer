"""Console configuration, themes, and visual formatting utilities using Rich."""

from rich.console import Console
from rich.theme import Theme

# Custom cohesive palette for DATADIS energy terminal UI
CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "danger": "bold red",
        "success": "bold green",
        "highlight": "bold magenta",
        "metric": "bold bright_cyan",
        "dimmed": "dim white",
        "header": "bold white on dark_blue",
        "bar.high": "bold red",
        "bar.mid": "bold yellow",
        "bar.low": "bold green",
    }
)

console = Console(theme=CUSTOM_THEME)


def format_kwh(val: float) -> str:
    """Format energy value in kilowatt-hours with thousands separator and 2 decimal places."""
    return f"{val:,.2f} kWh"


def format_pct(val: float) -> str:
    """Format percentage value with 2 decimal places."""
    return f"{val:5.2f}%"


def make_share_bar(pct: float, width: int = 16) -> str:
    """Create a sleek visual block bar showing the percentage share.

    Args:
        pct: Percentage (0.0 to 100.0).
        width: Character width of the progress bar.

    Returns:
        Colorized string with filled and empty blocks.
    """
    pct_clamped = max(0.0, min(100.0, pct))
    filled_len = round((pct_clamped / 100.0) * width)
    empty_len = width - filled_len

    if pct >= 50.0:
        bar_color = "magenta"
    elif pct >= 15.0:
        bar_color = "yellow"
    elif pct > 0.0:
        bar_color = "cyan"
    else:
        bar_color = "dim"

    bar = "█" * filled_len + "░" * empty_len
    return f"[{bar_color}]{bar}[/{bar_color}]"
