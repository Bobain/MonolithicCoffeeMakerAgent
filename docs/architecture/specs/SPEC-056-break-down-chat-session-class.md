# SPEC-056: Break Down ChatSession Class

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: code-searcher refactoring_priorities_2025-10-17.md (Priority 2.1)
**Priority**: MEDIUM
**Impact**: MEDIUM (Maintainability)

---

## Problem Statement

### Current State

`ChatSession` class in `chat_interface.py` has **31 methods**, violating the Single Responsibility Principle:

- **Rendering** (13 methods): `_format_*`, `_render_*`, `_display_*`
- **Command Handling** (12 methods): `cmd_*`, `_parse_command`
- **Core Logic** (6 methods): `start()`, `_run_loop()`, etc.

### code-searcher Finding

> **Class Complexity: ChatSession**
> - Location: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/chat_interface.py`
> - Methods: 31 (Target: <15)
> - Issue: Mixed concerns (rendering + commands + orchestration)
> - Recommendation: Apply mixin pattern to split into ChatRenderer and ChatCommandHandler
> - Effort: 8 hours
> - Impact: MEDIUM (easier testing, reduced complexity)

### Why This Matters

- **Testing Complexity**: Hard to test rendering separately from commands
- **Cognitive Load**: Understanding 31 methods requires mental overhead
- **Maintenance**: Changes to rendering affect command logic
- **Violation of SRP**: Single class has 3+ responsibilities

**Goal**: Reduce ChatSession from 31 to ~8 methods using mixin pattern

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Apply **mixin pattern** (per ADR-001) to separate concerns:

1. **ChatRendererMixin**: All rendering logic (13 methods)
2. **ChatCommandHandlerMixin**: All command logic (12 methods)
3. **ChatSession**: Orchestration only (~8 methods)

### Architecture

```python
# BEFORE (31 methods in one class)
class ChatSession:
    # Rendering methods (13)
    def format_status(self): pass
    def format_roadmap(self): pass
    def _render_priority(self): pass
    # ... 10 more rendering methods

    # Command methods (12)
    def cmd_add(self): pass
    def cmd_view(self): pass
    def _parse_command(self): pass
    # ... 9 more command methods

    # Core methods (6)
    def start(self): pass
    def _run_loop(self): pass
    # ... 4 more core methods


# AFTER (using mixins)
class ChatRendererMixin:
    """Handles all rendering concerns."""
    def format_status(self): pass
    def format_roadmap(self): pass
    def _render_priority(self): pass
    # ... 10 more rendering methods (13 total)


class ChatCommandHandlerMixin:
    """Handles all command parsing and execution."""
    def cmd_add(self, args): pass
    def cmd_view(self, args): pass
    def _parse_command(self, input): pass
    # ... 9 more command methods (12 total)


class ChatSession(ChatRendererMixin, ChatCommandHandlerMixin):
    """Core chat session orchestration (8 methods)."""
    def __init__(self, ai_service, editor):
        self.ai_service = ai_service
        self.editor = editor

    def start(self): pass
    def _run_loop(self): pass
    # ... 6 more core methods (8 total)
```

**Benefits**:
- **Testability**: Test rendering and commands separately
- **Reduced Complexity**: Each class <15 methods
- **Clear Separation**: Each mixin has one responsibility
- **Easier Maintenance**: Changes to rendering don't affect commands

---

## Component Design

### 1. ChatRendererMixin (13 methods)

**Responsibilities**:
- Format status displays
- Render roadmap information
- Display priority details
- Format error/success messages

**Key Methods**:
```python
class ChatRendererMixin:
    """Handles all rendering concerns."""

    def format_status(self) -> str:
        """Format developer status display."""
        pass

    def format_roadmap(self) -> str:
        """Format ROADMAP.md for display."""
        pass

    def _render_priority(self, priority: dict) -> str:
        """Render a single priority."""
        pass

    def _format_notification(self, notif: dict) -> str:
        """Format a notification for display."""
        pass

    def _display_help(self):
        """Display help text."""
        pass

    # ... 8 more rendering methods
```

### 2. ChatCommandHandlerMixin (12 methods)

**Responsibilities**:
- Parse user commands
- Execute command handlers
- Validate command arguments
- Return command results

**Key Methods**:
```python
class ChatCommandHandlerMixin:
    """Handles all command parsing and execution."""

    def _parse_command(self, user_input: str) -> tuple[str, list[str]]:
        """
        Parse user input into command and arguments.

        Returns:
            (command_name, arguments)
        """
        pass

    def cmd_add(self, args: list[str]) -> str:
        """Add a new priority to ROADMAP."""
        pass

    def cmd_view(self, args: list[str]) -> str:
        """View ROADMAP or specific priority."""
        pass

    def cmd_status(self, args: list[str]) -> str:
        """Show developer status."""
        pass

    def cmd_help(self, args: list[str]) -> str:
        """Display help message."""
        pass

    # ... 7 more command methods
