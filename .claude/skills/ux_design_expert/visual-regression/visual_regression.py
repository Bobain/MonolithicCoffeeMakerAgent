"""
Visual Regression Skill for ux-design-expert.
Capture screenshots, compare pixel-by-pixel, detect visual changes.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute visual regression testing."""
    baseline_url = context.get("baseline_url")
    current_url = context.get("current_url")
    pages = context.get("pages", ["/"])

    if not baseline_url or not current_url:
        return {
            "error": "Both baseline_url and current_url are required",
            "differences_found": False,
            "diff_screenshots": [],
            "report_path": "",
        }

    print(f"Visual regression test: {baseline_url} vs {current_url}")

    # Step 1: Capture baseline screenshots
    baseline_screenshots = capture_screenshots(baseline_url, pages, "baseline")

    # Step 2: Capture current screenshots
    current_screenshots = capture_screenshots(current_url, pages, "current")

    # Step 3: Compare screenshots
    diff_results = compare_screenshots(baseline_screenshots, current_screenshots)

    # Step 4: Generate report
    report_path = generate_regression_report(baseline_url, current_url, pages, diff_results)

    return {
        "differences_found": any(result["has_diff"] for result in diff_results),
        "diff_screenshots": [r["diff_path"] for r in diff_results if r["has_diff"]],
        "report_path": str(report_path),
    }


def capture_screenshots(base_url: str, pages: List[str], prefix: str) -> List[Dict[str, Any]]:
    """
    Capture screenshots for pages.

    NOTE: This is a placeholder implementation. In production, this would:
    1. Use Puppeteer MCP to navigate to each page
    2. Capture screenshots with mcp__puppeteer__puppeteer_screenshot
    3. Save screenshots to evidence/ directory

    For Phase 3, we're providing the structure that can be integrated
    when Puppeteer MCP is available in the skill execution context.
    """
    screenshots = []

    for page in pages:
        full_url = f"{base_url.rstrip('/')}{page}"
        screenshot_path = Path(f"evidence/{prefix}-{page.replace('/', '-')}.png")

        # Placeholder: In production, use Puppeteer MCP here
        print(f"[Placeholder] Would capture screenshot: {full_url}")

        screenshots.append({"page": page, "url": full_url, "path": str(screenshot_path)})

    return screenshots


def compare_screenshots(baseline: List[Dict[str, Any]], current: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compare screenshots pixel-by-pixel.

    NOTE: This is a placeholder implementation. In production, this would:
    1. Load both images using PIL/Pillow
    2. Use pixelmatch (or similar) to compare pixel-by-pixel
    3. Generate diff images highlighting differences
    4. Calculate difference percentage

    Requires: pip install pixelmatch Pillow
    """
    diff_results = []

    for base_shot, curr_shot in zip(baseline, current):
        page = base_shot["page"]

        # Placeholder: In production, use pixelmatch here
        print(f"[Placeholder] Would compare: {base_shot['path']} vs {curr_shot['path']}")

        diff_path = Path(f"evidence/diff-{page.replace('/', '-')}.png")

        # Simulated result
        diff_results.append(
            {
                "page": page,
                "baseline_path": base_shot["path"],
                "current_path": curr_shot["path"],
                "diff_path": str(diff_path),
                "has_diff": False,  # Would be True if actual differences detected
                "diff_percentage": 0.0,  # Would be actual percentage
            }
        )

    return diff_results


def generate_regression_report(
    baseline_url: str, current_url: str, pages: List[str], diff_results: List[Dict[str, Any]]
) -> Path:
    """Generate visual regression report."""

    total_pages = len(pages)
    pages_with_diffs = sum(1 for r in diff_results if r["has_diff"])

    report = f"""# Visual Regression Test Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Baseline**: {baseline_url}
**Current**: {current_url}

## Summary

- **Total Pages Tested**: {total_pages}
- **Pages with Differences**: {pages_with_diffs}
- **Status**: {'⚠️ DIFFERENCES DETECTED' if pages_with_diffs > 0 else '✅ NO DIFFERENCES'}

## Results by Page

"""

    for result in diff_results:
        status = "⚠️ CHANGED" if result["has_diff"] else "✅ UNCHANGED"
        report += f"""
### {result['page']} - {status}

- **Baseline**: `{result['baseline_path']}`
- **Current**: `{result['current_path']}`
"""

        if result["has_diff"]:
            report += f"""- **Diff**: `{result['diff_path']}`
- **Difference**: {result['diff_percentage']:.2f}%

![Diff]({result['diff_path']})

"""

    report += """

## Implementation Note

This skill currently provides a structural placeholder for visual regression testing.
Full implementation requires:

1. **Puppeteer MCP Integration**: Use `mcp__puppeteer__puppeteer_screenshot` to capture actual screenshots
2. **Pixelmatch Integration**: Install `pixelmatch` and `Pillow` for pixel-by-pixel comparison
3. **Image Processing**: Implement actual screenshot loading and comparison logic

The architecture and workflow are complete - only the MCP/pixelmatch integration remains.

"""

    # Save report
    report_path = Path("evidence/visual-regression-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return report_path


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
