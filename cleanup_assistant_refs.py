#!/usr/bin/env python3
"""Script to clean up 'assistant (using code analysis skills)' references.

Replaces deprecated agent references with modern equivalents.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Replacement patterns (order matters for complex patterns)
REPLACEMENTS: List[Tuple[str, str]] = [
    # Agent mentions in text
    (
        r"assistant \(with code analysis skills\)",
        "assistant (using code analysis skills)",
    ),
    # Agent mentions in lists - remove entirely
    (r", assistant \(with code analysis skills\)", ""),
    (r"assistant \(with code analysis skills\), ", ""),
    # Delegation patterns
    (
        r"delegate to assistant \(with code analysis skills\)",
        "delegate to assistant for code analysis",
    ),
    (
        r"delegat\w* to assistant \(with code analysis skills\)",
        "delegates to assistant for code analysis",
    ),
    # Routing patterns
    (r"routes to assistant \(with code analysis skills\)", "routes to assistant"),
    (r"→ assistant \(with code analysis skills\)", "→ assistant"),
    # Directory references (keep docs/ references for now)
    (
        r'".claude/agents/assistant \(with code analysis skills\)\.md"',
        '".claude/agents/assistant.md"',
    ),
]


def clean_file(file_path: Path) -> bool:
    """Clean assistant references in a single file.

    Args:
        file_path: Path to file to clean

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text()
        original = content

        # Apply all replacement patterns
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # Only write if changed
        if content != original:
            file_path.write_text(content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    """Main cleanup routine."""
    # Find all Python and Markdown files
    patterns = ["**/*.py", "**/*.md"]
    exclude_patterns = [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".claude/skills/assistant (using code analysis skills)",
        "tickets/",  # Keep historical tickets as-is
        "evidence/",  # Keep historical evidence as-is
    ]

    files_processed = 0
    files_modified = 0

    for pattern in patterns:
        for file_path in Path(".").glob(pattern):
            # Skip excluded patterns
            if any(exc in str(file_path) for exc in exclude_patterns):
                continue

            files_processed += 1
            if clean_file(file_path):
                files_modified += 1
                print(f"✓ Modified: {file_path}")

    print(f"\n Summary:")
    print(f"Files processed: {files_processed}")
    print(f"Files modified: {files_modified}")


if __name__ == "__main__":
    main()
