"""Unit and integration tests for mandatory initialization and CalVer versioning system."""

import re
from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.cli import app
from src.config import (
    AppConfig,
    is_initialized,
    load_config,
    save_config,
)
from src.presentation.export import export_comparison_markdown, export_markdown_summary
from src.processing.aggregator import DataAggregator
from src.version import (
    bump_version_files,
    check_version_consistency,
    format_version,
    generate_next_version,
    get_version,
    parse_version,
)

runner = CliRunner()


def test_get_version_matches_calver_pattern() -> None:
    """The current version must conform to <year>.<month>.<incremental number> (e.g. 2026.10.001)."""
    ver = get_version()
    match = re.match(r"^\d{4}\.\d{2}\.\d{3}$", ver)
    assert match is not None, f"Version '{ver}' does not match YYYY.MM.NNN format"


def test_parse_version() -> None:
    """parse_version extracts year, month, and sequence correctly."""
    y, m, s = parse_version("2026.10.001")
    assert (y, m, s) == (2026, 10, 1)

    y, m, s = parse_version("2025.04.042")
    assert (y, m, s) == (2025, 4, 42)

    with pytest.raises(ValueError, match="Invalid version format"):
        parse_version("0.1.0")

    with pytest.raises(ValueError, match="Invalid version format"):
        parse_version("2026.1.1")


def test_format_version() -> None:
    """format_version creates zero-padded strings."""
    assert format_version(2026, 10, 1) == "2026.10.001"
    assert format_version(2026, 3, 15) == "2026.03.015"


def test_generate_next_version_same_month() -> None:
    """Within the same year and month, the sequence increments by 1."""
    d = datetime(2026, 10, 15)
    next_v = generate_next_version("2026.10.001", target_date=d)
    assert next_v == "2026.10.002"

    next_v_2 = generate_next_version("2026.10.099", target_date=d)
    assert next_v_2 == "2026.10.100"


def test_generate_next_version_new_month_or_year() -> None:
    """When rolling over to a new month or year, sequence resets to 001."""
    next_month = datetime(2026, 11, 1)
    next_v = generate_next_version("2026.10.005", target_date=next_month)
    assert next_v == "2026.11.001"

    next_year = datetime(2027, 1, 1)
    next_v_year = generate_next_version("2026.12.010", target_date=next_year)
    assert next_v_year == "2027.01.001"


def test_check_version_consistency_repo_root() -> None:
    """Repository root version files must be consistent and valid."""
    valid, msg = check_version_consistency()
    assert valid is True, msg


def test_bump_version_in_isolated_dir(tmp_path: Path) -> None:
    """bump_version_files correctly updates both pyproject.toml and src/version.py in a directory."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text('[project]\nname = "test"\nversion = "2026.10.001"\n', encoding="utf-8")
    ver_py = src_dir / "version.py"
    ver_py.write_text('__version__ = "2026.10.001"\n', encoding="utf-8")

    fixed_date = datetime(2026, 10, 20)
    new_ver = bump_version_files(repo_root=tmp_path, target_date=fixed_date)
    assert new_ver == "2026.10.002"

    assert 'version = "2026.10.002"' in pyproj.read_text(encoding="utf-8")
    assert '__version__ = "2026.10.002"' in ver_py.read_text(encoding="utf-8")


def test_cli_version_flag() -> None:
    """The 'da --version' and 'da -V' flags display the CalVer version and exit 0."""
    result_long = runner.invoke(app, ["--version"])
    assert result_long.exit_code == 0
    assert get_version() in result_long.stdout
    assert "DATADIS Analyzer (da)" in result_long.stdout

    result_short = runner.invoke(app, ["-V"])
    assert result_short.exit_code == 0
    assert get_version() in result_short.stdout


def test_cli_help_displays_version() -> None:
    """The 'da help' manual displays the active version in the header banner."""
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert f"v{get_version()}" in result.stdout


def test_cli_init_displays_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The 'da init' command displays the active version during initialization."""
    test_config = tmp_path / "init_test_config.json"
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", test_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", test_config)

    result = runner.invoke(app, ["init", "--language", "en"])
    assert result.exit_code == 0
    assert get_version() in result.stdout
    assert "DATADIS Analyzer Version:" in result.stdout

    # Verify initialized_at was written to config
    cfg = load_config(test_config)
    assert cfg.initialized_at is not None
    assert is_initialized(test_config) is True


