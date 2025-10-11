"""Tests ensuring each coffee_maker script with a __main__ guard imports cleanly."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

from coffee_maker.config import ConfigManager

_REPO_ROOT = Path(__file__).resolve().parents[1].parent
_COFFEE_MAKER_DIR = _REPO_ROOT / "coffee_maker"


def _discover_main_scripts() -> list[Path]:
    """Discovers all Python scripts in the coffee_maker directory with a __main__ guard.

    Returns:
        list[Path]: A list of paths to the discovered scripts.
    """
    scripts: list[Path] = []
    for candidate in _COFFEE_MAKER_DIR.rglob("*.py"):
        try:
            source = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if 'if __name__ == "__main__"' in source:
            scripts.append(candidate)
    return scripts


_MAIN_SCRIPTS = _discover_main_scripts()


@pytest.mark.parametrize(
    "script_path",
    _MAIN_SCRIPTS,
    ids=lambda path: str(path.relative_to(_REPO_ROOT)),
)
def test_main_script_imports_without_running_main(script_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that a script with a main guard can be imported without executing its CLI.

    This test uses runpy to import the script with a run_name other than `__main__`,
    ensuring that the code under the `if __name__ == "__main__"` block is not run.
    It also sets dummy environment variables that might be required at import time.

    Args:
        script_path (Path): The path to the script to test.
        monkeypatch (pytest.MonkeyPatch): The pytest fixture for modifying environments.
    """
    # Set dummy Gemini API keys for import testing
    # Use existing keys if available, otherwise use dummy values
    monkeypatch.setenv("COFFEE_MAKER_GEMINI_API_KEY", ConfigManager.get_gemini_api_key(required=False) or "dummy")
    monkeypatch.setenv("GEMINI_API_KEY", ConfigManager.get_gemini_api_key(required=False) or "dummy")
    monkeypatch.setenv("GOOGLE_API_KEY", ConfigManager.get_gemini_api_key(required=False) or "dummy")

    try:
        runpy.run_path(str(script_path), run_name="__coffee_maker_test__")
    except ModuleNotFoundError as exc:  # pragma: no cover - optional deps
        pytest.skip(f"Optional dependency missing while importing {script_path}: {exc.name}")
