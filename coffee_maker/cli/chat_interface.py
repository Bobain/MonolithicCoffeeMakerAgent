"""Chat Interface - Interactive chat session with Rich UI.

This module provides an interactive REPL-style chat interface for managing
the roadmap with Claude AI assistance and rich terminal UI.

Example:
    >>> from coffee_maker.cli.chat_interface import ChatSession
    >>> from coffee_maker.cli.ai_service import AIService
    >>> from coffee_maker.cli.roadmap_editor import RoadmapEditor
    >>>
    >>> editor = RoadmapEditor(roadmap_path)
    >>> ai_service = AIService()
    >>> session = ChatSession(ai_service, editor)
    >>> session.start()
"""

import logging
import os
from pathlib import Path
from typing import Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.commands import get_command_handler, list_commands
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


class ProjectManagerCompleter(Completer):
    """Auto-completer for project-manager chat.

    Provides Tab completion for:
    - Slash commands (/help, /view, /add, etc.)
    - Priority names (PRIORITY 1, PRIORITY 2, etc.)
    - File paths (when relevant)
    """

    def __init__(self, editor: RoadmapEditor):
        """Initialize completer.

        Args:
            editor: RoadmapEditor instance for priority completion
        """
        self.editor = editor
        self.commands = [
            "help",
            "view",
            "add",
            "update",
            "status",
            "exit",
            "quit",
            "notifications",
        ]

    def get_completions(self, document, complete_event):
        """Generate completions based on current input.

        Args:
            document: Current document being edited
            complete_event: Completion event

        Yields:
            Completion objects
        """
        word_before_cursor = document.get_word_before_cursor()
        text_before_cursor = document.text_before_cursor

        # Complete slash commands
        if text_before_cursor.startswith("/") or (text_before_cursor == "" and word_before_cursor == ""):
            for cmd in self.commands:
                if cmd.startswith(word_before_cursor.lstrip("/")):
                    yield Completion(
                        cmd if text_before_cursor.startswith("/") else f"/{cmd}",
                        start_position=-len(word_before_cursor),
                        display_meta=f"command",
                    )

        # Complete priority names when relevant
        elif any(keyword in text_before_cursor.lower() for keyword in ["priority", "PRIORITY", "view", "update"]):
            try:
                priorities = self.editor.list_priorities()
                for priority in priorities[:15]:  # Limit to 15 for performance
                    priority_name = priority["name"]
                    if priority_name.lower().startswith(word_before_cursor.lower()):
                        yield Completion(
                            priority_name,
                            start_position=-len(word_before_cursor),
                            display_meta=f"{priority['title'][:40]}...",
                        )
            except Exception as e:
                logger.debug(f"Priority completion failed: {e}")


