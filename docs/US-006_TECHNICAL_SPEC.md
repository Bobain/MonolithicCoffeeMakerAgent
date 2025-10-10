# US-006: Claude-CLI Quality UX for project-manager chat

**Technical Specification Document**

**Status**: 📝 Planning (2025-10-10)
**Assignee**: code_developer (autonomous daemon)
**Estimated Effort**: 2-3 days (3 story points)
**Priority**: 🚨 **TOP PRIORITY**

---

## 1. Executive Summary

**Goal**: Transform `project-manager chat` from a basic REPL into a professional, polished console interface that matches the quality and UX of `claude-cli`.

**Why This Matters**:
- This is the PRIMARY interface users will interact with daily
- Quality UX directly impacts user satisfaction and adoption
- Foundation for all future project-manager features
- Demonstrates project maturity and professional polish

**Current State**: ✅ Functional but basic
- Basic REPL with Rich library for markdown
- Command routing (/help, /view, /add, etc.)
- Natural language processing with Claude AI
- Simple input/output (no streaming, no history, no auto-completion)

**Desired State**: 🎯 Claude-CLI quality
- Streaming responses with typing indicators
- Multi-line input (Shift+Enter)
- Input history (↑/↓ navigation)
- Auto-completion (Tab for commands/priorities)
- Enhanced syntax highlighting
- Session persistence
- File previews and progress indicators

---

## 2. Current Architecture Analysis

### 2.1 Current Implementation

**File**: `coffee_maker/cli/chat_interface.py` (394 lines)

**Key Components**:
```python
class ChatSession:
    def __init__(self, ai_service, editor):
        self.ai_service = AIService           # Claude AI integration
        self.editor = RoadmapEditor           # Roadmap manipulation
        self.console = Console()              # Rich console (basic)
        self.history: List[Dict] = []         # Conversation history (in-memory only)

    def start(self):
        """Main entry point - displays welcome and runs REPL loop"""

    def _run_repl_loop(self):
        """Simple REPL: console.input() → process → console.print()"""
        user_input = self.console.input("[bold cyan]You:[/] ")  # ← LIMITATION: No multi-line, no history

    def _process_input(self, user_input: str):
        """Routes to command handler or AI service"""

    def _display_response(self, response: str):
        """Renders markdown response"""
        md = Markdown(response)
        self.console.print(md)                # ← LIMITATION: No streaming
```

**Current Dependencies**:
```python
rich==13.7.0             # Terminal UI (markdown, panels, tables)
```

**Limitations Identified**:

| Feature | Current State | Limitation |
|---------|---------------|------------|
| **Input** | `console.input()` | Single-line only, no history, no completion |
| **Output** | `console.print()` | Blocking (no streaming), no typing indicator |
| **Syntax Highlighting** | `Markdown()` | Basic markdown only, no code highlighting |
| **History** | In-memory list | Not persisted, no navigation |
| **Session** | Ephemeral | Lost on exit, no restore |

---

## 3. Technical Requirements

### 3.1 Streaming Responses

**Objective**: Display AI responses progressively (character-by-character or chunk-by-chunk) like `claude-cli`

**Technical Approach**:

**Option A: Anthropic SDK Streaming** (Recommended ✅)
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Streaming API call
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=8000,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        console.print(text, end="")  # Print character-by-character
```

**Why Option A**:
- Native streaming support in Anthropic SDK
- Low latency (chunks arrive immediately)
- Clean API (no manual parsing needed)
- Matches claude-cli implementation

**Option B: Langchain Streaming** (Alternative)
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import StreamingStdOutCallbackHandler

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
```

**Why Not Option B**:
- ai_service.py already uses Langchain (but not streaming)
- More abstraction layers = harder to debug
- Less control over output formatting

**Implementation Plan**:
1. Add `stream=True` parameter to `AIService.process_request()`
2. Modify `_display_response()` to handle streaming iterator
3. Add typing indicator while waiting for first chunk
4. Use `rich.live.Live()` context for progressive display

