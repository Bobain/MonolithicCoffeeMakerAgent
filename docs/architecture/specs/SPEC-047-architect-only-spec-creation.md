# SPEC-047: Architect-Only Spec Creation Enforcement

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-17
**Related**: CFR-008, US-047
**Estimated Duration**: 2-3 days (SIMPLIFIED)

---

## Executive Summary

Enforce CFR-008: ONLY architect creates technical specifications, NEVER code_developer. This prevents role boundary violations, ensures architectural consistency, and enables big-picture optimization across all ROADMAP priorities.

**Key Principle**: architect thinks ahead proactively, code_developer implements reactively.

---

## Problem Statement

### Current Situation
- **Role Confusion**: code_developer sometimes tries to create specs when missing
- **Reactive Design**: Specs created when code_developer encounters priority (too late!)
- **Architectural Debt**: Each priority designed in isolation without cross-feature optimization
- **Infinite Loops**: code_developer delegates to architect → architect back to code_developer (deadlock)

### Root Cause
The daemon's `_ensure_technical_spec()` method allows code_developer to create specs from templates when none exist. This violates CFR-008 and leads to suboptimal architecture.

### Goal
Enforce strict boundary: architect creates ALL specs proactively, code_developer waits if spec missing.

### Non-Goals
- ❌ Automatic spec generation from AI (requires human architect judgment)
- ❌ Code_developer creating "quick specs" (defeats purpose of architect role)
- ❌ User creating specs directly (user_listener delegates to architect)

---

## Proposed Solution: SIMPLIFIED APPROACH

### Core Concept
1. **architect reviews FULL ROADMAP proactively** → creates ALL needed specs upfront
2. **code_developer checks for spec** → BLOCKS if missing (does NOT create)
3. **User notified of missing spec** → architect creates it → code_developer resumes

### Architecture (SIMPLE)
```
code_developer encounters priority
       ↓
Check: Does technical spec exist?
       ↓
    YES → Implement using spec
       ↓
    NO → BLOCK (do NOT create spec)
       ↓
Create notification: "Spec missing for PRIORITY X"
       ↓
User notified (sound + terminal)
       ↓
architect creates spec (proactively or on-demand)
       ↓
code_developer resumes with spec
```

**NO spec creation by code_developer, NO delegation loops!**

---

## Implementation Plan: PHASED & SIMPLE

### Phase 1: Enforce Blocking (Day 1 - 4 hours)

**Goal**: code_developer BLOCKS when spec missing, does NOT create specs.

**Files to Modify**:
1. `coffee_maker/autonomous/daemon_spec_manager.py` (~30 lines modified)
   - Modify `_ensure_technical_spec()`:
     ```python
     def _ensure_technical_spec(self, priority: dict) -> bool:
         """Check if technical spec exists.

         CFR-008: code_developer NEVER creates specs.
         If spec missing, notify user and BLOCK.

         Returns:
             True if spec exists
             False if spec missing (blocks implementation)
         """
         spec_path = self._get_spec_path(priority)

         if spec_path.exists():
             logger.info(f"✅ Technical spec found: {spec_path}")
             return True

         # CFR-008 ENFORCEMENT: Do NOT create spec!
         logger.error(f"❌ CFR-008: Spec missing for {priority['name']}")
         logger.error("code_developer CANNOT create specs")
         logger.error("→ Blocking until architect creates spec")

         # Notify user via user_listener
         self._notify_spec_missing(priority)

         return False  # BLOCK implementation
     ```

2. Add new method `_notify_spec_missing()` (~20 lines)
   - Create user-facing notification
   - Include priority details
   - Suggest architect action
   - Mark as HIGH priority + sound

**Testing**:
- Start daemon with priority lacking spec
- Verify: daemon BLOCKS (does not create spec)
- Verify: notification created with sound
- Create spec manually → daemon resumes

**Acceptance Criteria**:
- ✅ code_developer NEVER creates specs
- ✅ Daemon blocks when spec missing
- ✅ User notified immediately (sound + notification)
- ✅ Clear error messages explain situation

---

### Phase 2: Architect Proactive Workflow (Day 1-2 - 8 hours)

**Goal**: architect has tools to review ROADMAP and create ALL needed specs.

**Files to Create**:
1. `coffee_maker/cli/spec_review.py` (~150 lines)
   - Command: `project-manager spec-review`
   - Shows: All ROADMAP priorities
   - Highlights: Priorities missing specs
   - Output: Markdown table with status

   ```python
   class SpecReviewReport:
       """Generate spec review report for architect."""

       def generate_report(self) -> str:
           """Scan ROADMAP, check which priorities have specs.

           Returns:
               Markdown table showing spec coverage
           """
           priorities = self._parse_roadmap()

           report = "# Technical Spec Coverage Report\n\n"
           report += "| Priority | Title | Spec Status | Action |\n"
           report += "|----------|-------|-------------|--------|\n"

           for p in priorities:
               spec_exists = self._check_spec_exists(p)
               status = "✅ Exists" if spec_exists else "❌ Missing"
               action = "N/A" if spec_exists else "architect CREATE SPEC"

               report += f"| {p['name']} | {p['title']} | {status} | {action} |\n"

           return report
   ```

