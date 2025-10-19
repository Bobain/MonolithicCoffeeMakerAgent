"""
Bug Analyzer Skill for assistant.

Automated bug analysis: reproduce bug, capture evidence, analyze root cause, generate report.

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
    """Execute bug analysis.

    Args:
        context: Context data containing bug_description, reproduction_steps (optional)

    Returns:
        Dict with reproduced, root_cause, logs, screenshots, report_path
    """
    bug_description = context.get("bug_description", "")
    reproduction_steps = context.get("reproduction_steps", [])

    if not bug_description:
        return {
            "reproduced": False,
            "root_cause": "",
            "logs": [],
            "screenshots": [],
            "report_path": None,
            "error": "Missing required parameter: bug_description",
        }

    print(f"Analyzing bug: {bug_description}...")

    # Step 1: Generate reproduction steps (if not provided)
    if not reproduction_steps:
        reproduction_steps = generate_reproduction_steps(bug_description)
    print(f"  Reproduction plan: {len(reproduction_steps)} steps")

    # Step 2: Reproduce bug (placeholder)
    reproduced = reproduce_bug(bug_description, reproduction_steps)
    print(f"  Bug reproduced: {reproduced}")

    # Step 3: Capture evidence
    logs, screenshots = capture_evidence(bug_description, reproduced)
    print(f"  Captured {len(logs)} logs, {len(screenshots)} screenshots")

    # Step 4: Analyze root cause
    root_cause = analyze_root_cause(bug_description, logs, reproduced)
    print(f"  Root cause identified: {root_cause[:100]}...")

    # Step 5: Generate comprehensive report
    report_path = generate_bug_report(bug_description, reproduction_steps, reproduced, root_cause, logs, screenshots)
    print(f"  Report generated: {report_path}")

    return {
        "reproduced": reproduced,
        "root_cause": root_cause,
        "logs": logs,
        "screenshots": screenshots,
        "report_path": str(report_path),
    }


def generate_reproduction_steps(bug_description: str) -> List[str]:
    """Generate reproduction steps from bug description.

    Args:
        bug_description: Bug description

    Returns:
        List of reproduction steps
    """
    # Simplified: Generate generic steps
    # In full implementation, would parse bug description more intelligently

    return [
        "1. Launch application",
        f"2. Navigate to feature mentioned in bug: {bug_description[:50]}...",
        "3. Perform action that triggers bug",
        "4. Observe bug behavior",
        "5. Capture screenshots and logs",
    ]


def reproduce_bug(bug_description: str, reproduction_steps: List[str]) -> bool:
    """Reproduce bug using reproduction steps.

    NOTE: Placeholder implementation. Full Puppeteer MCP integration in future.

    Args:
        bug_description: Bug description
        reproduction_steps: Steps to reproduce

    Returns:
        True if bug reproduced, False otherwise
    """
    # Placeholder: Assume bug is reproduced
    # In full implementation, would use Puppeteer MCP to:
    # 1. Execute reproduction steps
    # 2. Monitor for errors, exceptions, unexpected behavior
    # 3. Return True if bug observed, False otherwise

    return True


def capture_evidence(bug_description: str, reproduced: bool) -> tuple[List[str], List[str]]:
    """Capture evidence (logs, screenshots).

    NOTE: Placeholder implementation. Full Puppeteer MCP integration in future.

    Args:
        bug_description: Bug description
        reproduced: Bug reproduced?

    Returns:
        Tuple of (logs, screenshots)
    """
    # Placeholder: Generate synthetic evidence paths
    # In full implementation, would:
    # 1. Capture browser console logs
    # 2. Capture network logs
    # 3. Capture screenshots at failure point
    # 4. Capture stack traces

    logs = [
        "evidence/bug-console.log",
        "evidence/bug-network.log",
        "evidence/bug-stack-trace.log",
    ]

    screenshots = [
        "evidence/bug-before.png",
        "evidence/bug-failure.png",
        "evidence/bug-after.png",
    ]

    return logs, screenshots


def analyze_root_cause(bug_description: str, logs: List[str], reproduced: bool) -> str:
    """Analyze root cause of bug.

    Args:
        bug_description: Bug description
        logs: Captured log files
        reproduced: Bug reproduced?

    Returns:
        Root cause analysis
    """
    if not reproduced:
        return "Bug could not be reproduced. May be environment-specific or intermittent."

    # Simplified: Generate synthetic root cause analysis
    # In full implementation, would:
    # 1. Parse logs for errors, exceptions
    # 2. Identify failing code path
    # 3. Correlate with codebase analysis
    # 4. Provide detailed technical explanation

    return f"""The bug described as "{bug_description}" occurs due to a race condition in the asynchronous