**Code Example**:
```python
from rich.live import Live
from rich.spinner import Spinner

def _display_streaming_response(self, stream_iterator):
    """Display AI response with streaming."""

    # Show typing indicator
    with Live(Spinner("dots", text="Claude is thinking..."), console=self.console):
        time.sleep(0.5)  # Brief pause for UX

    # Stream response
    self.console.print("\n[bold green]Claude:[/]")
    full_response = ""

    for chunk in stream_iterator:
        self.console.print(chunk, end="")
        full_response += chunk

    self.console.print()  # Final newline
    return full_response
```

**Testing**:
```python
def test_streaming_response():
    """Test streaming response display."""
    session = ChatSession(ai_service, editor)

    # Mock streaming iterator
    mock_stream = iter(["Hello", " ", "world", "!"])

    response = session._display_streaming_response(mock_stream)
    assert response == "Hello world!"
```

---

### 3.2 Multi-line Input Support

**Objective**: Allow users to input multi-line text (Shift+Enter for newlines, Enter to submit)

**Technical Approach**: Replace `console.input()` with `prompt-toolkit`

**Why prompt-toolkit**:
- Industry standard for advanced CLI input
- Used by IPython, ptpython, mycli, pgcli
- Built-in support for multi-line, history, auto-completion
- Excellent documentation and active maintenance

**Dependency**:
```toml
# Add to pyproject.toml
prompt-toolkit = "^3.0.47"
```

**Implementation**:
```python
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

# Create key bindings
bindings = KeyBindings()

@bindings.add('enter')
def _(event):
    """Submit on Enter."""
    event.current_buffer.validate_and_handle()

@bindings.add('s-enter')  # Shift+Enter
def _(event):
    """Insert newline on Shift+Enter."""
    event.current_buffer.insert_text('\n')

# Create prompt session
prompt_session = PromptSession(
    message="You: ",
    multiline=True,
    key_bindings=bindings,
)

# Get multi-line input
user_input = prompt_session.prompt()
```

**User Experience**:
```
You: I want to add a new priority
... for user authentication. It should
... include login, logout, and password reset.
... (Press Enter to submit)
```

**Edge Cases**:
- Empty input (just Enter): Skip, don't send to AI
- Long input (>2000 chars): Warn user about token limits
- Paste multi-line: Should work seamlessly

**Testing**:
```python
def test_multiline_input():
    """Test multi-line input handling."""
    # Simulate Shift+Enter for newlines, Enter to submit
    input_text = "Line 1\nLine 2\nLine 3"

    # Verify input is captured correctly
    assert "\n" in input_text
    assert input_text.count("\n") == 2
```

---

### 3.3 Input History Navigation

**Objective**: Allow users to navigate previous commands with ↑/↓ arrow keys

**Technical Approach**: Use `prompt-toolkit` built-in history

**Implementation**:
```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

# Create prompt session with file-backed history
prompt_session = PromptSession(
    message="You: ",
    history=FileHistory(os.path.expanduser("~/.project_manager_history")),
    enable_history_search=True,  # Ctrl+R for reverse search
)

# History automatically persists across sessions
user_input = prompt_session.prompt()  # ↑/↓ to navigate
```

**Features Enabled**:
- ↑/↓: Navigate history
- Ctrl+R: Reverse history search (incremental search)
- History persists across sessions (saved to file)
- Duplicate prevention (optional)

**Configuration**:
```python
# Advanced history configuration
from prompt_toolkit.history import InMemoryHistory, ThreadedHistory

class SmartHistory(FileHistory):
    """Custom history with de-duplication and limits."""

    def __init__(self, filename, max_entries=1000):
        super().__init__(filename)
        self.max_entries = max_entries

    def store_string(self, string):
        """Store string, avoiding duplicates."""
        # Don't store duplicates of last command
        if self.get_strings() and self.get_strings()[-1] == string:
            return

        super().store_string(string)

        # Trim to max entries
        if len(self.get_strings()) > self.max_entries:
            self._trim_history()
```

**Testing**:
```python
def test_input_history():
    """Test input history navigation."""
    history = InMemoryHistory()
    history.append_string("Command 1")
    history.append_string("Command 2")

    # Verify history contains commands
    assert list(history.get_strings()) == ["Command 1", "Command 2"]
```

---

### 3.4 Auto-completion

**Objective**: Tab completion for commands, priority names, and file paths

**Technical Approach**: `prompt-toolkit` custom completer

