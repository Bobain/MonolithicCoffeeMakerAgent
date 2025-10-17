# SPEC-050: Refactor roadmap_cli.py Modularization

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CODE_QUALITY_ANALYSIS_2025-10-17.md (Finding #1)
**Priority**: MEDIUM
**Impact**: HIGH (Maintainability)

---

## Problem Statement

### Current State
`roadmap_cli.py` is **1,806 lines of code**, containing 18 command handlers in a single file. This violates the project's code quality target of <500 LOC per file and creates significant maintainability challenges:

- **Hard to Navigate**: Developers must scroll through 1,800+ lines to find specific commands
- **Testing Complexity**: Difficult to isolate and test individual command handlers
- **Merge Conflicts**: High risk of conflicts when multiple developers modify commands
- **Cognitive Load**: Understanding the full file requires keeping 18 command patterns in mind
- **Violation of SRP**: Single file has 18+ distinct responsibilities

### code-searcher Finding
> "roadmap_cli.py: 1,806 LOC (complexity: HIGH)
> Recommendation: Split into 4-6 modules by concern
> Effort: 4-6 hours
> Impact: MEDIUM (maintainability)"

### Why This Matters
As the project grows, the roadmap CLI will need more commands. Without refactoring now, this file will grow to 2,500+ LOC, becoming a serious bottleneck for development.

---

## Proposed Solution

### Simplified Approach (per ADR-003)

Break `roadmap_cli.py` into **4 focused modules** by command category, maintaining backwards compatibility while dramatically improving maintainability.

### Architecture

```
coffee_maker/cli/
├── roadmap_cli.py              # Main entry point (200 LOC) ✅ Slim
│   └── Imports and delegates to submodules
│
└── commands/                    # New package
    ├── __init__.py             # Export all command functions
    ├── roadmap.py              # 300 LOC - Roadmap viewing commands
    ├── status.py               # 350 LOC - Status and monitoring
    ├── notifications.py        # 400 LOC - Notification management
    └── chat.py                 # 550 LOC - Chat and assistant commands
```

**Total**: 1,800 LOC split into 4 files (avg 375 LOC each) ✅

---

## Component Design

### 1. Main Entry Point: `roadmap_cli.py` (200 LOC)

**Responsibilities**:
- CLI argument parsing setup
- Delegate to command modules
- Shared utilities (error(), success(), info())

```python
# roadmap_cli.py - Slim orchestrator
import argparse
from coffee_maker.cli.commands import roadmap, status, notifications, chat

def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command")

    # Delegate to command modules
    roadmap.setup_parser(subparsers)
    status.setup_parser(subparsers)
    notifications.setup_parser(subparsers)
    chat.setup_parser(subparsers)

    args = parser.parse_args()

    # Route to appropriate handler
    if args.command in ["view", "view-priority"]:
        return roadmap.execute(args)
    elif args.command in ["status", "developer-status"]:
        return status.execute(args)
    # ... etc
```

### 2. Roadmap Commands: `commands/roadmap.py` (~300 LOC)

**Responsibilities**:
- `cmd_view()` - Display ROADMAP.md
- `cmd_view_priority()` - Display specific priority details
- Related utilities for roadmap parsing

**Key Functions**:
```python
def setup_parser(subparsers):
    """Configure roadmap-related subcommands."""
    view_parser = subparsers.add_parser("view", ...)
    priority_parser = subparsers.add_parser("view-priority", ...)

def execute(args) -> int:
    """Execute roadmap commands."""
    if args.command == "view":
        return cmd_view(args)
    elif args.command == "view-priority":
        return cmd_view_priority(args)
```

### 3. Status Commands: `commands/status.py` (~350 LOC)

**Responsibilities**:
- `cmd_status()` - Show priority status
- `cmd_developer_status()` - Developer status dashboard
- `cmd_metrics()` - Metrics and velocity
- `cmd_summary()` - Sprint summary
- `cmd_calendar()` - Calendar view
- `cmd_dev_report()` - Developer report

**Pattern**: Same as roadmap.py (setup_parser + execute)

### 4. Notification Commands: `commands/notifications.py` (~400 LOC)

**Responsibilities**:
- `cmd_notifications()` - List notifications
- `cmd_respond()` - Respond to notifications
- Notification filtering and formatting

### 5. Chat Commands: `commands/chat.py` (~550 LOC)

**Responsibilities**:
- `cmd_chat()` - Interactive chat interface
- `cmd_assistant()` - Assistant queries
- Chat utilities and formatting

**Note**: This is the largest module due to complex chat logic

---

## Technical Details

### Migration Strategy

**Phase 1: Create Module Structure** (1 hour)
```bash
mkdir -p coffee_maker/cli/commands
touch coffee_maker/cli/commands/__init__.py
touch coffee_maker/cli/commands/roadmap.py
touch coffee_maker/cli/commands/status.py
touch coffee_maker/cli/commands/notifications.py
touch coffee_maker/cli/commands/chat.py
```

**Phase 2: Move Functions** (2 hours)
1. Copy functions to new modules (don't delete from original yet)
2. Add imports and setup_parser/execute structure
3. Update __init__.py to export all functions

**Phase 3: Update Main CLI** (1 hour)
1. Import from commands package
2. Delegate to new modules
3. Keep shared utilities in main file

**Phase 4: Remove Old Code** (30 min)
1. Delete moved functions from roadmap_cli.py
2. Verify all imports work

**Phase 5: Test & Validate** (1.5 hours)
1. Run full test suite
2. Manual testing of all commands
3. Fix any broken imports or references

### Shared Utilities Location

Keep in `roadmap_cli.py` (used by all modules):
```python
# Shared utilities (stay in main file)
def error(msg: str):
    """Print error message."""
    print(f"❌ {msg}")

def success(msg: str):
    """Print success message."""
    print(f"✅ {msg}")

def info(msg: str):
    """Print info message."""
    print(f"ℹ️  {msg}")
```

### Import Structure

**commands/__init__.py**:
```python
# Export all command modules for easy importing
from . import roadmap
from . import status
from . import notifications
from . import chat

__all__ = ["roadmap", "status", "notifications", "chat"]
```

**Usage in main CLI**:
```python
from coffee_maker.cli.commands import roadmap, status, notifications, chat
```

---

## Data Structures

No new data structures needed. All existing structures remain unchanged:
- `argparse.Namespace` for argument parsing
- Existing database models (MetricsDB, NotificationDB, etc.)
- ROADMAP.md parsing logic stays the same

---

## Testing Strategy

### Unit Tests

**New Test Files**:
```
tests/unit/cli/commands/
├── test_roadmap_commands.py     # Test roadmap.py
├── test_status_commands.py      # Test status.py
├── test_notification_commands.py # Test notifications.py
└── test_chat_commands.py        # Test chat.py
```

**Test Coverage Requirements**:
- Each command function must have ≥1 test
- Test both success and error paths
- Mock external dependencies (databases, APIs)

### Integration Tests

**Existing Tests**:
- Keep existing integration tests in `tests/ci_tests/`
- Update imports if needed
- Verify commands work end-to-end

### Manual Testing Checklist
```bash
# Test all commands still work after refactor
project-manager view
project-manager view-priority 1
project-manager status
project-manager developer-status
project-manager notifications
project-manager respond 1 "approve"
project-manager chat
project-manager metrics
project-manager summary
project-manager calendar
```

---

## Rollout Plan

### Phase 1: Implementation (4 hours)
- Week 1, Days 1-2: Create module structure and move functions
- **Output**: All 4 command modules created and tested

### Phase 2: Integration (1 hour)
- Week 1, Day 2: Update main CLI to use new modules
- **Output**: Backwards compatibility verified

### Phase 3: Testing (1.5 hours)
- Week 1, Day 3: Run full test suite, manual testing
- **Output**: All tests passing, commands working

### Phase 4: Cleanup (30 min)
- Week 1, Day 3: Remove old code, update documentation
- **Output**: Clean codebase, updated docs

**Total Timeline**: 1 week (6.5 hours actual work)

---

## Risks & Mitigations

### Risk 1: Breaking Existing Functionality
**Likelihood**: MEDIUM
**Impact**: HIGH
**Mitigation**:
- Keep old code until new modules are fully tested
- Comprehensive manual testing checklist
- Run full CI/CD test suite before merging

### Risk 2: Import Circular Dependencies
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- Use shared utilities pattern (keep in main file)
- Avoid cross-imports between command modules
- Use dependency injection for shared services

### Risk 3: Test Failures Due to Import Changes
**Likelihood**: MEDIUM
**Impact**: LOW
**Mitigation**:
- Update test imports systematically
- Use find-replace for common import patterns
- Run tests after each module migration

### Risk 4: Developer Confusion (New Structure)
**Likelihood**: LOW
**Impact**: LOW
**Mitigation**:
- Update CLAUDE.md with new structure
- Add docstrings explaining module organization
- Create migration guide in this spec

---

## Success Criteria

### Quantitative
- ✅ `roadmap_cli.py` reduced to <250 LOC (from 1,806)
- ✅ All command modules <600 LOC
- ✅ Average module size: ~375 LOC (target: <500)
- ✅ 100% of existing tests passing
- ✅ No increase in test runtime
- ✅ Zero new linting/formatting errors

### Qualitative
- ✅ Developers can find commands faster (subjective)
- ✅ New commands easier to add (isolated modules)
- ✅ Code reviews focus on single responsibility
- ✅ Merge conflicts reduced (fewer people editing same file)

---

## Implementation Checklist

### Pre-Work
- [ ] Review this spec with team
- [ ] Create feature branch: `feature/refactor-roadmap-cli`
- [ ] Backup existing `roadmap_cli.py`

### Module Creation
- [ ] Create `commands/` package directory
- [ ] Create `commands/__init__.py`
- [ ] Create `commands/roadmap.py` (move view commands)
- [ ] Create `commands/status.py` (move status commands)
- [ ] Create `commands/notifications.py` (move notification commands)
- [ ] Create `commands/chat.py` (move chat commands)

### Integration
- [ ] Update `roadmap_cli.py` to import from commands
- [ ] Update argument parser to delegate to modules
- [ ] Verify shared utilities accessible to all modules

### Testing
- [ ] Create unit tests for each command module
- [ ] Run existing integration tests
- [ ] Manual testing of all 18 commands
- [ ] Verify no regressions

### Cleanup
- [ ] Remove old command functions from `roadmap_cli.py`
- [ ] Update CLAUDE.md with new structure
- [ ] Run `black` formatter on all files
- [ ] Run `pytest` with coverage check

### Completion
- [ ] Create PR with detailed description
- [ ] Request code review
- [ ] Merge to main after approval
- [ ] Update this spec status to "Implemented"

---

## Related Work

### Depends On
- None (independent refactoring)

### Blocks
- Future CLI expansion (easier to add new commands)
- SPEC-052 (error handling standardization will be easier with modular structure)

### Related Specs
- **SPEC-051**: Prompt utilities (could benefit from modular CLI structure)
- **SPEC-052**: Error handling (will apply to all command modules)

---

## Future Enhancements

### After This Refactor
1. **Command Plugins**: Commands could be dynamically loaded
2. **Async Commands**: Easier to add async support per module
3. **Command Aliases**: Simpler to manage with modular structure
4. **Auto-generated CLI Docs**: Extract from module docstrings

---

## Appendix A: Current Command Distribution

### Before Refactoring (roadmap_cli.py: 1,806 LOC)

| Command | Lines | Category |
|---------|-------|----------|
| cmd_view | 150 | Roadmap |
| cmd_view_priority | 120 | Roadmap |
| cmd_status | 200 | Status |
| cmd_developer_status | 180 | Status |
| cmd_notifications | 250 | Notifications |
| cmd_respond | 180 | Notifications |
| cmd_chat | 400 | Chat |
| cmd_assistant | 150 | Chat |
| cmd_metrics | 120 | Status |
| cmd_summary | 100 | Status |
| cmd_calendar | 80 | Status |
| cmd_dev_report | 76 | Status |
| Utilities | ~200 | Shared |

### After Refactoring

| Module | Lines | Commands |
|--------|-------|----------|
| roadmap_cli.py | 200 | Entry point + shared utilities |
| commands/roadmap.py | 300 | view, view-priority |
| commands/status.py | 350 | status, developer-status, metrics, summary, calendar, dev-report |
| commands/notifications.py | 400 | notifications, respond |
| commands/chat.py | 550 | chat, assistant |

**Total**: Same 1,800 LOC, but **organized into 5 files** (avg 360 LOC)

---

## Appendix B: File Size Comparison

### Before
```
roadmap_cli.py: 1,806 LOC ❌ (too large)
```

### After
```
roadmap_cli.py:           200 LOC ✅
commands/roadmap.py:      300 LOC ✅
commands/status.py:       350 LOC ✅
commands/notifications.py: 400 LOC ✅
commands/chat.py:         550 LOC ✅ (acceptable - complex logic)
```

**All files under 600 LOC** ✅

---

**Spec Version**: 1.0
**Last Updated**: 2025-10-17
**Estimated Effort**: 6.5 hours
**Actual Effort**: TBD (track during implementation)
