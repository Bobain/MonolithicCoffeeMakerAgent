"""Tests for coffee_maker/code_formatter/crewai/tools.py"""

from unittest import mock

import pytest
from pydantic import ValidationError

from github import GithubException

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
        """Test that missing GITHUB_TOKEN raises ValueError"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
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

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Auth")
    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_success(self, mock_github_class, mock_auth_class, monkeypatch):
        """Test successful posting of a suggestion"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        # Mock Auth.Token
        mock_auth_instance = mock.MagicMock()
        mock_auth_class.Token.return_value = mock_auth_instance

        # Mock GitHub API objects - use pr.head.sha instead of get_commits()
        mock_head = mock.MagicMock()
        mock_head.sha = "abc123"

        mock_pr = mock.MagicMock()
        mock_pr.head = mock_head
        mock_pr.create_review_comment.return_value = None
        mock_pr.get_files.return_value = [mock.MagicMock(filename="src/test.py")]

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

        # Verify API calls - now using Auth.Token and auth parameter
        mock_auth_class.Token.assert_called_once_with("fake_token")
        mock_github_class.assert_called_once_with(auth=mock_auth_instance)
        mock_github_instance.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_once_with(123)

        # Verify the review comment was created with correct formatting
        expected_body = "Consider this improvement\n```suggestion\nimproved code\n```"
        mock_pr.create_review_comment.assert_called_once_with(
            body=expected_body,
            commit="abc123",  # Changed from commit_id to commit
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

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Auth")
    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_multiline_suggestion(self, mock_github_class, mock_auth_class, monkeypatch):
        """Test posting a multi-line code suggestion"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        # Mock Auth.Token
        mock_auth_instance = mock.MagicMock()
        mock_auth_class.Token.return_value = mock_auth_instance

        # Use pr.head.sha instead of get_commits()
        mock_head = mock.MagicMock()
        mock_head.sha = "def456"

        mock_pr = mock.MagicMock()
        mock_pr.head = mock_head
        mock_pr.get_files.return_value = [mock.MagicMock(filename="app/main.py")]

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

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Auth")
    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_clears_pending_review_conflict(self, mock_github_class, mock_auth_class, monkeypatch):
        """Ensure the tool deletes an existing pending review and retries the comment."""

        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_auth_instance = mock.MagicMock()
        mock_auth_class.Token.return_value = mock_auth_instance

        pending_review = mock.MagicMock()
        pending_review.user.login = "bot"
        pending_review.state = "PENDING"

        conflict_exc = GithubException(
            status=422,
            data={
                "message": "Validation Failed",
                "errors": [
                    {
                        "resource": "PullRequestReview",
                        "code": "custom",
                        "field": "user_id",
                        "message": "user_id can only have one pending review per pull request",
                    }
                ],
            },
            headers=None,
        )

        mock_head = mock.MagicMock()
        mock_head.sha = "def456"

        mock_pr = mock.MagicMock()
        mock_pr.head = mock_head
        mock_pr.get_reviews.return_value = [pending_review]
        mock_pr.create_review_comment.side_effect = [conflict_exc, None]
        mock_pr.get_files.return_value = [mock.MagicMock(filename="app/utils.py")]

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_user = mock.MagicMock()
        mock_user.login = "bot"

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_instance.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github_instance

        tool = PostSuggestionToolLangAI()

        result = tool._run(
            repo_full_name="test/repo",
            pr_number=789,
            file_path="app/utils.py",
            start_line=5,
            end_line=6,
            suggestion_body="print('hello')",
            comment_text="Add logging",
        )

        assert result == "Successfully posted suggestion for app/utils.py in PR #789"
        pending_review.delete.assert_called_once()
        assert mock_pr.create_review_comment.call_count == 2

    @mock.patch("coffee_maker.code_formatter.crewai.tools.Auth")
    @mock.patch("coffee_maker.code_formatter.crewai.tools.Github")
    def test_run_invalid_path_error(self, mock_github_class, mock_auth_class, monkeypatch):
        """Ensure a clear error surfaces when the target file is not part of the PR."""

        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_auth_instance = mock.MagicMock()
        mock_auth_class.Token.return_value = mock_auth_instance

        mock_head = mock.MagicMock()
        mock_head.sha = "abc123"

        mock_pr = mock.MagicMock()
        mock_pr.head = mock_head
        mock_pr.get_reviews.return_value = []
        mock_pr.get_files.return_value = [mock.MagicMock(filename="another/path.py")]

        mock_repo = mock.MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

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
