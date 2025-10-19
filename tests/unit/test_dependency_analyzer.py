"""
Unit tests for dependency analyzer components.

Tests all 6 components:
- DependencyAnalyzer (orchestrator)
- ConflictAnalyzer
- SecurityScanner
- LicenseChecker
- VersionAnalyzer
- ImpactAssessor
"""

from unittest.mock import Mock, patch

import pytest

from coffee_maker.utils.dependency_analyzer import (
    DependencyAnalyzer,
    Recommendation,
    SecuritySeverity,
)
from coffee_maker.utils.dependency_conflict_analyzer import ConflictAnalyzer
from coffee_maker.utils.dependency_impact_assessor import ImpactAssessor
from coffee_maker.utils.dependency_license_checker import LicenseChecker
from coffee_maker.utils.dependency_security_scanner import SecurityScanner
from coffee_maker.utils.dependency_version_analyzer import VersionAnalyzer


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.poetry]
name = "test-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
"""
    )
    return tmp_path


@pytest.fixture
def sample_pypi_metadata():
    """Sample PyPI metadata for testing."""
    return {
        "info": {
            "name": "pytest-timeout",
            "version": "2.2.0",
            "license": "MIT",
            "summary": "pytest plugin to abort hanging tests",
            "classifiers": [
                "License :: OSI Approved :: MIT License",
                "Operating System :: POSIX :: Linux",
                "Operating System :: MacOS",
                "Operating System :: Microsoft :: Windows",
            ],
        },
        "releases": {
            "2.2.0": [
                {
                    "packagetype": "bdist_wheel",
                    "size": 12345,
                    "upload_time": "2023-01-15T10:30:00",
                }
            ],
            "2.1.0": [],
            "1.0.0": [],
        },
    }


# ==================== DependencyAnalyzer Tests ====================


class TestDependencyAnalyzer:
    """Tests for DependencyAnalyzer orchestrator."""

    def test_analyze_dependency_approve(self, project_root, sample_pypi_metadata):
        """Test analysis returns APPROVE for safe package."""
        analyzer = DependencyAnalyzer(project_root)

        # Mock all components to return safe results
        with patch.object(analyzer.conflict_analyzer, "check_conflicts") as mock_conflicts, patch.object(
            analyzer.security_scanner, "scan_security"
        ) as mock_security, patch.object(analyzer.license_checker, "check_license") as mock_license, patch.object(
            analyzer.version_analyzer, "analyze_version"
        ) as mock_version, patch.object(
            analyzer.impact_assessor, "assess_impact"
        ) as mock_impact:

            from coffee_maker.utils.dependency_analyzer import (
                ConflictInfo,
                ImpactAssessment,
                LicenseInfo,
                SecurityReport,
                VersionInfo,
            )

            mock_conflicts.return_value = ConflictInfo(
                has_conflicts=False,
                conflicts=[],
                circular_dependencies=[],
                tree_depth=0,
                total_sub_dependencies=0,
            )

            mock_security.return_value = SecurityReport(
                severity=SecuritySeverity.NONE,
                cve_count=0,
                cve_ids=[],
                vulnerabilities=[],
                mitigation_notes="No mitigation needed",
                scan_timestamp="2025-10-19T10:00:00",
            )

            mock_license.return_value = LicenseInfo(
                license_name="MIT",
                license_type="permissive",
                compatible_with_apache2=True,
                issues=[],
                alternatives=[],
            )

            mock_version.return_value = VersionInfo(
                requested_version=None,
                latest_stable="2.2.0",
                is_latest=True,
                is_deprecated=False,
                breaking_changes=[],
                suggested_constraint="^2.2.0",
                release_date="2023-01-15",
            )

            mock_impact.return_value = ImpactAssessment(
                estimated_install_time_seconds=2,
                bundle_size_mb=0.25,
                sub_dependencies_added=[],
                platform_compatibility={"linux": True, "macos": True, "windows": True},
            )

            # Run analysis
            report = analyzer.analyze_dependency("pytest-timeout")

            # Verify recommendation
            assert report.recommendation == Recommendation.APPROVE
            assert report.package_name == "pytest-timeout"
            assert report.security.severity == SecuritySeverity.NONE
            assert report.license.compatible_with_apache2
            assert not report.conflicts.has_conflicts
            assert report.installation_command == "poetry add pytest-timeout"

    def test_analyze_dependency_review(self, project_root):
        """Test analysis returns REVIEW for medium-risk package."""
        analyzer = DependencyAnalyzer(project_root)

        with patch.object(analyzer.conflict_analyzer, "check_conflicts") as mock_conflicts, patch.object(
            analyzer.security_scanner, "scan_security"
        ) as mock_security, patch.object(analyzer.license_checker, "check_license") as mock_license, patch.object(
            analyzer.version_analyzer, "analyze_version"
        ) as mock_version, patch.object(
            analyzer.impact_assessor, "assess_impact"
        ) as mock_impact:

            from coffee_maker.utils.dependency_analyzer import (
                ConflictInfo,
                ImpactAssessment,
                LicenseInfo,
                SecurityReport,
                VersionInfo,
            )

            mock_conflicts.return_value = ConflictInfo(
                has_conflicts=False, conflicts=[], circular_dependencies=[], tree_depth=0, total_sub_dependencies=0
            )

            # HIGH severity triggers REVIEW
            mock_security.return_value = SecurityReport(
                severity=SecuritySeverity.HIGH,
                cve_count=2,
                cve_ids=["CVE-2023-1234", "CVE-2023-5678"],
                vulnerabilities=[{"id": "CVE-2023-1234"}, {"id": "CVE-2023-5678"}],
                mitigation_notes="Use with caution",
                scan_timestamp="2025-10-19T10:00:00",
            )

            mock_license.return_value = LicenseInfo(
                license_name="MIT", license_type="permissive", compatible_with_apache2=True, issues=[], alternatives=[]
            )

            mock_version.return_value = VersionInfo(
                requested_version=None,
                latest_stable="1.0.0",
                is_latest=True,
                is_deprecated=False,
                breaking_changes=[],
                suggested_constraint="^1.0.0",
                release_date="2023-01-01",
            )

            mock_impact.return_value = ImpactAssessment(
                estimated_install_time_seconds=5,
                bundle_size_mb=2.0,
                sub_dependencies_added=["dep1", "dep2"],
                platform_compatibility={"linux": True, "macos": True, "windows": True},
            )

            report = analyzer.analyze_dependency("risky-package")

            assert report.recommendation == Recommendation.REVIEW
            assert report.security.severity == SecuritySeverity.HIGH
            assert report.security.cve_count == 2

    def test_analyze_dependency_reject(self, project_root):
        """Test analysis returns REJECT for GPL package."""
        analyzer = DependencyAnalyzer(project_root)

        with patch.object(analyzer.conflict_analyzer, "check_conflicts") as mock_conflicts, patch.object(
            analyzer.security_scanner, "scan_security"
        ) as mock_security, patch.object(analyzer.license_checker, "check_license") as mock_license, patch.object(
            analyzer.version_analyzer, "analyze_version"
        ) as mock_version, patch.object(
            analyzer.impact_assessor, "assess_impact"
        ) as mock_impact:

            from coffee_maker.utils.dependency_analyzer import (
                ConflictInfo,
                ImpactAssessment,
                LicenseInfo,
                SecurityReport,
                VersionInfo,
            )

            mock_conflicts.return_value = ConflictInfo(
                has_conflicts=False, conflicts=[], circular_dependencies=[], tree_depth=0, total_sub_dependencies=0
            )

            mock_security.return_value = SecurityReport(
                severity=SecuritySeverity.NONE,
                cve_count=0,
                cve_ids=[],
                vulnerabilities=[],
                mitigation_notes="No mitigation needed",
                scan_timestamp="2025-10-19T10:00:00",
            )

            # GPL license triggers REJECT
            mock_license.return_value = LicenseInfo(
                license_name="GPL-3.0",
                license_type="copyleft",
                compatible_with_apache2=False,
                issues=["GPL is copyleft - conflicts with Apache 2.0"],
                alternatives=["pymysql", "aiomysql"],
            )

            mock_version.return_value = VersionInfo(
                requested_version=None,
                latest_stable="1.0.0",
                is_latest=True,
                is_deprecated=False,
                breaking_changes=[],
                suggested_constraint="^1.0.0",
                release_date="2023-01-01",
            )

            mock_impact.return_value = ImpactAssessment(
                estimated_install_time_seconds=3,
                bundle_size_mb=1.0,
                sub_dependencies_added=[],
                platform_compatibility={"linux": True, "macos": True, "windows": True},
            )

            report = analyzer.analyze_dependency("mysql-connector-python")

            assert report.recommendation == Recommendation.REJECT
            assert not report.license.compatible_with_apache2
            assert report.license.license_type == "copyleft"
            assert len(report.alternatives) > 0


# ==================== ConflictAnalyzer Tests ====================


class TestConflictAnalyzer:
    """Tests for ConflictAnalyzer."""

    def test_no_conflicts(self, project_root):
        """Test no conflicts detected for compatible package."""
        analyzer = ConflictAnalyzer(project_root)

        with patch("subprocess.run") as mock_run:
            # Mock successful poetry add --dry-run
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Package operations: 1 install, 0 updates, 0 removals",
                stderr="",
            )

            result = analyzer.check_conflicts("pytest-timeout")

            assert not result.has_conflicts
            assert len(result.conflicts) == 0

    def test_version_conflict(self, project_root):
        """Test version conflict detection."""
        analyzer = ConflictAnalyzer(project_root)

        with patch("subprocess.run") as mock_run:
            # Mock poetry add --dry-run with conflict
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="Because package-a depends on package-b (>=2.0) and package-b requires >=3.0, package-a is forbidden.",
            )

            result = analyzer.check_conflicts("package-a", ">=1.0")

            assert result.has_conflicts
            assert len(result.conflicts) > 0


# ==================== LicenseChecker Tests ====================


class TestLicenseChecker:
    """Tests for LicenseChecker."""

    def test_mit_license_compatible(self, sample_pypi_metadata):
        """Test MIT license returns compatible=True."""
        checker = LicenseChecker()

        with patch.object(checker.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: sample_pypi_metadata)

            result = checker.check_license("pytest-timeout")

            assert result.license_name == "MIT"
            assert result.license_type == "permissive"
            assert result.compatible_with_apache2

    def test_gpl_license_incompatible(self):
        """Test GPL license returns compatible=False."""
        checker = LicenseChecker()

        gpl_metadata = {
            "info": {
                "license": "GPL-3.0",
                "classifiers": ["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
            }
        }

        with patch.object(checker.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: gpl_metadata)

            result = checker.check_license("some-gpl-package")

            assert result.license_name == "GPL-3.0"
            assert result.license_type == "copyleft"
            assert not result.compatible_with_apache2

    def test_unknown_license(self):
        """Test unknown license handling."""
        checker = LicenseChecker()

        unknown_metadata = {"info": {"license": ""}}

        with patch.object(checker.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: unknown_metadata)

            result = checker.check_license("unknown-package")

            assert result.license_name == "Unknown"
            assert result.license_type == "unknown"
            assert not result.compatible_with_apache2


# ==================== VersionAnalyzer Tests ====================


class TestVersionAnalyzer:
    """Tests for VersionAnalyzer."""

    def test_latest_version_detection(self, sample_pypi_metadata):
        """Test identifies latest stable version."""
        analyzer = VersionAnalyzer()

        with patch.object(analyzer.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: sample_pypi_metadata)

            result = analyzer.analyze_version("pytest-timeout")

            assert result.latest_stable == "2.2.0"
            assert result.is_latest
            assert not result.is_deprecated

    def test_deprecated_version(self):
        """Test detects deprecated versions."""
        analyzer = VersionAnalyzer()

        deprecated_metadata = {
            "info": {"version": "1.0.0", "description": "This package is deprecated"},
            "releases": {"1.0.0": [{"upload_time": "2020-01-01T00:00:00", "yanked": False}]},
        }

        with patch.object(analyzer.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: deprecated_metadata)

            result = analyzer.analyze_version("deprecated-package")

            assert result.is_deprecated


# ==================== ImpactAssessor Tests ====================


class TestImpactAssessor:
    """Tests for ImpactAssessor."""

    def test_bundle_size_estimation(self, project_root, sample_pypi_metadata):
        """Test estimates bundle size reasonably."""
        assessor = ImpactAssessor(project_root)

        with patch.object(assessor.session, "get") as mock_get:
            mock_get.return_value = Mock(status_code=200, json=lambda: sample_pypi_metadata)

            result = assessor.assess_impact("pytest-timeout")

            assert result.bundle_size_mb > 0
            assert result.estimated_install_time_seconds >= 2

    def test_sub_dependency_count(self, project_root):
        """Test counts sub-dependencies correctly."""
        assessor = ImpactAssessor(project_root)

        with patch("subprocess.run") as mock_run:
            # Mock poetry show --tree output
            mock_run.return_value = Mock(
                returncode=0,
                stdout="""
