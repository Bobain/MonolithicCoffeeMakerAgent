"""Tests for coffee_maker/code_formatter/crewai/tools.py"""

from unittest import mock

from github import GithubException
from pydantic import ValidationError
import pytest

from coffee_maker.code_formatter.crewai.tools import PostSuggestionInput, PostSuggestionToolLangAI
from coffee_maker.code_formatter.crewai.tools import PostSuggestionInput, PostSuggestionToolLangAI


class TestPostSuggestionInput:
    """Tests for PostSuggestionInput Pydantic model."""

    def test_valid_input(self) -> None:
        """Test creating PostSuggestionInput with valid data."""
        input_data = PostSuggestionInput(
            repo_full_name="owner/repo",
            pr_number=123,
            file_path="src/test.py",
            start_line=10,
            end_line=15,
            suggestion_body="improved code here",
            comment_text="Consider this improvement",
        )
        assert input_data.repo_full_name == "owner/repo"
        assert input_data.pr_number == 123
        assert input_data.file_path == "src/test.py"
        assert input_data.start_line == 10
        assert input_data.end_line == 15
        assert input_data.suggestion_body == "improved code here"
        assert input_data.comment_text == "Consider this improvement"

    def test_missing_required_field(self) -> None:
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PostSuggestionInput(
                repo_full_name="owner/repo",
                pr_number=123,
                # missing file_path
                start_line=10,
                end_line=15,
                suggestion_body="improved code",
                comment_text="comment",
            )


class TestPostSuggestionToolLangAI:
    """Tests for PostSuggestionToolLangAI CrewAI tool."""

    def test_tool_attributes(self) -> None:
        """Test that the tool has correct attributes."""
        tool = PostSuggestionToolLangAI()
        assert tool.name == "Post PR Review Suggestion Tool"
        assert "Post multi-line code suggestions on GitHub PRs" in tool.description
        assert tool.args_schema == PostSuggestionInput

    def test_run_missing_github_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that missing GITHUB_TOKEN raises ValueError."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        mocked = mock.Mock(side_effect=ValueError("Credentials for Github needed: GITHUB_TOKEN not defined."))
        monkeypatch.setattr(
            "coffee_maker.code_formatter.crewai.tools.post_suggestion_in_pr_review",
            mocked,
        )
        tool = PostSuggestionToolLangAI()

        with pytest.raises(ValueError, match="GITHUB_TOKEN not defined"):
            tool._run(
                repo_full_name="owner/repo",
                pr_number=123,
                file_path="src/test.py",
                start_line=10,
                end_line=15,
                suggestion_body="improved code",
                comment_text="Consider this",
            )

    def test_run_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful posting of a suggestion."""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
        mocked = mock.Mock(return_value="Successfully posted suggestion for src/test.py in PR #123")
        monkeypatch.setattr(
            "coffee_maker.code_formatter.crewai.tools.post_suggestion_in_pr_review",
            mocked,
        )

        tool = PostSuggestionToolLangAI()
        result = tool._run(
            repo_full_name="owner/repo",
            pr_number=123,
            file_path="src/test.py",
            start_line=10,
            end_line=15,
            suggestion_body="improved code",
            comment_text="Consider this improvement",
        )

        # Verify the result
        assert result == "Successfully posted suggestion for src/test.py in PR #123"

        mocked.assert_called_once_with(
            repo_full_name="owner/repo",
            pr_number=123,
            file_path="src/test.py",
            start_line=10,
            end_line=15,
            suggestion_body="improved code",
            comment_text="Consider this improvement",
        )

    def test_run_github_api_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling of GitHub API errors."""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
        mocked = mock.Mock(side_effect=GithubException(status=500, data={}, headers={}))
        monkeypatch.setattr(
            "coffee_maker.code_formatter.crewai.tools.post_suggestion_in_pr_review",
            mocked,
        )

        tool = PostSuggestionToolLangAI()

        with pytest.raises(GithubException):
            tool._run(
                repo_full_name="owner/repo",
                pr_number=123,
                file_path="src/test.py",
                start_line=10,
                end_line=15,
                suggestion_body="improved code",
                comment_text="Consider this",
            )

    def test_run_multiline_suggestion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test posting a multi-line code suggestion."""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
        mocked = mock.Mock(return_value="Successfully posted suggestion for app/main.py in PR #456")
        monkeypatch.setattr(
            "coffee_maker.code_formatter.crewai.tools.post_suggestion_in_pr_review",
            mocked,
        )

        tool = PostSuggestionToolLangAI()
        multiline_code = "def hello(name: str):\n    print(f'Hello, {name}!')"

        result = tool._run(
            repo_full_name="test/repo",
            pr_number=456,
            file_path="app/main.py",
            start_line=20,
            end_line=22,
            suggestion_body=multiline_code,
            comment_text="Improved function signature",
        )

        assert result == "Successfully posted suggestion for app/main.py in PR #456"
        mocked.assert_called_once()

    def test_run_invalid_path_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ensure a clear error surfaces when the target file is not part of the PR."""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mocked = mock.Mock(side_effect=ValueError("File path 'missing/file.py' not found in PR #789."))
        monkeypatch.setattr(
            "coffee_maker.code_formatter.crewai.tools.post_suggestion_in_pr_review",
            mocked,
        )

        tool = PostSuggestionToolLangAI()

        with pytest.raises(ValueError, match="not found in PR #789"):
            tool._run(
                repo_full_name="test/repo",
                pr_number=789,
                file_path="missing/file.py",
                start_line=1,
                end_line=2,
                suggestion_body="print('hello')",
                comment_text="Add output",
            )
