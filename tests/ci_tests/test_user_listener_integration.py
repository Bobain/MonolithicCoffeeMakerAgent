"""Integration tests for user_listener CLI.

Tests cover:
- Full user-listener flow
- Intent classification and delegation
- Conversation context preservation
- Singleton enforcement
- Error handling
"""

import pytest

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType
from coffee_maker.cli.agent_router import AgentDelegationRouter
from coffee_maker.cli.user_listener import UserListenerCLI


class MockChatSession:
    """Mock ChatSession for testing."""

    def __init__(self):
        """Initialize mock chat session."""
        self.history = []
        self.responses = []
        self.prompt_session = MockPromptSession()

    def _display_response(self, response: str):
        """Mock display response."""
        self.responses.append(response)


class MockPromptSession:
    """Mock prompt session."""

    def __init__(self):
        """Initialize mock prompt."""
        self.prompts = []

    def prompt(self, text: str):
        """Mock prompt method."""
        if not self.prompts:
            return "/exit"  # Default to exit
        return self.prompts.pop(0)


class MockAIService:
    """Mock AIService for integration tests."""

    def __init__(self):
        """Initialize mock AI service."""
        self.calls = []

    def process_request(self, user_input: str, context: dict, history: list, stream: bool = False):
        """Mock process_request."""
        self.calls.append({"user_input": user_input, "context": context, "history": history})

        class MockResponse:
            def __init__(self, msg):
                self.message = msg

        # Return different responses based on user input
        if "design" in user_input.lower():
            return MockResponse("Architectural recommendation: Use a distributed cache like Redis.")
        elif "roadmap" in user_input.lower():
            return MockResponse("Current priorities: PRIORITY 1, PRIORITY 2, etc.")
        else:
            return MockResponse("I can help with that.")

    def check_available(self):
        """Mock check_available."""
        return True


class TestUserListenerIntegration:
    """Integration tests for UserListenerCLI."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI with mocked dependencies."""
        cli = UserListenerCLI.__new__(UserListenerCLI)
        cli.ai_service = MockAIService()
        cli.chat_session = MockChatSession()
        cli.agent_router = AgentDelegationRouter(cli.ai_service)
        cli.registry = AgentRegistry()
        return cli

    def test_user_listener_initialization(self, cli_with_mocks):
        """Test user_listener CLI initialization."""
        cli = cli_with_mocks

        assert cli.ai_service is not None
        assert cli.chat_session is not None
        assert cli.agent_router is not None
        assert cli.registry is not None

    def test_user_listener_process_input_architecture(self, cli_with_mocks):
        """Test processing input that routes to architect."""
        cli = cli_with_mocks

        response = cli._process_input("Design a caching layer")

        assert response is not None
        assert len(response) > 0

    def test_user_listener_process_input_roadmap(self, cli_with_mocks):
        """Test processing input that routes to project_manager."""
        cli = cli_with_mocks

        response = cli._process_input("Show me the roadmap")

        assert response is not None
        assert len(response) > 0

    def test_user_listener_context_building(self, cli_with_mocks):
        """Test that context is properly built."""
        cli = cli_with_mocks

        context = cli._build_context()

        assert "role" in context
        assert context["role"] == "user_listener"
        assert "responsibilities" in context
        assert "available_agents" in context
        assert len(context["available_agents"]) >= 6

    def test_user_listener_singleton_enforcement(self):
        """Test that only one user_listener can run at a time."""
        registry = AgentRegistry()
        registry.reset()

        # Register first instance
        registry.register_agent(AgentType.USER_LISTENER)

        # Try to register second instance - should fail
        with pytest.raises(AgentAlreadyRunningError):
            registry.register_agent(AgentType.USER_LISTENER)

        registry.reset()

    def test_user_listener_context_manager_registration(self):
        """Test context manager registration."""
        registry = AgentRegistry()
        registry.reset()

        # Should register and unregister cleanly
        with AgentRegistry.register(AgentType.USER_LISTENER):
            assert registry.is_registered(AgentType.USER_LISTENER)

        assert not registry.is_registered(AgentType.USER_LISTENER)

    def test_user_listener_context_manager_exception_handling(self):
        """Test context manager handles exceptions properly."""
        registry = AgentRegistry()
        registry.reset()

        # Even if exception occurs, should unregister
        try:
            with AgentRegistry.register(AgentType.USER_LISTENER):
                assert registry.is_registered(AgentType.USER_LISTENER)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should be unregistered even after exception
        assert not registry.is_registered(AgentType.USER_LISTENER)

    def test_user_listener_process_input_ai_handling(self, cli_with_mocks):
        """Test processing ambiguous input with AI."""
        cli = cli_with_mocks

        # Ambiguous request
        response = cli._process_input("Help me with something unclear")

        assert response is not None

    def test_user_listener_handle_with_ai(self, cli_with_mocks):
        """Test _handle_with_ai method."""
        cli = cli_with_mocks

        response = cli._handle_with_ai("Tell me about the system")

        assert response is not None
        assert len(response) > 0

    def test_user_listener_agent_router_initialization(self, cli_with_mocks):
        """Test that agent_router is properly initialized."""
        cli = cli_with_mocks

        assert cli.agent_router is not None
        assert cli.agent_router.ai_service is not None


