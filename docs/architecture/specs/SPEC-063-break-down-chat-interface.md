# SPEC-063: Break Down chat_interface.py

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**: ADR-005 Modular CLI Architecture, REFACTORING_BACKLOG.md

---

## Problem Statement

`coffee_maker/cli/chat_interface.py` is **1,453 lines** - nearly **3x the recommended 500 LOC limit**.

### Current Issues

1. **Cognitive Overload**: Too much to understand in one file
2. **Testing Difficulty**: Hard to test individual components
3. **Change Risk**: Modifications can have unexpected ripple effects
4. **Maintenance Burden**: Takes 10-15 minutes just to orient in the file
5. **Code Reuse**: Components locked inside monolithic file

### File Composition

The file contains 3 classes and multiple responsibilities:

**`DeveloperStatusMonitor`** (207 lines):
- Background thread for status polling
- JSON file reading
- Status formatting
- Progress calculation

**`ProjectManagerCompleter`** (69 lines):
- Tab completion for commands
- Priority name completion
- Keyword-based completion

**`ChatSession`** (1,177 lines!):
- Session management
- REPL loop
- Command routing
- Natural language processing
- Streaming responses
- Daemon integration (start/stop/status)
- Bug tracking integration
- Assistant integration
- Notification checking
- Display rendering
- History persistence
- Context building
- Action execution

**God Class Alert**: `ChatSession` violates Single Responsibility Principle severely.

---

## Proposed Solution

### High-Level Architecture

Break down `chat_interface.py` into **10 focused modules** in new `coffee_maker/cli/chat/` directory:

```
coffee_maker/cli/chat/
├── __init__.py                     # Public API (50 LOC)
├── session.py                      # Core ChatSession coordinator (200 LOC)
├── status_monitor.py               # DeveloperStatusMonitor (150 LOC)
├── completer.py                    # ProjectManagerCompleter (70 LOC)
├── command_handler.py              # Command routing logic (150 LOC)
├── natural_language.py             # NL processing and streaming (200 LOC)
├── display.py                      # UI rendering (welcome, responses, help) (150 LOC)
├── daemon_integration.py           # Daemon communication (200 LOC)
├── bug_integration.py              # Bug tracking workflow (100 LOC)
├── assistant_integration.py        # Assistant bridge (100 LOC)
└── context_builder.py              # Context and history management (100 LOC)
```

**Total**: ~1,420 LOC across 11 files = **~130 LOC per file average**

---

## Detailed Component Design

### 1. `session.py` - Core ChatSession Coordinator (200 LOC)

**Responsibility**: Orchestrate REPL loop and delegate to specialized components.

```python
"""Core chat session coordinator.

Manages the REPL loop and delegates to specialized components
for command handling, natural language processing, and display.
"""

from typing import Optional
from pathlib import Path

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.chat.command_handler import CommandHandler
from coffee_maker.cli.chat.natural_language import NaturalLanguageHandler
from coffee_maker.cli.chat.display import DisplayManager
from coffee_maker.cli.chat.status_monitor import DeveloperStatusMonitor
from coffee_maker.cli.chat.completer import ProjectManagerCompleter
from coffee_maker.cli.chat.context_builder import ContextBuilder


class ChatSession:
    """Interactive chat session coordinator.

    Orchestrates the REPL loop and delegates to specialized components.
    """

    def __init__(
        self,
        ai_service: AIService,
        editor: RoadmapEditor,
        enable_streaming: bool = True,
    ):
        """Initialize chat session.

        Args:
            ai_service: AIService instance
            editor: RoadmapEditor instance
            enable_streaming: Enable streaming responses (default: True)
        """
        self.ai_service = ai_service
        self.editor = editor
        self.enable_streaming = enable_streaming
        self.active = False

        # Initialize components
        self.command_handler = CommandHandler(editor)
        self.nl_handler = NaturalLanguageHandler(ai_service, editor, enable_streaming)
        self.display = DisplayManager()
        self.status_monitor = DeveloperStatusMonitor(poll_interval=2.0)
        self.context_builder = ContextBuilder(editor)

        # Setup prompt session
        self._setup_prompt_session()

        # Load previous session
        self._load_session()

    def start(self):
        """Start interactive session."""
        self.active = True
        self.status_monitor.start()
        self.display.show_welcome()
        self._run_repl_loop()

    def _run_repl_loop(self):
        """Main REPL loop."""
        try:
            while self.active:
                user_input = self._get_user_input()

                if not user_input:
                    continue

                if self._is_exit_command(user_input):
                    break

                response = self._process_input(user_input)
                self.display.show_response(response)
                self._save_to_history(user_input, response)
        finally:
            self.status_monitor.stop()
            self.display.show_goodbye()

    def _process_input(self, user_input: str) -> str:
        """Process user input (command or natural language).

        Args:
            user_input: User input

        Returns:
            Response message
        """
        if user_input.startswith("/"):
            return self.command_handler.handle(user_input)
        else:
            context = self.context_builder.build_context(self.history)
            return self.nl_handler.handle(user_input, context, self.history)
```

