"""Tests ensuring each coffee_maker script with a __main__ guard imports cleanly."""

from __future__ import annotations

import os
import runpy
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1].parent
_COFFEE_MAKER_DIR = _REPO_ROOT / "coffee_maker"


def _discover_main_scripts() -> list[Path]:
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
    """Import each script with a non-__main__ run_name to avoid executing its CLI."""

    monkeypatch.setenv("COFFEE_MAKER_GEMINI_API_KEY", os.getenv("COFFEE_MAKER_GEMINI_API_KEY", "dummy"))
    monkeypatch.setenv("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "dummy"))
    monkeypatch.setenv("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", "dummy"))

    try:
        runpy.run_path(str(script_path), run_name="__coffee_maker_test__")
    except ModuleNotFoundError as exc:  # pragma: no cover - optional deps
        pytest.skip(f"Optional dependency missing while importing {script_path}: {exc.name}")
