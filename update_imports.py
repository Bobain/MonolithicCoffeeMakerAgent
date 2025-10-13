#!/usr/bin/env python3
"""
Update imports from old langfuse_observe paths to new module structure.

This script updates all Python files to use the new module hierarchy:
- langfuse_observe.llm* → llm.*
- langfuse_observe.rate_limiter → llm.rate_limiting.limiter
- langfuse_observe.strategies → llm.strategies
- langfuse_observe.llm_providers → llm.providers
- langfuse_observe.http_pool → utils.http_pool
- langfuse_observe (rest) → observability
"""

import re
from pathlib import Path
from typing import List, Tuple

# Define import mappings (order matters - most specific first)
IMPORT_MAPPINGS = [
    # LLM core modules
    (r"from coffee_maker\.langfuse_observe\.llm import", "from coffee_maker.llm.factory import"),
    (r"from coffee_maker\.langfuse_observe\.llm_config import", "from coffee_maker.llm.config import"),
    (r"from coffee_maker\.langfuse_observe\.llm_tools import", "from coffee_maker.llm.tools import"),
    (r"from coffee_maker\.langfuse_observe\.scheduled_llm import", "from coffee_maker.llm.scheduled import"),
    (
        r"from coffee_maker\.langfuse_observe\.auto_picker_llm_refactored import",
        "from coffee_maker.llm.auto_picker import",
    ),
    (r"from coffee_maker\.langfuse_observe\.builder import", "from coffee_maker.llm.builder import"),
    # Rate limiting
    (r"from coffee_maker\.langfuse_observe\.rate_limiter import", "from coffee_maker.llm.rate_limiting.limiter import"),
    (
        r"from coffee_maker\.langfuse_observe\.global_rate_tracker import",
        "from coffee_maker.llm.rate_limiting.tracker import",
    ),
    (r"from coffee_maker\.langfuse_observe\.cost_budget import", "from coffee_maker.llm.rate_limiting.budget import"),
    # Strategies
    (r"from coffee_maker\.langfuse_observe\.strategies\.retry import", "from coffee_maker.llm.strategies.retry import"),
    (
        r"from coffee_maker\.langfuse_observe\.strategies\.fallback import",
        "from coffee_maker.llm.strategies.fallback import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.strategies\.scheduling import",
        "from coffee_maker.llm.strategies.scheduling import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.strategies\.context import",
        "from coffee_maker.llm.strategies.context import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.strategies\.metrics import",
        "from coffee_maker.llm.strategies.metrics import",
    ),
    (r"from coffee_maker\.langfuse_observe\.strategies import", "from coffee_maker.llm.strategies import"),
    # LLM providers
    (r"from coffee_maker\.langfuse_observe\.llm_providers import", "from coffee_maker.llm.providers import"),
    (
        r"from coffee_maker\.langfuse_observe\.llm_providers\.openai import",
        "from coffee_maker.llm.providers.openai import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.llm_providers\.gemini import",
        "from coffee_maker.llm.providers.gemini import",
    ),
    # Utilities
    (r"from coffee_maker\.langfuse_observe\.http_pool import", "from coffee_maker.utils.http_pool import"),
    (r"from coffee_maker\.langfuse_observe\.response_parser import", "from coffee_maker.utils.response_parser import"),
    (r"from coffee_maker\.langfuse_observe\.token_estimator import", "from coffee_maker.utils.token_estimator import"),
    # Analytics (stay in observability)
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.analyzer_sqlite import",
        "from coffee_maker.observability.analytics.analyzer_sqlite import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.analyzer import",
        "from coffee_maker.observability.analytics.analyzer import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.exporter_sqlite import",
        "from coffee_maker.observability.analytics.exporter_sqlite import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.exporter import",
        "from coffee_maker.observability.analytics.exporter import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.models_sqlite import",
        "from coffee_maker.observability.analytics.models_sqlite import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.models import",
        "from coffee_maker.observability.analytics.models import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.db_schema import",
        "from coffee_maker.observability.analytics.db_schema import",
    ),
    (
        r"from coffee_maker\.langfuse_observe\.analytics\.config import",
        "from coffee_maker.observability.analytics.config import",
    ),
    (r"from coffee_maker\.langfuse_observe\.analytics import", "from coffee_maker.observability.analytics import"),
    # Everything else goes to observability (catch-all - must be last)
    (r"from coffee_maker\.langfuse_observe\.agents import", "from coffee_maker.observability.agents import"),
    (
        r"from coffee_maker\.langfuse_observe\.cost_calculator import",
        "from coffee_maker.observability.cost_calculator import",
    ),
    (r"from coffee_maker\.langfuse_observe\.retry import", "from coffee_maker.observability.retry import"),
    (r"from coffee_maker\.langfuse_observe\.exceptions import", "from coffee_maker.observability.exceptions import"),
    (r"from coffee_maker\.langfuse_observe\.tools import", "from coffee_maker.observability.tools import"),
    (
        r"from coffee_maker\.langfuse_observe\.langfuse_logger import",
        "from coffee_maker.observability.langfuse_logger import",
    ),
    (r"from coffee_maker\.langfuse_observe\.utils import", "from coffee_maker.observability.utils import"),
    (r"from coffee_maker\.langfuse_observe import", "from coffee_maker.observability import"),
]


def update_file(file_path: Path) -> Tuple[int, List[str]]:
    """Update imports in a single file.

    Returns:
        (num_replacements, list of changes made)
    """
    try:
        content = file_path.read_text()
        original_content = content
        changes = []

        for old_pattern, new_import in IMPORT_MAPPINGS:
            matches = list(re.finditer(old_pattern, content))
            if matches:
                content = re.sub(old_pattern, new_import, content)
                for match in matches:
                    old_line = original_content[match.start() : match.end()]
                    changes.append(f"  {old_pattern} → {new_import}")

        if content != original_content:
            file_path.write_text(content)
            return len(changes), changes

        return 0, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, []


def main():
    """Update all Python files."""
    project_root = Path(__file__).parent

    # Find all Python files
    python_files = []
    for directory in ["coffee_maker", "tests"]:
        dir_path = project_root / directory
        if dir_path.exists():
            python_files.extend(dir_path.rglob("*.py"))

    print(f"Found {len(python_files)} Python files")
    print("=" * 80)

    total_changes = 0
    files_changed = 0

    for file_path in sorted(python_files):
        num_changes, changes = update_file(file_path)
        if num_changes > 0:
            files_changed += 1
            total_changes += num_changes
            print(f"\n✅ {file_path.relative_to(project_root)}")
            for change in changes:
                print(change)

    print("\n" + "=" * 80)
    print(f"✅ Updated {files_changed} files with {total_changes} import changes")
    print("=" * 80)


if __name__ == "__main__":
    main()