**Key Design Points**:
- **Thin coordinator**: Delegates to specialized components
- **Clear boundaries**: Each component has well-defined responsibility
- **Easy to test**: Can mock each component
- **Easy to extend**: Add new handlers without changing core loop

---

### 2. `status_monitor.py` - DeveloperStatusMonitor (150 LOC)

**Responsibility**: Background monitoring of developer status.

```python
"""Developer status monitor.

Polls daemon status file and formats status for display.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class DeveloperStatusMonitor:
    """Background monitor for developer status.

    Polls developer_status.json and maintains current status data.
    """

    def __init__(self, poll_interval: float = 2.0):
        """Initialize status monitor.

        Args:
            poll_interval: Seconds between checks (default: 2.0)
        """
        self.poll_interval = poll_interval
        self.status_file = Path.home() / ".coffee_maker" / "daemon_status.json"
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Thread-safe status storage
        self._status_lock = threading.Lock()
        self._current_status: Optional[Dict] = None

    def start(self):
        """Start background monitoring thread."""
        if self.is_running:
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()

    def stop(self):
        """Stop background monitoring thread."""
        self.is_running = False

    def get_formatted_status(self) -> str:
        """Get formatted status text for toolbar display.

        Returns:
            Multi-line formatted status string
        """
        with self._status_lock:
            status_data = self._current_status

        if not status_data:
            return "⚫ code_developer: Not running"

        return self._format_status(status_data)

    def _monitor_loop(self):
        """Main monitoring loop (runs in background)."""
        while self.is_running:
            try:
                self._check_status()
            except Exception as e:
                logger.error(f"Status monitor error: {e}")

            time.sleep(self.poll_interval)

    def _check_status(self):
        """Check status file and update internal state."""
        if not self.status_file.exists():
            with self._status_lock:
                self._current_status = None
            return

        try:
            with open(self.status_file, "r") as f:
                status_data = json.load(f)

            with self._status_lock:
                self._current_status = status_data
        except json.JSONDecodeError:
            pass  # File mid-write, skip

    def _format_status(self, status_data: Dict) -> str:
        """Format status data for display.

        Args:
            status_data: Status dictionary

        Returns:
            Formatted status string
        """
        # Format logic (extracted from current implementation)
        # Returns multi-line string with progress bar, ETA, etc.
        pass
```

**Benefits**:
- Isolated responsibility
- Easy to test threading logic
- Can be reused in other contexts
- Clear API

---

### 3. `completer.py` - ProjectManagerCompleter (70 LOC)

**Responsibility**: Tab completion for commands and priorities.

