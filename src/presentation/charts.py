"""Chart generation module for DATADIS multi-year consumption comparisons using Matplotlib."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Headless backend for terminal/CLI environments
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.i18n import get_month_name, t
from src.processing.models import ComparisonSummary

# Modern, harmonious palette for multi-year visual distinction
YEAR_PALETTE = [
    "#2563EB",  # Vibrant Blue
    "#10B981",  # Emerald Teal
    "#F59E0B",  # Warm Amber
    "#8B5CF6",  # Modern Purple
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
]


def _format_kwh_compact(val: float) -> str:
    """Format energy values with thousands commas and 1 decimal place."""
    return f"{val:,.1f} kWh"


def generate_community_bar_chart(
    comparison: ComparisonSummary,
    output_dir: Path,
    lang: str = "en",
) -> Path:
    """Generate and save a grouped bar chart comparing community monthly consumption across years.

    Args:
        comparison: Multi-year comparison summary dataset.
        output_dir: Destination root directory.
        lang: Selected language ('en' or 'es').

    Returns:
        Path to the saved community chart image.
    """
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    years_slug = "_".join(map(str, comparison.years))
    chart_path = charts_dir / f"community_monthly_{years_slug}.png"

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    # 12 Calendar months
    months = list(range(1, 13))
    month_labels = [get_month_name(m, lang=lang, short=True) for m in months]
    n_years = len(comparison.years)
    total_group_width = 0.8
    bar_width = total_group_width / n_years

    # Map monthly comparisons
    month_map = {m.month: m for m in comparison.monthly_comparisons}

    for i, year in enumerate(comparison.years):
        color = YEAR_PALETTE[i % len(YEAR_PALETTE)]
        year_values: list[float] = []
        for m in months:
            m_comp = month_map.get(m)
            kwh = (m_comp.yearly_kwh.get(year) if m_comp else None) or 0.0
            year_values.append(float(kwh))

        x_positions = [
            m_idx - (total_group_width / 2.0) + (i + 0.5) * bar_width
            for m_idx in range(len(months))
        ]
        ann_total = comparison.annual_totals.get(year, 0.0)
        label = (
            f"{year} ({t('chart_legend_total', lang=lang, total=_format_kwh_compact(ann_total))})"
        )
        ax.bar(
            x_positions,
            year_values,
            width=bar_width * 0.92,
            color=color,
            label=label,
            edgecolor="none",
            alpha=0.92,
        )

    # Style axes
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(month_labels, fontsize=10, fontweight="normal")
    ax.set_xlabel(t("chart_month_axis", lang=lang), fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel(t("chart_kwh_axis", lang=lang), fontsize=11, fontweight="bold", labelpad=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:,.0f}"))

    # Title & Subtitle
    title_text = t("chart_community_title", lang=lang)
    years_str = " ➔ ".join(map(str, comparison.years))
    subtitle_text = t("chart_subtitle", lang=lang, years=years_str)
    ax.set_title(f"{title_text}\n{subtitle_text}", fontsize=12, fontweight="bold", pad=12)

    # Clean borders and grid
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.grid(axis="y", linestyle="--", alpha=0.35, color="#94a3b8")
    ax.set_axisbelow(True)

    ax.legend(frameon=True, facecolor="#f8fafc", edgecolor="#cbd5e1", fontsize=9, loc="upper right")
    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close(fig)
    return chart_path


def generate_cups_bar_charts(
    comparison: ComparisonSummary,
    output_dir: Path,
    lang: str = "en",
) -> list[Path]:
    """Generate and save grouped bar charts for every individual supply point (CUPS).

    Args:
        comparison: Multi-year comparison summary dataset.
        output_dir: Destination root directory.
        lang: Selected language ('en' or 'es').

    Returns:
        List of Path objects for all generated CUPS chart images.
    """
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    years_slug = "_".join(map(str, comparison.years))
    years_str = " ➔ ".join(map(str, comparison.years))

    months = list(range(1, 13))
    month_labels = [get_month_name(m, lang=lang, short=True) for m in months]
    n_years = len(comparison.years)
    total_group_width = 0.8
    bar_width = total_group_width / n_years

    generated_paths: list[Path] = []

    for cups, years_data in comparison.cups_monthly_data.items():
        chart_path = charts_dir / f"cups_{cups}_{years_slug}.png"
        fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)

        for i, year in enumerate(comparison.years):
            color = YEAR_PALETTE[i % len(YEAR_PALETTE)]
            monthly_dict = years_data.get(year, {})
            year_values = [float(monthly_dict.get(m, 0.0)) for m in months]

            x_positions = [
                m_idx - (total_group_width / 2.0) + (i + 0.5) * bar_width
                for m_idx in range(len(months))
            ]
            cups_annual = sum(year_values)
            label = f"{year} ({t('chart_legend_total', lang=lang, total=_format_kwh_compact(cups_annual))})"
            ax.bar(
                x_positions,
                year_values,
                width=bar_width * 0.92,
                color=color,
                label=label,
                edgecolor="none",
                alpha=0.92,
            )

        # Style axes
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(month_labels, fontsize=9.5, fontweight="normal")
        ax.set_xlabel(
            t("chart_month_axis", lang=lang), fontsize=10.5, fontweight="bold", labelpad=8
        )
        ax.set_ylabel(t("chart_kwh_axis", lang=lang), fontsize=10.5, fontweight="bold", labelpad=8)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{x:,.0f}"))

        # Titles
        cups_title = t("chart_cups_title", lang=lang, cups=cups)
        subtitle = t("chart_subtitle", lang=lang, years=years_str)
        ax.set_title(f"{cups_title}\n{subtitle}", fontsize=11.5, fontweight="bold", pad=10)

        # Clean borders and grid
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cbd5e1")
        ax.spines["bottom"].set_color("#cbd5e1")
        ax.grid(axis="y", linestyle="--", alpha=0.35, color="#94a3b8")
        ax.set_axisbelow(True)

        ax.legend(
            frameon=True, facecolor="#f8fafc", edgecolor="#cbd5e1", fontsize=8.5, loc="upper right"
        )
        plt.tight_layout()
        plt.savefig(chart_path, bbox_inches="tight")
        plt.close(fig)
        generated_paths.append(chart_path)

    return generated_paths


def generate_all_comparison_charts(
    comparison: ComparisonSummary,
    output_dir: Path,
    lang: str = "en",
) -> list[Path]:
    """Generate both community and individual CUPS multi-year comparison charts.

    Args:
        comparison: Multi-year comparison summary dataset.
        output_dir: Destination root directory.
        lang: Selected language ('en' or 'es').

    Returns:
        Combined list of paths for all generated chart images.
    """
    community_chart = generate_community_bar_chart(comparison, output_dir, lang=lang)
    cups_charts = generate_cups_bar_charts(comparison, output_dir, lang=lang)
    return [community_chart, *cups_charts]
