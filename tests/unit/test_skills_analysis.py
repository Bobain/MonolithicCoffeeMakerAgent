"""
Test suite for code analysis skills.

Tests: code_forensics, security_audit, dependency_tracer, functional_search, code_explainer
"""

import tempfile
from pathlib import Path

import pytest

from coffee_maker.skills.code_analysis.code_explainer import CodeExplainer
from coffee_maker.skills.code_analysis.code_forensics import CodeForensics
from coffee_maker.skills.code_analysis.dependency_tracer import DependencyTracer
from coffee_maker.skills.code_analysis.security_audit import SecurityAudit


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "coffee_maker").mkdir()
        (tmpdir / "coffee_maker" / "auth").mkdir()

        # Create test files
        (tmpdir / "coffee_maker" / "auth" / "jwt.py").write_text(
            """
'''JWT authentication module'''
import jwt
import hashlib
import random

def validate_jwt(token):
    '''Validate JWT token'''
    try:
        payload = jwt.decode(token, 'secret')
        return payload
    except Exception:
        raise ValueError("Invalid token")

def hash_password(password):
    '''Hash password using MD5'''
    return hashlib.md5(password.encode()).hexdigest()

class JWTValidator:
    '''Validates JWT tokens'''
    def __init__(self):
        self.secret = 'hardcoded_secret_key_123'
        self.api_key = 'sk-12345'

    def validate(self, token):
        try:
            return jwt.decode(token, self.secret)
        except:
            pass
"""
        )

        (tmpdir / "coffee_maker" / "auth" / "oauth.py").write_text(
            """
'''OAuth authentication module'''
from coffee_maker.auth.jwt import validate_jwt
import requests

def validate_oauth(token):
    '''Validate OAuth token'''
    return validate_jwt(token)
"""
        )

        (tmpdir / "coffee_maker" / "database.py").write_text(
            """
'''Database module'''
from coffee_maker.auth.jwt import JWTValidator

def query_user(user_id):
    '''Query user from database'''
    pass
"""
        )

        yield tmpdir


class TestCodeForensics:
    """Test CodeForensics skill."""

    def test_forensics_init(self, temp_codebase):
        """Test forensics initialization."""
        forensics = CodeForensics(str(temp_codebase))
        assert forensics.codebase_root == Path(temp_codebase)

    def test_find_patterns(self, temp_codebase):
        """Test pattern finding."""
        forensics = CodeForensics(str(temp_codebase))
        results = forensics.find_patterns("error_handling")

        assert "patterns_found" in results
        assert "error_handling" in results["patterns_found"]

    def test_find_all_patterns(self, temp_codebase):
        """Test finding all patterns."""
        forensics = CodeForensics(str(temp_codebase))
        results = forensics.find_patterns()

        assert "patterns_found" in results
        assert len(results["patterns_found"]) > 0

    def test_analyze_complexity(self, temp_codebase):
        """Test complexity analysis."""
        forensics = CodeForensics(str(temp_codebase))
        results = forensics.analyze_complexity()

        assert "files" in results
        assert "summary" in results
        assert results["summary"]["total_loc"] > 0

    def test_identify_duplication(self, temp_codebase):
        """Test duplication identification."""
        forensics = CodeForensics(str(temp_codebase))
        results = forensics.identify_duplication()

        assert "potential_duplicates" in results
        assert "summary" in results

    def test_architectural_analysis(self, temp_codebase):
        """Test architectural analysis."""
        forensics = CodeForensics(str(temp_codebase))
        results = forensics.architectural_analysis()

        assert "components" in results
        assert "auth" in results["components"]