**Implementation**:
```python
from prompt_toolkit.completion import Completer, Completion

class ProjectManagerCompleter(Completer):
    """Auto-completer for project-manager chat."""

    def __init__(self, editor: RoadmapEditor):
        self.editor = editor

    def get_completions(self, document, complete_event):
        """Generate completions based on current input."""
        word = document.get_word_before_cursor()
        text = document.text_before_cursor

        # Complete slash commands
        if text.startswith("/"):
            commands = ["help", "view", "add", "update", "status", "exit", "notifications"]
            for cmd in commands:
                if cmd.startswith(word.lstrip("/")):
                    yield Completion(cmd, start_position=-len(word))

        # Complete priority names
        elif "priority" in text.lower() or "PRIORITY" in text:
            priorities = self.editor.list_priorities()
            for priority in priorities:
                if priority["name"].lower().startswith(word.lower()):
                    yield Completion(
                        priority["name"],
                        start_position=-len(word),
                        display_meta=priority["title"][:50]  # Show title as hint
                    )

        # Complete file paths (for file-related commands)
        elif text.startswith("/view ") or text.startswith("/read "):
            # File path completion
            from prompt_toolkit.completion import PathCompleter
            path_completer = PathCompleter(only_directories=False)
            yield from path_completer.get_completions(document, complete_event)

# Use in prompt session
prompt_session = PromptSession(
    message="You: ",
    completer=ProjectManagerCompleter(editor),
    complete_while_typing=True,  # Show completions as user types
)
```

**User Experience**:
```
You: /v[TAB]
     → /view

You: PRIORITY [TAB]
     → PRIORITY 1 (Analytics Dashboard)
     → PRIORITY 2 (Project Manager CLI)
     → PRIORITY 2.5 (UX Documentation)
     → ...

You: /view docs/RO[TAB]
     → /view docs/ROADMAP.md
```

**Testing**:
```python
def test_auto_completion():
    """Test auto-completion functionality."""
    completer = ProjectManagerCompleter(editor)

    # Mock document
    from prompt_toolkit.document import Document
    doc = Document("/vi", cursor_position=3)

    # Get completions
    completions = list(completer.get_completions(doc, None))

    # Verify /view is suggested
    assert any(c.text == "view" for c in completions)
```

---

### 3.5 Enhanced Syntax Highlighting

**Objective**: Better code syntax highlighting (better than basic markdown)

**Technical Approach**: Use `Pygments` for code blocks

**Dependency**:
```toml
# Add to pyproject.toml
Pygments = "^2.18.0"  # Syntax highlighting
```

**Implementation**:
```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from rich.syntax import Syntax

def _display_response_with_syntax(self, response: str):
    """Display response with enhanced syntax highlighting."""

    # Split response into text and code blocks
    import re
    code_block_pattern = r'```(\w+)?\n(.*?)```'

    parts = []
    last_end = 0

    for match in re.finditer(code_block_pattern, response, re.DOTALL):
        # Add text before code block
        if match.start() > last_end:
            parts.append(("text", response[last_end:match.start()]))

        # Add code block with language
        language = match.group(1) or "python"  # Default to python
        code = match.group(2)
        parts.append(("code", code, language))

        last_end = match.end()

    # Add remaining text
    if last_end < len(response):
        parts.append(("text", response[last_end:]))

    # Render parts
    for part in parts:
        if part[0] == "text":
            md = Markdown(part[1])
            self.console.print(md)
        elif part[0] == "code":
            syntax = Syntax(part[1], part[2], theme="monokai", line_numbers=True)
            self.console.print(syntax)
```

**Before** (basic markdown):
```
Here's the code:

def hello():
    print("Hello")
```

**After** (syntax highlighted):
```python
1 │ def hello():
2 │     print("Hello")
```
(with colors: keywords in blue, strings in green, etc.)

**Testing**:
```python
def test_syntax_highlighting():
    """Test syntax highlighting for code blocks."""
    response = """
Here's some Python code:

```python
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
```

And some JavaScript:

```javascript
const add = (a, b) => a + b;
```
"""

    # Verify code blocks are extracted
    code_blocks = extract_code_blocks(response)
    assert len(code_blocks) == 2
    assert code_blocks[0]["language"] == "python"
    assert code_blocks[1]["language"] == "javascript"
```

