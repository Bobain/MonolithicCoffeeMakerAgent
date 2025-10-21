"""Daemon health check tests - manual tests only.

These tests require ANTHROPIC_API_KEY and verify daemon initialization.
They are excluded from CI/CD and must be run manually.

Usage:
    pytest manual_tests/test_daemon_health.py -v
"""

import pytest
from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.autonomous.roadmap_parser import RoadmapParser


class TestDaemonHealthCheck:
    """Health check tests for daemon - requires ANTHROPIC_API_KEY."""

    def test_daemon_can_initialize(self):
        """Verify daemon can be initialized with default settings.

        Requires: ANTHROPIC_API_KEY environment variable

        This test verifies that:
        - DevDaemon can be created with auto_approve=True
        - Daemon initializes without errors
        - No exceptions are raised during initialization
        """
        daemon = DevDaemon(roadmap_path="docs/roadmap/ROADMAP.md", auto_approve=True)
        assert daemon is not None
        print("✅ Daemon initialized successfully")

    def test_roadmap_parsing(self):
        """Verify ROADMAP can be parsed correctly.

        This test verifies that:
        - RoadmapParser can read ROADMAP.md
        - Priorities are extracted successfully
        - At least one priority exists in the ROADMAP
        """
        parser = RoadmapParser("docs/roadmap/ROADMAP.md")
        priorities = parser.get_all_priorities()
        assert isinstance(priorities, list)
        assert len(priorities) > 0
        print(f"✅ Found {len(priorities)} priorities in ROADMAP")

    def test_daemon_no_infinite_loop_patterns(self):
        """Verify daemon doesn't have infinite loop patterns.

        This is a placeholder for daemon health verification.
        The actual check is in scripts/check_daemon_health.py
        """
        # This would run the health check script if it exists
        from pathlib import Path

        health_script = Path("scripts/check_daemon_health.py")
        if health_script.exists():
            # Run the health check script
            import subprocess

            result = subprocess.run(["python", str(health_script)], capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, f"Health check failed: {result.stderr}"
            print("✅ No infinite loop patterns detected")
        else:
            pytest.skip("Health check script not found")
