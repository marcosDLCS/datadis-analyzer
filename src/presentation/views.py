"""Terminal views, tables, cards, and help screens rendered with Rich."""

from pathlib import Path
from typing import Optional

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.i18n import t
from src.ingestion.schema import ValidationResult
from src.presentation.console import console, format_kwh, format_pct, make_share_bar
from src.processing.models import CommunitySummary, CupsShare


def render_help(lang: Optional[str] = None) -> None:
    """Render a comprehensive, formatted help screen for the DATADIS CLI tool."""
    title_text = Text()
    title_text.append(f"{t('app_title', lang=lang)} ", style="bold yellow")
    title_text.append("(da)", style="bold cyan")
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
    console.print(f"[bold cyan]{t('overview_heading', lang=lang)}[/bold cyan]\n{t('overview_text', lang=lang)}\n")

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
        "da init",
        t("cmd_init_desc", lang=lang),
    )
    cmd_table.add_row(
        "da help",
        t("cmd_help_desc", lang=lang),
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
    console.print(Panel(t("data_layout_desc", lang=lang), title=t("data_layout_title", lang=lang), border_style="blue", box=box.ROUNDED))
    console.print()
    console.print(Panel(t("quick_start_text", lang=lang), title=t("quick_start_title", lang=lang), border_style="green", box=box.ROUNDED))
    console.print()


def render_init_success(lang_code: str, config_path: Path, lang: Optional[str] = None) -> None:
    """Render confirmation message after running da init."""
    lang_name = "Español" if lang_code == "es" else "English"
    message = (
        f"✔ {t('init_language_set', lang=lang_code).replace('English', lang_name).replace('Español', lang_name)}\n"
        f"[dim]{t('init_persistence_note', lang=lang_code, path=str(config_path))}[/dim]"
    )
    console.print()
    console.print(
        Panel(
            message,
            title=f"[bold green]{t('init_title', lang=lang_code)}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_validation_issues(validation_results: list[ValidationResult], lang: Optional[str] = None) -> None:
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
        table.add_row(res.file_path.name, "SKIPPED", res.error_message or "Unknown validation issue")

    console.print(table)
    console.print()


def render_community_overview(summary: CommunitySummary, file_count: int, lang: Optional[str] = None) -> None:
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
    filter_cups: Optional[str] = None,
    filter_year: Optional[int] = None,
    lang: Optional[str] = None,
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

        table.add_column(t("col_rank", lang=lang), justify="right", style="dim", width=2, no_wrap=True)
        table.add_column(t("col_cups", lang=lang), style="bold white", footer=t("col_total", lang=lang), no_wrap=True)
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
    filter_cups: Optional[str] = None,
    filter_year: Optional[int] = None,
    lang: Optional[str] = None,
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
    table.add_column(t("col_community_total", lang=lang), justify="right", style="bold bright_cyan", no_wrap=True)
    table.add_column(t("col_top_cups", lang=lang), style="bold magenta", no_wrap=True)
    table.add_column(t("col_top_share", lang=lang), justify="right", style="bold yellow", no_wrap=True)
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
    filter_cups: Optional[str] = None,
    filter_year: Optional[int] = None,
    lang: Optional[str] = None,
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
        table.add_column(t("col_rank", lang=lang), justify="right", style="dim", width=2, no_wrap=True)
        table.add_column(t("col_cups", lang=lang), style="bold white", footer=t("col_total", lang=lang), no_wrap=True)
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
    filter_year: Optional[int] = None,
    lang: Optional[str] = None,
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
    table.add_column(t("col_period", lang=lang), style="bold white", width=7, no_wrap=True, footer=t("col_total", lang=lang))
    table.add_column(t("col_cups_kwh", lang=lang), justify="right", style="bold bright_cyan", no_wrap=True)
    table.add_column(t("col_community_kwh", lang=lang), justify="right", style="dim white", no_wrap=True)
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

    overall_share = (total_cups_kwh / total_community_kwh * 100.0) if total_community_kwh > 0 else 0.0
    table.columns[1].footer = f"{format_kwh(total_cups_kwh)}"
    table.columns[2].footer = f"{format_kwh(total_community_kwh)}"
    table.columns[3].footer = f"{format_pct(overall_share)}"

    console.print(table)
    console.print()


def render_key_insights(summary: CommunitySummary, lang: Optional[str] = None) -> None:
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


def render_export_success(report_path: Path, lang: Optional[str] = None) -> None:
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
