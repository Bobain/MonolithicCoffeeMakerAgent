"""Unit tests for DoD verification skill."""

import pytest

from coffee_maker.skills.dod_verification.criteria_parser import CriteriaParser, DoDCriterion
from coffee_maker.skills.dod_verification.code_quality_checker import CodeQualityChecker
from coffee_maker.skills.dod_verification.documentation_checker import DocumentationChecker
from coffee_maker.skills.dod_verification.integration_verifier import IntegrationVerifier


class TestCriteriaParser:
    """Test criteria parsing."""

    def test_parse_explicit_criteria(self):
        """Test parsing explicit acceptance criteria."""
        description = """
        Feature description.

        Acceptance Criteria:
        - [ ] User can create new recipe
        - [ ] All tests passing
        - [ ] Documentation updated
        """

        parser = CriteriaParser()
        criteria = parser.parse_criteria(description)

        assert len(criteria) >= 3
        assert any("create new recipe" in c.description.lower() for c in criteria)
        assert any("test" in c.description.lower() for c in criteria)
        assert any("document" in c.description.lower() for c in criteria)

    def test_parse_numbered_criteria(self):
        """Test parsing numbered criteria."""
        description = """
        Acceptance Criteria:
        1. Feature works correctly
        2. Tests pass
        3. Code formatted
        """

        parser = CriteriaParser()
        criteria = parser.parse_criteria(description)

        assert len(criteria) >= 3

    def test_parse_implicit_criteria(self):
        """Test extracting implicit criteria."""
        description = """
        Implement new feature with tests and documentation.
        Code must follow formatting standards.
        """

        parser = CriteriaParser()
        criteria = parser.parse_criteria(description)

        # Should extract implicit test and doc criteria
        assert len(criteria) > 0
        assert any(c.type == "testing" for c in criteria)
        assert any(c.type == "documentation" for c in criteria)

    def test_default_criteria(self):
        """Test default criteria when none specified."""
        description = "Simple feature with no explicit criteria."

        parser = CriteriaParser()
        criteria = parser.parse_criteria(description)

        # Should return default criteria
        assert len(criteria) > 0

    def test_criterion_priority_detection(self):
        """Test priority detection (MUST vs SHOULD)."""
        description = """
        Acceptance Criteria:
        - [ ] User MUST be able to login
        - [ ] System SHOULD send confirmation email
        """

        parser = CriteriaParser()
        criteria = parser.parse_criteria(description)

        must_criteria = [c for c in criteria if c.priority == "MUST"]
        should_criteria = [c for c in criteria if c.priority == "SHOULD"]

        assert len(must_criteria) >= 1
        assert len(should_criteria) >= 1


class TestCodeQualityChecker:
    """Test code quality checking."""

    @pytest.fixture
    def temp_python_file(self, tmp_path):
        """Create a temporary Python file for testing."""
        file_path = tmp_path / "test_module.py"
        file_path.write_text(
            '''"""Module docstring."""

def public_function():
    """Public function with docstring."""
    return "test"

def _private_function():
    # Private function without docstring (OK)
    return "private"

class TestClass:
    """Class with docstring."""

    def method(self):
        """Method with docstring."""
        pass
'''
        )
        return file_path

    def test_check_quality_pass(self, temp_python_file, tmp_path):
        """Test quality check passes for good code."""
        checker = CodeQualityChecker(tmp_path)
        result = checker.check_quality([str(temp_python_file.relative_to(tmp_path))])

        assert result["status"] in ["PASS", "WARN"]
        assert result["files_checked"] == 1

    def test_check_quality_missing_docstrings(self, tmp_path):
        """Test detection of missing docstrings."""
        bad_file = tmp_path / "bad_module.py"
        bad_file.write_text(
            """
def public_function():
    return "test"

class MyClass:
    def method(self):
        pass
"""
        )

        checker = CodeQualityChecker(tmp_path)
        result = checker.check_quality([str(bad_file.relative_to(tmp_path))])

        # Should detect missing docstrings
        assert len(result["issues"]["missing_docstrings"]) > 0

    def test_check_quality_print_statements(self, tmp_path):
        """Test detection of print statements."""
        bad_file = tmp_path / "bad_module.py"
        bad_file.write_text(
            '''"""Module docstring."""

def debug_function():
    """Function with print statement."""
    print("Debug message")
    return True
'''
        )

        checker = CodeQualityChecker(tmp_path)
        result = checker.check_quality([str(bad_file.relative_to(tmp_path))])

        # Should detect print statements
        assert len(result["issues"]["print_statements"]) > 0


