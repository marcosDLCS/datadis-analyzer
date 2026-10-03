"""Data loader for DATADIS export files, handling directory traversal and DataFrame normalization."""

import logging
from pathlib import Path

import pandas as pd

from src.config import (
    COL_CONSUMPTION_KWH,
    COL_CUPS,
    COL_DATE,
    COL_MONTH,
    COL_TIME,
    COL_YEAR,
    DEFAULT_INPUT_DIR,
)
from src.ingestion.schema import (
    DatadisError,
    DatadisParseError,
    DatadisValidationError,
    ValidationResult,
)
from src.ingestion.validator import DatadisValidator

logger = logging.getLogger(__name__)


class DatadisLoader:
    """Traverses, validates, and loads DATADIS energy consumption CSV exports into pandas DataFrames."""

    def __init__(self, validator: DatadisValidator | None = None) -> None:
        self.validator = validator or DatadisValidator()

    def discover_files(
        self, base_dir: Path = DEFAULT_INPUT_DIR, year: int | None = None
    ) -> list[Path]:
        """Discover DATADIS CSV files located in annualized directories under base_dir.

        Args:
            base_dir: Root directory containing annualized folders (e.g., .input/).
            year: Optional year filter (e.g. 2025). When specified, prioritizes matching subdirectories.

        Returns:
            Sorted list of Path objects pointing to detected CSV files.
        """
        if not base_dir.exists():
            raise DatadisError(f"Input directory does not exist: {base_dir.resolve()}")

        csv_files: list[Path] = []
        if year is not None:
            # Check explicit year folder first
            year_dir = base_dir / str(year)
            if year_dir.exists() and year_dir.is_dir():
                csv_files.extend(year_dir.glob("*.csv"))

        if not csv_files:
            # Scan recursively under base directory
            csv_files = [
                p
                for p in base_dir.rglob("*.csv")
                if not p.name.startswith(".")
                and not any(part.startswith(".") and part != base_dir.name for part in p.parts)
            ]

        # Filter out hidden or backup files
        valid_files = [p for p in csv_files if p.is_file() and not p.name.startswith(".")]
        return sorted(valid_files)

    def load_file(self, file_path: Path) -> pd.DataFrame:
        """Parse a single DATADIS CSV file into a normalized pandas DataFrame.

        Args:
            file_path: Path to the DATADIS CSV file.

        Returns:
            Normalized pandas DataFrame with standardized column types and names.

        Raises:
            DatadisValidationError: If file fails schema validation.
            DatadisParseError: If file content cannot be parsed.
        """
        validation = self.validator.validate_file(file_path)
        if not validation.is_valid:
            raise DatadisValidationError(
                f"Validation failed for {file_path.name}: {validation.error_message}"
            )

        try:
            # Read CSV using detected delimiter and encoding
            df = pd.read_csv(
                file_path,
                sep=validation.delimiter,
                encoding=validation.encoding,
                quotechar='"',
                dtype=str,  # Read all as string initially to safely clean decimals and whitespace
                skipinitialspace=True,
            )

            # Standardize header names (case-insensitive mapping)
            col_map: dict[str, str] = {}
            for col in df.columns:
                cleaned = col.strip().strip('"').strip("'")
                lower = cleaned.lower()
                if lower == "cups":
                    col_map[col] = COL_CUPS
                elif lower == "fecha":
                    col_map[col] = COL_DATE
                elif lower == "hora":
                    col_map[col] = COL_TIME
                elif lower in ("consumo_kwh", "consumokwh"):
                    col_map[col] = COL_CONSUMPTION_KWH

            df = df.rename(columns=col_map)

            # Strip whitespace and quotes from string columns
            df[COL_CUPS] = df[COL_CUPS].astype(str).str.strip().str.strip('"').str.strip("'")
            df[COL_TIME] = df[COL_TIME].astype(str).str.strip().str.strip('"').str.strip("'")

            # Parse consumption values handling European comma decimals (e.g., '0,152')
            consumption_raw = (
                df[COL_CONSUMPTION_KWH]
                .astype(str)
                .str.strip()
                .str.strip('"')
                .str.replace(",", ".", regex=False)
            )
            df[COL_CONSUMPTION_KWH] = pd.to_numeric(consumption_raw, errors="coerce").fillna(0.0)

            # Parse date strings (supports YYYY/MM/DD, YYYY-MM-DD, DD/MM/YYYY, etc.)
            date_raw = df[COL_DATE].astype(str).str.strip().str.strip('"')
            parsed_dates = pd.to_datetime(date_raw, format="mixed", errors="coerce")

            if parsed_dates.isna().all():
                raise DatadisParseError(
                    f"Could not parse any valid dates from 'fecha' in {file_path.name}"
                )

            df[COL_DATE] = parsed_dates
            df[COL_YEAR] = df[COL_DATE].dt.year.astype(int)
            df[COL_MONTH] = df[COL_DATE].dt.month.astype(int)

            # Keep essential columns
            keep_cols = [COL_CUPS, COL_DATE, COL_YEAR, COL_MONTH, COL_TIME, COL_CONSUMPTION_KWH]
            return df[keep_cols]

        except Exception as exc:
            if isinstance(exc, DatadisValidationError | DatadisParseError):
                raise
            raise DatadisParseError(f"Failed to parse {file_path.name}: {exc}") from exc

    def load_all(
        self, base_dir: Path = DEFAULT_INPUT_DIR, year: int | None = None
    ) -> tuple[pd.DataFrame, list[ValidationResult]]:
        """Load and aggregate all DATADIS CSV files found in the directory tree.

        Args:
            base_dir: Root directory containing annualized input files.
            year: Optional year to filter by.

        Returns:
            Tuple of:
              - Combined pandas DataFrame containing all normalized rows.
              - List of ValidationResult objects for all discovered files.

        Raises:
            DatadisError: If no CSV files are found or no files could be parsed.
        """
        discovered = self.discover_files(base_dir=base_dir, year=year)
        if not discovered:
            filter_msg = f" for year {year}" if year else ""
            raise DatadisError(
                f"No DATADIS CSV files found under '{base_dir.resolve()}'{filter_msg}. "
                "Ensure files exist in ./.input/<year>/ directory."
            )

        dataframes: list[pd.DataFrame] = []
        validation_results: list[ValidationResult] = []

        for file_path in discovered:
            val_res = self.validator.validate_file(file_path)
            validation_results.append(val_res)

            if val_res.is_valid:
                try:
                    df = self.load_file(file_path)
                    dataframes.append(df)
                except Exception as exc:
                    logger.warning("Error loading %s: %s", file_path.name, exc)
                    val_res.is_valid = False
                    val_res.error_message = str(exc)

        if not dataframes:
            raise DatadisError(
                f"Found {len(discovered)} file(s), but none could be successfully loaded. "
                "Check validation results for details."
            )

        combined_df = pd.concat(dataframes, ignore_index=True)

        # Apply year filter if supplied
        if year is not None:
            combined_df = combined_df[combined_df[COL_YEAR] == year]

        return combined_df, validation_results
