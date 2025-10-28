"""Backward Compatibility Layer for Consolidated Commands.

This module provides deprecation wrappers and parameter transformations
for legacy commands that have been consolidated into the new action-based
command architecture.

Features:
- Automatic parameter transformation from old to new format
- Deprecation warnings with helpful migration guidance
- Usage tracking for monitoring migration progress
- Graceful fallback behavior

Example:
    # Old usage (deprecated):
    pm.check_priority_status("PRIORITY-28")

    # New usage (recommended):
    pm.roadmap(action="status", priority_id="PRIORITY-28")

    # The compatibility layer allows the old usage to work while warning:
    # DeprecationWarning: 'check_priority_status' is deprecated, use
    # 'roadmap(action='status')' instead.
"""

import logging
import warnings
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Tracks deprecation warnings shown (once per session per command)
_deprecation_warnings_shown = set()


class DeprecationRegistry:
    """Registry mapping old command names to new commands and actions."""

    # Project Manager mappings
    PROJECT_MANAGER = {
        # roadmap commands
        "check_priority_status": {"command": "roadmap", "action": "status"},
        "get_priority_details": {"command": "roadmap", "action": "details"},
        "list_all_priorities": {"command": "roadmap", "action": "list"},
        "update_priority_metadata": {"command": "roadmap", "action": "update"},
        # status commands
        "developer_status": {"command": "status", "action": "developer"},
        "notifications": {"command": "status", "action": "notifications"},
        # dependency commands
        "check_dependency": {"command": "dependencies", "action": "check"},
        "add_dependency": {"command": "dependencies", "action": "add"},
        # github commands
        "monitor_github_pr": {"command": "github", "action": "monitor_pr"},
        "track_github_issue": {"command": "github", "action": "track_issue"},
        "sync_github_status": {"command": "github", "action": "sync"},
        # stats commands
        "roadmap_stats": {"command": "stats", "action": "roadmap"},
        "feature_stats": {"command": "stats", "action": "feature"},
        "spec_stats": {"command": "stats", "action": "spec"},
        "audit_trail": {"command": "stats", "action": "audit"},
    }

    # Architect mappings
    ARCHITECT = {
        # spec commands
        "create_technical_spec": {"command": "spec", "action": "create"},
        "update_technical_spec": {"command": "spec", "action": "update"},
        "approve_spec": {"command": "spec", "action": "approve"},
        "deprecate_spec": {"command": "spec", "action": "deprecate"},
        "link_spec_to_priority": {"command": "spec", "action": "link"},
        # task commands
        "decompose_spec_to_tasks": {"command": "tasks", "action": "decompose"},
        "update_task_order": {"command": "tasks", "action": "update_order"},
        "merge_task_branches": {"command": "tasks", "action": "merge_branch"},
        # documentation commands
        "create_adr": {"command": "documentation", "action": "create_adr"},
        "update_guidelines": {"command": "documentation", "action": "update_guidelines"},
        "update_styleguide": {"command": "documentation", "action": "update_styleguide"},
        # review commands
        "validate_architecture": {"command": "review", "action": "validate_architecture"},
        "design_api": {"command": "review", "action": "design_api"},
        # dependency commands
        "check_dependency": {"command": "dependencies", "action": "check"},
        "add_dependency": {"command": "dependencies", "action": "add"},
        "evaluate_dependency": {"command": "dependencies", "action": "evaluate"},
    }

    # Code Developer mappings
    CODE_DEVELOPER = {
        # implement commands
        "claim_priority": {"command": "implement", "action": "claim"},
        "load_spec": {"command": "implement", "action": "load"},
        "update_implementation_status": {
            "command": "implement",
            "action": "update_status",
        },
        "record_commit": {"command": "implement", "action": "record_commit"},
        "complete_implementation": {"command": "implement", "action": "complete"},
        # test commands
        "run_tests": {"command": "test", "action": "run"},
        "fix_test_failures": {"command": "test", "action": "fix"},
        "generate_coverage_report": {"command": "test", "action": "coverage"},
        # git commands
        "git_commit": {"command": "git", "action": "commit"},
        "create_pull_request": {"command": "git", "action": "create_pr"},
        # review commands
        "request_code_review": {"command": "review", "action": "request"},
        "track_review_status": {"command": "review", "action": "track"},
        # quality commands
        "run_pre_commit_hooks": {"command": "quality", "action": "pre_commit"},
        "generate_quality_metrics": {"command": "quality", "action": "metrics"},
        "lint_code": {"command": "quality", "action": "lint"},
        # config commands
        "update_claude_config": {"command": "config", "action": "update_claude"},
        "update_project_config": {"command": "config", "action": "update_config"},
    }

    # Code Reviewer mappings
    CODE_REVIEWER = {
        # review commands
        "generate_review_report": {"command": "review", "action": "generate_report"},
        "score_code_quality": {"command": "review", "action": "score"},
        "validate_definition_of_done": {"command": "review", "action": "validate_dod"},
        # analyze commands
        "check_style_compliance": {"command": "analyze", "action": "check_style_compliance"},
        "run_security_scan": {"command": "analyze", "action": "run_security_scan"},
        "analyze_complexity": {"command": "analyze", "action": "analyze_complexity"},
        "check_test_coverage": {"command": "analyze", "action": "check_test_coverage"},
        "validate_type_hints": {"command": "analyze", "action": "validate_type_hints"},
        "validate_architecture": {"command": "analyze", "action": "validate_architecture"},
        "validate_documentation": {
            "command": "analyze",
            "action": "validate_documentation",
        },
        # monitor commands
        "detect_new_commits": {"command": "monitor", "action": "detect_commits"},
        "track_issue_resolution": {"command": "monitor", "action": "track_issues"},
        # notify commands
        "notify_architect": {"command": "notify", "action": "architect"},
        "notify_code_developer": {"command": "notify", "action": "code_developer"},
    }

    # Orchestrator mappings
    ORCHESTRATOR = {
        # agent commands
        "spawn_agent_session": {"command": "agents", "action": "spawn"},
        "kill_stalled_agent": {"command": "agents", "action": "kill"},
        "restart_agent": {"command": "agents", "action": "restart"},
        "monitor_agent_lifecycle": {"command": "agents", "action": "monitor_lifecycle"},
        "handle_agent_errors": {"command": "agents", "action": "handle_errors"},
        # message commands
        "route_inter_agent_messages": {"command": "messages", "action": "route_inter_agent_messages"},
        "send_message": {"command": "messages", "action": "send_message"},
        "receive_message": {"command": "messages", "action": "receive_message"},
        # orchestrate commands
        "coordinate_dependencies": {"command": "orchestrate", "action": "coordinate_dependencies"},
        "find_available_work": {"command": "orchestrate", "action": "find_available_work"},
        "create_parallel_tasks": {"command": "orchestrate", "action": "create_parallel_tasks"},
        "detect_deadlocks": {"command": "orchestrate", "action": "detect_deadlocks"},
        # worktree commands
        "create_worktree": {"command": "worktree", "action": "create_worktree"},
        "cleanup_worktrees": {"command": "worktree", "action": "cleanup_worktrees"},
        "merge_completed_work": {"command": "worktree", "action": "merge_completed_work"},
        # monitor commands
        "monitor_resource_usage": {"command": "monitor", "action": "monitor_resource_usage"},
        "generate_activity_summary": {"command": "monitor", "action": "generate_activity_summary"},
    }

    @classmethod
    def get_mapping(cls, agent_type: str, legacy_command: str) -> Optional[Dict[str, str]]:
        """Get mapping for a legacy command.

        Args:
            agent_type: Type of agent (PROJECT_MANAGER, ARCHITECT, etc.)
            legacy_command: Name of the legacy command

        Returns:
            Dictionary with 'command' and 'action' keys, or None if not found
        """
        registry = getattr(cls, agent_type, {})
        return registry.get(legacy_command)

    @classmethod
    def get_agent_registry(cls, agent_type: str) -> Dict[str, Dict[str, str]]:
        """Get all mappings for an agent type.

        Args:
            agent_type: Type of agent (PROJECT_MANAGER, ARCHITECT, etc.)

        Returns:
            Dictionary of all legacy command mappings for the agent
        """
        return getattr(cls, agent_type, {}).copy()


