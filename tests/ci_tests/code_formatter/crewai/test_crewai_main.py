"""Tests for coffee_maker/code_formatter/crewai/main.py"""

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

    def test_missing_github_token(self, monkeypatch, capsys):
        """Test that missing GITHUB_TOKEN is handled"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        result = _get_pr_file_content("owner/repo", 123, "src/file.py")

        assert result is None
        captured = capsys.readouterr()
        assert "GITHUB_TOKEN environment variable is not set" in captured.out

    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_successful_file_fetch(self, mock_github_class, monkeypatch):
        """Test successful fetching of file content from GitHub"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        # Mock the GitHub API chain
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
        mock_github_class.assert_called_once_with("fake_token")
        mock_github_instance.get_repo.assert_called_once_with("owner/repo")
        mock_repo.get_pull.assert_called_once_with(123)
        mock_repo.get_contents.assert_called_once_with("src/test.py", ref="abc123")

    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_github_api_error(self, mock_github_class, monkeypatch, capsys):
        """Test handling of GitHub API errors"""
        monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

        mock_github_instance = mock.MagicMock()
        mock_github_instance.get_repo.side_effect = Exception("Repository not found")
        mock_github_class.return_value = mock_github_instance

        result = _get_pr_file_content("owner/nonexistent", 123, "file.py")

        assert result is None
        captured = capsys.readouterr()
        assert "Could not fetch content" in captured.out
        assert "file.py" in captured.out

    @mock.patch("coffee_maker.code_formatter.crewai.main.Github")
    def test_file_not_found(self, mock_github_class, monkeypatch, capsys):
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
        captured = capsys.readouterr()
        assert "Could not fetch content" in captured.out


