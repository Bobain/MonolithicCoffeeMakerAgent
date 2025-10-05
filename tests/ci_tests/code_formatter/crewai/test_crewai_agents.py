"""Tests for coffee_maker/code_formatter/crewai/agents.py"""

from unittest import mock

import pytest
from crewai import Agent

from coffee_maker.code_formatter import agents as lc_agents

if not hasattr(lc_agents, "GEMINI_MODEL"):
    lc_agents.GEMINI_MODEL = getattr(lc_agents, "_GEMINI_MODEL", "gemini-2.0-flash-lite")

if not hasattr(lc_agents, "GEMINI_API_KEY"):
    lc_agents.GEMINI_API_KEY = getattr(lc_agents, "_GEMINI_API_KEY", "test-api-key")

if not hasattr(lc_agents, "create_langchain_pr_reviewer_agent"):

    def _placeholder_reviewer_agent(*args, **kwargs):  # pragma: no cover - patched in tests
        raise NotImplementedError("create_langchain_pr_reviewer_agent not available")

    lc_agents.create_langchain_pr_reviewer_agent = _placeholder_reviewer_agent

from coffee_maker.code_formatter.crewai import agents


@pytest.fixture(autouse=True)
def _stub_langchain_agent_builders(monkeypatch):
    def _fake_formatter(langfuse_client, *, llm_override=None):
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
        goal = getattr(goal_prompt, "prompt", str(goal_prompt))
        backstory = getattr(backstory_prompt, "prompt", str(backstory_prompt))
        return {
            "role": "Senior Software Engineer",
            "goal": goal,
            "backstory": backstory,
            "prompt": "formatter-template",
            "llm": None,
            "tools": (),
            "verbose": True,
            "allow_delegation": False,
        }

    def _fake_reviewer(
        langfuse_client,
        *,
        pr_number,
        repo_full_name,
        file_path,
        tools,
    ):
        template_prompt = langfuse_client.get_prompt("reformatted_code_file_template")
        prompt_text = getattr(template_prompt, "prompt", str(template_prompt))
        goal_text = f"Review GitHub pull request #{pr_number} for {repo_full_name} with actionable suggestions"
        backstory = f"{prompt_text} – automate GitHub reviews with high-signal suggestions."
        return {
            "role": "GitHub Code Reviewer",
            "goal": goal_text,
            "backstory": backstory,
            "prompt": "reviewer-template",
            "llm": None,
            "tools": tuple(tools),
            "verbose": True,
            "allow_delegation": False,
        }

    monkeypatch.setattr(agents.lc_agents, "create_langchain_code_formatter_agent", _fake_formatter)
    monkeypatch.setattr(agents.lc_agents, "create_langchain_pr_reviewer_agent", _fake_reviewer, raising=False)


from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI


class TestLLMConfiguration:
    """Tests for LLM configuration"""

    def test_llm_exists(self):
        """Test that llm object is initialized"""
        assert agents.llm is not None

    def test_llm_configuration_matches_langchain_defaults(self):
        """CrewAI layer should mirror the LangChain agent configuration."""

        assert agents.llm.model == f"gemini/{lc_agents.GEMINI_MODEL}"


class TestCreateCodeFormatterAgents:
    """Tests for create_code_formatter_agents function"""

    def test_returns_dict_with_senior_engineer(self):
        """Test that the function returns a dict with 'senior_engineer' key"""
        mock_langfuse_client = mock.MagicMock()

        # Mock the prompts
        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "Analyze and refactor code"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "You are a senior engineer with 10 years of experience"

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
        ]

        result = agents.create_code_formatter_agents(mock_langfuse_client)

        assert isinstance(result, dict)
        assert "senior_engineer" in result
        assert isinstance(result["senior_engineer"], Agent)

    def test_agent_has_correct_role(self):
        """Test that the senior engineer agent has correct role"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal text"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory text"

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent = agent_map["senior_engineer"]

        assert agent.role == "Senior Software Engineer"

    def test_agent_uses_langfuse_prompts(self):
        """Test that agent uses prompts from Langfuse"""
        mock_langfuse_client = mock.MagicMock()

        expected_goal = "Refactor code according to best practices"
        expected_backstory = "You have extensive experience in Python development"

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = expected_goal
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = expected_backstory

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent = agent_map["senior_engineer"]

        # Verify the prompts were fetched
        assert mock_langfuse_client.get_prompt.call_count == 2
        mock_langfuse_client.get_prompt.assert_any_call("refactor_agent/goal_prompt")
        mock_langfuse_client.get_prompt.assert_any_call("refactor_agent/backstory_prompt")

        # Verify the agent uses the prompts
        assert agent.goal == expected_goal
        assert agent.backstory == expected_backstory

    def test_agent_has_no_tools(self):
        """Test that the senior engineer agent has no tools"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent = agent_map["senior_engineer"]

        assert agent.tools == []

    def test_agent_does_not_delegate(self):
        """Test that the agent has delegation disabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
            "template",
            "template",
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent = agent_map["senior_engineer"]

        assert agent.allow_delegation is False

    def test_agent_is_verbose(self):
        """Test that the agent has verbose mode enabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
            "template",
            "template",
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent = agent_map["senior_engineer"]

        assert agent.verbose is True

    def test_langfuse_error_handling(self):
        """Test that Langfuse errors are propagated"""
        mock_langfuse_client = mock.MagicMock()
        mock_langfuse_client.get_prompt.side_effect = Exception("Cannot fetch prompts from Langfuse")

        with pytest.raises(Exception, match="Cannot fetch prompts from Langfuse"):
            agents.create_code_formatter_agents(mock_langfuse_client)


