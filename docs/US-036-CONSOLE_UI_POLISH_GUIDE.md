# US-036: Console UI Polish Implementation Guide

**Status**: 📝 PLANNED → Ready for Implementation
**Type**: User Experience / Polish
**Complexity**: Medium
**Estimated Effort**: 2-3 days (12-16 hours)
**Created**: 2025-10-16
**Documentation Created**: 2025-10-20

---

## Table of Contents

1. [Overview](#overview)
2. [Current State Analysis](#current-state-analysis)
3. [Implementation Phases](#implementation-phases)
4. [Technical Architecture](#technical-architecture)
5. [Code Examples](#code-examples)
6. [Testing Strategy](#testing-strategy)
7. [Success Criteria](#success-criteria)
8. [References](#references)

---

## Overview

### Goal

Enhance the project-manager console UI to match the professional quality and smooth user experience of claude-cli. Transform the basic functional UI into a polished, production-ready interface with streaming responses, rich formatting, keyboard shortcuts, and intuitive visual feedback.

### User Story

> "As a project manager user, I want project-manager chat to have polished console UI matching claude-cli quality, so that the user experience is professional, intuitive, and delightful."

### Business Value

- **User Satisfaction**: Professional UI increases confidence (target: >8/10 user rating)
- **Productivity**: Smooth UX reduces friction and makes users more productive
- **Adoption**: Polish encourages wider team adoption
- **Professional Image**: Production-quality UI reflects well on entire project

---

## Current State Analysis

### Existing Infrastructure

**Already Available** ✅:
- `coffee_maker/cli/console_ui.py` - Basic rich console utilities
- `prompt-toolkit` - Already in dependencies (pyproject.toml:23)
- `rich` library integration - Color scheme, panels, tables defined
- Basic formatting functions: success(), error(), warning(), info()

**Existing Code Structure**:
```python
# coffee_maker/cli/console_ui.py (current implementation)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

COLORS = {
    "info": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim white",
    "highlight": "cyan",
    "accent": "magenta",
}

SYMBOLS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "working": "⚙",
    "thinking": "🧠",
    "idle": "💤",
}
```

### What's Missing

**Need to Add** ⏳:
1. **Streaming Responses**: Character-by-character output like claude-cli
2. **Advanced Input**: Command history, autocomplete, multi-line support
3. **Keyboard Shortcuts**: Ctrl+C/D/L, navigation, search
4. **Enhanced Progress**: Spinners, progress bars with descriptive text
5. **Welcome Screen**: Professional project info display
6. **Theme Support**: Light/dark theme adaptation
7. **Terminal Resize Handling**: Graceful response to window changes

---

## Implementation Phases

### Phase 1: Rich Library Enhancement (4 hours)

**Objective**: Expand console_ui.py with streaming and enhanced formatting

**Tasks**:
- [ ] Add streaming response function
- [ ] Create professional welcome screen
- [ ] Enhance progress indicators with spinners
- [ ] Add syntax highlighting for code blocks
- [ ] Implement theme detection (light/dark)

**Key Files**:
- `coffee_maker/cli/console_ui.py` (extend existing)
- `coffee_maker/cli/ui_config.py` (NEW - theme configuration)

**Code to Add**:
```python
# In console_ui.py - Streaming response
from rich.live import Live
from rich.markdown import Markdown

def stream_response(text_generator, markdown: bool = True):
    """Stream response character-by-character like claude-cli.

    Args:
        text_generator: Generator yielding text chunks
        markdown: Whether to render as markdown (default: True)
    """
    buffer = ""

    with Live(console=console, auto_refresh=False) as live:
        for chunk in text_generator:
            buffer += chunk

            # Update display smoothly
            if markdown:
                live.update(Markdown(buffer))
            else:
                live.update(buffer)

            live.refresh()

    console.print()  # Final newline

# Welcome screen
def print_welcome():
    """Display professional welcome screen with project info."""
    from coffee_maker import __version__

    welcome_text = f"""
# Project Manager - AI Assistant 🤖

**Version**: {__version__}
**Mode**: Interactive Chat
**Model**: Claude Sonnet 4.5

## Quick Commands
- `/roadmap` - View project roadmap
- `/status` - Check daemon status
- `/notifications` - View pending notifications
- `/help` - Show all commands
- `Ctrl+D` or `exit` - Exit chat

Ready to help! Ask me anything about the project.
    """

    panel = Panel(
        Markdown(welcome_text.strip()),
        title="[bold cyan]Welcome[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )

    console.print(panel)
    console.print()
```

---

### Phase 2: Advanced Input with prompt_toolkit (4 hours)

**Objective**: Implement command history, autocomplete, and keyboard shortcuts

**Tasks**:
- [ ] Set up PromptSession with file-based history
- [ ] Implement command autocomplete (TAB completion)
- [ ] Add keyboard shortcuts (Ctrl+C, Ctrl+D, Ctrl+L, Ctrl+R)
- [ ] Enable multi-line input support
- [ ] Implement history navigation (up/down arrows)

**Key Files**:
- `coffee_maker/cli/advanced_input.py` (NEW)
- `.project_manager_history` (git-ignored history file)
- `.gitignore` (add history file)

**Code to Create**:
```python
# coffee_maker/cli/advanced_input.py (NEW FILE)

"""Advanced input handling with prompt_toolkit.

US-036: Console UI Polish - Phase 2

Features:
    - Command history (file-based persistence)
    - TAB autocomplete for commands
    - Keyboard shortcuts (Ctrl+C/D/L/R)
    - Multi-line input support
    - History search (Ctrl+R)
"""

from pathlib import Path
from typing import List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from coffee_maker.cli.console_ui import console, info


class ProjectManagerCompleter(Completer):
    """Smart autocomplete for project-manager commands."""

    COMMANDS = [
        '/roadmap', '/status', '/notifications', '/verify-dod',
        '/github-status', '/help', '/exit', '/clear', '/history'
    ]

    def get_completions(self, document, complete_event):
        """Generate completions for current input."""
        word = document.get_word_before_cursor()

        # Command completion
        if word.startswith('/'):
            for cmd in self.COMMANDS:
                if cmd.startswith(word):
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display_meta=self._get_command_help(cmd)
                    )

    def _get_command_help(self, cmd: str) -> str:
        """Get help text for command."""
        help_map = {
            '/roadmap': 'View project roadmap',
            '/status': 'Check daemon status',
            '/notifications': 'View notifications',
            '/verify-dod': 'Verify Definition of Done',
            '/github-status': 'Check GitHub status',
            '/help': 'Show all commands',
            '/exit': 'Exit chat',
            '/clear': 'Clear screen',
            '/history': 'Show command history',
        }
        return help_map.get(cmd, '')


def create_input_session(history_file: str = '.project_manager_history') -> PromptSession:
    """Create configured prompt session with all features.

    Args:
        history_file: Path to history file (default: .project_manager_history)

    Returns:
        Configured PromptSession
    """
    # Ensure history file exists
    history_path = Path.cwd() / history_file
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.touch(exist_ok=True)

    # Key bindings
    kb = KeyBindings()

    @kb.add('c-l')
    def _(event):
        """Clear screen on Ctrl+L."""
        console.clear()
        info("Screen cleared. Press Enter to continue.")

    @kb.add('c-d')
    def _(event):
        """Exit on Ctrl+D."""
        event.app.exit()

    # Style
    style = Style.from_dict({
        'prompt': 'cyan bold',
        'completion-menu': 'bg:#333333 #ffffff',
        'completion-menu.completion': 'bg:#333333 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'completion-menu.meta.completion': 'bg:#444444 #ffffff',
        'completion-menu.meta.completion.current': 'bg:#00aaaa #000000',
    })

    # Create session
    session = PromptSession(
        history=FileHistory(str(history_path)),
        auto_suggest=AutoSuggestFromHistory(),
        completer=ProjectManagerCompleter(),
        complete_while_typing=True,
        key_bindings=kb,
        style=style,
        enable_history_search=True,  # Ctrl+R
        multiline=False,  # Can be toggled for multi-line
    )

    return session


def get_user_input(
    session: PromptSession,
    prompt: str = "> ",
    multiline: bool = False
) -> Optional[str]:
    """Get user input with all advanced features.

    Args:
        session: PromptSession instance
        prompt: Input prompt string
        multiline: Enable multi-line input

    Returns:
        User input string, or None if interrupted
    """
    try:
        text = session.prompt(
            prompt,
            multiline=multiline,
            prompt_continuation='... ' if multiline else None
        )
        return text.strip()

    except (EOFError, KeyboardInterrupt):
        return None


# Example usage
if __name__ == '__main__':
    session = create_input_session()
    console.print("[cyan]Advanced Input Demo[/cyan]")
    console.print("Try: TAB completion, Ctrl+L (clear), Ctrl+D (exit), Ctrl+R (search)")
    console.print()

    while True:
        user_input = get_user_input(session, prompt="[bold cyan]>[/bold cyan] ")

        if user_input is None:
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if user_input == '/exit':
            break

        console.print(f"[green]You entered:[/green] {user_input}")
```

---

### Phase 3: Enhanced Visual Feedback (3 hours)

**Objective**: Add loading spinners, progress bars, and status indicators

**Tasks**:
- [ ] Create contextual spinners for async operations
- [ ] Implement progress bars for long-running tasks
- [ ] Add timestamps (optional, configurable)
- [ ] Enhanced status indicators with animations

**Code to Add**:
```python
# In console_ui.py - Enhanced progress indicators

from contextlib import contextmanager
from rich.spinner import Spinner
from rich.status import Status

@contextmanager
def spinner(description: str = "Processing...", spinner_style: str = "dots"):
    """Show spinner during long operation.

    Args:
        description: Operation description
        spinner_style: Spinner style (dots, line, arc, etc.)

    Example:
        >>> with spinner("Loading data..."):
        ...     time.sleep(2)
    """
    with console.status(f"[cyan]{description}[/cyan]", spinner=spinner_style):
        yield


def progress_bar(
    items,
    description: str = "Processing...",
    total: Optional[int] = None
):
    """Iterate with progress bar.

    Args:
        items: Iterable to process
        description: Progress description
        total: Total items (if not len(items))

    Yields:
        Items from iterable

    Example:
        >>> for item in progress_bar(range(100), "Processing items"):
        ...     process(item)
    """
    from rich.progress import track

    total = total or (len(items) if hasattr(items, '__len__') else None)

    for item in track(items, description=description, total=total):
        yield item
```

---

### Phase 4: Integration & Polish (3 hours)

**Objective**: Integrate all components into project_manager CLI

**Tasks**:
- [ ] Modify `coffee_maker/cli/roadmap_cli.py` to use enhanced UI
- [ ] Modify `coffee_maker/cli/assistant_manager.py` for streaming
- [ ] Add terminal resize handling
- [ ] Implement graceful error recovery
- [ ] Test on various terminal sizes (80x24 minimum)

**Files to Modify**:
```python
# In coffee_maker/cli/roadmap_cli.py - Integrate enhanced UI

from coffee_maker.cli.advanced_input import create_input_session, get_user_input
from coffee_maker.cli.console_ui import (
    print_welcome,
    stream_response,
    spinner,
    console
)

def main():
    """Main CLI entry point with enhanced UI."""
    # ... existing setup ...

    # Create input session with history and autocomplete
    session = create_input_session()

    # Show welcome screen
    print_welcome()

    # Main loop with enhanced input
    while True:
        user_input = get_user_input(session, prompt="[bold cyan]❯[/bold cyan] ")

        if user_input is None or user_input == '/exit':
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        # Process with spinner
        with spinner("Processing your request..."):
            response = process_command(user_input)

        # Stream response
        if response.is_streaming:
            stream_response(response.generator)
        else:
            console.print(response.text)
```

---

### Phase 5: Testing & Validation (4 hours)

**Objective**: Comprehensive testing across terminals and scenarios

**Tasks**:
- [ ] Unit tests for all new functions
- [ ] Integration tests for full flow
- [ ] Manual testing on iTerm2, Terminal.app, VS Code terminal
- [ ] Test terminal sizes: 80x24, 120x40, fullscreen
- [ ] Test light/dark themes
- [ ] User acceptance testing

**Test File**:
```python
# tests/unit/test_console_ui_enhanced.py (NEW)

"""Unit tests for enhanced console UI features.

US-036: Console UI Polish
"""

import pytest
from unittest.mock import MagicMock, patch

from coffee_maker.cli.console_ui import stream_response, print_welcome, spinner
from coffee_maker.cli.advanced_input import create_input_session, ProjectManagerCompleter


class TestStreamingResponse:
    """Test streaming response functionality."""

    def test_stream_basic_text(self):
        """Test basic text streaming."""
        def text_gen():
            yield "Hello"
            yield " "
            yield "World"

        # Should not raise
        stream_response(text_gen(), markdown=False)

    def test_stream_markdown(self):
        """Test markdown streaming."""
        def md_gen():
            yield "# Title\n"
            yield "Some **bold** text"

        stream_response(md_gen(), markdown=True)

    def test_stream_empty(self):
        """Test streaming with no content."""
        def empty_gen():
            return
            yield  # Never reached

        stream_response(empty_gen())


class TestWelcomeScreen:
    """Test welcome screen display."""

    def test_welcome_screen_renders(self):
        """Test welcome screen renders without error."""
        print_welcome()  # Should not raise

    @patch('coffee_maker.cli.console_ui.console.print')
    def test_welcome_includes_version(self, mock_print):
        """Test welcome screen includes version."""
        print_welcome()

        # Should have called print with version info
        assert mock_print.called
        call_args = str(mock_print.call_args_list)
        assert 'Version' in call_args


class TestAdvancedInput:
    """Test advanced input features."""

    def test_create_session(self, tmp_path):
        """Test creating input session."""
        history_file = tmp_path / "test_history"
        session = create_input_session(str(history_file))

        assert session is not None
        assert history_file.exists()

    def test_completer_commands(self):
        """Test command completer."""
        completer = ProjectManagerCompleter()

        # Mock document
        class MockDoc:
            def get_word_before_cursor(self):
                return '/road'

        doc = MockDoc()
        completions = list(completer.get_completions(doc, None))

        assert len(completions) > 0
        assert any('roadmap' in c.text for c in completions)

    def test_completer_no_match(self):
        """Test completer with no matches."""
        completer = ProjectManagerCompleter()

        class MockDoc:
            def get_word_before_cursor(self):
                return '/xyz123'

        doc = MockDoc()
        completions = list(completer.get_completions(doc, None))

        assert len(completions) == 0


class TestProgressIndicators:
    """Test progress indicators."""

    def test_spinner_context(self):
        """Test spinner context manager."""
        with spinner("Testing..."):
            # Should not raise
            pass

    def test_progress_bar(self):
        """Test progress bar iteration."""
        from coffee_maker.cli.console_ui import progress_bar

        items = range(10)
        results = list(progress_bar(items, "Processing"))

        assert results == list(items)


# Integration tests
@pytest.mark.integration
class TestUIIntegration:
    """Integration tests for complete UI flow."""

    def test_full_interaction_flow(self, tmp_path):
        """Test complete user interaction flow."""
        # This would test:
        # 1. Welcome screen
        # 2. Input prompt
        # 3. Command processing
        # 4. Response streaming
        # 5. Graceful exit
        pass  # Implementation depends on full system


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│           project-manager CLI (main)                │
│                 roadmap_cli.py                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ├──────────────┬─────────────────┬───────────────┐
                 │              │                 │               │
┌────────────────▼──────────┐  ▼                 ▼               ▼
│      console_ui.py        │  advanced_input.py  commands/      assistant_mgr
│  (Enhanced Rich output)   │  (prompt_toolkit)   (cmd modules)  (AI chat)
│                           │
│ - stream_response()       │  - PromptSession
│ - print_welcome()         │  - History
│ - spinner()               │  - Autocomplete
│ - progress_bar()          │  - Key bindings
│ - Themes                  │
└───────────────────────────┘
```

### File Structure

```
coffee_maker/cli/
├── roadmap_cli.py           # Main entry point (MODIFY)
├── console_ui.py            # Enhanced UI utilities (EXTEND)
├── advanced_input.py        # NEW - Advanced input handling
├── ui_config.py             # NEW - Theme and configuration
└── commands/                # Command modules (existing)

tests/unit/
├── test_console_ui.py       # Existing tests (EXTEND)
└── test_console_ui_enhanced.py  # NEW - Enhanced feature tests

.gitignore                   # ADD: .project_manager_history
pyproject.toml              # Already has dependencies ✅
```

---

## Code Examples

### Example 1: Using Streaming Response

```python
# Before (basic)
console.print(response_text)

# After (polished)
from coffee_maker.cli.console_ui import stream_response

def process_ai_query(query: str):
    """Process query with streaming response."""
    response_stream = call_ai_api(query)  # Returns generator

    console.print("[bold cyan]Assistant:[/bold cyan]")
    stream_response(response_stream, markdown=True)
    console.print()
```

### Example 2: Using Advanced Input

```python
# Before (basic input)
user_input = input("> ")

# After (polished)
from coffee_maker.cli.advanced_input import create_input_session, get_user_input

session = create_input_session()

while True:
    user_input = get_user_input(
        session,
        prompt="[bold cyan]❯[/bold cyan] "
    )

    if user_input is None:  # Ctrl+D pressed
        break

    # Process input (has history, autocomplete, etc.)
    process(user_input)
```

### Example 3: Using Spinners and Progress

```python
# Before (silent operation)
data = fetch_github_data()
process_notifications(data)

# After (polished with feedback)
from coffee_maker.cli.console_ui import spinner, progress_bar

with spinner("Fetching GitHub data..."):
    data = fetch_github_data()

for notification in progress_bar(data, "Processing notifications"):
    process_notification(notification)

success("All notifications processed!")
```

---

## Testing Strategy

### Unit Tests (10+ tests)

**Coverage Areas**:
- ✅ Stream response function (3 tests)
- ✅ Welcome screen rendering (2 tests)
- ✅ Advanced input session creation (2 tests)
- ✅ Command autocomplete (3 tests)
- ✅ Progress indicators (2 tests)
- ✅ Theme switching (1 test)
- ✅ Keyboard shortcuts (3 tests)

### Integration Tests (5+ tests)

**Test Scenarios**:
1. Full conversation flow with streaming
2. Command history persistence across sessions
3. Terminal resize handling
4. Multi-line input mode
5. Error recovery and graceful degradation

### Manual Testing Checklist

**Terminal Emulators**:
- [ ] iTerm2 (macOS)
- [ ] Terminal.app (macOS)
- [ ] VS Code integrated terminal
- [ ] tmux sessions

**Terminal Sizes**:
- [ ] 80x24 (minimum supported)
- [ ] 120x40 (typical)
- [ ] Fullscreen (varies)

**Themes**:
- [ ] Light theme
- [ ] Dark theme
- [ ] High contrast

**Keyboard Shortcuts**:
- [ ] Ctrl+C (graceful exit with confirmation)
- [ ] Ctrl+D (exit)
- [ ] Ctrl+L (clear screen)
- [ ] Up/Down arrows (history navigation)
- [ ] TAB (autocomplete)
- [ ] Ctrl+R (reverse search)

**User Acceptance**:
- [ ] 3+ users test the interface
- [ ] Collect feedback on smoothness and usability
- [ ] Target: >8/10 satisfaction rating

---

## Success Criteria

### Quantitative Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| User Satisfaction | >8/10 | User survey rating |
| Streaming Smoothness | Matches claude-cli | Visual comparison |
| Keyboard Shortcuts | 100% functional | Manual testing |
| Error Recovery | 100% graceful | Error simulation tests |
| Terminal Compatibility | 3+ emulators | Manual testing |
| Response Time | <100ms for input | Performance testing |

### Qualitative Metrics

- ✅ Visual quality matches claude-cli professional appearance
- ✅ Streaming feels smooth and natural
- ✅ Error messages are clear and actionable
- ✅ Users understand how to use keyboard shortcuts
- ✅ Interface feels intuitive and delightful
- ✅ Increased usage of project-manager chat

### Completion Checklist

**Phase 1**: Rich Library Enhancement
- [ ] Streaming response function implemented
- [ ] Professional welcome screen created
- [ ] Enhanced progress indicators added
- [ ] Syntax highlighting functional
- [ ] Theme detection working

**Phase 2**: Advanced Input
- [ ] Command history persisting to file
- [ ] TAB autocomplete working
- [ ] Keyboard shortcuts functional (Ctrl+C/D/L/R)
- [ ] Multi-line input support added
- [ ] History search (Ctrl+R) working

**Phase 3**: Enhanced Visual Feedback
- [ ] Loading spinners implemented
- [ ] Progress bars for long tasks
- [ ] Status indicators with animations
- [ ] Timestamps (optional) available

**Phase 4**: Integration & Polish
- [ ] roadmap_cli.py updated
- [ ] assistant_manager.py updated for streaming
- [ ] Terminal resize handling added
- [ ] Error recovery implemented
- [ ] Tested on 80x24 minimum

**Phase 5**: Testing & Validation
- [ ] 10+ unit tests passing
- [ ] 5+ integration tests passing
- [ ] Manual testing on 3+ terminals
- [ ] Light/dark themes tested
- [ ] User acceptance testing complete

---

## References

### Internal Documentation

- `coffee_maker/cli/console_ui.py` - Existing console UI utilities
- `coffee_maker/cli/roadmap_cli.py` - Main CLI entry point
- `docs/roadmap/ROADMAP.md` - US-036 definition (line 23698)
- `pyproject.toml` - Dependencies (rich, prompt-toolkit)

### External Resources

**Claude CLI Inspiration**:
- Observe streaming behavior in claude-cli
- Study color scheme and formatting
- Analyze keyboard shortcut patterns
- Note error message presentation

**Libraries**:
- [rich documentation](https://rich.readthedocs.io/) - Rich text formatting
- [prompt_toolkit documentation](https://python-prompt-toolkit.readthedocs.io/) - Advanced input
- [click documentation](https://click.palletsprojects.com/) - CLI framework

### Example Commands

```bash
# Current project-manager chat (basic)
poetry run project-manager chat

# After implementation (polished)
poetry run project-manager chat
# → Shows welcome screen
# → Streaming responses
# → TAB autocomplete
# → Ctrl+R for history search
# → Professional appearance

# Testing during development
pytest tests/unit/test_console_ui_enhanced.py -v
pytest tests/unit/test_console_ui_enhanced.py -v -m integration

# Manual testing
poetry run project-manager chat
# Try: TAB, Ctrl+L, Ctrl+R, arrow keys
```

---

## Notes for Implementer

### Critical Success Factors

1. **Smooth Streaming**: The streaming must feel as smooth as claude-cli - this is non-negotiable
2. **Keyboard Shortcuts**: All shortcuts must be intuitive and consistent with Unix conventions
3. **Error Messages**: Must guide users to solutions, not just report problems
4. **Testing**: Test on real terminal emulators, not just in tests
5. **User Feedback**: Get feedback from actual users before marking complete

### Common Pitfalls to Avoid

- ❌ Choppy streaming (buffer too much before displaying)
- ❌ Broken formatting on terminal resize
- ❌ Keyboard shortcuts that conflict with terminal defaults
- ❌ Assuming one terminal size/theme
- ❌ Generic error messages without context

### Best Practices

- ✅ Use context managers for spinners and progress
- ✅ Test edge cases (empty input, very long input)
- ✅ Provide clear feedback for every action
- ✅ Make keyboard shortcuts discoverable
- ✅ Graceful degradation if features unavailable

### Dependencies Already Satisfied

The good news: All required dependencies are already in `pyproject.toml`!

```toml
[tool.poetry.dependencies]
rich = (included via other deps)
prompt-toolkit = "^3.0.47"  ✅ Already there!
Pygments = "^2.18.0"        ✅ Already there!
```

No new dependencies needed - just use what's already available.

---

## Future Enhancements (Post-US-036)

These are NOT part of US-036 but could be future improvements:

1. **Custom Themes**: User-configurable color schemes
2. **Plugin System**: Extend UI with custom components
3. **Voice Input**: Optional voice command support
4. **Keyboard Macros**: Record/replay command sequences
5. **Split Panes**: Show status sidebar while chatting
6. **Search**: Search through conversation history
7. **Export**: Export conversations to markdown/HTML

---

**Last Updated**: 2025-10-20
**Status**: Ready for Implementation
**Estimated Timeline**: 2-3 days (12-16 hours)
**Next Step**: Begin Phase 1 - Rich Library Enhancement
