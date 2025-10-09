"""Tests for code review perspectives."""

from coffee_maker.code_reviewer.perspectives import (
    ArchitectCritic,
    BugHunter,
    PerformanceAnalyst,
    SecurityAuditor,
)


class TestBugHunter:
    """Test suite for BugHunter perspective."""

    def test_bug_hunter_initialization(self):
        """Test BugHunter can be initialized."""
        hunter = BugHunter()
        assert hunter.perspective_name == "Bug Hunter"
        assert hunter.model_name == "gpt-4-turbo"

    def test_detect_bare_except(self):
        """Test detection of bare except clauses."""
        code = """
try:
    risky_operation()
except:
    pass
"""
        hunter = BugHunter()
        issues = hunter.analyze(code, "test.py")

        # Should find bare except issue
        assert len(issues) > 0
        assert any("except" in issue.title.lower() for issue in issues)
        assert any(issue.severity == "medium" for issue in issues)

    def test_detect_resource_leak(self):
        """Test detection of file opens without context manager."""
        code = """
f = open("test.txt", "r")
data = f.read()
"""
        hunter = BugHunter()
        issues = hunter.analyze(code, "test.py")

        # Should find resource leak
        assert len(issues) > 0
        assert any("resource" in issue.title.lower() or "leak" in issue.title.lower() for issue in issues)

    def test_clean_code_no_issues(self):
        """Test that clean code produces fewer issues."""
        code = """
with open("test.txt", "r") as f:
    data = f.read()

try:
    result = safe_operation()
except ValueError as e:
    handle_error(e)
"""
        hunter = BugHunter()
        issues = hunter.analyze(code, "test.py")

        # Clean code should have no or minimal issues
        assert len(issues) == 0


class TestArchitectCritic:
    """Test suite for ArchitectCritic perspective."""

    def test_architect_critic_initialization(self):
        """Test ArchitectCritic can be initialized."""
        critic = ArchitectCritic()
        assert critic.perspective_name == "Architect Critic"
        assert critic.model_name == "claude-sonnet-4"

    def test_detect_large_class(self):
        """Test detection of overly large classes."""
        # Create a class with 350+ lines
        code = "class VeryLargeClass:\n" + "    pass\n" * 350

        critic = ArchitectCritic()
        issues = critic.analyze(code, "test.py")

        # Should find large class issue
        assert len(issues) > 0
        assert any("large class" in issue.title.lower() for issue in issues)

    def test_detect_complex_function(self):
        """Test detection of overly complex functions."""
        # Create a function with many lines
        code = "def complex_function():\n" + "    pass\n" * 60

        critic = ArchitectCritic()
        issues = critic.analyze(code, "test.py")

        # Should find complex function issue
        assert len(issues) > 0
        assert any("complex function" in issue.title.lower() or "function" in issue.title.lower() for issue in issues)

    def test_normal_sized_code(self):
        """Test that normal-sized code has fewer issues."""
        code = """
class SmallClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""
        critic = ArchitectCritic()
        issues = critic.analyze(code, "test.py")

        # Should have minimal architectural issues
        assert len([i for i in issues if i.severity in ["critical", "high"]]) == 0


class TestPerformanceAnalyst:
    """Test suite for PerformanceAnalyst perspective."""

    def test_performance_analyst_initialization(self):
        """Test PerformanceAnalyst can be initialized."""
        analyst = PerformanceAnalyst()
        assert analyst.perspective_name == "Performance Analyst"
        assert analyst.model_name == "gemini-pro"

    def test_detect_nested_loops(self):
        """Test detection of deeply nested loops."""
        code = """
for i in range(10):
    for j in range(10):
        for k in range(10):
            process(i, j, k)
"""
        analyst = PerformanceAnalyst()
        issues = analyst.analyze(code, "test.py")

        # Should find nested loop issue
        assert len(issues) > 0
        assert any("nested" in issue.title.lower() or "loop" in issue.title.lower() for issue in issues)

    def test_detect_string_concatenation_in_loop(self):
        """Test detection of string concatenation in loops."""
        code = """
result = ""
for i in range(100):
    result += str(i)
"""
        analyst = PerformanceAnalyst()
        issues = analyst.analyze(code, "test.py")

        # Should find string concatenation issue
        assert len(issues) > 0
        assert any("string" in issue.title.lower() or "concatenation" in issue.title.lower() for issue in issues)

    def test_detect_database_query_in_loop(self):
        """Test detection of N+1 query problem."""
        code = """
for user in users:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    process(profile)
"""
        analyst = PerformanceAnalyst()
        issues = analyst.analyze(code, "test.py")

        # Should find N+1 query issue
        assert len(issues) > 0
        assert any(
            "database" in issue.title.lower() or "query" in issue.title.lower() or "n+1" in issue.title.lower()
            for issue in issues
        )
        # N+1 queries should be critical
        assert any(issue.severity == "critical" for issue in issues)


class TestSecurityAuditor:
    """Test suite for SecurityAuditor perspective."""

    def test_security_auditor_initialization(self):
        """Test SecurityAuditor can be initialized."""
        auditor = SecurityAuditor()
        assert auditor.perspective_name == "Security Auditor"

    def test_detect_sql_injection(self):
        """Test detection of SQL injection vulnerabilities."""
        code = """
query = f"SELECT * FROM users WHERE name = '{user_input}'"
cursor.execute(query)
"""
        auditor = SecurityAuditor()
        issues = auditor.analyze(code, "test.py")

        # Should find SQL injection
        assert len(issues) > 0
        assert any("sql" in issue.title.lower() or "injection" in issue.title.lower() for issue in issues)
        # SQL injection should be critical
        assert any(issue.severity == "critical" for issue in issues)

    def test_detect_command_injection(self):
        """Test detection of command injection vulnerabilities."""
        code = """
import subprocess
subprocess.call(user_input, shell=True)
"""
        auditor = SecurityAuditor()
        issues = auditor.analyze(code, "test.py")

        # Should find command injection or shell=True issue
        assert len(issues) > 0
        assert any(
            "command" in issue.title.lower() or "shell" in issue.title.lower() or "injection" in issue.title.lower()
            for issue in issues
        )

    def test_detect_hardcoded_secrets(self):
        """Test detection of hardcoded secrets."""
        code = """
api_key = "sk-1234567890abcdef"
password = "secret123"
"""
        auditor = SecurityAuditor()
        issues = auditor.analyze(code, "test.py")

        # Should find hardcoded secrets
        assert len(issues) > 0
        assert any("secret" in issue.title.lower() or "hardcoded" in issue.title.lower() for issue in issues)
        # Hardcoded secrets should be critical
        assert any(issue.severity == "critical" for issue in issues)

    def test_detect_insecure_random(self):
        """Test detection of insecure random number generation."""
        code = """
import random
token = random.random()
session_id = random.randint(1000, 9999)
"""
        auditor = SecurityAuditor()
        issues = auditor.analyze(code, "test.py")

        # Should find insecure random usage
        assert len(issues) > 0
        assert any("random" in issue.title.lower() or "insecure" in issue.title.lower() for issue in issues)

    def test_secure_code_fewer_issues(self):
        """Test that secure code has fewer issues."""
        code = """
import secrets
from pathlib import Path

token = secrets.token_hex(32)

# Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Safe subprocess
subprocess.run(["ls", "-la"], shell=False)
"""
        auditor = SecurityAuditor()
        issues = auditor.analyze(code, "test.py")

        # Should have no critical security issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        assert len(critical_issues) == 0
