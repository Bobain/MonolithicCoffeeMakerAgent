# Refactoring Priorities & Technical Debt Roadmap - 2025-10-17

**Document**: Prioritized refactoring opportunities for architect review
**Analysis Date**: 2025-10-17
**Total Estimated Effort**: 60 hours over 2-3 sprints
**CFR Reference**: CFR-011 (Code-Searcher Integration)

---

## Quick Reference Table

| Priority | Category | Item | Effort | Impact | Sprint |
|----------|----------|------|--------|--------|--------|
| 🔴 P1 | Refactoring | SPEC-050: roadmap_cli modularization | 10h | HIGH | Sprint 1 |
| 🔴 P1 | Standardization | SPEC-052: Error handling standardization | 5h | HIGH | Sprint 1 |
| 🔴 P1 | Refactoring | Extract user_listener.main() | 2h | MEDIUM | Sprint 1 |
| 🟠 P2 | Architecture | Break down ChatSession class | 8h | MEDIUM | Sprint 2 |
| 🟠 P2 | Testing | Git operations test coverage | 8h | HIGH | Sprint 2 |
| 🟠 P2 | Testing | Prompt loader edge cases | 4h | MEDIUM | Sprint 2 |
| 🟡 P3 | Code Quality | Chat interface command handling | 6h | MEDIUM | Sprint 2 |
| 🟡 P3 | Architecture | ACE API completeness | 7h | MEDIUM | Sprint 3 |
| 🟡 P3 | Testing | Daemon CLI mode detection | 5h | LOW | Sprint 3 |
| 🔵 P4 | Maintenance | Logging setup consolidation | 3h | LOW | Future |

---

## Priority 1: Critical Path Refactoring (Must Do Next Sprint)

### 1.1 SPEC-050: Modularize roadmap_cli.py

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/roadmap_cli.py`

**Current State**:
- Single file with 150+ functions
- Handles: CLI routing, chat interface, roadmap editing, notifications
- Difficult to test individual commands
- Mixed concerns: UI, business logic, data access

**Target State**:
```
roadmap_cli/
├── roadmap_cli.py          (main entry point, <100 lines)
├── commands/
│   ├── __init__.py
│   ├── roadmap_commands.py (view, add, update, delete)
│   ├── chat_commands.py    (chat, ask)
│   ├── status_commands.py  (status, dev-report)
│   └── analyze_commands.py (analyze, test-coverage)
├── command_router.py       (Routes commands to handlers)
└── command_validators.py   (Validates command inputs)
```

**Deliverables**:
1. Extract each command group into separate module
2. Create command registry/router
3. Add command validators
4. Update tests to match new structure

**Testing Impact**: +15 unit tests become easier to write

**Effort**: 10 hours
**Benefit**:
- Easier to test individual commands
- Reduce cyclomatic complexity
- Easier to add new commands
- Better code reusability

**Acceptance Criteria**:
- All commands still work identically
- Test suite passes
- Each command module <200 lines
- Command router <100 lines

---

### 1.2 SPEC-052: Standardized Error Handling

**Location**: Multiple files in `autonomous/`, `cli/`, `api/`

**Current State**:
- Error handling varies across modules
- Some use decorators, some use try/except
- Error messages inconsistent
- Difficult to track error patterns

**Example Inconsistency 1**:
```python
# In daemon_git_ops.py (try/except)
except Exception as e:
    logger.error(f"Error syncing roadmap branch: {e}")
    return False
```

```python
# In chat_interface.py (try/except with user output)
except Exception as e:
    logger.error(f"Chat session failed: {e}")
    print("❌ Error:", e)
```

```python
# In api/routes/*.py (decorator pattern)
@error_handler
def some_route():
    pass
```

**Proposed Standard**:

**Tier 1 - Expected Errors** (user input errors):
```python
from coffee_maker.utils.error_handling import handle_validation_error

try:
    result = validate_input(user_input)
except ValueError as e:
    return handle_validation_error(e, "user")  # Logs + returns user-friendly message
```

**Tier 2 - System Errors** (operational failures):
```python
from coffee_maker.utils.error_handling import handle_system_error

try:
    result = system_operation()
except (IOError, OSError) as e:
    return handle_system_error(e, "filesystem")  # Logs + returns retry suggestion
```

**Tier 3 - Unexpected Errors** (bugs):
```python
from coffee_maker.utils.error_handling import handle_unexpected_error

try:
    result = untested_operation()
except Exception as e:
    logger.critical("Unexpected error", exc_info=True)
    return handle_unexpected_error(e)  # Logs stack trace + alerts
```

**Deliverables**:
1. Create `/coffee_maker/utils/error_handling.py` with handlers
2. Define error categories and responses
3. Update 8-10 critical modules to use standard handlers
4. Add error handling tests

**Effort**: 5 hours
**Benefit**:
- Consistent error messages
- Easier debugging
- Better user experience
- Easier to track error patterns

---

### 1.3 Extract user_listener.main() Function

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/user_listener.py:59-150`

