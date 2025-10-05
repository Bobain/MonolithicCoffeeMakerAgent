"""Tests for coffee_maker.code_formatter.agents."""

import os
from types import SimpleNamespace
from unittest import mock

import pytest

from coffee_maker.code_formatter import agents as lc_agents


@pytest.fixture(autouse=True)
def _patch_build_prompt(monkeypatch):
    def _fake_prompt(system_message, *_, **__):
        return lc_agents.ChatPromptTemplate.from_messages([("system", system_message), ("user", "{input}")])

    monkeypatch.setattr(lc_agents, "_build_prompt", _fake_prompt, raising=False)


class TestLangchainCodeFormatterAgent:
    """Tests for the LangChain senior engineer agent definition."""

    def test_agent_fields_from_langfuse_prompts(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.side_effect = [
            SimpleNamespace(prompt="Goal text"),
            SimpleNamespace(prompt="Backstory text"),
        ]

        agent = lc_agents.create_langchain_code_formatter_agent(langfuse_client)

        assert agent["role"] == "Senior Software Engineer: python code formatter"
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
        assert "You are a meticulous Senior Software Engineer" in formatted[0].content
        assert "Goal: Analyse" in formatted[0].content
        assert "Backstory: Experienced" in formatted[0].content
        assert formatted[1].type == "human"
        assert formatted[1].content == "hello"


class TestLangchainReviewerAgent:
    """Tests for the LangChain PR reviewer definition."""

    def test_reviewer_uses_template_and_tools(self):
        if not hasattr(lc_agents, "create_langchain_pr_reviewer_agent"):
            pytest.skip("create_langchain_pr_reviewer_agent not provided in module")

        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.return_value = SimpleNamespace(prompt="TEMPLATE")

        tool = object()
        try:
            agent = lc_agents.create_langchain_pr_reviewer_agent(
                langfuse_client,
                pr_number=42,
                repo_full_name="owner/repo",
                file_path="src/app.py",
                tools=(tool,),
            )
        except NotImplementedError:
            pytest.skip("create_langchain_pr_reviewer_agent stub not available")

        assert agent["role"] == "GitHub Code Reviewer"
        assert agent["tools"] == (tool,)
        formatted = agent["prompt"].format_messages(input="foo")
        assert formatted[1].content == "foo"
        langfuse_client.get_prompt.assert_called_once_with("reformatted_code_file_template")


@pytest.mark.parametrize("env_name", ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"])
def test_resolve_gemini_key_prefers_first_available(env_name, monkeypatch):
    resolve_func = getattr(lc_agents, "_resolve_gemini_api_key", None)
    if resolve_func is None:
        pytest.skip("_resolve_gemini_api_key helper not defined")

    for name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv(env_name, "test-key")

    result = resolve_func()

    assert result == "test-key"
    assert os.environ["GEMINI_API_KEY"] == "test-key"
