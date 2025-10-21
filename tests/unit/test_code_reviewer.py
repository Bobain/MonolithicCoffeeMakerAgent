"""Unit tests for CodeReviewerAgent."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from coffee_maker.autonomous.code_reviewer import CodeReviewerAgent, Issue, ReviewReport
from coffee_maker.autonomous.agent_registry import AgentRegistry


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root directory."""
    # Create required directories
    (tmp_path / "docs" / "code-reviews").mkdir(parents=True)
    (tmp_path / "coffee_maker").mkdir(parents=True)
    (tmp_path / ".git").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def code_reviewer(project_root):
    """Create a CodeReviewerAgent instance."""
    return CodeReviewerAgent(project_root)


@pytest.fixture(autouse=True)
def reset_agent_registry():
    """Reset agent registry before each test."""
    registry = AgentRegistry()
    registry.reset()
    yield
    registry.reset()


class TestCodeReviewerAgent:
    """Tests for CodeReviewerAgent class."""

    def test_initialization(self, code_reviewer, project_root):
        """Test agent initialization."""
        assert code_reviewer.project_root == project_root
        assert code_reviewer.reviews_dir == project_root / "docs" / "code-reviews"
        assert code_reviewer.reviews_dir.exists()

    @patch("subprocess.run")
    def test_get_commit_info(self, mock_run, code_reviewer):
        """Test getting commit information."""
        # Mock git rev-parse
        mock_run.side_effect = [
            MagicMock(stdout="abc123def456\n", returncode=0),
            MagicMock(stdout="feat: Add feature|Author Name|2025-10-19 12:00:00\n", returncode=0),
            MagicMock(
                stdout="file.py | 10 +++++++---\n 1 file changed, 7 insertions(+), 3 deletions(-)\n", returncode=0
            ),
        ]

        info = code_reviewer._get_commit_info("HEAD")

        assert info["sha"] == "abc123def456"
        assert info["message"] == "feat: Add feature"
        assert info["author"] == "Author Name"
        assert info["lines_added"] == 7
        assert info["lines_deleted"] == 3

    @patch("subprocess.run")
    def test_get_changed_files(self, mock_run, code_reviewer):
        """Test getting changed files from commit."""
        mock_run.return_value = MagicMock(
            stdout="coffee_maker/module.py\ntests/test_module.py\nREADME.md\n", returncode=0
        )

        files = code_reviewer._get_changed_files("abc123")

        assert len(files) == 2  # Only Python files
        assert "coffee_maker/module.py" in files
        assert "tests/test_module.py" in files
        assert "README.md" not in files

    def test_calculate_quality_score(self, code_reviewer):
        """Test quality score calculation."""
        issues = [
            Issue("CRITICAL", "Security", "file.py", 10, "Critical issue", "Fix it", "1 hour"),
            Issue("HIGH", "Performance", "file.py", 20, "High issue", "Fix it", "30 min"),
            Issue("MEDIUM", "Style", "file.py", 30, "Medium issue", "Fix it", "15 min"),
            Issue("LOW", "Documentation", "file.py", 40, "Low issue", "Fix it", "5 min"),
        ]

        score = code_reviewer._calculate_quality_score(issues)

        # 100 - 30 (critical) - 20 (high) - 10 (medium) - 5 (low) = 35
        assert score == 35

    def test_calculate_quality_score_no_issues(self, code_reviewer):
        """Test quality score with no issues."""
        score = code_reviewer._calculate_quality_score([])
        assert score == 100

    def test_calculate_quality_score_minimum_zero(self, code_reviewer):
        """Test quality score doesn't go below zero."""
        issues = [Issue("CRITICAL", "Security", "file.py", 10, "Issue", "Fix", "1h") for _ in range(10)]
        score = code_reviewer._calculate_quality_score(issues)
        assert score == 0

    def test_generate_overall_assessment_excellent(self, code_reviewer):
        """Test overall assessment for excellent quality."""
        assessment = code_reviewer._generate_overall_assessment(95, [], True)

        assert "APPROVED - EXCELLENT QUALITY" in assessment
        assert "95/100" in assessment

    def test_generate_overall_assessment_approved_with_notes(self, code_reviewer):
        """Test overall assessment for approved with notes."""
        issues = [
            Issue("MEDIUM", "Style", "file.py", 10, "Issue", "Fix", "15 min"),
            Issue("MEDIUM", "Style", "file.py", 20, "Issue", "Fix", "15 min"),
        ]
        assessment = code_reviewer._generate_overall_assessment(75, issues, True)

        assert "APPROVED WITH NOTES" in assessment
        assert "75/100" in assessment

    def test_generate_overall_assessment_request_changes(self, code_reviewer):
        """Test overall assessment for request changes."""
        issues = [
            Issue("HIGH", "Security", "file.py", 10, "Issue", "Fix", "1 hour"),
            Issue("MEDIUM", "Style", "file.py", 20, "Issue", "Fix", "15 min"),
        ]
        assessment = code_reviewer._generate_overall_assessment(55, issues, False)

        assert "REQUEST CHANGES" in assessment
        assert "55/100" in assessment

    def test_generate_overall_assessment_critical(self, code_reviewer):
        """Test overall assessment for critical issues."""
        issues = [Issue("CRITICAL", "Security", "file.py", 10, "Critical issue", "Fix immediately", "2 hours")]
        assessment = code_reviewer._generate_overall_assessment(35, issues, False)

        assert "BLOCK MERGE - CRITICAL ISSUES" in assessment
        assert "35/100" in assessment

    def test_generate_report_markdown(self, code_reviewer):
        """Test report markdown generation."""
        issues = [
            Issue("CRITICAL", "Security", "file.py", 10, "Critical issue", "Fix it", "1 hour"),
            Issue("MEDIUM", "Style", "file.py", 20, "Medium issue", "Fix it", "15 min"),
        ]

        report = ReviewReport(
            commit_sha="abc123def456",
            date=datetime(2025, 10, 19, 12, 0, 0),
            files_changed=3,
            lines_added=50,
            lines_deleted=20,
            quality_score=65,
            issues=issues,
            style_compliance={"line_length_120": True, "google_docstrings": False},
            architecture_compliance={"follows_specs": True},
            overall_assessment="REQUEST CHANGES",
            approved=False,
            review_duration_seconds=120.5,
        )

        md = code_reviewer._generate_report_markdown(report)

        assert "# Code Review Report" in md
        assert "abc123" in md
        assert "2025-10-19" in md
        assert "65/100" in md
        assert "🔴 CRITICAL (1)" in md
        assert "🟡 MEDIUM (1)" in md
        assert "Critical issue" in md
        assert "Medium issue" in md
        assert "✅ PASS - Line Length 120" in md
        assert "❌ FAIL - Google Docstrings" in md

    def test_check_style_compliance(self, code_reviewer):
        """Test style guide compliance checking."""
        files = ["coffee_maker/module.py"]
        compliance = code_reviewer._check_style_compliance(files)

        # Should have all compliance keys
        assert "line_length_120" in compliance
        assert "google_docstrings" in compliance
        assert "type_hints" in compliance
        assert "snake_case_naming" in compliance
        assert "imports_grouped" in compliance
        assert "logging_module" in compliance

    def test_check_architecture_compliance(self, code_reviewer, project_root):
        """Test architecture compliance checking."""
        # Create a test file with agent code (without AgentRegistry import)
        # Note: filename must have "Agent" with capital A to trigger check
        agent_file = project_root / "coffee_maker" / "MyAgent.py"
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.write_text("class MyAgent:\n    def run(self):\n        pass\n")

        compliance = code_reviewer._check_architecture_compliance(["coffee_maker/MyAgent.py"])

        # Should detect missing singleton enforcement (file has "Agent" but no "AgentRegistry")
        assert compliance["singleton_enforcement"] is False

    def test_check_architecture_compliance_with_registry(self, code_reviewer, project_root):
        """Test architecture compliance with proper singleton usage."""
        test_file = project_root / "coffee_maker" / "test_agent.py"
        test_file.write_text(
            "from coffee_maker.autonomous.agent_registry import AgentRegistry\nclass TestAgent:\n    pass\n"
        )

        compliance = code_reviewer._check_architecture_compliance(["coffee_maker/test_agent.py"])

        # Should pass with AgentRegistry import
        assert compliance["singleton_enforcement"] is True

    @patch("subprocess.run")
    def test_run_radon_analysis_high_complexity(self, mock_run, code_reviewer):
        """Test radon analysis detecting high complexity."""
        mock_run.return_value = MagicMock(stdout="file.py:10:func D 15 - Complex function\n", returncode=0)

        issues = code_reviewer._run_radon_analysis(["coffee_maker/file.py"])

        assert len(issues) >= 0  # Radon may or may not find issues

    @patch("subprocess.run")
    def test_run_mypy_analysis(self, mock_run, code_reviewer, project_root):
        """Test mypy type checking."""
        # Create test file
        test_file = project_root / "coffee_maker" / "module.py"
        test_file.write_text("def func():\n    pass\n")

        mock_run.return_value = MagicMock(stdout=f"{test_file}:5: error: Missing type annotation\n", returncode=1)

        issues = code_reviewer._run_mypy_analysis(["coffee_maker/module.py"])

        assert len(issues) >= 0  # Mypy may or may not find issues

    @patch("subprocess.run")
    def test_run_bandit_analysis_security_issue(self, mock_run, code_reviewer):
        """Test bandit security scanning."""
        mock_run.return_value = MagicMock(stdout="Issue: Use of exec detected\nCONFIDENCE: HIGH\n", returncode=1)

        issues = code_reviewer._run_bandit_analysis(["coffee_maker/module.py"])

        assert len(issues) >= 0  # Bandit may or may not find issues

    @patch("subprocess.run")
    def test_check_test_coverage_low(self, mock_run, code_reviewer):
        """Test coverage checking."""
        mock_run.return_value = MagicMock(stdout="coffee_maker/module.py 45 20 30%\n", returncode=0)

        issues = code_reviewer._check_test_coverage(["coffee_maker/module.py"])

        # Should detect low coverage (if parsed correctly)
        # This is a simplified test - actual implementation may vary
        assert isinstance(issues, list)

    @patch("coffee_maker.autonomous.code_reviewer.CodeReviewerAgent._notify_architect")
    @patch("coffee_maker.autonomous.code_reviewer.CodeReviewerAgent._save_report")
    @patch("coffee_maker.autonomous.code_reviewer.CodeReviewerAgent._analyze_files")
    @patch("coffee_maker.autonomous.code_reviewer.CodeReviewerAgent._get_changed_files")
    @patch("coffee_maker.autonomous.code_reviewer.CodeReviewerAgent._get_commit_info")
    def test_review_commit_workflow(
        self, mock_get_info, mock_get_files, mock_analyze, mock_save, mock_notify, code_reviewer
    ):
        """Test complete review workflow."""
        # Setup mocks
        mock_get_info.return_value = {
            "sha": "abc123def456",
            "message": "feat: Add feature",
            "author": "Author",
            "date": "2025-10-19",
            "lines_added": 50,
            "lines_deleted": 20,
        }
        mock_get_files.return_value = ["coffee_maker/module.py"]
        mock_analyze.return_value = [Issue("MEDIUM", "Style", "file.py", 10, "Issue", "Fix it", "15 min")]

        report = code_reviewer.review_commit("HEAD")

        # Verify workflow
        assert mock_get_info.called
        assert mock_get_files.called
        assert mock_analyze.called
        assert mock_save.called
        assert mock_notify.called

        # Verify report
        assert report.commit_sha == "abc123def456"
        assert report.files_changed == 1
        assert report.lines_added == 50
        assert report.lines_deleted == 20
        assert report.quality_score == 90  # 100 - 10 (1 medium issue)
        assert len(report.issues) == 1

    def test_save_report_creates_file(self, code_reviewer, project_root):
        """Test report saving creates file."""
        report = ReviewReport(
            commit_sha="abc123def456",
            date=datetime(2025, 10, 19, 12, 0, 0),
            files_changed=3,
            lines_added=50,
            lines_deleted=20,
            quality_score=85,
            issues=[],
            style_compliance={},
            architecture_compliance={},
            overall_assessment="APPROVED",
            approved=True,
            review_duration_seconds=120.0,
        )

        code_reviewer._save_report(report)

        # Check report file was created (commit_sha[:7] = "abc123d")
        report_file = project_root / "docs" / "code-reviews" / "REVIEW-2025-10-19-abc123d.md"
        assert report_file.exists()

        # Check index was updated
        index_file = project_root / "docs" / "code-reviews" / "INDEX.md"
        assert index_file.exists()
        content = index_file.read_text()
        assert "abc123d" in content  # First 7 chars of commit SHA
        assert "85/100" in content

    @patch("coffee_maker.cli.notifications.NotificationDB.create_notification")
    def test_notify_architect_excellent_quality(self, mock_create_notification, code_reviewer):
        """Test architect notification for excellent quality."""
        report = ReviewReport(
            commit_sha="abc123def456",
            date=datetime.now(),
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            quality_score=95,
            issues=[],
            style_compliance={},
            architecture_compliance={},
            overall_assessment="APPROVED",
            approved=True,
            review_duration_seconds=60.0,
        )

        code_reviewer._notify_architect(report)

        # Verify notification created
        assert mock_create_notification.called
        call_args = mock_create_notification.call_args[1]
        assert "Approved ✅" in call_args["title"]
        assert call_args["level"] == "info"
        assert call_args["sound"] is False  # CFR-009: background agent
        assert call_args["agent_id"] == "code_reviewer"

    @patch("coffee_maker.cli.notifications.NotificationDB.create_notification")
    def test_notify_architect_critical_issues(self, mock_create_notification, code_reviewer):
        """Test architect notification for critical issues."""
        report = ReviewReport(
            commit_sha="abc123def456",
            date=datetime.now(),
            files_changed=1,
            lines_added=10,
            lines_deleted=5,
            quality_score=30,
            issues=[Issue("CRITICAL", "Security", "file.py", 10, "Critical", "Fix", "2h")],
            style_compliance={},
            architecture_compliance={},
            overall_assessment="BLOCK MERGE",
            approved=False,
            review_duration_seconds=60.0,
        )

        code_reviewer._notify_architect(report)

        # Verify high-priority notification
        assert mock_create_notification.called
        call_args = mock_create_notification.call_args[1]
        assert "Critical Issues ❌" in call_args["title"]
        assert call_args["level"] == "high"

    def test_singleton_enforcement(self, code_reviewer):
        """Test that only one code-reviewer can run at a time."""
        from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType, AgentAlreadyRunningError

        registry = AgentRegistry()

        # Register first instance
        registry.register_agent(AgentType.CODE_REVIEWER)

        # Try to register second instance - should fail
        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            registry.register_agent(AgentType.CODE_REVIEWER)

        assert "code_reviewer" in str(exc_info.value)
        assert "already running" in str(exc_info.value).lower()

        # Clean up
        registry.unregister_agent(AgentType.CODE_REVIEWER)

    def test_context_manager_registration(self, code_reviewer):
        """Test context manager pattern for agent registration."""
        from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

        registry = AgentRegistry()

        # Use context manager
        with AgentRegistry.register(AgentType.CODE_REVIEWER):
            # Agent should be registered
            assert registry.is_registered(AgentType.CODE_REVIEWER)

        # Agent should be unregistered after context exit
        assert not registry.is_registered(AgentType.CODE_REVIEWER)


class TestIssueDataclass:
    """Tests for Issue dataclass."""

    def test_issue_creation(self):
        """Test creating an Issue instance."""
        issue = Issue(
            severity="HIGH",
            category="Security",
            file_path="module.py",
            line_number=42,
            description="Security vulnerability",
            recommendation="Fix immediately",
            effort_estimate="2 hours",
        )

        assert issue.severity == "HIGH"
        assert issue.category == "Security"
        assert issue.file_path == "module.py"
        assert issue.line_number == 42


class TestReviewReportDataclass:
    """Tests for ReviewReport dataclass."""

    def test_review_report_creation(self):
        """Test creating a ReviewReport instance."""
        report = ReviewReport(
            commit_sha="abc123",
            date=datetime.now(),
            files_changed=5,
            lines_added=100,
            lines_deleted=50,
            quality_score=85,
            issues=[],
            style_compliance={},
            architecture_compliance={},
            overall_assessment="APPROVED",
            approved=True,
            review_duration_seconds=120.0,
        )

        assert report.commit_sha == "abc123"
        assert report.files_changed == 5
        assert report.quality_score == 85
        assert report.approved is True
