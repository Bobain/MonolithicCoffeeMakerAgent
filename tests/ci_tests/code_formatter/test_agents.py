"""Tests for coffee_maker.code_formatter.agents."""

import os
from types import SimpleNamespace
from unittest import mock

import pytest

from coffee_maker.code_formatter import agents as lc_agents


class TestLangchainCodeFormatterAgent:
    """Tests for the LangChain senior engineer agent definition."""

    def test_agent_fields_from_langfuse_prompts(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.side_effect = [
            SimpleNamespace(prompt="Goal text"),
            SimpleNamespace(prompt="Backstory text"),
        ]

        agent = lc_agents.create_langchain_code_formatter_agent(langfuse_client)

        assert agent["role"] == "Senior Software Engineer"
        assert agent["goal"] == "Goal text"
        assert agent["backstory"] == "Backstory text"
        assert agent["tools"] == ()
        assert agent["allow_delegation"] is False
        assert agent["verbose"] is True
        assert agent["llm"] is lc_agents.llm

        # Two prompts fetched: goal and backstory
        assert langfuse_client.get_prompt.call_count == 2
        langfuse_client.get_prompt.assert_any_call("refactor_agent/goal_prompt")
        langfuse_client.get_prompt.assert_any_call("refactor_agent/backstory_prompt")

    def test_prompt_formats_messages(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.side_effect = [
            SimpleNamespace(prompt="Analyse"),
            SimpleNamespace(prompt="Experienced"),
        ]

        agent = lc_agents.create_langchain_code_formatter_agent(langfuse_client)

        formatted = agent["prompt"].format_messages(input="hello")
        assert formatted[0].type == "system"
        assert "Analyse" in formatted[0].content
        assert formatted[1].type == "human"
        assert formatted[1].content == "hello"


class TestLangchainReviewerAgent:
    """Tests for the LangChain PR reviewer definition."""

    def test_reviewer_uses_template_and_tools(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.return_value = SimpleNamespace(prompt="TEMPLATE")

        tool = object()
        agent = lc_agents.create_langchain_pr_reviewer_agent(
            langfuse_client,
            pr_number=42,
            repo_full_name="owner/repo",
            file_path="src/app.py",
            tools=(tool,),
        )

        assert agent["role"] == "GitHub Code Reviewer"
        assert agent["tools"] == (tool,)
        formatted = agent["prompt"].format_messages(input="foo")
        assert "owner/repo" in formatted[0].content
        assert formatted[1].content == "foo"
        langfuse_client.get_prompt.assert_called_once_with("reformatted_code_file_template")


@pytest.mark.parametrize("env_name", ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"])
def test_resolve_gemini_key_prefers_first_available(env_name, monkeypatch):
    for name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv(env_name, "test-key")

    result = lc_agents._resolve_gemini_api_key()

    assert result == "test-key"
    assert os.environ["GEMINI_API_KEY"] == "test-key"