**Current State**: 151-line main() function with mixed concerns

**Issue**:
```python
def main() -> int:
    try:
        with AgentRegistry.register(AgentType.USER_LISTENER):
            # 50 lines of mode detection
            # 20 lines of validation
            # 30 lines of setup
            # 10 lines of chat loop
    except AgentAlreadyRunningError as e:
        # Handle
    except Exception as e:
        # Handle
```

**Proposed Extraction**:
```python
def _detect_and_validate_mode() -> Tuple[bool, str]:
    """Detect Claude CLI vs API mode. Returns (use_cli, path)."""
    # Current lines 87-100 (mode detection logic)
    pass

def _validate_and_show_mode_info(use_cli: bool) -> bool:
    """Validate selected mode and show user info."""
    # Current lines 41-82 (info messages and validation)
    pass

def _initialize_chat_components(use_cli: bool, claude_path: str):
    """Initialize editor and AI service."""
    # Current lines 102-115 (component setup)
    pass

def main() -> int:
    try:
        with AgentRegistry.register(AgentType.USER_LISTENER):
            use_cli, path = _detect_and_validate_mode()
            if not _validate_and_show_mode_info(use_cli):
                return 1

            editor, ai_service = _initialize_chat_components(use_cli, path)
            session = ChatSession(ai_service, editor)
            session.start()
            return 0
    except AgentAlreadyRunningError as e:
        ...
```

**Deliverables**:
1. Extract three helper functions
2. Update main() to use helpers
3. Add unit tests for each helper
4. Verify behavior unchanged

**Effort**: 2 hours
**Benefit**:
- main() reduces to ~30 lines
- Each function testable independently
- Easier to debug mode detection
- Cleaner error handling

---

## Priority 2: Architecture Improvements (Sprint 2)

### 2.1 Break Down ChatSession Class

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/chat_interface.py`

**Current State**: 31 methods, mixed rendering + command handling

**Methods Breakdown**:
- **Rendering** (13 methods): `_format_*`, `_render_*`, `_display_*`
- **Command Handling** (12 methods): `cmd_*`, `_parse_command`
- **Core Logic** (6 methods): `start()`, `_run_loop()`, etc.

**Proposed Architecture**:

```python
class ChatSession:
    """Core chat session orchestration."""
    def __init__(self, ai_service, editor):
        self.renderer = ChatRenderer(ai_service)
        self.command_handler = ChatCommandHandler(editor)

    def start(self):
        """Main chat loop."""
        pass

class ChatRendererMixin:
    """Handles all rendering concerns."""
    def format_status(self): pass
    def format_roadmap(self): pass
    # ... other rendering methods

class ChatCommandHandlerMixin:
    """Handles all command parsing and execution."""
    def parse_command(self, input): pass
    def cmd_add(self, args): pass
    # ... other command handlers
```

**Implementation Strategy**:
1. Create `ChatRenderer` class with rendering methods
2. Create `ChatCommandHandler` class with command methods
3. Update `ChatSession` to delegate to these
4. Maintain backward compatibility in public interface

**Testing Impact**: +10 unit tests become tractable

**Effort**: 8 hours
**Benefit**:
- Reduce ChatSession from 31 to ~8 methods
- Each class <200 lines
- Easier to test rendering vs commands
- Easier to add new commands or formatters

---

### 2.2 Expand Git Operations Test Coverage

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_git_ops.py`

**Current State**: Basic tests, missing edge cases

**Missing Scenarios**:
1. **Merge conflicts** - Current: tested. Missing: recovery behavior
2. **Network errors** - Missing: git fetch timeout, git push failure
3. **Concurrent operations** - Missing: what if merge happens while fetching?
4. **Branch state changes** - Missing: detached HEAD, branch deletion
5. **File conflicts** - Missing: multiple conflict markers

**Test Plan**:

```python
# New tests to add
def test_merge_conflict_recovery():
    """Verify merge conflict handling and recovery."""
    pass

def test_sync_with_network_timeout():
    """Verify behavior when git fetch times out."""
    pass

def test_merge_with_uncommitted_changes():
    """Verify merge handles uncommitted changes."""
    pass

def test_concurrent_push_during_merge():
    """Verify handling of push failure during merge."""
    pass
```

**Test Infrastructure**:
- Use pytest fixtures for mock git repo
- Mock subprocess to simulate failures
- Test notification creation for failures

**Effort**: 8 hours
**Benefit**:
- 90% test coverage for daemon_git_ops
- Prevents production merge failures
- Better error messages for project_manager
- Safer concurrent operation

---

