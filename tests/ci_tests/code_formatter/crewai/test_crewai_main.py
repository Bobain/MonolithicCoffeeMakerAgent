"""Tests for coffee_maker/code_formatter/crewai/main.py"""

from types import SimpleNamespace
from unittest import mock

import pytest
from crewai import Agent

from coffee_maker.code_formatter.crewai.main import _get_pr_file_content, run_code_formatter


@pytest.fixture
def mock_agents():
    """Create real Agent instances for testing"""
    return {
        "senior_engineer": Agent(role="Senior Engineer", goal="Refactor code", backstory="Expert", verbose=False),
        "pull_request_reviewer": Agent(role="Reviewer", goal="Review PR", backstory="Expert", verbose=False),
    }


class TestGetPRFileContent:
    """Tests for _get_pr_file_content helper function"""

    def test_missing_github_token(self, monkeypatch, caplog):
        """Test that missing GITHUB_TOKEN is handled"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        result = _get_pr_file_content("owner/repo", 123, "src/file.py")

        assert result is None
        assert "GITHUB_TOKEN environment variable is not set" in caplog.text

    @mock.patch("coffee_maker.code_formatter.crewai.main.Auth")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_successful_file_fetch(self, mock_github_class, mock_auth_class, monkeypatch):
        """Test successful fetching of file content from GitHub"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_auth_instance = mock.MagicMock()
        mock_auth_class.Token.return_value = mock_auth_instance

        mock_contents = mock.MagicMock()
        mock_contents.decoded_content = b"def hello():\n    print('hello')"

        mock_pr = mock.MagicMock()
        mock_pr.head.sha = "abc123"

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_repo.get_contents.return_value = mock_contents

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        result = _get_pr_file_content("owner/repo", 123, "src/test.py")

        assert result == "def hello():\n    print('hello')"
        mock_auth_class.Token.assert_called_once_with("fake_token")
        mock_github_class.assert_called_once_with(auth=mock_auth_instance)
        mock_github_instance.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_repo.get_contents.assert_called_once_with("src/test.py", ref="abc123")

    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_github_api_error(self, mock_github_class, monkeypatch, caplog):
        """Test handling of GitHub API errors"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.side_effect = Exception("Repository not found")
        mock_github_class.return_value = mock_github_instance

        result = _get_pr_file_content("owner/nonexistent", 123, "file.py")

        assert result is None
        assert "Could not fetch content" in caplog.text
        assert "file.py" in caplog.text

    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_file_not_found(self, mock_github_class, monkeypatch, caplog):
        """Test handling when file doesn't exist in PR"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock.MagicMock(head=mock.MagicMock(sha="abc123"))
        mock_repo.get_contents.side_effect = Exception("404: Not Found")

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        result = _get_pr_file_content("owner/repo", 123, "nonexistent.py")

        assert result is None
        assert "Could not fetch content" in caplog.text


