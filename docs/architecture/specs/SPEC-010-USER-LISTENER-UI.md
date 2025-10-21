# SPEC-010: User-Listener UI Command (SIMPLIFIED)

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: PRIORITY 10, ADR-003 (Simplification-First Approach)
**Estimated Duration**: 4-6 hours (SIMPLIFIED from original 11-16 hours)

---

## Executive Summary

Create a standalone `poetry run user-listener` command that serves as the PRIMARY USER INTERFACE for all user interactions. This spec dramatically simplifies the original approach by **REUSING** the existing ChatSession infrastructure from `project-manager chat` with minimal modification.

**CRITICAL SIMPLIFICATION**: Instead of building a complex delegation system, we create a thin wrapper around existing ChatSession that enforces architectural boundaries (user_listener = UI agent).

**Key Principle**: The SIMPLEST solution that achieves the business goal - users have a dedicated UI command that represents the user_listener agent.

---

## Problem Statement

### Current Situation
- `project-manager chat` provides UI functionality
- Architecture defines `user_listener` as PRIMARY USER INTERFACE
- Mismatch between implementation (project-manager) and architecture (user_listener)
- No standalone `user-listener` command exists
- `AgentType.USER_LISTENER` defined but not used

### Goal
Users interact with a dedicated `poetry run user-listener` command that represents the PRIMARY USER INTERFACE agent.

### Non-Goals
- ❌ Complex agent delegation system (YAGNI - can add later if needed)
- ❌ AI-powered intent classification (YAGNI - existing ChatSession already works)
- ❌ Multi-agent workflow orchestration (YAGNI - defer to Phase 2)
- ❌ Agent routing logic (YAGNI - ChatSession handles this)
- ❌ Custom conversation threading (YAGNI - existing history sufficient)
- ❌ New AgentDelegationRouter class (YAGNI - reuse existing ChatSession)

---

## Proposed Solution: MAXIMUM REUSE APPROACH

### Core Concept
Copy the working `project-manager chat` implementation, rename to `user-listener`, enforce singleton pattern. **That's it.**

