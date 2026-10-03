"""Terminal views, tables, cards, and help screens rendered with Rich."""

import sys
from pathlib import Path

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.i18n import get_month_name, t
from src.ingestion.schema import ValidationResult
from src.presentation.console import console, format_kwh, format_pct, make_share_bar
from src.processing.models import (
    CommunitySummary,
    ComparisonSummary,
)
from src.version import get_version


def render_help(lang: str | None = None) -> None:
    """Render a comprehensive, formatted help screen for the DATADIS CLI tool."""
    title_text = Text()
    title_text.append(f"{t('app_title', lang=lang)} ", style="bold yellow")
    title_text.append(f"(da v{get_version()})", style="bold cyan")
    title_text.append(f"\n{t('app_subtitle', lang=lang)}", style="dim italic")

    console.print()
    console.print(
        Panel(
            Align.center(title_text),
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # Overview
    console.print(
        f"[bold cyan]{t('overview_heading', lang=lang)}[/bold cyan]\n{t('overview_text', lang=lang)}\n"
    )

    # Commands Table
    cmd_table = Table(
        title=f"[bold yellow]{t('available_commands', lang=lang)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=False,
    )
    cmd_table.add_column(t("cmd_name", lang=lang), style="bold green", no_wrap=True, width=16)
    cmd_table.add_column(t("cmd_desc", lang=lang), style="white")

    cmd_table.add_row(
        "da summary",
        t("cmd_summary_desc", lang=lang),
    )
    cmd_table.add_row(
        "da compare",
        t("cmd_compare_desc", lang=lang),
    )
    cmd_table.add_row(
        "da init",
        t("cmd_init_desc", lang=lang),
    )
    cmd_table.add_row(
        "da cleanup",
        t("cmd_cleanup_desc", lang=lang),
    )
    cmd_table.add_row(
        "da help",
        t("cmd_help_desc", lang=lang),
    )
    cmd_table.add_row(
        "da version",
        t("cmd_version_desc", lang=lang),
    )
    console.print(cmd_table)
    console.print()

    # Options Table
    opts_table = Table(
        title=f"[bold yellow]{t('options_title', lang=lang)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    opts_table.add_column(t("opt_name", lang=lang), style="bold green", no_wrap=True, width=16)
    opts_table.add_column(t("opt_type", lang=lang), style="cyan", no_wrap=True, width=10)
    opts_table.add_column(t("opt_default", lang=lang), style="dim", no_wrap=True, width=10)
    opts_table.add_column(t("opt_desc", lang=lang), style="white")

    opts_table.add_row(
        "-i, --input-dir",
        "PATH",
        "./.input",
        t("opt_input_dir", lang=lang),
    )
    opts_table.add_row(
        "-y, --year",
        "INTEGER",
        "All",
        t("opt_year", lang=lang),
    )
    opts_table.add_row(
        "-v, --view",
        "CHOICE",
        "all",
        t("opt_view", lang=lang),
    )
    opts_table.add_row(
        "-c, --cups",
        "STRING",
        "None",
        t("opt_cups", lang=lang),
    )
    opts_table.add_row(
        "-l, --lang",
        "CHOICE",
        "config",
        t("opt_lang", lang=lang),
    )
    console.print(opts_table)
    console.print()

    # Folder Structure & Examples in Panels
    console.print(
        Panel(
            t("data_layout_desc", lang=lang),
            title=t("data_layout_title", lang=lang),
            border_style="blue",
            box=box.ROUNDED,
        )
    )
    console.print()
    # Quick Start Examples Table
    examples_table = Table(
        title=f"[bold yellow]{t('quick_start_title', lang=lang)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=False,
    )
    examples_table.add_column(
        t("quick_start_col_cmd", lang=lang),
        style="bold green",
        no_wrap=True,
    )
    examples_table.add_column(
        t("quick_start_col_desc", lang=lang),
        style="white",
    )

    examples_table.add_row("da init --language es", t("quick_start_ex_init", lang=lang))
    examples_table.add_row("da summary", t("quick_start_ex_summary", lang=lang))
    examples_table.add_row("da summary --year 2025", t("quick_start_ex_year", lang=lang))
    examples_table.add_row("da summary --view monthly", t("quick_start_ex_monthly", lang=lang))
    examples_table.add_row(
        "da summary --cups ES0021000000000001AA", t("quick_start_ex_cups", lang=lang)
    )
    examples_table.add_row("da compare -y 2024 -y 2025", t("quick_start_ex_compare", lang=lang))
    examples_table.add_row("da cleanup -f", t("quick_start_ex_cleanup", lang=lang))
    examples_table.add_row("da version", t("quick_start_ex_version", lang=lang))

    console.print(examples_table)
    console.print()


def render_init_success(
    lang_code: str,
    config_path: Path,
    input_dir: Path | None = None,
    output_dir: Path | None = None,
    lang: str | None = None,
    version: str | None = None,
) -> None:
    """Render confirmation message after running da init."""
    target_lang = lang or lang_code
    lang_name = "Español" if target_lang == "es" else "English"
    app_version = version or get_version()
    message_lines = [
        f"✔ {t('init_version_info', lang=target_lang, version=app_version)}",
        f"✔ {t('init_language_set', lang=target_lang).replace('English', lang_name).replace('Español', lang_name)}",
    ]
    if input_dir is not None and output_dir is not None:
        message_lines.append(
            f"✔ {t('init_folders_created', lang=target_lang, input_dir=str(input_dir), output_dir=str(output_dir))}"
        )
    message_lines.append(
        f"[dim]{t('init_persistence_note', lang=target_lang, path=str(config_path))}[/dim]"
    )

    message = "\n".join(message_lines)
    console.print()
    console.print(
        Panel(
            message,
            title=f"[bold green]{t('init_title', lang=target_lang)}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_not_initialized_error(lang: str | None = None) -> None:
    """Render error notification when a command is executed before 'da init'."""
    error_msg = t("init_required_error", lang=lang)
    tip_msg = t("init_required_tip", lang=lang)
    body = f"[bold red]Error:[/bold red] {error_msg}\n\n[cyan]{tip_msg}[/cyan]"

    console.print()
    console.print(
        Panel(
            body,
            title="[bold red]Initialization Required / Inicialización Requerida[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_version() -> None:
    """Render a rich, formatted version panel for 'da version'."""
    version = get_version()
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Build inner content table (two-column key/value layout)
    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="bold cyan", no_wrap=True)
    info_table.add_column(style="white")

    info_table.add_row("⚡ Version", f"[bold cyan]{version}[/bold cyan]")
    info_table.add_row("🐍 Python", f"[dim]{py_version}[/dim]")
    info_table.add_row("📜 License", "[dim]MIT[/dim]")
    info_table.add_row(
        "🌐 Source",
        "[dim]github.com/marcosDLCS/datadis-analyzer[/dim]",
    )

    title_text = Text()
    title_text.append("DATADIS Analyzer ", style="bold yellow")
    title_text.append("(da)", style="bold white")

    subtitle = Text("\nSpain residential community energy analytics CLI\n", style="dim italic")

    body = Text.assemble(title_text, subtitle)
    panel_content = Columns([body, info_table], equal=False, expand=True)

    console.print()
    console.print(
        Panel(
            panel_content,
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 3),
        )
    )
    console.print()


def render_validation_issues(
    validation_results: list[ValidationResult], lang: str | None = None
) -> None:
    """Render a warning table if any CSV files failed validation."""
    invalid_results = [r for r in validation_results if not r.is_valid]
    if not invalid_results:
        return

    table = Table(
        title=f"[bold yellow]{t('validation_warnings_title', lang=lang)}[/bold yellow]",
        box=box.SIMPLE_HEAVY,
        header_style="bold yellow",
    )
    table.add_column(t("col_file", lang=lang), style="white", no_wrap=True)
    table.add_column(t("col_status", lang=lang), style="red", no_wrap=True)
    table.add_column(t("col_issue", lang=lang), style="dim white")

    for res in invalid_results:
        table.add_row(
            res.file_path.name, "SKIPPED", res.error_message or "Unknown validation issue"
        )

    console.print(table)
    console.print()


def render_community_overview(
    summary: CommunitySummary, file_count: int, lang: str | None = None
) -> None:
    """Render a high-level metrics card summarizing community figures."""
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    grid.add_row(
        f"[dim]{t('total_community_consumption', lang=lang)}[/dim]\n[bold bright_cyan]{format_kwh(summary.total_community_kwh)}[/bold bright_cyan]",
        f"[dim]{t('active_cups_meters', lang=lang)}[/dim]\n[bold green]{t('meters_count', lang=lang, count=summary.unique_cups_count)}[/bold green]",
        f"[dim]{t('csv_files_processed', lang=lang)}[/dim]\n[bold yellow]{t('files_count', lang=lang, count=file_count)}[/bold yellow]",
    )
    grid.add_row(
        f"[dim]{t('date_range', lang=lang)}[/dim]\n[white]{summary.date_min} to {summary.date_max}[/white]",
        f"[dim]{t('peak_month', lang=lang)}[/dim]\n[bold magenta]{summary.peak_month_label}[/bold magenta] ({format_kwh(summary.peak_month_kwh)})",
        f"[dim]{t('total_hourly_readings', lang=lang)}[/dim]\n[dim white]{t('hours_count', lang=lang, count=summary.total_readings)}[/dim white]",
    )

    console.print(
        Panel(
            grid,
            title=f"[bold cyan]{t('overview_card_title', lang=lang)}[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_annual_tables(
    summary: CommunitySummary,
    filter_cups: str | None = None,
    filter_year: int | None = None,
    lang: str | None = None,
) -> None:
    """Render formatted annual consumption tables with percentage share visual bars."""
    years_to_display = (
        [filter_year]
        if filter_year is not None and filter_year in summary.annual_summaries
        else sorted(summary.annual_summaries.keys())
    )

    for year in years_to_display:
        annual_data = summary.annual_summaries[year]
        shares = annual_data.cups_shares

        if filter_cups:
            shares = [s for s in shares if s.cups == filter_cups]

        title = (
            f"[bold yellow]{t('annual_summary_title', lang=lang, year=year)}[/bold yellow] "
            f"[dim]({t('community_total_label', lang=lang, total=format_kwh(annual_data.community_total_kwh))})[/dim]"
        )

        table = Table(
            title=title,
            box=box.ROUNDED,
            header_style="bold cyan",
            show_footer=True,
        )

        table.add_column(
            t("col_rank", lang=lang), justify="right", style="dim", width=2, no_wrap=True
        )
        table.add_column(
            t("col_cups", lang=lang),
            style="bold white",
            footer=t("col_total", lang=lang),
            no_wrap=True,
        )
        table.add_column(
            t("col_consumption", lang=lang),
            justify="right",
            style="bold bright_cyan",
            footer=f"{format_kwh(annual_data.community_total_kwh)}",
            no_wrap=True,
        )
        table.add_column(
            t("col_share", lang=lang),
            justify="right",
            style="bold yellow",
            footer="100.00%",
            no_wrap=True,
        )
        table.add_column(t("col_distribution", lang=lang), justify="left", width=12, no_wrap=True)

        for idx, item in enumerate(shares, start=1):
            cups_label = item.cups
            if idx == 1 and item.share_pct > 30.0:
                cups_label = f"{item.cups} [bold magenta]★[/bold magenta]"
            elif item.consumption_kwh < 1.0:
                cups_label = f"{item.cups} [dim](0)[/dim]"

            table.add_row(
                str(idx),
                cups_label,
                format_kwh(item.consumption_kwh),
                format_pct(item.share_pct),
                make_share_bar(item.share_pct, width=12),
            )

        console.print(table)
        console.print(f"[dim]{t('annual_legend', lang=lang)}[/dim]\n")


def render_monthly_overview(
    summary: CommunitySummary,
    filter_cups: str | None = None,
    filter_year: int | None = None,
    lang: str | None = None,
) -> None:
    """Render a concise monthly timeline overview showing community consumption and top contributor."""
    filtered_months = summary.monthly_summaries
    if filter_year is not None:
        filtered_months = [m for m in filtered_months if m.year == filter_year]

    if not filtered_months:
        return

    table = Table(
        title=f"[bold yellow]{t('monthly_timeline_title', lang=lang)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column(t("col_period", lang=lang), style="bold white", width=7, no_wrap=True)
    table.add_column(
        t("col_community_total", lang=lang), justify="right", style="bold bright_cyan", no_wrap=True
    )
    table.add_column(t("col_top_cups", lang=lang), style="bold magenta", no_wrap=True)
    table.add_column(
        t("col_top_share", lang=lang), justify="right", style="bold yellow", no_wrap=True
    )
    table.add_column(t("col_distribution", lang=lang), justify="left", width=12, no_wrap=True)

    for month_data in filtered_months:
        top = month_data.top_consumer
        table.add_row(
            month_data.period_label,
            format_kwh(month_data.community_total_kwh),
            top.cups,
            format_pct(top.share_pct),
            make_share_bar(top.share_pct, width=12),
        )

    console.print(table)
    console.print()


def render_detailed_monthly_breakdown(
    summary: CommunitySummary,
    filter_cups: str | None = None,
    filter_year: int | None = None,
    lang: str | None = None,
) -> None:
    """Render full monthly CUPS breakdown tables, showing percentage shares for each period."""
    filtered_months = summary.monthly_summaries
    if filter_year is not None:
        filtered_months = [m for m in filtered_months if m.year == filter_year]

    if not filtered_months:
        return

    for month_data in filtered_months:
        shares = month_data.cups_shares
        if filter_cups:
            shares = [s for s in shares if s.cups == filter_cups]

        title = (
            f"[bold yellow]{t('period_title', lang=lang, period=month_data.period_label)}[/bold yellow] "
            f"[dim]({t('community_total_label', lang=lang, total=format_kwh(month_data.community_total_kwh))})[/dim]"
        )

        table = Table(
            title=title,
            box=box.ROUNDED,
            header_style="bold cyan",
            show_footer=True,
        )
        table.add_column(
            t("col_rank", lang=lang), justify="right", style="dim", width=2, no_wrap=True
        )
        table.add_column(
            t("col_cups", lang=lang),
            style="bold white",
            footer=t("col_total", lang=lang),
            no_wrap=True,
        )
        table.add_column(
            t("col_consumption", lang=lang),
            justify="right",
            style="bold bright_cyan",
            footer=f"{format_kwh(month_data.community_total_kwh)}",
            no_wrap=True,
        )
        table.add_column(
            t("col_share", lang=lang),
            justify="right",
            style="bold yellow",
            footer="100.00%",
            no_wrap=True,
        )
        table.add_column(t("col_distribution", lang=lang), justify="left", width=12, no_wrap=True)

        for idx, item in enumerate(shares, start=1):
            cups_label = item.cups
            if idx == 1 and item.share_pct > 30.0:
                cups_label = f"{item.cups} [bold magenta]★[/bold magenta]"
            elif item.consumption_kwh < 0.1:
                cups_label = f"{item.cups} [dim](0)[/dim]"

            table.add_row(
                str(idx),
                cups_label,
                format_kwh(item.consumption_kwh),
                format_pct(item.share_pct),
                make_share_bar(item.share_pct, width=12),
            )

        console.print(table)
        console.print()


def render_cups_trajectory(
    summary: CommunitySummary,
    target_cups: str,
    filter_year: int | None = None,
    lang: str | None = None,
) -> None:
    """Render a dedicated month-by-month trajectory table for a single selected CUPS."""
    filtered_months = summary.monthly_summaries
    if filter_year is not None:
        filtered_months = [m for m in filtered_months if m.year == filter_year]

    table = Table(
        title=f"[bold yellow]{t('cups_trajectory_title', lang=lang, cups=target_cups)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_footer=True,
    )
    table.add_column(
        t("col_period", lang=lang),
        style="bold white",
        width=7,
        no_wrap=True,
        footer=t("col_total", lang=lang),
    )
    table.add_column(
        t("col_cups_kwh", lang=lang), justify="right", style="bold bright_cyan", no_wrap=True
    )
    table.add_column(
        t("col_community_kwh", lang=lang), justify="right", style="dim white", no_wrap=True
    )
    table.add_column(t("col_share", lang=lang), justify="right", style="bold yellow", no_wrap=True)
    table.add_column(t("col_distribution", lang=lang), justify="left", width=12, no_wrap=True)

    total_cups_kwh = 0.0
    total_community_kwh = 0.0

    for month_data in filtered_months:
        match = next((s for s in month_data.cups_shares if s.cups == target_cups), None)
        if match:
            total_cups_kwh += match.consumption_kwh
            total_community_kwh += month_data.community_total_kwh
            table.add_row(
                month_data.period_label,
                format_kwh(match.consumption_kwh),
                format_kwh(month_data.community_total_kwh),
                format_pct(match.share_pct),
                make_share_bar(match.share_pct, width=12),
            )

    overall_share = (
        (total_cups_kwh / total_community_kwh * 100.0) if total_community_kwh > 0 else 0.0
    )
    table.columns[1].footer = f"{format_kwh(total_cups_kwh)}"
    table.columns[2].footer = f"{format_kwh(total_community_kwh)}"
    table.columns[3].footer = f"{format_pct(overall_share)}"

    console.print(table)
    console.print()


def render_key_insights(summary: CommunitySummary, lang: str | None = None) -> None:
    """Render an analytical insights panel highlighting main findings."""
    top_overall = summary.overall_cups_shares[0] if summary.overall_cups_shares else None
    zero_consumers = [s.cups for s in summary.overall_cups_shares if s.consumption_kwh < 1.0]

    insights: list[str] = []

    if top_overall and top_overall.share_pct > 50.0:
        insights.append(
            t(
                "dominant_consumer_insight",
                lang=lang,
                cups=top_overall.cups,
                pct=top_overall.share_pct,
                kwh=format_kwh(top_overall.consumption_kwh),
            )
        )

    if zero_consumers:
        insights.append(
            t(
                "zero_consumer_insight",
                lang=lang,
                count=len(zero_consumers),
                cups=", ".join(zero_consumers),
            )
        )

    insights.append(
        t(
            "seasonality_insight",
            lang=lang,
            peak_month=summary.peak_month_label,
            peak_kwh=format_kwh(summary.peak_month_kwh),
            lowest_month=summary.lowest_month_label,
            lowest_kwh=format_kwh(summary.lowest_month_kwh),
        )
    )

    console.print(
        Panel(
            "\n\n".join(insights),
            title=f"[bold yellow]{t('insights_title', lang=lang)}[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_export_success(report_path: Path, lang: str | None = None) -> None:
    """Render a notification card when markdown report is saved to .output/."""
    msg = f"✔ {t('report_generated', lang=lang, path=str(report_path))}"
    console.print(
        Panel(
            msg,
            border_style="green",
            box=box.ROUNDED,
        )
    )
    console.print()


def render_cleanup_result(
    removed_files: list[Path],
    output_dir: Path,
    lang: str | None = None,
) -> None:
    """Render notification panel after executing da cleanup."""
    if not removed_files:
        console.print()
        console.print(
            Panel(
                f"[bold yellow](i)[/bold yellow] {t('cleanup_empty', lang=lang, dir=str(output_dir))}",
                title=f"[bold yellow]{t('cleanup_title', lang=lang)}[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )
        console.print()
        return

    file_list = "\n".join(f"  • [dim]{f.name}[/dim]" for f in removed_files[:10])
    if len(removed_files) > 10:
        file_list += f"\n  [dim]... and {len(removed_files) - 10} more[/dim]"

    msg = f"✔ {t('cleanup_success', lang=lang, count=len(removed_files), dir=str(output_dir))}\n\n{file_list}"
    console.print()
    console.print(
        Panel(
            msg,
            title=f"[bold green]{t('cleanup_title', lang=lang)}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_comparison_overview(comparison: ComparisonSummary, lang: str | None = None) -> None:
    """Render executive overview panel comparing multiple calendar years."""
    years_str = " ➔ ".join(map(str, comparison.years))

    lines: list[str] = []
    lines.append(
        f"[bold white]{t('compare_years_label', lang=lang)}[/bold white] [bold cyan]{years_str}[/bold cyan]"
    )

    # Comparable period note
    if comparison.comparable_months:
        first_m = get_month_name(min(comparison.comparable_months), lang=lang, short=True)
        last_m = get_month_name(max(comparison.comparable_months), lang=lang, short=True)
        period_str = f"{first_m} - {last_m}"
        lines.append(
            f"  [dim cyan]{t('comparable_period_note', lang=lang, period=period_str, months=len(comparison.comparable_months))}[/dim cyan]"
        )

    # Annual totals
    for y in comparison.years:
        raw_kwh = comparison.annual_totals[y]
        comp_kwh = comparison.comparable_annual_totals.get(y, raw_kwh)
        if comparison.excluded_months and comp_kwh != raw_kwh:
            lines.append(
                f"  • [bold]{y}:[/bold] [yellow]{format_kwh(comp_kwh)}[/yellow] [dim]({format_kwh(raw_kwh)} total)[/dim]"
            )
        else:
            lines.append(f"  • [bold]{y}:[/bold] [yellow]{format_kwh(raw_kwh)}[/yellow]")

    lines.append("")
    # Overall change across comparable months
    diff = comparison.total_diff_kwh
    pct = comparison.total_pct_change
    if diff is not None and pct is not None:
        if diff < 0:
            status_text = t(
                "compare_status_saving",
                lang=lang,
                diff_kwh=format_kwh(abs(diff)),
                pct=f"{abs(pct):.2f}",
            )
        elif diff > 0:
            status_text = t(
                "compare_status_increase",
                lang=lang,
                diff_kwh=format_kwh(diff),
                pct=f"{pct:.2f}",
            )
        else:
            status_text = t("compare_status_stable", lang=lang, diff_kwh=format_kwh(diff))
        lines.append(f"[bold]{t('compare_overall_change', lang=lang)}[/bold] {status_text}")
    elif comparison.excluded_months and not comparison.comparable_months:
        lines.append(f"[yellow]{t('no_comparable_months', lang=lang)}[/yellow]")

    # Highlights
    highlights: list[str] = []
    if comparison.max_decrease_month and comparison.max_decrease_month.diff_kwh is not None:
        m_name = get_month_name(comparison.max_decrease_month.month, lang=lang)
        pct_val = abs(comparison.max_decrease_month.pct_change or 0.0)
        highlights.append(
            f"[green]▼[/green] {t('compare_max_decrease', lang=lang)} [bold]{m_name}[/bold] "
            f"([green]-{pct_val:.1f}%[/green] / [green]-{format_kwh(abs(comparison.max_decrease_month.diff_kwh))}[/green])"
        )

    if comparison.max_increase_month and comparison.max_increase_month.diff_kwh is not None:
        m_name = get_month_name(comparison.max_increase_month.month, lang=lang)
        pct_val = comparison.max_increase_month.pct_change or 0.0
        highlights.append(
            f"[red]▲[/red] {t('compare_max_increase', lang=lang)} [bold]{m_name}[/bold] "
            f"([red]+{pct_val:.1f}%[/red] / [red]+{format_kwh(comparison.max_increase_month.diff_kwh)}[/red])"
        )

    if comparison.top_saving_cups:
        highlights.append(
            f"[green]🏆[/green] {t('compare_top_saver', lang=lang)} [cyan]{comparison.top_saving_cups.cups}[/cyan] "
            f"([green]-{format_kwh(abs(comparison.top_saving_cups.diff_kwh))}[/green])"
        )

    if comparison.top_increasing_cups:
        highlights.append(
            f"[yellow]⚡[/yellow] {t('compare_top_increaser', lang=lang)} [cyan]{comparison.top_increasing_cups.cups}[/cyan] "
            f"([red]+{format_kwh(comparison.top_increasing_cups.diff_kwh)}[/red])"
        )

    if highlights:
        lines.append("")
        lines.extend(f"  {h}" for h in highlights)

    if comparison.excluded_months:
        lines.append("")
        ex_names = ", ".join(
            get_month_name(m, lang=lang, short=True) for m in comparison.excluded_months
        )
        lines.append(
            f"  [dim yellow]* {t('excluded_months_note', lang=lang, count=len(comparison.excluded_months), months=ex_names)}[/dim yellow]"
        )

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title=f"[bold cyan]{t('compare_overview_title', lang=lang)}[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_monthly_comparison_table(comparison: ComparisonSummary, lang: str | None = None) -> None:
    """Render month-by-month comparative consumption and variation table."""
    table = Table(
        title=f"[bold yellow]{t('compare_monthly_title', lang=lang)}[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column(t("compare_month_col", lang=lang), style="bold white", no_wrap=True, width=6)
    for y in comparison.years:
        table.add_column(f"{y}", justify="right", style="cyan", no_wrap=True, width=13)
    table.add_column(t("compare_diff_col", lang=lang), justify="right", no_wrap=True, width=13)
    table.add_column(t("compare_var_col", lang=lang), justify="right", no_wrap=True, width=11)
    table.add_column(t("compare_trend_col", lang=lang), justify="center", no_wrap=True, width=11)

    for m in comparison.monthly_comparisons:
        m_label = get_month_name(m.month, lang=lang, short=True)

        year_cells: list[str] = []
        for y in comparison.years:
            status = m.year_status.get(y, "complete")
            val = m.yearly_kwh.get(y)
            if status == "no_data" or val is None:
                year_cells.append(f"[dim]{t('no_data', lang=lang)}[/dim]")
            elif status == "incomplete":
                year_cells.append(f"[yellow]{format_kwh(val)}*[/yellow]")
            else:
                year_cells.append(format_kwh(val))

        # Diff cell
        if m.diff_kwh is not None:
            if m.diff_kwh < 0:
                diff_cell = f"[green]-{format_kwh(abs(m.diff_kwh))}[/green]"
            elif m.diff_kwh > 0:
                diff_cell = f"[red]+{format_kwh(m.diff_kwh)}[/red]"
            else:
                diff_cell = "[dim]0.00 kWh[/dim]"
        else:
            diff_cell = "[dim]—[/dim]"

        # Variation & Trend
        if m.pct_change is not None:
            if m.pct_change < 0:
                var_cell = f"[bold green]▼ {m.pct_change:.1f}%[/bold green]"
                trend_cell = f"[green]{t('compare_trend_reduced', lang=lang)}[/green]"
            elif m.pct_change > 0:
                var_cell = f"[bold red]▲ +{m.pct_change:.1f}%[/bold red]"
                trend_cell = f"[red]{t('compare_trend_increased', lang=lang)}[/red]"
            else:
                var_cell = "[dim]— 0.0%[/dim]"
                trend_cell = f"[dim]{t('compare_trend_equal', lang=lang)}[/dim]"
        else:
            var_cell = "[dim]—[/dim]"
            trend_cell = (
                f"[dim]{t('no_data', lang=lang)}[/dim]" if not m.is_complete else "[dim]—[/dim]"
            )

        table.add_row(m_label, *year_cells, diff_cell, var_cell, trend_cell)

    # Total Row (Comparable period)
    table.add_section()
    if comparison.comparable_months:
        first_m = get_month_name(min(comparison.comparable_months), lang=lang, short=True)
        last_m = get_month_name(max(comparison.comparable_months), lang=lang, short=True)
        total_label = (
            f"Total ({first_m}-{last_m})" if len(comparison.comparable_months) < 12 else "Total"
        )
        total_year_cells = [
            format_kwh(comparison.comparable_annual_totals[y]) for y in comparison.years
        ]
        diff_tot = comparison.total_diff_kwh
        pct_tot = comparison.total_pct_change

        if diff_tot is not None:
            if diff_tot < 0:
                total_diff_cell = f"[bold green]-{format_kwh(abs(diff_tot))}[/bold green]"
            elif diff_tot > 0:
                total_diff_cell = f"[bold red]+{format_kwh(diff_tot)}[/bold red]"
            else:
                total_diff_cell = "[bold]0.00 kWh[/bold]"
        else:
            total_diff_cell = "[dim]—[/dim]"

        if pct_tot is not None:
            if pct_tot < 0:
                total_var_cell = f"[bold green]▼ {pct_tot:.1f}%[/bold green]"
                total_trend_cell = (
                    f"[bold green]{t('compare_trend_reduced', lang=lang)}[/bold green]"
                )
            elif pct_tot > 0:
                total_var_cell = f"[bold red]▲ +{pct_tot:.1f}%[/bold red]"
                total_trend_cell = f"[bold red]{t('compare_trend_increased', lang=lang)}[/bold red]"
            else:
                total_var_cell = "[bold dim]— 0.0%[/bold dim]"
                total_trend_cell = f"[bold dim]{t('compare_trend_equal', lang=lang)}[/bold dim]"
        else:
            total_var_cell = "[dim]—[/dim]"
            total_trend_cell = "[dim]—[/dim]"

        table.add_row(
            f"[bold]{total_label}[/bold]",
            *total_year_cells,
            total_diff_cell,
            total_var_cell,
            total_trend_cell,
        )
    else:
        raw_year_cells = [format_kwh(comparison.annual_totals[y]) for y in comparison.years]
        table.add_row(
            "[bold]Total[/bold]", *raw_year_cells, "[dim]—[/dim]", "[dim]—[/dim]", "[dim]—[/dim]"
        )

    console.print(table)
    console.print()


def render_cups_comparison_table(comparison: ComparisonSummary, lang: str | None = None) -> None:
    """Render comparison table showing individual CUPS shifts between earliest and latest years."""
    if not comparison.cups_comparisons:
        return

    earliest_y = comparison.years[0]
    latest_y = comparison.years[-1]

    sub_note = ""
    if comparison.comparable_months and len(comparison.comparable_months) < 12:
        first_m = get_month_name(min(comparison.comparable_months), lang=lang, short=True)
        last_m = get_month_name(max(comparison.comparable_months), lang=lang, short=True)
        sub_note = f" [{first_m}-{last_m}]"

    table = Table(
        title=f"[bold yellow]{t('compare_cups_title', lang=lang)} ({earliest_y} ➔ {latest_y}{sub_note})[/bold yellow]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("Rank", justify="right", style="dim", width=4)
    table.add_column(t("compare_cups_col", lang=lang), style="bold white", no_wrap=True, width=22)
    table.add_column(f"{earliest_y}", justify="right", style="cyan", no_wrap=True, width=12)
    table.add_column(f"{latest_y}", justify="right", style="cyan", no_wrap=True, width=12)
    table.add_column(t("compare_diff_col", lang=lang), justify="right", no_wrap=True, width=12)
    table.add_column(t("compare_var_col", lang=lang), justify="right", no_wrap=True, width=11)

    for idx, c in enumerate(comparison.cups_comparisons, start=1):
        c_kwh_base = c.yearly_kwh.get(earliest_y, 0.0)
        c_kwh_target = c.yearly_kwh.get(latest_y, 0.0)

        if c.diff_kwh < 0:
            diff_cell = f"[green]-{format_kwh(abs(c.diff_kwh))}[/green]"
        elif c.diff_kwh > 0:
            diff_cell = f"[red]+{format_kwh(c.diff_kwh)}[/red]"
        else:
            diff_cell = "[dim]0.00 kWh[/dim]"

        if c.pct_change is not None:
            if c.pct_change < 0:
                var_cell = f"[bold green]▼ {c.pct_change:.1f}%[/bold green]"
            elif c.pct_change > 0:
                var_cell = f"[bold red]▲ +{c.pct_change:.1f}%[/bold red]"
            else:
                var_cell = "[dim]— 0.0%[/dim]"
        else:
            var_cell = "[dim]N/A[/dim]"

        table.add_row(
            str(idx),
            c.cups,
            format_kwh(c_kwh_base),
            format_kwh(c_kwh_target),
            diff_cell,
            var_cell,
        )

    console.print(table)
    console.print()
