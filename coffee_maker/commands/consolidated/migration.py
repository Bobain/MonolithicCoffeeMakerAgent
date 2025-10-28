"""Migration helper for updating code from legacy to consolidated commands.

This module provides tools for finding and migrating legacy command usage
to the new consolidated command architecture.

Features:
- Find legacy command usage in code
- Generate migration suggestions
- Validate migration completeness
- Create automated migration scripts

Example:
    from coffee_maker.commands.consolidated.migration import CodeMigrator

    migrator = CodeMigrator()

    # Find legacy usage in a file
    findings = migrator.scan_file("coffee_maker/old_module.py")
    for cmd, line_no in findings:
        print(f"Line {line_no}: {cmd}")

    # Generate a migration report
    report = migrator.generate_migration_report("coffee_maker/")

    # Create a migration script
    script = migrator.create_migration_script(
        from_pattern="check_priority_status",
        to_pattern="roadmap(action='status')"
    )
"""

import os
import re
from typing import Dict, List, Optional, Tuple

if __name__ not in ("__main__", "__coffee_maker_test__"):
    from .compatibility import DeprecationRegistry
else:
    # When run as script or in tests, use absolute import
    from coffee_maker.commands.consolidated.compatibility import DeprecationRegistry


class CodeMigrator:
    """Tool for migrating code from legacy to consolidated commands."""

    def __init__(self):
        """Initialize the code migrator."""
        self.legacy_commands: Dict[str, Dict[str, str]] = {
            "PROJECT_MANAGER": DeprecationRegistry.PROJECT_MANAGER,
            "ARCHITECT": DeprecationRegistry.ARCHITECT,
            "CODE_DEVELOPER": DeprecationRegistry.CODE_DEVELOPER,
            "CODE_REVIEWER": DeprecationRegistry.CODE_REVIEWER,
            "ORCHESTRATOR": DeprecationRegistry.ORCHESTRATOR,
        }

        # Build reverse index: legacy_command -> (agent_type, mapping)
        self.legacy_index: Dict[str, Tuple[str, Dict[str, str]]] = {}
        for agent_type, commands in self.legacy_commands.items():
            for legacy_name, mapping in commands.items():
                self.legacy_index[legacy_name] = (agent_type, mapping)

    def scan_file(self, filepath: str) -> List[Tuple[str, int, str]]:
        """Scan a file for legacy command usage.

        Args:
            filepath: Path to the file to scan

        Returns:
            List of (command_name, line_number, line_content) tuples
        """
        findings = []

        if not os.path.exists(filepath):
            return findings

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_no, line in enumerate(lines, 1):
                # Skip comments and strings
                if line.strip().startswith("#"):
                    continue

                for legacy_cmd in self.legacy_index.keys():
                    # Look for method call pattern
                    pattern = rf"\b{re.escape(legacy_cmd)}\s*\("
                    if re.search(pattern, line):
                        findings.append((legacy_cmd, line_no, line.rstrip()))

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

        return findings

    def scan_directory(self, directory: str) -> Dict[str, List[Tuple[str, int, str]]]:
        """Scan a directory recursively for legacy command usage.

        Args:
            directory: Path to directory to scan

        Returns:
            Dictionary mapping filepaths to list of findings
        """
        findings_by_file: Dict[str, List[Tuple[str, int, str]]] = {}

        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    ".git",
                    "__pycache__",
                    ".pytest_cache",
                    "node_modules",
                    ".venv",
                    "venv",
                ]
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                filepath = os.path.join(root, file)
                findings = self.scan_file(filepath)

                if findings:
                    findings_by_file[filepath] = findings

        return findings_by_file

    def get_migration_suggestion(self, legacy_command: str) -> Optional[str]:
        """Get migration suggestion for a legacy command.

        Args:
            legacy_command: Name of the legacy command

        Returns:
            Migration suggestion string or None if not found
        """
        if legacy_command not in self.legacy_index:
            return None

        agent_type, mapping = self.legacy_index[legacy_command]
        new_command = mapping["command"]
        new_action = mapping["action"]

        return f"{new_command}(action='{new_action}', ...)"

    def generate_migration_report(self, directory: str) -> str:
        """Generate a migration report for a directory.

        Args:
            directory: Path to directory to scan

        Returns:
            Formatted migration report
        """
        findings = self.scan_directory(directory)

        if not findings:
            return f"No legacy command usage found in {directory}"

        report_lines = [
            "MIGRATION REPORT",
            "=" * 80,
            f"Directory: {directory}",
            f"Total files with legacy commands: {len(findings)}",
            "",
        ]

        total_occurrences = 0

        for filepath in sorted(findings.keys()):
            occurrences = findings[filepath]
            total_occurrences += len(occurrences)

            report_lines.append(f"File: {filepath}")
            report_lines.append("-" * 80)

            for cmd, line_no, line_content in occurrences:
                suggestion = self.get_migration_suggestion(cmd)
                report_lines.append(f"  Line {line_no}: {cmd}")
                report_lines.append(f"    Migrate to: {suggestion}")
                report_lines.append(f"    Code: {line_content}")
                report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append(f"Total legacy command occurrences: {total_occurrences}")

        return "\n".join(report_lines)

    def create_find_replace_rules(self) -> Dict[str, str]:
        """Create find/replace rules for migration.

        Returns:
            Dictionary mapping old patterns to suggested new patterns
        """
        rules = {}

        for legacy_cmd, (agent_type, mapping) in self.legacy_index.items():
            new_command = mapping["command"]
            new_action = mapping["action"]

            # Create a simple pattern that can be visually reviewed
            old_pattern = legacy_cmd
            new_pattern = f"{new_command}(action='{new_action}'"

            rules[old_pattern] = new_pattern

        return rules

    def validate_file_migrated(self, filepath: str) -> bool:
        """Check if a file has no legacy command usage.

        Args:
            filepath: Path to file to check

        Returns:
            True if no legacy commands found, False otherwise
        """
        findings = self.scan_file(filepath)
        return len(findings) == 0

    def generate_summary(self, directory: str) -> str:
        """Generate a summary of legacy usage.

        Args:
            directory: Path to directory to scan

        Returns:
            Summary string with statistics
        """
        findings = self.scan_directory(directory)

        # Count by command
        command_counts: Dict[str, int] = {}
        for filepath, occurrences in findings.items():
            for cmd, _, _ in occurrences:
                command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Count by agent type
        agent_counts: Dict[str, int] = {}
        for cmd, count in command_counts.items():
            if cmd in self.legacy_index:
                agent_type = self.legacy_index[cmd][0]
                agent_counts[agent_type] = agent_counts.get(agent_type, 0) + count

        # Generate summary
        summary_lines = [
            "MIGRATION SUMMARY",
            "=" * 80,
            f"Directory: {directory}",
            "",
            "By Command:",
        ]

        for cmd in sorted(command_counts.keys()):
            count = command_counts[cmd]
            summary_lines.append(f"  {cmd}: {count} occurrence(s)")

        summary_lines.append("")
        summary_lines.append("By Agent:")

        for agent_type in sorted(agent_counts.keys()):
            count = agent_counts[agent_type]
            summary_lines.append(f"  {agent_type}: {count} occurrence(s)")

        total = sum(command_counts.values())
        summary_lines.append("")
        summary_lines.append("=" * 80)
        summary_lines.append(f"Total legacy command occurrences: {total}")

        return "\n".join(summary_lines)