def create_deprecation_wrapper(old_name: str, new_command: str, new_action: str, handler: Callable) -> Callable:
    """Create a deprecation wrapper that forwards to the new command.

    Args:
        old_name: Name of the deprecated command
        new_command: Name of the new consolidated command
        new_action: Action to use in the new command
        handler: The actual handler function to call

    Returns:
        A wrapper function that issues deprecation warning and calls handler
    """

    def wrapper(*args, **kwargs):
        # Issue deprecation warning (once per session)
        if old_name not in _deprecation_warnings_shown:
            warnings.warn(
                f"'{old_name}' is deprecated, use " f"'{new_command}(action='{new_action}')' instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            _deprecation_warnings_shown.add(old_name)

        # Log the usage
        logger.warning(f"Deprecated command called: {old_name} -> " f"{new_command}(action='{new_action}')")

        # Call the actual handler with action parameter
        return handler(*args, action=new_action, **kwargs)

    return wrapper


def transform_parameters(old_params: Dict[str, Any], param_mapping: Dict[str, str]) -> Dict[str, Any]:
    """Transform old parameter names to new format.

    Args:
        old_params: Dictionary of old parameter names and values
        param_mapping: Dictionary mapping old parameter names to new ones

    Returns:
        Dictionary with new parameter names
    """
    new_params = {}

    for old_name, value in old_params.items():
        new_name = param_mapping.get(old_name, old_name)
        new_params[new_name] = value

    return new_params


class CompatibilityMixin:
    """Mixin for adding backward compatibility to command classes.

    This mixin should be added to command classes to provide automatic
    generation of legacy command aliases with deprecation warnings.

    Example:
        class ProjectManagerCommands(ConsolidatedCommand, CompatibilityMixin):
            def __init__(self):
                super().__init__()
                self._setup_legacy_aliases()
    """

    def _setup_legacy_aliases(self, registry_type: str) -> None:
        """Setup legacy command aliases for this agent.

        Args:
            registry_type: The registry type to use (PROJECT_MANAGER, ARCHITECT, etc.)
        """
        registry = DeprecationRegistry.get_agent_registry(registry_type)

        for legacy_name, mapping in registry.items():
            command_name = mapping["command"]
            action_name = mapping["action"]

            # Get the actual command method
            if not hasattr(self, command_name):
                logger.warning(f"Command method '{command_name}' not found for " f"legacy alias '{legacy_name}'")
                continue

            command_method = getattr(self, command_name)

            # Create the wrapper
            wrapper = create_deprecation_wrapper(legacy_name, command_name, action_name, command_method)

            # Assign the wrapper as a method
            setattr(self, legacy_name, wrapper)


class MigrationHelper:
    """Helper for migrating code from legacy to consolidated commands."""

    @staticmethod
    def get_migration_pattern(agent_type: str, legacy_command: str) -> Optional[str]:
        """Get migration pattern for a legacy command.

        Args:
            agent_type: Type of agent
            legacy_command: Name of legacy command

        Returns:
            String showing how to migrate the command
        """
        mapping = DeprecationRegistry.get_mapping(agent_type, legacy_command)

        if not mapping:
            return None

        return f"{legacy_command}(...) -> " f"{mapping['command']}(action='{mapping['action']}', ...)"

    @staticmethod
    def get_all_legacy_commands(agent_type: str) -> list[str]:
        """Get list of all legacy commands for an agent.

        Args:
            agent_type: Type of agent

        Returns:
            List of legacy command names
        """
        registry = DeprecationRegistry.get_agent_registry(agent_type)
        return sorted(registry.keys())

    @staticmethod
    def generate_migration_report() -> str:
        """Generate a report of all legacy commands and their replacements.

        Returns:
            Formatted string with migration information
        """
        report_lines = [
            "LEGACY COMMAND MIGRATION REPORT",
            "=" * 80,
        ]

        agent_types = [
            "PROJECT_MANAGER",
            "ARCHITECT",
            "CODE_DEVELOPER",
            "CODE_REVIEWER",
            "ORCHESTRATOR",
        ]

        total_legacy = 0

        for agent_type in agent_types:
            registry = DeprecationRegistry.get_agent_registry(agent_type)

            if not registry:
                continue

            report_lines.append("")
            report_lines.append(f"{agent_type}")
            report_lines.append("-" * 80)

            for legacy_name in sorted(registry.keys()):
                mapping = registry[legacy_name]
                pattern = f"{legacy_name}(...) -> " f"{mapping['command']}(action='{mapping['action']}', ...)"
                report_lines.append(f"  {pattern}")
                total_legacy += 1

        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append(f"Total legacy commands: {total_legacy}")

        return "\n".join(report_lines)

    @staticmethod
    def find_legacy_usage(code: str) -> list[tuple[str, int]]:
        """Find potential legacy command usage in code.

        Args:
            code: Python code to search

        Returns:
            List of (command_name, line_number) tuples
        """
        import re

        all_legacy_commands = set()

        # Get all agent registries
        for agent_type in [
            "PROJECT_MANAGER",
            "ARCHITECT",
            "CODE_DEVELOPER",
            "CODE_REVIEWER",
            "ORCHESTRATOR",
        ]:
            registry = DeprecationRegistry.get_agent_registry(agent_type)
            all_legacy_commands.update(registry.keys())

        # Find usage patterns
        findings = []
        for line_no, line in enumerate(code.split("\n"), 1):
            for cmd in all_legacy_commands:
                # Look for method call pattern: cmd(
                pattern = rf"\b{re.escape(cmd)}\s*\("
                if re.search(pattern, line):
                    findings.append((cmd, line_no))

        return findings

    @staticmethod
    def create_find_replace_rules() -> Dict[str, str]:
        """Create find/replace rules for code migration.

        Returns:
            Dictionary mapping old patterns to new patterns
        """
        rules = {}

        agent_types = [
            "PROJECT_MANAGER",
            "ARCHITECT",
            "CODE_DEVELOPER",
            "CODE_REVIEWER",
            "ORCHESTRATOR",
        ]

        for agent_type in agent_types:
            registry = DeprecationRegistry.get_agent_registry(agent_type)

            for legacy_name, mapping in registry.items():
                # Create a simple replacement suggestion
                # Full migration would need parameter analysis
                old_pattern = f"{legacy_name}("
                new_pattern = f"{mapping['command']}(action='{mapping['action']}',"
                rules[old_pattern] = new_pattern

        return rules


# Deprecation tracking decorator
def deprecated_command(old_name: str, new_command: str, new_action: str):
    """Decorator to mark a command method as deprecated.

    Args:
        old_name: Name of the deprecated command
        new_command: Name of the new consolidated command
        new_action: Action to use in the new command

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Issue deprecation warning
            if old_name not in _deprecation_warnings_shown:
                warnings.warn(
                    f"'{old_name}' is deprecated, use " f"'{new_command}(action='{new_action}')' instead.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                _deprecation_warnings_shown.add(old_name)

            # Log usage
            logger.warning(f"Deprecated command called: {old_name} -> " f"{new_command}(action='{new_action}')")

            # Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
