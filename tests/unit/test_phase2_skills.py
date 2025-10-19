"""
Unit tests for Phase 2 Claude Skills (US-056).

Tests all 6 Phase 2 skills:
- roadmap-health (project_manager)
- architecture-analysis (architect)
- dependency-impact (architect)
- demo-creator (assistant)
- bug-analyzer (assistant)
- security-audit (code-searcher)

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-056, US-056
"""

import json
import subprocess
from pathlib import Path


def parse_skill_output(stdout: str) -> dict:
    """Parse JSON output from skill execution.

    Skills output multiple lines (progress, etc.) followed by JSON result.
    This function extracts the JSON result block.

    Args:
        stdout: Standard output from skill execution

    Returns:
        Parsed JSON dictionary
    """
    # Look for "Result:" followed by JSON
    if "Result:" in stdout:
        json_start = stdout.index("Result:") + len("Result:")
        json_text = stdout[json_start:].strip()
        return json.loads(json_text)
    else:
        # Fallback: try last line
        output_lines = stdout.strip().split("\n")
        return json.loads(output_lines[-1])


class TestRoadmapHealthSkill:
    """Tests for roadmap-health skill (project_manager)."""

    def test_roadmap_health_execution(self):
        """Test that roadmap-health skill executes successfully."""
        skill_path = Path(".claude/skills/project-manager/roadmap-health/roadmap-health.py")
        assert skill_path.exists(), "roadmap-health.py not found"

        # Execute skill with test context
        context = {"generate_report": True}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "health_status" in output_data
        assert "blockers" in output_data
        assert "github_status" in output_data
        assert "report_path" in output_data

        # Verify health status is valid
        assert output_data["health_status"] in ["HEALTHY", "WARNING", "CRITICAL"]

    def test_roadmap_health_generates_report(self):
        """Test that roadmap-health generates a report file."""
        skill_path = Path(".claude/skills/project-manager/roadmap-health/roadmap-health.py")

        context = {"generate_report": True}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        report_path = Path(output_data["report_path"])
        assert report_path.exists(), f"Report not generated: {report_path}"

        # Verify report is not too large (synthetic = 1-2 pages)
        report_text = report_path.read_text()
        assert len(report_text) < 5000, "Report is too verbose (should be 1-2 pages)"


class TestArchitectureAnalysisSkill:
    """Tests for architecture-analysis skill (architect)."""

    def test_architecture_analysis_execution(self):
        """Test that architecture-analysis skill executes successfully."""
        skill_path = Path(".claude/skills/architect/architecture-analysis/architecture-analysis.py")
        assert skill_path.exists(), "architecture-analysis.py not found"

        context = {"scope": "coffee_maker/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=120
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "complexity_score" in output_data
        assert "recommendations" in output_data
        assert "report_path" in output_data

        # Verify complexity score is reasonable
        assert 0 <= output_data["complexity_score"] <= 100

    def test_architecture_analysis_generates_report(self):
        """Test that architecture-analysis generates a report file."""
        skill_path = Path(".claude/skills/architect/architecture-analysis/architecture-analysis.py")

        context = {"scope": "coffee_maker/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=120
        )

        assert result.returncode == 0

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        report_path = Path(output_data["report_path"])
        assert report_path.exists(), f"Report not generated: {report_path}"

        report_text = report_path.read_text()
        assert len(report_text) < 5000, "Report is too verbose (should be 1-2 pages)"


class TestDependencyImpactSkill:
    """Tests for dependency-impact skill (architect)."""

    def test_dependency_impact_execution(self):
        """Test that dependency-impact skill executes successfully."""
        skill_path = Path(".claude/skills/architect/dependency-impact/dependency-impact.py")
        assert skill_path.exists(), "dependency-impact.py not found"

        context = {"package_name": "pytest", "current_version": "7.0.0", "target_version": "8.0.0"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "breaking_changes" in output_data
        assert "migration_risk" in output_data
        assert "rollout_plan" in output_data
        assert "report_path" in output_data

        # Verify risk level is valid
        assert output_data["migration_risk"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class TestDemoCreatorSkill:
    """Tests for demo-creator skill (assistant)."""

    def test_demo_creator_execution(self):
        """Test that demo-creator skill executes successfully."""
        skill_path = Path(".claude/skills/assistant/demo-creator/demo-creator.py")
        assert skill_path.exists(), "demo-creator.py not found"

        context = {"feature_name": "User Dashboard", "url": "http://localhost:8000"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "screenshots" in output_data
        assert "narration" in output_data
        assert "demo_path" in output_data


class TestBugAnalyzerSkill:
    """Tests for bug-analyzer skill (assistant)."""

    def test_bug_analyzer_execution(self):
        """Test that bug-analyzer skill executes successfully."""
        skill_path = Path(".claude/skills/assistant/bug-analyzer/bug-analyzer.py")
        assert skill_path.exists(), "bug-analyzer.py not found"

        context = {"bug_description": "Dashboard shows incorrect data when multiple users access simultaneously"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "reproduced" in output_data
        assert "root_cause" in output_data
        assert "logs" in output_data
        assert "screenshots" in output_data
        assert "report_path" in output_data


class TestSecurityAuditSkill:
    """Tests for security-audit skill (code-searcher)."""

    def test_security_audit_execution(self):
        """Test that security-audit skill executes successfully."""
        skill_path = Path(".claude/skills/code-searcher/security-audit/security-audit.py")
        assert skill_path.exists(), "security-audit.py not found"

        context = {"scope": "coffee_maker/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=90
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "vulnerabilities" in output_data
        assert "security_score" in output_data
        assert "report_path" in output_data

        # Verify security score is in range
        assert 0 <= output_data["security_score"] <= 100

    def test_security_audit_generates_report(self):
        """Test that security-audit generates a report file."""
        skill_path = Path(".claude/skills/code-searcher/security-audit/security-audit.py")

        context = {"scope": "coffee_maker/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=90
        )

        assert result.returncode == 0

        # Parse output using helper
        output_data = parse_skill_output(result.stdout)

        report_path = Path(output_data["report_path"])
        assert report_path.exists(), f"Report not generated: {report_path}"

        report_text = report_path.read_text()
        assert len(report_text) < 5000, "Report is too verbose (should be 1-2 pages)"


class TestLangfuseTracking:
    """Tests for Langfuse skill tracking."""

    def test_skill_tracking_import(self):
        """Test that skill_tracking module can be imported."""
        from coffee_maker.langfuse_observe.skill_tracking import track_skill_execution

        assert callable(track_skill_execution)

    def test_skill_tracking_execution(self):
        """Test that skill tracking works (even without Langfuse)."""
        from coffee_maker.langfuse_observe.skill_tracking import track_skill_execution

        result = track_skill_execution(
            agent_type="project_manager",
            skill_name="roadmap-health",
            duration=5.23,
            success=True,
            context_size=1024,
            output_size=2048,
        )

        # Should return tracking info (even if Langfuse not available)
        assert "tracked" in result
        assert "agent" in result
        assert "skill" in result
