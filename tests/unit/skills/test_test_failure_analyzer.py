"""
Unit tests for test_failure_analyzer skill.

Tests all failure categories and fix recommendations.
"""

import pytest
from claude.skills.code_analysis.test_failure_analyzer import (
    TestFailureAnalyzerSkill,
    FailureCategory,
)


class TestTestFailureAnalyzer:
    """Tests for TestFailureAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return TestFailureAnalyzerSkill()

    @pytest.fixture
    def sample_import_error_output(self):
        """Sample pytest output with import error."""
        return """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_login FAILED                               [ 33%]

=================================== FAILURES ===================================
_______________________________ test_login _____________________________________

    def test_login():
>       from coffee_maker.auth import jwt_handler
E       ImportError: cannot import name 'jwt_handler'

tests/unit/test_auth.py:5: ImportError
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_login - ImportError: cannot import name 'jwt_handler'
========================= 1 failed, 2 passed in 0.12s ==========================
"""

    @pytest.fixture
    def sample_assertion_error_output(self):
        """Sample pytest output with assertion error."""
        return """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_login_success FAILED                      [ 33%]

=================================== FAILURES ===================================
____________________________ test_login_success ________________________________

    def test_login_success():
        user = login("admin", "password123")
>       assert user is not None
E       AssertionError: assert None is not None

tests/unit/test_auth.py:12: AssertionError
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_login_success - AssertionError
========================= 1 failed, 2 passed in 0.12s ==========================
"""

    @pytest.fixture
    def sample_attribute_error_output(self):
        """Sample pytest output with attribute error."""
        return """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_user_name FAILED                          [ 33%]

=================================== FAILURES ===================================
______________________________ test_user_name __________________________________

    def test_user_name():
        user = User("alice")
>       name = user.get_name()
E       AttributeError: 'User' object has no attribute 'get_name'

tests/unit/test_auth.py:20: AttributeError
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_user_name - AttributeError
========================= 1 failed, 2 passed in 0.12s ==========================
"""

    @pytest.fixture
    def sample_type_error_output(self):
        """Sample pytest output with type error."""
        return """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_validate_age FAILED                       [ 33%]

=================================== FAILURES ===================================
_____________________________ test_validate_age ________________________________

    def test_validate_age():
>       result = validate_age("25")
E       TypeError: expected int, got str

tests/unit/test_auth.py:25: TypeError
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_validate_age - TypeError
========================= 1 failed, 2 passed in 0.12s ==========================
"""

    @pytest.fixture
    def sample_fixture_error_output(self):
        """Sample pytest output with fixture error."""
        return """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_with_db FAILED                            [ 33%]

=================================== FAILURES ===================================
_______________________________ test_with_db ___________________________________

    def test_with_db(db_session):
E       fixture 'db_session' not found

tests/unit/test_auth.py:30: Error
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_with_db - fixture 'db_session' not found
========================= 1 failed, 2 passed in 0.12s ==========================
"""

    @pytest.fixture
    def sample_multiple_failures_output(self):
        """Sample pytest output with multiple failures."""
        return """
============================= test session starts ==============================
collected 5 items

tests/unit/test_auth.py::test_login FAILED                               [ 20%]
tests/unit/test_auth.py::test_logout FAILED                              [ 40%]
tests/unit/test_auth.py::test_register PASSED                            [ 60%]
tests/unit/test_auth.py::test_password_reset FAILED                      [ 80%]
tests/unit/test_auth.py::test_profile PASSED                             [100%]

=================================== FAILURES ===================================
________________________________ test_login ____________________________________

    def test_login():
>       from coffee_maker.auth import jwt_handler
E       ImportError: cannot import name 'jwt_handler'

tests/unit/test_auth.py:5: ImportError
________________________________ test_logout ___________________________________

    def test_logout():
        user = get_current_user()
>       assert user.is_authenticated
E       AssertionError: assert False

tests/unit/test_auth.py:25: AssertionError
____________________________ test_password_reset _______________________________

    def test_password_reset():
        user = User.get("alice")
>       user.reset_password("newpass")
E       AttributeError: 'User' object has no attribute 'reset_password'