```python
"""Project manager tab completion.

Provides auto-completion for commands and priority names.
"""

from prompt_toolkit.completion import Completer, Completion
from coffee_maker.cli.roadmap_editor import RoadmapEditor


class ProjectManagerCompleter(Completer):
    """Auto-completer for project-manager chat."""

    def __init__(self, editor: RoadmapEditor):
        """Initialize completer.

        Args:
            editor: RoadmapEditor for priority completion
        """
        self.editor = editor
        self.commands = [
            "help", "view", "add", "update", "status",
            "start", "stop", "restart", "exit", "quit",
            "notifications",
        ]

    def get_completions(self, document, complete_event):
        """Generate completions based on current input.

        Args:
            document: Current document
            complete_event: Completion event

        Yields:
            Completion objects
        """
        word = document.get_word_before_cursor()
        text = document.text_before_cursor

        # Complete slash commands
        if text.startswith("/"):
            yield from self._complete_commands(word)

        # Complete priority names
        elif any(kw in text.lower() for kw in ["priority", "view", "update"]):
            yield from self._complete_priorities(word)

    def _complete_commands(self, word: str):
        """Complete command names."""
        for cmd in self.commands:
            if cmd.startswith(word.lstrip("/")):
                yield Completion(
                    cmd,
                    start_position=-len(word),
                    display_meta="command"
                )

    def _complete_priorities(self, word: str):
        """Complete priority names."""
        try:
            priorities = self.editor.list_priorities()
            for priority in priorities[:15]:
                name = priority["name"]
                if name.lower().startswith(word.lower()):
                    yield Completion(
                        name,
                        start_position=-len(word),
                        display_meta=priority["title"][:40]
                    )
        except Exception:
            pass
```

**Benefits**:
- Self-contained
- Easy to test
- Easy to extend with new completion sources

---

### 4. `command_handler.py` - Command Routing (150 LOC)

**Responsibility**: Route and execute slash commands.

```python
"""Command routing and execution.

Routes slash commands to appropriate handlers.
"""

import logging
from typing import Optional

from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.commands import get_command_handler
from coffee_maker.cli.chat.daemon_integration import DaemonIntegration
from coffee_maker.process_manager import ProcessManager

logger = logging.getLogger(__name__)


class CommandHandler:
    """Routes and executes slash commands."""

    def __init__(self, editor: RoadmapEditor):
        """Initialize command handler.

        Args:
            editor: RoadmapEditor instance
        """
        self.editor = editor
        self.daemon = DaemonIntegration(ProcessManager())

    def handle(self, command: str) -> str:
        """Handle slash command.

        Args:
            command: Command string (e.g., "/status")

        Returns:
            Response message
        """
        # Parse command
        parts = command.split(maxsplit=1)
        cmd_name = parts[0][1:].lower()
        args_str = parts[1] if len(parts) > 1 else ""
        args = args_str.split() if args_str else []

        logger.debug(f"Handling command: {cmd_name}")

        # Route to daemon commands
        if cmd_name in ["status", "start", "stop", "restart"]:
            return self.daemon.handle_command(cmd_name)

        # Route to other commands
        handler = get_command_handler(cmd_name)
        if handler:
            try:
                return handler.execute(args, self.editor)
            except Exception as e:
                logger.error(f"Command failed: {e}", exc_info=True)
                return f"❌ Command failed: {str(e)}"

        return f"❌ Unknown command: /{cmd_name}\\nType /help for available commands."
```

**Benefits**:
- Clear routing logic
- Easy to add new command types
- Testable without UI

---

### 5. `natural_language.py` - NL Processing (200 LOC)

**Responsibility**: Handle natural language input and streaming.