---

### 3.6 Colored Diffs

**Objective**: Show roadmap changes with colored diff (added/removed lines)

**Technical Approach**: Use `difflib` + Rich styling

**Implementation**:
```python
import difflib
from rich.table import Table

def _display_roadmap_diff(self, old_content: str, new_content: str):
    """Display colored diff of roadmap changes."""

    # Generate unified diff
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile="ROADMAP.md (before)",
        tofile="ROADMAP.md (after)",
        lineterm=""
    )

    # Display with colors
    self.console.print("\n[bold cyan]Roadmap Changes:[/]\n")

    for line in diff:
        if line.startswith("+"):
            self.console.print(f"[green]{line}[/]")
        elif line.startswith("-"):
            self.console.print(f"[red]{line}[/]")
        elif line.startswith("@@"):
            self.console.print(f"[cyan]{line}[/]")
        else:
            self.console.print(line)
```

**User Experience**:
```diff
Roadmap Changes:

@@ -106,6 +106,8 @@
 ### PRIORITY 2: Project Manager ✅ Complete
+### PRIORITY 2.6: Chat UX 🔄 In Progress
+Status: Implementing streaming responses
 ### PRIORITY 3: code_developer ✅ Complete
```
(with colors: green for additions, red for deletions, cyan for line numbers)

---

### 3.7 Session Persistence

**Objective**: Save and restore conversation history across sessions

**Technical Approach**: JSON file in user's home directory

**Implementation**:
```python
import json
from pathlib import Path

class ChatSession:
    def __init__(self, ai_service, editor):
        self.session_file = Path.home() / ".project_manager_sessions" / "default.json"
        self.session_file.parent.mkdir(exist_ok=True)

        # Load previous session
        self._load_session()

    def _load_session(self):
        """Load previous session history."""
        if self.session_file.exists():
            with open(self.session_file, "r") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.console.print(f"[dim]Restored {len(self.history)} messages from previous session[/]")

    def _save_session(self):
        """Save session history to file."""
        with open(self.session_file, "w") as f:
            json.dump({
                "history": self.history,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)

    def _run_repl_loop(self):
        """REPL loop with auto-save."""
        while self.active:
            # ... process input ...

            # Auto-save after each interaction
            self._save_session()

    def _display_goodbye(self):
        """Save session on exit."""
        self._save_session()
        self.console.print("[dim]Session saved.[/]")
```

**Session File Format** (`~/.project_manager_sessions/default.json`):
```json
{
  "history": [
    {"role": "user", "content": "Add priority for authentication"},
    {"role": "assistant", "content": "✅ Added PRIORITY 10: Authentication"}
  ],
  "last_updated": "2025-10-10T14:30:00"
}
```

**Testing**:
```python
def test_session_persistence():
    """Test session save/restore."""
    session1 = ChatSession(ai_service, editor)
    session1.history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
    session1._save_session()

    # Create new session (should restore history)
    session2 = ChatSession(ai_service, editor)
    assert len(session2.history) == 2
    assert session2.history[0]["content"] == "Hello"
```

---

### 3.8 Typing Indicator

**Objective**: Show spinner/indicator while AI is thinking

**Technical Approach**: Rich spinner with Live context

**Implementation**:
```python
from rich.live import Live
from rich.spinner import Spinner

def _handle_natural_language(self, text: str) -> str:
    """Handle natural language with typing indicator."""

    # Show typing indicator
    with Live(
        Spinner("dots", text="[cyan]Claude is thinking...[/]"),
        console=self.console,
        refresh_per_second=10
    ) as live:
        # Process request (blocking)
        response = self.ai_service.process_request(
            user_input=text,
            context=self._build_context(),
            history=self.history
        )

    # Typing indicator disappears, response appears
    return response.message
```

**User Experience**:
```
You: What's the next priority?

⠋ Claude is thinking...

(after 2 seconds)

Claude: The next priority is PRIORITY 2.6: Chat UX improvements.
```

---

### 3.9 File Previews

**Objective**: Show first 10 lines of files when AI references them

**Technical Approach**: Detect file paths in responses, offer preview

