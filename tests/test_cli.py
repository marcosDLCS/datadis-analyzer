"""Tests for the Typer command-line interface entrypoints."""

from pathlib import Path

from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


def test_cli_help_command() -> None:
    """The 'da help' command should display the formatted reference guide with tables."""
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "DATADIS ANALYZER" in result.stdout
    assert "AVAILABLE COMMANDS" in result.stdout
    assert "da summary" in result.stdout
    assert "OPTIONS FOR 'da summary'" in result.stdout
    assert "Quick Start Examples" in result.stdout
    assert "Command / Example" in result.stdout


def test_cli_help_spanish_command() -> None:
    """The 'da help --lang es' command displays Spanish tables including Quick Start Examples."""
    result = runner.invoke(app, ["help", "--lang", "es"])
    assert result.exit_code == 0
    assert "COMANDOS DISPONIBLES" in result.stdout
    assert "Ejemplos de Inicio Rápido" in result.stdout
    assert "Comando / Ejemplo" in result.stdout


def test_cli_no_args_displays_help() -> None:
    """Invoking 'da' without arguments should render the custom help screen."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "DATADIS ANALYZER" in result.stdout
    assert "Quick Start Examples" in result.stdout


def test_cli_summary_on_mock_data(sample_input_hierarchy: Path) -> None:
    """The 'da summary' command should execute successfully on valid input directory."""
    result = runner.invoke(app, ["summary", "-i", str(sample_input_hierarchy)])
    assert result.exit_code == 0
    assert "Residential Community Energy Overview" in result.stdout
    assert "Annual Summary — Year 2024" in result.stdout
    assert "Annual Summary — Year 2025" in result.stdout
    assert "Period 2024-05" in result.stdout
    assert "Period 2025-01" in result.stdout
    assert "ES0021000000000002BB" in result.stdout


def test_cli_summary_year_filter(sample_input_hierarchy: Path) -> None:
    """The 'da summary --year 2024' command should only display the filtered year."""
    result = runner.invoke(app, ["summary", "-i", str(sample_input_hierarchy), "--year", "2024"])
    assert result.exit_code == 0
    assert "Year 2024" in result.stdout
    assert "Year 2025" not in result.stdout


def test_cli_summary_view_monthly(sample_input_hierarchy: Path) -> None:
    """The 'da summary --view monthly' should render detailed monthly period tables."""
    result = runner.invoke(app, ["summary", "-i", str(sample_input_hierarchy), "--view", "monthly"])
    assert result.exit_code == 0
    assert "Period 2024-05" in result.stdout
    assert "Period 2024-06" in result.stdout


def test_cli_summary_single_cups(sample_input_hierarchy: Path) -> None:
    """The 'da summary --cups <CUPS>' should display dedicated CUPS monthly trajectory."""
    target_cups = "ES0021000000000001AA"
    result = runner.invoke(
        app, ["summary", "-i", str(sample_input_hierarchy), "--cups", target_cups]
    )
    assert result.exit_code == 0
    assert f"Monthly Trajectory for CUPS: {target_cups}" in result.stdout
    assert "Period" in result.stdout
    assert "CUPS kWh" in result.stdout


def test_cli_summary_invalid_cups(sample_input_hierarchy: Path) -> None:
    """The 'da summary --cups INVALID' should exit with error code 1."""
    result = runner.invoke(
        app, ["summary", "-i", str(sample_input_hierarchy), "--cups", "ES9999999999999999ZZ"]
    )
    assert result.exit_code == 1
    assert "not found in the loaded dataset" in result.stdout


def test_cli_summary_invalid_view(sample_input_hierarchy: Path) -> None:
    """The 'da summary --view invalid' should exit with error code 1."""
    result = runner.invoke(
        app, ["summary", "-i", str(sample_input_hierarchy), "--view", "invalid_mode"]
    )
    assert result.exit_code == 1
    assert "Invalid view mode" in result.stdout


def test_cli_summary_nonexistent_directory(tmp_path: Path) -> None:
    """The 'da summary -i /nonexistent' should exit with error code 1."""
    missing_dir = tmp_path / "does_not_exist"
    result = runner.invoke(app, ["summary", "-i", str(missing_dir)])
    assert result.exit_code == 1
    assert "Error:" in result.stdout


def test_cli_cleanup_empty_directory(tmp_path: Path) -> None:
    """The 'da cleanup' on empty directory should notify without error."""
    out_dir = tmp_path / "empty_out"
    out_dir.mkdir()
    result = runner.invoke(app, ["cleanup", "-o", str(out_dir), "-f", "--lang", "en"])
    assert result.exit_code == 0
    assert "already empty" in result.stdout


def test_cli_cleanup_removes_files_force(tmp_path: Path) -> None:
    """The 'da cleanup --force' should delete files without interactive confirmation."""
    out_dir = tmp_path / "report_out"
    out_dir.mkdir()
    f1 = out_dir / "report1.md"
    f2 = out_dir / "report2.md"
    f1.write_text("sample 1", encoding="utf-8")
    f2.write_text("sample 2", encoding="utf-8")

    assert f1.exists() and f2.exists()

    result = runner.invoke(app, ["cleanup", "-o", str(out_dir), "--force", "--lang", "en"])
    assert result.exit_code == 0
    assert "Successfully removed 2 file(s)" in result.stdout
    assert not f1.exists()
    assert not f2.exists()


def test_cli_cleanup_interactive_confirm(tmp_path: Path) -> None:
    """The 'da cleanup' with 'y' input should confirm and delete files."""
    out_dir = tmp_path / "confirm_out"
    out_dir.mkdir()
    f1 = out_dir / "report.md"
    f1.write_text("sample", encoding="utf-8")

    result = runner.invoke(app, ["cleanup", "-o", str(out_dir), "--lang", "en"], input="y\n")
    assert result.exit_code == 0
    assert "Successfully removed 1 file(s)" in result.stdout
    assert not f1.exists()


def test_cli_cleanup_interactive_abort(tmp_path: Path) -> None:
    """The 'da cleanup' with 'n' input should abort and preserve files."""
    out_dir = tmp_path / "abort_out"
    out_dir.mkdir()
    f1 = out_dir / "report.md"
    f1.write_text("sample", encoding="utf-8")

    result = runner.invoke(app, ["cleanup", "-o", str(out_dir), "--lang", "en"], input="n\n")
    assert result.exit_code == 0
    assert "Cleanup aborted" in result.stdout
    assert f1.exists()


def test_cli_clean_alias(tmp_path: Path) -> None:
    """The 'da clean' alias should execute cleanup identically."""
    out_dir = tmp_path / "clean_alias_out"
    out_dir.mkdir()
    f1 = out_dir / "test.md"
    f1.write_text("content", encoding="utf-8")

    result = runner.invoke(app, ["clean", "-o", str(out_dir), "-f", "--lang", "es"])
    assert result.exit_code == 0
    assert "Se han eliminado 1 archivo(s)" in result.stdout
    assert not f1.exists()
