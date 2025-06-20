import pathlib

import pytest

# Define paths to fixture files
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_code_before_content() -> str:
    with open(FIXTURES_DIR / "sample_code_before.py", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_code_after_content() -> str:
    with open(FIXTURES_DIR / "sample_code_after.py", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_styleguide_content() -> str:
    with open(FIXTURES_DIR / "sample_styleguide.md", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def llm_response_changes_content() -> str:
    with open(FIXTURES_DIR / "sample_llm_response_changes.txt", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def llm_response_no_changes_content() -> str:
    with open(FIXTURES_DIR / "sample_llm_response_no_changes.txt", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def llm_response_malformed_content() -> str:
    with open(FIXTURES_DIR / "sample_llm_response_malformed.txt", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def temp_env_file_with_key(tmp_path: pathlib.Path, monkeypatch) -> pathlib.Path:
    env_file = tmp_path / ".env"
    env_file.write_text("GEMINI_API_KEY=test_api_key_from_file\n")
    # Ensure load_dotenv uses this temp file if it's called
    monkeypatch.setattr(pathlib.Path, "is_file", lambda self: self == env_file)
    return env_file


@pytest.fixture
def temp_env_file_empty(tmp_path: pathlib.Path) -> pathlib.Path:
    env_file = tmp_path / ".env_empty"
    env_file.touch()  # Create an empty file
    return env_file
