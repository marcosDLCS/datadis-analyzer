"""Security audit and privacy enforcement engine for DATADIS Analyzer.

Enforces zero-leakage invariants:
1. Universal supply point code (CUPS) privacy: Under Spanish regulations (RD 1435/2002)
   and EU GDPR (Regulation EU 2016/679 / LOPDGDD), a CUPS is personal data identifying
   a physical supply point. Real CUPS numbers must NEVER be committed to Git.
   Only synthetic dummy mock identifiers matching allowed patterns are permitted.
2. Coordinates & address privacy: Precise community coordinates (lat/long) or residential
   addresses identifying physical buildings must never be hardcoded into the repository.
3. Secrets & credentials: API keys, tokens, passwords, and private certificates are blocked.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

# Spanish CUPS pattern: ES followed by 16 alphanumeric characters and 2 letters (or optional 2-4 border point chars)
CUPS_REGEX = re.compile(r"\b(ES[0-9]{16}[A-Z]{2}(?:[0-9A-Z]{2,4})?)\b", re.IGNORECASE)

# Whitelist of allowed synthetic test mock CUPS patterns
ALLOWED_SYNTHETIC_CUPS_PATTERNS = [
    re.compile(
        r"^ES002100000000\d{4}[A-Z]{2}(?:[0-9A-Z]{2,4})?$", re.IGNORECASE
    ),  # ES0021000000000001AA..9999ZZ
    re.compile(r"^ES0000000000000000[A-Z]{2}(?:[0-9A-Z]{2,4})?$", re.IGNORECASE),  # All zeroes
    re.compile(r"^ES9999999999999999[A-Z]{2}(?:[0-9A-Z]{2,4})?$", re.IGNORECASE),  # All nines
]

# Known leaked coordinate patterns to block permanently
FORBIDDEN_COORDINATES_REGEX = re.compile(
    r"(41\.651983|-4\.728469)",
    re.IGNORECASE,
)

# Potential generic geographic coordinate patterns (latitude / longitude in decimal degrees with cardinal suffix)
GENERIC_COORDINATE_REGEX = re.compile(r"\b(-?\d{1,2}\.\d{4,6})\s*°?\s*([NSnsOEWoew])\b")

# Coordinate pairs in decimal degrees (e.g., latitude, longitude values)
COORDINATE_PAIR_REGEX = re.compile(r"\b([+-]?\d{1,2}\.\d{4,7})\s*,\s*([+-]?\d{1,3}\.\d{4,7})\b")

# Secret and credential patterns
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9_\-\.]{20,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|secret[_-]?token|auth[_-]?token|access[_-]?token)\s*[:=]\s*['\"][a-zA-Z0-9_\-/.+=]{8,}['\"]"
    ),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b"),
    re.compile(r"\bxox[baprs]-[0-9a-zA-Z]{10,48}\b"),
]

# File patterns to exclude from inspection
IGNORED_DIRS = {
    ".eggs",
    ".gemini",
    ".git",
    ".idea",
    ".input",
    ".output",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "build",
    "dist",
    "env",
    "node_modules",
    "venv",
    "__pycache__",
}

IGNORED_EXTENSIONS = {
    ".dylib",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".lock",
    ".pdf",
    ".png",
    ".pyc",
    ".pyd",
    ".pyo",
    ".so",
    ".svg",
    ".tar",
    ".webp",
    ".zip",
}


def is_allowed_synthetic_cups(cups: str) -> bool:
    """Return True if the given CUPS is an approved synthetic dummy mock."""
    clean = cups.strip().upper()
    return any(p.match(clean) is not None for p in ALLOWED_SYNTHETIC_CUPS_PATTERNS)


def scan_cups_violations(text: str) -> list[str]:
    """Find any CUPS in text that are not on the approved synthetic whitelist."""
    violations: list[str] = []
    seen: set[str] = set()
    for match in CUPS_REGEX.finditer(text):
        candidate = match.group(1).upper()
        if candidate not in seen and not is_allowed_synthetic_cups(candidate):
            seen.add(candidate)
            violations.append(candidate)
    return violations


def scan_coordinate_violations(text: str) -> list[str]:
    """Find any forbidden or suspicious coordinates in text."""
    violations: list[str] = []
    seen: set[str] = set()

    for match in FORBIDDEN_COORDINATES_REGEX.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            violations.append(f"Forbidden coordinate pattern: {val}")

    for match in GENERIC_COORDINATE_REGEX.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            violations.append(f"Suspicious geographic coordinate: {val}")

    for match in COORDINATE_PAIR_REGEX.finditer(text):
        val = match.group(0)
        if val not in seen:
            seen.add(val)
            violations.append(f"Suspicious decimal coordinate pair: {val}")

    return violations


def scan_secret_violations(text: str) -> list[str]:
    """Find any exposed secrets or private keys in text."""
    violations: list[str] = []
    seen: set[str] = set()
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            val = match.group(0).strip()
            snippet = val[:24] + ("..." if len(val) > 24 else "")
            if snippet not in seen:
                seen.add(snippet)
                violations.append(f"Potential secret pattern: {snippet}")
    return violations


def scan_content(content: str, filename: str = "") -> list[str]:
    """Scan text content for any security or privacy violations.

    Returns:
        List of human-readable violation descriptions with line numbers.
    """
    # Skip test files specifically designed to test security rules
    if "test_security" in filename:
        return []

    violations: list[str] = []

    # 1. CUPS check
    seen_cups: dict[str, list[int]] = {}
    for match in CUPS_REGEX.finditer(content):
        candidate = match.group(1).upper()
        if not is_allowed_synthetic_cups(candidate):
            line_no = content[: match.start()].count("\n") + 1
            seen_cups.setdefault(candidate, []).append(line_no)

    for candidate, lines in seen_cups.items():
        line_str = (
            f"Line {lines[0]}"
            if len(lines) == 1
            else f"Lines {', '.join(str(ln) for ln in lines[:5])}{'...' if len(lines) > 5 else ''} ({len(lines)} occurrences)"
        )
        violations.append(
            f"{line_str}: Unapproved / non-synthetic CUPS '{candidate}' detected. "
            "Under Spanish Law (RD 1435/2002) and GDPR (Regulation EU 2016/679), CUPS is personal data. "
            "Use approved mock IDs (e.g. ES0021000000000001AA)."
        )

    # 2. Coordinates check
    seen_coords: dict[str, list[int]] = {}
    for match in FORBIDDEN_COORDINATES_REGEX.finditer(content):
        val = match.group(0)
        line_no = content[: match.start()].count("\n") + 1
        seen_coords.setdefault(f"Forbidden coordinate pattern: {val}", []).append(line_no)

    for match in GENERIC_COORDINATE_REGEX.finditer(content):
        val = match.group(0)
        line_no = content[: match.start()].count("\n") + 1
        seen_coords.setdefault(f"Suspicious geographic coordinate: {val}", []).append(line_no)

    for match in COORDINATE_PAIR_REGEX.finditer(content):
        val = match.group(0)
        line_no = content[: match.start()].count("\n") + 1
        seen_coords.setdefault(f"Suspicious decimal coordinate pair: {val}", []).append(line_no)

    for desc, lines in seen_coords.items():
        line_str = (
            f"Line {lines[0]}"
            if len(lines) == 1
            else f"Lines {', '.join(str(ln) for ln in lines[:5])}"
        )
        violations.append(
            f"{line_str}: {desc}. Physical community coordinates must not be committed."
        )

    # 3. Secret check
    seen_secrets: dict[str, list[int]] = {}
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(content):
            val = match.group(0).strip()
            snippet = val[:24] + ("..." if len(val) > 24 else "")
            line_no = content[: match.start()].count("\n") + 1
            seen_secrets.setdefault(snippet, []).append(line_no)

    for snippet, lines in seen_secrets.items():
        line_str = (
            f"Line {lines[0]}"
            if len(lines) == 1
            else f"Lines {', '.join(str(ln) for ln in lines[:5])}"
        )
        violations.append(
            f"{line_str}: Potential exposed secret or credential pattern '{snippet}' detected."
        )

    return violations


def scan_file(path: Path, repo_root: Path | None = None) -> list[str]:
    """Scan an individual file for security violations.

    Returns:
        List of violations prefixed with the file's relative path.
    """
    if not path.is_file():
        return []
    if any(part in IGNORED_DIRS for part in path.parts):
        return []
    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return []

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    root = repo_root or find_repo_root(path.parent)
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        rel_path = path

    file_violations = scan_content(content, filename=str(rel_path))
    return [f"[{rel_path}] {v}" for v in file_violations]


def find_repo_root(start_path: Path | None = None) -> Path:
    """Locate the repository root containing pyproject.toml."""
    current = (start_path or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").is_file():
            return directory
    return current


def get_repo_files(repo_root: Path, staged_only: bool = False) -> list[Path]:
    """Retrieve candidate files to inspect from git or filesystem."""
    root = repo_root.resolve()

    if staged_only:
        try:
            res = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=d"],
                cwd=str(root),
                capture_output=True,
                text=True,
                check=True,
            )
            paths = [
                root / line.strip()
                for line in res.stdout.splitlines()
                if line.strip() and (root / line.strip()).is_file()
            ]
            return paths
        except Exception:
            return []

    # Full audit: try git tracked + untracked non-ignored files
    try:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        others = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
        combined = set(tracked.stdout.splitlines() + others.stdout.splitlines())
        paths = [
            root / line.strip()
            for line in combined
            if line.strip() and (root / line.strip()).is_file()
        ]
        if paths:
            return paths
    except Exception:
        pass

    # Fallback to filesystem traversal
    results: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in IGNORED_EXTENSIONS:
            continue
        results.append(path)
    return results


def audit_repository(
    repo_root: Path | None = None,
    staged_only: bool = False,
    files: Sequence[Path] | None = None,
) -> tuple[bool, list[str]]:
    """Audit repository files for security and privacy violations.

    Returns:
        (is_clean, list_of_errors)
    """
    root = repo_root or find_repo_root()
    target_files = (
        list(files) if files is not None else get_repo_files(root, staged_only=staged_only)
    )

    all_violations: list[str] = []

    for path in target_files:
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in IGNORED_EXTENSIONS:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        try:
            rel_path = path.relative_to(root)
        except ValueError:
            rel_path = path

        file_violations = scan_content(content, filename=str(rel_path))
        for v in file_violations:
            all_violations.append(f"[{rel_path}] {v}")

    return len(all_violations) == 0, all_violations


def check_commit_security(repo_root: Path | None = None) -> int:
    """Pre-commit check: inspect git staged changes for privacy and security leaks."""
    root = find_repo_root(repo_root)
    staged_files = get_repo_files(root, staged_only=True)

    if not staged_files:
        # If nothing is staged, audit full repo (e.g. pre-commit run --all-files)
        is_clean, violations = audit_repository(repo_root=root)
    else:
        is_clean, violations = audit_repository(repo_root=root, files=staged_files)

    if not is_clean:
        print_violations(violations)
        return 1

    print_success("Pre-commit security & CUPS privacy check passed.")
    return 0


def print_violations(violations: list[str]) -> None:
    """Render formatted violation report to stderr."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        err_console = Console(stderr=True)
        items_text = "\n".join(f"  • [red]{v}[/red]" for v in violations)
        panel_content = (
            f"[bold red]Violations Detected ({len(violations)}):[/bold red]\n\n"
            f"{items_text}\n\n"
            "[bold yellow]💡 Resolution:[/bold yellow]\n"
            "  1. Universal CUPS privacy: Replace real identifiers with synthetic test mocks "
            "(e.g., ES0021000000000001AA..99ZZ).\n"
            "  2. Address & coordinate privacy: Remove hardcoded community lat/long coordinates.\n"
            "  3. Credentials: Do not commit API tokens, passwords, or private keys."
        )
        err_console.print(
            Panel(
                panel_content,
                title="[bold red]🔒 SECURITY & PRIVACY VIOLATIONS DETECTED[/bold red]",
                border_style="red",
            )
        )
    except Exception:
        print("\n❌ SECURITY & PRIVACY VIOLATIONS DETECTED:", file=sys.stderr)
        for v in violations:
            print(f"  • {v}", file=sys.stderr)
        print(
            "\n💡 Resolution: Ensure all CUPS are synthetic dummy IDs (ES0021000000000001AA..99ZZ) "
            "and remove any coordinates, personal data, or credentials.\n",
            file=sys.stderr,
        )


