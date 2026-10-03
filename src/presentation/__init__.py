"""Presentation layer for DATADIS console interface and export utilities."""

from src.presentation.console import console, format_kwh, format_pct, make_share_bar
from src.presentation.export import export_markdown_summary
from src.presentation.views import (
    render_annual_tables,
    render_community_overview,
    render_cups_trajectory,
    render_detailed_monthly_breakdown,
    render_export_success,
    render_help,
    render_init_success,
    render_key_insights,
    render_monthly_overview,
    render_not_initialized_error,
    render_validation_issues,
)

__all__ = [
    "console",
    "export_markdown_summary",
    "format_kwh",
    "format_pct",
    "make_share_bar",
    "render_annual_tables",
    "render_community_overview",
    "render_cups_trajectory",
    "render_detailed_monthly_breakdown",
    "render_export_success",
    "render_help",
    "render_init_success",
    "render_key_insights",
    "render_monthly_overview",
    "render_not_initialized_error",
    "render_validation_issues",
]
