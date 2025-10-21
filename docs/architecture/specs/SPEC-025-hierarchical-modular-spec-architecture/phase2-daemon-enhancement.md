# SPEC-025 - Phase 2: Daemon Enhancement

**Estimated Time**: 3 hours
**Dependencies**: Phase 1 complete (technical-specification-handling v2.0.0)
**Status**: Planned
**Files Modified**: `coffee_maker/autonomous/daemon_implementation.py`

---

## Goal

Update `daemon_implementation.py` to leverage hierarchical specs with progressive disclosure, enabling code_developer to:
1. Automatically detect current phase (ROADMAP, git, file existence)
2. Load only relevant spec content (overview + current phase)
3. Track progress correctly (reset no_progress_count when files change)
4. Support unlimited iterations while making forward progress

**What This Phase Accomplishes**:
- daemon integrates with technical-specification-handling skill v2.0.0
- Context usage reduced by 71% (150 lines vs 350 lines)
- Progressive implementation supported (Phase 1 → Phase 2 → Phase 3 → ...)
- CFR-016 compliance (incremental steps, each 1-2 hours)

---

## Prerequisites

- [x] Phase 1 complete (technical-specification-handling v2.0.0 available)
- [ ] daemon_implementation.py already updated with no_progress_count tracking
- [ ] Understanding of daemon's current spec loading logic

---

## Detailed Steps

### Step 1: Integrate Hierarchical Spec Reading

**What**: Replace current spec reading logic with hierarchical spec handler

**Why**: Leverage progressive disclosure to reduce context usage

**How**:
1. Import SpecHandler from coffee_maker.utils.spec_handler
2. Replace direct file reading with `read_hierarchical()` call
3. Handle both hierarchical and monolithic specs (backward compatible)
4. Extract spec content from handler response

**Current Implementation** (daemon_implementation.py):
```python
# Around line 400-450 (approximate)
def _load_spec_content(self, priority: dict) -> str:
    """Load technical spec content."""
    spec_path = self._find_spec(priority)

    if not spec_path or not spec_path.exists():
        return "[NO SPEC FOUND]"

    # Read entire file (monolithic)
    return spec_path.read_text()
```

**New Implementation**:
```python
from coffee_maker.utils.spec_handler import SpecHandler

def _load_spec_content(self, priority: dict) -> str:
    """
    Load technical spec with progressive disclosure.

    Returns:
        str: Spec content (overview + current phase for hierarchical,
             full content for monolithic)
    """
    spec_handler = SpecHandler()

    # Try hierarchical first
    result = spec_handler.read_hierarchical(
        priority_id=priority.get("name"),  # e.g., "PRIORITY 25" or "US-104"
        phase=None  # Auto-detect
    )

    if result["success"] and result["spec_type"] == "hierarchical":
        # Hierarchical spec found
        logger.info(
            f"📖 Loaded hierarchical spec: Phase {result['current_phase']}/{result['total_phases']}"
        )
        logger.info(f"📊 Context size: {result['context_size']} chars (vs ~8500 monolithic)")
        return result["full_context"]

    # Fallback: Try monolithic
    spec_path = spec_handler.find_spec(priority)

    if not spec_path or not spec_path.exists():
        return "[NO SPEC FOUND]"

    logger.info(f"📖 Loaded monolithic spec: {spec_path}")
    return spec_path.read_text()
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (update `_load_spec_content()`)

---

### Step 2: Add Phase Detection Integration

**What**: Use skill's phase detection to identify current phase

**Why**: daemon needs to know which phase code_developer is working on

**How**:
1. Call `detect_current_phase()` from skill (via SpecHandler)
2. Log current phase for debugging
3. Use phase info to update ROADMAP checkboxes

**Implementation**:
```python
def _detect_current_phase(self, priority: dict) -> int:
    """
    Detect which phase to work on next.

    Uses technical-specification-handling skill's detection logic.

    Returns:
        int: Phase number (1, 2, 3, ...)
    """
    spec_handler = SpecHandler()

    # Extract priority identifier
    priority_id = priority.get("name")  # "PRIORITY 25" or "US-104"

    # Use skill's detection
    result = spec_handler.read_hierarchical(priority_id, phase=None)

    if result["success"]:
        current_phase = result["current_phase"]
        total_phases = result["total_phases"]

        logger.info(
            f"📍 Current phase: {current_phase}/{total_phases} "
            f"(based on ROADMAP/git/file detection)"
        )

        return current_phase

    # Fallback: Phase 1
    logger.warning("⚠️ Could not detect phase, defaulting to Phase 1")
    return 1
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (add `_detect_current_phase()`)

