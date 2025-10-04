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

        assert agent.role == "Senior Software Engineer"
        assert agent.goal == "Goal text"
        assert agent.backstory == "Backstory text"
        assert agent.allow_delegation is False
        assert agent.tools == ()
        assert agent.llm is lc_agents.llm

        # Two prompts fetched: goal and backstory
        assert langfuse_client.get_prompt.call_count == 2
        langfuse_client.get_prompt.assert_any_call("refactor_agent/goal_prompt")
        langfuse_client.get_prompt.assert_any_call("refactor_agent/backstory_prompt")

    def test_as_runnable_returns_langchain_chain(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.side_effect = [
            SimpleNamespace(prompt="Do the thing"),
            SimpleNamespace(prompt="You have context"),
        ]

        agent = lc_agents.create_langchain_code_formatter_agent(langfuse_client)

        class DummyLLM:
            def __init__(self):
                self.called = False

            def invoke(self, messages, **kwargs):
                self.called = True
                if hasattr(messages, "to_messages"):
                    message_list = messages.to_messages()
                else:
                    message_list = messages
                last = message_list[-1]
                content = getattr(last, "content", str(last))
                return SimpleNamespace(content=f"Echo: {content}")

            __call__ = invoke

        dummy_llm = DummyLLM()
        agent.llm = dummy_llm

        runnable = agent.as_runnable()
        response = runnable.invoke({"input": "Hello"})
        assert response.content.startswith("Echo")
        assert dummy_llm.called is True


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

        assert agent.role == "GitHub Code Reviewer"
        assert agent.tools == (tool,)
        assert "owner/repo" in agent.prompt.format_messages(input="foo")[0].content
        langfuse_client.get_prompt.assert_called_once_with("reformatted_code_file_template")

    def test_with_tools_factory_helper(self):
        langfuse_client = mock.MagicMock()
        langfuse_client.get_prompt.return_value = SimpleNamespace(prompt="TPL")

        agent = lc_agents.create_langchain_pr_reviewer_agent(
            langfuse_client,
            pr_number=1,
            repo_full_name="repo",
            file_path="file",
        )

        sentinel = object()

        def factory():
            return sentinel

        updated = agent.with_tools(factory)
        assert updated.tools == (sentinel,)
        assert agent.tools == ()


@pytest.mark.parametrize("env_name", ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"])
def test_resolve_gemini_key_prefers_first_available(env_name, monkeypatch):
    for name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv(env_name, "test-key")

    result = lc_agents._resolve_gemini_api_key()

    assert result == "test-key"
    assert os.environ["GEMINI_API_KEY"] == "test-key"
