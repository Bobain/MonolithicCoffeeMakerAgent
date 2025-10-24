# GUIDELINE-002: CLI Command Creation Template

**Category**: Best Practice
**Applies To**: All new Poetry CLI commands
**Author**: architect agent
**Date**: 2025-10-17

---

## When to Use

Use this template when creating new Poetry CLI commands for the MonolithicCoffeeMakerAgent project.

**Examples**:
- `poetry run user-listener` - User interface command
- `poetry run project-manager` - Project management CLI
- `poetry run code-developer` - Autonomous daemon
- `poetry run dev-report` - Daily reports

---

## Template Overview

Creating a CLI command requires:
1. **CLI Module**: Python file with `main()` function
2. **Poetry Registration**: Entry in `pyproject.toml`
3. **Singleton Enforcement**: If agent owns files
4. **Rich Formatting**: Beautiful terminal output
5. **Help Text**: Clear usage instructions

**Time Estimate**: 1-2 hours with this template (vs 4-6 hours without)

---

## Step 1: Create CLI Module

**Location**: `coffee_maker/cli/my_command.py`

**Template Code**:

```python
"""My Command - Description of what this command does.

This module provides [brief description of functionality].

Usage:
    poetry run my-command

Examples:
    $ poetry run my-command
    [Expected output]

Author: code_developer
Date: YYYY-MM-DD
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType


def main() -> None:
    """Main entry point for my-command CLI.

    This function:
    1. Registers agent with singleton enforcement
    2. Initializes console for rich formatting
    3. Executes command logic
    4. Cleans up and exits

    Raises:
        AgentAlreadyRunningError: If another instance is running
        Exception: Any errors during execution
    """
    # Singleton enforcement (if agent owns files)
    with AgentRegistry.register(AgentType.MY_AGENT):
        console = Console()

        # Welcome banner
        banner = Panel(
            "[bold cyan]My Command[/bold cyan]\n"
            "[dim]Description of what this does[/dim]",
            title="Welcome",
            border_style="cyan"
        )
        console.print(banner)

        try:
            # Command logic here
            result = do_work()

            # Display results with rich formatting
            console.print("\n[green]✓[/green] Success!")
            console.print(Markdown(result))

        except Exception as e:
            console.print(f"\n[red]✗ Error:[/red] {e}")
            raise


def do_work() -> str:
    """Execute the main command logic.

    Returns:
        Markdown-formatted results

    Example:
        >>> result = do_work()
        >>> print(result)
        # Results
        - Item 1
        - Item 2
    """
    # Implementation here
    return "# Results\n\n- Example result"


if __name__ == "__main__":
    main()
```

---

## Step 2: Register in pyproject.toml

**Location**: `pyproject.toml`

**Add to `[tool.poetry.scripts]` section**:

```toml
[tool.poetry.scripts]
my-command = "coffee_maker.cli.my_command:main"
```

**Example**:

```toml
[tool.poetry.scripts]
project-manager = "coffee_maker.cli.roadmap_cli:main"
code-developer = "coffee_maker.autonomous.daemon:main"
user-listener = "coffee_maker.cli.user_listener:main"
dev-report = "coffee_maker.cli.daily_report_generator:main"  # ← Add yours here
```

---

## Step 3: Install and Test

**Install the command**:

```bash
poetry install
```

**Test basic execution**:

```bash
poetry run my-command
```

**Expected output**:

```
╭─ Welcome ────────────────────────────────────╮
│ My Command                                   │
│ Description of what this does                │
╰──────────────────────────────────────────────╯

✓ Success!

Results
═══════

• Example result
```

---

## Step 4: Singleton Enforcement (Optional)

**When to use**:
- If your agent **OWNS FILES** (can write to directories)
- Prevents file conflicts from concurrent writes

**When to skip**:
- If your agent is **READ-ONLY** or **DELEGATION-ONLY**
- Examples: assistant, user_listener, assistant (with code analysis skills)

**Ownership Check**:

| Agent | Owns Files? | Needs Singleton? |
|-------|-------------|------------------|
| code_developer | YES (.claude/, coffee_maker/, tests/) | YES |
| project_manager | YES (docs/roadmap/) | YES |
| architect | YES (docs/architecture/) | YES |
| assistant | NO (reads/delegates only) | NO |
| user_listener | NO (delegates only) | NO |
| assistant (with code analysis skills) | NO (reads only) | NO |

**Singleton Code**:

