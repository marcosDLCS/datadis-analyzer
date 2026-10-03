"""Tests for year-over-year comparison processing, presentation, and CLI commands."""

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.cli import app
from src.ingestion.loader import DatadisLoader
from src.ingestion.schema import DatadisError
from src.presentation.export import export_comparison_markdown
from src.processing.aggregator import DataAggregator

runner = CliRunner()


def test_compare_years_default_all_years(sample_input_hierarchy: Path) -> None:
    """compare_years without target_years should compare all years in the dataset."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)

    comparison = DataAggregator.compare_years(df)

    assert comparison.years == [2024, 2025]
    assert comparison.annual_totals[2024] == 100.0
    assert comparison.annual_totals[2025] == 100.0
    # Because months in sample_input_hierarchy are incomplete / non-overlapping, comparable_months is empty
    assert comparison.comparable_months == []
    assert comparison.excluded_months == [1, 5, 6]
    assert comparison.total_diff_kwh is None
    assert comparison.total_pct_change is None

    # Verify monthly comparisons (months 1, 5, 6 have data)
    months = {m.month: m for m in comparison.monthly_comparisons}
    assert 1 in months
    assert 5 in months
    assert 6 in months

    # Month 1 (Jan): 2024 had no data, 2025 had incomplete data (1 day)
    assert months[1].is_complete is False
    assert months[1].year_status[2024] == "no_data"
    assert months[1].year_status[2025] == "incomplete"
    assert months[1].diff_kwh is None
    assert months[1].pct_change is None

    # Month 5 (May): 2024 had incomplete data, 2025 had no data
    assert months[5].is_complete is False
    assert months[5].year_status[2024] == "incomplete"
    assert months[5].year_status[2025] == "no_data"
    assert months[5].diff_kwh is None
    assert months[5].pct_change is None


def test_compare_years_explicit_target_years(sample_input_hierarchy: Path) -> None:
    """compare_years with explicit target_years should filter to requested years."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)

    comparison = DataAggregator.compare_years(df, target_years=[2024, 2025])
    assert comparison.years == [2024, 2025]


def test_compare_years_raises_on_single_year(sample_input_hierarchy: Path) -> None:
    """compare_years should raise DatadisError when fewer than two distinct years are given."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)

    with pytest.raises(DatadisError, match="At least two distinct years"):
        DataAggregator.compare_years(df, target_years=[2024])


def test_compare_years_raises_on_missing_year(sample_input_hierarchy: Path) -> None:
    """compare_years should raise DatadisError when requested year does not exist."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)

    with pytest.raises(DatadisError, match=r"Requested year.*not found"):
        DataAggregator.compare_years(df, target_years=[2020, 2024])


def test_compare_years_raises_on_empty_df() -> None:
    """compare_years should raise DatadisError on empty DataFrame."""
    import pandas as pd

    with pytest.raises(DatadisError, match="Cannot compare an empty DataFrame"):
        DataAggregator.compare_years(pd.DataFrame())


def test_cli_compare_command(sample_input_hierarchy: Path) -> None:
    """The 'da compare' command should execute successfully on valid input directory."""
    result = runner.invoke(app, ["compare", "-i", str(sample_input_hierarchy)])
    assert result.exit_code == 0
    assert "Multi-Year Community Energy Comparison" in result.stdout
    assert "2024" in result.stdout
    assert "2025" in result.stdout
    assert "Monthly Community Consumption & Year-over-Year Variation" in result.stdout
    assert "Total" in result.stdout


def test_cli_compare_command_with_years_flag(sample_input_hierarchy: Path) -> None:
    """The 'da compare --years 2024,2025' should filter and compare specified years."""
    result = runner.invoke(
        app, ["compare", "-i", str(sample_input_hierarchy), "--years", "2024,2025"]
    )
    assert result.exit_code == 0
    assert "2024" in result.stdout
    assert "2025" in result.stdout


def test_cli_compare_command_multiple_y_flags(sample_input_hierarchy: Path) -> None:
    """The 'da compare -y 2024 -y 2025' should accept multiple -y arguments."""
    result = runner.invoke(
        app, ["compare", "-i", str(sample_input_hierarchy), "-y", "2024", "-y", "2025"]
    )
    assert result.exit_code == 0
    assert "2024" in result.stdout
    assert "2025" in result.stdout


def test_cli_compare_invalid_year_string(sample_input_hierarchy: Path) -> None:
    """Passing a non-numeric year string should report an error and exit with code 1."""
    result = runner.invoke(
        app, ["compare", "-i", str(sample_input_hierarchy), "--years", "invalid_year,2025"]
    )
    assert result.exit_code == 1
    assert "Invalid year 'invalid_year'" in result.stdout


def test_cli_compare_nonexistent_year(sample_input_hierarchy: Path) -> None:
    """Passing a year not present in the dataset should report an error and exit with code 1."""
    result = runner.invoke(
        app, ["compare", "-i", str(sample_input_hierarchy), "--years", "2019,2024"]
    )
    assert result.exit_code == 1
    assert "Error:" in result.stdout


def test_cli_compare_spanish(sample_input_hierarchy: Path) -> None:
    """The 'da compare --lang es' should render comparison in Spanish."""
    result = runner.invoke(app, ["compare", "-i", str(sample_input_hierarchy), "--lang", "es"])
    assert result.exit_code == 0
    assert "Comparativa Energética Interanual de la Comunidad" in result.stdout
    assert "Consumo Mensual y Variación Interanual" in result.stdout


