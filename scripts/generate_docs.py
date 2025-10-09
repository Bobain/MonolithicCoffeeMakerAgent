#!/usr/bin/env python3
"""Generate API documentation with pdoc.

This script generates HTML documentation for the Coffee Maker Agent codebase.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Generate documentation."""
    # Get project root
    project_root = Path(__file__).parent.parent

    # Output directory
    output_dir = project_root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating API documentation with pdoc...")
    print(f"Output directory: {output_dir}")

    # Run pdoc
    cmd = [
        "poetry",
        "run",
        "pdoc",
        "coffee_maker/langchain_observe",
        "-o",
        str(output_dir),
        "--docformat",
        "google",
        "--search",
        "--show-source",
    ]

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=True, text=True)
        print("✅ Documentation generated successfully!")
        print(f"📚 View at: file://{output_dir}/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Documentation generation failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
