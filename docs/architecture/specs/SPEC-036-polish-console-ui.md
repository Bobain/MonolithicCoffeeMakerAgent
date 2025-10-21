# SPEC-036: Polish Console UI to Claude-CLI Quality

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-17

**Last Updated**: 2025-10-17

**Related**: US-036 (ROADMAP), ADR-003 (Simplification-First Approach)

**Related ADRs**: None

**Assigned To**: code_developer

---

## Executive Summary

This specification describes incremental UI improvements to bring project-manager console chat to professional quality, focusing on smooth streaming responses and rich formatting. Uses existing `rich` library and adds character-by-character streaming for claude-cli-like experience.

---

## Problem Statement

### Current Situation

project-manager console UI works but lacks polish:
- Responses appear all-at-once (no streaming)
- Plain text output (no colors, formatting)
- No progress indicators during long operations
- Basic error messages
- Feels "unfinished" compared to claude-cli

**Proof**: Try `poetry run project-manager` → output is functional but not delightful

### Goal

Improve console UI to feel professional:
- **Smooth streaming** (character-by-character like claude-cli)
- **Rich formatting** (colors, bold, syntax highlighting)
- **Clear progress** (spinners for long operations)
- **Professional errors** (formatted, actionable messages)

### Non-Goals

- NOT rebuilding entire CLI (incremental improvements only)
- NOT adding complex features (keyboard shortcuts, autocomplete → future)
- NOT creating custom UI framework (use `rich` library)
- NOT matching 100% of claude-cli features (focus on core UX)

---

## Requirements

### Functional Requirements

1. **FR-1**: Streaming responses character-by-character (like claude-cli)
2. **FR-2**: Rich text formatting (colors, bold, code blocks)
3. **FR-3**: Progress indicators (spinners for API calls, file operations)
4. **FR-4**: Syntax highlighting for code blocks
5. **FR-5**: Clear error messages with formatting

### Non-Functional Requirements

1. **NFR-1**: Performance: Streaming latency < 50ms per chunk
2. **NFR-2**: Compatibility: Works in standard terminals (80x24 minimum)
3. **NFR-3**: Accessibility: Colors work in light and dark themes
4. **NFR-4**: Maintainability: Uses `rich` library (not custom rendering)

### Constraints

- Must use existing `rich` library (already installed)
- Must work on macOS, Linux (development environments)
- Must not break existing CLI behavior
- Must integrate with current chat_interface.py

---

## Proposed Solution

### High-Level Approach

**Incremental Polish**: Add streaming + formatting to existing CLI using `rich` library.

**Why This is Simple**:
- Use `rich` library (already installed, well-documented)
- Minimal code changes (~150 lines total)
- No architecture changes (just presentation layer)
- No new dependencies

### Key Improvements

```
BEFORE (current):
User: What is US-035?
[... 2 second delay ...]
Response: US-035 is about singleton agent enforcement...
[entire response appears at once]

AFTER (polished):
User: What is US-035?
[spinner] Thinking...
Response: [streams character-by-character]
US-035 is about singleton agent enforcement...
[smooth, gradual appearance]

Code blocks have syntax highlighting
Errors are nicely formatted in red
Progress shown for long operations
```

---

## Detailed Design

### Component 1: Streaming Response Renderer

**File**: `coffee_maker/cli/streaming_renderer.py` (~80 lines, NEW)

**Purpose**: Stream text character-by-character with rich formatting