def test_cli_compare_exports_markdown_report(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """The 'da compare' must generate a markdown comparison report with timestamp prefix."""
    out_dir = tmp_path / "comp_out"
    result = runner.invoke(
        app,
        ["compare", "-i", str(sample_input_hierarchy), "-o", str(out_dir), "--lang", "en"],
    )
    assert result.exit_code == 0

    exported_files = list(out_dir.glob("*.md"))
    assert len(exported_files) == 1

    pattern = r"^\d{8}_\d{6}_comparison_2024_2025\.md$"
    assert re.match(pattern, exported_files[0].name) is not None

    content = exported_files[0].read_text(encoding="utf-8")
    assert "# ⚡ Multi-Year Community Energy Comparison (2024 vs 2025)" in content
    assert "Executive Comparison Overview" in content
    assert "Month-by-Month Consumption Comparison" in content
    assert "2024 (kWh)" in content
    assert "2025 (kWh)" in content


def test_compare_never_pollutes_production_output(sample_input_hierarchy: Path) -> None:
    """Running 'da compare' without explicit -o must never write to production .output directory."""
    real_output_dir = Path(".output")
    initial_files = set(real_output_dir.glob("*")) if real_output_dir.exists() else set()

    result = runner.invoke(app, ["compare", "-i", str(sample_input_hierarchy)])
    assert result.exit_code == 0

    current_files = set(real_output_dir.glob("*")) if real_output_dir.exists() else set()
    assert current_files == initial_files, "Production .output directory was modified by compare!"


def test_export_comparison_markdown_direct(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """Direct call to export_comparison_markdown should produce structured file."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    comparison = DataAggregator.compare_years(df)

    out_dir = tmp_path / "custom_comp_dir"
    report_file = export_comparison_markdown(comparison, output_dir=out_dir, lang="es")

    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Comparativa Energética Interanual" in content
    assert "Resumen Ejecutivo" in content


def test_compare_complete_month_calculation(tmp_path: Path) -> None:
    """When a month has all calendar days recorded in all compared years, it must be marked complete and compared."""
    input_dir = tmp_path / "complete_input"
    dir_2024 = input_dir / "2024"
    dir_2025 = input_dir / "2025"
    dir_2024.mkdir(parents=True)
    dir_2025.mkdir(parents=True)

    # Generate 28 days for Feb in 2025 and 29 days in 2024
    lines_2024 = ["cups;fecha;hora;consumo_kWh"]
    for day in range(1, 30):
        lines_2024.append(f'"ES0021000000000001AA";"2024/02/{day:02d}";"12:00";"1,00"')
    (dir_2024 / "feb_2024.csv").write_text("\n".join(lines_2024) + "\n", encoding="utf-8")

    lines_2025 = ["cups;fecha;hora;consumo_kWh"]
    for day in range(1, 29):
        lines_2025.append(f'"ES0021000000000001AA";"2025/02/{day:02d}";"12:00";"2,00"')
    (dir_2025 / "feb_2025.csv").write_text("\n".join(lines_2025) + "\n", encoding="utf-8")

    loader = DatadisLoader()
    df, _ = loader.load_all(input_dir)
    comparison = DataAggregator.compare_years(df)

    assert comparison.years == [2024, 2025]
    assert comparison.comparable_months == [2]
    assert len(comparison.monthly_comparisons) == 1
    m2 = comparison.monthly_comparisons[0]
    assert m2.month == 2
    assert m2.is_complete is True
    assert m2.yearly_kwh[2024] == 29.0
    assert m2.yearly_kwh[2025] == 56.0
    assert m2.diff_kwh == 27.0
    assert m2.pct_change is not None and round(m2.pct_change, 1) == 93.1
    assert comparison.total_diff_kwh == 27.0


def test_charts_generation_and_export(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """generate_all_comparison_charts must produce community and CUPS png images."""
    from src.presentation.charts import generate_all_comparison_charts

    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    comparison = DataAggregator.compare_years(df)

    out_dir = tmp_path / "charts_out"
    chart_files = generate_all_comparison_charts(comparison, out_dir, lang="en")

    # Community chart + 2 CUPS = 3 charts
    assert len(chart_files) == 3
    for cf in chart_files:
        assert cf.exists()
        assert cf.stat().st_size > 0
        assert cf.suffix == ".png"

    # Export markdown and verify images are referenced
    report = export_comparison_markdown(
        comparison,
        output_dir=out_dir,
        lang="en",
        chart_paths=chart_files,
    )
    content = report.read_text(encoding="utf-8")
    assert "community_monthly_2024_2025.png" in content
    assert "cups_ES0021000000000001AA_2024_2025.png" in content
    assert "cups_ES0021000000000002BB_2024_2025.png" in content


def test_cli_compare_no_charts_flag(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """The 'da compare --no-charts' flag should skip chart generation."""
    out_dir = tmp_path / "no_charts_out"
    result = runner.invoke(
        app,
        ["compare", "-i", str(sample_input_hierarchy), "-o", str(out_dir), "--no-charts"],
    )
    assert result.exit_code == 0
    charts_dir = out_dir / "charts"
    assert not charts_dir.exists()
