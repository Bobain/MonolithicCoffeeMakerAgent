# GUIDELINE-002: CLI Command Pattern

**Category**: Implementation Pattern
**Applies To**: Creating new CLI commands in coffee_maker
**Author**: architect agent
**Date**: 2025-10-16
**Status**: Active

---

## When to Use

Use this pattern when creating ANY new command-line interface command in the coffee_maker project.

**Examples**:
- `poetry run project-manager`
- `poetry run code-developer`
- `poetry run user-listener`
- `poetry run dev-report`

**NOT for**:
- Python library APIs (use different patterns)
- Internal functions (not user-facing)
- Daemon background processes (different pattern)

---

## Pattern Overview

All CLI commands in coffee_maker follow a consistent structure:

```
1. CLI Class (manages interface)
   ↓
2. Singleton Registration (prevents duplicates)
   ↓
3. Main Entry Point (handles errors)
   ↓
4. Poetry Script Registration (makes it runnable)
```

---

## Step-by-Step Implementation

### Step 1: Create CLI Class

**Location**: `coffee_maker/cli/<command_name>.py`

**Template**:

```python
"""
<Command Name> CLI - <One-line description>

Usage:
    poetry run <command-name>

Example:
    $ poetry run <command-name>
    <Example output>
"""

import logging
from pathlib import Path
from rich.console import Console

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType, AgentAlreadyRunningError

logger = logging.getLogger(__name__)


class <CommandName>CLI:
    """<Brief description of what this CLI does>

    This CLI provides <functionality description>.

    Attributes:
        console: Rich console for formatted output
        # Add other attributes as needed
    """

    def __init__(self):
        """Initialize <command name> CLI."""
        self.console = Console()
        # Initialize other components

    def start(self):
        """Start <command name> CLI.

        Registers as singleton and starts main loop.
        """
        # Register as singleton to prevent duplicate instances
        with AgentRegistry.register(AgentType.<YOUR_AGENT_TYPE>):
            self._display_welcome()
            self._run_main_loop()

    def _display_welcome(self):
        """Display welcome message."""
        self.console.print("\n[bold]<Command Name>[/] [dim]·[/] <Tagline>")
        self.console.print("[dim]<Brief description>[/]\n")

    def _run_main_loop(self):
        """Main loop for command execution."""
        # Implement your main logic here
        pass


def main():
    """Main entry point for <command-name> CLI.

    Command: poetry run <command-name>
    """
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    try:
        # Create and start CLI
        cli = <CommandName>CLI()
        cli.start()

    except AgentAlreadyRunningError as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/]\n")
        sys.exit(1)

    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[dim]Goodbye![/]\n")
        sys.exit(0)

    except Exception as e:
        console = Console()
        console.print(f"\n[red]Unexpected error: {e}[/]\n")
        logger.error(f"Fatal error in <command-name>", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### Step 2: Register Poetry Script

**Location**: `pyproject.toml`

**Add to `[tool.poetry.scripts]` section**:

```toml
[tool.poetry.scripts]
<command-name> = "coffee_maker.cli.<module_name>:main"
```

**Example**:
```toml
[tool.poetry.scripts]
project-manager = "coffee_maker.cli.roadmap_cli:main"
code-developer = "coffee_maker.autonomous.daemon_cli:main"
user-listener = "coffee_maker.cli.user_listener:main"
dev-report = "coffee_maker.cli.dev_report:main"
```

---

### Step 3: Register AgentType (if new agent)

**Location**: `coffee_maker/autonomous/agent_registry.py`

**Add to AgentType enum**:

```python
class AgentType(Enum):
    """Enum for different agent types in the system."""
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    USER_LISTENER = "user_listener"
    <YOUR_AGENT> = "<your_agent>"  # Add here
```

**Note**: Only needed if this is a NEW agent type. Reuse existing types if applicable.

---

### Step 4: Add Help Text and Usage Examples

**In Module Docstring**:

```python
"""
<Command Name> CLI - <Description>

Usage:
    poetry run <command-name> [OPTIONS]

Options:
    --help          Show this help message
    --option VALUE  Description of option

Examples:
    # Example 1: Basic usage
    $ poetry run <command-name>
    <Expected output>

    # Example 2: With option
    $ poetry run <command-name> --option value
    <Expected output>

See Also:
    - docs/<RELATED_DOCS>.md
    - Other related commands
"""
```

---

### Step 5: Add Rich Formatting

**Use Rich Console for beautiful output**:

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Example 1: Simple text with markup
console.print("[bold green]Success![/] Report generated.")

# Example 2: Tables
table = Table(title="Report Summary")
table.add_column("Metric", style="cyan")
table.add_column("Value", style="magenta")
table.add_row("Commits", "15")
table.add_row("Files Changed", "23")
console.print(table)

# Example 3: Panels
panel = Panel(
    "This is important information",
    title="[bold]Note[/]",
    border_style="blue"
)
console.print(panel)

# Example 4: Markdown rendering
markdown = Markdown("# Report\n\nThis is **bold** text.")
console.print(markdown)
```

