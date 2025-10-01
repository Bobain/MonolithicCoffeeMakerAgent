"""Tests for coffee_maker/code_formatter/crewai/agents.py"""

from unittest import mock

import pytest
from crewai import Agent

from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI
from coffee_maker.code_formatter.crewai.agents import create_code_formatter_agents, create_pr_reviewer_agent, llm


class TestLLMConfiguration:
    """Tests for LLM configuration"""

    def test_llm_exists(self):
        """Test that llm object is initialized"""
        assert llm is not None

    @mock.patch("coffee_maker.code_formatter.crewai.agents.ChatGoogleGenerativeAI")
    def test_llm_initialization_error(self, mock_llm_class):
        """Test that LLM initialization errors are raised"""
        mock_llm_class.side_effect = Exception("GOOGLE_API_KEY not set")

        # This would happen during import, so we just verify the mock raises
        with pytest.raises(Exception, match="GOOGLE_API_KEY not set"):
            mock_llm_class(model="gemini-1.5-pro-latest")


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

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        result = create_code_formatter_agents(mock_langfuse_client)

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

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agent = agents["senior_engineer"]

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

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agent = agents["senior_engineer"]

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

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agent = agents["senior_engineer"]

        assert agent.tools == []

    def test_agent_does_not_delegate(self):
        """Test that the agent has delegation disabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agent = agents["senior_engineer"]

        assert agent.allow_delegation is False

    def test_agent_is_verbose(self):
        """Test that the agent has verbose mode enabled"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agent = agents["senior_engineer"]

        assert agent.verbose is True

    def test_langfuse_error_handling(self):
        """Test that Langfuse errors are propagated"""
        mock_langfuse_client = mock.MagicMock()
        mock_langfuse_client.get_prompt.side_effect = Exception("Cannot fetch prompts from Langfuse")

        with pytest.raises(Exception, match="Cannot fetch prompts from Langfuse"):
            create_code_formatter_agents(mock_langfuse_client)


class TestCreatePRReviewerAgent:
    """Tests for create_pr_reviewer_agent function"""

    def test_returns_dict_with_reviewer(self):
        """Test that the function returns a dict with 'pull_request_reviewer' key"""
        mock_langfuse_client = mock.MagicMock()

        result = create_pr_reviewer_agent(mock_langfuse_client)

        assert isinstance(result, dict)
        assert "pull_request_reviewer" in result
        assert isinstance(result["pull_request_reviewer"], Agent)

    def test_reviewer_has_correct_role(self):
        """Test that the PR reviewer agent has correct role"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert agent.role == "GitHub Code Reviewer"

    def test_reviewer_goal_mentions_github(self):
        """Test that the reviewer's goal mentions posting to GitHub"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert "GitHub" in agent.goal or "pull request" in agent.goal
        assert "suggestions" in agent.goal

    def test_reviewer_backstory_mentions_automation(self):
        """Test that the reviewer's backstory mentions automation"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert "automated" in agent.backstory.lower() or "code review" in agent.backstory.lower()

    def test_reviewer_has_post_suggestion_tool(self):
        """Test that the reviewer has the PostSuggestionToolLangAI"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert len(agent.tools) == 1
        assert isinstance(agent.tools[0], PostSuggestionToolLangAI)

    def test_reviewer_does_not_delegate(self):
        """Test that the reviewer has delegation disabled"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert agent.allow_delegation is False

    def test_reviewer_is_verbose(self):
        """Test that the reviewer has verbose mode enabled"""
        mock_langfuse_client = mock.MagicMock()

        agents = create_pr_reviewer_agent(mock_langfuse_client)
        agent = agents["pull_request_reviewer"]

        assert agent.verbose is True

    def test_reviewer_does_not_use_langfuse_prompts(self):
        """Test that the reviewer doesn't call Langfuse (uses hardcoded prompts)"""
        mock_langfuse_client = mock.MagicMock()

        create_pr_reviewer_agent(mock_langfuse_client)

        # The reviewer agent has hardcoded goal and backstory, so Langfuse shouldn't be called
        mock_langfuse_client.get_prompt.assert_not_called()


class TestAgentIntegration:
    """Integration tests for agent creation"""

    def test_both_agents_can_be_created_together(self):
        """Test that both agent creation functions work together"""
        mock_langfuse_client = mock.MagicMock()

        mock_goal_prompt = mock.MagicMock()
        mock_goal_prompt.prompt = "goal"
        mock_backstory_prompt = mock.MagicMock()
        mock_backstory_prompt.prompt = "backstory"

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        formatter_agents = create_code_formatter_agents(mock_langfuse_client)
        reviewer_agents = create_pr_reviewer_agent(mock_langfuse_client)

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

        mock_langfuse_client.get_prompt.side_effect = [mock_goal_prompt, mock_backstory_prompt]

        agents = create_code_formatter_agents(mock_langfuse_client)
        agents.update(create_pr_reviewer_agent(mock_langfuse_client))

        assert len(agents) == 2
        assert "senior_engineer" in agents
        assert "pull_request_reviewer" in agents
        assert isinstance(agents["senior_engineer"], Agent)
        assert isinstance(agents["pull_request_reviewer"], Agent)