class TestUserListenerErrorHandling:
    """Test error handling in user_listener."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI with mocked dependencies."""
        cli = UserListenerCLI.__new__(UserListenerCLI)
        cli.ai_service = MockAIService()
        cli.chat_session = MockChatSession()
        cli.agent_router = AgentDelegationRouter(cli.ai_service)
        cli.registry = AgentRegistry()
        return cli

    def test_user_listener_handles_invalid_input_gracefully(self, cli_with_mocks):
        """Test handling of invalid/problematic input."""
        cli = cli_with_mocks

        # Should not raise exception
        response = cli._process_input("")
        assert isinstance(response, str)

    def test_user_listener_handles_ai_service_errors(self):
        """Test handling of AI service errors."""

        class FailingAIService:
            def process_request(self, *args, **kwargs):
                raise RuntimeError("AI service error")

        cli = UserListenerCLI.__new__(UserListenerCLI)
        cli.ai_service = FailingAIService()
        cli.chat_session = MockChatSession()
        cli.agent_router = AgentDelegationRouter(FailingAIService())
        cli.registry = AgentRegistry()

        # Should handle error gracefully
        response = cli._process_input("Some request")
        assert isinstance(response, str)
        assert "error" in response.lower()


class TestAgentDelegation:
    """Test agent delegation in user_listener."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI with mocked dependencies."""
        cli = UserListenerCLI.__new__(UserListenerCLI)
        cli.ai_service = MockAIService()
        cli.chat_session = MockChatSession()
        cli.agent_router = AgentDelegationRouter(cli.ai_service)
        cli.registry = AgentRegistry()
        return cli

    def test_delegation_to_architect(self, cli_with_mocks):
        """Test delegation path to architect."""
        cli = cli_with_mocks

        agent_type, confidence = cli.agent_router.classify_intent("Design a caching layer")

        assert agent_type == AgentType.ARCHITECT
        assert confidence > 0.8

    def test_delegation_to_project_manager(self, cli_with_mocks):
        """Test delegation path to project_manager."""
        cli = cli_with_mocks

        agent_type, confidence = cli.agent_router.classify_intent("Show the roadmap")

        assert agent_type == AgentType.PROJECT_MANAGER
        assert confidence > 0.8

    def test_delegation_to_code_developer(self, cli_with_mocks):
        """Test delegation path to code_developer."""
        cli = cli_with_mocks

        agent_type, confidence = cli.agent_router.classify_intent("Implement the feature")

        assert agent_type == AgentType.CODE_DEVELOPER
        assert confidence > 0.8

    def test_delegation_preserves_conversation_context(self, cli_with_mocks):
        """Test that delegation preserves conversation context."""
        cli = cli_with_mocks
        cli.chat_session.history = [
            {"role": "user", "content": "Design a caching layer"},
            {"role": "assistant", "content": "I recommend Redis"},
        ]

        response = cli._process_input("What about Memcached?")

        # Should process with history
        assert response is not None

    def test_user_listener_classify_intent_accuracy(self, cli_with_mocks):
        """Test accuracy of intent classification."""
        cli = cli_with_mocks

        test_cases = [
            ("Design a caching layer", AgentType.ARCHITECT),
            ("Show the roadmap", AgentType.PROJECT_MANAGER),
            ("Implement the feature", AgentType.CODE_DEVELOPER),
            ("Explain how this works", AgentType.ASSISTANT),
            ("Make the dashboard UI better", AgentType.UX_DESIGN_EXPERT),
        ]

        for user_input, expected_agent in test_cases:
            agent_type, confidence = cli.agent_router.classify_intent(user_input)
            assert agent_type == expected_agent, f"Failed for input: {user_input}"
            assert confidence > 0.7, f"Low confidence for input: {user_input}"


class TestUserListenerHelp:
    """Test help and documentation features."""

    @pytest.fixture
    def cli_with_mocks(self):
        """Create CLI with mocked dependencies."""
        cli = UserListenerCLI.__new__(UserListenerCLI)
        cli.ai_service = MockAIService()
        cli.chat_session = MockChatSession()
        cli.agent_router = AgentDelegationRouter(cli.ai_service)
        cli.registry = AgentRegistry()
        return cli

    def test_context_includes_all_agents(self, cli_with_mocks):
        """Test that context includes all available agents."""
        cli = cli_with_mocks
        context = cli._build_context()

        agents_list = context.get("available_agents", [])
        agent_names = [ag.split(" - ")[0].lower() for ag in agents_list]

        assert "project_manager" in agent_names
        assert "architect" in agent_names
        assert "code_developer" in agent_names
        assert "assistant" in agent_names

    def test_context_describes_responsibilities(self, cli_with_mocks):
        """Test that context describes user_listener responsibilities."""
        cli = cli_with_mocks
        context = cli._build_context()

        responsibilities = context.get("responsibilities", [])
        assert len(responsibilities) > 0
        # Check that at least one responsibility contains "interface"
        assert any("interface" in r.lower() for r in responsibilities)
