# DATADIS Analyzer (`da`)

A modular, high-performance Python CLI tool to analyze hourly electrical energy consumption data exported from Spain's [DATADIS](https://datadis.es) platform for residential building communities (*comunidades de vecinos*).

---

## Key Features

- **Automatic Format Detection:** Auto-detects delimiters (`;`, `,`, `\t`), European comma decimal notations (`0,152`), text encodings (`utf-8`, `utf-8-sig`, `latin-1`), and flexible date patterns (`YYYY/MM/DD`, `YYYY-MM-DD`).
- **Community-Level Share Computation:** Aggregates consumption across all CUPS meters in annualized input folders (`./.input/<year>/`), calculating exact percentage shares of collective consumption by month and year.
- **Rich Terminal Presentation:** Colorized overview dashboards, styled data tables, visual inline percentage distribution bars (`████████░░`), and analytical community insights.
- **Flexible Analysis Views:** Supports full community overview (`--view all`), annual totals (`--view annual`), monthly breakdowns (`--view monthly`), year filtering (`--year <YYYY>`), and individual CUPS trajectories (`--cups <CUPS>`).
- **Strict Architecture Standards:** Written in modern Python (3.11+), PEP 8 compliant, strictly type-annotated (`typing`), with comprehensive automated tests (`pytest`).

---

## Project Structure

```text
datadis-analyzer/
├── pyproject.toml              # Build metadata, dependencies, and CLI script entrypoint (`da`)
├── requirements.txt            # Core and test dependency manifest
├── README.md                   # Project documentation
├── .input/                     # Annualized DATADIS CSV export directories
│   ├── 2025/
│   └── 2026/
├── .output/                    # Directory for exports and reports
├── src/
│   ├── __init__.py             # Package marker and version
│   ├── cli.py                  # Typer CLI application, subcommands, and options
│   ├── config.py               # Constants, column definitions, and supported dialects
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── schema.py           # Dataclass models for validation results and exceptions
│   │   ├── validator.py        # Delimiter/encoding detection and schema validator
│   │   └── loader.py           # Directory scanner and pandas DataFrame normalizer
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── models.py           # Typed domain summary containers (CupsShare, CommunitySummary)
│   │   └── aggregator.py       # Aggregation engine, monthly/annual grouping, and share math
│   └── presentation/
│       ├── __init__.py
│       ├── console.py          # Rich console instance, palettes, and visual bar generators
│       └── views.py            # Formatted tables, cards, help screens, and observations
└── tests/
    ├── __init__.py
    ├── conftest.py             # Reusable mock datasets and temporary directory fixtures
    ├── test_validator.py       # Encoding, delimiter, and schema validation tests
    ├── test_loader.py          # Discovery, normalization, and DataFrame parsing tests
    ├── test_aggregator.py      # Period grouping, share calculations (100% sum), and pivots
    └── test_cli.py             # CLI runner integration tests for all commands and options
```

---

## Installation & Local Setup

### 1. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install in Editable Mode

Install the dependencies and register the `da` binary entry point in your environment:

```bash
pip install -e .
```

To include test dependencies:

```bash
pip install -e ".[dev]"
```

Verify the installation:

```bash
da --help
```

---

## Data Input Layout

Place DATADIS CSV export files inside annualized subdirectories under `./.input/`:

```text
.input/
  ├── 2025/
  │   ├── ES0021000000000001AA_Consumo_01-01-2025_31-12-2025.csv
  │   ├── ES0021000000000002BB_Consumo_01-01-2025_31-12-2025.csv
  │   └── ...
  └── 2026/
      ├── ES0021000000000001AA_Consumo_01-01-2026_30-09-2026.csv
      └── ...
```

Required DATADIS CSV columns (semicolon or comma delimited):
- `cups`: Universal Supply Point Code (e.g., `ES0021000000000001AA`)
- `fecha`: Date (`YYYY/MM/DD` or `YYYY-MM-DD`)
- `hora`: Time interval (`01:00` to `24:00`)
- `consumo_kWh`: Consumption value (e.g., `0,152` or `0.152`)

---

## Usage Guide

### 1. Initialize Configuration (`da init`)

Select and persist the output language between **English** (default) and **Spanish**:

```bash
# Interactive selection:
da init

# Or via flag:
da init --language es
da init -l en
```

The selected preference is saved to `.da_config.json` and automatically remembered across all future commands.

### 2. Help Command (`da help`)

Display the interactive CLI reference, available options, and input conventions:

```bash
da help
# or in Spanish if configured:
da help --lang es
```

*(You can also use `da --help` or simply run `da` with no arguments)*.

### 3. Community Summary (`da summary`)

Analyze all annualized data in `./.input/` and display annual summaries, the monthly timeline, detailed month-by-month tables showing the distribution of all CUPS with percentage shares and bars, and community insights.

**Automatic Report Generation:** Every run automatically exports a complete, localized Markdown report into `./.output/` with a concise name starting with a timestamp down to seconds:
`./.output/YYYYMMDD_HHMMSS_community_summary.md`

```bash
da summary
```

#### Filter by Year:
```bash
da summary --year 2025
# or
da summary -y 2026
```

#### Detailed Month-by-Month Breakdown:
```bash
da summary --view monthly
da summary --year 2025 --view monthly
```

#### Focus on a Specific CUPS Meter:
Inspect the full monthly trajectory and community share evolution for an individual supply point:

```bash
da summary --cups ES0021000000000001AA
```

#### Custom Input Directory:
```bash
da summary --input-dir /path/to/custom_input
```

---

## Running Automated Tests

Run the complete test suite with `pytest`:

```bash
pytest -v
```