---

### Step 3: Update Progress Tracking for Phases

**What**: Update ROADMAP checkboxes to track phase completion

**Why**: Users need visibility into which phase is complete, which is next

**How**:
1. After successful commit, mark current phase complete
2. Update ROADMAP with phase checkbox: `- [x] Phase 2 complete`
3. Log phase completion

**Implementation**:
```python
def _mark_phase_complete(self, priority: dict, phase: int):
    """
    Mark phase as complete in ROADMAP.

    Updates ROADMAP.md with phase completion checkbox.

    Args:
        priority: Priority dict
        phase: Phase number that was completed
    """
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    roadmap = roadmap_path.read_text()

    # Find priority section
    priority_name = priority.get("name")
    pattern = f"### {priority_name}:"

    if pattern not in roadmap:
        logger.warning(f"Could not find priority section: {priority_name}")
        return

    # Find section boundaries
    section_start = roadmap.index(pattern)
    section_end = roadmap.find("###", section_start + 1)
    if section_end == -1:
        section_end = len(roadmap)

    section = roadmap[section_start:section_end]

    # Add/update phase checkbox
    phase_marker = f"- [ ] Phase {phase}"
    phase_complete = f"- [x] Phase {phase} complete"

    if phase_marker in section:
        # Update existing checkbox
        section = section.replace(phase_marker, phase_complete)
    else:
        # Add new checkbox (after phase list)
        phase_section_end = section.find("**Technical Specification**:")
        if phase_section_end == -1:
            phase_section_end = len(section) - 1

        section = (
            section[:phase_section_end]
            + f"\n{phase_complete}\n"
            + section[phase_section_end:]
        )

    # Replace section in roadmap
    updated_roadmap = (
        roadmap[:section_start]
        + section
        + roadmap[section_end:]
    )

    roadmap_path.write_text(updated_roadmap)

    logger.info(f"✅ Marked Phase {phase} complete in ROADMAP")
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (add `_mark_phase_complete()`)

---

### Step 4: Integrate Phase Completion into Work Loop

**What**: Call `_mark_phase_complete()` after successful commit

**Why**: Automatically track phase progress in ROADMAP

**How**:
1. After commit succeeds, detect completed phase
2. Call `_mark_phase_complete()`
3. Log completion message

**Implementation**:
```python
# In _run_iteration() or equivalent method

# After successful commit
if commit_success:
    # Detect which phase was just completed
    current_phase = self._detect_current_phase(priority)

    # Mark complete in ROADMAP
    self._mark_phase_complete(priority, current_phase)

    # Reset no_progress_count (files changed)
    self.no_progress_count = 0

    logger.info(
        f"✅ Phase {current_phase} complete, proceeding to Phase {current_phase + 1}"
    )
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (update work loop logic)

---

### Step 5: Add Context Efficiency Logging

**What**: Log context usage metrics (hierarchical vs monolithic)

**Why**: Demonstrate 71% context reduction benefit

**How**:
1. After loading spec, log context size
2. Compare to monolithic equivalent
3. Show savings percentage

**Implementation**:
```python
def _load_spec_content(self, priority: dict) -> str:
    """Load spec with context efficiency logging."""
    spec_handler = SpecHandler()

    result = spec_handler.read_hierarchical(
        priority_id=priority.get("name"),
        phase=None
    )

    if result["success"] and result["spec_type"] == "hierarchical":
        context_size = result["context_size"]
        estimated_monolithic = context_size * 3.5  # Approximate monolithic size

        savings_pct = ((estimated_monolithic - context_size) / estimated_monolithic) * 100

        logger.info(
            f"📊 Context efficiency:\n"
            f"  Loaded: {context_size} chars (hierarchical)\n"
            f"  vs ~{int(estimated_monolithic)} chars (monolithic)\n"
            f"  Savings: {int(savings_pct)}% ✅"
        )

        return result["full_context"]

    # Fallback...
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (update `_load_spec_content()`)

---

### Step 6: Update Error Handling

**What**: Handle cases where hierarchical spec exists but phase file missing

**Why**: Graceful degradation if phase files incomplete

**How**:
1. Catch `read_hierarchical()` failures
2. Fall back to monolithic spec or README only
3. Log warning, continue execution

**Implementation**:
```python
result = spec_handler.read_hierarchical(priority_id, phase=None)

