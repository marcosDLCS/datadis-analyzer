"""Markdown report generator exporting community energy summaries to .output/."""

import shutil
from datetime import datetime
from pathlib import Path

from src.config import DEFAULT_OUTPUT_DIR
from src.i18n import get_month_name, t
from src.presentation.console import format_kwh, format_pct
from src.processing.models import CommunitySummary, ComparisonSummary


def _make_ascii_bar(pct: float, width: int = 12) -> str:
    """Create a plain text block bar suitable for standard Markdown rendering."""
    pct_clamped = max(0.0, min(100.0, pct))
    filled_len = round((pct_clamped / 100.0) * width)
    empty_len = width - filled_len
    return "`" + "█" * filled_len + "░" * empty_len + "`"


def export_markdown_summary(
    summary: CommunitySummary,
    output_dir: Path | None = None,
    lang: str | None = None,
    year_filter: int | None = None,
    cups_filter: str | None = None,
    view_mode: str = "all",
) -> Path:
    """Generate and persist a complete community summary report in Markdown format.

    The output filename begins with a datetime down to seconds (e.g. 'YYYYMMDD_HHMMSS_summary.md').

    Args:
        summary: Aggregated CommunitySummary dataset.
        output_dir: Directory where the report will be saved (default: loaded config or .output).
        lang: Target language ('en' or 'es').
        year_filter: Optional year filter applied.
        cups_filter: Optional CUPS filter applied.
        view_mode: Selected view mode ('all', 'annual', 'monthly').

    Returns:
        Path to the saved markdown file.
    """
    from src.config import load_config

    target_output_dir = output_dir or Path(load_config().output_dir or DEFAULT_OUTPUT_DIR)
    target_output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    timestamp_prefix = now.strftime("%Y%m%d_%H%M%S")

    # Construct concise filename
    if year_filter:
        filename = f"{timestamp_prefix}_summary_{year_filter}.md"
    elif cups_filter:
        filename = f"{timestamp_prefix}_summary_{cups_filter}.md"
    else:
        filename = f"{timestamp_prefix}_community_summary.md"

    report_path = target_output_dir / filename

    lines: list[str] = []

    # Title & Metadata
    lines.append(t("md_doc_title", lang=lang))
    lines.append("")
    lines.append(f"> {t('md_generated_at', lang=lang, datetime=now.strftime('%Y-%m-%d %H:%M:%S'))}")
    lines.append("")

    # Section 1: Executive Overview
    lines.append(t("md_section_overview", lang=lang))
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| :--- | :--- |")
    lines.append(
        f"| {t('total_community_consumption', lang=lang).rstrip(':')} | **{format_kwh(summary.total_community_kwh)}** |"
    )
    lines.append(
        f"| {t('active_cups_meters', lang=lang).rstrip(':')} | {summary.unique_cups_count} |"
    )
    lines.append(
        f"| {t('date_range', lang=lang).rstrip(':')} | {summary.date_min} to {summary.date_max} |"
    )
    lines.append(
        f"| {t('peak_month', lang=lang).rstrip(':')} | {summary.peak_month_label} ({format_kwh(summary.peak_month_kwh)}) |"
    )
    lines.append(
        f"| {t('total_hourly_readings', lang=lang).rstrip(':')} | {summary.total_readings:,} |"
    )
    lines.append("")

    # Section 2: Annual Breakdown
    if view_mode in ("all", "annual") and not cups_filter:
        lines.append(t("md_section_annual", lang=lang))
        lines.append("")

        years_to_display = (
            [year_filter]
            if year_filter is not None and year_filter in summary.annual_summaries
            else sorted(summary.annual_summaries.keys())
        )

        for year in years_to_display:
            annual = summary.annual_summaries[year]
            lines.append(f"### {t('annual_summary_title', lang=lang, year=year)}")
            lines.append(
                f"*{t('community_total_label', lang=lang, total=format_kwh(annual.community_total_kwh))}*"
            )
            lines.append("")
            lines.append(
                f"| {t('col_rank', lang=lang)} | {t('col_cups', lang=lang)} | {t('col_consumption', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |"
            )
            lines.append("| :---: | :--- | :---: | :---: | :--- |")

            for idx, item in enumerate(annual.cups_shares, start=1):
                badge = " ★" if (idx == 1 and item.share_pct > 30.0) else ""
                lines.append(
                    f"| {idx} | `{item.cups}`{badge} | {format_kwh(item.consumption_kwh)} | {format_pct(item.share_pct)} | {_make_ascii_bar(item.share_pct)} |"
                )

            lines.append(
                f"| | **{t('col_total', lang=lang)}** | **{format_kwh(annual.community_total_kwh)}** | **100.00%** | |"
            )
            lines.append("")

    # Section 3: Monthly Community Timeline
    if view_mode in ("all", "monthly") and not cups_filter:
        lines.append(t("md_section_timeline", lang=lang))
        lines.append("")
        lines.append(
            f"| {t('col_period', lang=lang)} | {t('col_community_total', lang=lang)} | {t('col_top_cups', lang=lang)} | {t('col_top_share', lang=lang)} | {t('col_distribution', lang=lang)} |"
        )
        lines.append("| :---: | :---: | :--- | :---: | :--- |")

        filtered_months = summary.monthly_summaries
        if year_filter is not None:
            filtered_months = [m for m in filtered_months if m.year == year_filter]

        for m in filtered_months:
            top = m.top_consumer
            lines.append(
                f"| {m.period_label} | {format_kwh(m.community_total_kwh)} | `{top.cups}` | {format_pct(top.share_pct)} | {_make_ascii_bar(top.share_pct)} |"
            )
        lines.append("")

    # Section 4: Detailed Monthly Breakdown
    if view_mode in ("all", "monthly") and not cups_filter:
        lines.append(t("md_section_monthly", lang=lang))
        lines.append("")

        filtered_months = summary.monthly_summaries
        if year_filter is not None:
            filtered_months = [m for m in filtered_months if m.year == year_filter]

        for m in filtered_months:
            lines.append(f"### {t('period_title', lang=lang, period=m.period_label)}")
            lines.append(
                f"*{t('community_total_label', lang=lang, total=format_kwh(m.community_total_kwh))}*"
            )
            lines.append("")
            lines.append(
                f"| {t('col_rank', lang=lang)} | {t('col_cups', lang=lang)} | {t('col_consumption', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |"
            )
            lines.append("| :---: | :--- | :---: | :---: | :--- |")

            for idx, item in enumerate(m.cups_shares, start=1):
                badge = " ★" if (idx == 1 and item.share_pct > 30.0) else ""
                lines.append(
                    f"| {idx} | `{item.cups}`{badge} | {format_kwh(item.consumption_kwh)} | {format_pct(item.share_pct)} | {_make_ascii_bar(item.share_pct)} |"
                )

            lines.append(
                f"| | **{t('col_total', lang=lang)}** | **{format_kwh(m.community_total_kwh)}** | **100.00%** | |"
            )
            lines.append("")

    # Section for single CUPS trajectory if filtered
    if cups_filter:
        lines.append(f"## {t('cups_trajectory_title', lang=lang, cups=cups_filter)}")
        lines.append("")
        lines.append(
            f"| {t('col_period', lang=lang)} | {t('col_cups_kwh', lang=lang)} | {t('col_community_kwh', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |"
        )
        lines.append("| :---: | :---: | :---: | :---: | :--- |")

        total_c = 0.0
        total_comm = 0.0
        filtered_months = summary.monthly_summaries
        if year_filter is not None:
            filtered_months = [m for m in filtered_months if m.year == year_filter]

        for m in filtered_months:
            match = next((s for s in m.cups_shares if s.cups == cups_filter), None)
            if match:
                total_c += match.consumption_kwh
                total_comm += m.community_total_kwh
                lines.append(
                    f"| {m.period_label} | {format_kwh(match.consumption_kwh)} | {format_kwh(m.community_total_kwh)} | {format_pct(match.share_pct)} | {_make_ascii_bar(match.share_pct)} |"
                )

        ov_share = (total_c / total_comm * 100.0) if total_comm > 0 else 0.0
        lines.append(
            f"| **{t('col_total', lang=lang)}** | **{format_kwh(total_c)}** | **{format_kwh(total_comm)}** | **{format_pct(ov_share)}** | |"
        )
        lines.append("")

    # Section 5: Key Observations
    lines.append(t("md_section_insights", lang=lang))
    lines.append("")
    top_overall = summary.overall_cups_shares[0] if summary.overall_cups_shares else None
    zero_consumers = [s.cups for s in summary.overall_cups_shares if s.consumption_kwh < 1.0]

    if top_overall and top_overall.share_pct > 50.0:
        lines.append(
            f"- **{t('dominant_consumer_insight', lang=lang, cups=top_overall.cups, pct=top_overall.share_pct, kwh=format_kwh(top_overall.consumption_kwh)).replace('[bold magenta]', '').replace('[/]', '').replace('[bold yellow]', '').replace('[/bold yellow]', '').replace('[bold]', '').replace('[/bold]', '').lstrip('• ')}**"
        )
    if zero_consumers:
        lines.append(
            f"- {t('zero_consumer_insight', lang=lang, count=len(zero_consumers), cups=', '.join(zero_consumers)).replace('[dim white]', '').replace('[/]', '').replace('[dim]', '').replace('[/dim]', '').lstrip('• ')}"
        )
    lines.append(
        f"- {t('seasonality_insight', lang=lang, peak_month=summary.peak_month_label, peak_kwh=format_kwh(summary.peak_month_kwh), lowest_month=summary.lowest_month_label, lowest_kwh=format_kwh(summary.lowest_month_kwh)).replace('[cyan]', '').replace('[/]', '').replace('[bold yellow]', '').replace('[/bold yellow]', '').replace('[bold cyan]', '').replace('[/bold cyan]', '').lstrip('• ')}"
    )
    lines.append("")

    # Write report
    report_content = "\n".join(lines) + "\n"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path


