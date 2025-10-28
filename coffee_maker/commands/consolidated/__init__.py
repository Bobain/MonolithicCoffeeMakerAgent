"""Consolidated command architecture for MonolithicCoffeeMakerAgent.

This module provides unified command interfaces for all agents, reducing
cognitive load by consolidating related commands into logical groups.

Architecture:
- Each agent has 3-6 consolidated commands instead of 5-15 individual commands
- Each command uses action-based routing (parameter-driven pattern)
- Backward compatibility with legacy commands via deprecation wrappers
- Comprehensive error handling and validation

Backward Compatibility (Phase 2):
- All 79 legacy commands automatically aliased to new consolidated commands
- Deprecation warnings guide users to new command format
- Migration helper tools for automated code updates

Example - Old style (deprecated, but still works):
    pm.check_priority_status("PRIORITY-28")
    pm.get_priority_details("PRIORITY-28")
    pm.list_all_priorities(status="blocked")

Example - New style (recommended):
    pm.roadmap(action="status", priority_id="PRIORITY-28")
    pm.roadmap(action="details", priority_id="PRIORITY-28")
    pm.roadmap(action="list", status="blocked")

Migration Tools:
    from coffee_maker.commands.consolidated.migration import (
        CodeMigrator,
        find_legacy_commands,
        generate_migration_report,
    )

    # Find legacy commands in a directory
    findings = find_legacy_commands("coffee_maker/")

    # Generate migration report
    report = generate_migration_report("coffee_maker/")
"""

from .base_command import ConsolidatedCommand
from .project_manager_commands import ProjectManagerCommands
from .architect_commands import ArchitectCommands
from .code_developer_commands import CodeDeveloperCommands
from .code_reviewer_commands import CodeReviewerCommands
from .orchestrator_commands import OrchestratorCommands
from .assistant_commands import AssistantCommands
from .user_listener_commands import UserListenerCommands
from .ux_design_expert_commands import UXDesignExpertCommands
from .compatibility import (
    DeprecationRegistry,
    CompatibilityMixin,
    MigrationHelper,
    create_deprecation_wrapper,
)
from .migration import (
    CodeMigrator,
    MigrationValidator,
    MigrationScriptGenerator,
    find_legacy_commands,
    generate_migration_report,
    validate_directory_migrated,
)

__all__ = [
    # Consolidated command classes
    "ConsolidatedCommand",
    "ProjectManagerCommands",
    "ArchitectCommands",
    "CodeDeveloperCommands",
    "CodeReviewerCommands",
    "OrchestratorCommands",
    "AssistantCommands",
    "UserListenerCommands",
    "UXDesignExpertCommands",
    # Backward compatibility utilities
    "DeprecationRegistry",
    "CompatibilityMixin",
    "MigrationHelper",
    "create_deprecation_wrapper",
    # Migration tools
    "CodeMigrator",
    "MigrationValidator",
    "MigrationScriptGenerator",
    "find_legacy_commands",
    "generate_migration_report",
    "validate_directory_migrated",
]

__version__ = "2.0.0"