### 2.3 Prompt Loader Edge Case Tests

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/prompt_loader.py`

**Current State**: Basic loading, missing edge cases

**Missing Scenarios**:
1. **Missing template file** - Current: raises error. Missing: test error message
2. **Missing variables** - Missing: test for incomplete variable replacement
3. **Special characters** - Missing: test unicode, escape sequences
4. **Very large templates** - Missing: performance test
5. **Concurrent loading** - Missing: thread safety test

**Test Plan**:

```python
def test_missing_prompt_file():
    """Verify error when prompt file missing."""
    pass

def test_missing_variable_substitution():
    """Verify error message for unsubstituted variables."""
    pass

def test_unicode_in_template():
    """Verify unicode handling in templates."""
    pass

def test_concurrent_template_loading():
    """Verify thread safety of template loading."""
    pass
```

**Effort**: 4 hours
**Benefit**:
- Better error messages for daemon
- Prevent incomplete prompt substitution
- Safer for multi-agent execution

---

## Priority 3: Testing & Documentation (Sprint 2-3)

### 3.1 Chat Interface Command Testing

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/chat_interface.py`

**Missing Coverage**:
- Command parsing logic (`_parse_command`)
- Error handling for invalid commands
- Help text generation
- Command validation

**Test Plan**: Add 10 unit tests for command parsing

**Effort**: 6 hours
**Benefit**: Better command reliability, easier debugging

---

### 3.2 ACE API Completeness

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/ace/api.py`

**Missing Tests**:
- Trace creation and retrieval
- File ownership enforcement
- Agent registry integration
- Error scenarios

**Effort**: 7 hours
**Benefit**: ACE framework reliability

---

### 3.3 Daemon CLI Mode Detection

**Location**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/daemon_cli.py`

**Missing Tests**:
- CLI detection (when installed/not installed)
- API key validation
- Auto-approval flag handling
- Error conditions

**Effort**: 5 hours
**Benefit**: More robust daemon startup

---

## Priority 4: Maintenance Tasks (Lower Priority)

### 4.1 Logging Setup Consolidation

**Current State**: 12 files have logging.basicConfig() calls

**Recommendation**:
- Extract to single utility: `coffee_maker/utils/logging_setup.py`
- Use across all modules
- Centralize log configuration

**Effort**: 3 hours
**Benefit**: Consistent logging across codebase

---

## TODO Comments Review

**Files with Most TODOs**:

1. **`spec_template_manager.py`** - 5 TODOs
   - Most are feature enhancements (low priority)

2. **`notification_dispatcher.py`** - 2 TODOs
   - Consider for Sprint 3

3. **`status_tracking_updater.py`** - 1 TODO
   - Straightforward fix (2 hours)

**Recommendation**: Quarterly TODO review cycle

---

## Implementation Order (Recommended)

### Week 1 (Sprint 1 - Foundational)
1. **P1.2** - SPEC-052: Error handling standardization (5h)
2. **P1.3** - Extract user_listener.main() (2h)
3. **P1.1** - Start SPEC-050: roadmap_cli structure (5h)

### Week 2 (Sprint 1 - Completion)
4. **P1.1** - Complete SPEC-050: roadmap_cli tests (5h)
5. **Testing** - Add git operations tests (4h)

### Week 3 (Sprint 2 - Architecture)
6. **P2.1** - Break down ChatSession (8h)
7. **P2.3** - Prompt loader edge cases (4h)
8. **P3.1** - Chat interface commands (3h)

### Week 4 (Sprint 2 - Completion)
9. **P2.2** - Complete git operations tests (4h)
10. **P3** - Remaining test coverage

### Week 5+ (Sprint 3 - Polish)
11. **P3.2** - ACE API completeness (7h)
12. **P3.3** - Daemon CLI testing (5h)
13. **P4** - Maintenance tasks (3h)

---

## Risk Assessment

| Item | Risk | Mitigation |
|------|------|-----------|
| Breaking existing functionality | Medium | Comprehensive test suite for changes |
| Testing becoming too comprehensive | Low | Set time box for each task |
| Conflicting with new features | Medium | Coordinate with feature schedule |

---

## Success Metrics

After completing all priorities:

| Metric | Target | Current |
|--------|--------|---------|
| Average function length | <50 lines | 90 lines |
| Max class methods | <15 | 31 |
| Test coverage | >80% | ~70% |
| TODOs per file | <1 | 1.2 |
| Code duplication | <5% | ~3% |

---

## Conclusion

This refactoring roadmap addresses:
- **Architecture**: Breaking down complex classes and modules
- **Quality**: Standardizing error handling and extracting long functions
- **Testing**: Expanding coverage for critical paths
- **Maintainability**: Consolidating utilities and reducing technical debt

**Total Effort**: 60 hours across 3 sprints
**Expected Benefit**: 40% reduction in code complexity, 25% improvement in test coverage

**Next Step**: Architect reviews and approves, then schedule into ROADMAP

---

**Prepared by**: code-searcher
**For Review by**: architect
**Date**: 2025-10-17