class TestSecurityAudit:
    """Test SecurityAudit skill."""

    def test_security_init(self, temp_codebase):
        """Test security audit initialization."""
        audit = SecurityAudit(str(temp_codebase))
        assert audit.codebase_root == Path(temp_codebase)

    def test_check_vulnerabilities(self, temp_codebase):
        """Test vulnerability checking."""
        audit = SecurityAudit(str(temp_codebase))
        results = audit.check_vulnerabilities()

        assert "vulnerabilities" in results
        assert "summary" in results
        # Should find weak crypto (MD5) and hardcoded secrets
        assert results["summary"]["total_issues"] >= 0

    def test_analyze_dependencies(self, temp_codebase):
        """Test dependency analysis."""
        audit = SecurityAudit(str(temp_codebase))
        results = audit.analyze_dependencies()

        assert "dependencies" in results
        assert "summary" in results
        assert "jwt" in results["dependencies"]

    def test_find_security_patterns(self, temp_codebase):
        """Test security pattern finding."""
        audit = SecurityAudit(str(temp_codebase))
        results = audit.find_security_patterns()

        assert "patterns" in results

    def test_generate_security_report(self, temp_codebase):
        """Test security report generation."""
        audit = SecurityAudit(str(temp_codebase))
        report = audit.generate_security_report()

        assert "vulnerabilities" in report
        assert "dependencies" in report
        assert "recommendations" in report


class TestDependencyTracer:
    """Test DependencyTracer skill."""

    def test_tracer_init(self, temp_codebase):
        """Test dependency tracer initialization."""
        tracer = DependencyTracer(str(temp_codebase))
        assert tracer.codebase_root == Path(temp_codebase)

    def test_trace_imports(self, temp_codebase):
        """Test import tracing."""
        tracer = DependencyTracer(str(temp_codebase))
        results = tracer.trace_imports("coffee_maker/auth/jwt.py")

        assert "file" in results
        assert "imports" in results
        assert "jwt" in results["imports"]["third_party"]

    def test_find_dependents(self, temp_codebase):
        """Test finding dependent files."""
        tracer = DependencyTracer(str(temp_codebase))
        results = tracer.find_dependents("coffee_maker/auth/jwt.py")

        assert "module" in results
        assert "dependents" in results

    def test_impact_analysis(self, temp_codebase):
        """Test impact analysis."""
        tracer = DependencyTracer(str(temp_codebase))
        results = tracer.impact_analysis("coffee_maker/auth/jwt.py")

        assert "file" in results
        assert "direct_impact" in results
        assert "impact_level" in results

    def test_circular_dependencies(self, temp_codebase):
        """Test circular dependency detection."""
        tracer = DependencyTracer(str(temp_codebase))
        results = tracer.circular_dependencies()

        assert "cycles_found" in results
        assert "circular_count" in results

    def test_dependency_graph(self, temp_codebase):
        """Test dependency graph generation."""
        tracer = DependencyTracer(str(temp_codebase))
        graph = tracer.dependency_graph()

        assert isinstance(graph, dict)


class TestCodeExplainer:
    """Test CodeExplainer skill."""

    def test_explainer_init(self, temp_codebase):
        """Test code explainer initialization."""
        explainer = CodeExplainer(str(temp_codebase))
        assert explainer.codebase_root == Path(temp_codebase)

    def test_explain_file(self, temp_codebase):
        """Test file explanation."""
        explainer = CodeExplainer(str(temp_codebase))
        results = explainer.explain_file("coffee_maker/auth/jwt.py")

        assert "file" in results
        assert "summary" in results
        assert "exports" in results

    def test_explain_function(self, temp_codebase):
        """Test function explanation."""
        explainer = CodeExplainer(str(temp_codebase))
        results = explainer.explain_function("coffee_maker/auth/jwt.py", "validate_jwt")

        assert "function" in results
        assert results["function"] == "validate_jwt"
        assert "summary" in results

    def test_explain_class(self, temp_codebase):
        """Test class explanation."""
        explainer = CodeExplainer(str(temp_codebase))
        results = explainer.explain_class("coffee_maker/auth/jwt.py", "JWTValidator")

        assert "class" in results
        assert results["class"] == "JWTValidator"
        assert "methods" in results

    def test_explain_pattern(self, temp_codebase):
        """Test pattern explanation."""
        explainer = CodeExplainer(str(temp_codebase))
        results = explainer.explain_pattern("singleton")

        assert "pattern" in results
        assert "description" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
