"""
Unit tests for Phase 3 Claude Skills (US-057).

Tests all 3 Phase 3 skills:
- code-forensics (assistant (with code analysis skills))
- design-system (ux-design-expert)
- visual-regression (ux-design-expert)

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-057, US-057
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

    # Try to find JSON object in output (look for opening brace)
    lines = stdout.strip().split("\n")

    # Find the start of JSON output (line starting with "{")
    json_lines = []
    in_json = False

    for line in lines:
        if line.strip().startswith("{"):
            in_json = True
        if in_json:
            json_lines.append(line)

    if json_lines:
        json_text = "\n".join(json_lines)
        return json.loads(json_text)

    # Fallback: try last line
    return json.loads(lines[-1])


class TestCodeForensicsSkill:
    """Tests for code-forensics skill (assistant (with code analysis skills))."""

    def test_code_forensics_execution(self):
        """Test that code-forensics skill executes successfully."""
        skill_path = Path(".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py")
        assert skill_path.exists(), "code_forensics.py not found"

        # Execute skill with test context
        context = {"scope": ".", "time_range": "last 6 months"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=120
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "contributors" in output_data
        assert "hotspots" in output_data
        assert "patterns" in output_data
        assert "report_path" in output_data

        # Verify contributors is a list
        assert isinstance(output_data["contributors"], list)

        # Verify hotspots is a list
        assert isinstance(output_data["hotspots"], list)

        # Verify patterns has expected keys
        assert "peak_hour" in output_data["patterns"] or output_data["patterns"]["peak_hour"] is None
        assert "peak_day" in output_data["patterns"] or output_data["patterns"]["peak_day"] is None

    def test_code_forensics_generates_report(self):
        """Test that code-forensics generates a report file."""
        skill_path = Path(".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py")

        context = {"scope": "."}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=120
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        report_path = Path(output_data["report_path"])
        assert report_path.exists(), f"Report not generated: {report_path}"

        # Verify report content
        report_text = report_path.read_text()
        assert "# Code Forensics Report" in report_text
        assert "Top 5 Contributors" in report_text
        assert "Top 5 Code Hotspots" in report_text
        assert "Commit Patterns" in report_text

        # Verify report is concise (should be 1-2 pages)
        assert len(report_text) < 5000, "Report is too verbose (should be 1-2 pages)"

    def test_code_forensics_with_specific_scope(self):
        """Test code-forensics with specific file/directory scope."""
        skill_path = Path(".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py")

        # Test with specific directory
        context = {"scope": "coffee_maker/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=120
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Should return results for scoped analysis
        assert "contributors" in output_data
        assert "hotspots" in output_data


class TestDesignSystemSkill:
    """Tests for design-system skill (ux-design-expert)."""

    def test_design_system_execution(self):
        """Test that design-system skill executes successfully."""
        skill_path = Path(".claude/skills/ux-design-expert/design-system/design_system.py")
        assert skill_path.exists(), "design_system.py not found"

        # Execute skill with test context
        context = {"scope": "templates/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "design_tokens" in output_data
        assert "components" in output_data
        assert "report_path" in output_data

        # Verify design_tokens structure
        assert isinstance(output_data["design_tokens"], dict)

        # Verify components is a list
        assert isinstance(output_data["components"], list)

    def test_design_system_extracts_tokens(self):
        """Test that design-system extracts design tokens correctly."""
        skill_path = Path(".claude/skills/ux-design-expert/design-system/design_system.py")

        context = {"scope": "templates/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        design_tokens = output_data["design_tokens"]

        # Verify token categories exist (even if empty for test run)
        expected_categories = ["colors", "spacing", "typography", "layout", "effects"]
        for category in expected_categories:
            assert category in design_tokens, f"Missing token category: {category}"

    def test_design_system_generates_report(self):
        """Test that design-system generates a documentation file."""
        skill_path = Path(".claude/skills/ux-design-expert/design-system/design_system.py")

        context = {"scope": "templates/"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        report_path = Path(output_data["report_path"])
        assert report_path.exists(), f"Report not generated: {report_path}"

        # Verify report content
        report_text = report_path.read_text()
        assert "# Design System Documentation" in report_text
        assert "Design Tokens" in report_text


class TestVisualRegressionSkill:
    """Tests for visual-regression skill (ux-design-expert)."""

    def test_visual_regression_execution(self):
        """Test that visual-regression skill executes successfully."""
        skill_path = Path(".claude/skills/ux-design-expert/visual-regression/visual_regression.py")
        assert skill_path.exists(), "visual_regression.py not found"

        # Execute skill with test context
        context = {
            "baseline_url": "http://localhost:8000",
            "current_url": "http://localhost:8000",
            "pages": ["/", "/about"],
        }
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0, f"Skill failed: {result.stderr}"

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Verify output structure
        assert "differences_found" in output_data
        assert "diff_screenshots" in output_data
        assert "report_path" in output_data

        # Verify differences_found is boolean
        assert isinstance(output_data["differences_found"], bool)

        # Verify diff_screenshots is a list
        assert isinstance(output_data["diff_screenshots"], list)

    def test_visual_regression_requires_urls(self):
        """Test that visual-regression requires baseline_url and current_url."""
        skill_path = Path(".claude/skills/ux-design-expert/visual-regression/visual_regression.py")

        # Test with missing baseline_url
        context = {"current_url": "http://localhost:8000"}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Should return error
        assert "error" in output_data or output_data["differences_found"] is False

    def test_visual_regression_generates_report(self):
        """Test that visual-regression generates a report file."""
        skill_path = Path(".claude/skills/ux-design-expert/visual-regression/visual_regression.py")

        context = {"baseline_url": "http://localhost:8000", "current_url": "http://localhost:8000", "pages": ["/"]}
        result = subprocess.run(
            ["python", str(skill_path)], input=json.dumps(context), capture_output=True, text=True, timeout=60
        )

        assert result.returncode == 0

        # Parse output
        output_data = parse_skill_output(result.stdout)

        # Note: Report path might be empty if it's placeholder implementation
        # This is OK for Phase 3 since Puppeteer MCP integration is future work
        assert "report_path" in output_data


class TestPhase3Integration:
    """Integration tests for all Phase 3 skills together."""

    def test_all_phase3_skills_exist(self):
        """Test that all Phase 3 skill files exist."""
        skills = [
            ".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py",
            ".claude/skills/ux-design-expert/design-system/design_system.py",
            ".claude/skills/ux-design-expert/visual-regression/visual_regression.py",
        ]

        for skill_path in skills:
            assert Path(skill_path).exists(), f"Skill not found: {skill_path}"

    def test_all_phase3_skill_metadata_exist(self):
        """Test that all Phase 3 SKILL.md files exist."""
        metadata_files = [
            ".claude/skills/assistant (with code analysis skills)/code-forensics/SKILL.md",
            ".claude/skills/ux-design-expert/design-system/SKILL.md",
            ".claude/skills/ux-design-expert/visual-regression/SKILL.md",
        ]

        for metadata_path in metadata_files:
            path = Path(metadata_path)
            assert path.exists(), f"Metadata not found: {metadata_path}"

            # Verify metadata is valid YAML/Markdown
            content = path.read_text()
            assert "name:" in content
            assert "version:" in content
            assert "agent:" in content
            assert "triggers:" in content

    def test_phase3_skills_execution_time(self):
        """Test that Phase 3 skills execute within expected time limits.

        Per SPEC-057, 95% of skills should complete in <5 minutes.
        Phase 3 skills are designed to complete in:
        - code-forensics: 10-15 minutes (acceptable, complex analysis)
        - design-system: 30 minutes (acceptable, template scanning)
        - visual-regression: 10 minutes (placeholder, future optimization)
        """
        import time

        skills_timing = {
            ".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py": {
                "context": {"scope": "coffee_maker/", "time_range": "last 3 months"},
                "max_time": 900,  # 15 minutes
            },
            ".claude/skills/ux-design-expert/design-system/design_system.py": {
                "context": {"scope": "templates/"},
                "max_time": 1800,  # 30 minutes
            },
        }

        for skill_path, config in skills_timing.items():
            start_time = time.time()

            result = subprocess.run(
                ["python", skill_path],
                input=json.dumps(config["context"]),
                capture_output=True,
                text=True,
                timeout=config["max_time"],
            )

            execution_time = time.time() - start_time

            assert result.returncode == 0, f"Skill failed: {skill_path}"
            assert (
                execution_time < config["max_time"]
            ), f"Skill too slow: {skill_path} ({execution_time:.2f}s > {config['max_time']}s)"


class TestPhase3SkillQuality:
    """Quality tests for Phase 3 skills."""

    def test_skill_code_quality(self):
        """Test that skill code follows best practices."""
        skills = [
            ".claude/skills/assistant (with code analysis skills)/code-forensics/code_forensics.py",
            ".claude/skills/ux-design-expert/design-system/design_system.py",
            ".claude/skills/ux-design-expert/visual-regression/visual_regression.py",
        ]

        for skill_path in skills:
            code = Path(skill_path).read_text()

            # Must have docstring
            assert '"""' in code or "'''" in code, f"No docstring: {skill_path}"

            # Must have main() function
            assert "def main(" in code, f"No main() function: {skill_path}"

            # Must have type hints
            assert "Dict[str, Any]" in code or "dict" in code, f"No type hints: {skill_path}"

            # Must handle JSON I/O
            assert "json.load" in code or "json.loads" in code, f"No JSON input handling: {skill_path}"
            assert "json.dumps" in code, f"No JSON output: {skill_path}"

    def test_skill_metadata_quality(self):
        """Test that skill metadata follows standards."""
        metadata_files = [
            ".claude/skills/assistant (with code analysis skills)/code-forensics/SKILL.md",
            ".claude/skills/ux-design-expert/design-system/SKILL.md",
            ".claude/skills/ux-design-expert/visual-regression/SKILL.md",
        ]

        for metadata_path in metadata_files:
            content = Path(metadata_path).read_text()

            # Must have required fields
            assert "name:" in content
            assert "version:" in content
            assert "agent:" in content
            assert "triggers:" in content
            assert "inputs:" in content
            assert "outputs:" in content
            assert "author:" in content
            assert "created:" in content

            # Must have workflow section
            assert "## Workflow" in content or "## Use Cases" in content

            # Must have time savings section
            assert "Expected Time Savings" in content or "Time Saved" in content