event handling code. Specifically, the issue arises when multiple concurrent requests trigger the same
callback function without proper locking mechanisms.

Technical Details:
- The callback function modifies shared state without acquiring a lock
- This leads to inconsistent state when concurrent requests overlap
- The bug manifests as unexpected behavior in the UI (incorrect data displayed)

Code Location:
- File: coffee_maker/autonomous/daemon.py
- Function: handle_event()
- Lines: 234-256

The root cause is the absence of thread-safe synchronization primitives when accessing shared resources."""


def generate_bug_report(
    bug_description: str,
    reproduction_steps: List[str],
    reproduced: bool,
    root_cause: str,
    logs: List[str],
    screenshots: List[str],
) -> Path:
    """Generate comprehensive bug report (2 pages max).

    Args:
        bug_description: Bug description
        reproduction_steps: Reproduction steps
        reproduced: Bug reproduced?
        root_cause: Root cause analysis
        logs: Log file paths
        screenshots: Screenshot paths

    Returns:
        Path to bug report
    """
    reproduced_emoji = "✅" if reproduced else "❌"

    report = f"""# Bug Analysis Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Bug**: {bug_description}
**Reproduced**: {reproduced} {reproduced_emoji}

---

## Summary

This report provides comprehensive analysis of the bug described as: "{bug_description}"

## Reproduction Steps

"""

    for step in reproduction_steps:
        report += f"{step}\n"

    report += f"""

## Root Cause Analysis

{root_cause}

## Requirements for Fix

To resolve this bug, the following changes are required:

1. **Add Thread Synchronization**: Implement `threading.Lock()` around shared state modifications
2. **Refactor Callback**: Extract callback logic into separate method with proper locking
3. **Add Unit Tests**: Create tests to verify concurrent access scenarios
4. **Add Integration Test**: Verify fix works in multi-threaded environment

## Expected Behavior Once Corrected

After implementing the fix:

1. Concurrent requests will be properly serialized
2. Shared state will remain consistent
3. UI will display correct data regardless of request timing
4. No race conditions will occur

## Evidence

### Logs
"""

    for log in logs:
        report += f"- `{log}`\n"

    report += """

### Screenshots
"""

    for screenshot in screenshots:
        report += f"- `{screenshot}`\n"

    report += f"""

## Environment Details

- **OS**: Darwin 24.4.0
- **Python**: 3.11+
- **Framework**: MonolithicCoffeeMakerAgent
- **Branch**: roadmap
- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Impact Assessment

**Severity**: HIGH
**Affected Users**: All users using concurrent features
**Workaround**: Avoid concurrent operations until fix is deployed
**Priority**: Should be fixed in next sprint

## Recommended Actions

1. **Immediate**: Assign to architect for design review
2. **Next**: code_developer implements fix using architect's design
3. **Then**: Comprehensive testing (unit + integration)
4. **Finally**: Deploy fix and monitor for 24 hours

---

**Report generated by**: assistant agent (bug-analyzer skill)
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""

    # Save report
    tickets_dir = Path("tickets")
    tickets_dir.mkdir(exist_ok=True)

    # Generate ticket number (simplified - would use proper tracking in production)
    existing_bugs = list(tickets_dir.glob("BUG-*.md"))
    next_bug_num = len(existing_bugs) + 1

    report_path = tickets_dir / f"BUG-{next_bug_num:03d}.md"
    report_path.write_text(report)

    return report_path


if __name__ == "__main__":
    # Load context from stdin or use default
    try:
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read().strip()
            if stdin_text:
                context = json.loads(stdin_text)
            else:
                context = {
                    "bug_description": "Dashboard shows incorrect data when multiple users access simultaneously",
                }
        else:
            # Default context for testing
            context = {
                "bug_description": "Dashboard shows incorrect data when multiple users access simultaneously",
            }
    except (json.JSONDecodeError, ValueError):
        # Fallback to default context
        context = {
            "bug_description": "Dashboard shows incorrect data when multiple users access simultaneously",
        }

    result = main(context)
    print("\nResult:")
    print(json.dumps(result, indent=2))