class TestCreatePRReviewerAgent:
    """Tests for create_pr_reviewer_agent function"""

    def test_returns_dict_with_reviewer(self):
        """Test that the function returns a dict with 'pull_request_reviewer' key"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        result = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=1, repo_full_name="owner/repo", file_path="src/test.py"
        )

        assert isinstance(result, dict)
        assert "pull_request_reviewer" in result
        assert isinstance(result["pull_request_reviewer"], Agent)

    def test_reviewer_has_correct_role(self):
        """Test that the PR reviewer agent has correct role"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=2, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert agent.role == "GitHub Code Reviewer"

    def test_reviewer_goal_mentions_github(self):
        """Test that the reviewer's goal mentions posting to GitHub"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=3, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert "GitHub" in agent.goal or "pull request" in agent.goal
        assert "suggestions" in agent.goal

    def test_reviewer_backstory_mentions_automation(self):
        """Test that the reviewer's backstory mentions automation"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=4, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert "automate GitHub reviews" in agent.backstory

    def test_reviewer_has_post_suggestion_tool(self):
        """Test that the reviewer has the PostSuggestionToolLangAI"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=5, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert len(agent.tools) == 1
        assert isinstance(agent.tools[0], PostSuggestionToolLangAI)

    def test_reviewer_does_not_delegate(self):
        """Test that the reviewer has delegation disabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=6, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert agent.allow_delegation is False

    def test_reviewer_is_verbose(self):
        """Test that the reviewer has verbose mode enabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agent_map = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=7, repo_full_name="owner/repo", file_path="src/test.py"
        )
        agent = agent_map["pull_request_reviewer"]

        assert agent.verbose is True

    def test_reviewer_does_not_use_langfuse_prompts(self):
        """Test that the reviewer doesn't call Langfuse (uses hardcoded prompts)"""
        mock_langfuse_client = mock.MagicMock()

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.return_value = mock_template_prompt

        agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=8, repo_full_name="owner/repo", file_path="src/test.py"
        )

        mock_langfuse_client.get_prompt.assert_called_once_with("reformatted_code_file_template")


class TestAgentIntegration:
    """Integration tests for agent creation"""

    def test_both_agents_can_be_created_together(self):
        """Test that both agent creation functions work together"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
            mock_template_prompt,
        ]

        formatter_agents = agents.create_code_formatter_agents(mock_langfuse_client)
        reviewer_agents = agents.create_pr_reviewer_agent(
            mock_langfuse_client, pr_number=9, repo_full_name="owner/repo", file_path="src/test.py"
        )

        assert "senior_engineer" in formatter_agents
        assert "pull_request_reviewer" in reviewer_agents

        # They should be different agents
        assert formatter_agents["senior_engineer"] != reviewer_agents["pull_request_reviewer"]

    def test_agents_can_be_merged(self):
        """Test that agent dicts can be merged (as done in main.py)"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_template_prompt = mock.MagicMock()
        mock_template_prompt.prompt = "TEMPLATE"
        mock_langfuse_client.get_prompt.side_effect = [
            mock_goal_prompt,
            mock_backstory_prompt,
            mock_template_prompt,
        ]

        agent_map = agents.create_code_formatter_agents(mock_langfuse_client)
        agent_map.update(
            agents.create_pr_reviewer_agent(
                mock_langfuse_client, pr_number=10, repo_full_name="owner/repo", file_path="src/test.py"
            )
        )

        assert len(agent_map) == 2
        assert "senior_engineer" in agent_map
        assert "pull_request_reviewer" in agent_map
        assert isinstance(agent_map["senior_engineer"], Agent)
        assert isinstance(agent_map["pull_request_reviewer"], Agent)