def print_success(message: str) -> None:
    """Render formatted success confirmation."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        out_console = Console()
        out_console.print(
            Panel(
                f"[bold green]✔ {message}[/bold green]",
                border_style="green",
            )
        )
    except Exception:
        print(f"✔ {message}")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for manual audits, CI checks, and pre-commit hooks."""
    args = list(argv if argv is not None else sys.argv[1:])
    action = args[0].lower() if args else "audit"

    if action in ("--help", "-h", "help"):
        print(
            "DATADIS Analyzer — Security & Privacy Enforcement Engine\n\n"
            "Usage:\n"
            "  python -m src.security [audit] [path]  Audit repository or path (default)\n"
            "  python -m src.security hook / check    Audit staged changes (pre-commit hook)\n"
            "  python -m src.security scan <path>     Audit a specific file or directory\n"
        )
        return 0

    if action in ("check", "hook"):
        return check_commit_security()

    if action == "scan":
        if len(args) < 2:
            print("Error: 'scan' requires a file or directory path argument.", file=sys.stderr)
            return 1
        target_path = Path(args[1])
        if target_path.is_file():
            violations = scan_file(target_path)
            if violations:
                print_violations(violations)
                return 1
            print_success(f"File '{target_path}' passed security audit.")
            return 0
        is_clean, violations = audit_repository(repo_root=target_path)
        if not is_clean:
            print_violations(violations)
            return 1
        print_success(f"Directory '{target_path}' passed security audit: 0 violations found.")
        return 0

    # Default action: audit entire repository or specified path
    target_root = Path(args[1]) if len(args) > 1 else None
    print("🔒 Running DATADIS Analyzer Security & CUPS Privacy Audit...")
    is_clean, violations = audit_repository(repo_root=target_root)

    if not is_clean:
        print_violations(violations)
        return 1

    print_success("Security & privacy audit passed: 0 violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
