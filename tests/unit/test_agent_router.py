"""Unit tests for AgentDelegationRouter.

Tests cover:
- Intent classification (pattern matching)
- Intent classification (AI fallback)
- Agent delegation
- Prompt generation
"""

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.cli.agent_router import AgentDelegationRouter


class MockAIService:
    """Mock AIService for testing."""

    def __init__(self, response: str = "test response"):
        """Initialize mock with optional response."""
        self.response = response
        self.calls = []

    def process_request(self, user_input: str, context: dict, history: list, stream: bool = False):
        """Mock process_request method."""
        self.calls.append({"user_input": user_input, "context": context, "history": history})

        class MockResponse:
            def __init__(self, msg):
                self.message = msg

        return MockResponse(self.response)


class TestAgentDelegationRouter:
    """Test cases for AgentDelegationRouter."""

    def test_classify_intent_architect_design(self):
        """Test classification for architect requests - design."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Design a caching layer")

        assert agent_type == AgentType.ARCHITECT
        assert confidence > 0.8

    def test_classify_intent_architect_spec(self):
        """Test classification for architect requests - spec."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Create a technical specification")

        assert agent_type == AgentType.ARCHITECT
        assert confidence > 0.8

    def test_classify_intent_architect_adr(self):
        """Test classification for architect requests - ADR."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Create an ADR for our architecture decision")

        assert agent_type == AgentType.ARCHITECT
        assert confidence > 0.8

    def test_classify_intent_project_manager_roadmap(self):
        """Test classification for project_manager requests - roadmap."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Show me the roadmap")

        assert agent_type == AgentType.PROJECT_MANAGER
        assert confidence > 0.8

    def test_classify_intent_project_manager_github(self):
        """Test classification for project_manager requests - github."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("What's our PR status on GitHub")

        assert agent_type == AgentType.PROJECT_MANAGER
        assert confidence > 0.8

    def test_classify_intent_code_developer_implement(self):
        """Test classification for code_developer requests - implement."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Implement the caching layer")

        assert agent_type == AgentType.CODE_DEVELOPER
        assert confidence > 0.8

    def test_classify_intent_code_developer_pr(self):
        """Test classification for code_developer requests - PR."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Create a pull request for this")

        assert agent_type == AgentType.CODE_DEVELOPER
        assert confidence > 0.8

    def test_classify_intent_assistant_demo(self):
        """Test classification for assistant requests - demo."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Show me a demo of the dashboard")

        assert agent_type == AgentType.ASSISTANT
        assert confidence > 0.8

    def test_classify_intent_assistant_help(self):
        """Test classification for assistant requests - help."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Help me understand how this works")

        assert agent_type == AgentType.ASSISTANT
        assert confidence > 0.8

    def test_classify_intent_ux_design_expert(self):
        """Test classification for ux_design_expert requests."""
        router = AgentDelegationRouter(MockAIService())
        agent_type, confidence = router.classify_intent("Make the dashboard UI better with Tailwind CSS styling")

        assert agent_type == AgentType.UX_DESIGN_EXPERT
        assert confidence > 0.8

    def test_classify_intent_ambiguous_fallback(self):
        """Test classification for ambiguous requests - uses AI fallback."""
        mock_ai = MockAIService(
            response="<classification><agent>architect</agent><confidence>0.75</confidence></classification>"
        )
        router = AgentDelegationRouter(mock_ai)

        # Ambiguous request that doesn't match any keywords
        agent_type, confidence = router.classify_intent("Do something with the system")

        # Should use AI fallback
        assert mock_ai.calls  # AI was called
        assert agent_type == AgentType.ARCHITECT
        assert confidence == 0.75

    def test_classify_intent_ai_fallback_default_to_assistant(self):
        """Test AI fallback defaults to assistant on parse error."""
        mock_ai = MockAIService(response="unparseable response")
        router = AgentDelegationRouter(mock_ai)

        agent_type, confidence = router.classify_intent("Something unclear")

        # Should default to assistant
        assert agent_type == AgentType.ASSISTANT
        assert confidence == 0.5

    def test_delegate_to_agent_architect(self):
        """Test delegation to architect agent."""
        mock_ai = MockAIService(response="Here's your architectural design...")
        router = AgentDelegationRouter(mock_ai)

        response = router.delegate_to_agent(AgentType.ARCHITECT, "Design a caching layer", [])

        assert response == "Here's your architectural design..."
        assert mock_ai.calls
        assert "architect" in mock_ai.calls[0]["context"].get("agent_type", "").lower()

    def test_delegate_to_agent_with_history(self):
        """Test delegation passes conversation history."""
        mock_ai = MockAIService(response="Based on our previous discussion...")
        router = AgentDelegationRouter(mock_ai)

        history = [
            {"role": "user", "content": "Let's design a caching layer"},
            {"role": "assistant", "content": "Sure, I can help with that"},
        ]

        router.delegate_to_agent(AgentType.ARCHITECT, "What about Redis?", history)

        assert mock_ai.calls
        # History should be truncated to last 5
        assert len(mock_ai.calls[0]["history"]) <= 5

    def test_get_delegation_prompt_architect(self):
        """Test delegation prompt generation for architect."""
        mock_ai = MockAIService()
        router = AgentDelegationRouter(mock_ai)

        prompt = router._get_delegation_prompt(AgentType.ARCHITECT, "Design a caching layer")

        assert "architect" in prompt.lower()
        assert "Design a caching layer" in prompt

    def test_get_delegation_prompt_project_manager(self):
        """Test delegation prompt generation for project_manager."""
        mock_ai = MockAIService()
        router = AgentDelegationRouter(mock_ai)

        prompt = router._get_delegation_prompt(AgentType.PROJECT_MANAGER, "Show the roadmap")

        assert "project" in prompt.lower()
        assert "Show the roadmap" in prompt

    def test_get_delegation_prompt_code_developer(self):
        """Test delegation prompt generation for code_developer."""
        mock_ai = MockAIService()
        router = AgentDelegationRouter(mock_ai)

        prompt = router._get_delegation_prompt(AgentType.CODE_DEVELOPER, "Implement the feature")

        assert "developer" in prompt.lower()
        assert "Implement the feature" in prompt

    def test_classify_intent_case_insensitive(self):
        """Test intent classification is case-insensitive."""
        router = AgentDelegationRouter(MockAIService())

        # All should classify as ARCHITECT
        agent_type1, _ = router.classify_intent("DESIGN a caching layer")
        agent_type2, _ = router.classify_intent("design a caching layer")
        agent_type3, _ = router.classify_intent("Design A CACHING LAYER")

        assert agent_type1 == AgentType.ARCHITECT
        assert agent_type2 == AgentType.ARCHITECT
        assert agent_type3 == AgentType.ARCHITECT

    def test_delegate_to_agent_empty_history(self):
        """Test delegation handles empty history."""
        mock_ai = MockAIService(response="Response with empty history")
        router = AgentDelegationRouter(mock_ai)

        response = router.delegate_to_agent(AgentType.ARCHITECT, "Design something", [])

        assert response == "Response with empty history"
        assert mock_ai.calls[0]["history"] == []

    def test_classify_intent_multiple_keywords(self):
        """Test classification with multiple keywords."""
        router = AgentDelegationRouter(MockAIService())

        # This has keywords for both architect and project_manager
        # But "design" comes first in the architect patterns
        agent_type, confidence = router.classify_intent("Design the architecture and update the roadmap")

        # Should match first agent that matches
        assert agent_type in [AgentType.ARCHITECT, AgentType.PROJECT_MANAGER]
        assert confidence > 0.8


class TestAgentClassificationEdgeCases:
    """Test edge cases in agent classification."""

    def test_empty_input(self):
        """Test classification with empty input."""
        mock_ai = MockAIService(
            response="<classification><agent>assistant</agent><confidence>0.5</confidence></classification>"
        )
        router = AgentDelegationRouter(mock_ai)

        agent_type, confidence = router.classify_intent("")

        # Should use AI fallback for empty input
        assert mock_ai.calls

    def test_very_long_input(self):
        """Test classification with very long input."""
        router = AgentDelegationRouter(MockAIService())

        long_input = "Design " + "a caching layer " * 100

        agent_type, confidence = router.classify_intent(long_input)

        # Should still classify as architect (pattern matching)
        assert agent_type == AgentType.ARCHITECT
        assert confidence > 0.8

    def test_special_characters(self):
        """Test classification with special characters."""
        router = AgentDelegationRouter(MockAIService())

        agent_type, confidence = router.classify_intent("Design!@#$%^ a caching layer")

        # Should still work (case-insensitive substring matching)
        assert agent_type == AgentType.ARCHITECT
