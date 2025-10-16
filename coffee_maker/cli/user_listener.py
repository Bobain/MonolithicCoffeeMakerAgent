"""User Listener CLI - Primary user interface for MonolithicCoffeeMakerAgent.

This module provides the standalone `poetry run user-listener` command that serves
as the PRIMARY USER INTERFACE for the MonolithicCoffeeMakerAgent system.

Architecture:
    UserListenerCLI: Main class for interactive chat interface
    - Uses Haiku 4.5 for cost-efficient UI orchestration
    - Reuses existing ChatSession infrastructure
    - AgentDelegationRouter for intent classification and delegation
    - Enforces singleton pattern via AgentRegistry

Usage:
    $ poetry run user-listener

Key Features:
    - Interactive REPL for user input
    - Intent classification to route to appropriate agents
    - Rich terminal output with markdown and syntax highlighting
    - Conversation context preservation
    - Singleton enforcement (only one instance at a time)

References:
    - SPEC-010: User-Listener UI Command
    - AgentRegistry: Singleton enforcement
    - ChatSession: Existing chat infrastructure reuse
    - AIService: Haiku 4.5 model for orchestration
"""

import logging
from typing import Dict

from rich.console import Console

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType
from coffee_maker.cli.agent_router import AgentDelegationRouter
from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.chat_interface import ChatSession

logger = logging.getLogger(__name__)
console = Console()


class UserListenerCLI:
    """Primary user interface for MonolithicCoffeeMakerAgent.

    ONLY agent with UI responsibility. All user interactions go through here.

    This class:
    - Manages interactive chat session with Haiku 4.5
    - Classifies user intent and delegates to specialized agents
    - Maintains conversation history and context
    - Enforces singleton pattern via AgentRegistry
    - Provides rich terminal UI with markdown rendering

    Attributes:
        ai_service: AIService with Haiku 4.5 model
        chat_session: ChatSession for managing conversation
        agent_router: AgentDelegationRouter for intent classification
        registry: AgentRegistry for singleton enforcement
    """

    def __init__(self):
        """Initialize user-listener CLI.

        Sets up:
        - Haiku 4.5 AI service for cost-efficient orchestration
        - ChatSession for conversation management
        - AgentDelegationRouter for intent routing
        - AgentRegistry for singleton enforcement
        """
        # Use Haiku 4.5 for cost-efficient UI orchestration
        self.ai_service = AIService(model="claude-3-5-haiku-20241022", max_tokens=4000, use_claude_cli=False)

        # Reuse existing ChatSession infrastructure
        self.chat_session = ChatSession(ai_service=self.ai_service, editor=None, enable_streaming=True)

        # Agent delegation router
        self.agent_router = AgentDelegationRouter(self.ai_service)

        # Register as singleton
        self.registry = AgentRegistry()

    def start(self):
        """Start interactive user-listener session.

        Registers as singleton and starts REPL loop.
        Only exits on /exit, /quit, or Ctrl+C.
        """
        with AgentRegistry.register(AgentType.USER_LISTENER):
            self._display_welcome()
            self._run_repl_loop()

    def _display_welcome(self):
        """Display welcome message."""
        console.print("\n[bold]User Listener[/] [dim]·[/] Primary Interface")
        console.print("[dim]Powered by Claude Haiku 4.5[/]\n")
        console.print("[dim]I'm your interface to the agent team.[/]")
        console.print("[dim]Tell me what you need, and I'll route it to the right specialist.[/]")
        console.print("[dim]Type /exit or /quit to leave.\n[/]")

    def _run_repl_loop(self):
        """Main REPL loop for user interaction.

        Continuously prompts for user input and processes it until exit.
        """
        while True:
            try:
                user_input = self.chat_session.prompt_session.prompt("› ")

                if not user_input.strip():
                    continue

                # Handle exit commands
                if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                    break

                # Process input and display response
                response = self._process_input(user_input)
                self.chat_session._display_response(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing input: {e}", exc_info=True)
                console.print(f"\n[red]Error: {e}[/]\n")

    def _process_input(self, user_input: str) -> str:
        """Process user input and delegate to appropriate agent.

        Args:
            user_input: User's message

        Returns:
            Response from delegated agent or user_listener

        Logic:
            1. Classify intent (which agent should handle this?)
            2. If high confidence (>0.8), delegate directly
            3. Otherwise, ask user_listener's AI (Haiku 4.5) to handle
        """
        try:
            # Classify intent (which agent should handle this?)
            agent_type, confidence = self.agent_router.classify_intent(user_input)

            # Log classification
            logger.info(f"Intent: {agent_type.value} (confidence: {confidence:.2f})")

            # If high confidence, delegate directly
            if confidence > 0.8:
                return self.agent_router.delegate_to_agent(agent_type, user_input, self.chat_session.history)

            # Otherwise, ask user_listener's AI (Haiku 4.5) to handle
            return self._handle_with_ai(user_input)

        except Exception as e:
            logger.error(f"Error in _process_input: {e}", exc_info=True)
            return f"I encountered an error processing your request: {e}"

    def _handle_with_ai(self, user_input: str) -> str:
        """Handle request with user_listener's AI (Haiku 4.5).

        Used for general questions, clarifications, and ambiguous requests
        that don't clearly map to a specific agent.

        Args:
            user_input: User's message

        Returns:
            AI response from Haiku 4.5
        """
        try:
            context = self._build_context()

            response = self.ai_service.process_request(
                user_input=user_input,
                context=context,
                history=self.chat_session.history[-5:] if self.chat_session.history else [],
                stream=False,
            )

            return response.message

        except Exception as e:
            logger.error(f"Error in _handle_with_ai: {e}", exc_info=True)
            return f"I encountered an error: {e}"

    def _build_context(self) -> Dict:
        """Build context for AI requests.

        Returns:
            Context dictionary with agent info
        """
        return {
            "role": "user_listener",
            "responsibilities": [
                "Primary user interface",
                "Intent classification",
                "Agent delegation",
                "Context maintenance",
            ],
            "available_agents": [
                "project_manager - Strategic tasks, ROADMAP, GitHub",
                "architect - Design, specs, ADRs, dependencies",
                "code_developer - Implementation, PRs",
                "assistant - Documentation, demos, bugs",
                "code-searcher - Deep code analysis",
                "ux-design-expert - UI/UX design",
            ],
        }


def main():
    """Main entry point for user-listener CLI.

    Command: poetry run user-listener

    This function:
    1. Sets up logging
    2. Creates UserListenerCLI instance
    3. Registers singleton via AgentRegistry
    4. Starts interactive REPL loop
    5. Handles errors gracefully
    """
    import sys

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    try:
        # Create and start user-listener CLI
        cli = UserListenerCLI()
        cli.start()

    except AgentAlreadyRunningError as e:
        console.print(f"\n[red]Error: {e}[/]\n")
        sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[dim]Goodbye![/]\n")
        sys.exit(0)

    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/]\n")
        logger.error(f"Fatal error in user-listener", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
