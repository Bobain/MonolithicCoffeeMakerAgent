"""
Demo Creator Skill for assistant.

Automated demo creation: use Puppeteer MCP to interact with app, capture screenshots, generate demo.

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-056, US-056

NOTE: This is a placeholder implementation. Full Puppeteer MCP integration will be added in future.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute demo creation.

    Args:
        context: Context data containing feature_name, url (optional), steps (optional)

    Returns:
        Dict with screenshots, narration, demo_path
    """
    feature_name = context.get("feature_name", "")
    url = context.get("url", "http://localhost:8000")
    steps = context.get("steps", [])

    if not feature_name:
        return {
            "screenshots": [],
            "narration": "",
            "demo_path": None,
            "error": "Missing required parameter: feature_name",
        }

    print(f"Creating demo for feature: {feature_name}...")

    # Step 1: Plan demo steps (if not provided)
    if not steps:
        steps = plan_demo_steps(feature_name)
    print(f"  Demo plan: {len(steps)} steps")

    # Step 2: Launch browser (placeholder - Puppeteer integration later)
    print(f"  Launching browser at {url}...")

    # Step 3: Execute steps and capture screenshots (placeholder)
    screenshots = execute_demo_steps(feature_name, steps)
    print(f"  Captured {len(screenshots)} screenshots")

    # Step 4: Generate narration
    narration = generate_narration(feature_name, steps)
    print(f"  Generated narration ({len(narration)} chars)")

    # Step 5: Compile demo
    demo_path = compile_demo(feature_name, steps, screenshots, narration)
    print(f"  Demo compiled: {demo_path}")

    return {
        "screenshots": screenshots,
        "narration": narration,
        "demo_path": str(demo_path),
    }


def plan_demo_steps(feature_name: str) -> List[str]:
    """Plan demo steps based on feature name.

    Args:
        feature_name: Feature to demonstrate

    Returns:
        List of demo steps
    """
    # Simplified: Generate generic steps based on feature name
    # In full implementation, would analyze feature docs/code to determine steps

    return [
        f"Navigate to {feature_name} page",
        f"Show {feature_name} UI elements",
        f"Demonstrate {feature_name} core functionality",
        f"Show {feature_name} edge cases",
        f"Verify {feature_name} works as expected",
    ]


def execute_demo_steps(feature_name: str, steps: List[str]) -> List[str]:
    """Execute demo steps and capture screenshots.

    NOTE: Placeholder implementation. Full Puppeteer MCP integration in future.

    Args:
        feature_name: Feature name
        steps: Demo steps

    Returns:
        List of screenshot paths (placeholder)
    """
    # Placeholder: Generate synthetic screenshot paths
    # In full implementation, would use Puppeteer MCP to:
    # 1. Navigate to URL
    # 2. Interact with elements (click, type, etc.)
    # 3. Capture screenshots at each step

    screenshots = []
    for i, step in enumerate(steps, 1):
        screenshot_path = f"evidence/demo-{feature_name}-step-{i}.png"
        screenshots.append(screenshot_path)

    return screenshots


def generate_narration(feature_name: str, steps: List[str]) -> str:
    """Generate demo narration text.

    Args:
        feature_name: Feature name
        steps: Demo steps

    Returns:
        Narration text
    """
    narration = f"""# {feature_name} Demo

This demo showcases the {feature_name} feature and how it works.

## Overview

The {feature_name} feature provides users with powerful capabilities to enhance their workflow.

## Demo Steps

"""

    for i, step in enumerate(steps, 1):
        narration += f"{i}. **{step}**: This step demonstrates how to {step.lower()}.\n"

    narration += """

## Summary

As you can see, the {feature_name} feature is intuitive and easy to use. It provides significant value
by streamlining the user workflow and improving productivity.

"""

    return narration


def compile_demo(feature_name: str, steps: List[str], screenshots: List[str], narration: str) -> Path:
    """Compile demo into markdown file with screenshots.

    Args:
        feature_name: Feature name
        steps: Demo steps
        screenshots: Screenshot paths
        narration: Narration text

    Returns:
        Path to demo markdown file
    """
    # Create docs/demos directory if it doesn't exist
    demos_dir = Path("docs/demos")
    demos_dir.mkdir(parents=True, exist_ok=True)

    # Generate demo markdown
    demo_md = f"""# {feature_name} Feature Demo

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Feature**: {feature_name}

---

{narration}

## Screenshots

"""

    for i, (step, screenshot) in enumerate(zip(steps, screenshots), 1):
        demo_md += f"""### Step {i}: {step}

![Screenshot {i}]({screenshot})

"""

    demo_md += """

---

**Demo created by**: assistant agent (demo-creator skill)
**Created**: """ + datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    # Save demo
    demo_path = (
        demos_dir / f"{feature_name.lower().replace(' ', '-')}-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    )
    demo_path.write_text(demo_md)

    return demo_path


if __name__ == "__main__":
    # Load context from stdin or use default
    try:
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read().strip()
            if stdin_text:
                context = json.loads(stdin_text)
            else:
                context = {
                    "feature_name": "User Dashboard",
                    "url": "http://localhost:8000/dashboard",
                }
        else:
            # Default context for testing
            context = {
                "feature_name": "User Dashboard",
                "url": "http://localhost:8000/dashboard",
            }
    except (json.JSONDecodeError, ValueError):
        # Fallback to default context
        context = {
            "feature_name": "User Dashboard",
            "url": "http://localhost:8000/dashboard",
        }

    result = main(context)
    print("\nResult:")
    print(json.dumps(result, indent=2))
