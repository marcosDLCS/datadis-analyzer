"""Global configuration, schema constants, and persistent application settings for DATADIS Analyzer."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, Optional

# Default paths
DEFAULT_INPUT_DIR: Final[Path] = Path(".input")
DEFAULT_OUTPUT_DIR: Final[Path] = Path(".output")
CONFIG_FILE_PATH: Final[Path] = Path(".da_config.json")

# Required DATADIS CSV columns (case-insensitive)
REQUIRED_COLUMNS: Final[list[str]] = [
    "cups",
    "fecha",
    "hora",
    "consumo_kWh",
]

# Optional DATADIS CSV columns
OPTIONAL_COLUMNS: Final[list[str]] = [
    "metodoObtencion",
    "energiaVertida_kWh",
    "energiaGenerada_kWh",
    "energiaAutoconsumida_kWh",
]

# Standard normalized column names used internally
COL_CUPS: Final[str] = "cups"
COL_DATE: Final[str] = "date"
COL_TIME: Final[str] = "time"
COL_CONSUMPTION_KWH: Final[str] = "consumption_kwh"
COL_YEAR: Final[str] = "year"
COL_MONTH: Final[str] = "month"

# Delimiters and encodings commonly encountered in DATADIS exports
SUPPORTED_DELIMITERS: Final[list[str]] = [";", ",", "\t"]
SUPPORTED_ENCODINGS: Final[list[str]] = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

# Supported date string patterns
DATE_FORMATS: Final[list[str]] = [
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
]

# Supported application languages
SUPPORTED_LANGUAGES: Final[dict[str, str]] = {
    "en": "English",
    "english": "English",
    "es": "Español",
    "spanish": "Español",
    "español": "Español",
    "espanol": "Español",
}


@dataclass
class AppConfig:
    """Persistent user and application settings.

    Attributes:
        language: Active output language ('en' for English, 'es' for Spanish).
        input_dir: Default input folder path.
        output_dir: Default output folder path for markdown reports.
    """

    language: str = "en"
    input_dir: str = ".input"
    output_dir: str = ".output"


def normalize_language_code(lang_raw: str) -> str:
    """Normalize input language string to standard two-letter ISO code ('en' or 'es').

    Raises:
        ValueError: If the language is not supported.
    """
    clean = lang_raw.strip().lower()
    if clean in ("en", "english"):
        return "en"
    if clean in ("es", "spanish", "español", "espanol"):
        return "es"
    raise ValueError(f"Unsupported language '{lang_raw}'. Supported options: 'en' (English), 'es' (Spanish).")


def load_config(path: Optional[Path] = None) -> AppConfig:
    """Load configuration from disk, returning default settings if the file does not exist."""
    target_path = path or CONFIG_FILE_PATH
    if not target_path.exists():
        return AppConfig()

    try:
        data = json.loads(target_path.read_text(encoding="utf-8"))
        lang = data.get("language", "en")
        try:
            normalized_lang = normalize_language_code(lang)
        except ValueError:
            normalized_lang = "en"

        return AppConfig(
            language=normalized_lang,
            input_dir=data.get("input_dir", ".input"),
            output_dir=data.get("output_dir", ".output"),
        )
    except Exception:
        return AppConfig()


def save_config(config: AppConfig, path: Optional[Path] = None) -> None:
    """Persist application configuration to disk as JSON."""
    target_path = path or CONFIG_FILE_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")


def set_language(language: str, path: Optional[Path] = None) -> str:
    """Update and persist the active language setting.

    Returns:
        The normalized two-letter language code ('en' or 'es').
    """
    code = normalize_language_code(language)
    cfg = load_config(path)
    cfg.language = code
    save_config(cfg, path)
    return code


def get_language(path: Optional[Path] = None) -> str:
    """Retrieve the currently configured language code ('en' or 'es')."""
    return load_config(path).language