```python
"""Natural language processing and streaming.

Handles user's natural language input with AI assistance.
"""

import logging
from typing import Dict, List

from rich.console import Console

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.cli.chat.bug_integration import BugIntegration
from coffee_maker.cli.chat.assistant_integration import AssistantIntegration
from coffee_maker.cli.chat.daemon_integration import DaemonIntegration

logger = logging.getLogger(__name__)


class NaturalLanguageHandler:
    """Handles natural language input with AI."""

    def __init__(
        self,
        ai_service: AIService,
        editor: RoadmapEditor,
        enable_streaming: bool = True,
    ):
        """Initialize NL handler.

        Args:
            ai_service: AIService instance
            editor: RoadmapEditor instance
            enable_streaming: Enable streaming (default: True)
        """
        self.ai_service = ai_service
        self.editor = editor
        self.enable_streaming = enable_streaming
        self.console = Console()

        # Initialize integrations
        self.bug_integration = BugIntegration()
        self.assistant_integration = AssistantIntegration()
        self.daemon_integration = DaemonIntegration()

    def handle(
        self,
        user_input: str,
        context: Dict,
        history: List[Dict],
    ) -> str:
        """Handle natural language input.

        Args:
            user_input: User's natural language input
            context: Roadmap context
            history: Conversation history

        Returns:
            Response message
        """
        # Detect bug reports
        if self.bug_integration.is_bug_report(user_input):
            return self.bug_integration.handle(user_input)

        # Detect daemon commands
        if self.daemon_integration.is_daemon_command(user_input):
            return self.daemon_integration.handle(user_input)

        # Check if assistant should handle complex question
        if self.assistant_integration.should_handle(user_input):
            return self.assistant_integration.handle(user_input)

        # Normal AI response
        if self.enable_streaming:
            return self._handle_streaming(user_input, context, history)
        else:
            return self._handle_blocking(user_input, context, history)

    def _handle_streaming(
        self,
        user_input: str,
        context: Dict,
        history: List[Dict],
    ) -> str:
        """Handle with streaming response."""
        self.console.print("\\n[dim]...[/]", end="\\r")
        self.console.print("\\n[bold]Claude[/]")

        full_response = ""
        for chunk in self.ai_service.process_request_stream(
            user_input=user_input,
            context=context,
            history=history,
        ):
            self.console.print(chunk, end="")
            full_response += chunk

        self.console.print()
        return full_response

    def _handle_blocking(
        self,
        user_input: str,
        context: Dict,
        history: List[Dict],
    ) -> str:
        """Handle with blocking response."""
        response = self.ai_service.process_request(
            user_input=user_input,
            context=context,
            history=history,
            stream=False,
        )
        return response.message
```

**Benefits**:
- Isolated NL processing logic
- Easy to test different input types
- Clear integration points

---

### 6. `display.py` - UI Rendering (150 LOC)

**Responsibility**: Render UI elements (welcome, responses, help).

```python
"""Display management for chat UI.

Handles all UI rendering (welcome, responses, help, goodbye).
"""

import re
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table


class DisplayManager:
    """Manages all UI rendering for chat session."""

    def __init__(self):
        """Initialize display manager."""
        self.console = Console()

    def show_welcome(self):
        """Display welcome message."""
        self.console.print()
        self.console.print("[bold]Coffee Maker[/] [dim]·[/] AI Project Manager")
        self.console.print("[dim]Powered by Claude AI[/]")
        self.console.print()

        # Keyboard shortcuts
        self.console.print("[dim]Keyboard shortcuts:[/]")
        self.console.print("[dim]  /help[/] [dim]- Show commands[/]")
        self.console.print("[dim]  Alt+Enter[/] [dim]- Multi-line input[/]")
        self.console.print("[dim]  ↑↓[/] [dim]- History    [/][dim]Tab[/] [dim]- Complete[/]")
        self.console.print()

    def show_response(self, response: str):
        """Display AI response with syntax highlighting.

        Args:
            response: Response text (supports markdown)
        """
        self.console.print("\\n[bold]Claude[/]")

        try:
            self._render_with_syntax(response)
        except Exception:
            # Fallback to markdown
            try:
                md = Markdown(response)
                self.console.print(md)
            except Exception:
                # Final fallback to plain text
                self.console.print(response)

    def show_help(self, commands: Dict):
        """Display help table.

        Args:
            commands: Dictionary of command_name -> handler
        """
        table = Table(
            title="Available Commands",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for name, handler in sorted(commands.items()):
            table.add_row(f"/{name}", handler.description)

        table.add_row("/help", "Show this help message")
        table.add_row("/exit", "Exit chat session")

        self.console.print(table)

    def show_goodbye(self):
        """Display goodbye message."""
        self.console.print("\\n[dim]Session saved. Goodbye![/]")
        self.console.print()

    def _render_with_syntax(self, response: str):
        """Render response with code syntax highlighting.

        Args:
            response: Response with markdown code blocks
        """
        # Pattern to match code blocks
        code_block_pattern = r"```(\\w+)?\\n(.*?)```"

        parts = []
        last_end = 0

        # Find all code blocks
        for match in re.finditer(code_block_pattern, response, re.DOTALL):
            # Add text before code block
            if match.start() > last_end:
                text = response[last_end:match.start()]
                if text.strip():
                    parts.append(("text", text))

            # Add code block
            language = match.group(1) or "python"
            code = match.group(2).strip()
            parts.append(("code", code, language))

            last_end = match.end()

        # Add remaining text
        if last_end < len(response):
            remaining = response[last_end:]
            if remaining.strip():
                parts.append(("text", remaining))

        # Render parts
        if not parts:
            md = Markdown(response)
            self.console.print(md)
        else:
            for part in parts:
                if part[0] == "text":
                    md = Markdown(part[1])
                    self.console.print(md)
                elif part[0] == "code":
                    code, language = part[1], part[2]
                    syntax = Syntax(
                        code,
                        language,
                        theme="monokai",
                        line_numbers=True,
                    )
                    self.console.print(syntax)
```