def cleanup_output_directory(output_dir: Path | None = None) -> list[Path]:
    """Remove all files and subdirectories from the specified output directory.

    Args:
        output_dir: Directory to clear (default: loaded config or ./.output).

    Returns:
        Sorted list of Path objects for all deleted items.
    """
    from src.config import load_config

    target_output_dir = output_dir or Path(load_config().output_dir or DEFAULT_OUTPUT_DIR)
    if not target_output_dir.exists() or not target_output_dir.is_dir():
        return []

    removed: list[Path] = []
    for item in sorted(target_output_dir.iterdir()):
        if item.is_file():
            item.unlink()
            removed.append(item)
        elif item.is_dir():
            shutil.rmtree(item)
            removed.append(item)

    return removed


def export_comparison_markdown(
    comparison: ComparisonSummary,
    output_dir: Path | None = None,
    lang: str | None = None,
) -> Path:
    """Generate and persist a complete multi-year comparison report in Markdown format.

    Args:
        comparison: Aggregated ComparisonSummary dataset.
        output_dir: Directory where report will be stored.
        lang: Target language ('en' or 'es').

    Returns:
        Path to the generated markdown file.
    """
    from src.config import load_config

    target_output_dir = output_dir or Path(load_config().output_dir or DEFAULT_OUTPUT_DIR)
    target_output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    timestamp_prefix = now.strftime("%Y%m%d_%H%M%S")
    years_str = "_".join(map(str, comparison.years))
    filename = f"{timestamp_prefix}_comparison_{years_str}.md"
    report_path = target_output_dir / filename

    lines: list[str] = []

    # Title & Metadata
    years_title = " vs ".join(map(str, comparison.years))
    lines.append(t("md_compare_title", lang=lang, years=years_title))
    lines.append("")
    lines.append(f"> {t('md_generated_at', lang=lang, datetime=now.strftime('%Y-%m-%d %H:%M:%S'))}")
    lines.append("")

    # Section 1: Executive Overview
    lines.append(t("md_compare_overview", lang=lang))
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| :--- | :--- |")
    lines.append(
        f"| {t('compare_years_label', lang=lang).rstrip(':')} | **{', '.join(map(str, comparison.years))}** |"
    )
    for y in comparison.years:
        lines.append(
            f"| {y} Total Community Consumption | **{format_kwh(comparison.annual_totals[y])}** |"
        )

    diff = comparison.total_diff_kwh
    pct = comparison.total_pct_change
    diff_sign = (
        f"+{format_kwh(diff)}"
        if diff > 0
        else f"-{format_kwh(abs(diff))}"
        if diff < 0
        else "0.00 kWh"
    )
    pct_sign = (
        f"+{pct:.2f}%"
        if (pct is not None and pct > 0)
        else f"{pct:.2f}%"
        if pct is not None
        else "N/A"
    )
    lines.append(
        f"| {t('compare_overall_change', lang=lang).rstrip(':')} | **{diff_sign} ({pct_sign})** |"
    )
    lines.append("")

    # Section 2: Monthly Comparison Table
    lines.append(t("md_compare_monthly", lang=lang))
    lines.append("")
    year_headers = " | ".join(f"{y} (kWh)" for y in comparison.years)
    lines.append(
        f"| {t('compare_month_col', lang=lang)} | {year_headers} | {t('compare_diff_col', lang=lang)} | {t('compare_var_col', lang=lang)} | {t('compare_trend_col', lang=lang)} |"
    )
    col_dashes = " | ".join(
        ":---:" if idx == 0 else "---:" for idx in range(len(comparison.years) + 4)
    )
    lines.append(f"| {col_dashes} |")

    for m in comparison.monthly_comparisons:
        m_name = get_month_name(m.month, lang=lang, short=True)
        year_vals = " | ".join(f"{m.yearly_kwh.get(y, 0.0):,.2f}" for y in comparison.years)
        m_diff = (
            f"+{m.diff_kwh:,.2f}"
            if m.diff_kwh > 0
            else f"-{abs(m.diff_kwh):,.2f}"
            if m.diff_kwh < 0
            else "0.00"
        )
        m_pct = (
            f"+{m.pct_change:.1f}%"
            if (m.pct_change is not None and m.pct_change > 0)
            else f"{m.pct_change:.1f}%"
            if m.pct_change is not None
            else "N/A"
        )
        m_trend = (
            t("compare_trend_reduced", lang=lang)
            if (m.pct_change is not None and m.pct_change < 0)
            else t("compare_trend_increased", lang=lang)
            if (m.pct_change is not None and m.pct_change > 0)
            else t("compare_trend_equal", lang=lang)
        )
        lines.append(f"| {m_name} | {year_vals} | {m_diff} | {m_pct} | {m_trend} |")

    # Total row
    total_vals = " | ".join(f"**{comparison.annual_totals[y]:,.2f}**" for y in comparison.years)
    lines.append(f"| **Total** | {total_vals} | **{diff_sign}** | **{pct_sign}** | |")
    lines.append("")

    # Section 3: CUPS shifts (if available)
    if comparison.cups_comparisons:
        lines.append(t("md_compare_cups", lang=lang))
        lines.append("")
        earliest_y = comparison.years[0]
        latest_y = comparison.years[-1]
        lines.append(
            f"| Rank | {t('compare_cups_col', lang=lang)} | {earliest_y} (kWh) | {latest_y} (kWh) | {t('compare_diff_col', lang=lang)} | {t('compare_var_col', lang=lang)} |"
        )
        lines.append("| ---: | :--- | ---: | ---: | ---: | ---: |")
        for idx, c in enumerate(comparison.cups_comparisons, start=1):
            c_base = c.yearly_kwh.get(earliest_y, 0.0)
            c_target = c.yearly_kwh.get(latest_y, 0.0)
            c_diff = (
                f"+{c.diff_kwh:,.2f}"
                if c.diff_kwh > 0
                else f"-{abs(c.diff_kwh):,.2f}"
                if c.diff_kwh < 0
                else "0.00"
            )
            c_pct = (
                f"+{c.pct_change:.1f}%"
                if (c.pct_change is not None and c.pct_change > 0)
                else f"{c.pct_change:.1f}%"
                if c.pct_change is not None
                else "N/A"
            )
            lines.append(
                f"| {idx} | `{c.cups}` | {c_base:,.2f} | {c_target:,.2f} | {c_diff} | {c_pct} |"
            )
        lines.append("")

    # Section 4: Key Insights
    lines.append(t("md_compare_insights", lang=lang))
    lines.append("")
    if comparison.max_decrease_month:
        m_name = get_month_name(comparison.max_decrease_month.month, lang=lang)
        pct_val = abs(comparison.max_decrease_month.pct_change or 0.0)
        lines.append(
            f"- **{t('compare_max_decrease', lang=lang).rstrip(':')}:** {m_name} (-{pct_val:.1f}% / -{format_kwh(abs(comparison.max_decrease_month.diff_kwh))})"
        )
    if comparison.max_increase_month:
        m_name = get_month_name(comparison.max_increase_month.month, lang=lang)
        pct_val = comparison.max_increase_month.pct_change or 0.0
        lines.append(
            f"- **{t('compare_max_increase', lang=lang).rstrip(':')}:** {m_name} (+{pct_val:.1f}% / +{format_kwh(comparison.max_increase_month.diff_kwh)})"
        )
    if comparison.top_saving_cups:
        lines.append(
            f"- **{t('compare_top_saver', lang=lang).rstrip(':')}:** `{comparison.top_saving_cups.cups}` (-{format_kwh(abs(comparison.top_saving_cups.diff_kwh))})"
        )
    if comparison.top_increasing_cups:
        lines.append(
            f"- **{t('compare_top_increaser', lang=lang).rstrip(':')}:** `{comparison.top_increasing_cups.cups}` (+{format_kwh(comparison.top_increasing_cups.diff_kwh)})"
        )
    lines.append("")

    report_content = "\n".join(lines) + "\n"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path
