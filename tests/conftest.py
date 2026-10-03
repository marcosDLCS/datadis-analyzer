import pytest
from src.config import AppConfig, save_config


@pytest.fixture(autouse=True)
def reset_default_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate configuration file during test execution to prevent cross-test contamination."""
    test_config = tmp_path / ".da_test_config.json"
    save_config(AppConfig(language="en"), test_config)
    monkeypatch.setattr("src.config.CONFIG_FILE_PATH", test_config)
    monkeypatch.setattr("src.cli.CONFIG_FILE_PATH", test_config)


@pytest.fixture
def sample_valid_csv(tmp_path: Path) -> Path:
    """Create a temporary valid DATADIS CSV file formatted with standard Spanish semicolons and commas."""
    content = (
        'cups;fecha;hora;consumo_kWh;metodoObtencion;energiaVertida_kWh;energiaGenerada_kWh;energiaAutoconsumida_kWh\n'
        '"ES0021000000000001AA";"2025/01/01";"01:00";"1,500";;;;\n'
        '"ES0021000000000001AA";"2025/01/01";"02:00";"2,500";;;;\n'
        '"ES0021000000000001AA";"2025/02/01";"01:00";"3,000";;;;\n'
    )
    file_path = tmp_path / "valid_sample.csv"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_second_cups_csv(tmp_path: Path) -> Path:
    """Create a second temporary valid DATADIS CSV for another CUPS."""
    content = (
        'cups;fecha;hora;consumo_kWh;metodoObtencion;energiaVertida_kWh;energiaGenerada_kWh;energiaAutoconsumida_kWh\n'
        '"ES0021000000000002BB";"2025/01/01";"01:00";"4,500";;;;\n'
        '"ES0021000000000002BB";"2025/01/01";"02:00";"1,500";;;;\n'
        '"ES0021000000000002BB";"2025/02/01";"01:00";"7,000";;;;\n'
    )
    file_path = tmp_path / "valid_sample_cups2.csv"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_input_hierarchy(tmp_path: Path) -> Path:
    """Create an annualized .input directory hierarchy with multiple years and CUPS."""
    input_root = tmp_path / ".input"
    dir_2024 = input_root / "2024"
    dir_2025 = input_root / "2025"
    dir_2024.mkdir(parents=True)
    dir_2025.mkdir(parents=True)

    # 2024 files
    c2024_1 = (
        'cups;fecha;hora;consumo_kWh\n'
        '"ES0021000000000001AA";"2024/05/10";"12:00";"10,00"\n'
        '"ES0021000000000001AA";"2024/06/10";"12:00";"20,00"\n'
    )
    (dir_2024 / "cups1_2024.csv").write_text(c2024_1, encoding="utf-8")

    c2024_2 = (
        'cups;fecha;hora;consumo_kWh\n'
        '"ES0021000000000002BB";"2024/05/10";"12:00";"30,00"\n'
        '"ES0021000000000002BB";"2024/06/10";"12:00";"40,00"\n'
    )
    (dir_2024 / "cups2_2024.csv").write_text(c2024_2, encoding="utf-8")

    # 2025 files
    c2025_1 = (
        'cups;fecha;hora;consumo_kWh\n'
        '"ES0021000000000001AA";"2025/01/15";"10:00";"50,00"\n'
    )
    (dir_2025 / "cups1_2025.csv").write_text(c2025_1, encoding="utf-8")

    c2025_2 = (
        'cups;fecha;hora;consumo_kWh\n'
        '"ES0021000000000002BB";"2025/01/15";"10:00";"50,00"\n'
    )
    (dir_2025 / "cups2_2025.csv").write_text(c2025_2, encoding="utf-8")

    return input_root
