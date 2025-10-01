"""Tests for coffee_maker/code_formatter/crewai/tools.py"""

from unittest import mock

import pytest
from pydantic import ValidationError

from coffee_maker.code_formatter.crewai.tools import PostSuggestionInput, PostSuggestionToolLangAI


class TestPostSuggestionInput:
    """Tests for PostSuggestionInput Pydantic model"""

    def test_valid_input(self):
        """Test creating PostSuggestionInput with valid data"""
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

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
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
    """Tests for PostSuggestionToolLangAI CrewAI tool"""

    def test_tool_attributes(self):
        """Test that the tool has correct attributes"""
        tool = PostSuggestionToolLangAI()
        assert tool.name == "Post PR Review Suggestion Tool"
        assert "Post multi-line code suggestions on GitHub PRs" in tool.description
        assert tool.args_schema == PostSuggestionInput

    def test_run_missing_github_token(self, monkeypatch):
        """Test that missing GITHUB_TOKEN returns error"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        tool = PostSuggestionToolLangAI()

        result = tool._run(
            repo_full_name="owner/repo",
            pr_number=123,
            file_path="src/test.py",
            start_line=10,
            end_line=15,
            suggestion_body="improved code",
            comment_text="Consider this",
        )

        assert result == "Error: GITHUB_TOKEN env var not set"

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_success(self, mock_github_class, monkeypatch):
        """Test successful posting of a suggestion"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        # Mock GitHub API objects
        mock_commit = mock.MagicMock()
        mock_commit.sha = "abc123"

        mock_pr = mock.MagicMock()
        mock_pr.get_commits.return_value = [mock_commit]
        mock_pr.create_review_comment.return_value = None

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo

        mock_github_class.return_value = mock_github_instance

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

        # Verify API calls
        mock_github_class.assert_called_once_with("fake_token")
        mock_github_instance.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_pr.get_commits.assert_called_once()

        # Verify the review comment was created with correct formatting
        expected_body = "Consider this improvement\n```suggestion\nimproved code\n```"
        mock_pr.create_review_comment.assert_called_once_with(
            body=expected_body,
            commit_id="abc123",
            path="src/test.py",
            start_line=10,
            line=15,
            side="RIGHT",
        )

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_github_api_error(self, mock_github_class, monkeypatch):
        """Test handling of GitHub API errors"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        # Mock GitHub API to raise an exception
        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.side_effect = Exception("API error")
        mock_github_class.return_value = mock_github_instance

        tool = PostSuggestionToolLangAI()

        # Should raise the exception (not caught in the tool)
        with pytest.raises(Exception, match="API error"):
            tool._run(
                repo_full_name="owner/repo",
                pr_number=123,
                file_path="src/test.py",
                start_line=10,
                end_line=15,
                suggestion_body="improved code",
                comment_text="Consider this",
            )

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_multiline_suggestion(self, mock_github_class, monkeypatch):
        """Test posting a multi-line code suggestion"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_commit = mock.MagicMock()
        mock_commit.sha = "def456"

        mock_pr = mock.MagicMock()
        mock_pr.get_commits.return_value = [mock_commit]

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

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

        # Verify the formatted suggestion includes the multiline code
        call_kwargs = mock_pr.create_review_comment.call_args[1]
        assert "```suggestion" in call_kwargs["body"]
        assert multiline_code in call_kwargs["body"]
        assert "Improved function signature" in call_kwargs["body"]