```

### 3. ChatSession (8 methods)

**Responsibilities**:
- Initialize chat session
- Run main chat loop
- Coordinate rendering and commands
- Handle session lifecycle

**Key Methods**:
```python
class ChatSession(ChatRendererMixin, ChatCommandHandlerMixin):
    """
    Core chat session orchestration.

    Composes ChatRendererMixin (rendering) and ChatCommandHandlerMixin (commands).
    """

    def __init__(self, ai_service: AIService, editor: RoadmapEditor):
        """Initialize chat session with dependencies."""
        self.ai_service = ai_service
        self.editor = editor
        self.running = False

    def start(self) -> int:
        """Start the chat session."""
        pass

    def _run_loop(self):
        """Main chat loop (reads input, dispatches commands)."""
        pass

    def _handle_command(self, command: str, args: list[str]) -> str:
        """Dispatch command to appropriate handler."""
        pass

    def _handle_user_message(self, message: str) -> str:
        """Send message to AI and get response."""
        pass

    def stop(self):
        """Stop the chat session."""
        pass

    # ... 3 more core methods (8 total)
```

---

## Technical Details

### File Structure

**Current**:
```
coffee_maker/cli/
└── chat_interface.py  (800 lines, 31 methods)
```

**After Refactoring**:
```
coffee_maker/cli/
├── chat_interface.py          (Main ChatSession class, 200 lines)
├── chat_renderer_mixin.py     (Rendering logic, 250 lines)
└── chat_command_mixin.py      (Command logic, 350 lines)
```

### Migration Strategy

**Phase 1: Create Mixin Files** (1 hour)
```bash
# Create new files
touch coffee_maker/cli/chat_renderer_mixin.py
touch coffee_maker/cli/chat_command_mixin.py
```

**Phase 2: Extract Rendering Methods** (2 hours)
1. Copy all `_format_*`, `_render_*`, `_display_*` methods to `ChatRendererMixin`
2. Add necessary imports
3. Test rendering methods in isolation

**Phase 3: Extract Command Methods** (2 hours)
1. Copy all `cmd_*` and `_parse_command` methods to `ChatCommandHandlerMixin`
2. Add necessary imports
3. Test command methods in isolation

**Phase 4: Update ChatSession** (2 hours)
1. Make ChatSession inherit from both mixins
2. Remove extracted methods from ChatSession
3. Verify all tests pass

**Phase 5: Testing** (1 hour)
1. Run full test suite
2. Manual testing of chat interface
3. Fix any import or reference issues

**Total**: 8 hours

### Data Flow

```
User Input
    ↓
ChatSession._run_loop()
    ↓
ChatSession._handle_command() [dispatches]
    ↓
ChatCommandHandlerMixin.cmd_*() [executes]
    ↓
ChatRendererMixin.format_*() [renders]
    ↓
Display to User
```

---

## Data Structures

No new data structures needed. Existing structures remain:
- `AIService` interface
- `RoadmapEditor` class
- Command arguments (list of strings)

---

## Testing Strategy

### Unit Tests

**New Test Files**:
```
tests/unit/cli/
├── test_chat_renderer_mixin.py     # NEW: Test rendering logic
├── test_chat_command_mixin.py      # NEW: Test command logic
└── test_chat_interface.py          # UPDATE: Test orchestration
```

**Example Tests**:
```python
# test_chat_renderer_mixin.py
class TestChatRendererMixin:
    def test_format_status(self):
        """Test status formatting."""
        renderer = ChatRendererMixin()
        renderer.ai_service = mock_ai_service

        status = renderer.format_status()

        assert "Developer Status" in status
        assert "Current Priority" in status

    def test_render_priority(self):
        """Test priority rendering."""
        renderer = ChatRendererMixin()

        priority = {"name": "PRIORITY 5", "title": "Test"}
        result = renderer._render_priority(priority)

        assert "PRIORITY 5" in result
        assert "Test" in result


# test_chat_command_mixin.py
class TestChatCommandHandlerMixin:
    def test_parse_command_simple(self):
        """Test parsing simple command."""
        handler = ChatCommandHandlerMixin()

        cmd, args = handler._parse_command("/add New Priority")

        assert cmd == "add"
        assert args == ["New", "Priority"]

    def test_cmd_add(self):
        """Test add command execution."""
        handler = ChatCommandHandlerMixin()
        handler.editor = mock_editor

        result = handler.cmd_add(["New", "Priority"])

        assert "added" in result.lower()
