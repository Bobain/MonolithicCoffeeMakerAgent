#!/usr/bin/env python3
"""Test script for project_manager warning capabilities.

This script demonstrates how the project_manager agent can warn users
about blockers, issues, and project health concerns.
"""

import time
from coffee_maker.cli.ai_service import AIService


def main():
    """Test project_manager warning functionality."""
    print("=== Project Manager Warning System Test ===\n")

    # Initialize AI service
    service = AIService()

    # Test 1: Critical Blocker Warning
    print("Test 1: Critical Blocker Warning")
    print("-" * 50)
    notif_id = service.warn_user(
        title="🚨 BLOCKER: Technical spec review needed",
        message="US-021 (Code Refactoring) is waiting on technical spec review. "
        "code_developer cannot proceed until spec is approved. "
        "Please review docs/US_021_TECHNICAL_SPEC.md and provide feedback.",
        priority="critical",
        context={"priority": "US-021", "blocker_type": "spec_review", "days_waiting": 2},
    )
    print(f"✓ Created critical warning (ID: {notif_id})")
    print("  - Should play 'Sosumi' sound (macOS)")
    print()
    time.sleep(2)

    # Test 2: High Priority Warning
    print("Test 2: High Priority Warning - Dependency Conflict")
    print("-" * 50)
    notif_id = service.warn_user(
        title="⚠️ WARNING: Dependency conflict detected",
        message="US-032 depends on US-031 which is not yet complete. "
        "Implementing US-032 now will require rework when US-031 changes. "
        "Recommend completing US-031 first to avoid technical debt.",
        priority="high",
        context={"priority": "US-032", "blocked_by": "US-031", "risk_level": "high"},
    )
    print(f"✓ Created high priority warning (ID: {notif_id})")
    print("  - Should play 'Glass' sound (macOS)")
    print()
    time.sleep(2)

    # Test 3: Normal Warning - Project Health
    print("Test 3: Normal Warning - Project Health Concern")
    print("-" * 50)
    notif_id = service.warn_user(
        title="📊 Project velocity declining",
        message="Completed priorities per week has dropped from 2.5 to 1.2 (52% decrease). "
        "This trend suggests potential issues with: "
        "1) Priority complexity increasing, "
        "2) Code quality issues requiring more time, or "
        "3) External dependencies causing delays. "
        "\n\nRecommendations: "
        "\n- Review recent priorities for common bottlenecks"
        "\n- Consider breaking down larger priorities"
        "\n- Check if code_developer is encountering blockers",
        priority="normal",
        context={
            "metric": "velocity",
            "previous_velocity": 2.5,
            "current_velocity": 1.2,
            "trend": "declining",
            "decline_percentage": 52,
        },
    )
    print(f"✓ Created normal warning (ID: {notif_id})")
    print("  - Should play 'Pop' sound (macOS)")
    print()
    time.sleep(2)

    # Test 4: Silent Warning (no sound)
    print("Test 4: Silent Warning (Low Priority)")
    print("-" * 50)
    notif_id = service.warn_user(
        title="💡 Suggestion: Consider adding integration tests",
        message="Current test coverage is good (85%), but integration tests would "
        "provide additional confidence for multi-component features. "
        "Consider adding integration tests for: "
        "\n- Daemon + NotificationDB interaction"
        "\n- AIService + ROADMAP parser integration"
        "\n- End-to-end priority implementation flow",
        priority="low",
        context={"metric": "test_coverage", "current": 85, "suggestion_type": "improvement"},
    )
    print(f"✓ Created low priority suggestion (ID: {notif_id})")
    print("  - Should play 'Pop' sound (macOS)")
    print()

    print("\n=== Test Complete ===")
    print("\nCheck notifications:")
    print("  poetry run project-manager notifications")
    print("\nYou should have heard 4 sounds (unless sounds are disabled):")
    print("  1. Sosumi (critical)")
    print("  2. Glass (high)")
    print("  3. Pop (normal)")
    print("  4. Pop (low)")


if __name__ == "__main__":
    main()