**Implementation**:
```python
import re
from pathlib import Path

def _display_response_with_previews(self, response: str):
    """Display response with file previews."""

    # Detect file paths (simple heuristic)
    file_pattern = r'`([a-zA-Z0-9_/\.]+\.(py|md|txt|json|yaml))`'

    files_mentioned = re.findall(file_pattern, response)

    # Display response
    self._display_response(response)

    # Offer previews for mentioned files
    if files_mentioned:
        self.console.print("\n[dim]Files mentioned:[/]")
        for file_path, _ in files_mentioned[:3]:  # Max 3 previews
            if Path(file_path).exists():
                preview = self._get_file_preview(file_path, lines=10)

                self.console.print(f"\n[cyan]{file_path}:[/]")
                syntax = Syntax(preview, Path(file_path).suffix[1:], line_numbers=True)
                self.console.print(syntax)

def _get_file_preview(self, file_path: str, lines: int = 10) -> str:
    """Get first N lines of file."""
    with open(file_path, "r") as f:
        preview_lines = [next(f) for _ in range(lines) if f]
        return "".join(preview_lines)
```

**User Experience**:
```
You: What's in ai_service.py?

Claude: `ai_service.py` contains the AIService class that handles Claude API integration.

Files mentioned:
coffee_maker/cli/ai_service.py:
  1 │ """AI Service - Claude API integration."""
  2 │
  3 │ import os
  4 │ from langchain_anthropic import ChatAnthropic
  5 │ ...
```

---

### 3.10 Progress Bars

**Objective**: Show progress for long operations (e.g., analyzing all priorities)

**Technical Approach**: Rich progress bar with task tracking

**Implementation**:
```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

def _analyze_all_priorities(self):
    """Analyze all priorities with progress bar."""
    priorities = self.editor.list_priorities()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=self.console
    ) as progress:
        task = progress.add_task(
            "[cyan]Analyzing priorities...",
            total=len(priorities)
        )

        for priority in priorities:
            # Analyze priority
            analysis = self._analyze_priority(priority)

            # Update progress
            progress.update(task, advance=1)

    self.console.print("[green]✅ Analysis complete![/]")
```

**User Experience**:
```
You: Analyze all priorities

⠋ Analyzing priorities... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 47% (7/15)
```

---

## 4. Implementation Plan

### Day 1: Streaming + Typing Indicators (8 hours)

**Morning (4h)**: Streaming responses
1. ✅ Add `anthropic` SDK to dependencies
2. ✅ Create `_display_streaming_response()` method
3. ✅ Modify `AIService` to support streaming mode
4. ✅ Update `_handle_natural_language()` to use streaming
5. ✅ Test with simple queries

**Afternoon (4h)**: Typing indicators + polish
1. ✅ Add typing indicator with Rich spinner
2. ✅ Test with various response lengths
3. ✅ Handle streaming errors gracefully
4. ✅ Add streaming toggle (environment variable)
5. ✅ Write unit tests

**Deliverables**:
- Streaming responses working end-to-end
- Typing indicator shows while waiting
- Tests pass

---

### Day 2: Advanced Input (8 hours)

**Morning (4h)**: Multi-line input + history
1. ✅ Add `prompt-toolkit` dependency
2. ✅ Replace `console.input()` with `PromptSession`
3. ✅ Configure Shift+Enter for multi-line
4. ✅ Add file-backed history (`~/.project_manager_history`)
5. ✅ Test multi-line input scenarios

**Afternoon (4h)**: Auto-completion
1. ✅ Create `ProjectManagerCompleter` class
2. ✅ Implement command completion
3. ✅ Implement priority name completion
4. ✅ Add file path completion
5. ✅ Test completion with Tab key

**Deliverables**:
- Multi-line input working (Shift+Enter)
- History navigation (↑/↓ arrows)
- Auto-completion (Tab key)
- Tests pass

---

### Day 3: Visual Polish + Persistence (6-8 hours)

**Morning (3h)**: Syntax highlighting + diffs
1. ✅ Add `Pygments` dependency
2. ✅ Implement `_display_response_with_syntax()`
3. ✅ Extract code blocks from markdown
4. ✅ Render code with syntax highlighting
5. ✅ Implement colored diff display

