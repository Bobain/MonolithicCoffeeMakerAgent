# Repository Guidelines

## Project Structure & Module Organization
- `coffee_maker/` holds agent modules; `auto_gemini_styleguide.py` orchestrates AI-driven formatting, `utils/` contains shared helpers, `sec_vuln_helper/` isolates security scans, and `code_formatter/` hosts formatting pipelines consumed by CI.
- Example projects live in `coffee_maker/examples/llama_index/` and `examples/HF_MCP_course/`; use them as reference when wiring new agents or MCP integrations.
- Tests are under `tests/`, with fast guardrails in `ci_tests/` (arranged by feature folders) and slower external checks in `integration_tests/`.
- Static assets and docs reside in `resources/README/` and automation helpers in `init_scripts/`.

## Build, Test, and Development Commands
- `poetry install` — provision a local virtualenv aligned with `pyproject.toml`.
- `poetry run pytest tests/ci_tests` — execute the smoke suite expected by CI.
- `poetry run pytest -m integration` — run integration flows that hit external services; export required tokens beforehand.
- `poetry run python coffee_maker/auto_gemini_styleguide.py --help` — inspect the AI-guided formatter when modifying style prompts.

## Coding Style & Naming Conventions
- Target Python ≥3.11 with `black` enforcing 120-character lines; run `poetry run pre-commit install` to enable local hooks.
- Keep modules snake_case and reusable helpers inside `coffee_maker/utils/`; prefer descriptive function names such as `load_api_key`.
- Allow `autoflake` to prune unused imports/variables before review; avoid manual formatting that fights the hook chain.

## Testing Guidelines
- Use `pytest` for all new tests; co-locate them beside the feature folder under `tests/ci_tests/<feature>/`.
- Name files `*_test.py` and mark long-running checks with `@pytest.mark.integration` so they can be skipped via `-m "not integration"`.
- Aim to touch primary execution paths and regenerate coverage locally with `poetry run pytest --cov=coffee_maker --cov-report=term-missing`.

## Commit & Pull Request Guidelines
- Follow the existing short, descriptive subject style (e.g., `added tracing`); keep the summary ≤50 characters and prefer present tense.
- Group related changes per commit and include context in the body when behavior shifts or configuration changes.
- Pull requests should link the motivating issue, list manual test commands, and attach screenshots for UI or Gradio tweaks.

## Security & Configuration Tips
- Copy `.env.example` to `.env`, supply credentials such as `COFFEE_MAKER_GEMINI_API_KEY`, and never commit secrets.
- Review `.github/workflows/` when adding dependencies to ensure CI and publishing jobs remain green.
