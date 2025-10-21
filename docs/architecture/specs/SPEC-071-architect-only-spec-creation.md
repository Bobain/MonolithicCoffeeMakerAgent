# SPEC-071: Architect-Only Spec Creation (CFR-008 Enforcement)

**User Story**: [US-047] Enforce CFR-008 Architect-Only Spec Creation

**Status**: Draft

**Created**: 2025-10-18

**Author**: architect agent

**Estimated Effort**: 2-3 days (16-24 hours)

**Related Documents**:
- [CFR-008: Architect-Only Spec Creation](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md)
- [ADR-003: Simplification-First Approach](../decisions/ADR-003-simplification-first-approach.md)
- [US-047](../../roadmap/ROADMAP.md#us-047)

---

## Executive Summary

Enforce **Critical Functional Requirement CFR-008** system-wide: ONLY the architect agent can create technical specifications. code_developer must BLOCK and notify when specs are missing, rather than creating them reactively. This ensures architectural consistency, enables cross-feature optimization, and reduces implementation complexity by 30-87% (per ADR-003).

**Key Changes**:
1. **Remove spec creation from code_developer** - Eliminate fallback template generation
2. **Enforce blocking behavior** - code_developer BLOCKS when spec missing
3. **Clear notifications** - User and architect notified via NotificationDB
4. **Proactive architect workflow** - architect reviews FULL ROADMAP, creates ALL specs
5. **Automated validation** - Pre-flight checks for spec readiness

**Time Savings**:
- **Immediate**: Prevents 2-5 hours/priority wasted on suboptimal implementations
- **Long-term**: 30-87% reduction in implementation complexity (ADR-003)
- **ROI**: 3-5x return on spec creation investment

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Architecture Overview](#architecture-overview)
3. [Component Specifications](#component-specifications)
4. [Implementation Plan](#implementation-plan)
5. [Testing Strategy](#testing-strategy)
6. [Rollout Plan](#rollout-plan)
7. [Success Metrics](#success-metrics)

---

## Problem Statement

### Current State (Problematic)

```
code_developer encounters priority without spec
    ↓
code_developer creates spec using template fallback ❌
    ↓
Spec lacks architectural insight (no cross-feature view)
    ↓
Implementation proceeds with suboptimal design
    ↓
Technical debt accumulates (30-87% more complexity)
```

**Pain Points**:
1. **Separation of Concerns Violated**: code_developer does BOTH design AND implementation
2. **Reactive Spec Creation**: Specs created only when needed, missing optimization opportunities
3. **No Cross-Feature Planning**: Each priority designed in isolation
4. **Architectural Debt**: Suboptimal designs compound over time
5. **Inconsistent Quality**: Template-based specs lack depth and insight

**Quantified Impact** (from ADR-003):
- **Implementation complexity**: 30-87% higher without proactive architectural design
- **Refactoring cost**: 2-4x more expensive to fix after implementation
- **Time wasted**: 2-5 hours/priority on suboptimal implementations

### Desired State (CFR-008 Compliant)

```
architect proactively reviews FULL ROADMAP
    ↓
architect creates specs for ALL priorities requiring design ✅
    ↓
Specs consider cross-feature dependencies and reuse
    ↓
code_developer reads spec, implements exactly as designed
    ↓
Implementation is 30-87% simpler (ADR-003)
```

**Benefits**:
1. **Architectural Consistency**: Single source of design authority
2. **Proactive Optimization**: architect sees full ROADMAP, identifies simplifications
3. **Cross-Feature Synergy**: Shared components, reduced duplication
4. **Quality**: Thoughtful, well-designed specs before any code
5. **Efficiency**: 30-87% reduction in implementation complexity

---

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                   ROADMAP (Source of Truth)                 │
│         docs/roadmap/ROADMAP.md (managed by PM)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌──────────────────┐                  ┌──────────────────┐
│    ARCHITECT     │                  │  CODE_DEVELOPER  │
│  (Proactive)     │                  │   (Reactive)     │
└──────────────────┘                  └──────────────────┘
        ↓                                       ↓
Reviews FULL ROADMAP                  Reads next priority
Creates ALL specs                     Checks for spec
Considers cross-feature               BLOCKS if missing
Optimizes for simplicity              Notifies user/architect
        ↓                                       ↓
┌────────────────────────────────┐    ┌────────────────────┐
│ docs/architecture/specs/       │    │  Notification DB   │
│   SPEC-047-feature.md          │    │  (User Alert)      │
│   SPEC-048-feature.md          │    │                    │
└────────────────────────────────┘    └────────────────────┘
        ↓
code_developer reads spec
Implements exactly as designed
Implementation is 30-87% simpler
```

### System Flow

#### **Flow 1: Architect Proactive Spec Creation** (NEW - Primary Flow)

```
1. architect scheduled task (weekly or on-demand)
   ↓
2. architect reads FULL ROADMAP.md
   ↓
3. architect identifies priorities needing specs:
   - Status: "📝 Planned"
   - Estimated effort > 1 day
   - Technical complexity: Medium/High
   - No existing spec in docs/architecture/specs/
   ↓
4. architect creates specs for ALL identified priorities:
   - Cross-feature dependency analysis
   - Shared component identification
   - Simplification opportunities (ADR-003)
   - Reuse existing patterns
   ↓
5. architect commits specs to docs/architecture/specs/
   - SPEC-047-enforce-architect-only-specs.md
   - SPEC-048-silent-background-agents.md
   - etc.
   ↓
6. code_developer can now implement (specs ready)
```

#### **Flow 2: code_developer Implementation** (UPDATED - Enforcement)

```
1. code_developer reads next priority from ROADMAP
   ↓
2. code_developer checks for technical spec:
   - Priority name: US-047
   - Expected spec prefix: SPEC-047
   - Search: docs/architecture/specs/SPEC-047-*.md
   ↓
3A. Spec exists ✅
    ↓
    code_developer reads spec
    ↓
    code_developer implements exactly as designed
    ↓
    Implementation proceeds normally

3B. Spec missing ❌
    ↓
    code_developer BLOCKS (does NOT create spec)
    ↓
    code_developer creates notification:
        - Title: "CFR-008: Missing Spec for US-047"
        - Level: critical
        - Sound: False (CFR-009)
        - Agent: code_developer
    ↓
    Notification alerts user and architect
    ↓
    User manually invokes architect to create spec
    ↓
    Once spec exists, code_developer resumes
```

#### **Flow 3: Validation & Monitoring** (NEW)

```
1. Pre-flight check (on daemon startup):
   ↓
2. Scan ROADMAP for "📝 Planned" priorities
   ↓
3. Check each priority for spec presence:
   - Effort > 1 day → Spec REQUIRED
   - Effort ≤ 1 day → Spec optional
   ↓
4A. All specs present ✅
    ↓
    Daemon starts normally

4B. Missing specs found ⚠️
    ↓
    Create summary notification:
        - List all priorities missing specs
        - Suggest architect review
        - Continue daemon (non-blocking warning)
```

---

## Component Specifications

### 1. SpecManagerMixin (Updated)

**File**: `coffee_maker/autonomous/daemon_spec_manager.py`

**Current State**: Already has delegation and notification logic (lines 61-203)

**Changes Required**:

#### 1.1. Remove Fallback Spec Creation

**Current Code** (lines 109-146):
```python
# Step 2: Spec missing - Try to create via architect delegation
logger.warning(f"⚠️  Technical spec missing for {priority_name}")
logger.info(f"   Attempting to delegate spec creation to architect via Claude...")

# Build and execute delegation prompt
prompt = self._build_architect_delegation_prompt(priority, spec_prefix)

try:
    result = self.claude.execute_prompt(prompt)
    if result.success:
        logger.info(f"✅ Claude accepted delegation request")
        # Check if spec file was created...
```

**New Code** (SIMPLIFIED):
```python
# Step 2: Spec missing - BLOCK and notify (CFR-008)
logger.error(f"❌ Technical spec REQUIRED but missing for {priority_name}")
logger.error(f"   CFR-008: code_developer CANNOT create specs")
logger.error(f"   → architect must create: docs/architecture/specs/{spec_prefix}-*.md")

# Create notification to alert user and architect
self._notify_spec_missing(priority, spec_prefix)

# Return False to BLOCK implementation
return False
```

**Rationale**: Remove delegation attempt entirely. code_developer should not try to create specs under any circumstances (even via delegation). Clean blocking behavior is clearer.

#### 1.2. Simplify _notify_spec_missing

**Current Code** (lines 148-203): Already correct! Uses NotificationDB.

**Enhancement**: Add more context for actionability

```python
def _notify_spec_missing(self, priority: dict, spec_prefix: str) -> None:
    """Notify user and architect about missing technical specification.

    CFR-008: ARCHITECT-ONLY SPEC CREATION
    """
    priority_name = priority.get("name", "Unknown Priority")
    priority_title = priority.get("title", "Unknown Title")
    priority_effort = priority.get("estimated_effort", "Unknown")

    # Create notification message
    title = f"CFR-008: Missing Spec for {priority_name}"
    message = (
        f"Technical specification REQUIRED for '{priority_title}'.\n\n"
        f"Priority: {priority_name}\n"
        f"Title: {priority_title}\n"
        f"Estimated Effort: {priority_effort}\n"
        f"Expected spec prefix: {spec_prefix}\n\n"
        f"CFR-008 ENFORCEMENT: code_developer cannot create specs.\n"
        f"→ architect must create: docs/architecture/specs/{spec_prefix}-<feature-name>.md\n\n"
        f"Implementation is BLOCKED until architect creates the spec.\n\n"
        f"ACTIONS:\n"
        f"1. Invoke architect agent to create technical spec\n"
        f"2. architect reviews US-047 in ROADMAP.md\n"
        f"3. architect creates comprehensive spec in docs/architecture/specs/\n"
        f"4. code_developer will auto-resume when spec exists"
    )

    context = {
        "priority_name": priority_name,
        "priority_title": priority_title,
        "priority_effort": priority_effort,
        "spec_prefix": spec_prefix,
        "enforcement": "CFR-008",
        "action_required": "architect must create technical spec",
        "spec_directory": "docs/architecture/specs/",
    }

    try:
        self.notifications.create_notification(
            type="error",
            title=title,
            message=message,
            priority="critical",
            context=context,
            sound=False,  # CFR-009: code_developer must use sound=False
            agent_id="code_developer",  # CFR-009: identify calling agent
        )

        logger.info(f"✅ Created CFR-008 notification for {priority_name}")

    except Exception as e:
        logger.error(f"Failed to create notification: {e}", exc_info=True)
        # Don't fail - notification is nice-to-have but not critical
```

#### 1.3. Remove Deprecated Methods

**Delete**:
- `_build_architect_delegation_prompt()` (lines 204-243) - No longer needed
- `_build_spec_creation_prompt()` (lines 245-258) - Deprecated

**Rationale**: Clean up dead code. code_developer doesn't delegate or create specs anymore.

---

### 2. Pre-Flight Validation (NEW)

**File**: `coffee_maker/autonomous/daemon.py` (or new `daemon_validation.py` mixin)

**Purpose**: Warn about missing specs on daemon startup (non-blocking)

**Implementation**:

```python
class ValidationMixin:
    """Mixin providing pre-flight validation for daemon startup."""

    def _validate_spec_readiness(self) -> None:
        """Check if all Planned priorities have technical specs.

        CFR-008 ENFORCEMENT: Pre-flight check

        This runs on daemon startup and warns if priorities are missing specs.
        It's a non-blocking warning (daemon continues), but helps architect
        identify priorities needing specs proactively.

        Example:
            >>> daemon._validate_spec_readiness()
            ⚠️  3 priorities missing technical specs:
               - US-047: Enforce CFR-008 Architect-Only Spec Creation
               - US-048: Enforce CFR-009 Silent Background Agents
               - US-049: Implement User Listener Command
        """
        logger.info("🔍 Validating spec readiness (CFR-008)...")

        # Read ROADMAP
        roadmap = self._read_roadmap()
        if not roadmap:
            logger.warning("⚠️  Could not read ROADMAP - skipping validation")
            return

        # Find all "Planned" priorities
        planned_priorities = [
            p for p in roadmap.get("priorities", [])
            if p.get("status") == "📝 Planned"
        ]

        if not planned_priorities:
            logger.info("✅ No planned priorities - validation skipped")
            return

        # Check each priority for spec
        missing_specs = []

        for priority in planned_priorities:
            priority_name = priority.get("name", "Unknown")
            priority_title = priority.get("title", "Unknown")
            effort = priority.get("estimated_effort", "Unknown")

            # Extract spec prefix
            if priority_name.startswith("US-"):
                spec_number = priority_name.split("-")[1]
                spec_prefix = f"SPEC-{spec_number}"
            elif priority_name.startswith("PRIORITY"):
                priority_num = priority_name.replace("PRIORITY", "").strip()
                if "." in priority_num:
                    major, minor = priority_num.split(".")
                    spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
                else:
                    spec_prefix = f"SPEC-{priority_num.zfill(3)}"
            else:
                spec_prefix = f"SPEC-{priority_name.replace(' ', '-')}"

            # Check if spec exists
            docs_dir = self.roadmap_path.parent.parent
            architect_spec_dir = docs_dir / "architecture" / "specs"

            spec_exists = False
            if architect_spec_dir.exists():
                for spec_file in architect_spec_dir.glob(f"{spec_prefix}-*.md"):
                    spec_exists = True
                    break

            # Add to missing list if:
            # 1. Effort > 1 day (requires spec)
            # 2. Complexity is Medium/High (requires spec)
            if not spec_exists:
                # Parse effort (e.g., "2-3 days" → 2)
                requires_spec = False
                if "day" in effort.lower():
                    try:
                        days = int(effort.split("-")[0].split()[0])
                        if days > 1:
                            requires_spec = True
                    except (ValueError, IndexError):
                        pass  # Can't parse - assume doesn't need spec

                # Also check complexity field if present
                if priority.get("complexity") in ["Medium", "High"]:
                    requires_spec = True

                if requires_spec:
                    missing_specs.append({
                        "name": priority_name,
                        "title": priority_title,
                        "spec_prefix": spec_prefix,
                        "effort": effort,
                    })

        # Report findings
        if missing_specs:
            logger.warning(f"⚠️  {len(missing_specs)} priorities missing technical specs:")
            for spec in missing_specs:
                logger.warning(
                    f"   - {spec['name']}: {spec['title']} "
                    f"(effort: {spec['effort']}, expected: {spec['spec_prefix']}-*.md)"
                )

            logger.warning(
                f"\n💡 CFR-008: architect should create specs proactively in docs/architecture/specs/\n"
            )

            # Create summary notification (non-critical, informational)
            self._notify_spec_readiness_summary(missing_specs)
        else:
            logger.info("✅ All planned priorities have technical specs!")

    def _notify_spec_readiness_summary(self, missing_specs: list) -> None:
        """Create summary notification about missing specs.

        Args:
            missing_specs: List of dicts with priority details
        """
        count = len(missing_specs)

        # Build summary message
        spec_list = "\n".join([
            f"   • {s['name']}: {s['title']} (expected: {s['spec_prefix']}-*.md)"
            for s in missing_specs
        ])

        title = f"CFR-008: {count} Priorities Missing Specs"
        message = (
            f"Pre-flight validation found {count} planned priorities without technical specs:\n\n"
            f"{spec_list}\n\n"
            f"CFR-008 RECOMMENDATION:\n"
            f"→ architect should create these specs proactively in docs/architecture/specs/\n"
            f"→ This prevents blocking when code_developer reaches these priorities\n\n"
            f"NOTE: This is a non-blocking warning. Daemon will continue, but implementation\n"
            f"will block when it reaches priorities without specs."
        )

        context = {
            "missing_count": count,
            "missing_specs": missing_specs,
            "enforcement": "CFR-008",
            "severity": "warning",  # Non-blocking
        }

        try:
            self.notifications.create_notification(
                type="warning",
                title=title,
                message=message,
                priority="medium",
                context=context,
                sound=False,  # CFR-009: code_developer must use sound=False
                agent_id="code_developer",
            )

            logger.info(f"✅ Created spec readiness summary notification")

        except Exception as e:
            logger.error(f"Failed to create notification: {e}", exc_info=True)
```

**Integration in DevDaemon**:

```python
class DevDaemon(SpecManagerMixin, ValidationMixin, ...):

    def run(self):
        """Main daemon loop."""
        logger.info("🤖 Starting code_developer daemon...")

        # CFR-008: Pre-flight validation (check spec readiness)
        self._validate_spec_readiness()

        # Continue with normal daemon loop...
        while self.running:
            # ... existing logic ...
```

---

### 3. Architect Proactive Workflow (MANUAL)

**Purpose**: architect regularly reviews ROADMAP and creates specs

**Process** (Documented in `.claude/agents/architect.md`):

```markdown
# Architect Proactive Spec Creation Workflow

## When to Review ROADMAP

**Frequency**: Weekly or when notified of missing specs

**Trigger Conditions**:
1. CFR-008 notification received (priority blocked)
2. Weekly scheduled review (every Monday)
3. On-demand: User requests spec creation

## Review Process

### Step 1: Read ROADMAP
```bash
cat docs/roadmap/ROADMAP.md | grep "📝 Planned"
```

### Step 2: Identify Priorities Needing Specs

**Criteria**:
- Status: "📝 Planned"
- Estimated effort > 1 day
- Complexity: Medium or High
- No existing spec in docs/architecture/specs/

### Step 3: Prioritize Spec Creation

**Order**:
1. **Critical**: Blocking code_developer (has CFR-008 notification)
2. **High**: Next 2-3 priorities in ROADMAP order
3. **Medium**: Remaining planned priorities

### Step 4: Create Specs

**For each priority**:
1. Read full priority description in ROADMAP
2. Review related user stories, ADRs, specs
3. Analyze cross-feature dependencies
4. Identify reuse opportunities (ADR-003)
5. Design architecture with simplification first
6. Create comprehensive spec in docs/architecture/specs/

**Spec Template**: docs/templates/TECHNICAL_SPEC_TEMPLATE.md

**Naming Convention**: SPEC-{number}-{feature-slug}.md
- US-047 → SPEC-047-architect-only-spec-creation.md
- PRIORITY 5 → SPEC-005-streamlit-dashboard.md

### Step 5: Commit Specs

```bash
git add docs/architecture/specs/SPEC-*.md
git commit -m "docs: Add technical specs for US-047, US-048, US-049

Created comprehensive architectural specifications for:
- SPEC-047: Architect-Only Spec Creation (CFR-008)
- SPEC-048: Silent Background Agents (CFR-009)
- SPEC-049: User Listener Command

Each spec includes:
- Architecture overview with diagrams
- Component specifications with APIs
- Implementation plan with phases
- Testing strategy with coverage targets
- Rollout plan with timelines

These specs enable code_developer to implement with 30-87%
reduced complexity (per ADR-003 simplification principles).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 6: Notify code_developer

**If blocking**: Respond to CFR-008 notification
**If proactive**: Create informational notification

```python
notifications.create_notification(
    type="info",
    title="Specs Created for US-047, US-048, US-049",
    message="architect has created technical specifications. code_developer can now implement.",
    priority="medium",
    sound=False,
    agent_id="architect"
)
```
```

---

### 4. Documentation Updates

#### 4.1. Update CLAUDE.md

**Section**: Coding Standards → Architecture Patterns

**Add**:
```markdown
### Technical Specification Workflow (CFR-008) ⭐ CRITICAL

**IMPORTANT**: ONLY architect creates technical specifications.

**Architect Responsibilities**:
- Proactively review FULL ROADMAP (weekly or on-demand)
- Create specs for ALL planned priorities (effort > 1 day)
- Consider cross-feature dependencies and reuse
- Optimize for simplification (ADR-003: 30-87% complexity reduction)
- Save specs to `docs/architecture/specs/SPEC-{number}-{feature}.md`

**code_developer Responsibilities**:
- Check for spec existence before starting work
- BLOCK if spec missing (do NOT create spec)
- Notify user and architect via NotificationDB
- Implement exactly as spec describes (no deviation)
- NEVER create or modify specs (read-only)

**Correct Flow**:
```
architect (weekly):
  → Reviews ROADMAP for "📝 Planned" priorities
  → Creates ALL needed specs proactively
  → Commits to docs/architecture/specs/

code_developer (continuous):
  → Reads next priority
  → Checks for spec (docs/architecture/specs/SPEC-{number}-*.md)
  → If spec exists: implement
  → If spec missing: BLOCK + notify
```

**Examples**:
```bash
# ✅ CORRECT: architect creates spec proactively
# (architect agent, before code_developer starts work)
cat > docs/architecture/specs/SPEC-047-architect-only-specs.md
git add docs/architecture/specs/SPEC-047-architect-only-specs.md
git commit -m "docs: Add SPEC-047 for CFR-008 enforcement"

# ✅ CORRECT: code_developer blocks when spec missing
# (code_developer daemon, during implementation)
logger.error("❌ Spec REQUIRED but missing for US-047")
self._notify_spec_missing(priority, "SPEC-047")
return False  # BLOCK implementation

# ❌ INCORRECT: code_developer tries to create spec
# (This should NEVER happen - CFR-008 violation)
self.claude.execute_prompt(spec_creation_prompt)  # ❌ WRONG!
```
```

#### 4.2. Update .claude/agents/architect.md

**Add Section**: Proactive Spec Creation

(See section 3 above for full content)

#### 4.3. Update .claude/agents/code_developer.md

**Update Section**: Technical Specifications

```markdown
## Technical Specifications (CFR-008)

**CRITICAL**: code_developer CANNOT create technical specifications.

**Spec Check Process**:
1. Read next priority from ROADMAP
2. Extract spec prefix (US-047 → SPEC-047)
3. Search: docs/architecture/specs/SPEC-047-*.md
4. If spec exists: read and implement
5. If spec missing: BLOCK and notify

**Blocking Behavior**:
```python
if not self._ensure_technical_spec(priority):
    # Spec missing - implementation BLOCKED
    # Notification sent to user and architect
    # Daemon skips this priority and waits
    continue
```

**Notification**:
- Title: "CFR-008: Missing Spec for {priority}"
- Level: critical
- Sound: False (CFR-009)
- Agent: code_developer
- Action: architect must create spec

**DO NOT**:
- ❌ Create specs (even via delegation)
- ❌ Modify existing specs
- ❌ Use template fallbacks
- ❌ Implement without spec (if effort > 1 day)

**DO**:
- ✅ Check for spec existence
- ✅ BLOCK if spec missing
- ✅ Notify user and architect
- ✅ Read spec and implement exactly as designed
```

---

## Implementation Plan

### Phase 1: Remove Spec Creation from code_developer (Day 1, 4-6 hours)

**Tasks**:
1. Update `daemon_spec_manager.py`:
   - Simplify `_ensure_technical_spec()` to remove delegation logic
   - Keep blocking and notification logic
   - Delete `_build_architect_delegation_prompt()`
   - Delete `_build_spec_creation_prompt()`

2. Enhance `_notify_spec_missing()`:
   - Add estimated effort to context
   - Add actionable steps for user
   - Improve message clarity

3. Update `code_developer.md` documentation:
   - Document blocking behavior
   - Add examples of correct/incorrect usage
   - Link to CFR-008

4. Write unit tests:
   - Test blocking when spec missing
   - Test notification creation
   - Test spec existence check

**Acceptance Criteria**:
- [ ] code_developer CANNOT create specs (logic removed)
- [ ] code_developer BLOCKS when spec missing
- [ ] Notification created with actionable guidance
- [ ] Unit tests pass (100% coverage)

---

### Phase 2: Pre-Flight Validation (Day 2, 4-6 hours)

**Tasks**:
1. Create `daemon_validation.py` mixin:
   - Implement `_validate_spec_readiness()`
   - Implement `_notify_spec_readiness_summary()`

2. Integrate validation into `DevDaemon.run()`:
   - Call `_validate_spec_readiness()` on startup
   - Log warnings for missing specs
   - Create summary notification

3. Update `CLAUDE.md` documentation:
   - Add CFR-008 enforcement section
   - Document correct flow
   - Provide examples

4. Write integration tests:
   - Test validation with missing specs
   - Test validation with all specs present
   - Test summary notification

**Acceptance Criteria**:
- [ ] Pre-flight validation runs on daemon startup
- [ ] Summary notification created when specs missing
- [ ] Validation is non-blocking (daemon continues)
- [ ] Integration tests pass

---

### Phase 3: Architect Proactive Workflow (Day 3, 2-4 hours)

**Tasks**:
1. Create/update `architect.md`:
   - Document proactive spec creation workflow
   - Add review schedule (weekly)
   - Provide spec template reference
   - Add commit message examples

2. Create spec template (if not exists):
   - `docs/templates/TECHNICAL_SPEC_TEMPLATE.md`
   - Include all standard sections
   - Provide examples

3. Document in CLAUDE.md:
   - Add architect responsibilities
   - Add code_developer responsibilities
   - Show correct flow diagram

4. Create example specs:
   - SPEC-047 (this document) ✅
   - SPEC-048 (Silent Background Agents)
   - SPEC-049 (User Listener Command)

**Acceptance Criteria**:
- [ ] architect.md documents proactive workflow
- [ ] Spec template exists and is comprehensive
- [ ] CLAUDE.md updated with CFR-008 section
- [ ] Example specs created for next 3 priorities

---

### Phase 4: Testing & Validation (Day 3, 2-4 hours)

**Tasks**:
1. Write comprehensive tests:
   - Unit tests for all modified methods
   - Integration tests for full flow
   - End-to-end tests (daemon startup → blocking → notification)

2. Test scenarios:
   - Spec exists → Implementation proceeds
   - Spec missing → Blocking + notification
   - Pre-flight validation → Summary notification
   - Multiple missing specs → Correct count

3. Manual testing:
   - Start daemon with missing spec
   - Verify notification appears
   - Create spec as architect
   - Verify daemon resumes

4. Code review:
   - Review all changes
   - Verify CFR-008 compliance
   - Check for edge cases
   - Validate error handling

**Acceptance Criteria**:
- [ ] All unit tests pass (100% coverage)
- [ ] All integration tests pass
- [ ] Manual testing successful
- [ ] Code review complete

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_daemon_spec_manager.py`

**Test Coverage**:

```python
class TestSpecManagerMixin:
    """Test spec creation blocking and notification."""

    def test_ensure_spec_exists_returns_true_when_spec_found(self):
        """Test that _ensure_technical_spec returns True when spec exists."""
        # Setup: Create mock spec file
        # Execute: _ensure_technical_spec(priority)
        # Assert: Returns True

    def test_ensure_spec_blocks_when_spec_missing(self):
        """Test that _ensure_technical_spec returns False when spec missing."""
        # Setup: No spec file
        # Execute: _ensure_technical_spec(priority)
        # Assert: Returns False (BLOCKS)

    def test_notify_spec_missing_creates_notification(self):
        """Test that notification is created when spec missing."""
        # Setup: Mock NotificationDB
        # Execute: _notify_spec_missing(priority, spec_prefix)
        # Assert: create_notification called with correct params

    def test_notify_includes_actionable_steps(self):
        """Test that notification includes actionable guidance."""
        # Setup: Mock NotificationDB
        # Execute: _notify_spec_missing(priority, spec_prefix)
        # Assert: Message contains architect action steps

    def test_delegation_methods_removed(self):
        """Test that delegation methods no longer exist."""
        # Assert: _build_architect_delegation_prompt not in dir(mixin)
        # Assert: _build_spec_creation_prompt not in dir(mixin)
```

**File**: `tests/unit/test_daemon_validation.py`

**Test Coverage**:

```python
class TestValidationMixin:
    """Test pre-flight spec readiness validation."""

    def test_validate_finds_missing_specs(self):
        """Test that validation identifies priorities without specs."""
        # Setup: ROADMAP with 3 planned priorities, 1 missing spec
        # Execute: _validate_spec_readiness()
        # Assert: Logs warning for 1 missing spec

    def test_validate_passes_when_all_specs_present(self):
        """Test that validation passes when all specs exist."""
        # Setup: ROADMAP with 3 planned priorities, all have specs
        # Execute: _validate_spec_readiness()
        # Assert: Logs success message

    def test_validate_creates_summary_notification(self):
        """Test that summary notification created when specs missing."""
        # Setup: Mock NotificationDB, missing specs
        # Execute: _validate_spec_readiness()
        # Assert: create_notification called with summary

    def test_validate_skips_low_effort_priorities(self):
        """Test that priorities < 1 day don't require specs."""
        # Setup: ROADMAP with priority (effort: "4 hours")
        # Execute: _validate_spec_readiness()
        # Assert: No warning for this priority
```

### Integration Tests

**File**: `tests/integration/test_cfr_008_enforcement.py`

**Test Coverage**:

```python
class TestCFR008Enforcement:
    """Integration tests for CFR-008 architect-only spec creation."""

    def test_daemon_blocks_on_missing_spec(self):
        """Test that daemon blocks when spec missing."""
        # Setup: ROADMAP with US-047, no spec
        # Execute: Start daemon
        # Assert: Daemon blocks, notification created, logs error

    def test_daemon_proceeds_when_spec_exists(self):
        """Test that daemon proceeds when spec exists."""
        # Setup: ROADMAP with US-047, spec exists
        # Execute: Start daemon
        # Assert: Implementation proceeds normally

    def test_pre_flight_validation_on_startup(self):
        """Test that pre-flight validation runs on startup."""
        # Setup: ROADMAP with missing specs
        # Execute: Start daemon
        # Assert: Summary notification created, daemon continues

    def test_full_cycle_architect_creates_spec(self):
        """Test full cycle: blocking → architect creates spec → resume."""
        # 1. Start daemon (blocks on missing spec)
        # 2. Architect creates spec
        # 3. Daemon detects spec and resumes
        # Assert: Implementation completes successfully
```

### Manual Testing Checklist

- [ ] Start daemon with missing spec for US-047
- [ ] Verify error logs: "❌ Technical spec REQUIRED but missing"
- [ ] Verify notification appears in NotificationDB
- [ ] Create SPEC-047 manually as architect
- [ ] Verify daemon resumes on next iteration
- [ ] Check implementation proceeds normally
- [ ] Verify pre-flight validation on fresh daemon start
- [ ] Verify summary notification for multiple missing specs

---

## Rollout Plan

### Week 1: Development & Testing

**Day 1** (4-6 hours):
- Implement Phase 1: Remove spec creation from code_developer
- Write unit tests for SpecManagerMixin
- Manual testing of blocking behavior

**Day 2** (4-6 hours):
- Implement Phase 2: Pre-flight validation
- Write unit tests for ValidationMixin
- Integration tests for full flow

**Day 3** (4-6 hours):
- Implement Phase 3: Architect workflow documentation
- Create spec template
- Create example specs for US-048, US-049
- Final testing and validation

### Week 2: Deployment & Monitoring

**Day 4** (2 hours):
- Deploy to production
- Monitor daemon behavior
- Track CFR-008 notifications

**Day 5-7** (Ongoing):
- architect reviews ROADMAP (weekly task)
- Create missing specs proactively
- Monitor spec readiness metrics
- Adjust validation thresholds if needed

---

## Success Metrics

### Immediate Metrics (Week 1)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Spec Creation Blocked** | 100% | code_developer never creates specs |
| **Notifications Created** | 100% | Every missing spec triggers notification |
| **Pre-Flight Validation** | 100% | Runs on every daemon startup |
| **Blocking Correct** | 100% | Implementation blocked when spec missing |
| **Test Coverage** | 100% | All new code covered by tests |

### Long-Term Metrics (Month 1-3)

| Metric | Baseline | Target (Month 1) | Target (Month 3) |
|--------|----------|------------------|------------------|
| **Spec Readiness** | 30% | 70% | 90% |
| **Proactive Specs** | 0% | 60% | 80% |
| **Implementation Complexity** | Baseline | -20% | -40% |
| **Refactoring Cost** | Baseline | -30% | -50% |
| **Architectural Reuse** | 10% | 30% | 50% |

**Definitions**:
- **Spec Readiness**: % of planned priorities with specs BEFORE code_developer starts
- **Proactive Specs**: % of specs created by architect before blocking
- **Implementation Complexity**: LOC, cyclomatic complexity, file count
- **Refactoring Cost**: Time spent refactoring after initial implementation
- **Architectural Reuse**: % of specs using shared components

### Quality Metrics (Ongoing)

| Metric | Target | Frequency |
|--------|--------|-----------|
| **CFR-008 Violations** | 0 | Daily |
| **Spec Coverage** | >80% | Weekly |
| **Spec Quality Score** | >8/10 | Per spec |
| **User Satisfaction** | >9/10 | Monthly |

---

## Risk Assessment

### Risk 1: Architect Bottleneck 🟠 MEDIUM

**Description**: architect becomes bottleneck if too many priorities need specs

**Impact**: code_developer blocked frequently, development slows down

**Mitigation**:
- **Proactive Review**: architect reviews ROADMAP weekly (not reactively)
- **Batch Creation**: architect creates 3-5 specs at once
- **Prioritization**: architect focuses on next 2-3 priorities in queue
- **Template**: Use spec template to speed up creation (50% faster)
- **Delegation**: For simple priorities, architect can create lightweight specs

**Monitoring**:
- Track: % of time code_developer is blocked waiting for specs
- Alert if blocking >20% of the time
- Reevaluate if sustained blocking for >1 week

### Risk 2: Spec Quality Varies 🟡 LOW

**Description**: Proactive specs may be lower quality (less context)

**Impact**: Implementation takes longer, more questions, suboptimal design

**Mitigation**:
- **Spec Template**: Standard structure ensures consistency
- **Review Process**: architect reviews own specs before committing
- **User Feedback**: code_developer can request clarifications
- **Iterative**: Specs can be updated based on implementation learnings
- **Quality Checklist**: architect uses checklist (ADR-003 principles)

**Monitoring**:
- Track: Spec quality score (user feedback, implementation time)
- Track: # of clarification requests per spec
- Reevaluate if quality <7/10 consistently

### Risk 3: Over-Specification 🟢 LOW

**Description**: architect creates overly detailed specs (wasted effort)

**Impact**: Spec creation takes too long, specs become stale

**Mitigation**:
- **Right-Sized Specs**: Match detail level to priority complexity
- **Effort Guidelines**: 1-2 hours for simple, 4-6 hours for complex
- **Focus on Architecture**: Don't specify implementation details
- **Living Documents**: Specs can evolve during implementation
- **Feedback Loop**: code_developer provides feedback on spec usefulness

**Monitoring**:
- Track: Time spent per spec vs. implementation time
- Alert if spec creation >30% of implementation time
- Adjust detail level based on feedback

### Risk 4: Urgent Priorities Blocked 🟠 MEDIUM

**Description**: Urgent bug fixes blocked by missing spec requirement

**Impact**: Production incidents delayed, user frustration

**Mitigation**:
- **Exemption for Hotfixes**: Priorities tagged "hotfix" skip spec requirement
- **Lightweight Specs**: architect can create minimal spec in 30 min for urgent items
- **Async Spec**: architect creates spec during implementation (parallel)
- **Post-Hoc Spec**: For true emergencies, spec created after implementation
- **Priority Escalation**: User can request immediate architect support

**Monitoring**:
- Track: # of urgent priorities blocked
- Track: Time to create urgent specs
- Adjust exemption criteria if blocking critical work

---

## Appendix

### A. Spec Naming Convention

**Format**: `SPEC-{number}-{feature-slug}.md`

**Examples**:
- US-047 → `SPEC-047-architect-only-spec-creation.md`
- US-048 → `SPEC-048-silent-background-agents.md`
- PRIORITY 5 → `SPEC-005-streamlit-dashboard.md`
- PRIORITY 10.5 → `SPEC-010-5-user-listener-command.md`

**Rules**:
- Use priority number from ROADMAP (US-XXX, PRIORITY XXX)
- Zero-pad numbers to 3 digits for PRIORITY (SPEC-005 not SPEC-5)
- Use hyphens for multi-part numbers (10.5 → 010-5)
- Feature slug is lowercase, hyphen-separated, descriptive
- Extension is always `.md` (Markdown)

### B. Spec Template Reference

**Location**: `docs/templates/TECHNICAL_SPEC_TEMPLATE.md`

**Sections**:
1. Header (title, status, author, dates)
2. Executive Summary
3. Problem Statement
4. Architecture Overview
5. Component Specifications
6. API Contracts
7. Data Models
8. Implementation Plan
9. Testing Strategy
10. Rollout Plan
11. Success Metrics
12. Risk Assessment

**Example**: This document (SPEC-071) follows the template.

### C. Related Documents

- [CFR-008: Architect-Only Spec Creation](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-008)
- [ADR-003: Simplification-First Approach](../decisions/ADR-003-simplification-first-approach.md)
- [US-047: Enforce CFR-008](../../roadmap/ROADMAP.md#us-047)
- [Spec Template](../../templates/TECHNICAL_SPEC_TEMPLATE.md)
- [Architect Agent Definition](.claude/agents/architect.md)
- [code_developer Agent Definition](.claude/agents/code_developer.md)

---

**Created**: 2025-10-18
**Author**: architect agent
**Version**: 1.0
**Status**: Draft (Pending Review)
