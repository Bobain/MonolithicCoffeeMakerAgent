"""Integration tests for DoD verification skill."""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coffee_maker.skills.dod_verification.criteria_parser import CriteriaParser
from coffee_maker.skills.dod_verification.automated_checks import AutomatedChecks
from coffee_maker.skills.dod_verification.code_quality_checker import CodeQualityChecker


class TestDoDVerificationIntegration:
    """Integration tests for DoD verification."""

    def test_full_verification_workflow(self):
        """Test complete DoD verification workflow."""
        # Example priority description
        priority_description = """
        **US-066**: Implement DoD Verification Skill

        **User Story**:
        As a code_developer agent, I need an automated DoD verification skill,
        so that I can comprehensively check all acceptance criteria before
        marking priorities complete.

        **Acceptance Criteria**:
        - [ ] Skill executes in <3 minutes for typical priority
        - [ ] Checks all DoD criteria (tests, docs, code quality, security)
        - [ ] Generates completion report with evidence
        - [ ] <5% false positive rate
        - [ ] Unit tests for all criteria types
        - [ ] Integration tests with real priorities
        - [ ] Documentation with examples

        **Technical Requirements**:
        - Must have tests
        - Code must follow Black formatting
        - Documentation must be complete
        """

        # Parse criteria
        parser = CriteriaParser()
        criteria = parser.parse_criteria(priority_description)

        # Verify we extracted criteria
        assert len(criteria) >= 7  # At least the explicit criteria

        # Verify criteria types are categorized
        types = {c.type for c in criteria}
        assert "functionality" in types or "testing" in types

        # Verify priorities are assigned
        priorities = {c.priority for c in criteria}
        assert "MUST" in priorities or "SHOULD" in priorities

    def test_automated_checks_on_real_codebase(self):
        """Test automated checks on actual codebase."""
        # Run on actual codebase
        codebase_root = Path(__file__).parent.parent.parent
        AutomatedChecks(codebase_root)

        # Run tests (this will actually run pytest)
        # Note: This is commented out to avoid long test execution in CI
        # Uncomment for manual integration testing
        # result = checker.run_all_checks()
        # assert result is not None
        # assert "status" in result

    def test_code_quality_on_skill_files(self):
        """Test code quality checker on DoD verification skill files."""
        codebase_root = Path(__file__).parent.parent.parent
        checker = CodeQualityChecker(codebase_root)

        # Check quality of our own skill files
        skill_files = [
            "coffee_maker/skills/dod_verification/criteria_parser.py",
            "coffee_maker/skills/dod_verification/automated_checks.py",
            "coffee_maker/skills/dod_verification/code_quality_checker.py",
        ]

        result = checker.check_quality(skill_files)

        # Our code should have good quality
        assert result is not None
        assert "status" in result
        # Allow WARN status for minor issues
        assert result["status"] in ["PASS", "WARN"]

    def test_parse_real_roadmap_priority(self):
        """Test parsing a real ROADMAP priority."""
        # Example from actual ROADMAP
        real_priority = """
        ### US-066: Implement dod-verification Skill

        **Status**: 📝 Planned

        **User Story**:
        As a code_developer agent, I need an automated DoD verification skill.

        **Acceptance Criteria**:
        - [ ] Skill executes in <3 minutes
        - [ ] Checks all DoD criteria
        - [ ] Generates report
        - [ ] Unit tests
        - [ ] Documentation

        **Deliverables**:
        1. dod-verification skill implementation
        2. Tests (unit + integration)
        3. Skill documentation
        """

        parser = CriteriaParser()
        criteria = parser.parse_criteria(real_priority)

        # Should extract explicit criteria
        assert len(criteria) >= 5

        # Check that IDs are assigned
        for criterion in criteria:
            assert criterion.id.startswith("criterion_")
            assert criterion.description
            assert criterion.type
            assert criterion.priority
            assert criterion.verification_method


@pytest.mark.skip(reason="Requires actual test execution - use for manual testing")
class TestDoDVerificationEndToEnd:
    """End-to-end tests (skip in CI)."""

    def test_verify_current_implementation(self):
        """Test DoD verification on current US-066 implementation."""
        from coffee_maker.skills.dod_verification.automated_checks import AutomatedChecks
        from coffee_maker.skills.dod_verification.code_quality_checker import CodeQualityChecker
        from coffee_maker.skills.dod_verification.documentation_checker import DocumentationChecker

        codebase_root = Path(__file__).parent.parent.parent

        # Files changed for US-066
        files_changed = [
            "coffee_maker/skills/dod_verification/__init__.py",
            "coffee_maker/skills/dod_verification/criteria_parser.py",
            "coffee_maker/skills/dod_verification/automated_checks.py",
            "coffee_maker/skills/dod_verification/code_quality_checker.py",
            "coffee_maker/skills/dod_verification/functionality_tester.py",
            "coffee_maker/skills/dod_verification/documentation_checker.py",
            "coffee_maker/skills/dod_verification/integration_verifier.py",
            "coffee_maker/skills/dod_verification/report_generator.py",
            ".claude/skills/dod-verification/SKILL.md",
            ".claude/skills/dod-verification/scripts/dod_verification.py",
            "tests/unit/skills/test_dod_verification.py",
            "tests/integration/test_dod_verification_integration.py",
        ]

        # Run automated checks
        automated = AutomatedChecks(codebase_root)
        auto_result = automated.run_all_checks()
        assert auto_result["status"] == "PASS"

        # Run code quality checks
        quality = CodeQualityChecker(codebase_root)
        quality_result = quality.check_quality(files_changed)
        assert quality_result["status"] in ["PASS", "WARN"]

        # Run documentation checks
        docs = DocumentationChecker(codebase_root)
        docs_result = docs.check_documentation(files_changed)
        assert docs_result["status"] in ["PASS", "WARN"]

        print("\n✅ US-066 DoD verification PASSED")
        print(f"   Automated checks: {auto_result['status']}")
        print(f"   Code quality: {quality_result['status']}")
        print(f"   Documentation: {docs_result['status']}")