**Benefits**:
- All UI logic in one place
- Easy to test rendering
- Easy to change UI style

---

### 7. `daemon_integration.py` - Daemon Communication (200 LOC)

**Responsibility**: All daemon-related operations.

```python
"""Daemon integration for chat interface.

Handles daemon start/stop/status/communication.
"""

import logging
from datetime import datetime
from pathlib import Path

from coffee_maker.process_manager import ProcessManager
from coffee_maker.cli.notifications import NotificationDB, NOTIF_PRIORITY_HIGH
from coffee_maker.utils.file_io import read_json_file

logger = logging.getLogger(__name__)


class DaemonIntegration:
    """Handles all daemon-related operations."""

    def __init__(self, process_manager: Optional[ProcessManager] = None):
        """Initialize daemon integration.

        Args:
            process_manager: ProcessManager instance (creates if None)
        """
        self.process_manager = process_manager or ProcessManager()
        self.notif_db = NotificationDB()
        self.status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

    def is_daemon_command(self, text: str) -> bool:
        """Check if text is a daemon command.

        Args:
            text: User input

        Returns:
            True if daemon command
        """
        daemon_keywords = [
            "ask daemon", "tell daemon", "daemon implement",
            "daemon work on", "daemon please", "ask code_developer",
        ]
        return any(kw in text.lower() for kw in daemon_keywords)

    def handle_command(self, command: str) -> str:
        """Handle daemon control command.

        Args:
            command: Command name (status, start, stop, restart)

        Returns:
            Response message
        """
        if command == "status":
            return self._get_status()
        elif command == "start":
            return self._start()
        elif command == "stop":
            return self._stop()
        elif command == "restart":
            return self._restart()
        else:
            return f"❌ Unknown daemon command: {command}"

    def handle(self, user_command: str) -> str:
        """Handle daemon natural language command.

        Args:
            user_command: User's command to daemon

        Returns:
            Confirmation message
        """
        if not self.process_manager.is_daemon_running():
            return (
                "⚠️  **Daemon Not Running**\\n\\n"
                "Use `/start` to launch the daemon."
            )

        # Send notification to daemon
        notif_id = self.notif_db.create_notification(
            type="command",
            title="Command from project-manager",
            message=user_command,
            priority=NOTIF_PRIORITY_HIGH,
        )

        return (
            f"✅ **Command Sent to Daemon** (#{notif_id})\\n\\n"
            f"Your message has been delivered to code_developer.\\n\\n"
            f"⏰ Response time: May take 12+ hours.\\n\\n"
            f"💡 Use `/notifications` to check for response."
        )

    def _get_status(self) -> str:
        """Get detailed daemon status."""
        if not self.status_file.exists():
            return "❌ Daemon status file not found. Daemon may not be running."

        try:
            status = read_json_file(self.status_file)
            return self._format_status(status)
        except Exception as e:
            return f"❌ Error reading status: {e}"

    def _start(self) -> str:
        """Start daemon."""
        if self.process_manager.is_daemon_running():
            return "✅ Daemon is already running!"

        success = self.process_manager.start_daemon(background=True)
        if success:
            return "✅ Daemon started successfully!"
        else:
            return "❌ Failed to start daemon. Check logs."

    def _stop(self) -> str:
        """Stop daemon."""
        if not self.process_manager.is_daemon_running():
            return "⚠️  Daemon is not running."

        success = self.process_manager.stop_daemon(timeout=10)
        if success:
            return "✅ Daemon stopped successfully."
        else:
            return "❌ Failed to stop daemon. May need manual kill."

    def _restart(self) -> str:
        """Restart daemon."""
        self._stop()
        import time
        time.sleep(2)
        return self._start()

    def _format_status(self, status: Dict) -> str:
        """Format status dictionary for display.

        Args:
            status: Status dictionary

        Returns:
            Formatted status string
        """
        # Format logic here (extracted from current implementation)
        pass
```