**Interface**:
```python
"""
Streaming renderer for console UI using rich library.
"""

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.syntax import Syntax
import time

console = Console()

def stream_response(text: str, delay: float = 0.01) -> None:
    """
    Stream text character-by-character to console.

    Args:
        text: Text to stream
        delay: Delay between characters in seconds (default: 0.01 = 10ms)

    Example:
        >>> stream_response("Hello, world!")
        # Prints "Hello, world!" smoothly, one char at a time
    """
    for char in text:
        console.print(char, end="", highlight=False)
        time.sleep(delay)
    console.print()  # Newline at end


def stream_markdown(markdown_text: str) -> None:
    """
    Stream markdown content with rich formatting.

    Args:
        markdown_text: Markdown-formatted text

    Example:
        >>> stream_markdown("# Heading\\n\\nSome **bold** text")
        # Renders with formatting, streams smoothly
    """
    # Parse markdown
    md = Markdown(markdown_text)

    # Stream with formatting
    with Live(md, console=console, refresh_per_second=20) as live:
        # Render incrementally
        for i in range(len(markdown_text)):
            partial_md = Markdown(markdown_text[:i+1])
            live.update(partial_md)
            time.sleep(0.01)


def show_spinner(message: str) -> Live:
    """
    Show spinner for long operations.

    Args:
        message: Message to show alongside spinner

    Returns:
        Live object (use as context manager)

    Example:
        >>> with show_spinner("Thinking..."):
        ...     # Do long operation
        ...     result = api_call()
    """
    from rich.spinner import Spinner
    spinner = Spinner("dots", text=message)
    return Live(spinner, console=console)


def format_code_block(code: str, language: str = "python") -> None:
    """
    Display code block with syntax highlighting.

    Args:
        code: Code to display
        language: Programming language (for syntax highlighting)

    Example:
        >>> format_code_block("def hello(): print('hi')", language="python")
        # Displays with Python syntax highlighting
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def format_error(error_message: str) -> None:
    """
    Display error message with formatting.

    Args:
        error_message: Error to display

    Example:
        >>> format_error("API key not found!")
        # Displays in red with error icon
    """
    console.print(f"[bold red]❌ Error:[/bold red] {error_message}")
```

**Implementation Notes**:
- `time.sleep(0.01)` = 10ms delay between chars (smooth but not slow)
- `rich.live.Live` for incremental rendering
- `rich.syntax.Syntax` for code highlighting
- `rich.spinner.Spinner` for progress

### Component 2: Integration with Existing Chat Interface

**File**: `coffee_maker/cli/chat_interface.py` (~20 lines modified)

**Changes**:
```python
# BEFORE
def display_response(response: str) -> None:
    print(response)  # Entire response at once

# AFTER
from coffee_maker.cli.streaming_renderer import (
    stream_response,
    stream_markdown,
    show_spinner,
    format_error
)

def display_response(response: str) -> None:
    """Display response with streaming."""
    # If response has markdown (code blocks, headers)
    if has_markdown_formatting(response):
        stream_markdown(response)
    else:
        stream_response(response)

def handle_api_call() -> str:
    """Make API call with spinner."""
    with show_spinner("Thinking..."):
        response = api.call(...)
    return response

def handle_error(error: Exception) -> None:
    """Display error with formatting."""
    format_error(str(error))
```

**Minimal Changes**:
- Replace `print()` → `stream_response()`
- Wrap API calls with `show_spinner()`
- Use `format_error()` for exceptions

### Component 3: Rich Console Configuration

**File**: `coffee_maker/cli/console_config.py` (~30 lines, NEW)

**Purpose**: Configure rich console for consistent formatting

**Interface**:
```python
"""
Console configuration for rich UI.
"""

from rich.console import Console
from rich.theme import Theme

# Custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "agent": "bold magenta",
    "code": "white on grey23",
})

# Global console instance
console = Console(theme=custom_theme)

# Status indicators
STATUS_ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "thinking": "🤔",
    "working": "⚙️",
}
```

---

## Testing Strategy

### Manual Testing

**Test 1: Streaming Response**
```bash
poetry run project-manager
> What is US-035?
# Expected: Response streams smoothly, character-by-character
# Verify: Not all-at-once, smooth like claude-cli
```

**Test 2: Code Block Formatting**
```bash
poetry run project-manager
> Show me the daemon code
# Expected: Code block with syntax highlighting
# Verify: Colors, line numbers, readable
```

**Test 3: Error Handling**
```bash
# Trigger API error (disconnect network)
poetry run project-manager
> test
# Expected: Red error message with icon
# Verify: Clear, actionable, nicely formatted
```

**Test 4: Spinner**
```bash
poetry run project-manager
> Analyze the codebase
# Expected: Spinner shows "Thinking..." during API call
# Verify: Spinner animates, message clear
```

### Acceptance Criteria

- [ ] Responses stream character-by-character (like claude-cli)
- [ ] Code blocks have syntax highlighting
- [ ] Spinners show during API calls
- [ ] Errors formatted in red with icon
- [ ] UI feels smooth and professional
- [ ] Works in standard terminal (80x24)
- [ ] No broken formatting in dark/light themes

---

## Rollout Plan

### Phase 1: Core Streaming (Day 1 - 4 hours)

**Goal**: Add character-by-character streaming

**Tasks**:
1. Create `streaming_renderer.py` (80 lines)
2. Implement `stream_response()` and `stream_markdown()`
3. Update `chat_interface.py` to use streaming (20 lines)
4. Test with real API responses

