# 🤖 AGENTS.md — Development & Agent Guidelines

> Technical directives, architectural specifications, and domain invariants for autonomous AI agents and developers.

[![Agents: Directives Active](https://img.shields.io/badge/Agents-Directives%20Active-blue.svg?style=flat&logo=robot&logoColor=white)](AGENTS.md)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg?style=flat&logo=ruff&logoColor=white)](https://astral.sh/ruff)
[![Pre-commit](https://img.shields.io/badge/Pre--commit-Enforced-brightgreen.svg?style=flat&logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat&logo=git)](CONTRIBUTING.md)

---

## 1. 🎯 Project Mission & Core Capabilities

`datadis-analyzer` (`da`) is a modular CLI tool for analyzing hourly electricity consumption exported from Spain's [DATADIS](https://datadis.es) platform for residential communities (*comunidades de vecinos*).

### ⚡ Core Capabilities
- **📥 Robust Ingestion:** Ingest and validate DATADIS CSV files organized by year in `./.input/<year>/`. Auto-detect delimiters, encodings, and decimal formats.
- **🧮 Fair-Share Math:** Calculate exact percentage shares per CUPS for months and years (guaranteed 100.00% sum).
- **📊 Rich Terminal UI:** Render tables, metric cards, percentage bars, and consumption alerts (`★` dominant, `(0)` inactive).
- **⚙️ Configuration Persistence:** Maintain language preferences (`en`/`es`) and paths in `.da_config.json`.
- **📝 Automated Reporting:** Export timestamped Markdown summaries to `.output/YYYYMMDD_HHMMSS_*.md` with Matplotlib comparison charts.

---

## 2. 🧩 Architecture & Component Boundaries

The codebase follows a modular pipeline across distinct component boundaries:
- **`src/cli.py`:** Typer entry point and command dispatch (`init`, `summary`, `compare`, `cleanup`, `version`, `help`).
- **`src/config.py` & `src/i18n.py`:** Persistent settings (`.da_config.json`), paths, and English/Spanish localization.
- **`src/version.py`:** CalVer management engine (`YYYY.MM.NNN`) and pre-commit version validator.
- **`src/security.py`:** Zero-leakage privacy auditor, synthetic CUPS whitelist, and credential scanner.
- **`src/ingestion/`:** Delimiter/encoding detection (`validator.py`) and vectorized Pandas normalization (`loader.py`).
- **`src/processing/`:** Aggregation engine, calendar completeness logic (`aggregator.py`), and dataclasses (`models.py`).
- **`src/presentation/`:** Rich terminal UI (`views.py`), Matplotlib chart generator (`charts.py`), and Markdown exporter (`export.py`).

---

## 3. 🛠️ Technology Stack & Standards

| Component | Technology | Standard / Role |
| :--- | :--- | :--- |
| **Runtime** | Python 3.11+ | Modern typing, native union types (`X \| Y`) |
| **CLI & UI** | Typer & Rich | Command parser, 80-column tables, visual bars |
| **Data & Charts** | Pandas & Matplotlib | CSV normalization, time-series grouping, headless PNG charts |
| **Versioning** | CalVer (`YYYY.MM.NNN`) | Automated per-commit version increments |
| **Quality** | Ruff & Pre-commit | Linter, code formatter, git hook enforcement |
| **Testing** | Pytest | Unit and integration test coverage |

---

## 4. 🎮 Workflows & Terminal Commands

### Environment Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip && pip install -e ".[dev]"
pre-commit install
```

### Running the CLI
```bash
da init [-l en|es]        # Mandatory initialization before running analytics
da summary [--year YYYY]  # Community summary (annual/monthly overview + export)
da summary --view monthly # Full month-by-month CUPS breakdown
da summary --cups <CUPS>  # Inspect specific CUPS trajectory
da compare [-y YYYY ...]  # Multi-year consumption comparison, trends & export
da cleanup [-f]           # Clear generated reports from .output/
da help                   # Interactive manual
da version                # Display active application version
```

### Testing & Quality Checks
```bash
pytest -v                 # Run all automated tests
ruff check --fix .        # Lint and auto-fix code
ruff format .             # Format code
python -m src.version check # Validate version consistency
python -m src.version bump  # Bump version before committing
python -m src.security    # Audit repository for privacy & secret leaks
pre-commit run --all-files # Run all git hooks
```

---

## 5. 📐 Domain Invariants & Data Assumptions

1. **Annualized Folder Layout:** Input CSV files reside in `./.input/<year>/` (e.g., `./.input/2025/*.csv`).
2. **Community Scope:** All CUPS in the input directory belong to the same residential community (*comunidad de vecinos*).
3. **DATADIS CSV Format:** Required columns: `cups`, `fecha` (`YYYY/MM/DD` or `YYYY-MM-DD`), `hora` (`01:00`–`24:00`), `consumo_kWh`. Delimiters: `;` or `,`. Decimals: `,` or `.`.
4. **The 100.00% Share Invariant:**
   $$\text{Share}_i = \frac{\sum_{t \in T} \text{kWh}_{i, t}}{\sum_{j} \sum_{t \in T} \text{kWh}_{j, t}} \times 100$$
   The sum of shares across all community CUPS for any period must equal $100.00\%$.
5. **Special CUPS Classification:** Dominant consumer (`★`): >30% of total consumption (e.g., central HVAC/pumps). Inactive supply (`(0)`): <1 kWh total consumption.
6. **Mandatory Workspace Initialization:** `da init` must be successfully run before executing `da summary`, `da compare`, or `da cleanup`. The command records `initialized_at` and CalVer `version` in `.da_config.json`.
7. **CalVer Pattern Invariant:** The version string adheres strictly to `<year>.<month>.<incremental number (3 positions)>` (e.g., `2026.10.001`), displayed in banners, `da init`, and reports.

---

## 6. 🤖 Directives for Autonomous AI Agents

- **🛡️ Directive 1: Anonymization is Absolute.** Never commit or log real DATADIS CUPS, contract numbers, or real residential datasets. Use synthetic mock identifiers (`ES0021000000000001AA`, `ES0021000000000002BB`). Enforced by pre-commit hook and `python -m src.security`.
- **🌐 Directive 2: Universal English Codebase.** Write all code, comments, docstrings, test names, CLI messages, and commit messages entirely in **English**.
- **🎯 Directive 3: Strict Modern Typing.** Use strict type hints (`typing`, native union syntax `X | Y`) on all function signatures, dataclasses, and class methods. Avoid bare `Any`.
- **🚨 Directive 4: Domain Exceptions.** Use custom domain exceptions from `src.ingestion.schema` (`DatadisError`, `DatadisValidationError`, `DatadisParseError`). Handle errors gracefully without uncaught stack traces.
- **🖥️ Directive 5: The 80-Column Terminal Rule.** Rich tables must render cleanly on standard **80-column terminals**. Set `no_wrap=True` on numeric, percentage, and CUPS columns.
- **🧪 Directive 6: Test Completeness.** Any new calculation logic, CLI flag, or validation rule must include automated unit tests in `tests/`. Always run `pytest` before finalizing tasks.
- **🧹 Directive 7: Ruff & Pre-Commit Adherence.** Run `ruff check --fix .` and `ruff format .` before committing changes. Git pre-commit hooks will automatically reject non-compliant commits.
- **📝 Directive 8: Conventional Commits.** Adhere strictly to Conventional Commits format (`<type>(<scope>): <desc>`).
- **🏷️ Directive 9: CalVer Increments on Every Commit.** Every commit must increment the CalVer sequence (`python -m src.version bump`) so that each commit has a distinct version in `src/version.py` and `pyproject.toml`. Pre-commit hooks enforce version validity.

---

## 7. 📚 Related Documentation

- 📘 [Operational Guide (English)](docs/GUIDE_EN.md) — Technical architecture, ingestion pipeline, math invariants, and outputs.
- 🇪🇸 [Guía Operativa (Español)](docs/GUIDE_ES.md) — Arquitectura técnica, canal de ingesta, cálculo de reparto y salidas.
- 📖 [README.md](README.md) — User setup, command reference, and visual overview.
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines, coding standards, and PR workflows.
- 📄 [LICENSE](LICENSE) — Full MIT open-source license text.