```python
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

def main():
    """Main entry point with singleton enforcement."""
    # If agent owns files: Use context manager for auto-cleanup
    with AgentRegistry.register(AgentType.MY_AGENT):
        # Your command logic here
        pass
    # Automatically unregistered on exit (even if exception)

# Alternative: Manual registration (not recommended)
def main_manual():
    """Manual singleton registration (use context manager instead)."""
    registry = AgentRegistry()
    try:
        registry.register_agent(AgentType.MY_AGENT)
        # Your command logic
    finally:
        registry.unregister_agent(AgentType.MY_AGENT)
```

**Error Handling**:

If singleton already running:

```python
from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError

try:
    with AgentRegistry.register(AgentType.MY_AGENT):
        # Command logic
except AgentAlreadyRunningError as e:
    console.print(f"[red]Error:[/red] {e}")
    console.print("[yellow]Tip:[/yellow] Stop existing instance first")
    sys.exit(1)
```

---

## Step 5: Rich Formatting

**Use Rich library** for beautiful terminal output:

### Welcome Banner

```python
from rich.panel import Panel

banner = Panel(
    "[bold cyan]My Command[/bold cyan]\n"
    "[dim]Brief description[/dim]",
    title="Welcome",
    border_style="cyan"
)
console.print(banner)
```

**Output**:

```
╭─ Welcome ────────────────────────╮
│ My Command                       │
│ Brief description                │
╰──────────────────────────────────╯
```

---

### Markdown Rendering

```python
from rich.markdown import Markdown

report = """
# Daily Report

## Summary
- Total commits: 5
- Files changed: 10

## Details
**PRIORITY 9**: Enhanced Communication
- Created DailyReportGenerator
- Added report formatting
"""

console.print(Markdown(report))
```

**Output**: Beautifully formatted markdown with headers, lists, bold, etc.

---

### Progress Indicators

```python
from rich.progress import track

for item in track(items, description="Processing..."):
    process(item)
```

---

### Tables

```python
from rich.table import Table

table = Table(title="Results")
table.add_column("Name", style="cyan")
table.add_column("Status", style="green")

table.add_row("Item 1", "✓ Complete")
table.add_row("Item 2", "✓ Complete")

console.print(table)
```

---

## Step 6: Help Text

**Add `--help` support**:

```python
import argparse

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="My Command - Description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  poetry run my-command
  poetry run my-command --option value

For more information, see docs/my-command.md
        """
    )

    parser.add_argument(
        "--option",
        help="Optional parameter description",
        default="default_value"
    )

    args = parser.parse_args()

    # Use args.option in command logic
```

**Usage**:

```bash
$ poetry run my-command --help
usage: my-command [-h] [--option OPTION]

My Command - Description

optional arguments:
  -h, --help       show this help message and exit
  --option OPTION  Optional parameter description

Examples:
  poetry run my-command
  poetry run my-command --option value
```

---

## Step 7: Testing

### Unit Tests

**File**: `tests/unit/test_my_command.py`

```python
"""Unit tests for my-command CLI."""

import pytest
from coffee_maker.cli.my_command import do_work


def test_do_work():
    """Test command logic."""
    result = do_work()
    assert result is not None
    assert "Results" in result


def test_singleton_enforcement():
    """Test singleton enforcement (if applicable)."""
    from coffee_maker.autonomous.agent_registry import (
        AgentAlreadyRunningError,
        AgentRegistry,
        AgentType,
    )

    # First instance
    with AgentRegistry.register(AgentType.MY_AGENT):
        # Try second instance - should fail
        with pytest.raises(AgentAlreadyRunningError):
            AgentRegistry().register_agent(AgentType.MY_AGENT)


def test_cleanup_on_exit():
    """Test cleanup after command exits."""
    from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

    # Register and exit
    with AgentRegistry.register(AgentType.MY_AGENT):
        pass  # Auto-cleanup

    # Should be able to register again
    with AgentRegistry.register(AgentType.MY_AGENT):
        pass  # Should succeed
```

---

### Integration Tests

**File**: `tests/ci_tests/test_my_command_integration.py`

```python
"""Integration tests for my-command CLI."""

import subprocess


def test_command_runs_successfully():
    """Test command executes without errors."""
    result = subprocess.run(
        ["poetry", "run", "my-command"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    assert "Success" in result.stdout


def test_command_help():
    """Test --help flag."""
    result = subprocess.run(
        ["poetry", "run", "my-command", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
```

---

### Manual Testing Checklist

- [ ] `poetry run my-command` executes successfully
- [ ] Welcome banner displays correctly
- [ ] Output formatted with rich (markdown, colors, etc.)
- [ ] Singleton enforcement works (if applicable)
- [ ] `--help` shows usage information
- [ ] Command exits cleanly (no hanging processes)
- [ ] Can run command again after exit

---

## Anti-Patterns to Avoid

### ❌ DON'T: Hardcode paths

```python
# BAD
config_file = "/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/data/config.json"
```

**Instead**: Use `Path` and relative paths

