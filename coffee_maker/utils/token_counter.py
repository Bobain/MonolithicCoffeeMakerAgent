"""Token counting utilities for context budget validation.

This module provides accurate token counting using character-based estimation
and runtime validation with actual API token usage.

References:
    - Anthropic token estimation: ~4 chars per token
    - CFR-018: Command Execution Context Budget
    - Runtime validation doc: docs/RUNTIME_CONTEXT_VALIDATION.md
"""

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage breakdown for context validation."""

    command_tokens: int
    readme_tokens: int
    skills_tokens: int
    total_tokens: int
    budget_tokens: int
    usage_percent: float
    within_budget: bool

    def __str__(self) -> str:
        status = "✅" if self.within_budget else "❌"
        return (
            f"{status} {self.total_tokens:,} tokens ({self.usage_percent:.1f}% of {self.budget_tokens:,})\n"
            f"  Command: {self.command_tokens:,} | "
            f"README: {self.readme_tokens:,} | "
            f"Skills: {self.skills_tokens:,}"
        )


def estimate_tokens_from_text(text: str) -> int:
    """Estimate token count from text using word-based heuristic.

    Uses the rule of thumb: ~0.75 words per token (or ~1.33 tokens per word).
    This is more accurate than character-based counting for English text.

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated number of tokens

    Note:
        This is an approximation. For exact counts, use Anthropic's API
        token counting endpoint (when available).

    Examples:
        >>> estimate_tokens_from_text("Hello world")
        3  # 2 words * 1.33 ≈ 3 tokens

        >>> estimate_tokens_from_text("The quick brown fox jumps")
        7  # 5 words * 1.33 ≈ 7 tokens
    """
    # Count words (split on whitespace)
    words = text.split()
    word_count = len(words)

    # Rule of thumb: ~1.33 tokens per word (or ~0.75 words per token)
    # Rounded to nearest integer
    estimated_tokens = int(word_count * 1.33 + 0.5)

    return estimated_tokens


def estimate_tokens_from_file(file_path: Path) -> int:
    """Estimate token count from a file.

    Args:
        file_path: Path to the file

    Returns:
        Estimated number of tokens

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return estimate_tokens_from_text(text)


def validate_context_budget(
    command_text: str,
    agent_readme: str,
    auto_skills: str = "",
    max_tokens: int = 60_000,  # 30% of 200K context
) -> TokenUsage:
    """Validate that context fits within budget.

    Args:
        command_text: The command prompt text
        agent_readme: The agent README text
        auto_skills: Auto-loaded skills text (if any)
        max_tokens: Maximum allowed tokens (default: 60K = 30% of 200K)

    Returns:
        TokenUsage object with breakdown and validation result

    Example:
        >>> command = Path(".claude/commands/agents/architect/design.md").read_text()
        >>> readme = Path(".claude/commands/agents/architect/README.md").read_text()
        >>> usage = validate_context_budget(command, readme)
        >>> print(usage)
        ✅ 8,234 tokens (13.7% of 60,000)
          Command: 4,123 | README: 3,891 | Skills: 220
    """
    command_tokens = estimate_tokens_from_text(command_text)
    readme_tokens = estimate_tokens_from_text(agent_readme)
    skills_tokens = estimate_tokens_from_text(auto_skills)

    total = command_tokens + readme_tokens + skills_tokens
    usage_percent = (total / max_tokens) * 100
    within_budget = total <= max_tokens

    return TokenUsage(
        command_tokens=command_tokens,
        readme_tokens=readme_tokens,
        skills_tokens=skills_tokens,
        total_tokens=total,
        budget_tokens=max_tokens,
        usage_percent=usage_percent,
        within_budget=within_budget,
    )


def validate_command_file(
    agent_type: str,
    command_name: str,
    base_path: Path = Path(".claude/commands/agents"),
    max_tokens: int = 60_000,
) -> TokenUsage:
    """Validate a specific command file against budget.

    Args:
        agent_type: Agent type (e.g., "architect", "code_developer")
        command_name: Command name (e.g., "design", "implement")
        base_path: Base path to agent commands directory
        max_tokens: Maximum allowed tokens

    Returns:
        TokenUsage object with validation results

    Raises:
        FileNotFoundError: If command or README file not found

    Example:
        >>> usage = validate_command_file("architect", "design")
        >>> if not usage.within_budget:
        ...     print(f"❌ Over budget: {usage}")
    """
    agent_dir = base_path / agent_type

    # Load files
    readme_path = agent_dir / "README.md"
    command_path = agent_dir / f"{command_name}.md"

    if not readme_path.exists():
        raise FileNotFoundError(f"Agent README not found: {readme_path}")

    if not command_path.exists():
        raise FileNotFoundError(f"Command file not found: {command_path}")

    readme_text = readme_path.read_text(encoding="utf-8")
    command_text = command_path.read_text(encoding="utf-8")

    # Assume no skills for now (can be parameterized later)
    return validate_context_budget(command_text, readme_text, "", max_tokens)


