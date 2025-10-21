"""Unit tests for Git Workflow Automation."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coffee_maker.skills.git_workflow.commit_generator import CommitMessage
from coffee_maker.skills.git_workflow.git_workflow_automation import (
    GitWorkflowAutomation,
    GitWorkflowResult,
)
from coffee_maker.skills.git_workflow.pr_creator import PullRequest


@pytest.fixture
def git_workflow():
    """Create GitWorkflowAutomation instance."""
    return GitWorkflowAutomation(repo_path=Path("/tmp/test-repo"))


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for git commands."""
    with patch("subprocess.run") as mock_run:
        yield mock_run


class TestGitWorkflowAutomation:
    """Test GitWorkflowAutomation class."""

    def test_init(self, git_workflow):
        """Test initialization."""
        assert git_workflow.repo_path == Path("/tmp/test-repo")
        assert git_workflow.commit_generator is not None
        assert git_workflow.pr_creator is not None

    def test_verify_roadmap_branch_success(self, git_workflow, mock_subprocess_run):
        """Test roadmap branch verification succeeds."""
        mock_subprocess_run.return_value = Mock(stdout="roadmap\n", returncode=0)

        result = git_workflow._verify_roadmap_branch()

        assert result is True
        mock_subprocess_run.assert_called_once_with(
            ["git", "branch", "--show-current"],
            cwd=git_workflow.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

    def test_verify_roadmap_branch_failure(self, git_workflow, mock_subprocess_run):
        """Test roadmap branch verification fails when on wrong branch."""
        mock_subprocess_run.return_value = Mock(stdout="main\n", returncode=0)

        result = git_workflow._verify_roadmap_branch()

        assert result is False

    def test_verify_roadmap_branch_error(self, git_workflow, mock_subprocess_run):
        """Test roadmap branch verification handles errors."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git")

        result = git_workflow._verify_roadmap_branch()

        assert result is False

    def test_is_never_stage(self, git_workflow):
        """Test file exclusion logic."""
        # Secrets should never be staged
        assert git_workflow._is_never_stage(".env") is True
        assert git_workflow._is_never_stage("credentials.json") is True
        assert git_workflow._is_never_stage("secret.key") is True

        # Build artifacts should never be staged
        assert git_workflow._is_never_stage("__pycache__/test.pyc") is True
        assert git_workflow._is_never_stage(".pytest_cache/file") is True

        # Valid files should not be excluded
        # Need to mock _might_contain_secrets to avoid file I/O
        with patch.object(git_workflow, "_might_contain_secrets", return_value=False):
            assert git_workflow._is_never_stage("coffee_maker/test.py") is False
            assert git_workflow._is_never_stage("tests/test_unit.py") is False

    def test_should_stage(self, git_workflow):
        """Test file inclusion logic."""
        # Implementation files should be staged
        assert git_workflow._should_stage("coffee_maker/test.py") is True
        assert git_workflow._should_stage("tests/test_unit.py") is True
        assert git_workflow._should_stage("docs/README.md") is True
        assert git_workflow._should_stage(".claude/skills/test.md") is True
        assert git_workflow._should_stage("README.md") is True

        # Other files should not be staged
        assert git_workflow._should_stage("random.txt") is False

    def test_might_contain_secrets(self, git_workflow, tmp_path):
        """Test secret detection."""
        # Create test file with secrets
        git_workflow.repo_path = tmp_path
        test_file = tmp_path / "test.py"

        # File with API key should be detected
        test_file.write_text("API_KEY = 'sk-abcdefghijklmnopqrstuvwxyz123456'")
        assert git_workflow._might_contain_secrets("test.py") is True

        # File with password should be detected
        test_file.write_text("PASSWORD = 'my-secret-password'")
        assert git_workflow._might_contain_secrets("test.py") is True

        # File without secrets should pass
        test_file.write_text("def hello():\n    print('Hello')")
        assert git_workflow._might_contain_secrets("test.py") is False

    def test_generate_tag_name(self, git_workflow):
        """Test tag name generation."""
        assert git_workflow._generate_tag_name("US-067") == "wip-us-067"
        assert git_workflow._generate_tag_name("PRIORITY 10") == "wip-priority-10"
        assert git_workflow._generate_tag_name("TEST_FEATURE") == "wip-test-feature"

    def test_generate_pr_title(self, git_workflow):
        """Test PR title generation."""
        # With description
        title = git_workflow._generate_pr_title("US-067", "Implement git-workflow-automation Skill")
        assert title == "US-067: Implement git-workflow-automation Skill"

        # Without description
        title = git_workflow._generate_pr_title("US-067", "")
        assert title == "Implement US-067"

    @patch("coffee_maker.skills.git_workflow.git_workflow_automation.Path.read_text")
    @patch("coffee_maker.skills.git_workflow.git_workflow_automation.Path.write_text")
    @patch("coffee_maker.skills.git_workflow.git_workflow_automation.Path.exists")
    def test_update_roadmap_status(
        self,
        mock_exists,
        mock_write_text,
        mock_read_text,
        git_workflow,
        mock_subprocess_run,
    ):
        """Test ROADMAP.md update."""
        mock_exists.return_value = True
        mock_read_text.return_value = """
### US-067: Implement git-workflow-automation Skill 🔄 In Progress

Content here
"""
        mock_subprocess_run.return_value = Mock(returncode=0)

        result = git_workflow._update_roadmap_status(
            "US-067", "https://github.com/user/repo/pull/123", "data/dod_reports/dod.md"
        )

        assert result is True
        # Verify write_text was called
        assert mock_write_text.called
        # Verify content was updated
        updated_content = mock_write_text.call_args[0][0]
        assert "✅ Complete" in updated_content
        assert "PR**: #123" in updated_content
        assert "DoD**: Verified" in updated_content

    def test_create_commit_with_validation_success(self, git_workflow, mock_subprocess_run):
        """Test commit creation succeeds."""
        # Mock successful commit
        mock_subprocess_run.side_effect = [
            Mock(returncode=0),  # pre-commit hooks
            Mock(returncode=0),  # git commit
            Mock(stdout="abc123def\n", returncode=0),  # git rev-parse HEAD
        ]

        commit_msg = CommitMessage(
            type="feat",
            scope="skills",
            subject="Implement git workflow",
            body="Details here",
            footer="Footer",
        )

        commit_hash = git_workflow._create_commit_with_validation(commit_msg)

        assert commit_hash == "abc123def"

    def test_create_commit_with_validation_pre_commit_failure(self, git_workflow, mock_subprocess_run):
        """Test commit creation with pre-commit hook failure."""
        # Mock pre-commit failure, then success after auto-fix
        mock_subprocess_run.side_effect = [
            subprocess.CalledProcessError(1, "pre-commit"),  # pre-commit fails
            Mock(returncode=0),  # black (auto-fix)
            Mock(returncode=0),  # autoflake (auto-fix)
            Mock(returncode=0),  # git add -u (re-stage)
            Mock(returncode=0),  # git commit (success)
            Mock(stdout="abc123def\n", returncode=0),  # git rev-parse HEAD
        ]

        commit_msg = CommitMessage(
            type="feat",
            scope="skills",
            subject="Implement git workflow",
            body="Details here",
            footer="Footer",
        )

        commit_hash = git_workflow._create_commit_with_validation(commit_msg)

        assert commit_hash == "abc123def"

    def test_create_wip_tag_success(self, git_workflow, mock_subprocess_run):
        """Test WIP tag creation."""
        mock_subprocess_run.return_value = Mock(returncode=0)

        commit_msg = CommitMessage(
            type="feat",
            scope="skills",
            subject="Implement git workflow",
            body="Implementation complete",
            footer="Footer",
        )

        tag_name = git_workflow._create_wip_tag("US-067", commit_msg)

        assert tag_name == "wip-us-067"
        # Verify git tag command was called
        assert mock_subprocess_run.called

    def test_push_to_remote_success(self, git_workflow, mock_subprocess_run):
        """Test push to remote succeeds."""
        mock_subprocess_run.return_value = Mock(returncode=0)

        result = git_workflow._push_to_remote(tag_name="wip-us-067")

        assert result is True
        # Verify both push commands called
        assert mock_subprocess_run.call_count == 2
        mock_subprocess_run.assert_any_call(
            ["git", "push", "origin", "roadmap"],
            cwd=git_workflow.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        mock_subprocess_run.assert_any_call(
            ["git", "push", "origin", "wip-us-067"],
            cwd=git_workflow.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

    def test_push_to_remote_with_rebase(self, git_workflow, mock_subprocess_run):
        """Test push to remote with rebase on failure."""
        # First push fails, pull succeeds, retry push succeeds
        mock_subprocess_run.side_effect = [
            subprocess.CalledProcessError(1, "git"),  # push fails
            Mock(returncode=0),  # pull --rebase
            Mock(returncode=0),  # retry push (commits)
            Mock(returncode=0),  # retry push (tag)
        ]

        result = git_workflow._push_to_remote(tag_name="wip-us-067")

        assert result is True

    @patch.object(GitWorkflowAutomation, "_verify_roadmap_branch", return_value=True)
    @patch.object(GitWorkflowAutomation, "_stage_files_intelligently")
    @patch.object(GitWorkflowAutomation, "_create_commit_with_validation")
    @patch.object(GitWorkflowAutomation, "_create_wip_tag")
    @patch.object(GitWorkflowAutomation, "_push_to_remote")
    @patch.object(GitWorkflowAutomation, "_generate_pr_title")
    @patch.object(GitWorkflowAutomation, "_update_roadmap_status")
    def test_execute_success(
        self,
        mock_update_roadmap,
        mock_gen_pr_title,
        mock_push,
        mock_create_tag,
        mock_create_commit,
        mock_stage_files,
        mock_verify_branch,
        git_workflow,
    ):
        """Test full workflow execution succeeds."""
        # Setup mocks
        mock_stage_files.return_value = ["file1.py", "file2.py"]
        mock_create_commit.return_value = "abc123def"
        mock_create_tag.return_value = "wip-us-067"
        mock_push.return_value = True
        mock_gen_pr_title.return_value = "Implement US-067"
        mock_update_roadmap.return_value = True

        # Mock commit generator
        with patch.object(
            git_workflow.commit_generator,
            "generate",
            return_value=CommitMessage(
                type="feat",
                scope="skills",
                subject="Implement git workflow",
                body="Details",
                footer="Footer",
            ),
        ):
            # Mock PR creator
            with patch.object(
                git_workflow.pr_creator,
                "create",
                return_value=PullRequest(
                    number=123,
                    url="https://github.com/user/repo/pull/123",
                    title="Implement US-067",
                    body="PR body",
                    created=True,
                ),
            ):
                result = git_workflow.execute(
                    priority_name="US-067",
                    priority_description="Implement git-workflow-automation Skill",
                    dod_report_path="data/dod_reports/dod.md",
                )

        assert result.success is True
        assert result.commit_hash == "abc123def"
        assert result.tag_name == "wip-us-067"
        assert result.pr_number == 123
        assert result.pr_url == "https://github.com/user/repo/pull/123"
        assert result.roadmap_updated is True
        assert result.files_committed == 2

    @patch.object(GitWorkflowAutomation, "_verify_roadmap_branch", return_value=False)
    def test_execute_wrong_branch(self, mock_verify_branch, git_workflow):
        """Test execution fails when not on roadmap branch."""
        result = git_workflow.execute(
            priority_name="US-067",
            priority_description="Test",
        )

        assert result.success is False
        assert "CFR-013 violation" in result.error_message

    @patch.object(GitWorkflowAutomation, "_verify_roadmap_branch", return_value=True)
    @patch.object(GitWorkflowAutomation, "_stage_files_intelligently", return_value=[])
    def test_execute_no_files_staged(self, mock_stage_files, mock_verify_branch, git_workflow):
        """Test execution fails when no files staged."""
        result = git_workflow.execute(
            priority_name="US-067",
            priority_description="Test",
        )

        assert result.success is False
        assert "No files to commit" in result.error_message

    def test_get_all_changed_files(self, git_workflow, mock_subprocess_run):
        """Test getting all changed files."""
        # Mock different git commands
        mock_subprocess_run.side_effect = [
            Mock(stdout="file1.py\nfile2.py\n", returncode=0),  # staged
            Mock(stdout="file3.py\n", returncode=0),  # unstaged
            Mock(stdout="file4.py\nfile5.py\n", returncode=0),  # untracked
        ]

        files = git_workflow._get_all_changed_files()

        # Should return unique files
        assert len(files) == 5
        assert "file1.py" in files
        assert "file2.py" in files
        assert "file3.py" in files
        assert "file4.py" in files
        assert "file5.py" in files


class TestGitWorkflowResult:
    """Test GitWorkflowResult dataclass."""

    def test_init_success(self):
        """Test successful result initialization."""
        result = GitWorkflowResult(
            success=True,
            commit_hash="abc123",
            tag_name="wip-us-067",
            pr_number=123,
            pr_url="https://github.com/user/repo/pull/123",
            roadmap_updated=True,
            files_staged=["file1.py", "file2.py"],
            files_committed=2,
        )

        assert result.success is True
        assert result.commit_hash == "abc123"
        assert result.tag_name == "wip-us-067"
        assert result.pr_number == 123
        assert result.pr_url == "https://github.com/user/repo/pull/123"
        assert result.roadmap_updated is True
        assert len(result.files_staged) == 2
        assert result.files_committed == 2
        assert result.error_message is None

    def test_init_failure(self):
        """Test failed result initialization."""
        result = GitWorkflowResult(success=False, error_message="Test error")

        assert result.success is False
        assert result.error_message == "Test error"
        assert result.commit_hash is None
        assert result.tag_name is None
        assert result.pr_number is None
        assert result.pr_url is None
        assert result.roadmap_updated is False
        assert result.files_staged == []
        assert result.files_committed == 0

    def test_post_init_files_staged_default(self):
        """Test files_staged defaults to empty list."""
        result = GitWorkflowResult(success=True)

        assert result.files_staged == []
