# REFACTOR-001: Split Monolithic CLI Files

## Overview

# REFACTOR-001: Split Monolithic CLI Files

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-16
**Priority**: 🔴 CRITICAL
**Estimated Effort**: 12 hours
**Expected Value**: ⭐⭐⭐⭐⭐ (very high)
**ROI**: 4.2

---

## Problem Statement

### Current State

Two CLI files have grown into unmaintainable monoliths:

1. **`roadmap_cli.py`**: 1,593 lines
   - Contains 12+ command handlers
   - Mixes UI rendering, business logic, and data access
   - Hard to test individual commands
   - Frequent merge conflicts

2. **`chat_interface.py`**: 1,559 lines
   - Combines REPL loop, command routing, status monitoring, daemon control, assistant integration, bug tracking
   - Deep nesting (>5 levels in places)
   - Difficult to understand control flow
   - Hard to add new commands

### Impact

**Maintainability**: 😞 Poor
- Developers avoid these files (cognitive overload)
- Bug fixes take 2-3x longer than they should
- New features require touching 100+ line sections

**Testability**: 😞 Very Poor
- Hard to isolate command logic for unit tests
- Integration tests slow and brittle
- Mock setup requires understanding entire file

**Extensibility**: 😞 Poor
- Adding new commands requires modifying large switch statements
- Risk of breaking existing commands
- No clear pattern to follow

---

## Proposed Solution

### Architecture: Command Pattern + Modular Chat Components

Split into focused, single-responsibility modules using the **Command Pattern** for CLI commands and **Strategy Pattern** for chat handlers.

### New Structure

```
coffee_maker/cli/
├── roadmap_cli.py (200 lines)               # Main entry point, command registration
├── commands/                                 # Individual command handlers
│   ├── __init__.py
│   ├── base.py (50 lines)                   # BaseCommand class
│   ├── view_command.py (100 lines)          # /roadmap, view priorities
│   ├── status_command.py (150 lines)        # /status, project health
│   ├── developer_status_command.py (120 lines)  # developer-status
│   ├── notifications_command.py (100 lines) # notifications list/read/clear
│   ├── respond_command.py (80 lines)        # respond to questions
│   ├── spec_command.py (150 lines)          # /spec workflow
│   ├── metrics_command.py (120 lines)       # /metrics
│   ├── summary_command.py (120 lines)       # /summary
│   └── calendar_command.py (120 lines)      # /calendar
├── chat/                                     # Chat interface components
│   ├── __init__.py
│   ├── chat_interface.py (300 lines)        # Core REPL loop
│   ├── status_monitor.py (150 lines)        # DeveloperStatusMonitor
│   ├── completer.py (80 lines)              # ProjectManagerCompleter
│   ├── command_handlers.py (200 lines)      # Command routing
│   ├── natural_language_handler.py (250 lines)  # NL processing
│   ├── daemon_commands.py (150 lines)       # Daemon control
│   ├── assistant_integration.py (100 lines) # Assistant bridge
│   └── bug_reporting.py (150 lines)         # Bug workflow
└── ui/                                       # Shared UI utilities
    ├── __init__.py
    ├── colors.py (50 lines)                 # Color constants
    ├── formatters.py (100 lines)            # Table/list formatters
    └── progress.py (80 lines)               # Progress bars

Total: ~2,420 lines (split from 3,152) with better organization
```

---

## Component Design

### 1. Base Command Class

```python
# coffee_maker/cli/commands/base.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseCommand(ABC):
    """Base class for all CLI commands.

    Provides common functionality:
    - Logging
    - Error handling
    - Output formatting
    - Context management
    """

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """Initialize command with optional context.

        Args:
            context: Shared context (roadmap_path, ai_service, etc.)
        """
        self.context = context or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, args: Any) -> int:
        """Execute the command.

        Args:
            args: Command arguments (parsed by argparse)

        Returns:
            Exit code (0 = success, >0 = error)
        """
        pass

    def handle_error(self, error: Exception) -> int:
        """Handle command execution error.

        Args:
            error: Exception that occurred

        Returns:
            Error exit code
        """
        self.logger.error(f"Command failed: {error}")
        print(f"❌ Error: {str(error)}")
        return 1

    def format_table(self, rows: List[List[str]], headers: List[str]) -> str:
        """Format data as table.

        Args:
            rows: Table rows
            headers: Column headers

        Returns:
            Formatted table string
        """
        from coffee_maker.cli.ui.formatters import TableFormatter
        return TableFormatter.format(rows, headers)
```