def validate_all_commands(
    base_path: Path = Path(".claude/commands/agents"),
    max_tokens: int = 60_000,
) -> dict[str, dict[str, TokenUsage]]:
    """Validate all agent commands against budget.

    Args:
        base_path: Base path to agent commands directory
        max_tokens: Maximum allowed tokens

    Returns:
        Nested dict: {agent_type: {command_name: TokenUsage}}

    Example:
        >>> results = validate_all_commands()
        >>> for agent, commands in results.items():
        ...     for cmd, usage in commands.items():
        ...         if not usage.within_budget:
        ...             print(f"❌ {agent}.{cmd}: {usage}")
    """
    results = {}

    # Get all agent directories
    for agent_dir in sorted(base_path.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue

        agent_type = agent_dir.name
        results[agent_type] = {}

        # Get all command files (exclude README)
        for command_file in sorted(agent_dir.glob("*.md")):
            if command_file.name == "README.md":
                continue

            command_name = command_file.stem

            try:
                usage = validate_command_file(agent_type, command_name, base_path, max_tokens)
                results[agent_type][command_name] = usage
            except Exception as e:
                logger.error(f"Error validating {agent_type}.{command_name}: {e}")

    return results


def generate_budget_report(
    results: dict[str, dict[str, TokenUsage]],
    show_compliant: bool = True,
    show_violations: bool = True,
) -> str:
    """Generate human-readable budget validation report.

    Args:
        results: Results from validate_all_commands()
        show_compliant: Include compliant commands in report
        show_violations: Include budget violations in report

    Returns:
        Formatted report string

    Example:
        >>> results = validate_all_commands()
        >>> report = generate_budget_report(results, show_violations=True)
        >>> print(report)
    """
    lines = ["# CFR-018 Context Budget Validation Report", ""]

    # Summary stats
    total_commands = sum(len(cmds) for cmds in results.values())
    violations = sum(1 for cmds in results.values() for usage in cmds.values() if not usage.within_budget)
    compliant = total_commands - violations

    lines.extend(
        [
            "## Summary",
            "",
            f"- **Total Commands**: {total_commands}",
            f"- **Compliant**: {compliant} ({compliant/total_commands*100:.1f}%)",
            f"- **Violations**: {violations} ({violations/total_commands*100 if total_commands > 0 else 0:.1f}%)",
            "",
        ]
    )

    # Per-agent breakdown
    lines.extend(["## Per-Agent Breakdown", ""])

    for agent_type, commands in sorted(results.items()):
        lines.append(f"### {agent_type.replace('_', ' ').title()}")
        lines.append("")

        avg_usage = sum(u.usage_percent for u in commands.values()) / len(commands) if commands else 0
        lines.append(f"**Average Usage**: {avg_usage:.1f}%")
        lines.append("")
        lines.append("| Command | Tokens | Usage % | Status |")
        lines.append("|---------|--------|---------|--------|")

        for command_name, usage in sorted(commands.items()):
            # Filter based on show_* flags
            if not usage.within_budget and not show_violations:
                continue
            if usage.within_budget and not show_compliant:
                continue

            status = "✅" if usage.within_budget else "❌"
            lines.append(f"| {command_name} | {usage.total_tokens:,} | {usage.usage_percent:.1f}% | {status} |")

        lines.append("")

    # Violations detail (if any)
    if violations > 0 and show_violations:
        lines.extend(["## ❌ Budget Violations (Detailed)", ""])

        for agent_type, commands in sorted(results.items()):
            for command_name, usage in sorted(commands.items()):
                if not usage.within_budget:
                    lines.extend(
                        [
                            f"### {agent_type}.{command_name}",
                            "",
                            f"```",
                            f"{usage}",
                            f"```",
                            "",
                            "**Recommendation**: Compress command or agent README to fit budget.",
                            "",
                        ]
                    )

    return "\n".join(lines)


if __name__ == "__main__":
    """Quick validation script for all commands."""
    import sys

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    base_path = project_root / ".claude" / "commands" / "agents"

    logger.info(f"Validating commands in: {base_path}\n")

    # Validate all commands
    results = validate_all_commands(base_path)

    # Generate report
    report = generate_budget_report(results, show_compliant=True, show_violations=True)
    print(report)

    # Exit with error code if violations
    total_violations = sum(1 for cmds in results.values() for usage in cmds.values() if not usage.within_budget)

    if total_violations > 0:
        logger.error(f"\n❌ Found {total_violations} budget violations!")
        sys.exit(1)
    else:
        logger.info("\n✅ All commands within budget!")
        sys.exit(0)