**Benefits**:
- All daemon logic in one place
- Easy to test daemon operations
- Clear API for daemon communication

---

### 8. `bug_integration.py` - Bug Tracking (100 LOC)

**Responsibility**: Bug report detection and ticket creation.

```python
"""Bug tracking integration.

Detects bug reports and creates tickets.
"""

import logging
from coffee_maker.cli.bug_tracker import BugTracker
from coffee_maker.cli.notifications import NotificationDB, NOTIF_PRIORITY_HIGH

logger = logging.getLogger(__name__)


class BugIntegration:
    """Handles bug tracking workflow."""

    def __init__(self):
        """Initialize bug integration."""
        self.bug_tracker = BugTracker()
        self.notif_db = NotificationDB()

    def is_bug_report(self, text: str) -> bool:
        """Check if text is a bug report.

        Args:
            text: User input

        Returns:
            True if bug report detected
        """
        return self.bug_tracker.detect_bug_report(text)

    def handle(self, bug_description: str) -> str:
        """Handle bug report.

        Args:
            bug_description: Bug description from user

        Returns:
            Ticket creation confirmation
        """
        try:
            # Create ticket
            bug_number, ticket_path = self.bug_tracker.create_bug_ticket(
                description=bug_description
            )

            # Extract metadata
            title = self.bug_tracker.extract_bug_title(bug_description)
            priority = self.bug_tracker.assess_bug_priority(bug_description)

            # Notify daemon
            notif_id = self.notif_db.create_notification(
                type="bug",
                title=f"BUG-{bug_number:03d}: {title}",
                message=f"New bug reported. See {ticket_path}\\n\\n{bug_description}",
                priority=(NOTIF_PRIORITY_HIGH if priority in ["Critical", "High"] else "normal"),
                context={
                    "bug_number": bug_number,
                    "ticket_path": str(ticket_path),
                    "priority": priority,
                },
            )

            logger.info(f"Bug ticket {bug_number} created, notification {notif_id}")

            return self.bug_tracker.format_ticket_response(
                bug_number, ticket_path, title, priority
            )

        except Exception as e:
            logger.error(f"Failed to create bug ticket: {e}", exc_info=True)
            return f"❌ Failed to create bug ticket: {e}"
```

**Benefits**:
- Isolated bug workflow
- Easy to test
- Clear API

---

### 9. `assistant_integration.py` - Assistant Bridge (100 LOC)

**Responsibility**: LangChain assistant integration.

```python
"""Assistant integration for complex questions.

Bridges chat session to LangChain assistant.
"""

import logging
from coffee_maker.cli.assistant_bridge import AssistantBridge

logger = logging.getLogger(__name__)


class AssistantIntegration:
    """Handles assistant invocation for complex questions."""

    def __init__(self, action_callback=None):
        """Initialize assistant integration.

        Args:
            action_callback: Callback for displaying actions
        """
        self.assistant = AssistantBridge(action_callback=action_callback)

    def should_handle(self, question: str) -> bool:
        """Check if assistant should handle question.

        Args:
            question: User question

        Returns:
            True if assistant should handle
        """
        return (
            self.assistant.is_available()
            and self.assistant.should_invoke_for_question(question)
        )

    def handle(self, question: str) -> str:
        """Invoke assistant for complex question.

        Args:
            question: User question

        Returns:
            Assistant's answer
        """
        try:
            result = self.assistant.invoke(question)
            if result["success"]:
                return result["answer"]
            else:
                error = result.get("error", "Unknown error")
                logger.warning(f"Assistant failed: {error}")
                return None  # Fall back to normal AI
        except Exception as e:
            logger.error(f"Assistant invocation failed: {e}", exc_info=True)
            return None  # Fall back to normal AI
```