tests/unit/test_auth.py:35: AttributeError
=========================== short test summary info ============================
FAILED tests/unit/test_auth.py::test_login - ImportError: cannot import name 'jwt_handler'
FAILED tests/unit/test_auth.py::test_logout - AssertionError
FAILED tests/unit/test_auth.py::test_password_reset - AttributeError
======================= 3 failed, 2 passed in 0.25s ==========================
"""

    # Test parsing

    def test_parse_single_failure(self, analyzer, sample_import_error_output):
        """Test parsing single test failure."""
        failures = analyzer._parse_pytest_output(sample_import_error_output)

        assert len(failures) == 1
        assert failures[0].test_name == "test_login"
        assert failures[0].file == "tests/unit/test_auth.py"
        assert failures[0].error_type == "ImportError"
        assert "cannot import name 'jwt_handler'" in failures[0].message

    def test_parse_multiple_failures(self, analyzer, sample_multiple_failures_output):
        """Test parsing multiple test failures."""
        failures = analyzer._parse_pytest_output(sample_multiple_failures_output)

        assert len(failures) == 3
        assert failures[0].test_name == "test_login"
        assert failures[1].test_name == "test_logout"
        assert failures[2].test_name == "test_password_reset"

    def test_parse_empty_output(self, analyzer):
        """Test parsing empty pytest output."""
        failures = analyzer._parse_pytest_output("")
        assert len(failures) == 0

    def test_parse_all_passed_output(self, analyzer):
        """Test parsing output with all tests passed."""
        output = """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py::test_login PASSED                              [ 33%]
tests/unit/test_auth.py::test_logout PASSED                             [ 67%]
tests/unit/test_auth.py::test_register PASSED                           [100%]

