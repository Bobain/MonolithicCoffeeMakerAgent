# SPEC-048: Silent Background Agents Enforcement

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CFR-009, US-048
**Estimated Duration**: 4-6 hours (SIMPLIFIED)

---

## Executive Summary

Enforce CFR-009: ONLY user_listener plays sound notifications. All other agents (code_developer, architect, project_manager, etc.) work silently in background.

**Key Principle**: Background work should be silent - only user-facing interactions make sound.

---

## Problem Statement

### Current Situation
- **Background agents play sounds**: code_developer plays "Max Retries Reached" sound
- **User confusion**: "Which agent is notifying me?"
- **Noise pollution**: Multiple agents creating sounds interrupts workflow
- **Violated expectations**: Background work should be silent

### Root Cause
`NotificationDB.create_notification()` defaults to `sound=True`, and agents don't specify `sound=False` explicitly.

### Goal
Enforce that ONLY user_listener can play sounds. All other agents create silent notifications.

### Non-Goals
- ❌ Disable notifications entirely (they're still useful, just silent)
- ❌ Complex sound configuration system (just boolean: sound or no sound)
- ❌ Per-user sound preferences (future enhancement)

---

## Proposed Solution: SIMPLIFIED APPROACH

### Core Concept
1. **Add `agent_id` parameter to `NotificationDB.create_notification()`**
2. **Validate caller identity** → raise error if non-UI agent tries `sound=True`
3. **Update all agent code** → explicitly set `sound=False`

### Architecture (SIMPLE)
```
Agent calls: notifications.create_notification(
    type=...,
    message=...,
    sound=True,  # ← Validation happens here
    agent_id=AgentType.CODE_DEVELOPER
)
       ↓
NotificationDB validates:
    if sound=True and agent_id != AgentType.USER_LISTENER:
        raise CFR009ViolationError
       ↓
Agent must use sound=False (silent notification)
```

**ONLY user_listener can use `sound=True`!**

---

## Implementation Plan: SINGLE PHASE

### Phase 1: Enforcement (4-6 hours)

**Goal**: Enforce CFR-009 system-wide with validation.

**Files to Modify**:

1. `coffee_maker/cli/notifications.py` (~50 lines modified)

   **Add Exception**:
   ```python
   class CFR009ViolationError(Exception):
       """Raised when non-UI agent tries to play sound notification.

       CFR-009: ONLY user_listener can use sound notifications.
       """
       pass
   ```

   **Modify `create_notification()`**:
   ```python
   def create_notification(
       self,
       type: str,
       title: str,
       message: str,
       priority: int = NOTIF_PRIORITY_MEDIUM,
       sound: bool = False,  # ← Default changed to False
       context: dict = None,
       agent_id: str = None,  # ← NEW: Identify calling agent
   ) -> int:
       """Create a notification.

       Args:
           type: Notification type
           title: Title text
           message: Message text
           priority: Priority level
           sound: Play sound? (ONLY user_listener can use True)
           context: Additional context dict
           agent_id: Calling agent identifier (for CFR-009 enforcement)

       Returns:
           Notification ID

       Raises:
           CFR009ViolationError: If non-UI agent tries sound=True
       """
       # CFR-009: Validate sound usage
       if sound and agent_id and agent_id != "user_listener":
           raise CFR009ViolationError(
               f"CFR-009 VIOLATION: Agent '{agent_id}' cannot use sound=True. "
               f"ONLY user_listener can play sounds. "
               f"Background agents must use sound=False."
           )

       # ... rest of implementation
   ```

2. `coffee_maker/autonomous/daemon_implementation.py` (~15 lines modified)

   **All notification calls**:
   ```python
   # Before (VIOLATION):
   self.notifications.create_notification(
       type=NOTIF_TYPE_INFO,
       title=f"{priority_name}: Max Retries Reached",
       message="...",
       priority=NOTIF_PRIORITY_HIGH,
       # sound defaults to True - CFR-009 VIOLATION!
   )

   # After (COMPLIANT):
   self.notifications.create_notification(
       type=NOTIF_TYPE_INFO,
       title=f"{priority_name}: Max Retries Reached",
       message="...",
       priority=NOTIF_PRIORITY_HIGH,
       sound=False,  # CFR-009: Background agent must be silent
       agent_id="code_developer",
   )
   ```

3. Find and fix ALL notification calls in codebase:
   - `daemon.py`
   - `daemon_implementation.py`
   - `daemon_spec_manager.py`
   - `roadmap_cli.py` (project_manager backend calls)
   - Any other agents

**Testing**:
- Run daemon → trigger "Max Retries" → verify NO sound
- Try to create notification with `sound=True` from code_developer → raises CFR009ViolationError
- Create notification from user_listener with `sound=True` → works (allowed)

**Acceptance Criteria**:
- ✅ ONLY user_listener can use `sound=True`
- ✅ All other agents forced to `sound=False`
- ✅ Clear exception when violation attempted
- ✅ Daemon works silently in background

---

## Component Design

### NotificationDB Validation

**Modification**:
```python
def create_notification(
    self,
    type: str,
    title: str,
    message: str,
    priority: int = NOTIF_PRIORITY_MEDIUM,
    sound: bool = False,  # Changed default: False (silent)
    context: dict = None,
    agent_id: str = None,  # NEW parameter
) -> int:
    """Create a notification with CFR-009 enforcement.

    CFR-009: ONLY user_listener can use sound=True.
    All other agents MUST use sound=False.

    Args:
        agent_id: Identifies calling agent for validation
                  - "user_listener": Can use sound=True
                  - "code_developer": MUST use sound=False
                  - "architect": MUST use sound=False
                  - "project_manager": MUST use sound=False
                  - etc.

    Raises:
        CFR009ViolationError: If non-UI agent tries sound=True

    Implementation:
        1. Validate sound usage
        2. If sound=True and agent_id != "user_listener": RAISE
        3. Otherwise: Create notification as normal
    """
    # CFR-009 enforcement
    if sound and agent_id and agent_id != "user_listener":
        raise CFR009ViolationError(
            f"CFR-009 VIOLATION: Agent '{agent_id}' cannot use sound=True. "
            f"ONLY user_listener can play sounds. "
            f"Background agents must use sound=False."
        )

    # Continue with normal notification creation...
```

**Why This Works**:
- **Simple validation**: Single if-statement check
- **Clear errors**: Explicit exception with explanation
- **Backward compatible**: `agent_id=None` allowed (no validation)
- **Future-proof**: Can add agent-specific rules later

---

## Data Structures

### AgentType Enum (Optional Enhancement)

```python
from enum import Enum

class AgentType(str, Enum):
    """Agent types for CFR-009 enforcement."""

    USER_LISTENER = "user_listener"  # ONLY agent with UI/sound
    CODE_DEVELOPER = "code_developer"
    ARCHITECT = "architect"
    PROJECT_MANAGER = "project_manager"
    ASSISTANT = "assistant"
    CODE_SEARCHER = "code_searcher"
    UX_DESIGN_EXPERT = "ux_design_expert"

# Usage:
notifications.create_notification(
    ...,
    sound=False,
    agent_id=AgentType.CODE_DEVELOPER,
)
```

**Benefits**:
- Type safety (IDE autocomplete)
- Prevents typos ("code_develoepr")
- Clear list of all agents

---

## Testing Strategy

### Unit Tests (~1 hour)

**File**: `tests/unit/test_cfr009_enforcement.py`

```python
from coffee_maker.cli.notifications import CFR009ViolationError, NotificationDB
import pytest

def test_user_listener_can_use_sound():
    """user_listener can play sounds (CFR-009 compliant)."""
    db = NotificationDB()
    # Should NOT raise
    notif_id = db.create_notification(
        type="info",
        title="Test",
        message="Test",
        sound=True,
        agent_id="user_listener",
    )
    assert notif_id > 0

def test_code_developer_cannot_use_sound():
    """code_developer cannot play sounds (CFR-009 enforcement)."""
    db = NotificationDB()
    with pytest.raises(CFR009ViolationError, match="code_developer"):
        db.create_notification(
            type="info",
            title="Test",
            message="Test",
            sound=True,
            agent_id="code_developer",
        )

def test_background_agents_silent():
    """All background agents use sound=False."""
    db = NotificationDB()
    agents = ["code_developer", "architect", "project_manager"]

    for agent in agents:
        # Should work with sound=False
        notif_id = db.create_notification(
            type="info",
            title="Test",
            message="Test",
            sound=False,
            agent_id=agent,
        )
        assert notif_id > 0
```

### Integration Tests (~30 minutes)

**File**: `tests/ci_tests/test_daemon_silent.py`

```python
def test_daemon_notifications_are_silent():
    """Daemon creates silent notifications (CFR-009)."""
    # Run daemon
    # Trigger notification (e.g., max retries)
    # Verify: notification created with sound=False
    # Verify: no sound played
```

---

## Rollout Plan

### Single Day (4-6 hours)

**Hour 1-2**: Modify `NotificationDB`
- Add `agent_id` parameter
- Add `CFR009ViolationError` exception
- Implement validation logic
- Change default `sound` to `False`

**Hour 3-4**: Update All Agent Code
- Find all `create_notification()` calls (grep)
- Add `sound=False` and `agent_id=...` to each
- Focus on: daemon, daemon_implementation, daemon_spec_manager

**Hour 5**: Testing
- Write unit tests
- Run tests (verify enforcement works)
- Manual testing (daemon silent)

**Hour 6**: Documentation & Commit
- Update CFR-009 documentation
- Add docstring examples
- Commit with clear message

**Total: 4-6 hours (single day)**

---

## Success Criteria

### Must Have (P0)
- ✅ ONLY user_listener can use `sound=True`
- ✅ All background agents use `sound=False`
- ✅ Clear exception on violation
- ✅ Daemon works silently

### Should Have (P1)
- ✅ All existing code updated (no violations)
- ✅ Tests verify enforcement
- ✅ Documentation updated

### Could Have (P2) - DEFERRED
- ⚪ AgentType enum for type safety
- ⚪ Per-user sound preferences
- ⚪ Audit log of sound violations

---

## Why This is SIMPLE

### Compared to Comprehensive Approach

**Comprehensive had**:
- Per-agent sound configuration files
- User preferences database
- Complex sound routing system
- Multiple notification channels
- Advanced audio mixing

**This spec has**:
- Single boolean check (`agent_id != "user_listener"`)
- One new parameter (`agent_id`)
- Simple exception (`CFR009ViolationError`)
- Update existing code (add `sound=False`)

**Result**: 90% reduction in complexity

### What We REUSE

✅ **Existing NotificationDB**: Just add validation
✅ **Existing agents**: Just update calls
✅ **Existing sound system**: Don't need to modify
✅ **Existing exceptions**: Same pattern as others

**New code**: ~100 lines total (validation + updates + tests)

---

## Risks & Mitigations

### Risk 1: Missed notification calls (still use sound=True)

**Impact**: Medium
**Mitigation**:
- Grep entire codebase for `create_notification`
- Update ALL calls in one commit
- Tests verify no violations
- Exception will catch any missed ones

### Risk 2: user_listener not implemented yet

**Impact**: Low
**Mitigation**:
- user_listener agent exists (PRIORITY 10 complete)
- If not used yet, no sound notifications anywhere (acceptable)
- Enforcement ready for when user_listener launches

### Risk 3: Developers forget to pass `agent_id`

**Impact**: Low
**Mitigation**:
- `agent_id=None` → no validation (backward compatible)
- Documentation emphasizes CFR-009
- Code review catches missing `agent_id`

---

## Future Enhancements (NOT NOW)

Phase 2+ (if users request):
1. Per-user sound preferences (enable/disable sounds)
2. Different sound types (info, warning, error)
3. Notification channels (desktop, mobile, email)
4. Sound theme customization

**But**: Only add if users ask. Start simple!

---

## Implementation Checklist

### Single Day
- [ ] Add `CFR009ViolationError` exception to `notifications.py`
- [ ] Add `agent_id` parameter to `create_notification()`
- [ ] Implement validation logic (raise if violation)
- [ ] Change `sound` default to `False`
- [ ] Find all `create_notification()` calls (grep)
- [ ] Update daemon code: `sound=False, agent_id="code_developer"`
- [ ] Write unit tests (enforcement works)
- [ ] Run tests (all pass)
- [ ] Update CFR-009 documentation
- [ ] Commit with clear message

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending
- [ ] User (final approval) - Approval pending

---

**Remember**: CFR-009 enforces clear role boundaries - user_listener is UI, all others are backend. Silent background agents create better user experience and prevent notification spam!

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements (4-6 hours)