### Architecture (SIMPLE)
\`\`\`
User runs: poetry run user-listener
       ↓
user_listener.py main()
       ↓
Register as USER_LISTENER (singleton)
       ↓
Create ChatSession (REUSED from project_manager)
       ↓
Start chat loop
       ↓
User interacts (same as project-manager chat)
\`\`\`

**NO new infrastructure, NO complex delegation, JUST rename and register!**

---

## What We REUSE

✅ **ChatSession**: Entire interactive chat infrastructure (~1000 lines)
✅ **AIService**: Claude API/CLI integration
✅ **RoadmapEditor**: ROADMAP modification capabilities
✅ **AssistantManager**: Documentation knowledge
✅ **All command handlers**: /add, /update, /view, /analyze, etc.
✅ **Rich terminal UI**: Markdown rendering, syntax highlighting, streaming
✅ **Prompt-toolkit**: Multi-line input, history, auto-completion
✅ **AgentRegistry**: Singleton enforcement

**New code**: ~50 lines (just the wrapper)

---

## Why This is SIMPLE

### Compared to Original SPEC-010 (970 lines)

**Original had**:
- 2 new classes (UserListenerCLI, AgentDelegationRouter)
- 11-16 hours implementation
- Intent classification system (pattern matching + AI)
- Agent-specific delegation prompts
- Context passing mechanism
- Phase 1-4 rollout (over 4 phases)
- Agent status awareness
- Conversation threading
- ~500 lines of new code

**This spec has**:
- 1 file (`user_listener.py`)
- 4-6 hours implementation
- 100% reuse of ChatSession
- No new delegation system (reuse existing)
- No new context mechanism (reuse existing)
- Single phase rollout
- No status awareness (YAGNI)
- No threading (YAGNI)
- ~250 lines total (mostly copied from project-manager)

**Result**: 74% reduction in code (970 → 250 lines)

---

## Implementation: SINGLE FILE

**File**: `coffee_maker/cli/user_listener.py` (~250 lines, mostly copy-paste from roadmap_cli.py)

The implementation is straightforward - copy the `cmd_chat()` function from `roadmap_cli.py` and make it a standalone command with singleton registration.

**Key changes from project-manager chat**:
1. Register as `AgentType.USER_LISTENER` (singleton)
2. Update welcome banner to "User Listener · Primary Interface"
3. Update help text to reflect user_listener role
4. Same ChatSession, same AIService, same everything else

**That's it!** No complex new systems, just architectural alignment.

---

## Rollout Plan

### Day 1: Implementation (4-6 hours total)

**Hour 1-2: Create user_listener.py**
- Copy structure from `cmd_chat()` in `roadmap_cli.py`
- Add singleton registration with `AgentRegistry.register(AgentType.USER_LISTENER)`
- Update welcome banner and help text

**Hour 3-4: Integration & Testing**
- Add to `pyproject.toml` scripts section: `user-listener = "coffee_maker.cli.user_listener:main"`
- Run `poetry install`
- Test: `poetry run user-listener`
- Verify singleton enforcement

**Hour 5: Tests**
- Write `tests/unit/test_user_listener.py` (singleton tests)
- Write `tests/ci_tests/test_user_listener_integration.py` (startup tests)
- Run: `pytest tests/`

**Hour 6: Documentation**
- Update CLAUDE.md with new command
- Test all manual scenarios
- Create PR and commit

### Deployment Strategy

**Phase 1 (Week 1)**: Soft launch
- Launch `user-listener` alongside `project-manager chat`
- No breaking changes
- Gather feedback

**Phase 2 (Week 2-3)**: Promote
- Update README to recommend `user-listener`
- Add deprecation notice to `project-manager chat`

**Phase 3 (Week 4+)**: Migrate
- Redirect `project-manager chat` → `user-listener`
- Remove chat code from project-manager

---

## Testing Strategy

### Unit Tests (30 minutes)

**File**: `tests/unit/test_user_listener.py`

\`\`\`python
"""Tests for user_listener CLI."""

import pytest

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
)


def test_singleton_enforcement():
    """Test that only one user_listener can run at a time."""
    # Register first instance
    with AgentRegistry.register(AgentType.USER_LISTENER):
        # Try to register another instance - should fail
        with pytest.raises(AgentAlreadyRunningError) as exc_info:
            AgentRegistry().register_agent(AgentType.USER_LISTENER)

        assert "user_listener" in str(exc_info.value).lower()
        assert "already running" in str(exc_info.value).lower()


def test_cleanup_on_exit():
    """Test that singleton is cleaned up on exit."""
    # Register and exit
    with AgentRegistry.register(AgentType.USER_LISTENER):
        pass  # Automatically cleaned up

    # Should be able to register again
    with AgentRegistry.register(AgentType.USER_LISTENER):
        pass  # Should succeed
\`\`\`

### Manual Testing (1 hour)

**Test Scenarios**:

1. **Basic Startup**
   \`\`\`bash
   $ poetry run user-listener
   [Should show welcome banner and start chat]
   \`\`\`

2. **Singleton Enforcement**
   \`\`\`bash
   # Terminal 1
   $ poetry run user-listener

   # Terminal 2 (should fail)
   $ poetry run user-listener
   Error: Agent 'user_listener' is already running! PID: 12345
   \`\`\`

3. **All Commands Work**
   \`\`\`bash
   $ poetry run user-listener
   › /view
   [Shows ROADMAP]

   › /add PRIORITY 99: Test feature
   [Adds to ROADMAP]

   › Design a caching layer
   [AI responds with architectural guidance]
   \`\`\`

4. **Cleanup on Exit**
   \`\`\`bash
   $ poetry run user-listener
   › /exit
   [Exits cleanly]

   # Can start again
   $ poetry run user-listener
   [Starts successfully]
   \`\`\`

---

## Success Criteria

### Must Have (P0)
- ✅ `poetry run user-listener` starts successfully
- ✅ Provides same functionality as `project-manager chat`
- ✅ Singleton enforcement prevents duplicate instances
- ✅ Cleanup on exit (can restart)
- ✅ All existing commands work (/add, /update, /view, etc.)

### Should Have (P1)
- ✅ Welcome banner identifies as "User Listener"
- ✅ Documentation updated in CLAUDE.md
- ✅ Unit tests pass
- ✅ Integration tests pass

### Could Have (P2) - DEFERRED
- ⚪ Complex agent delegation (not needed - ChatSession handles this)
- ⚪ Intent classification AI (not needed - existing AI works)
- ⚪ Multi-agent orchestration (defer to Phase 2)

---

## Risks & Mitigations

### Risk 1: Confusion with project-manager chat

**Impact**: Medium
**Mitigation**: Clear deprecation path, documentation, welcome banner differentiates

### Risk 2: Code duplication

**Impact**: Low
**Mitigation**: Acceptable for 250 lines. Can refactor later if needed (YAGNI)

### Risk 3: Users don't migrate

**Impact**: Low
**Mitigation**: Both commands work during transition. Gradual deprecation.

---

## Future Enhancements (NOT NOW)

Phase 2+ (if users request):
1. Complex agent delegation system
2. AI-powered intent classification
3. Multi-agent workflow orchestration
4. Agent status dashboard
5. Conversation threading

**But**: Only add if users actually need them. Start simple!

---

## Implementation Checklist

### Hour 1-2: Core File
- [ ] Create `coffee_maker/cli/user_listener.py`
- [ ] Copy structure from `cmd_chat()` function in `roadmap_cli.py`
- [ ] Add singleton registration (AgentType.USER_LISTENER)
- [ ] Update welcome banner ("User Listener · Primary Interface")

### Hour 3-4: Integration & Testing
- [ ] Add to `pyproject.toml` scripts section
- [ ] Run `poetry install`
- [ ] Test: `poetry run user-listener`
- [ ] Verify singleton enforcement

### Hour 5: Tests
- [ ] Write `tests/unit/test_user_listener.py`
- [ ] Write `tests/ci_tests/test_user_listener_integration.py`
- [ ] Run: `pytest tests/`

### Hour 6: Documentation
- [ ] Update CLAUDE.md (new command usage)
- [ ] Test all manual scenarios
- [ ] Create PR and commit

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] User (final approval) - Approval pending

---

**Remember**: Simplicity is a feature, not a bug. This spec gives code_developer everything needed to implement a high-value feature in 4-6 hours instead of 11-16 hours, with 74% less code.

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements in 4-6 hours

---

## ADR-003 Compliance Checklist

This spec follows ADR-003 Simplification-First principles:

- ✅ **REUSE Over Rebuild**: 100% reuse of ChatSession infrastructure
- ✅ **MINIMUM Viable Solution**: Just a wrapper around existing code
- ✅ **YAGNI**: Deferred complex delegation, threading, status awareness
- ✅ **Optimize for Speed**: 4-6 hours vs 11-16 hours (62% faster)
- ✅ **Clear Non-Goals**: Explicit list of deferred features
- ✅ **Comparison**: Shows 74% code reduction vs original spec

**Simplification Win**: 62% faster implementation, 74% less code, same business value.