class TestRunCodeFormatter:
    """Tests for run_code_formatter orchestration function"""

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_successful_run_single_file(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_langfuse_client,
        mock_create_refactor_task,
        mock_create_review_task,
        mock_agents,
    ):
        """Test successful execution with a single file"""
        # Mock the callback handler
        mock_handler = mock.MagicMock()
        mock_callback_handler.return_value = mock_handler

        # Mock PR modified files retrieval
        mock_get_modified_files.return_value = ["src/test.py"]

        # Mock file content retrieval
        mock_get_content.return_value = "def test():\n    pass"

        # Mock agent creation with real agents
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        # Mock crew execution
        mock_crew_instance = mock.MagicMock()
        mock_crew_instance.kickoff.return_value = "Success"
        mock_crew_class.return_value = mock_crew_instance

        # Mock Langfuse client
        mock_langfuse_client.flush.return_value = None
        mock_langfuse_client.update_current_trace.return_value = None

        # Mock task creation
        mock_refactor_task_instance = mock.MagicMock()
        mock_review_task_instance = mock.MagicMock()
        mock_create_refactor_task.return_value = mock_refactor_task_instance
        mock_create_review_task.return_value = mock_review_task_instance

        result = run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        # Verify the result
        assert result == "Success"

        # Verify modified files were fetched
        mock_get_modified_files.assert_called_once_with("owner/repo", 123)

        # Verify file content was fetched
        mock_get_content.assert_called_once_with("owner/repo", 123, "src/test.py")

        # Verify crew was created and kicked off
        mock_crew_class.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_run_multiple_files(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_langfuse_client,
        mock_create_refactor_task,
        mock_create_review_task,
        mock_agents,
    ):
        """Test execution with multiple files creates multiple task pairs"""
        mock_callback_handler.return_value = mock.MagicMock()

        # Mock PR modified files
        file_list = ["src/file1.py", "src/file2.py", "src/file3.py"]
        mock_get_modified_files.return_value = file_list

        # Mock file content retrieval for multiple files
        file_contents = {
            "src/file1.py": "def func1(): pass",
            "src/file2.py": "def func2(): pass",
            "src/file3.py": "def func3(): pass",
        }
        mock_get_content.side_effect = lambda repo, pr, path: file_contents.get(path)

        # Mock agents
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        mock_crew_instance = mock.MagicMock()
        mock_crew_instance.kickoff.return_value = "Success"
        mock_crew_class.return_value = mock_crew_instance

        mock_langfuse_client.flush.return_value = None
        mock_langfuse_client.update_current_trace.return_value = None

        # Mock task creation
        mock_refactor_task_instance = mock.MagicMock()
        mock_review_task_instance = mock.MagicMock()
        mock_create_refactor_task.return_value = mock_refactor_task_instance
        mock_create_review_task.return_value = mock_review_task_instance

        run_code_formatter(repo_full_name="owner/repo", pr_number=456)

        # Verify modified files were fetched
        mock_get_modified_files.assert_called_once_with("owner/repo", 456)

        # Verify all files were fetched
        assert mock_get_content.call_count == 3

        # Verify crew was created with tasks (2 tasks per file: refactor + review)
        crew_call_kwargs = mock_crew_class.call_args[1]
        tasks = crew_call_kwargs["tasks"]
        assert len(tasks) == 6  # 3 files * 2 tasks each

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_skip_files_with_no_content(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_create_refactor_task,
        mock_create_review_task,
        capsys,
        mock_agents,
    ):
        """Test that files that can't be fetched are skipped"""
        mock_callback_handler.return_value = mock.MagicMock()

        # Mock PR modified files
        mock_get_modified_files.return_value = ["src/missing.py", "src/existing.py"]

        # Mock some files returning None (fetch failed)
        def get_content_side_effect(repo, pr, path):
            if path == "src/missing.py":
                return None
            return "def test(): pass"

        mock_get_content.side_effect = get_content_side_effect

        # Mock agents
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        # Mock crew
        mock_crew_instance = mock.MagicMock()
        mock_crew_instance.kickoff.return_value = "Success"
        mock_crew_class.return_value = mock_crew_instance

        # Mock task creation
        mock_refactor_task_instance = mock.MagicMock()
        mock_review_task_instance = mock.MagicMock()
        mock_create_refactor_task.return_value = mock_refactor_task_instance
        mock_create_review_task.return_value = mock_review_task_instance

        # Mock Langfuse to avoid initialization issues
        with mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client") as mock_langfuse:
            mock_langfuse.flush.return_value = None
            mock_langfuse.update_current_trace.return_value = None

            run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        # Verify modified files were fetched
        mock_get_modified_files.assert_called_once_with("owner/repo", 123)

        # Should have tried to fetch both files
        assert mock_get_content.call_count == 2

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_no_tasks_created(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_create_refactor_task,
        mock_create_review_task,
        capsys,
        mock_agents,
    ):
        """Test handling when no tasks can be created (all files failed to fetch)"""
        mock_callback_handler.return_value = mock.MagicMock()
        mock_get_modified_files.return_value = ["src/missing.py"]
        mock_get_content.return_value = None  # All fetches fail

        # Mock agents
        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        # Mock Langfuse
        with mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client") as mock_langfuse:
            mock_langfuse.flush.return_value = None

            result = run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        assert result is None
        captured = capsys.readouterr()
        assert "No tasks were created" in captured.out

    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_callback_handler_error(self, mock_callback_handler, mock_get_modified_files, capsys):
        """Test handling of CallbackHandler initialization errors"""
        mock_callback_handler.side_effect = Exception("Langfuse connection error")
        mock_get_modified_files.return_value = ["file.py"]

        # Mock Langfuse
        with mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client"):
            result = run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        assert result is None
        captured = capsys.readouterr()
        assert "Langfuse Callback handler could not be created" in captured.out

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_task_context_dependency_set(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_langfuse_client,
        mock_create_refactor_task,
        mock_create_review_task,
        mock_agents,
    ):
        """Test that review task has refactor task in its context"""
        mock_callback_handler.return_value = mock.MagicMock()
        mock_get_modified_files.return_value = ["file.py"]
        mock_get_content.return_value = "code"

        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        mock_crew_instance = mock.MagicMock()
        mock_crew_class.return_value = mock_crew_instance

        mock_langfuse_client.flush.return_value = None
        mock_langfuse_client.update_current_trace.return_value = None

        # Mock task creation with tasks that track context
        mock_refactor_task_instance = mock.MagicMock()
        mock_review_task_instance = mock.MagicMock()
        mock_create_refactor_task.return_value = mock_refactor_task_instance
        mock_create_review_task.return_value = mock_review_task_instance

        run_code_formatter(repo_full_name="owner/repo", pr_number=123)

        # Get the tasks that were passed to Crew
        crew_call_kwargs = mock_crew_class.call_args[1]
        tasks = crew_call_kwargs["tasks"]

        # Should have 2 tasks: refactor and review
        assert len(tasks) == 2
        refactor_task = tasks[0]
        review_task = tasks[1]

        # Verify the review task has the refactor task in its context
        assert review_task.context == [refactor_task]

    @mock.patch("coffee_maker.code_formatter.crewai.main.create_review_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_refactor_task")
    @mock.patch("coffee_maker.code_formatter.crewai.main.langfuse_client")
    @mock.patch("coffee_maker.code_formatter.crewai.main.Crew")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_pr_reviewer_agent")
    @mock.patch("coffee_maker.code_formatter.crewai.main.create_code_formatter_agents")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_file_content")
    @mock.patch("coffee_maker.code_formatter.crewai.main._get_pr_modified_files")
    @mock.patch("coffee_maker.code_formatter.crewai.main.CallbackHandler")
    def test_langfuse_session_id_set(
        self,
        mock_callback_handler,
        mock_get_modified_files,
        mock_get_content,
        mock_create_formatter,
        mock_create_reviewer,
        mock_crew_class,
        mock_langfuse_client,
        mock_create_refactor_task,
        mock_create_review_task,
        mock_agents,
    ):
        """Test that Langfuse session ID is set correctly"""
        mock_callback_handler.return_value = mock.MagicMock()
        mock_get_modified_files.return_value = ["file.py"]
        mock_get_content.return_value = "code"

        mock_create_formatter.return_value = {"senior_engineer": mock_agents["senior_engineer"]}
        mock_create_reviewer.return_value = {"pull_request_reviewer": mock_agents["pull_request_reviewer"]}

        mock_crew_instance = mock.MagicMock()
        mock_crew_class.return_value = mock_crew_instance

        # Mock task creation
        mock_refactor_task_instance = mock.MagicMock()
        mock_review_task_instance = mock.MagicMock()
        mock_create_refactor_task.return_value = mock_refactor_task_instance
        mock_create_review_task.return_value = mock_review_task_instance

        run_code_formatter(repo_full_name="test/repo", pr_number=999)

        # Verify the session ID was set
        mock_langfuse_client.update_current_trace.assert_called_once_with(session_id="pr-review-test/repo-999")
        mock_langfuse_client.flush.assert_called_once()