class MigrationValidator:
    """Validator for migration completeness."""

    def __init__(self):
        """Initialize the validator."""
        self.migrator = CodeMigrator()

    def validate_directory(self, directory: str) -> Tuple[bool, List[str]]:
        """Validate that a directory has no legacy commands.

        Args:
            directory: Path to directory to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        findings = self.migrator.scan_directory(directory)

        if not findings:
            return True, []

        errors = []

        for filepath, occurrences in findings.items():
            for cmd, line_no, _ in occurrences:
                suggestion = self.migrator.get_migration_suggestion(cmd)
                errors.append(f"{filepath}:{line_no} - Use {suggestion} " f"instead of {cmd}")

        return False, errors

    def validate_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate that a file has no legacy commands.

        Args:
            filepath: Path to file to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        findings = self.migrator.scan_file(filepath)

        if not findings:
            return True, []

        errors = []

        for cmd, line_no, _ in findings:
            suggestion = self.migrator.get_migration_suggestion(cmd)
            errors.append(f"Line {line_no} - Use {suggestion} instead of {cmd}")

        return False, errors


class MigrationScriptGenerator:
    """Generate migration scripts for automated updates."""

    def __init__(self):
        """Initialize the script generator."""
        self.migrator = CodeMigrator()

    def generate_shell_script(self, directory: str) -> str:
        """Generate a bash script to find/replace legacy commands.

        Args:
            directory: Path to directory to migrate

        Returns:
            Bash script content
        """
        rules = self.migrator.create_find_replace_rules()

        script_lines = [
            "#!/bin/bash",
            "# Migration script for updating legacy commands to consolidated format",
            f"# Generated for directory: {directory}",
            "",
            "set -e  # Exit on first error",
            "",
            "echo 'Starting legacy command migration...'",
            "",
        ]

        for old, new in sorted(rules.items()):
            # Use sed with find and replace
            script_lines.append(f"# Migrate {old} to {new}")
            script_lines.append(
                f"find {directory} -name '*.py' -exec sed -i '' " f"'s/{re.escape(old)}/{re.escape(new)}/g' {{}} \\;"
            )
            script_lines.append("")

        script_lines.extend(
            [
                "echo 'Migration complete!'",
                "echo 'Review changes and run tests to verify:'",
                "echo 'pytest'",
            ]
        )

        return "\n".join(script_lines)

    def generate_python_script(self, directory: str) -> str:
        """Generate a Python script to find and suggest migrations.

        Args:
            directory: Path to directory to check

        Returns:
            Python script content
        """
        script_lines = [
            '"""Auto-generated migration script for legacy commands."""',
            "",
            "import os",
            "from pathlib import Path",
            "",
            "from coffee_maker.commands.consolidated.migration import CodeMigrator",
            "",
            "def main():",
            f"    migrator = CodeMigrator()",
            f'    directory = "{directory}"',
            "    ",
            '    print("Scanning for legacy command usage...")',
            "    findings = migrator.scan_directory(directory)",
            "    ",
            "    if not findings:",
            '        print("No legacy commands found!")',
            "        return",
            "    ",
            '    print(f"Found {{len(findings)}} files with legacy commands:")',
            "    print()",
            "    ",
            "    for filepath, occurrences in sorted(findings.items()):",
            '        print(f"{{filepath}}:")',
            "        for cmd, line_no, line_content in occurrences:",
            "            suggestion = migrator.get_migration_suggestion(cmd)",
            '            print(f"  Line {{line_no}}: {{cmd}}")',
            '            print(f"    Migrate to: {{suggestion}}")',
            "            print()",
            "    ",
            '    print("Review suggestions above and update code manually.")',
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]

        return "\n".join(script_lines)


# Convenience functions
def find_legacy_commands(directory: str) -> Dict[str, List[Tuple[str, int, str]]]:
    """Find all legacy command usage in a directory.

    Args:
        directory: Path to directory to scan

    Returns:
        Dictionary mapping filepaths to findings
    """
    migrator = CodeMigrator()
    return migrator.scan_directory(directory)


def generate_migration_report(directory: str) -> str:
    """Generate a migration report for a directory.

    Args:
        directory: Path to directory

    Returns:
        Formatted migration report
    """
    migrator = CodeMigrator()
    return migrator.generate_migration_report(directory)


def validate_directory_migrated(directory: str) -> Tuple[bool, List[str]]:
    """Validate that a directory has no legacy commands.

    Args:
        directory: Path to directory

    Returns:
        Tuple of (is_valid, errors)
    """
    validator = MigrationValidator()
    return validator.validate_directory(directory)
