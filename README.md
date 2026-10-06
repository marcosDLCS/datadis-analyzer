# ⚡ DATADIS Analyzer (`da`)

> Energy analytics and fair-share allocation CLI for residential communities (*comunidades de vecinos*) in Spain.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2026.10.001-blue.svg)](pyproject.toml)
[![CLI Framework](https://img.shields.io/badge/CLI-Typer-009688?style=flat)](https://typer.tiangolo.com/)
[![Terminal UI](https://img.shields.io/badge/UI-Rich-E9573F?style=flat)](https://rich.readthedocs.io/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000?style=flat&logo=ruff&logoColor=white)](https://astral.sh/ruff)
[![Pre-commit](https://img.shields.io/badge/Pre--commit-Enabled-brightgreen?style=flat&logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](https://opensource.org/licenses/MIT)

---

## 🚀 Key Capabilities

- **🔍 Multi-Dialect CSV Ingestion:** Auto-detects delimiters (`;`, `,`, `\t`), decimal formats (`0,152` vs `0.152`), encodings (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`), and dates (`YYYY/MM/DD`, `YYYY-MM-DD`).
- **🧮 Exact Fair-Share Math:** Calculates each supply point's (CUPS) percentage share of collective community energy across months and years (guaranteed 100.00% sum).
- **📊 Rich Terminal Visualizations:** Displays interactive tables, metric cards, inline percentage bars (`████░░`), and alerts for dominant (`★`) or inactive (`(0)`) meters.
- **🏷️ Automated CalVer Versioning:** Increments release version on every commit (`YYYY.MM.NNN`), shown in banners, init cards, and reports.
- **🌐 Dual-Language Support:** English (`en`) and Spanish (`es`) localization, persisted in `.da_config.json`.
- **📝 Automated Reporting & Charts:** Exports timestamped Markdown reports to `.output/` with embedded high-resolution Matplotlib comparison charts.

---

## 🏗️ Architecture & Data Flow

Data flows unidirectionally across three core layers:
1. **Ingestion & Validation:** Discovers raw CSV files in `./.input/<year>/`, sniffs encodings and dialects via `DatadisValidator`, and normalizes schemas into Pandas DataFrames via `DatadisLoader`.
2. **Processing Core:** Groups time-series readings, evaluates calendar completeness for honest multi-year comparisons, and computes exact fair-share percentages via `DataAggregator`.
3. **Presentation & Export:** Renders 80-column Rich terminal views (`views.py`), generates Matplotlib comparison bar charts (`charts.py`), and exports timestamped Markdown summaries (`export.py`).

---

## 🖥️ Terminal Output Preview

```text
╭──────────────── ⚡ DATADIS RESIDENTIAL COMMUNITY ENERGY SUMMARY ────────────────╮
│  Supply Points (CUPS): 8         Date Range: 2025-01-01 ➔ 2025-12-31             │
│  Total Meter Readings: 70,080    Total Community Energy: 18,450.25 kWh           │
╰──────────────────────────────────────────────────────────────────────────────────╯

╭───────────── 📅 Annual Consumption & Shares: 2025 (Total: 9,250.00 kWh) ─────────────╮
│ Rank │ CUPS                   │  Consumption │   Share │ Distribution                │
│──────┼────────────────────────┼──────────────┼─────────┼─────────────────────────────│
│    1 │ ES0021000000000001AA ★ │ 4,625.00 kWh │  50.00% │ ██████░░░░░░                │
│    2 │ ES0021000000000002BB   │ 2,312.50 kWh │  25.00% │ ███░░░░░░░░░                │
│    3 │ ES0021000000000003CC   │ 1,850.00 kWh │  20.00% │ ██░░░░░░░░░░                │
│    4 │ ES0021000000000004DD   │   462.50 kWh │   5.00% │ █░░░░░░░░░░░                │
│    5 │ ES0021000000000005EE   │     0.00 kWh │   0.00% │ ░░░░░░░░░░░░                │
│──────┼────────────────────────┼──────────────┼─────────┼─────────────────────────────│
│      │ Total                  │ 9,250.00 kWh │ 100.00% │                             │
╰──────────────────────────────────────────────────────────────────────────────────────╯
Legend: ★ Dominant Consumer (>30% of total)  |  (0) Inactive supply (<1 kWh)
```

---

## 📦 Installation & Setup

```bash
# 1. Clone repository & create virtual environment
git clone git@github.com:marcosDLCS/datadis-analyzer.git && cd datadis-analyzer
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies with development tools and git hooks
pip install --upgrade pip && pip install -e ".[dev]"
pre-commit install

# 3. Initialize workspace directories (.input, .output) and default language
da init
```

---

## 📂 Input Data Conventions

Place DATADIS CSV files into annualized subdirectories: `./.input/<year>/<CUPS>_Consumo_*.csv`.

> [!IMPORTANT]
> **Data Privacy:** DATADIS exports contain private household data. Never commit real CUPS files to version control. The `./.input/` and `./.output/` directories are permanently git-ignored.

Required CSV columns (semicolon or comma delimited):
| Column | Description | Example |
| :--- | :--- | :--- |
| `cups` | Universal Supply Point Code | `"ES0021000000000001AA"` |
| `fecha` | Reading date (`DD/MM/YYYY` or `YYYY-MM-DD`) | `"2025/01/15"` |
| `hora` | Hour interval (`01:00` to `24:00`) | `"14:00"` |
| `consumo_kWh` | Interval energy consumption | `"0,152"` or `"0.152"` |

---

## 🎮 CLI Usage Manual

> [!IMPORTANT]
> **Mandatory First Step:** You must run `da init` before executing `da summary`, `da compare`, or `da cleanup`. Initialization records a timestamp in `.da_config.json` and prepares workspace folders.

### ⚙️ Workspace Initialization (`da init`) — *Mandatory*
```bash
da init                 # Interactive language selection and directory initialization
da init --language es   # Set language to Spanish (-l en for English)
```

### 🏷️ Version Display (`da version`)
```bash
da version              # Display active CalVer version (e.g., 2026.10.001)
```

### 📖 Help & Manual (`da help`)
```bash
da help                 # Interactive reference manual with command table
da help --lang es       # Display help in Spanish
```

### 📊 Community Summary (`da summary`)
```bash
da summary              # Annual & monthly community overview + markdown export
da summary --year 2025  # Filter to a specific year
da summary --view monthly # Full month-by-month CUPS breakdown table
da summary --cups ES0021000000000001AA # Dedicated CUPS trajectory view
da summary --input-dir /path/to/input   # Custom input directory
```

### 🔄 Multi-Year Comparison (`da compare`)
```bash
da compare              # Compare all years in ./.input/, generate charts & export report
da compare -y 2024 -y 2025  # Compare specific years (--years 2024,2025 also supported)
da compare --no-charts  # Skip PNG bar chart generation
da compare --lang es    # Render comparison in Spanish
```
- **Incomplete Month Handling:** Incomplete months display `[Inc]` and are excluded from delta/trend calculations for fair comparisons.
- **Visual Bar Charts:** Generates high-resolution grouped bar charts for the community and each CUPS into `.output/charts/`, embedded in Markdown reports.

### 🧹 Output Cleanup (`da cleanup` / `da clean`)
```bash
da cleanup              # Interactive cleanup (prompts before deletion)
da cleanup --force      # Immediate deletion without confirmation (-f alias)
da cleanup --output-dir /path/to/output -f # Clean custom output directory
```

---

## 🧪 Quality Assurance & Tooling

```bash
pytest -v                 # Run test suite
ruff check --fix .        # Lint and auto-fix code
ruff format .             # Format code
pre-commit run --all-files # Verify pre-commit hooks across all files
```

---

## 🤝 Documentation, Contributing & License

- 📘 [Operational Architecture Guide (English)](docs/GUIDE_EN.md) — Comprehensive guide to ingestion, heuristics, math invariants, and outputs.
- 🇪🇸 [Guía de Arquitectura y Operación (Español)](docs/GUIDE_ES.md) — Guía completa sobre el canal de ingesta, cálculo de reparto, heurísticas y salidas.
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines, Conventional Commits, and PR workflow.
- 🤖 [AGENTS.md](AGENTS.md) — Technical instructions and architectural guidelines for AI agents and developers.
- 📄 [LICENSE](LICENSE) — Licensed under the [MIT License](LICENSE).

---

## 🤖 AI Development & Vibe Coding Disclosure

Developed via a **vibe coding** workflow pairing natural language direction with agentic code generation:
- **🛠️ Agentic IDE:** Google Antigravity IDE (DeepMind Advanced Agentic Coding).
- **🧠 Models:** Google Gemini (Gemini Flash 3.8 in High reasoning).
- **🛡️ Quality Assurance:** Automated test suite via Pytest, strict Ruff linting, 100.00% fair-share math invariants, and zero-leakage CUPS privacy enforcement.