def test_mandatory_init_blocks_summary_when_not_initialized(
    sample_input_hierarchy: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Running 'da summary' without prior initialization must fail with exit code 1."""
    uninit_config = tmp_path / "uninit_config.json"
    save_config(
        AppConfig(language="en", input_dir=".input", output_dir=".output", initialized_at=None),
        uninit_config,
    )
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", uninit_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", uninit_config)

    result = runner.invoke(app, ["summary", "-i", str(sample_input_hierarchy)])
    assert result.exit_code == 1
    assert "Initialization Required" in result.stdout or "Error:" in result.stdout
    assert "da init" in result.stdout


def test_mandatory_init_blocks_compare_when_not_initialized(
    sample_input_hierarchy: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Running 'da compare' without prior initialization must fail with exit code 1."""
    uninit_config = tmp_path / "uninit_config.json"
    save_config(
        AppConfig(language="en", input_dir=".input", output_dir=".output", initialized_at=None),
        uninit_config,
    )
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", uninit_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", uninit_config)

    result = runner.invoke(app, ["compare", "-i", str(sample_input_hierarchy)])
    assert result.exit_code == 1
    assert "Initialization Required" in result.stdout or "Error:" in result.stdout
    assert "da init" in result.stdout


def test_mandatory_init_blocks_cleanup_when_not_initialized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Running 'da cleanup' without prior initialization must fail with exit code 1."""
    uninit_config = tmp_path / "uninit_config.json"
    save_config(
        AppConfig(language="en", input_dir=".input", output_dir=".output", initialized_at=None),
        uninit_config,
    )
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", uninit_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", uninit_config)

    result = runner.invoke(app, ["cleanup", "-f"])
    assert result.exit_code == 1
    assert "Initialization Required" in result.stdout or "Error:" in result.stdout
    assert "da init" in result.stdout


def test_help_allowed_when_not_initialized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Help commands ('da help' and 'da' with no args) must work even when uninitialized."""
    nonexistent_config = tmp_path / "does_not_exist.json"
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", nonexistent_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", nonexistent_config)

    res_help = runner.invoke(app, ["help"])
    assert res_help.exit_code == 0
    assert "AVAILABLE COMMANDS" in res_help.stdout

    res_no_args = runner.invoke(app, [])
    assert res_no_args.exit_code == 0
    assert "AVAILABLE COMMANDS" in res_no_args.stdout


def test_markdown_summary_report_includes_version(
    sample_input_hierarchy: Path,
    tmp_path: Path,
) -> None:
    """export_markdown_summary must include application version in report metadata and header."""
    from src.ingestion.loader import DatadisLoader

    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    summary = DataAggregator.aggregate_community(df)

    out_dir = tmp_path / "reports_test"
    report_file = export_markdown_summary(summary, output_dir=out_dir, lang="en")
    content = report_file.read_text(encoding="utf-8")

    current_ver = get_version()
    assert f"**Version:** {current_ver}" in content
    assert f"| DATADIS Analyzer Version | `{current_ver}` |" in content


def test_markdown_comparison_report_includes_version(
    sample_input_hierarchy: Path,
    tmp_path: Path,
) -> None:
    """export_comparison_markdown must include application version in report metadata and header."""
    from src.ingestion.loader import DatadisLoader

    loader = DatadisLoader()
    df, _ = loader.load_all(sample_input_hierarchy)
    comparison = DataAggregator.compare_years(df)

    out_dir = tmp_path / "reports_comp_test"
    report_file = export_comparison_markdown(comparison, output_dir=out_dir, lang="en")
    content = report_file.read_text(encoding="utf-8")

    current_ver = get_version()
    assert f"**Version:** {current_ver}" in content
    assert f"| DATADIS Analyzer Version | `{current_ver}` |" in content
