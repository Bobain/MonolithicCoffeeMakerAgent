"""
Hello World Skill - Example skill for Claude Skills infrastructure.

Simple skill that demonstrates skill execution.

Author: code_developer
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import json
import sys
from typing import Dict, Any


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute hello world skill.

    Args:
        context: Context data containing optional 'name' field

    Returns:
        Dict with 'message' field containing greeting
    """
    name = context.get("name", "World")
    message = f"Hello, {name}!"

    print(f"Hello World Skill executed: {message}")

    return {"message": message}


if __name__ == "__main__":
    # Load context from stdin or file
    if not sys.stdin.isatty():
        context = json.load(sys.stdin)
    else:
        # Default context for testing
        context = {"name": "World"}

    result = main(context)
    print(json.dumps(result, indent=2))