```python
# GOOD
from pathlib import Path

config_file = Path("data/config.json")
```

---

### ❌ DON'T: Print to stdout directly

```python
# BAD
print("Results:")
print(f"Total: {total}")
```

**Instead**: Use Rich console

```python
# GOOD
from rich.console import Console

console = Console()
console.print("[bold]Results:[/bold]")
console.print(f"Total: [cyan]{total}[/cyan]")
```

---

### ❌ DON'T: Ignore errors

```python
# BAD
def main():
    try:
        do_work()
    except Exception:
        pass  # Silent failure
```

**Instead**: Handle and report errors

```python
# GOOD
def main():
    try:
        do_work()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise  # Re-raise for debugging
```

---

### ❌ DON'T: Forget singleton cleanup

```python
# BAD
registry = AgentRegistry()
registry.register_agent(AgentType.MY_AGENT)
# Never unregisters - blocks future runs!
```

**Instead**: Use context manager

```python
# GOOD
with AgentRegistry.register(AgentType.MY_AGENT):
    # Automatically cleaned up on exit
    pass
```

---

## Complete Example

**File**: `coffee_maker/cli/spec_review.py`

```python
"""Spec Review Command - Generate technical spec coverage report.

This command shows which ROADMAP priorities have technical specifications,
helping architect identify gaps proactively.

Usage:
    poetry run spec-review

Example:
    $ poetry run spec-review
    ╭─ Spec Coverage Report ──────────────────╮
    │ Total Priorities: 12                    │
    │ Specs Exist: 8 (67%)                    │
    │ Specs Missing: 4 (33%)                  │
    ╰─────────────────────────────────────────╯

Author: code_developer
Date: 2025-10-17
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType


def main() -> None:
    """Main entry point for spec-review command."""
    # architect owns docs/architecture/, needs singleton
    with AgentRegistry.register(AgentType.ARCHITECT):
        console = Console()

        # Welcome banner
        banner = Panel(
            "[bold cyan]Spec Coverage Report[/bold cyan]\n"
            "[dim]Review technical spec coverage for ROADMAP priorities[/dim]",
            title="architect · Spec Review",
            border_style="cyan"
        )
        console.print(banner)

        try:
            # Generate report
            report = generate_report()

            # Display table
            console.print("\n")
            console.print(report)

            console.print("\n[green]✓[/green] Report generated successfully")

        except Exception as e:
            console.print(f"\n[red]✗ Error:[/red] {e}")
            raise


def generate_report() -> Table:
    """Generate spec coverage table.

    Returns:
        Rich Table with coverage details
    """
    table = Table(title="Spec Coverage")
    table.add_column("Priority", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Spec Status", style="yellow")
    table.add_column("Action", style="magenta")

    # Example data (real implementation would parse ROADMAP)
    table.add_row("PRIORITY 9", "Enhanced Communication", "✅ Exists", "N/A")
    table.add_row("PRIORITY 10", "user-listener UI", "✅ Exists", "N/A")
    table.add_row("US-047", "Architect-Only Specs", "✅ Exists", "N/A")
    table.add_row("US-048", "Silent Agents", "✅ Exists", "N/A")
    table.add_row("US-035", "Singleton Enforcement", "❌ Missing", "CREATE SPEC")

    return table


if __name__ == "__main__":
    main()
```

**Registration** (`pyproject.toml`):

```toml
[tool.poetry.scripts]
spec-review = "coffee_maker.cli.spec_review:main"
```

**Usage**:

```bash
$ poetry run spec-review

╭─ architect · Spec Review ───────────────────╮
│ Spec Coverage Report                        │
│ Review technical spec coverage for ROADMAP  │
╰─────────────────────────────────────────────╯

┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Priority   ┃ Title               ┃ Spec Status ┃ Action     ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ PRIORITY 9 │ Enhanced Comm...    │ ✅ Exists   │ N/A        │
│ PRIORITY10 │ user-listener UI    │ ✅ Exists   │ N/A        │
│ US-047     │ Architect-Only...   │ ✅ Exists   │ N/A        │
│ US-048     │ Silent Agents       │ ✅ Exists   │ N/A        │
│ US-035     │ Singleton Enfor...  │ ❌ Missing  │ CREATE ... │
└────────────┴─────────────────────┴─────────────┴────────────┘

✓ Report generated successfully
```

---

## Related Guidelines

- **GUIDELINE-001**: Spec Review Process
- **ADR-003**: Simplification-First Approach
- **CFR-001**: Document Ownership Boundaries

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created GUIDELINE-002 | architect |

---

**Remember**: This template saves 2-3 hours per CLI command by providing copy-paste examples and avoiding common pitfalls. Use it religiously!