**Benefits**:
- Simple bridge to assistant
- Easy to test
- Clean fallback handling

---

### 10. `context_builder.py` - Context Management (100 LOC)

**Responsibility**: Build context for AI requests.

```python
"""Context building for AI requests.

Builds context from roadmap and conversation history.
"""

import logging
from typing import Dict, List
from pathlib import Path
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.utils.file_io import read_json_file, write_json_file

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds context for AI requests."""

    def __init__(self, editor: RoadmapEditor):
        """Initialize context builder.

        Args:
            editor: RoadmapEditor instance
        """
        self.editor = editor
        self.session_dir = Path.home() / ".project_manager" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / "default.json"

    def build_context(self, history: List[Dict]) -> Dict:
        """Build context from roadmap and history.

        Args:
            history: Conversation history

        Returns:
            Context dictionary
        """
        summary = self.editor.get_priority_summary()

        return {
            "roadmap_summary": summary,
            "current_session": len(history),
        }

    def load_history(self) -> List[Dict]:
        """Load conversation history from file.

        Returns:
            List of message dictionaries
        """
        if self.session_file.exists():
            try:
                data = read_json_file(self.session_file, default={"history": []})
                history = data.get("history", [])
                logger.info(f"Loaded {len(history)} messages")
                return history
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")

        return []

    def save_history(self, history: List[Dict]):
        """Save conversation history to file.

        Args:
            history: List of message dictionaries
        """
        try:
            from datetime import datetime
            write_json_file(
                self.session_file,
                {
                    "history": history,
                    "last_updated": datetime.now().isoformat(),
                },
            )
            logger.debug(f"Saved {len(history)} messages")
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
```

**Benefits**:
- Isolated history management
- Easy to test
- Easy to extend with more context sources

---

### 11. `__init__.py` - Public API (50 LOC)

**Responsibility**: Export public API for backward compatibility.

```python
"""Chat interface module.

Provides interactive chat session for project management.
"""

from coffee_maker.cli.chat.session import ChatSession
from coffee_maker.cli.chat.status_monitor import DeveloperStatusMonitor
from coffee_maker.cli.chat.completer import ProjectManagerCompleter

__all__ = [
    "ChatSession",
    "DeveloperStatusMonitor",
    "ProjectManagerCompleter",
]
```

**Benefits**:
- Backward compatibility
- Clean public API
- Easy imports

---

## Migration Strategy

### Phase 1: Create New Module Structure (Day 1)

1. Create `coffee_maker/cli/chat/` directory
2. Create all new module files with stubs
3. Add `__init__.py` with public API
4. No changes to existing code yet

### Phase 2: Write Characterization Tests (Day 1-2)

1. Write tests for `ChatSession` public API
2. Ensure tests cover all major workflows:
   - Starting session
   - Processing commands
   - Processing natural language
   - Daemon integration
   - Bug tracking
   - Assistant integration
3. Run tests against current implementation
4. Ensure 100% pass rate

### Phase 3: Extract Components Incrementally (Day 2-4)

**Order of extraction** (dependencies first):

1. `completer.py` (no dependencies)
2. `status_monitor.py` (no dependencies)
3. `display.py` (no dependencies)
4. `context_builder.py` (no dependencies)
5. `bug_integration.py` (depends on BugTracker)
6. `assistant_integration.py` (depends on AssistantBridge)
7. `daemon_integration.py` (depends on ProcessManager)
8. `command_handler.py` (depends on daemon_integration)
9. `natural_language.py` (depends on bug, assistant, daemon integrations)
10. `session.py` (depends on all others)

**For each component**:
1. Copy relevant code to new module
2. Update imports
3. Run tests (should still pass)
4. Remove code from `chat_interface.py`
5. Run tests again
6. Commit if tests pass

### Phase 4: Update `chat_interface.py` to Re-export (Day 4)

Add backward compatibility:

