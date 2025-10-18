#!/usr/bin/env python3
"""Pre-commit hook to check for unapproved dependencies.

This script scans pyproject.toml for dependencies that are not in the
pre-approved list (SPEC-070). It blocks commits with unapproved dependencies
and provides guidance on the approval process.

Usage:
    # Run manually
    python scripts/check_dependencies.py

    # Run via pre-commit (automatically)
    git commit -m "Add dependency"
    # → Pre-commit hook runs check_dependencies.py
    # → Blocks commit if unapproved dependencies found

Exit Codes:
    0: All dependencies approved
    1: Unapproved dependencies found (blocks commit)

See: docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coffee_maker.utils.dependency_checker import DependencyChecker


def main() -> int:
    """Check pyproject.toml for unapproved dependencies.

    Returns:
        int: 0 if all dependencies approved, 1 otherwise
    """
    checker = DependencyChecker()
    unapproved = checker.check_pyproject_toml()

    if unapproved:
        print("\n" + "=" * 70)
        print("❌ DEPENDENCY CHECK FAILED")
        print("=" * 70)
        print("\nFound unapproved dependencies in pyproject.toml:\n")

        for package in unapproved:
            if "(BANNED)" in package:
                package_name = package.replace(" (BANNED)", "")
                print(f"   🚫 {package_name} (BANNED)")
                reason = checker.get_ban_reason(package_name)
                alternatives = checker.get_alternatives(package_name)
                print(f"      Reason: {reason}")
                if alternatives:
                    print(f"      Alternatives: {', '.join(alternatives)}")
            else:
                print(f"   ⚠️  {package} (NEEDS REVIEW)")

        print("\n" + "-" * 70)
        print("💡 SOLUTIONS:")
        print("-" * 70)
        print()
        print("1. PRE-APPROVED packages (auto-add, no user approval):")
        print(f"   - {checker.get_pre_approved_count()} packages are pre-approved")
        print("   - See: docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md")
        print()
        print("2. NEEDS REVIEW packages:")
        print("   - Delegate to architect for evaluation")
        print("   - architect uses dependency-conflict-resolver skill")
        print("   - User approval required (20-30 min process)")
        print()
        print("3. BANNED packages:")
        print("   - Use suggested alternatives (pre-approved)")
        print("   - Banned due to: GPL license, unmaintained, security issues")
        print()
        print("4. Check specific package:")
        print("   poetry run project-manager check-dependency <package-name>")
        print()
        print("=" * 70)

        return 1

    # All dependencies approved
    print("✅ All dependencies are approved")
    print(f"   Pre-approved: {checker.get_pre_approved_count()} packages")
    print(f"   Banned: {checker.get_banned_count()} packages")

    return 0


if __name__ == "__main__":
    sys.exit(main())