2. **Files to Modify**:
   - `coffee_maker/cli/roadmap_cli.py` (~10 lines added)
     - Add command: `spec-review`
     - Route to `SpecReviewReport`

**Testing**:
- Run `project-manager spec-review`
- Verify: Shows all priorities
- Verify: Highlights missing specs
- Create spec → rerun command → see status change

**Acceptance Criteria**:
- ✅ architect can see full spec coverage at a glance
- ✅ Missing specs highlighted clearly
- ✅ Command runs in <1 second (fast feedback)

---

### Phase 3: Automated Proactive Checking (Day 2-3 - 4 hours)

**Goal**: architect automatically notified when new priorities added without specs.

**Files to Create**:
1. `coffee_maker/autonomous/spec_watcher.py` (~100 lines)
   - Watches ROADMAP.md for changes
   - Detects new priorities
   - Checks if specs exist
   - Notifies architect if missing

   ```python
   class SpecWatcher:
       """Monitor ROADMAP.md for new priorities needing specs."""

       def __init__(self):
           self.roadmap_path = Path("docs/roadmap/ROADMAP.md")
           self.last_check = None
           self.known_priorities = set()

       def check_for_new_priorities(self) -> list[dict]:
           """Check if new priorities added to ROADMAP.

           Returns:
               List of new priorities needing specs
           """
           current_priorities = self._parse_roadmap()
           new_priorities = []

           for p in current_priorities:
               if p['name'] not in self.known_priorities:
                   # New priority detected
                   if not self._spec_exists(p):
                       new_priorities.append(p)
                   self.known_priorities.add(p['name'])

           return new_priorities
   ```

2. **Files to Modify**:
   - `coffee_maker/autonomous/daemon.py` (~15 lines added)
     - Add periodic spec check (every 5 minutes)
     - Notify if new priorities without specs

**Testing**:
- Add new priority to ROADMAP
- Wait 5 minutes
- Verify: architect notified
- Create spec → notification cleared

**Acceptance Criteria**:
- ✅ New priorities auto-detected
- ✅ architect notified within 5 minutes
- ✅ Notification includes priority details
- ✅ No false positives

---

## Component Design

### SpecReviewReport

**Responsibility**: Generate comprehensive report of spec coverage.

**Interface**:
```python
class SpecReviewReport:
    """Generate spec review reports for architect."""

    def __init__(self):
        self.roadmap_path = Path("docs/roadmap/ROADMAP.md")
        self.spec_dir = Path("docs/architecture/specs")

    def generate_report(self) -> str:
        """Generate markdown report of spec coverage.

        Returns:
            Markdown-formatted report

        Steps:
            1. Parse ROADMAP.md for all priorities
            2. Check which have technical specs
            3. Format as markdown table
            4. Include summary stats
        """
        pass

    def _parse_roadmap(self) -> list[dict]:
        """Parse ROADMAP.md to extract priorities."""
        pass

    def _check_spec_exists(self, priority: dict) -> bool:
        """Check if technical spec exists for priority."""
        spec_path = self._get_spec_path(priority)
        return spec_path.exists()

    def _get_spec_path(self, priority: dict) -> Path:
        """Get expected spec file path."""
        # SPEC-{number}-{name}.md
        number = priority['name'].replace('PRIORITY ', '')
        name = priority['title'].lower().replace(' ', '-')[:30]
        return self.spec_dir / f"SPEC-{number}-{name}.md"
```

---

## Data Structures

### Priority (from ROADMAP)
```python
{
    "name": "PRIORITY 9",
    "title": "Enhanced code_developer Communication",
    "content": "...",
    "status": "🔄 In Progress",
    "number": 9
}
```

### Spec Coverage Report
```markdown
# Technical Spec Coverage Report

Generated: 2025-10-17 14:30:00

## Summary
- Total Priorities: 12
- Specs Exist: 8 (67%)
- Specs Missing: 4 (33%)

## Coverage Details

| Priority | Title | Spec Status | Action |
|----------|-------|-------------|--------|
| PRIORITY 9 | Enhanced Communication | ✅ Exists | N/A |
| PRIORITY 10 | user-listener UI | ✅ Exists | N/A |
| US-047 | Architect-Only Specs | ❌ Missing | architect CREATE SPEC |
| US-048 | Silent Background Agents | ❌ Missing | architect CREATE SPEC |

## Priorities Needing Specs (4)

1. **US-047**: Architect-Only Spec Creation
   - Spec Path: `docs/architecture/specs/SPEC-047-architect-only-spec-creation.md`
   - Status: Missing
   - Priority: CRITICAL (CFR-008)

2. **US-048**: Silent Background Agents
   - Spec Path: `docs/architecture/specs/SPEC-048-silent-background-agents.md`
   - Status: Missing
   - Priority: HIGH (CFR-009)
```

---

## Testing Strategy

### Unit Tests (~2 hours)

**File**: `tests/unit/test_spec_enforcement.py`

