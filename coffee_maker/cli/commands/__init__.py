"""CLI command modules - Modularized commands for roadmap_cli.py.

SPEC-050: Refactor roadmap_cli.py Modularization

This package organizes the 17+ command functions from roadmap_cli.py into
focused, testable modules by command category.

Directory structure:
    commands/
    ├── __init__.py          # This file (exports all commands)
    ├── roadmap.py           # View commands (cmd_view, cmd_view_priority)
    ├── status.py            # Status commands (cmd_status, cmd_developer_status, etc.)
    ├── notifications.py     # Notification commands (cmd_notifications, cmd_respond)
    └── chat.py              # Chat commands (cmd_chat, cmd_assistant_*)

Module exports:
All command functions are imported here and re-exported for easy importing:
    from coffee_maker.cli.commands import roadmap, status, notifications, chat

Usage:
    # Import all modules
    from coffee_maker.cli.commands import roadmap, status, notifications, chat

    # Use in main CLI
    commands = {
        "view": roadmap.cmd_view,
        "status": status.cmd_status,
        # ... etc
    }

Migration Strategy (SPEC-050 Implementation Plan):
    Phase 1: Create package structure (this file + all submodules)
    Phase 2: Incrementally move command functions to submodules
    Phase 3: Update roadmap_cli.py to import from commands package
    Phase 4: Remove moved functions from roadmap_cli.py
    Phase 5: Test and validate all commands

Status: Phase 1 - Package structure created
Next: Phase 2 - Incrementally move commands

Reference:
    SPEC-050: docs/architecture/specs/SPEC-050-refactor-roadmap-cli-modularization.md
"""

# This file will be populated as commands are moved to submodules
# Placeholder for now - commands remain in roadmap_cli.py during migration

all_commands = []