============================== 3 passed in 0.12s ===============================
"""
        failures = analyzer._parse_pytest_output(output)
        assert len(failures) == 0

    # Test categorization

    def test_categorize_import_error(self, analyzer, sample_import_error_output):
        """Test categorization of import error."""
        failures = analyzer._parse_pytest_output(sample_import_error_output)
        category = analyzer._categorize_failure(failures[0])
        assert category == FailureCategory.IMPORT_ERROR

    def test_categorize_assertion_error(self, analyzer, sample_assertion_error_output):
        """Test categorization of assertion error."""
        failures = analyzer._parse_pytest_output(sample_assertion_error_output)
        category = analyzer._categorize_failure(failures[0])
        assert category == FailureCategory.ASSERTION_ERROR

    def test_categorize_attribute_error(self, analyzer, sample_attribute_error_output):
        """Test categorization of attribute error."""
        failures = analyzer._parse_pytest_output(sample_attribute_error_output)
        category = analyzer._categorize_failure(failures[0])
        assert category == FailureCategory.ATTRIBUTE_ERROR

    def test_categorize_type_error(self, analyzer, sample_type_error_output):
        """Test categorization of type error."""
        failures = analyzer._parse_pytest_output(sample_type_error_output)
        category = analyzer._categorize_failure(failures[0])
        assert category == FailureCategory.TYPE_ERROR

    def test_categorize_fixture_error(self, analyzer, sample_fixture_error_output):
        """Test categorization of fixture error."""
        failures = analyzer._parse_pytest_output(sample_fixture_error_output)
        category = analyzer._categorize_failure(failures[0])
        assert category == FailureCategory.FIXTURE_ERROR

    # Test correlation

    def test_correlate_high_correlation(self, analyzer, sample_assertion_error_output):
        """Test correlation with high match."""
        failures = analyzer._parse_pytest_output(sample_assertion_error_output)
        files_changed = ["coffee_maker/auth/login.py", "coffee_maker/auth/__init__.py"]

        correlation = analyzer._correlate_with_changes(failures[0], files_changed)
        assert correlation == "HIGH"

    def test_correlate_low_correlation(self, analyzer, sample_assertion_error_output):
        """Test correlation with low match."""
        failures = analyzer._parse_pytest_output(sample_assertion_error_output)
        files_changed = ["coffee_maker/utils/helpers.py"]

        correlation = analyzer._correlate_with_changes(failures[0], files_changed)
        assert correlation == "LOW"

    def test_correlate_no_files_changed(self, analyzer, sample_assertion_error_output):
        """Test correlation with no files changed."""
        failures = analyzer._parse_pytest_output(sample_assertion_error_output)
        correlation = analyzer._correlate_with_changes(failures[0], [])
        assert correlation == "UNKNOWN"

    # Test priority calculation

    def test_calculate_priority_critical(self, analyzer):
        """Test priority calculation for critical failure."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_login",
            file="tests/unit/test_auth.py",
            line=10,
            error_type="ImportError",
            message="cannot import",
            traceback="",
            category=FailureCategory.IMPORT_ERROR,
            correlation="HIGH",
        )

        priority = analyzer._calculate_priority(failure)
        assert priority == 1  # CRITICAL

    def test_calculate_priority_high(self, analyzer):
        """Test priority calculation for high priority failure."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_validate",
            file="tests/unit/test_utils.py",
            line=20,
            error_type="TypeError",
            message="type mismatch",
            traceback="",
            category=FailureCategory.TYPE_ERROR,
            correlation="MEDIUM",
        )

        priority = analyzer._calculate_priority(failure)
        assert priority == 2  # HIGH

    def test_calculate_priority_medium(self, analyzer):
        """Test priority calculation for medium priority failure."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_fixture",
            file="tests/unit/test_db.py",
            line=30,
            error_type="FixtureError",
            message="fixture not found",
            traceback="",
            category=FailureCategory.FIXTURE_ERROR,
            correlation="LOW",
        )

        priority = analyzer._calculate_priority(failure)
        assert priority == 3  # MEDIUM

    # Test full analysis

    def test_analyze_single_failure(self, analyzer, sample_import_error_output):
        """Test full analysis of single failure."""
        result = analyzer.analyze(
            test_output=sample_import_error_output,
            files_changed=["coffee_maker/auth/jwt_handler.py"],
            priority_name="US-123",
        )

        assert result.total_failures == 1
        assert result.critical_failures >= 0
        assert len(result.failures) == 1
        assert len(result.recommendations) == 1
        assert result.estimated_total_time_min > 0

    def test_analyze_multiple_failures(self, analyzer, sample_multiple_failures_output):
        """Test full analysis of multiple failures."""
        result = analyzer.analyze(
            test_output=sample_multiple_failures_output,
            files_changed=["coffee_maker/auth/login.py"],
            priority_name="US-456",
        )

        assert result.total_failures == 3
        assert len(result.failures) == 3
        assert len(result.recommendations) == 3
        assert len(result.recommended_fix_order) == 3
        assert result.estimated_total_time_min > 0

    def test_analyze_no_failures(self, analyzer):
        """Test analysis of output with no failures."""
        output = """
============================= test session starts ==============================
collected 3 items

tests/unit/test_auth.py PASSED                                         [100%]

============================== 3 passed in 0.12s ===============================
"""
        result = analyzer.analyze(test_output=output, files_changed=[], priority_name="US-789")

        assert result.total_failures == 0
        assert result.critical_failures == 0
        assert len(result.failures) == 0
        assert len(result.recommendations) == 0
        assert result.estimated_total_time_min == 0

    def test_analyze_execution_time(self, analyzer, sample_import_error_output):
        """Test that analysis executes quickly (< 2 minutes target)."""
        import time

        start = time.time()
        result = analyzer.analyze(test_output=sample_import_error_output, files_changed=[], priority_name="US-999")
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete in < 2 seconds (well under 2 minute target)
        assert result.total_failures == 1

    # Test fix recommendations

    def test_recommend_import_fix(self, analyzer):
        """Test import error fix recommendation."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_login",
            file="tests/unit/test_auth.py",
            line=10,
            error_type="ImportError",
            message="cannot import",
            traceback="",
            category=FailureCategory.IMPORT_ERROR,
        )

        rec = analyzer._recommend_import_fix(failure)
        assert rec.quick_fix_time_min > 0
        assert "import" in rec.root_cause.lower()
        assert rec.deep_fix is not None

    def test_recommend_assertion_fix(self, analyzer):
        """Test assertion error fix recommendation."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_value",
            file="tests/unit/test_logic.py",
            line=20,
            error_type="AssertionError",
            message="assert False",
            traceback="",
            category=FailureCategory.ASSERTION_ERROR,
        )

        rec = analyzer._recommend_assertion_fix(failure)
        assert rec.quick_fix_time_min > 0
        assert "logic" in rec.root_cause.lower() or "implementation" in rec.root_cause.lower()

    def test_recommend_attribute_fix(self, analyzer):
        """Test attribute error fix recommendation."""
        from claude.skills.code_analysis.test_failure_analyzer import TestFailure

        failure = TestFailure(
            test_name="test_method",
            file="tests/unit/test_class.py",
            line=30,
            error_type="AttributeError",
            message="no attribute",
            traceback="",
            category=FailureCategory.ATTRIBUTE_ERROR,
        )

        rec = analyzer._recommend_attribute_fix(failure)
        assert rec.quick_fix_time_min > 0
        assert "method" in rec.root_cause.lower() or "property" in rec.root_cause.lower()

    # Test report formatting

    def test_format_analysis_report(self, analyzer, sample_multiple_failures_output):
        """Test formatted report generation."""
        result = analyzer.analyze(
            test_output=sample_multiple_failures_output,
            files_changed=["coffee_maker/auth/login.py"],
            priority_name="US-456",
        )

        report = analyzer.format_analysis_report(result, "US-456")

        assert "Test Failure Analysis Report" in report
        assert "US-456" in report
        assert "Total Failures: 3" in report
        assert "CRITICAL" in report or "Summary" in report
        assert "Recommended Fix Order" in report

    def test_format_report_with_no_failures(self, analyzer):
        """Test report formatting with no failures."""
        result = analyzer.analyze(test_output="", files_changed=[], priority_name="US-000")

        report = analyzer.format_analysis_report(result, "US-000")

        assert "Test Failure Analysis Report" in report
        assert "Total Failures: 0" in report

    # Test prioritization

    def test_prioritize_fixes(self, analyzer, sample_multiple_failures_output):
        """Test fix prioritization logic."""
        result = analyzer.analyze(
            test_output=sample_multiple_failures_output,
            files_changed=["coffee_maker/auth/login.py"],
            priority_name="US-456",
        )

        # Should have recommended fix order
        assert len(result.recommended_fix_order) == 3

        # First item should be highest priority (lowest priority number)
        first_test = result.recommended_fix_order[0]
        first_rec = next(r for r in result.recommendations if r.failure.test_name == first_test)

        for test_name in result.recommended_fix_order[1:]:
            rec = next(r for r in result.recommendations if r.failure.test_name == test_name)
            # Priority should be >= first (lower number = higher priority)
            assert rec.failure.priority >= first_rec.failure.priority

    # Test edge cases

    def test_malformed_pytest_output(self, analyzer):
        """Test handling of malformed pytest output."""
        malformed_output = """
This is not valid pytest output
Some random text
No test results here
"""
        result = analyzer.analyze(test_output=malformed_output, files_changed=[], priority_name="US-ERR")

        # Should handle gracefully
        assert result.total_failures == 0
        assert len(result.failures) == 0

    def test_very_long_pytest_output(self, analyzer):
        """Test handling of very long pytest output."""
        # Create output with many failures
        long_output = "============================= test session starts ==============================\n"
        for i in range(100):
            long_output += f"""
FAILED tests/unit/test_{i}.py::test_{i}

    def test_{i}():
>       assert False
E       AssertionError

tests/unit/test_{i}.py:10: AssertionError
"""

        result = analyzer.analyze(test_output=long_output, files_changed=[], priority_name="US-LONG")

        # Should parse all failures
        assert result.total_failures == 100
        assert len(result.failures) == 100
        assert len(result.recommendations) == 100

    def test_categorization_accuracy(self, analyzer, sample_multiple_failures_output):
        """Test that categorization is accurate (90%+ target)."""
        result = analyzer.analyze(
            test_output=sample_multiple_failures_output,
            files_changed=["coffee_maker/auth/login.py"],
            priority_name="US-ACC",
        )

        # Check that categories match expected types
        [f.category for f in result.failures]

        # ImportError should be categorized as IMPORT_ERROR
        import_failures = [f for f in result.failures if "ImportError" in f.error_type]
        for f in import_failures:
            assert f.category == FailureCategory.IMPORT_ERROR

        # AssertionError should be categorized as ASSERTION_ERROR
        assert_failures = [f for f in result.failures if "AssertionError" in f.error_type]
        for f in assert_failures:
            assert f.category == FailureCategory.ASSERTION_ERROR

        # AttributeError should be categorized as ATTRIBUTE_ERROR
        attr_failures = [f for f in result.failures if "AttributeError" in f.error_type]
        for f in attr_failures:
            assert f.category == FailureCategory.ATTRIBUTE_ERROR


class TestTestFailureAnalysisIntegration:
    """Integration tests for test_failure_analysis convenience function."""

    def test_test_failure_analysis_function(self, sample_import_error_output):
        """Test test_failure_analysis convenience function."""
        from claude.skills import test_failure_analysis

        result = test_failure_analysis(
            test_output=sample_import_error_output,
            files_changed=["coffee_maker/auth/jwt.py"],
            priority_name="US-INT",
        )

        assert isinstance(result, dict)
        assert "total_failures" in result
        assert "recommendations" in result
        assert "report" in result
        assert result["total_failures"] == 1

    @pytest.fixture
    def sample_import_error_output(self):
        """Sample pytest output with import error."""
        return """
FAILED tests/unit/test_auth.py::test_login - ImportError: cannot import name 'jwt_handler'
"""
