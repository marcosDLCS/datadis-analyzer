"""Automated unit and integration tests for security and privacy enforcement engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.security import (
    audit_repository,
    check_commit_security,
    is_allowed_synthetic_cups,
    main,
    scan_content,
    scan_coordinate_violations,
    scan_cups_violations,
    scan_file,
    scan_secret_violations,
)


def test_is_allowed_synthetic_cups_approved() -> None:
    """Approved synthetic mock CUPS must return True."""
    assert is_allowed_synthetic_cups("ES0021000000000001AA")
    assert is_allowed_synthetic_cups("ES0021000000000002BB")
    assert is_allowed_synthetic_cups("ES0021000000000099ZZ")
    assert is_allowed_synthetic_cups("ES0021000000001234AA")
    assert is_allowed_synthetic_cups("ES0000000000000000AA")
    assert is_allowed_synthetic_cups("ES9999999999999999ZZ")
    # Case insensitivity
    assert is_allowed_synthetic_cups("es0021000000000001aa")
    # Optional border point characters
    assert is_allowed_synthetic_cups("ES0021000000000001AA0F")


def test_is_allowed_synthetic_cups_forbidden() -> None:
    """Real or non-synthetic mock CUPS must return False."""
    bad_cups_1 = "ES" + "0021000043179111WN"
    bad_cups_2 = "ES" + "0031123456789012AA"
    bad_cups_3 = "ES" + "1234567890123456AB"
    assert not is_allowed_synthetic_cups(bad_cups_1)
    assert not is_allowed_synthetic_cups(bad_cups_2)
    assert not is_allowed_synthetic_cups(bad_cups_3)
    assert not is_allowed_synthetic_cups("INVALID_CUPS")
    assert not is_allowed_synthetic_cups("")


def test_scan_cups_violations() -> None:
    """scan_cups_violations should detect unapproved CUPS and deduplicate them."""
    clean_text = "Community with ES0021000000000001AA and ES0021000000000002BB meters."
    assert scan_cups_violations(clean_text) == []

    bad_cups = "ES" + "0021000043179111WN"
    dirty_text = f"Supply 1: {bad_cups}, Supply 2: {bad_cups} duplicate."
    violations = scan_cups_violations(dirty_text)
    assert violations == [bad_cups]


def test_scan_coordinate_violations() -> None:
    """scan_coordinate_violations should detect forbidden and suspicious coordinates."""
    clean_text = "No coordinates here, just energy consumption 42.5 kWh."
    assert scan_coordinate_violations(clean_text) == []

    # Forbidden specific coordinates (constructed dynamically to avoid scanner hit)
    coord_1 = "41." + "651983"
    coord_2 = "-4." + "728469"
    v1 = scan_coordinate_violations(f"Building location: {coord_1}")
    assert any("Forbidden coordinate pattern" in v and coord_1 in v for v in v1)
    v2 = scan_coordinate_violations(f"Longitude: {coord_2}")
    assert any("Forbidden coordinate pattern" in v and coord_2 in v for v in v2)

    # Generic coordinate with cardinal suffix
    generic_coord = "41.6519" + "° N"
    v3 = scan_coordinate_violations(f"Site: {generic_coord}")
    assert any("Suspicious geographic coordinate" in v for v in v3)

    # Coordinate decimal pair
    coord_pair = "40.4167" + ", -3.7037"
    v4 = scan_coordinate_violations(f"Center: {coord_pair}")
    assert any("Suspicious decimal coordinate pair" in v for v in v4)


def test_scan_secret_violations() -> None:
    """scan_secret_violations should flag private keys and token patterns."""
    clean_text = "Standard public code without secrets."
    assert scan_secret_violations(clean_text) == []

    # Private key
    priv_key = "-----BEGIN " + "RSA PRIVATE KEY-----"
    v_key = scan_secret_violations(priv_key)
    assert any("Potential secret pattern" in v for v in v_key)

    # Bearer token
    bearer = "bearer " + "a" * 25
    v_bearer = scan_secret_violations(bearer)
    assert any("Potential secret pattern" in v for v in v_bearer)

    # API key assignment
    api_key_str = "api_key" + " = 'secret1234567890'"
    v_api = scan_secret_violations(api_key_str)
    assert any("Potential secret pattern" in v for v in v_api)

    # AWS Access Key ID
    aws_key = "AKIA" + "IOSFODNN7EXAMPLE"
    v_aws = scan_secret_violations(aws_key)
    assert any("Potential secret pattern" in v for v in v_aws)

    # GitHub token
    gh_token = "ghp_" + "a" * 36
    v_gh = scan_secret_violations(gh_token)
    assert any("Potential secret pattern" in v for v in v_gh)


def test_scan_content() -> None:
    """scan_content should format violations with line numbers and skip test_security files."""
    bad_cups = "ES" + "0021000043179111WN"
    content = f"First line\nSecond line with {bad_cups}\nThird line"
    violations = scan_content(content, filename="module.py")
    assert len(violations) == 1
    assert "Line 2:" in violations[0]
    assert bad_cups in violations[0]

    # test_security should be bypassed
    assert scan_content(content, filename="tests/test_security.py") == []


def test_scan_file(tmp_path: Path) -> None:
    """scan_file should scan an individual file and respect exclusions."""
    bad_cups = "ES" + "0021000043179111WN"
    dirty_file = tmp_path / "sample.py"
    dirty_file.write_text(f"cups = '{bad_cups}'\n", encoding="utf-8")

    violations = scan_file(dirty_file, repo_root=tmp_path)
    assert len(violations) == 1
    assert bad_cups in violations[0]

    clean_file = tmp_path / "clean.py"
    clean_file.write_text("cups = 'ES0021000000000001AA'\n", encoding="utf-8")
    assert scan_file(clean_file, repo_root=tmp_path) == []

    # File with ignored extension
    img_file = tmp_path / "photo.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert scan_file(img_file, repo_root=tmp_path) == []


def test_audit_repository_clean_live_repo() -> None:
    """The live repository must be 100% clean of security and privacy violations."""
    is_clean, violations = audit_repository()
    assert is_clean is True
    assert violations == []


def test_audit_repository_mock_tree(tmp_path: Path) -> None:
    """audit_repository should inspect mock tree and ignore ignored directories."""
    repo = tmp_path / "mock_repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='mock'\n", encoding="utf-8")

    # Clean file in src
    src_dir = repo / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("cups = 'ES0021000000000001AA'\n", encoding="utf-8")

    is_clean, violations = audit_repository(repo_root=repo)
    assert is_clean is True
    assert violations == []

    # Ignored directory (.input) containing unapproved CUPS should be skipped
    input_dir = repo / ".input" / "2025"
    input_dir.mkdir(parents=True)
    bad_cups = "ES" + "0021000043179111WN"
    (input_dir / "data.csv").write_text(f"cups,val\n{bad_cups},10\n", encoding="utf-8")

    is_clean, violations = audit_repository(repo_root=repo)
    assert is_clean is True
    assert violations == []

    # File in tracked src containing unapproved CUPS should trigger violation
    (src_dir / "leaked.py").write_text(f"bad = '{bad_cups}'\n", encoding="utf-8")
    is_clean, violations = audit_repository(repo_root=repo)
    assert is_clean is False
    assert len(violations) == 1
    assert "leaked.py" in violations[0]


def test_check_commit_security(tmp_path: Path) -> None:
    """check_commit_security should return 0 on a clean repository."""
    repo = tmp_path / "clean_repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='clean'\n", encoding="utf-8")
    (repo / "code.py").write_text("x = 1\n", encoding="utf-8")

    exit_code = check_commit_security(repo_root=repo)
    assert exit_code == 0


def test_main_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """main(['--help']) should display command instructions and exit 0."""
    code = main(["--help"])
    assert code == 0
    captured = capsys.readouterr()
    assert "DATADIS Analyzer — Security & Privacy Enforcement Engine" in captured.out
    assert "Usage:" in captured.out


def test_main_cli_audit_clean() -> None:
    """main(['audit']) on the clean repository should return 0."""
    code = main(["audit"])
    assert code == 0


def test_main_cli_scan(tmp_path: Path) -> None:
    """main(['scan', path]) should inspect individual files and directories."""
    clean_file = tmp_path / "clean.py"
    clean_file.write_text("ok = True\n", encoding="utf-8")

    assert main(["scan", str(clean_file)]) == 0

    bad_cups = "ES" + "0021000043179111WN"
    dirty_file = tmp_path / "dirty.py"
    dirty_file.write_text(f"bad = '{bad_cups}'\n", encoding="utf-8")

    assert main(["scan", str(dirty_file)]) == 1

    # Scan without argument
    assert main(["scan"]) == 1
