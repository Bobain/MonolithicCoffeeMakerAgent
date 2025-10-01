"""Tests for coffee_maker/code_formatter/crewai/tasks.py"""

from unittest import mock

import pytest
from crewai import Agent, Task

from coffee_maker.code_formatter.crewai.tasks import (
    EXPLANATIONS_DELIMITER_END,
    EXPLANATIONS_DELIMITER_START,
    MODIFIED_CODE_DELIMITER_END,
    MODIFIED_CODE_DELIMITER_START,
    create_refactor_task,
    create_review_task,
)


@pytest.fixture
def mock_agent():
    """Create a real Agent instance for testing"""
    return Agent(role="Test Agent", goal="Test goal", backstory="Test backstory", verbose=False)


class TestDelimiters:
    """Test that delimiter constants are defined"""

    def test_delimiters_exist(self):
        """Test that all required delimiters are defined"""
        assert MODIFIED_CODE_DELIMITER_START == "---MODIFIED_CODE_START---"
        assert MODIFIED_CODE_DELIMITER_END == "---MODIFIED_CODE_END---"
        assert EXPLANATIONS_DELIMITER_START == "---EXPLANATIONS_START---"
        assert EXPLANATIONS_DELIMITER_END == "---EXPLANATIONS_END---"


class TestCreateRefactorTask:
    """Tests for create_refactor_task function"""

    def test_create_refactor_task_basic(self, mock_agent):
        """Test creating a basic refactor task"""
        mock_langfuse_client = mock.MagicMock()

        # Mock the prompt compilation
        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "Compiled prompt text"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        file_path = "src/test.py"
        file_content = "def hello():\n    print('hello')"

        task = create_refactor_task(mock_agent, mock_langfuse_client, file_path, file_content)

        # Verify it returns a Task
        assert isinstance(task, Task)
        assert task.agent == mock_agent

        # Verify the prompt was fetched and compiled
        mock_langfuse_client.get_prompt.assert_called_once_with("code_formatter_main_llm_entry")
        mock_prompt.compile.assert_called_once_with(
            filename=file_path,
            file_content=file_content,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )

    def test_create_refactor_task_description(self, mock_agent):
        """Test that the task description is set correctly"""
        mock_langfuse_client = mock.MagicMock()

        mock_prompt = mock.MagicMock()
        compiled_text = "You are a senior engineer. Refactor this code."
        mock_prompt.compile.return_value = compiled_text
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        task = create_refactor_task(mock_agent, mock_langfuse_client, "file.py", "code content")

        assert task.description == compiled_text

    def test_create_refactor_task_expected_output(self, mock_agent):
        """Test that the expected_output contains required information"""
        mock_langfuse_client = mock.MagicMock()

        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "prompt"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        task = create_refactor_task(mock_agent, mock_langfuse_client, "file.py", "code")

        assert "code given as input" in task.expected_output
        assert "formatting suggestions" in task.expected_output
        assert "delimiters" in task.expected_output
        assert "explanation" in task.expected_output

    def test_create_refactor_task_langfuse_error(self):
        """Test handling of Langfuse client errors"""
        mock_agent = mock.MagicMock()
        mock_langfuse_client = mock.MagicMock()
        mock_langfuse_client.get_prompt.side_effect = Exception("Langfuse connection error")

        with pytest.raises(Exception, match="Langfuse connection error"):
            create_refactor_task(mock_agent, mock_langfuse_client, "file.py", "code")


class TestCreateReviewTask:
    """Tests for create_review_task function"""

    def test_create_review_task_basic(self, mock_agent):
        """Test creating a basic review task"""
        mock_langfuse_client = mock.MagicMock()
        mock_refactor_task = mock.MagicMock()
        mock_refactor_task.output = "refactored code output"

        # Mock the prompt compilation
        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "Review prompt text"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        file_path = "src/review.py"
        repo_full_name = "owner/repo"
        pr_number = 42

        task = create_review_task(
            mock_agent, mock_langfuse_client, file_path, repo_full_name, pr_number, mock_refactor_task
        )

        # Verify it returns a Task
        assert isinstance(task, Task)
        assert task.agent == mock_agent

        # Verify the prompt was compiled with correct parameters
        mock_langfuse_client.get_prompt.assert_called_once_with("code_formatter_main_llm_entry")
        mock_prompt.compile.assert_called_once_with(
            filename=file_path,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            refactored_code=mock_refactor_task.output,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )

    def test_create_review_task_expected_output(self, mock_agent):
        """Test that the expected_output contains success/failure messages"""
        mock_langfuse_client = mock.MagicMock()
        mock_refactor_task = mock.MagicMock()
        mock_refactor_task.output = "output"

        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "prompt"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        file_path = "src/test.py"
        task = create_review_task(mock_agent, mock_langfuse_client, file_path, "repo", 1, mock_refactor_task)

        assert file_path in task.expected_output
        assert "confirmation message" in task.expected_output
        assert "successfully posted" in task.expected_output
        assert "OK" in task.expected_output
        assert "KO" in task.expected_output

    def test_create_review_task_with_different_params(self, mock_agent):
        """Test creating review tasks with different parameters"""
        mock_langfuse_client = mock.MagicMock()
        mock_refactor_task = mock.MagicMock()
        mock_refactor_task.output = "different output"

        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "compiled"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        task = create_review_task(
            mock_agent, mock_langfuse_client, "different/path.py", "test/repo", 999, mock_refactor_task
        )

        # Verify the compile was called with the different parameters
        compile_call_kwargs = mock_prompt.compile.call_args[1]
        assert compile_call_kwargs["filename"] == "different/path.py"
        assert compile_call_kwargs["repo_full_name"] == "test/repo"
        assert compile_call_kwargs["pr_number"] == 999
        assert compile_call_kwargs["refactored_code"] == "different output"

    def test_create_review_task_uses_refactor_output(self, mock_agent):
        """Test that review task uses refactor task output"""
        mock_langfuse_client = mock.MagicMock()
        mock_refactor_task = mock.MagicMock()

        expected_output = "This is the refactored code from previous task"
        mock_refactor_task.output = expected_output

        mock_prompt = mock.MagicMock()
        mock_prompt.compile.return_value = "prompt"
        mock_langfuse_client.get_prompt.return_value = mock_prompt

        create_review_task(mock_agent, mock_langfuse_client, "file.py", "repo", 1, mock_refactor_task)

        # Verify the refactored_code parameter was passed correctly
        compile_kwargs = mock_prompt.compile.call_args[1]
        assert compile_kwargs["refactored_code"] == expected_output