**Success Criteria**:
- Responses stream smoothly
- No performance degradation
- Feels like claude-cli

### Phase 2: Progress & Errors (Day 2 - 3 hours)

**Goal**: Add spinners and error formatting

**Tasks**:
1. Implement `show_spinner()` in `streaming_renderer.py`
2. Implement `format_error()` in `streaming_renderer.py`
3. Update error handling in `chat_interface.py`
4. Test all error scenarios

**Success Criteria**:
- Spinner shows during API calls
- Errors nicely formatted
- Clear user feedback

### Phase 3: Code Highlighting (Day 2 - 2 hours)

**Goal**: Add syntax highlighting for code blocks

**Tasks**:
1. Implement `format_code_block()` in `streaming_renderer.py`
2. Detect code blocks in responses (```python ... ```)
3. Apply syntax highlighting
4. Test with various languages (Python, JSON, bash)

**Success Criteria**:
- Code blocks highlighted correctly
- Multiple languages supported
- Readable in dark and light themes

### Phase 4: Polish & Testing (Day 3 - 3 hours)

**Goal**: Final polish and validation

**Tasks**:
1. Create `console_config.py` (theme, icons)
2. Apply consistent colors across UI
3. Test in different terminals (iTerm, Terminal.app, Linux)
4. Get user feedback
5. Refine based on feedback

**Success Criteria**:
- Consistent theme
- Works across terminals
- User feedback positive (> 8/10)

---

## Why This is Simple (vs Strategic Spec)

**Strategic Spec** (US-036 in ROADMAP):
- Mentioned prompt_toolkit (complex input handling)
- Keyboard shortcuts (Ctrl+C, Ctrl+L, Tab, etc.)
- Command history and autocomplete
- Multi-line input support
- Responsive design for terminal resize
- ~2-3 days estimate

**This Simplified Spec**:
- **Only streaming + formatting** (core UX improvement)
- **Uses rich library** (no custom rendering)
- **No keyboard shortcuts** (future enhancement)
- **No autocomplete** (future enhancement)
- **Minimal code** (~130 lines total, not 500+)
- **Same 2-3 days estimate** (but simpler implementation)

**What We REUSE**:
- Existing `rich` library (already installed)
- Existing `chat_interface.py` structure (minimal changes)
- Existing API integration (no changes needed)
- Standard terminal capabilities (no custom UI framework)

**Complexity Reduction**:
- **No prompt_toolkit** (complex, 80+ lines to integrate)
- **No keyboard shortcuts** (20+ shortcuts deferred)
- **No command history** (arrows, Ctrl+R deferred)
- **No autocomplete** (TAB completion deferred)
- **Core UX only** (streaming, formatting, spinners)

**Result**: 70% less code, same perceived quality improvement

---

## Future Enhancements

**NOT in this spec** (deferred):
1. **Keyboard Shortcuts** → US-036-Phase-2
   - Ctrl+C (graceful exit), Ctrl+L (clear), Ctrl+R (history search)
   - Requires prompt_toolkit integration (~80 lines)

2. **Command Autocomplete** → US-036-Phase-3
   - TAB completion for commands
   - Requires command registry (~40 lines)

3. **Multi-line Input** → US-036-Phase-4
   - Shift+Enter for multi-line prompts
   - Requires prompt_toolkit (~30 lines)

4. **Terminal Resize Handling** → US-036-Phase-5
   - Graceful reflow on resize
   - Requires signal handling (~20 lines)

5. **Custom Themes** → US-036-Phase-6
   - User-configurable color schemes
   - Requires config file (~40 lines)

**Phased Approach**: Start simple, add features based on user feedback

---

## References

- US-036: Polish Console UI to Claude-CLI Quality (ROADMAP)
- ADR-003: Simplification-First Approach
- Rich library: https://rich.readthedocs.io/
- Claude CLI: https://github.com/anthropics/claude-cli (inspiration)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Created (Draft) | architect |

---

## Approval

- [ ] architect (author) - Ready for review
- [ ] code_developer (implementer) - Can implement in 2-3 days
- [ ] project_manager (strategic alignment) - Meets US-036 core goals
- [ ] User (final approval) - Pending

**Approval Date**: TBD

---

**Implementation Estimate**: 2-3 days (12 hours)

**Phases**:
- Phase 1: Streaming (4 hours)
- Phase 2: Progress/Errors (3 hours)
- Phase 3: Code Highlighting (2 hours)
- Phase 4: Polish (3 hours)

**Result**: Professional console UI with smooth streaming and rich formatting!