```python
def test_spec_missing_blocks_implementation():
    """Test that missing spec blocks code_developer."""
    # Setup: Remove spec file
    # Execute: daemon._ensure_technical_spec()
    # Assert: Returns False (blocks)

def test_spec_exists_allows_implementation():
    """Test that existing spec allows implementation."""
    # Setup: Create spec file
    # Execute: daemon._ensure_technical_spec()
    # Assert: Returns True (allows)

def test_notification_created_on_missing_spec():
    """Test notification when spec missing."""
    # Setup: Remove spec file
    # Execute: daemon._ensure_technical_spec()
    # Assert: Notification created with correct details
```

### Integration Tests (~1 hour)

**File**: `tests/ci_tests/test_spec_workflow.py`

```python
def test_full_workflow_spec_blocking():
    """Test full workflow: missing spec → blocks → notify → create → resume."""
    # 1. Remove spec
    # 2. Start daemon
    # 3. Verify: daemon blocks
    # 4. Verify: notification created
    # 5. Create spec
    # 6. Verify: daemon resumes
```

---

## Rollout Plan

### Day 1 Morning (4 hours)
- Modify `daemon_spec_manager.py` to BLOCK on missing spec
- Add `_notify_spec_missing()` method
- Write unit tests
- Manual testing: daemon blocks correctly

### Day 1 Afternoon (4 hours)
- Create `SpecReviewReport` class
- Add `spec-review` command to CLI
- Test spec coverage report
- Verify output format

### Day 2 Morning (4 hours)
- Create `SpecWatcher` class
- Integrate with daemon (periodic checks)
- Test new priority detection
- Verify architect notifications

### Day 2 Afternoon (4 hours)
- Write integration tests
- End-to-end testing
- Update documentation
- Final testing and commit

**Total: 2-3 days (16-24 hours)**

---

## Success Criteria

### Must Have (P0)
- ✅ code_developer NEVER creates specs (enforced)
- ✅ Daemon blocks when spec missing
- ✅ User notified immediately (sound + notification)
- ✅ architect has spec coverage report
- ✅ Clear error messages

### Should Have (P1)
- ✅ Automated detection of new priorities
- ✅ architect notified within 5 minutes
- ✅ Spec review command (<1 second)

### Could Have (P2) - DEFERRED
- ⚪ AI-assisted spec generation (future)
- ⚪ Spec quality scoring (future)
- ⚪ Cross-spec dependency analysis (future)

---

## Why This is SIMPLE

### Compared to Comprehensive Approach

**Comprehensive had**:
- AI-based spec generation
- Complex delegation protocols
- Spec templates with 50+ fields
- Advanced quality metrics
- Cross-feature dependency graphs

**This spec has**:
- Simple file existence check (BLOCK if missing)
- Single notification to user
- Basic spec coverage report
- Manual architect workflow (no AI automation)

**Result**: 70% reduction in complexity

### What We REUSE

✅ **Existing notification system**: Already has sound, priority, context
✅ **Existing ROADMAP parser**: Already extracts priorities
✅ **Existing file system**: Just check if spec file exists
✅ **Existing daemon structure**: Just modify `_ensure_technical_spec()`

**New code**: ~300 lines total (SpecReviewReport + SpecWatcher + modifications)

---

## Risks & Mitigations

### Risk 1: code_developer stuck waiting for specs

**Impact**: High
**Mitigation**:
- Loud notification (sound) ensures user/architect aware
- Spec coverage report makes missing specs obvious
- Proactive monitoring (every 5 minutes)

### Risk 2: architect overwhelmed with spec requests

**Impact**: Medium
**Mitigation**:
- architect creates specs in batches (review full ROADMAP)
- Simplification-first approach (ADR-003) makes specs fast to create
- Target 2-4 days per spec (sustainable pace)

### Risk 3: Users bypass architect (edit code directly)

**Impact**: Low
**Mitigation**:
- Documentation clearly states CFR-008
- Pre-commit hooks could check for spec references (future)

---

## Future Enhancements (NOT NOW)

Phase 2+ (if users request):
1. AI-assisted spec drafting (architect reviews/approves)
2. Spec quality scoring system
3. Cross-spec dependency analysis
4. Automatic spec updates when ROADMAP changes

**But**: Only add if actually needed. Start simple!

---

## Implementation Checklist

### Day 1
- [ ] Modify `daemon_spec_manager._ensure_technical_spec()` to BLOCK
- [ ] Add `_notify_spec_missing()` method
- [ ] Create `SpecReviewReport` class
- [ ] Add `spec-review` CLI command
- [ ] Write unit tests
- [ ] Manual testing

### Day 2
- [ ] Create `SpecWatcher` class
- [ ] Integrate with daemon (periodic checks)
- [ ] Write integration tests
- [ ] Update CFR-008 documentation
- [ ] Final testing
- [ ] Create PR and commit

---

## Approval

- [x] architect (author) - Approved 2025-10-17
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending
- [ ] User (final approval) - Approval pending

---

**Remember**: CFR-008 is CRITICAL for architectural quality. Enforcing strict role boundaries prevents debt accumulation and enables big-picture optimization. This spec makes that enforcement automatic and obvious!

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements Phase 1
