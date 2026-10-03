"""Tests for configuration persistence, internationalization, da init command, and markdown export."""

import re
from pathlib import Path
from typer.testing import CliRunner

from src.cli import app
from src.config import (
    AppConfig,
    get_language,
    load_config,
    save_config,
    set_language,
)
from src.i18n import t
from src.ingestion.loader import DatadisLoader
from src.presentation.export import export_markdown_summary
from src.processing.aggregator import DataAggregator

runner = CliRunner()


def test_config_save_and_load(tmp_path: Path) -> None:
    """Config should persist and reload correctly from disk."""
    cfg_file = tmp_path / ".da_config.json"
    cfg = AppConfig(language="es", input_dir="custom_input", output_dir="custom_output")
    save_config(cfg, cfg_file)

    loaded = load_config(cfg_file)
    assert loaded.language == "es"
    assert loaded.input_dir == "custom_input"
    assert loaded.output_dir == "custom_output"


def test_set_and_get_language(tmp_path: Path) -> None:
    """Setting language should validate and update configuration file."""
    cfg_file = tmp_path / ".da_config.json"
    set_language("spanish", cfg_file)
    assert get_language(cfg_file) == "es"

    set_language("English", cfg_file)
    assert get_language(cfg_file) == "en"


def test_i18n_translation_fallback() -> None:
    """Translator should return English or Spanish according to requested code."""
    assert "DATADIS" in t("app_title", lang="en")
    assert "ANALIZADOR" in t("app_title", lang="es")
    # Missing key fallback returns key
    assert t("non_existent_key_123", lang="en") == "non_existent_key_123"


def test_export_markdown_naming_and_content(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """Markdown export must start with datetime with seconds and contain structured tables."""
    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    summary = DataAggregator.aggregate_community(df)

    out_dir = tmp_path / ".output"
    report_file = export_markdown_summary(summary, output_dir=out_dir, lang="es")

    assert report_file.exists()
    assert report_file.parent == out_dir

    # Filename must begin with YYYYMMDD_HHMMSS (datetime with seconds)
    pattern = r"^\d{8}_\d{6}_.*\.md$"
    assert re.match(pattern, report_file.name) is not None

    content = report_file.read_text(encoding="utf-8")
    assert "# Informe Energético de la Comunidad de Propietarios (DATADIS)" in content
    assert "Resumen Ejecutivo" in content
    assert "Consumo Anual y Porcentajes de Reparto por CUPS" in content
    assert "ES0021000000000002BB" in content
    assert "100.00%" in content


def test_cli_init_command_with_flag() -> None:
    """The 'da init --language es' should configure language to Spanish."""
    result = runner.invoke(app, ["init", "--language", "es"])
    assert result.exit_code == 0
    assert "Español" in result.stdout or "Spanish" in result.stdout

    # Verify persistent config
    assert get_language() == "es"

    # Reset back to English
    result_en = runner.invoke(app, ["init", "-l", "en"])
    assert result_en.exit_code == 0
    assert get_language() == "en"


def test_cli_init_command_interactive() -> None:
    """The 'da init' should accept language choice via interactive prompt."""
    result = runner.invoke(app, ["init"], input="es\n")
    assert result.exit_code == 0
    assert get_language() == "es"

    # Reset
    runner.invoke(app, ["init"], input="en\n")
    assert get_language() == "en"


def test_cli_init_invalid_language() -> None:
    """The 'da init --language invalid' should exit with code 1."""
    result = runner.invoke(app, ["init", "--language", "french"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout


def test_cli_summary_exports_markdown_file(sample_input_hierarchy: Path, tmp_path: Path) -> None:
    """The 'da summary' must save a markdown file into the output directory."""
    out_dir = tmp_path / "test_output"
    result = runner.invoke(
        app,
        ["summary", "-i", str(sample_input_hierarchy), "-o", str(out_dir), "--lang", "en"],
    )
    assert result.exit_code == 0
    assert "Markdown summary report saved to:" in result.stdout

    saved_files = list(out_dir.glob("*.md"))
    assert len(saved_files) == 1
    # Check datetime with seconds pattern
    assert re.match(r"^\d{8}_\d{6}_.*\.md$", saved_files[0].name) is not None
