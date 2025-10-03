"""Tests for coffee_maker/code_formatter/crewai/flow.py"""

from unittest import mock

import pytest

from crewai import Agent

from coffee_maker.code_formatter.crewai.flow import (
    EXPLANATIONS_DELIMITER_END,
    EXPLANATIONS_DELIMITER_START,
    MODIFIED_CODE_DELIMITER_END,
    MODIFIED_CODE_DELIMITER_START,
    CodeFormatterFlow,
    create_code_formatter_flow,
    kickoff_code_formatter_flow,
)
from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI


@pytest.fixture
def formatter_agent():
    """Mocked formatter agent"""
    agent = mock.create_autospec(Agent, instance=True)
    agent.kickoff.return_value = mock.Mock(raw="formatted output")
    return agent


@pytest.fixture
def reviewer_agent():
    """Mocked reviewer agent"""
    agent = mock.create_autospec(Agent, instance=True)
    agent.kickoff.return_value = mock.Mock(raw="review output")
    agent.tools = []
    return agent


@pytest.fixture
def langfuse_client():
    """Mock Langfuse client returning dedicated prompt mocks."""
    formatter_prompt = mock.Mock()
    formatter_prompt.compile.return_value = "compiled formatter prompt"

    reviewer_prompt = mock.Mock()
    reviewer_prompt.compile.return_value = "compiled reviewer prompt"

    client = mock.Mock()
    client.get_prompt.side_effect = [formatter_prompt, reviewer_prompt]
    client.formatter_prompt = formatter_prompt
    client.reviewer_prompt = reviewer_prompt
    return client


class TestConstants:
    """Verify delimiter constants are preserved."""

    def test_delimiter_constants_match(self):
        assert MODIFIED_CODE_DELIMITER_START == "---MODIFIED_CODE_START---"
        assert MODIFIED_CODE_DELIMITER_END == "---MODIFIED_CODE_END---"
        assert EXPLANATIONS_DELIMITER_START == "---EXPLANATIONS_START---"
        assert EXPLANATIONS_DELIMITER_END == "---EXPLANATIONS_END---"


class TestCodeFormatterFlow:
    """Behavioural tests for the formatter flow."""

    def test_flow_runs_all_steps(
        self,
        formatter_agent,
        reviewer_agent,
        langfuse_client,
    ):
        file_path = "src/example.py"
        repo_full_name = "owner/repo"
        pr_number = 42
        file_content = "print('hello world')\n"

        flow = CodeFormatterFlow(
            formatter_agent=formatter_agent,
            reviewer_agent=reviewer_agent,
            langfuse_client=langfuse_client,
            file_path=file_path,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_content=file_content,
        )

        flow.kickoff()

        langfuse_client.formatter_prompt.compile.assert_called_once_with(
            filename=file_path,
            file_content=file_content,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )
        langfuse_client.reviewer_prompt.compile.assert_called_once_with(
            file_path=file_path,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )

        formatter_agent.kickoff.assert_called_once_with("compiled formatter prompt")

        reviewer_agent.kickoff.assert_called_once()
        messages = reviewer_agent.kickoff.call_args.args[0]
        assert messages[0]["content"] == "compiled reviewer prompt"
        assert messages[1]["content"] == "formatted output"

        assert flow.state.reformat_prompt == "compiled formatter prompt"
        assert flow.state.reformat_result == "formatted output"
        assert flow.state.review_prompt == "compiled reviewer prompt"
        assert flow.state.review_result == "review output"
        assert any(isinstance(tool, PostSuggestionToolLangAI) for tool in flow.reviewer_agent.tools)

    def test_flow_factory_helper(self, formatter_agent, reviewer_agent, langfuse_client):
        flow = create_code_formatter_flow(
            formatter_agent=formatter_agent,
            reviewer_agent=reviewer_agent,
            langfuse_client=langfuse_client,
            file_path="src/example.py",
            repo_full_name="owner/repo",
            pr_number=1,
            file_content="code",
        )

        assert isinstance(flow, CodeFormatterFlow)
        assert flow.state.file_path == "src/example.py"
        assert flow.state.repo_full_name == "owner/repo"
        assert flow.state.pr_number == 1
        assert flow.state.file_content == "code"

    def test_kickoff_helper_runs_flow(self, formatter_agent, reviewer_agent, langfuse_client):
        flow = kickoff_code_formatter_flow(
            formatter_agent=formatter_agent,
            reviewer_agent=reviewer_agent,
            langfuse_client=langfuse_client,
            file_path="src/example.py",
            repo_full_name="owner/repo",
            pr_number=7,
            file_content="code",
        )

        assert isinstance(flow, CodeFormatterFlow)
        formatter_agent.kickoff.assert_called_once()
        reviewer_agent.kickoff.assert_called_once()
        assert flow.state.review_result == "review output"