class TestDocumentationChecker:
    """Test documentation checking."""

    @pytest.fixture
    def codebase_with_docs(self, tmp_path):
        """Create a temporary codebase with documentation."""
        # Create README
        readme = tmp_path / "README.md"
        readme.write_text("# Project README")

        # Create architecture docs
        docs_dir = tmp_path / "docs" / "architecture"
        docs_dir.mkdir(parents=True)
        (docs_dir / "specs").mkdir()
        (docs_dir / "decisions").mkdir()

        return tmp_path

    def test_check_documentation_pass(self, codebase_with_docs):
        """Test documentation check passes when docs exist."""
        checker = DocumentationChecker(codebase_with_docs)
        result = checker.check_documentation(["coffee_maker/test.py"])

        # Should pass basic checks
        assert result["status"] in ["PASS", "WARN"]

    def test_check_code_docs_missing_module_docstring(self, tmp_path):
        """Test detection of missing module docstrings."""
        bad_file = tmp_path / "coffee_maker" / "bad_module.py"
        bad_file.parent.mkdir(parents=True, exist_ok=True)
        bad_file.write_text(
            """
def function():
    pass
"""
        )

        checker = DocumentationChecker(tmp_path)
        result = checker.check_documentation(["coffee_maker/bad_module.py"])

        # Should detect missing module docstring
        assert len(result["missing_docs"]) > 0


class TestIntegrationVerifier:
    """Test integration verification."""

    def test_verify_integration_no_changes(self, tmp_path):
        """Test integration verification with no critical changes."""
        verifier = IntegrationVerifier(tmp_path)
        result = verifier.verify_integration([])

        # Should pass with no changes
        assert result["status"] == "PASS"

    def test_has_dependency_changes(self, tmp_path):
        """Test detection of dependency changes."""
        verifier = IntegrationVerifier(tmp_path)

        assert verifier._has_dependency_changes(["pyproject.toml"])
        assert verifier._has_dependency_changes(["poetry.lock"])
        assert not verifier._has_dependency_changes(["coffee_maker/test.py"])

    def test_has_config_changes(self, tmp_path):
        """Test detection of config changes."""
        verifier = IntegrationVerifier(tmp_path)

        assert verifier._has_config_changes([".claude/settings.json"])
        assert verifier._has_config_changes(["config/settings.py"])
        assert not verifier._has_config_changes(["coffee_maker/test.py"])


class TestDoDCriterion:
    """Test DoDCriterion dataclass."""

    def test_criterion_creation(self):
        """Test creating a DoD criterion."""
        criterion = DoDCriterion(
            id="test_1",
            description="Test criterion",
            type="functionality",
            priority="MUST",
            verification_method="automated_test",
        )

        assert criterion.id == "test_1"
        assert criterion.description == "Test criterion"
        assert criterion.type == "functionality"
        assert criterion.priority == "MUST"
        assert criterion.status == "pending"

    def test_criterion_status_update(self):
        """Test updating criterion status."""
        criterion = DoDCriterion(
            id="test_1",
            description="Test",
            type="functionality",
            priority="MUST",
            verification_method="manual_test",
        )

        criterion.status = "pass"
        assert criterion.status == "pass"

        criterion.status = "fail"
        assert criterion.status == "fail"