class TestRunCodeFormatter:
    """Tests for run_code_formatter orchestration function"""

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_flow")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    def test_successful_run_single_file(
        self,
        mock_langfuse_client,
        mock_create_flow,
        mock_create_reviewer,
        mock_create_formatter,
        mock_get_content,
        mock_get_modified_files,
        mock_agents,
    ):
        """Flow executes once and returns formatter/reviewer outputs."""

        mock_get_modified_files.return_value = ["src/test.py", "README.md"]
        mock_get_content.return_value = "def test():\n    pass"
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        mock_flow = mock.MagicMock()
        mock_flow.state = SimpleNamespace(
            reformat_result="formatted output",
            review_result="review output",
            reformat_prompt="formatter prompt",
        )
        mock_create_flow.return_value = mock_flow

        mock_langfuse_client.update_current_trace.return_value = None
        mock_langfuse_client.trace.return_value = None
        mock_langfuse_client.flush.return_value = None

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        assert result == [
            {
                "file_path": "src/test.py",
                "reformat_result": "formatted output",
                "review_result": "review output",
            }
        ]
        mock_get_modified_files.assert_called_once_with("owner/repo", 123)
        mock_get_content.assert_called_once_with("owner/repo", 123, "src/test.py")
        mock_create_reviewer.assert_called_once_with(mock_langfuse_client, 123, "owner/repo", "src/test.py")
        mock_create_flow.assert_called_once_with(
            formatter_agent=mock_agents["senior_engineer"],
            reviewer_agent=mock_agents["pull_request_reviewer"],
            langfuse_client=mock_langfuse_client,
            file_path="src/test.py",
            repo_full_name="owner/repo",
            pr_number=123,
            file_content="def test():\n    pass",
        )
        mock_flow.kickoff.assert_called_once()
        mock_langfuse_client.update_current_trace.assert_called_once()
        mock_langfuse_client.trace.assert_called_once()
        mock_langfuse_client.flush.assert_called_once()

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_flow")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    def test_run_multiple_files(
        self,
        mock_langfuse_client,
        mock_create_flow,
        mock_create_reviewer,
        mock_create_formatter,
        mock_get_content,
        mock_get_modified_files,
        mock_agents,
    ):
        """Multiple modified files trigger multiple flow executions."""

        file_list = ["src/file1.py", "src/file2.py"]
        mock_get_modified_files.return_value = file_list + ["README.md"]
        mock_get_content.side_effect = ["code1", "code2"]
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        flow1 = mock.MagicMock()
        flow1.state = SimpleNamespace(reformat_result="fmt1", review_result="rev1", reformat_prompt="prompt1")
        flow2 = mock.MagicMock()
        flow2.state = SimpleNamespace(reformat_result="fmt2", review_result="rev2", reformat_prompt="prompt2")
        mock_create_flow.side_effect = [flow1, flow2]

        mock_langfuse_client.flush.return_value = None

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=456)

        assert result == [
            {"file_path": "src/file1.py", "reformat_result": "fmt1", "review_result": "rev1"},
            {"file_path": "src/file2.py", "reformat_result": "fmt2", "review_result": "rev2"},
        ]
        assert mock_create_flow.call_count == 2
        flow1.kickoff.assert_called_once()
        flow2.kickoff.assert_called_once()

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_flow")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    def test_skip_files_with_no_content(
        self,
        mock_langfuse_client,
        mock_create_flow,
        mock_create_reviewer,
        mock_create_formatter,
        mock_get_content,
        mock_get_modified_files,
        mock_agents,
    ):
        """Files without content are skipped and do not execute flows."""

        mock_get_modified_files.return_value = ["src/missing.py", "src/existing.py", "README.md"]
        mock_get_content.side_effect = [None, "code"]
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        flow = mock.MagicMock()
        flow.state = SimpleNamespace(reformat_result="fmt", review_result="rev", reformat_prompt="prompt")
        mock_create_flow.return_value = flow

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        assert result == [{"file_path": "src/existing.py", "reformat_result": "fmt", "review_result": "rev"}]
        mock_create_flow.assert_called_once()

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_flow")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    def test_no_flows_executed_returns_none(
        self,
        mock_langfuse_client,
        mock_create_flow,
        mock_create_reviewer,
        mock_create_formatter,
        mock_get_content,
        mock_get_modified_files,
        mock_agents,
    ):
        """When all content fetches fail, the function returns None."""

        mock_get_modified_files.return_value = ["src/missing.py", "README.md"]
        mock_get_content.return_value = None
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        mock_langfuse_client.flush.return_value = None

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=789)

        assert result is None
        mock_create_flow.assert_not_called()
        mock_langfuse_client.flush.assert_called_once()

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_flow")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    def test_missing_formatter_agent_returns_none(
        self,
        mock_langfuse_client,
        mock_create_flow,
        mock_create_reviewer,
        mock_create_formatter,
        mock_get_content,
        mock_get_modified_files,
    ):
        """If the formatter agent is missing, execution aborts."""

        mock_get_modified_files.return_value = ["src/test.py", "README.md"]
        mock_get_content.return_value = "code"
        mock_create_formatter.return_value = {}

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=111)

        assert result is None
        mock_create_reviewer.assert_not_called()
        mock_create_flow.assert_not_called()