---

### Step 6: Add Error Handling

**Handle all errors gracefully**:

```python
try:
    # Your main logic
    result = do_something()

except FileNotFoundError as e:
    console.print(f"[red]Error:[/] File not found: {e}")
    logger.error(f"File not found: {e}")
    sys.exit(1)

except ValueError as e:
    console.print(f"[red]Error:[/] Invalid value: {e}")
    logger.error(f"Invalid value: {e}")
    sys.exit(1)

except Exception as e:
    console.print(f"[red]Unexpected error:[/] {e}")
    logger.error(f"Unexpected error in command", exc_info=True)
    sys.exit(1)
```

**Error Exit Codes**:
- 0: Success
- 1: General error
- 2: Configuration error
- 130: Keyboard interrupt (Ctrl+C)

---

## Complete Example: dev-report Command

**File**: `coffee_maker/cli/dev_report.py`

```python
"""
Daily Developer Report CLI - Show code_developer's recent work

Usage:
    poetry run dev-report [--days N]

Options:
    --days N    Show report for last N days (default: 1)

Examples:
    # Show yesterday's work
    $ poetry run dev-report

    # Show last week's work
    $ poetry run dev-report --days 7

See Also:
    - SPEC-009: Enhanced Communication
    - `poetry run project-manager status` for current status
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType, AgentAlreadyRunningError
from coffee_maker.cli.daily_report_generator import DailyReportGenerator

logger = logging.getLogger(__name__)


class DevReportCLI:
    """Generate and display developer activity reports.

    This CLI generates markdown reports of code_developer's recent work
    by analyzing git commits, developer status, and notifications.

    Attributes:
        console: Rich console for formatted output
        report_generator: Generates reports from git/status data
    """

    def __init__(self, days: int = 1):
        """Initialize dev-report CLI.

        Args:
            days: Number of days to include in report (default: 1)
        """
        self.console = Console()
        self.days = days
        self.report_generator = DailyReportGenerator()

    def start(self):
        """Generate and display developer report.

        No singleton registration needed (not a long-running agent).
        """
        self._display_header()
        self._generate_and_display_report()

    def _display_header(self):
        """Display header with date range."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)

        self.console.print(
            f"\n[bold]Developer Report[/] [dim]·[/] "
            f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n"
        )

    def _generate_and_display_report(self):
        """Generate report and display with rich formatting."""
        try:
            # Generate markdown report
            since_date = datetime.now() - timedelta(days=self.days)
            report_markdown = self.report_generator.generate_report(since_date)

            # Display with rich markdown rendering
            markdown = Markdown(report_markdown)
            self.console.print(markdown)

        except FileNotFoundError as e:
            self.console.print(f"[red]Error:[/] {e}")
            self.console.print("[dim]Tip: Make sure you're in a git repository.[/]")
            logger.error(f"File not found: {e}")
            raise

        except Exception as e:
            self.console.print(f"[red]Error generating report:[/] {e}")
            logger.error(f"Report generation failed", exc_info=True)
            raise


def main():
    """Main entry point for dev-report CLI.

    Command: poetry run dev-report [--days N]
    """
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Show code_developer's recent work"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to include in report (default: 1)"
    )
    args = parser.parse_args()

    try:
        # Create and start CLI
        cli = DevReportCLI(days=args.days)
        cli.start()

    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[dim]Report cancelled.[/]\n")
        sys.exit(130)

    except Exception as e:
        console = Console()
        console.print(f"\n[red]Unexpected error: {e}[/]\n")
        logger.error(f"Fatal error in dev-report", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Poetry Registration** (`pyproject.toml`):
```toml
[tool.poetry.scripts]
dev-report = "coffee_maker.cli.dev_report:main"
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_<command_name>.py`

```python
import pytest
from coffee_maker.cli.<command_name> import <CommandName>CLI


