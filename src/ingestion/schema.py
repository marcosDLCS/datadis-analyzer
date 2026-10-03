"""Schema definitions, validation result containers, and custom exceptions for DATADIS ingestion."""

from dataclasses import dataclass, field
from pathlib import Path


class DatadisError(Exception):
    """Base exception for DATADIS analyzer errors."""


class DatadisValidationError(DatadisError):
    """Raised when a DATADIS export file fails format or schema validation."""


class DatadisParseError(DatadisError):
    """Raised when data values cannot be parsed or transformed."""


@dataclass
class ValidationResult:
    """Detailed result of validating a DATADIS CSV export file.

    Attributes:
        file_path: Path to the validated CSV file.
        is_valid: True if file satisfies schema requirements; False otherwise.
        delimiter: Detected column delimiter (e.g. ';' or ',').
        encoding: Detected character encoding (e.g. 'utf-8' or 'latin-1').
        detected_columns: List of headers found in the CSV.
        missing_columns: List of mandatory headers that were absent.
        total_rows: Number of raw data rows discovered.
        error_message: Explanatory error details if validation failed.
    """

    file_path: Path
    is_valid: bool
    delimiter: str = ";"
    encoding: str = "utf-8"
    detected_columns: list[str] = field(default_factory=list)
    missing_columns: list[str] = field(default_factory=list)
    total_rows: int = 0
    error_message: str | None = None
