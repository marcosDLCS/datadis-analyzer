# AGENTS.md — Development & Agent Guidelines

Guidelines and repository context for AI agents and human contributors working on `datadis-analyzer`.

---

## 1. Project Mission & Overview

`datadis-analyzer` is a modular, high-performance Python CLI tool (`da`) designed to analyze hourly electrical energy consumption data exported from Spain's [DATADIS](https://datadis.es) platform for residential building communities (*comunidades de vecinos*).

### Core Capabilities
- Ingest and validate DATADIS CSV export files organized by year in `./.input/<year>/`.
- Auto-detect delimiters (`;`, `,`), character encodings (`utf-8`, `latin-1`), and decimal notations (`0,152` vs `0.152`).
- Aggregate community energy consumption across all individual CUPS (*Código Unificado de Punto de Suministro*).
- Calculate each CUPS's percentage share of the total community consumption for each year and month.
- Render high-impact terminal visualizations (tables, metric cards, inline percentage bars, and analytical observations) using `rich`.
- Persist user configuration (output language between English and Spanish) and initialize workspace directories (.input, .output) via `da init`.
- Automatically export every generated community summary to `.output/` as a timestamped Markdown report (`YYYYMMDD_HHMMSS_*.md`).

---

## 2. Architecture & Codebase Layout

The project enforces a strict separation of concerns:

```text
datadis-analyzer/
├── pyproject.toml              # Build config & CLI entry point (da = "src.cli:main")
├── requirements.txt            # Core and test dependency manifest
├── README.md                   # User guide and project overview
├── AGENTS.md                   # Agent and developer instructions
├── CONTRIBUTING.md             # Contribution guidelines & Conventional Commits specification
├── .da_config.json             # Persistent application configuration (language, paths)
├── .input/                     # Annualized raw CSV files (.input/<year>/*.csv)
├── .output/                    # Target directory for generated reports/exports
├── src/
│   ├── __init__.py             # Package marker and version (__version__ = "0.1.0")
│   ├── cli.py                  # Typer CLI application, subcommands (init, summary, help), and flags
│   ├── config.py               # Constants, column definitions, AppConfig, and persistence helpers
│   ├── i18n.py                 # Multi-language translation engine (English & Spanish)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── schema.py           # Dataclasses (ValidationResult) and custom exceptions
│   │   ├── validator.py        # Delimiter/encoding detector and schema validator
│   │   └── loader.py           # File discovery and pandas DataFrame normalizer
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── models.py           # Domain models: CupsShare, PeriodSummary, CommunitySummary
│   │   └── aggregator.py       # Aggregation engine, monthly/annual grouping, and share math
│   └── presentation/
│       ├── __init__.py
│       ├── console.py          # Rich console instance, themes, and visual bar formatters
│       ├── views.py            # Formatted tables, overview panels, help view, and insight cards
│       └── export.py           # Markdown report exporter into .output/
└── tests/
    ├── __init__.py
    ├── conftest.py             # Reusable mock datasets and temporary directory fixtures
    ├── test_validator.py       # Format and schema validation tests
    ├── test_loader.py          # Ingestion, normalization, and DataFrame parsing tests
    ├── test_aggregator.py      # Period grouping, share calculations (100% sum), and pivots
    ├── test_cli.py             # Typer CliRunner integration tests for commands and options
    └── test_config_and_export.py # Config persistence, language switching, and markdown export tests
```

---

## 3. Technology Stack & Standards

- **Runtime:** Python 3.11+
- **CLI Framework:** [Typer](https://typer.tiangolo.com/) (modern, type-annotated, Click-compatible)
- **Terminal UI & Tables:** [Rich](https://rich.readthedocs.io/)
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
- **Test Runner:** [Pytest](https://docs.pytest.org/)

---

## 4. Development Workflows & Commands

### Virtual Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### Running the CLI
```bash
# Initialize workspace directories (.input, .output) and persist language preference (English default, Spanish option)
da init
da init --language es
da init -l en

# Display help and reference manual
da help
da --help

# Default community summary (annual + monthly overview + export to .output/)
da summary

# Filter by year
da summary --year 2025

# Show detailed month-by-month CUPS breakdown
da summary --view monthly

# Inspect single CUPS trajectory
da summary --cups ES0021000000000001AA

# Custom input directory
da summary --input-dir /path/to/input
```

### Running Tests
```bash
# Run all tests
pytest -v

# Run with test coverage or short output
pytest -q
```

---

## 5. Domain Rules & Data Ingestion Assumptions

1. **Annualized Folder Layout:** Input CSV files reside in `./.input/<year>/` (e.g., `./.input/2025/`, `./.input/2026/`).
2. **Community Scope:** All CUPS across these files are assumed to belong to the same residential building community (*comunidad de vecinos*).
3. **DATADIS CSV Format:**
   - Standard columns: `cups`, `fecha`, `hora`, `consumo_kWh` (optional: `metodoObtencion`, `energiaVertida_kWh`, `energiaGenerada_kWh`, `energiaAutoconsumida_kWh`).
   - Delimiter is typically `;` (Spanish Excel standard) or `,`.
   - Decimal separator is typically `,` (e.g., `"0,152"`) or `.`.
   - Hours range from `01:00` to `24:00` (24 hourly intervals per day).
4. **Calculations & Share Invariant:**
   - Percentage share for CUPS $i$ in a given period $T$:
     $$\text{Share}_i = \frac{\sum_{t \in T} \text{kWh}_{i, t}}{\sum_{j} \sum_{t \in T} \text{kWh}_{j, t}} \times 100$$
   - The sum of shares across all community CUPS for any period must equal $100.00\%$.
5. **Special CUPS Classification:**
   - Dominant consumer (>30%–80% of total): typically community HVAC/pumps/collective services (marked with `★`).
   - Inactive / vacant supply points (<1 kWh): marked with `(0)`.

---

## 6. Coding Guidelines for Agents

- **Language:** Write all code, comments, docstrings, test names, CLI messages, and commit messages entirely in **English**.
- **Typing:** Use strict type hints (`typing`) on all function signatures, dataclasses, and class methods.
- **Error Handling:** Use custom domain exceptions from `src.ingestion.schema` (`DatadisError`, `DatadisValidationError`, `DatadisParseError`). Handle missing files, wrong headers, and corrupted rows gracefully without crashing.
- **Terminal Aesthetics:** Keep Rich tables compact and responsive. Ensure all tables fit comfortably within standard **80-column terminals** without unwanted line-wrapping or column truncation (`no_wrap=True` for identifiers, numbers, and percentages).
- **Testing:** Any new ingestion format, calculation logic, or CLI flag must include corresponding automated unit/integration tests in `tests/`. Always run `pytest` before finalizing changes.
- **Git & Commits:** Adhere strictly to the Conventional Commits specification documented in [CONTRIBUTING.md](CONTRIBUTING.md). Never include sensitive or real CUPS data in commits.

---

## 7. Related Documentation

- [README.md](README.md) — User setup, command reference, and visual overview.
- [CONTRIBUTING.md](CONTRIBUTING.md) — Open-source contribution guidelines, coding standards, and PR workflows.