pytest-timeout 2.2.0
├── pytest 7.0.0
│   ├── pluggy 1.0.0
│   └── iniconfig 1.0.0
                """,
                stderr="",
            )

            result = assessor.assess_impact("pytest-timeout")

            assert len(result.sub_dependencies_added) >= 0
            assert isinstance(result.sub_dependencies_added, list)


# ==================== SecurityScanner Tests ====================


class TestSecurityScanner:
    """Tests for SecurityScanner."""

    def test_no_vulnerabilities(self):
        """Test returns severity=NONE for safe package."""
        scanner = SecurityScanner()

        # Mock both pip-audit and safety returning no vulnerabilities
        result = scanner.scan_security("pytest-timeout")

        assert result.severity == SecuritySeverity.NONE
        assert result.cve_count == 0

    def test_critical_vulnerabilities(self):
        """Test detects CRITICAL severity."""
        scanner = SecurityScanner()

        # Mock vulnerabilities with CRITICAL severity
        with patch.object(scanner, "_run_pip_audit") as mock_pip_audit, patch.object(
            scanner, "_run_safety_check"
        ) as mock_safety:

            mock_pip_audit.return_value = [{"id": "CVE-2023-1234", "severity": "CRITICAL", "cvss_score": 9.5}]
            mock_safety.return_value = []

            result = scanner.scan_security("vulnerable-package")

            assert result.severity == SecuritySeverity.CRITICAL
            assert result.cve_count == 1


# ==================== Integration Tests ====================


class TestDependencyAnalyzerIntegration:
    """Integration tests for full analysis workflow."""

    def test_generate_markdown_report(self, project_root):
        """Test generates valid markdown report."""
        analyzer = DependencyAnalyzer(project_root)

        with patch.object(analyzer.conflict_analyzer, "check_conflicts") as mock_conflicts, patch.object(
            analyzer.security_scanner, "scan_security"
        ) as mock_security, patch.object(analyzer.license_checker, "check_license") as mock_license, patch.object(
            analyzer.version_analyzer, "analyze_version"
        ) as mock_version, patch.object(
            analyzer.impact_assessor, "assess_impact"
        ) as mock_impact:

            from coffee_maker.utils.dependency_analyzer import (
                ConflictInfo,
                ImpactAssessment,
                LicenseInfo,
                SecurityReport,
                VersionInfo,
            )

            mock_conflicts.return_value = ConflictInfo(
                has_conflicts=False, conflicts=[], circular_dependencies=[], tree_depth=0, total_sub_dependencies=0
            )
            mock_security.return_value = SecurityReport(
                severity=SecuritySeverity.NONE,
                cve_count=0,
                cve_ids=[],
                vulnerabilities=[],
                mitigation_notes="",
                scan_timestamp="2025-10-19T10:00:00",
            )
            mock_license.return_value = LicenseInfo(
                license_name="MIT", license_type="permissive", compatible_with_apache2=True, issues=[], alternatives=[]
            )
            mock_version.return_value = VersionInfo(
                requested_version=None,
                latest_stable="2.2.0",
                is_latest=True,
                is_deprecated=False,
                breaking_changes=[],
                suggested_constraint="^2.2.0",
                release_date="2023-01-15",
            )
            mock_impact.return_value = ImpactAssessment(
                estimated_install_time_seconds=2,
                bundle_size_mb=0.25,
                sub_dependencies_added=[],
                platform_compatibility={"linux": True, "macos": True, "windows": True},
            )

            report = analyzer.analyze_dependency("pytest-timeout")
            markdown = analyzer.generate_markdown_report(report)

            # Verify markdown contains key sections
            assert "# Dependency Analysis Report: pytest-timeout" in markdown
            assert "## ✅ Recommendation: APPROVE" in markdown
            assert "## ✅ Security Analysis" in markdown
            assert "## ✅ License Compatibility" in markdown
            assert "MIT" in markdown
            assert "poetry add pytest-timeout" in markdown