class ChatSession:
    """Interactive chat session manager.

    Manages the interactive REPL loop, command routing, and rich terminal UI
    for the project manager CLI.

    Attributes:
        ai_service: AIService instance for natural language processing
        editor: RoadmapEditor instance for roadmap manipulation
        console: Rich console for terminal output
        history: Conversation history
        active: Session active flag

    Example:
        >>> session = ChatSession(ai_service, editor)
        >>> session.start()  # Starts interactive session
    """

    def __init__(self, ai_service: AIService, editor: RoadmapEditor, enable_streaming: bool = True):
        """Initialize chat session.

        Args:
            ai_service: AIService instance
            editor: RoadmapEditor instance
            enable_streaming: If True, use streaming responses (default: True)
        """
        self.ai_service = ai_service
        self.editor = editor
        self.console = Console()
        self.history: List[Dict] = []
        self.active = False

        # Check for streaming environment variable
        env_no_streaming = os.environ.get("PROJECT_MANAGER_NO_STREAMING", "").lower() in ["1", "true", "yes"]
        self.enable_streaming = enable_streaming and not env_no_streaming

        # Setup prompt-toolkit for advanced input
        self._setup_prompt_session()

        logger.info(f"ChatSession initialized (streaming={'enabled' if self.enable_streaming else 'disabled'})")

    def _setup_prompt_session(self):
        """Setup prompt-toolkit session with history, completion, and key bindings."""
        # History file location
        history_dir = Path.home() / ".project_manager"
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / "chat_history.txt"

        # Key bindings for multi-line input
        bindings = KeyBindings()

        @bindings.add("enter")
        def _(event):
            """Submit on Enter."""
            event.current_buffer.validate_and_handle()

        @bindings.add("s-enter")  # Shift+Enter
        def _(event):
            """Insert newline on Shift+Enter."""
            event.current_buffer.insert_text("\n")

        @bindings.add("escape", "enter")  # Alt+Enter (fallback)
        def _(event):
            """Insert newline on Alt+Enter (alternative to Shift+Enter)."""
            event.current_buffer.insert_text("\n")

        # Create prompt session
        self.prompt_session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=ProjectManagerCompleter(self.editor),
            complete_while_typing=False,  # Complete only on Tab
            multiline=False,  # Will be controlled by key bindings
            key_bindings=bindings,
            enable_history_search=True,  # Ctrl+R for reverse search
        )

    def start(self):
        """Start interactive chat session.

        Displays welcome message and enters REPL loop.
        Handles user input, routes commands, and displays responses.

        Example:
            >>> session.start()
            # Enters interactive mode
        """
        self.active = True
        self._display_welcome()
        self._load_roadmap_context()
        self._run_repl_loop()

    def _run_repl_loop(self):
        """Main REPL loop.

        Continuously reads user input and processes it until
        the session is terminated. Uses prompt-toolkit for advanced
        input features (multi-line, history, auto-completion).
        """
        while self.active:
            try:
                # Show prompt with Rich styling hint
                self.console.print("\n[bold cyan]You:[/] ", end="")

                # Get user input with prompt-toolkit
                # (supports: ↑/↓ history, Tab completion, Shift+Enter multi-line)
                user_input = self.prompt_session.prompt("")

                if not user_input.strip():
                    continue

                # Check for exit commands
                if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                    self._display_goodbye()
                    break

                # Check for help command
                if user_input.lower() in ["/help", "help"]:
                    self._display_help()
                    continue

                # Process input
                response = self._process_input(user_input)

                # Display response
                self._display_response(response)

                # Add to history
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "assistant", "content": response})

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Type /exit to quit.[/]")
            except EOFError:
                self._display_goodbye()
                break
            except Exception as e:
                logger.error(f"Error in REPL loop: {e}", exc_info=True)
                self.console.print(f"\n[red]Error: {e}[/]")

    def _process_input(self, user_input: str) -> str:
        """Process user input (command or natural language).

        Routes input to appropriate handler based on whether it's
        a slash command or natural language.

        Args:
            user_input: User input string

        Returns:
            Response message

        Example:
            >>> response = session._process_input("/help")
            >>> response = session._process_input("What should we do next?")
        """
        # Check if it's a slash command
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        else:
            # Natural language - use AI
            return self._handle_natural_language(user_input)

    def _handle_command(self, command: str) -> str:
        """Handle slash command.

        Parses command and arguments, then routes to appropriate
        command handler.

        Args:
            command: Command string (e.g., "/add New Priority")

        Returns:
            Response message

        Example:
            >>> response = session._handle_command("/view 3")
        """
        # Parse command and args
        parts = command.split(maxsplit=1)
        cmd_name = parts[0][1:].lower()  # Remove '/'
        args_str = parts[1] if len(parts) > 1 else ""
        args = args_str.split() if args_str else []

        logger.debug(f"Handling command: {cmd_name} with args: {args}")

        # Get command handler
        handler = get_command_handler(cmd_name)

        if handler:
            try:
                return handler.execute(args, self.editor)
            except Exception as e:
                logger.error(f"Command execution failed: {e}", exc_info=True)
                return f"❌ Command failed: {str(e)}"
        else:
            return f"❌ Unknown command: /{cmd_name}\n" f"Type /help to see available commands."

    def _handle_natural_language(self, text: str) -> str:
        """Handle natural language input with AI.

        Uses AIService to process natural language and optionally
        execute extracted actions. Supports streaming responses.

        Args:
            text: Natural language input

        Returns:
            Response message

        Example:
            >>> response = session._handle_natural_language(
            ...     "Add a priority for authentication"
            ... )
        """
        try:
            # Build context from current roadmap
            context = self._build_context()

            logger.debug(f"Processing natural language: {text[:100]}...")

            # Use streaming if enabled
            if self.enable_streaming:
                return self._handle_natural_language_stream(text, context)
            else:
                # Get AI response (blocking)
                response = self.ai_service.process_request(
                    user_input=text, context=context, history=self.history, stream=False
                )

                # If AI suggests an action, ask for confirmation
                if response.action:
                    action_desc = self._describe_action(response.action)
                    confirmation = self.console.input(
                        f"\n[yellow]Action suggested: {action_desc}[/]\n" f"[yellow]Execute this action? [y/n]:[/] "
                    )

                    if confirmation.lower() in ["y", "yes"]:
                        result = self._execute_action(response.action)
                        return f"{response.message}\n\n{result}"

                return response.message

        except Exception as e:
            logger.error(f"Natural language processing failed: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def _handle_natural_language_stream(self, text: str, context: Dict) -> str:
        """Handle natural language with streaming response.

        Args:
            text: Natural language input
            context: Roadmap context

        Returns:
            Complete response message
        """
        try:
            # Show typing indicator briefly
            with Live(
                Spinner("dots", text="[cyan]Claude is thinking...[/]"), console=self.console, refresh_per_second=10
            ):
                # Brief pause for UX (let user see the indicator)
                import time

                time.sleep(0.3)

            # Stream response
            self.console.print("\n[bold green]Claude:[/] ", end="")

            full_response = ""
            for chunk in self.ai_service.process_request_stream(user_input=text, context=context, history=self.history):
                self.console.print(chunk, end="")
                full_response += chunk

            self.console.print()  # Final newline

            # TODO: Extract action from full_response if needed
            # For now, streaming responses don't support actions

            return full_response

        except Exception as e:
            logger.error(f"Streaming natural language processing failed: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def _build_context(self) -> Dict:
        """Build context dictionary from current roadmap.

        Returns:
            Context dictionary with roadmap summary

        Example:
            >>> context = session._build_context()
            >>> print(context['roadmap_summary']['total'])
            9
        """
        summary = self.editor.get_priority_summary()

        return {
            "roadmap_summary": summary,
            "current_session": len(self.history),
        }

    def _describe_action(self, action: Dict) -> str:
        """Describe an action in human-readable format.

        Args:
            action: Action dictionary

        Returns:
            Human-readable description

        Example:
            >>> desc = session._describe_action({
            ...     'type': 'add_priority',
            ...     'priority': '10',
            ...     'title': 'Authentication'
            ... })
        """
        action_type = action.get("type", "unknown")

        if action_type == "add_priority":
            return f"Add new priority: {action.get('title', 'Unknown')}"
        elif action_type == "update_priority":
            return (
                f"Update {action.get('priority', 'Unknown')} "
                f"{action.get('field', 'status')} to {action.get('value', 'Unknown')}"
            )
        elif action_type == "start_daemon":
            return f"Start daemon on {action.get('priority', 'next priority')}"
        else:
            return f"Execute {action_type}"

    def _execute_action(self, action: Dict) -> str:
        """Execute an action extracted from AI response.

        Args:
            action: Action dictionary

        Returns:
            Result message

        Example:
            >>> result = session._execute_action({
            ...     'type': 'update_priority',
            ...     'priority': '3',
            ...     'field': 'status',
            ...     'value': '✅ Complete'
            ... })
        """
        try:
            action_type = action.get("type")

            if action_type == "add_priority":
                # Use add command
                handler = get_command_handler("add")
                if handler:
                    title = action.get("title", "New Priority")
                    return handler.execute([title], self.editor)

            elif action_type == "update_priority":
                # Use update command
                handler = get_command_handler("update")
                if handler:
                    priority = action.get("priority", "")
                    field = action.get("field", "status")
                    value = action.get("value", "")
                    return handler.execute([priority, field, value], self.editor)

            return "❌ Action execution not implemented yet"

        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return f"❌ Failed to execute action: {str(e)}"

    def _display_welcome(self):
        """Display welcome message with rich formatting."""
        features = (
            "✨ [bold]New Features:[/] ✨\n"
            "  • [cyan]Streaming responses[/] - Text appears progressively\n"
            "  • [cyan]↑/↓[/] - Navigate input history\n"
            "  • [cyan]Tab[/] - Auto-complete commands and priorities\n"
            "  • [cyan]Shift+Enter[/] - Multi-line input\n"
            "  • [cyan]Ctrl+R[/] - Reverse history search\n\n"
        )

        panel = Panel.fit(
            "[bold cyan]Coffee Maker - AI Project Manager[/]\n\n"
            "Powered by Claude AI - Your intelligent roadmap assistant\n\n"
            f"{features}"
            "Type [bold]/help[/] for commands or just chat naturally\n\n"
            "[dim]Session started. Type /exit to quit.[/]",
            title="🤖 Welcome",
            border_style="cyan",
        )
        self.console.print(panel)

    def _display_goodbye(self):
        """Display goodbye message."""
        self.active = False
        self.console.print("\n[bold cyan]Thank you for using Coffee Maker Project Manager![/]")
        self.console.print("[dim]Session ended. All changes have been saved.[/]\n")

    def _display_response(self, response: str):
        """Display AI response with rich formatting.

        Args:
            response: Response text (supports markdown)

        Example:
            >>> session._display_response("**Success!** Priority added.")
        """
        self.console.print("\n[bold green]Claude:[/]")

        # Try to render as markdown
        try:
            md = Markdown(response)
            self.console.print(md)
        except Exception:
            # Fallback to plain text
            self.console.print(response)

    def _display_help(self):
        """Display help with all available commands."""
        table = Table(
            title="Available Commands",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        # Get all registered commands
        commands = list_commands()

        # Add commands to table
        for name, handler in sorted(commands.items()):
            table.add_row(f"/{name}", handler.description)

        # Add built-in commands
        table.add_row("/help", "Show this help message")
        table.add_row("/exit", "Exit chat session")

        self.console.print(table)
        self.console.print("\n[italic]You can also use natural language![/]")
        self.console.print('[dim]Example: "Add a priority for user authentication"[/]\n')

    def _load_roadmap_context(self):
        """Load roadmap context at session start.

        Loads roadmap summary and displays brief status.
        """
        try:
            summary = self.editor.get_priority_summary()

            self.console.print(
                f"\n[dim]Loaded roadmap: {summary['total']} priorities "
                f"({summary['completed']} completed, "
                f"{summary['in_progress']} in progress, "
                f"{summary['planned']} planned)[/]\n"
            )

        except Exception as e:
            logger.warning(f"Failed to load roadmap context: {e}")
            self.console.print("\n[yellow]Warning: Could not load roadmap summary[/]\n")