```

### Integration Tests

**Update Existing**:
```python
# tests/ci_tests/test_chat_interface.py
def test_chat_session_integration():
    """Test full chat session workflow."""
    session = ChatSession(ai_service, editor)

    # Should inherit from both mixins
    assert hasattr(session, 'format_status')  # From renderer
    assert hasattr(session, 'cmd_add')        # From commands
    assert hasattr(session, 'start')          # Core method
```

### Manual Testing

```bash
# Start chat session
poetry run project-manager chat

# Test commands
/add New Priority
/view
/status
/help
```

---

## Rollout Plan

### Week 1: Implementation (6 hours)
- **Day 1**: Create mixin files, extract rendering methods (3 hours)
- **Day 2**: Extract command methods (2 hours)
- **Day 2**: Update ChatSession to use mixins (1 hour)

### Week 1: Testing (2 hours)
- **Day 3**: Write unit tests for mixins (1 hour)
- **Day 3**: Manual testing and bug fixes (1 hour)

**Total Timeline**: 1 week (8 hours actual work)

---

## Risks & Mitigations

### Risk 1: Breaking Existing Functionality
**Likelihood**: MEDIUM
**Impact**: HIGH
**Mitigation**:
- Keep existing tests passing
- Manual testing of all chat commands
- Gradual migration (extract one mixin at a time)

### Risk 2: Import Circular Dependencies
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- Mixins don't import each other
- ChatSession imports both mixins
- Use dependency injection for shared services

### Risk 3: Method Name Conflicts
**Likelihood**: LOW
**Impact**: LOW
**Mitigation**:
- Review method names before extraction
- Use descriptive names (cmd_*, format_*, _render_*)
- Python's MRO handles conflicts gracefully

---

## Success Criteria

### Quantitative
- ✅ ChatSession reduced to ≤8 methods
- ✅ ChatRendererMixin contains all 13 rendering methods
- ✅ ChatCommandHandlerMixin contains all 12 command methods
- ✅ All existing tests pass
- ✅ No new linting/formatting errors
- ✅ Test coverage maintained (≥70%)

### Qualitative
- ✅ Easier to test rendering vs commands
- ✅ Clearer separation of concerns
- ✅ Easier to add new commands (just extend mixin)
- ✅ Easier to add new rendering formats

---

## Related Work

### Depends On
- ADR-001: Mixin pattern (already implemented)

### Enables
- Easier to add new chat commands
- Easier to change rendering (e.g., rich library)
- Better test coverage of chat functionality

### Related Specs
- **SPEC-050**: CLI modularization (similar pattern)
- **SPEC-052**: Error handling (will apply to chat commands)

---

## Future Enhancements

### After This Refactor
1. **Rich Rendering**: Use rich library for better terminal output
2. **Command Plugins**: Dynamically load chat commands
3. **Async Commands**: Support async command execution
4. **Chat History**: Add session history persistence

---

## Appendix A: Method Distribution

### Before (31 methods in ChatSession)

**Rendering Methods** (13):
- `format_status()`
- `format_roadmap()`
- `_render_priority()`
- `_display_help()`
- `_format_notification()`
- `_render_metrics()`
- `_display_calendar()`
- `_format_summary()`
- `_render_dev_report()`
- `_display_error()`
- `_display_success()`
- `_format_list()`
- `_render_details()`

**Command Methods** (12):
- `_parse_command()`
- `cmd_add()`
- `cmd_view()`
- `cmd_status()`
- `cmd_help()`
- `cmd_metrics()`
- `cmd_calendar()`
- `cmd_summary()`
- `cmd_notifications()`
- `cmd_respond()`
- `cmd_exit()`
- `cmd_clear()`

**Core Methods** (6):
- `__init__()`
- `start()`
- `_run_loop()`
- `_handle_command()`
- `_handle_user_message()`
- `stop()`

### After (using mixins)

**ChatRendererMixin**: 13 methods
**ChatCommandHandlerMixin**: 12 methods
**ChatSession**: 8 methods (includes 2 orchestration methods)

**Total**: Same 31 methods, but organized into 3 classes

---

## Appendix B: Complexity Metrics

### Before
```python
Class ChatSession:
    Methods: 31 ❌ (target: <15)
    Lines: ~800
    Cyclomatic Complexity: HIGH
```

### After
```python
Class ChatRendererMixin:
    Methods: 13 ✅
    Lines: ~250
    Cyclomatic Complexity: MEDIUM

Class ChatCommandHandlerMixin:
    Methods: 12 ✅
    Lines: ~350
    Cyclomatic Complexity: MEDIUM

Class ChatSession:
    Methods: 8 ✅
    Lines: ~200
    Cyclomatic Complexity: LOW
```

**Improvement**: Each class now <15 methods ✅

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 8 hours
**Actual Effort**: TBD (track during implementation)