```python
"""Chat interface - DEPRECATED, use coffee_maker.cli.chat instead.

This file is kept for backward compatibility.
"""

import warnings

# Re-export from new location
from coffee_maker.cli.chat import (
    ChatSession,
    DeveloperStatusMonitor,
    ProjectManagerCompleter,
)

warnings.warn(
    "coffee_maker.cli.chat_interface is deprecated, "
    "use coffee_maker.cli.chat instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ChatSession",
    "DeveloperStatusMonitor",
    "ProjectManagerCompleter",
]
```

### Phase 5: Update All Imports (Day 5)

1. Find all files importing from `chat_interface`
2. Update to import from `coffee_maker.cli.chat`
3. Run full test suite
4. Fix any issues

### Phase 6: Remove Old File (Day 5)

1. Delete `coffee_maker/cli/chat_interface.py`
2. Run tests one final time
3. Update documentation

---

## Testing Strategy

### Unit Tests

Each new module gets comprehensive unit tests:

```python
# tests/unit/cli/chat/test_status_monitor.py
def test_status_monitor_formats_status():
    """Test status formatting."""
    monitor = DeveloperStatusMonitor()
    status = monitor._format_status({
        "status": "running",
        "current_priority": {
            "name": "PRIORITY 5",
            "title": "Test Priority",
        },
    })
    assert "PRIORITY 5" in status
    assert "Test Priority" in status

# tests/unit/cli/chat/test_command_handler.py
def test_command_handler_routes_status():
    """Test /status command routing."""
    editor = Mock()
    handler = CommandHandler(editor)
    response = handler.handle("/status")
    assert "Daemon" in response

# tests/unit/cli/chat/test_natural_language.py
def test_natural_language_detects_bugs():
    """Test bug detection."""
    nl_handler = NaturalLanguageHandler(Mock(), Mock())
    assert nl_handler.bug_integration.is_bug_report("I found a bug in X")
```

### Integration Tests

Test component interactions:

```python
# tests/integration/test_chat_session_integration.py
def test_chat_session_processes_command():
    """Test full command processing flow."""
    session = ChatSession(mock_ai_service, mock_editor)
    response = session._process_input("/status")
    assert "Daemon" in response

def test_chat_session_processes_natural_language():
    """Test NL processing flow."""
    session = ChatSession(mock_ai_service, mock_editor)
    response = session._process_input("What should we work on next?")
    assert response  # Got some response
```

### Characterization Tests

Capture current behavior:

```python
# tests/characterization/test_chat_interface_behavior.py
def test_current_chat_interface_behavior():
    """Capture current behavior before refactoring."""
    # These tests ensure we don't break anything during refactoring
    session = ChatSession(ai_service, editor)

    # Test all major workflows
    assert session._handle_command("/status")
    assert session._handle_natural_language("Hello")
    assert session._process_input("/help")
```

---

## Rollout Plan

### Week 1
- **Day 1-2**: Create module structure, write characterization tests
- **Day 2-4**: Extract components incrementally
- **Day 4-5**: Update imports, remove old file

### Success Criteria

✅ All tests pass
✅ No regressions in functionality
✅ All files <200 LOC
✅ Test coverage maintained (>80%)
✅ Documentation updated

---

## Risks & Mitigations

### Risk 1: Breaking Existing Functionality

**Mitigation**:
- Write characterization tests FIRST
- Extract incrementally, test after each extraction
- Keep backward compatibility during transition

### Risk 2: Import Confusion

**Mitigation**:
- Clear deprecation warnings
- Update all imports in same PR
- Document new import paths

### Risk 3: Thread Safety Issues

**Mitigation**:
- Carefully preserve threading logic in `status_monitor.py`
- Add threading-specific tests
- Review thread-related code carefully

---

## Related Documents

- `ADR-005-modular-cli-architecture.md` - Architectural decision
- `docs/architecture/REFACTORING_BACKLOG.md` - Full refactoring plan
- `SPEC-057-break-down-ai-service.md` - Related refactoring (to be created)

---

## Status

**Draft** - Ready for review and implementation

**Estimated Effort**: 3-5 days

**Priority**: P0 (Critical)

**Blocking**: None (can start immediately)