if not result["success"]:
    logger.warning(
        f"⚠️ Hierarchical spec read failed: {result.get('reason')}\n"
        f"Falling back to monolithic or README only"
    )

    # Fallback strategy
    spec_path = spec_handler.find_spec(priority)
    if spec_path and spec_path.is_dir():
        # Directory exists, read README only
        readme = (spec_path / "README.md").read_text()
        logger.info("📖 Loaded README.md only (phase file missing)")
        return readme
    elif spec_path and spec_path.is_file():
        # Monolithic spec
        logger.info("📖 Loaded monolithic spec")
        return spec_path.read_text()
    else:
        return "[NO SPEC FOUND]"
```

**Files to Create/Modify**:
- `coffee_maker/autonomous/daemon_implementation.py` (update error handling)

---

## Acceptance Criteria

**This phase is complete when**:

- [ ] daemon uses SpecHandler.read_hierarchical() to load specs
- [ ] Phase detection integrated (automatic detection via skill)
- [ ] ROADMAP updated with phase checkboxes after completion
- [ ] Context efficiency logged (showing 71% reduction)
- [ ] Error handling for missing phase files
- [ ] Backward compatibility maintained (monolithic specs still work)
- [ ] All existing tests passing
- [ ] Manual testing with hierarchical spec (SPEC-025) successful

**Validation Tests**:
```bash
# Unit tests
pytest tests/unit/test_daemon_implementation.py::test_load_hierarchical_spec -v
pytest tests/unit/test_daemon_implementation.py::test_detect_current_phase -v
pytest tests/unit/test_daemon_implementation.py::test_mark_phase_complete -v

# Integration test
# 1. Create test hierarchical spec (SPEC-999-test-feature/)
# 2. Run daemon with PRIORITY 999
# 3. Verify phase detection works
# 4. Verify ROADMAP updated after commit
# 5. Verify context reduction logged
```

---

## Testing This Phase

### Manual Testing Checklist

1. **Test with hierarchical spec**:
   ```bash
   # Use SPEC-025 (this spec) for testing
   poetry run code-developer --priority=25 --dry-run
   # Expected: Loads README + phase2-daemon-enhancement.md (~150 lines)
   ```

2. **Test with monolithic spec**:
   ```bash
   # Use older spec (e.g., SPEC-020-orchestrator.md)
   poetry run code-developer --priority=20 --dry-run
   # Expected: Loads full monolithic spec, backward compatible
   ```

3. **Test phase detection**:
   ```bash
   # Mark Phase 1 complete in ROADMAP, run daemon
   # Expected: Detects Phase 2, loads phase2-*.md
   ```

4. **Test ROADMAP update**:
   ```bash
   # Run daemon, make commit
   # Expected: ROADMAP updated with "- [x] Phase N complete"
   ```

5. **Test context logging**:
   ```bash
   # Check logs for context efficiency metrics
   # Expected: "Context efficiency: 2456 chars vs ~8500 chars, Savings: 71%"
   ```

---

## References for This Phase

**Code Locations**:
- `coffee_maker/autonomous/daemon_implementation.py` (daemon work loop)
- `coffee_maker/utils/spec_handler.py` (SpecHandler class)
- `.claude/skills/shared/technical-specification-handling/SKILL.md` (skill documentation)

**Related Documents**:
- [CFR-016: Incremental Implementation](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-016)
- [SPEC-NEXT: Design Rationale](../SPEC-NEXT-hierarchical-modular-spec-architecture.md)

**Dependencies**:
- Phase 1: technical-specification-handling v2.0.0 (COMPLETED)

---

## Next Phase

**After completing this phase, proceed to**:
- **[Phase 3: Guidelines Library](phase3-guidelines-library.md)**

**Deliverable Handoff**:
- daemon supports hierarchical specs
- Progressive disclosure working (71% context reduction)
- Phase detection automatic
- ROADMAP tracking phase completion
- Ready to create guidelines for common patterns

---

**Note**: This phase focuses on daemon integration. The shared skill (Phase 1) already implements the core logic. This phase is about wiring up the daemon to use it correctly.