### 2. Example Command: ViewCommand

```python
# coffee_maker/cli/commands/view_command.py

from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.cli.ui.formatters import PriorityFormatter

class ViewCommand(BaseCommand):
    """Display roadmap priorities.

    Usage:
        project-manager view [--filter STATUS]
        project-manager /roadmap
    """

    def execute(self, args) -> int:
        """Execute view command.

        Args:
            args: Command arguments (filter, format, etc.)

        Returns:
            0 on success, 1 on error
        """
        try:
            # Get roadmap path from context
            roadmap_path = self.context.get('roadmap_path', 'docs/roadmap/ROADMAP.md')
            parser = RoadmapParser(roadmap_path)

            # Get priorities
            priorities = parser.get_priorities()

            # Apply filter if specified
            if args.filter:
                priorities = [p for p in priorities if args.filter.lower() in p['status'].lower()]

            # Format and display
            formatter = PriorityFormatter()
            output = formatter.format_priority_list(priorities)
            print(output)

            return 0

        except Exception as e:
            return self.handle_error(e)
```

### 3. Main CLI Entry Point

```python
# coffee_maker/cli/roadmap_cli.py (simplified)

import argparse
from coffee_maker.cli.commands import (
    ViewCommand,
    StatusCommand,
    DeveloperStatusCommand,
    NotificationsCommand,
    # ... other commands
)

# Command registry
COMMANDS = {
    'view': ViewCommand,
    'status': StatusCommand,
    'developer-status': DeveloperStatusCommand,
    'notifications': NotificationsCommand,
    # ... more commands
}

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Project Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Register all commands
    for name, command_class in COMMANDS.items():
        command_parser = subparsers.add_parser(name, help=command_class.__doc__)
        # Add command-specific arguments
        if hasattr(command_class, 'add_arguments'):
            command_class.add_arguments(command_parser)

    args = parser.parse_args()

    # Build shared context
    context = {
        'roadmap_path': 'docs/roadmap/ROADMAP.md',
        'ai_service': AIService(),  # Lazy init
        # ... other shared resources
    }

    # Execute command
    if args.command in COMMANDS:
        command = COMMANDS[args.command](context)
        exit_code = command.execute(args)
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)
```

### 4. Chat Interface (Refactored)

```python
# coffee_maker/cli/chat/chat_interface.py (core loop only)

from coffee_maker.cli.chat.status_monitor import StatusMonitor
from coffee_maker.cli.chat.command_handlers import CommandRouter
from coffee_maker.cli.chat.natural_language_handler import NaturalLanguageHandler

class ChatSession:
    """Interactive chat interface for project_manager.

    Responsibilities:
    - REPL loop
    - Input handling
    - Output display
    - Component coordination
    """

    def __init__(self):
        self.running = False
        self.status_monitor = StatusMonitor()
        self.command_router = CommandRouter()
        self.nl_handler = NaturalLanguageHandler()

    def run(self):
        """Run interactive chat loop."""
        self.running = True
        print("🤖 Project Manager Chat")

        while self.running:
            try:
                # Get user input (with status toolbar)
                user_input = self._prompt_with_status()

                if not user_input.strip():
                    continue

                # Route to handler
                response = self._handle_input(user_input)

                # Display response
                print(response)

            except KeyboardInterrupt:
                self.stop()

    def _handle_input(self, text: str) -> str:
        """Route input to appropriate handler."""
        # Check if it's a command
        if self.command_router.is_command(text):
            return self.command_router.handle(text)

        # Otherwise, natural language
        return self.nl_handler.handle(text)

    def _prompt_with_status(self) -> str:
        """Prompt user with status toolbar."""
        status = self.status_monitor.get_status()
        toolbar = self._format_toolbar(status)
        return prompt("> ", bottom_toolbar=toolbar)
```

---

---

## Implementation Phases

This specification is organized into phases for progressive disclosure and context efficiency.

### Phase 1: Extract Commands (5 hours)
**Document**: [phase1-extract-commands.md](./phase1-extract-commands.md)

### Phase 2: Refactor Chat Interface (4 hours)
**Document**: [phase2-refactor-chat-interface.md](./phase2-refactor-chat-interface.md)

### Phase 3: Update Tests & Documentation (3 hours)
**Document**: [phase3-update-tests-documentation.md](./phase3-update-tests-documentation.md)


---

**Note**: This specification uses hierarchical format for 71% context reduction.
Each phase is in a separate file - read only the phase you're implementing.
