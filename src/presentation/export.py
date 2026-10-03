"""Markdown report generator exporting community energy summaries to .output/."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import DEFAULT_OUTPUT_DIR
from src.i18n import t
from src.presentation.console import format_kwh, format_pct
from src.processing.models import CommunitySummary


def _make_ascii_bar(pct: float, width: int = 12) -> str:
    """Create a plain text block bar suitable for standard Markdown rendering."""
    pct_clamped = max(0.0, min(100.0, pct))
    filled_len = int(round((pct_clamped / 100.0) * width))
    empty_len = width - filled_len
    return "`" + "█" * filled_len + "░" * empty_len + "`"


def export_markdown_summary(
    summary: CommunitySummary,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    lang: Optional[str] = None,
    year_filter: Optional[int] = None,
    cups_filter: Optional[str] = None,
    view_mode: str = "all",
) -> Path:
    """Generate and persist a complete community summary report in Markdown format.

    The output filename begins with a datetime down to seconds (e.g. 'YYYYMMDD_HHMMSS_summary.md').

    Args:
        summary: Aggregated CommunitySummary dataset.
        output_dir: Directory where the report will be saved (default: .output).
        lang: Target language ('en' or 'es').
        year_filter: Optional year filter applied.
        cups_filter: Optional CUPS filter applied.
        view_mode: Selected view mode ('all', 'annual', 'monthly').

    Returns:
        Path to the saved markdown file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    timestamp_prefix = now.strftime("%Y%m%d_%H%M%S")

    # Construct concise filename
    if year_filter:
        filename = f"{timestamp_prefix}_summary_{year_filter}.md"
    elif cups_filter:
        filename = f"{timestamp_prefix}_summary_{cups_filter}.md"
    else:
        filename = f"{timestamp_prefix}_community_summary.md"

    report_path = output_dir / filename

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
    lines.append(f"| {t('total_community_consumption', lang=lang).rstrip(':')} | **{format_kwh(summary.total_community_kwh)}** |")
    lines.append(f"| {t('active_cups_meters', lang=lang).rstrip(':')} | {summary.unique_cups_count} |")
    lines.append(f"| {t('date_range', lang=lang).rstrip(':')} | {summary.date_min} to {summary.date_max} |")
    lines.append(f"| {t('peak_month', lang=lang).rstrip(':')} | {summary.peak_month_label} ({format_kwh(summary.peak_month_kwh)}) |")
    lines.append(f"| {t('total_hourly_readings', lang=lang).rstrip(':')} | {summary.total_readings:,} |")
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
            lines.append(f"*{t('community_total_label', lang=lang, total=format_kwh(annual.community_total_kwh))}*")
            lines.append("")
            lines.append(f"| {t('col_rank', lang=lang)} | {t('col_cups', lang=lang)} | {t('col_consumption', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |")
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
        lines.append(f"| {t('col_period', lang=lang)} | {t('col_community_total', lang=lang)} | {t('col_top_cups', lang=lang)} | {t('col_top_share', lang=lang)} | {t('col_distribution', lang=lang)} |")
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
            lines.append(f"*{t('community_total_label', lang=lang, total=format_kwh(m.community_total_kwh))}*")
            lines.append("")
            lines.append(f"| {t('col_rank', lang=lang)} | {t('col_cups', lang=lang)} | {t('col_consumption', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |")
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
        lines.append(f"| {t('col_period', lang=lang)} | {t('col_cups_kwh', lang=lang)} | {t('col_community_kwh', lang=lang)} | {t('col_share', lang=lang)} | {t('col_distribution', lang=lang)} |")
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
        lines.append(f"| **{t('col_total', lang=lang)}** | **{format_kwh(total_c)}** | **{format_kwh(total_comm)}** | **{format_pct(ov_share)}** | |")
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
