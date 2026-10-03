"""Tests for DATADIS data loader, file discovery, and normalization."""

from pathlib import Path

import pytest

from src.config import (
    COL_CONSUMPTION_KWH,
    COL_CUPS,
    COL_DATE,
    COL_MONTH,
    COL_TIME,
    COL_YEAR,
)
from src.ingestion.loader import DatadisLoader
from src.ingestion.schema import DatadisError


def test_loader_discover_files_in_hierarchy(sample_input_hierarchy: Path) -> None:
    """Loader should recursively discover CSV files within annualized folders."""
    loader = DatadisLoader()
    files = loader.discover_files(sample_input_hierarchy)
    assert len(files) == 4
    # All files end in .csv
    assert all(f.suffix == ".csv" for f in files)


def test_loader_discover_files_filtered_by_year(sample_input_hierarchy: Path) -> None:
    """Loader should find only files in the 2024 subfolder when filtered."""
    loader = DatadisLoader()
    files = loader.discover_files(sample_input_hierarchy, year=2024)
    assert len(files) == 2
    assert all("2024" in str(f) for f in files)


def test_loader_load_file_normalizes_data(sample_valid_csv: Path) -> None:
    """Loader should parse European comma decimals, dates, and clean string columns."""
    loader = DatadisLoader()
    df = loader.load_file(sample_valid_csv)

    assert len(df) == 3
    assert COL_CUPS in df.columns
    assert COL_DATE in df.columns
    assert COL_YEAR in df.columns
    assert COL_MONTH in df.columns
    assert COL_TIME in df.columns
    assert COL_CONSUMPTION_KWH in df.columns

    # Verify decimal normalization: "1,500" -> 1.5, "2,500" -> 2.5
    assert df[COL_CONSUMPTION_KWH].iloc[0] == 1.5
    assert df[COL_CONSUMPTION_KWH].iloc[1] == 2.5
    assert df[COL_YEAR].iloc[0] == 2025
    assert df[COL_MONTH].iloc[0] == 1
    assert df[COL_MONTH].iloc[2] == 2


def test_loader_load_all_combines_and_aggregates(sample_input_hierarchy: Path) -> None:
    """Loader should aggregate multiple files across years into a unified DataFrame."""
    loader = DatadisLoader()
    combined_df, val_results = loader.load_all(sample_input_hierarchy)

    assert len(val_results) == 4
    assert all(v.is_valid for v in val_results)
    # Total rows: 2 rows in 2024_1 + 2 in 2024_2 + 1 in 2025_1 + 1 in 2025_2 = 6 rows
    assert len(combined_df) == 6
    assert set(combined_df[COL_YEAR].unique()) == {2024, 2025}


def test_loader_raises_on_empty_directory(tmp_path: Path) -> None:
    """Loader should raise DatadisError when directory has no CSVs."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    loader = DatadisLoader()
    with pytest.raises(DatadisError, match="No DATADIS CSV files found"):
        loader.load_all(empty_dir)


def test_real_dataset_loader() -> None:
    """If real .input directory exists, verify all files load cleanly."""
    real_input = Path(".input")
    if not real_input.exists():
        pytest.skip("Local .input directory not present")

    loader = DatadisLoader()
    combined_df, val_results = loader.load_all(real_input)
    assert len(val_results) == 18
    assert all(v.is_valid for v in val_results)
    assert len(combined_df) > 100_000
    assert len(combined_df[COL_CUPS].unique()) == 9