**Afternoon (3-5h)**: Session persistence + extras
1. ✅ Implement session save/restore
2. ✅ Add file preview functionality
3. ✅ Add progress bar for long operations
4. ✅ Final testing and polish
5. ✅ Update documentation

**Deliverables**:
- Enhanced syntax highlighting
- Colored diffs for changes
- Session persistence
- File previews
- Progress indicators
- Documentation updated

---

## 5. Testing Strategy

### 5.1 Unit Tests

**File**: `tests/cli/test_chat_interface_advanced.py`

```python
import pytest
from coffee_maker.cli.chat_interface import ChatSession

def test_streaming_response(mock_ai_service, mock_editor):
    """Test streaming response display."""
    session = ChatSession(mock_ai_service, mock_editor)

    # Mock streaming iterator
    def mock_stream():
        yield "Hello"
        yield " "
        yield "world"

    response = session._display_streaming_response(mock_stream())
    assert response == "Hello world"

def test_multiline_input():
    """Test multi-line input handling."""
    # Simulate Shift+Enter for newlines
    input_text = "Line 1\nLine 2\nLine 3"
    assert "\n" in input_text
    assert input_text.count("\n") == 2

def test_auto_completion(mock_editor):
    """Test auto-completion."""
    completer = ProjectManagerCompleter(mock_editor)

    from prompt_toolkit.document import Document
    doc = Document("/vi", cursor_position=3)

    completions = list(completer.get_completions(doc, None))
    assert any(c.text == "view" for c in completions)

def test_session_persistence(tmp_path):
    """Test session save/restore."""
    session_file = tmp_path / "session.json"

    # Create and save session
    session1 = ChatSession(ai_service, editor)
    session1.session_file = session_file
    session1.history = [{"role": "user", "content": "Hello"}]
    session1._save_session()

    # Load session
    session2 = ChatSession(ai_service, editor)
    session2.session_file = session_file
    session2._load_session()

    assert len(session2.history) == 1
    assert session2.history[0]["content"] == "Hello"
```

### 5.2 Integration Tests

**File**: `tests/manual_tests/test_chat_interface_integration.py`

```python
@pytest.mark.manual
def test_chat_full_session():
    """Manual test: Full chat session with all features.

    Run manually: pytest tests/manual_tests/test_chat_interface_integration.py -v

    This test is interactive and requires human verification.
    """
    from coffee_maker.cli.roadmap_cli import main

    # Start chat
    main(["chat"])

    # Verify:
    # 1. Streaming response works (text appears progressively)
    # 2. Multi-line input works (Shift+Enter)
    # 3. History navigation works (↑/↓)
    # 4. Auto-completion works (Tab)
    # 5. Syntax highlighting works (code blocks)
    # 6. Session persists (restart and verify history restored)
```

### 5.3 User Acceptance Testing

**Test Plan**:
1. ✅ Start chat: `poetry run project-manager chat`
2. ✅ Test streaming: Ask "Explain PRIORITY 1" → verify text streams
3. ✅ Test multi-line: Type "Add priority for\n<Shift+Enter>\nauthentication" → verify newline
4. ✅ Test history: Press ↑ → verify previous command shown
5. ✅ Test completion: Type "/v<Tab>" → verify "/view" completes
6. ✅ Test syntax: Ask for code example → verify highlighting
7. ✅ Test session: Exit and restart → verify history restored
8. ✅ Compare with claude-cli: Run both and verify similar UX

---

## 6. Dependencies

**New Dependencies to Add**:
```toml
# Add to pyproject.toml [tool.poetry.dependencies]
prompt-toolkit = "^3.0.47"       # Advanced CLI input (multi-line, history, completion)
Pygments = "^2.18.0"             # Syntax highlighting
anthropic = "^0.40.0"            # Streaming support (may already exist)
```

**Current Dependencies** (already in project):
```toml
rich = "^13.7.0"                 # Terminal UI (already present)
langchain-anthropic = "^0.3.0"   # AI service (already present)
```

**Total Size Impact**: ~5MB (acceptable for CLI tool)

---

## 7. Configuration

**Environment Variables**:
```bash
# Optional: Disable streaming for debugging
export PROJECT_MANAGER_NO_STREAMING=1

# Optional: Custom session directory
export PROJECT_MANAGER_SESSION_DIR=~/.custom_sessions

# Optional: History file location
export PROJECT_MANAGER_HISTORY_FILE=~/.custom_history
```

