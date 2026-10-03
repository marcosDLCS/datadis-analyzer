"""Tests for DATADIS format and schema validator."""

from pathlib import Path

from src.ingestion.validator import DatadisValidator


def test_validator_detects_semicolon(sample_valid_csv: Path) -> None:
    """Validator should correctly identify semicolon as delimiter."""
    result = DatadisValidator.validate_file(sample_valid_csv)
    assert result.is_valid is True
    assert result.delimiter == ";"
    assert result.encoding == "utf-8"
    assert result.total_rows == 3
    assert result.error_message is None


def test_validator_detects_comma_delimiter(tmp_path: Path) -> None:
    """Validator should correctly identify comma delimiter when present."""
    csv_file = tmp_path / "comma.csv"
    csv_file.write_text(
        'cups,fecha,hora,consumo_kWh\n"ES0021000000000001AA","2025/01/01","01:00","1.5"\n',
        encoding="utf-8",
    )
    result = DatadisValidator.validate_file(csv_file)
    assert result.is_valid is True
    assert result.delimiter == ","
    assert result.total_rows == 1


def test_validator_fails_on_missing_columns(tmp_path: Path) -> None:
    """Validator should reject files missing required headers like consumo_kWh."""
    csv_file = tmp_path / "invalid_header.csv"
    csv_file.write_text(
        'cups;fecha;hora\n"ES0021000000000001AA";"2025/01/01";"01:00"\n',
        encoding="utf-8",
    )
    result = DatadisValidator.validate_file(csv_file)
    assert result.is_valid is False
    assert "consumo_kWh" in result.missing_columns
    assert "Missing required columns" in (result.error_message or "")


def test_validator_fails_on_empty_file(tmp_path: Path) -> None:
    """Validator should reject empty files."""
    csv_file = tmp_path / "empty.csv"
    csv_file.touch()
    result = DatadisValidator.validate_file(csv_file)
    assert result.is_valid is False
    assert "empty" in (result.error_message or "").lower()


def test_validator_fails_on_nonexistent_file(tmp_path: Path) -> None:
    """Validator should gracefully report missing file."""
    csv_file = tmp_path / "does_not_exist.csv"
    result = DatadisValidator.validate_file(csv_file)
    assert result.is_valid is False
    assert "not found" in (result.error_message or "").lower()


def test_validator_handles_latin1_encoding(tmp_path: Path) -> None:
    """Validator should detect and read ISO-8859-1 / Latin-1 encoded CSVs."""
    csv_file = tmp_path / "latin1.csv"
    content = (
        "cups;fecha;hora;consumo_kWh;metodoObtención\n"
        '"ES0021000000000001AA";"2025/01/01";"01:00";"1,500";"Real"\n'
    )
    csv_file.write_bytes(content.encode("latin-1"))
    result = DatadisValidator.validate_file(csv_file)
    assert result.is_valid is True
    assert result.total_rows == 1
