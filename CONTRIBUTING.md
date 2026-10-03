# Contributing to DATADIS Analyzer

Thank you for your interest in contributing to **DATADIS Analyzer** (`da`)! This project is an open-source CLI tool and library designed to analyze hourly electrical energy consumption data exported from Spain's [DATADIS](https://datadis.es) platform for residential building communities (*comunidades de vecinos*).

We welcome contributions of all kinds: bug reports, documentation enhancements, feature proposals, and pull requests.

To maintain code quality, security, and a clean repository history, all contributors are expected to follow the guidelines outlined below.

---

## Table of Contents
1. [Guiding Principles & Anonymization Policy](#1-guiding-principles--anonymization-policy)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Conventional Commits Specification](#3-conventional-commits-specification)
4. [Coding Standards & Conventions](#4-coding-standards--conventions)
5. [Testing Guidelines](#5-testing-guidelines)
6. [Pull Request Workflow](#6-pull-request-workflow)
7. [Related Documentation](#7-related-documentation)

---

## 1. Guiding Principles & Anonymization Policy

### ⚠️ Strict Privacy & Data Anonymization Rule
DATADIS CSV exports contain sensitive information:
- Real CUPS identifiers (*Código Unificado de Punto de Suministro*), which identify physical properties.
- Hourly consumption figures that can reveal private household routines.
- Contract numbers and distributor identifiers.

> [!CAUTION]
> **NEVER commit real CUPS numbers, contract numbers, or real residential datasets into this repository.**

- All test fixtures in `tests/conftest.py` and mock CSV files must use **anonymized dummy CUPS** following Spain's format (e.g., `ES0021000000000001AA`, `ES0021000000000002BB`).
- Any issue, pull request description, or test case leaking real supply point identifiers will be scrubbed immediately.

---

## 2. Development Environment Setup

### Prerequisites
- **Python:** Version 3.11 or higher (Python 3.12+ recommended).
- **Git:** Version 2.30+.

### Local Setup Steps

1. **Clone the repository:**
   ```bash
   git clone git@github.com:marcosDLCS/datadis-analyzer.git
   cd datadis-analyzer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the package in editable mode with development dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

4. **Install git pre-commit hooks:**
   ```bash
   pre-commit install
   ```
   This automatically runs Ruff linting, formatting, and file sanity checks before every `git commit`.

5. **Verify the installation:**
   ```bash
   da --help
   pytest
   ruff check .
   ruff format --check .
   ```

6. **Initialize local workspace directories:**
   ```bash
   da init
   ```
   This command creates `./.input` and `./.output` directories and persists your output language preference in `.da_config.json`.

---

## 3. Conventional Commits Specification

This project strictly adheres to the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification. Every commit message must follow this structure:

```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types
| Type | Description | Example |
| :--- | :--- | :--- |
| `feat` | A new user-facing feature | `feat(cli): add CSV delimiter override option` |
| `fix` | A bug fix | `fix(validator): handle empty lines at end of CSV` |
| `docs` | Documentation only changes | `docs: add contributing guide and link to readme` |
| `style` | Formatting, missing whitespace, no production code change | `style(views): adjust table border padding` |
| `refactor` | Code restructuring without altering external behavior | `refactor(aggregator): optimize monthly pivot calculation` |
| `perf` | Code changes improving execution speed or memory usage | `perf(loader): use vectorized datetime parsing` |
| `test` | Adding or updating automated tests | `test(cli): add tests for custom input directory` |
| `build` | Build system, packaging, or dependency updates | `build: bump rich dependency to 13.9.0` |
| `ci` | Continuous integration configuration changes | `ci: add GitHub Actions workflow for pytest` |
| `chore` | Maintenance tasks, repository housekeeping | `chore: update .gitignore for editor artifacts` |

### Allowed Scopes
Common scopes include:
- `cli` — Typer CLI commands, options, and callbacks (`src/cli.py`)
- `core` — Core application infrastructure
- `config` — Settings persistence, path resolution (`src/config.py`)
- `i18n` — Multi-language translations and localization engine (`src/i18n.py`)
- `loader` — CSV file discovery and DataFrame ingestion (`src/ingestion/loader.py`)
- `validator` — Delimiter, encoding, and schema validation (`src/ingestion/validator.py`)
- `aggregator` — Grouping logic, period shares, and pivots (`src/processing/aggregator.py`)
- `views` — Terminal tables, metric panels, and formatting (`src/presentation/views.py`)
- `export` — Markdown report generation (`src/presentation/export.py`)

### Formatting Rules
- **Description:** Written in the imperative mood, present tense ("add", not "added" or "adds").
- **Case:** Start with a lowercase letter.
- **Punctuation:** Do not end the description with a period (`.`).
- **Body:** Use the body to explain the *what* and *why* behind the change, not just restate the commit title.

---

## 4. Coding Standards & Conventions

### Language & Documentation
- **Code Language:** Write all code, class/function names, variables, comments, docstrings, and commit messages entirely in **English**.
- **User Interface (i18n):** Any string presented to the user via the CLI or markdown export must be registered in [src/i18n.py](src/i18n.py) in both English (`en`) and Spanish (`es`).

### Type Annotations
- Use strict, explicit type hinting from the standard `typing` module on **all** function signatures, dataclasses, and class methods.
- Avoid untyped `Any` whenever a concrete type or `Union` can be defined.

### Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Keep line lengths reasonable (maximum 100–120 characters).
- Maintain modular architecture: keep data ingestion (`src/ingestion/`), domain processing (`src/processing/`), and visual presentation (`src/presentation/`) strictly separated.

### Linting & Formatting (Ruff & Pre-Commit)
We enforce clean, consistent code style using [Ruff](https://astral.sh/ruff), the high-performance Python linter and code formatter:
- **Linting:** `ruff check .` (run `ruff check --fix .` to automatically fix common lint issues).
- **Formatting (Prettier for Python):** `ruff format .` (run `ruff format --check .` to verify formatting in CI).
- **Pre-commit Automation:** Git pre-commit hooks ensure that all staged Python files pass Ruff linting and formatting before any commit is accepted. Install once via `pre-commit install`.
- **Manual Hook Verification:** Run all hooks across the codebase with `pre-commit run --all-files`.

### Terminal UI Aesthetics
- Keep Rich tables responsive and compact.
- Ensure terminal tables fit comfortably within standard **80-column terminals** without line wraps or broken column alignments (`no_wrap=True` for identifiers, numbers, and percentages).

### Error Handling
- Use custom domain exceptions defined in `src.ingestion.schema`:
  - `DatadisError`: Base exception for all domain errors.
  - `DatadisValidationError`: Raised when file headers, delimiters, or formats fail validation.
  - `DatadisParseError`: Raised when data cannot be normalized into valid numeric records.
- CLI commands should catch known domain exceptions and print formatted error panels rather than dumping raw Python stack traces.

---

## 5. Testing Guidelines

Automated testing is mandatory for all contributions.

### Running Tests
Execute the test suite using `pytest`:

```bash
# Run all tests with verbose output
pytest -v

# Run with concise summary
pytest -q

# Run a specific test module
pytest tests/test_aggregator.py -v
```

### Test Standards
- Every new feature, validation rule, or calculation must include automated tests in `tests/`.
- Ensure all tests use isolated temporary fixtures (`tmp_path`, `sample_valid_csv`, `sample_input_hierarchy`) to prevent side effects on the workspace or configuration files.
- The entire test suite must pass with a 100% pass rate before opening a Pull Request.

---

## 6. Pull Request Workflow

1. **Create a topic branch:**
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes:**
   - Write clean, well-tested code.
   - Update documentation and docstrings where relevant.

3. **Verify tests and style locally:**
   ```bash
   pytest -v
   ```

4. **Commit using Conventional Commits:**
   ```bash
   git commit -m "feat(aggregator): add quarterly aggregation support"
   ```

5. **Push and open a Pull Request:**
   - Provide a clear, detailed PR description outlining the motivation and changes.
   - Confirm that the PR checklist has been satisfied:
     - [ ] Commits follow the Conventional Commits specification.
     - [ ] All automated tests pass (`pytest -v`).
     - [ ] Pre-commit hooks and Ruff checks pass (`pre-commit run --all-files`).
     - [ ] No real CUPS codes or personal data are included.
     - [ ] Both English and Spanish translations are updated in `src/i18n.py` (if applicable).
     - [ ] Documentation (`README.md`, `AGENTS.md`) is updated if CLI options or behaviors changed.

---

## 7. Related Documentation

- [README.md](README.md) — User guide, installation steps, and CLI usage reference.
- [AGENTS.md](AGENTS.md) — Technical reference, domain architecture, and AI agent guidelines.