def test_cli_initialization():
    """Test CLI initializes correctly."""
    cli = <CommandName>CLI()

    assert cli.console is not None
    # Add other assertions


def test_display_welcome():
    """Test welcome message displays."""
    cli = <CommandName>CLI()

    # Capture console output
    # Assert expected text appears


def test_error_handling():
    """Test CLI handles errors gracefully."""
    cli = <CommandName>CLI()

    # Trigger error condition
    # Assert error message displayed correctly
```

---

### Integration Tests

**File**: `tests/ci_tests/test_<command_name>_integration.py`

```python
import subprocess
import pytest


def test_command_runs_successfully():
    """Test command executes without errors."""
    result = subprocess.run(
        ["poetry", "run", "<command-name>"],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0


def test_help_flag():
    """Test --help flag works."""
    result = subprocess.run(
        ["poetry", "run", "<command-name>", "--help"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout
```

---

### Manual Testing

**Checklist**:

- [ ] Command runs: `poetry run <command-name>`
- [ ] Help text displays: `poetry run <command-name> --help`
- [ ] Singleton enforcement works (can't run twice)
- [ ] Ctrl+C exits gracefully
- [ ] Error messages are clear and actionable
- [ ] Rich formatting displays correctly
- [ ] Command shows in `poetry run --help`

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: No Singleton Enforcement

**Bad**:
```python
def main():
    cli = MyCLI()
    cli.start()  # No singleton check
```

**Why Bad**: Multiple instances can run simultaneously, causing conflicts.

**Good**:
```python
def main():
    cli = MyCLI()
    with AgentRegistry.register(AgentType.MY_AGENT):
        cli.start()  # Protected by singleton
```

---

### ❌ Anti-Pattern 2: No Error Handling

**Bad**:
```python
def main():
    cli = MyCLI()
    cli.start()  # Crashes on any error
```

**Why Bad**: Uncaught exceptions show ugly stack traces to users.

**Good**:
```python
def main():
    try:
        cli = MyCLI()
        cli.start()
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)
```

---

### ❌ Anti-Pattern 3: Plain Print Statements

**Bad**:
```python
print("Report generated successfully!")
print("Commits: 15")
print("Files: 23")
```

**Why Bad**: No formatting, ugly output, hard to read.

**Good**:
```python
console.print("[bold green]Report generated successfully![/]")
table = Table()
table.add_row("Commits", "15")
table.add_row("Files", "23")
console.print(table)
```

---

### ❌ Anti-Pattern 4: No Logging

**Bad**:
```python
def process():
    # Do work
    pass  # No logging
```

**Why Bad**: Can't debug issues, no audit trail.

**Good**:
```python
def process():
    logger.info("Starting process")
    # Do work
    logger.info("Process complete")
```

---

### ❌ Anti-Pattern 5: No Module Docstring

**Bad**:
```python
# No docstring

import sys

def main():
    pass
```

**Why Bad**: Users don't know how to use the command.

**Good**:
```python
"""
My Command CLI - Does something useful

Usage:
    poetry run my-command [OPTIONS]

Examples:
    $ poetry run my-command
    Success!
"""

import sys

def main():
    pass
```

---

## Common Pitfalls

### Pitfall 1: Forgetting Poetry Script Registration
**Symptom**: `poetry run <command>` not found
**Fix**: Add script to `pyproject.toml` and run `poetry install`

### Pitfall 2: Wrong Exit Code
**Symptom**: Shell scripts can't detect errors
**Fix**: Use `sys.exit(1)` for errors, `sys.exit(0)` for success

### Pitfall 3: Blocking Singleton Registration
**Symptom**: Command hangs, never starts
**Fix**: Ensure previous instance exited cleanly, check agent registry

### Pitfall 4: Missing Logging Setup
**Symptom**: No logs appear
**Fix**: Add `logging.basicConfig()` in `main()`

### Pitfall 5: Rich Markup Errors
**Symptom**: `[bold]` appears literally in output
**Fix**: Use `markup=True` in console.print() or use Markdown()

---

## Related Guidelines

- **GUIDELINE-001**: Error Handling (not yet created)
- **GUIDELINE-003**: Rich Console Formatting (not yet created)
- **US-035**: Singleton Agent Enforcement (implemented)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-16 | Created | architect |

---

## Approval

- [x] architect (author)
- [ ] code_developer (reviewer)
- [ ] project_manager (strategic alignment)

**Status**: Active
**Next Review**: 2025-11-16 (1 month)
