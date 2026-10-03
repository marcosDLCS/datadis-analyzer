"""Robust CSV format and schema validator for DATADIS exports."""

import csv
from pathlib import Path

from src.config import REQUIRED_COLUMNS, SUPPORTED_DELIMITERS, SUPPORTED_ENCODINGS
from src.ingestion.schema import ValidationResult


class DatadisValidator:
    """Validates DATADIS CSV files for schema conformance, encoding, and delimiters."""

    @classmethod
    def detect_encoding(cls, file_path: Path) -> str:
        """Detect the appropriate character encoding for a given file.

        Tries modern UTF-8 variants before falling back to Latin-1 / ISO encodings.
        """
        for encoding in SUPPORTED_ENCODINGS:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    # Read a representative chunk to ensure encoding validity
                    f.read(8192)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        return "latin-1"

    @classmethod
    def detect_delimiter(cls, file_path: Path, encoding: str) -> str:
        """Detect the CSV delimiter used in the export file.

        Standard DATADIS exports use semicolon (';'). Falls back to Sniffer or comma.
        """
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                sample_lines = [f.readline() for _ in range(5)]
                sample = "".join(sample_lines)

            if not sample:
                return ";"

            # Priority check for common DATADIS semicolon format
            first_line = sample_lines[0]
            counts = {delim: first_line.count(delim) for delim in SUPPORTED_DELIMITERS}
            best_delim = max(counts, key=counts.get)
            if counts[best_delim] > 0:
                return best_delim

            # Fallback to csv.Sniffer
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=";,\t")
            return dialect.delimiter
        except Exception:
            return ";"

    @classmethod
    def validate_file(cls, file_path: Path) -> ValidationResult:
        """Inspect and validate a DATADIS export CSV file against required specifications.

        Checks:
        1. File existence and non-zero size.
        2. Delimiter and encoding detection.
        3. Presence of mandatory DATADIS columns (cups, fecha, hora, consumo_kWh).
        4. Presence of at least one data row.
        """
        if not file_path.exists() or not file_path.is_file():
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                error_message=f"File not found: {file_path}",
            )

        if file_path.stat().st_size == 0:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                error_message="File is empty (0 bytes).",
            )

        encoding = cls.detect_encoding(file_path)
        delimiter = cls.detect_delimiter(file_path, encoding)

        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)
                try:
                    raw_headers = next(reader)
                except StopIteration:
                    return ValidationResult(
                        file_path=file_path,
                        is_valid=False,
                        encoding=encoding,
                        delimiter=delimiter,
                        error_message="File has no headers.",
                    )

                cleaned_headers = [h.strip().strip('"').strip("'") for h in raw_headers]
                normalized_headers = {h.lower(): h for h in cleaned_headers}

                missing = []
                for required in REQUIRED_COLUMNS:
                    if required.lower() not in normalized_headers:
                        missing.append(required)

                if missing:
                    return ValidationResult(
                        file_path=file_path,
                        is_valid=False,
                        delimiter=delimiter,
                        encoding=encoding,
                        detected_columns=cleaned_headers,
                        missing_columns=missing,
                        error_message=f"Missing required columns: {', '.join(missing)}",
                    )

                # Count rows to verify dataset presence
                row_count = sum(1 for _ in reader)
                if row_count == 0:
                    return ValidationResult(
                        file_path=file_path,
                        is_valid=False,
                        delimiter=delimiter,
                        encoding=encoding,
                        detected_columns=cleaned_headers,
                        total_rows=0,
                        error_message="File contains header but has zero data rows.",
                    )

                return ValidationResult(
                    file_path=file_path,
                    is_valid=True,
                    delimiter=delimiter,
                    encoding=encoding,
                    detected_columns=cleaned_headers,
                    total_rows=row_count,
                )

        except Exception as exc:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                delimiter=delimiter,
                encoding=encoding,
                error_message=f"Error reading file: {exc}",
            )