**Config File** (`~/.project_manager_config.json`):
```json
{
  "streaming": true,
  "typing_indicator": true,
  "auto_completion": true,
  "syntax_highlighting": true,
  "session_persistence": true,
  "history_max_entries": 1000,
  "theme": "monokai"
}
```

---

## 8. Success Criteria

**Acceptance Criteria** (from US-006):
- [x] Basic chat interface exists ✅ (already done)
- [x] Rich terminal UI with markdown ✅ (already done)
- [x] Command routing ✅ (already done)
- [ ] **Streaming responses** 🎯 (Day 1)
- [ ] **Syntax highlighting** 🎯 (Day 3)
- [ ] **Multi-line input** 🎯 (Day 2)
- [ ] **Input history** 🎯 (Day 2)
- [ ] **Auto-completion** 🎯 (Day 2)
- [ ] **Typing indicators** 🎯 (Day 1)
- [ ] **File preview** 🎯 (Day 3)
- [ ] **Progress bars** 🎯 (Day 3)
- [ ] **Colored diff** 🎯 (Day 3)
- [ ] **Session persistence** 🎯 (Day 3)

**Quality Bar** (matches claude-cli):
- ✅ Response latency <100ms for first chunk
- ✅ Smooth streaming (no stuttering)
- ✅ Multi-line input feels natural
- ✅ History navigation is instant
- ✅ Auto-completion is smart and fast
- ✅ Code is readable with syntax highlighting
- ✅ Session restore is seamless

**User Satisfaction**:
- User can complete common tasks as easily as with claude-cli
- User feels the interface is professional and polished
- User prefers project-manager chat over basic CLI commands

---

## 9. Risks and Mitigations

**Risk 1**: Anthropic SDK streaming may not work as expected
**Mitigation**: Test streaming early (Day 1 morning), fallback to blocking if needed

**Risk 2**: prompt-toolkit may conflict with Rich
**Mitigation**: Test both libraries together early, use Rich for output only

**Risk 3**: Session persistence may cause file corruption
**Mitigation**: Use atomic writes, add error handling, test with corrupted files

**Risk 4**: Auto-completion may be slow with many priorities
**Mitigation**: Cache priority list, limit completions to 50 results

**Risk 5**: Syntax highlighting may fail for unknown languages
**Mitigation**: Fallback to plain text, add error handling

---

## 10. Future Enhancements (Post-MVP)

**Phase 2** (after US-006 complete):
- **Voice input**: Speak commands instead of typing
- **Image display**: Show charts/diagrams in terminal (using Rich)
- **Notifications**: Desktop notifications for important events
- **Themes**: Customizable color schemes
- **Shortcuts**: Configurable keyboard shortcuts
- **Plugins**: Extension system for custom commands
- **Web UI**: Browser-based alternative to terminal

**Community Requests**:
- Export chat history to markdown
- Share chat sessions with team members
- Integrate with Slack/Discord for remote collaboration

---

## 11. Success Metrics

**Quantitative**:
- User spends >80% of time in chat vs CLI commands
- Average session duration >10 minutes (indicates engagement)
- <5% of sessions end in errors
- 100% of features tested and working

**Qualitative**:
- User feedback: "Feels as good as claude-cli"
- User reports increased productivity
- User recommends project-manager to others

---

## 12. Conclusion

This specification provides a complete roadmap for transforming `project-manager chat` into a professional, claude-cli-quality interface. The implementation is feasible within 2-3 days with clear deliverables and testing strategy.

**Next Steps**:
1. Get approval on specification
2. Add dependencies to pyproject.toml
3. Start Day 1 implementation (streaming + typing indicators)
4. Test continuously throughout development
5. Deploy and gather user feedback

**Questions for Review**:
1. Are streaming responses required, or can we start with typing indicators only?
2. Should we support custom themes from day 1, or defer to Phase 2?
3. Do we need Windows compatibility testing, or Mac/Linux only?
4. Should session files be encrypted for sensitive projects?

---

**Document Version**: 1.0
**Last Updated**: 2025-10-10
**Status**: Ready for Implementation
**Approved By**: (Awaiting user approval)
