# project_manager CFR-015 Violation: Reading ROADMAP.md File Instead of Database

**Date**: 2025-10-23
**Severity**: 🔴 **CRITICAL** - Violates CFR-015 (database-only pattern)
**Agent**: project_manager
**Type**: File access violation

---

## Executive Summary

The **project_manager agent prompt** instructs reading `docs/roadmap/ROADMAP.md` file directly, violating CFR-015 which mandates database-only access. A proper `RoadmapDBSkill` exists but is not being used.

---

## The Violation

### Location: `.claude/agents/project_manager.md`

**Multiple references to direct file access**:

- **Line 94**: `1. **docs/roadmap/ROADMAP.md** 🔴 REQUIRED`
- **Line 134**: `Read docs/roadmap/ROADMAP.md → Understand current project status`
- **Line 142**: `→ Read docs/roadmap/ROADMAP.md, analyze priorities`
- **Line 145**: `→ Check docs/roadmap/ROADMAP.md status`
- **Line 148**: `→ Analyze docs/roadmap/ROADMAP.md`
- **Line 154**: `📊 Project status: docs/roadmap/ROADMAP.md`
- **Line 164**: `docs/roadmap/ROADMAP.md - Master task list (owns this file)`
- **Line 214**: `**Read**: Parse and understand ROADMAP.md`
- **Line 391**: `docs/roadmap/ROADMAP.md - Master task list`
- **Line 529**: `health_check: ROADMAP.md (ultra-compact summary)`
- **Line 538**: `docs/roadmap/ directory writable`
- **Line 539**: `ROADMAP.md readable`
- **Line 558**: `✅ ROADMAP.md readable`
- **Line 578**: `file_read - File read operations (e.g., ROADMAP.md)`
- **Line 602**: `"file": "docs/roadmap/ROADMAP.md"`
- **Line 639**: `Loads ROADMAP.md (ultra-compact summary)`
- **Line 909**: `**ROADMAP Parser**: Read/analyze ROADMAP.md`

### What the Prompt Says (INCORRECT ❌):

```markdown
**MANDATORY - Read these BEFORE responding to users**:

1. **`docs/roadmap/ROADMAP.md`** 🔴 REQUIRED
   - Master project task list and status
   - All priorities, their status, and completion dates
   - Current work in progress
```

```markdown
### ⚡ Startup Checklist

Every time you start a session:
- [ ] Read `docs/roadmap/ROADMAP.md` → Understand current project status
```

```markdown
**"What's the project status?"**
→ Read `docs/roadmap/ROADMAP.md`, analyze priorities, provide summary
```

---

## What Should Be Used Instead

### The Correct Skill: `RoadmapDBSkill`

**Location**: `.claude/skills/shared/roadmap_database_handling/roadmap_db_skill.py`

**Explicit Instructions** (lines 51-56):
```python
IMPORTANT Rules:
    1. NEVER read/write ROADMAP.md file directly
    2. Always use RoadmapDatabaseV2 for roadmap operations
    3. Non-PM agents must use notifications for status updates
    4. project_manager reviews and approves all notifications
    5. Database is the single source of truth for roadmap
```

### Correct Usage Pattern:

```python
import sys
sys.path.insert(0, '.claude/skills/shared/roadmap_database_handling')
from roadmap_db_skill import RoadmapDBSkill

# Initialize with agent name
roadmap_skill = RoadmapDBSkill(agent_name="project_manager")

# Read operations (database-only)
all_items = roadmap_skill.get_all_items()
next_priority = roadmap_skill.get_next_priority()
item = roadmap_skill.get_item_by_id("PRIORITY-27")
stats = roadmap_skill.get_stats()

# Write operations (project_manager only)
if roadmap_skill.can_write:
    roadmap_skill.update_status("PRIORITY-27", "✅ Complete", "project_manager")
    roadmap_skill.link_spec_to_item("PRIORITY-27", "SPEC-115")
```

### Available Database Methods:

From `RoadmapDatabaseV2` (via `RoadmapDBSkill`):

**Read Operations** (all agents):
- `get_all_items()` - Get all roadmap items
- `get_next_planned()` - Get next planned priority
- `get_item(item_id)` - Get specific item by ID
- `get_items_by_status(status)` - Get items with specific status
- `get_stats()` - Get roadmap statistics
- `search_items(query)` - Search roadmap items

**Write Operations** (project_manager only):
- `create_item(item_data)` - Create new roadmap item
- `update_status(item_id, new_status, updated_by)` - Update item status
- `update_item(item_id, updates, updated_by)` - Update item fields
- `link_spec(item_id, spec_id, updated_by)` - Link technical spec
- `approve_notification(notification_id, approver)` - Process notifications

---

## Why This is Critical

### 1. Violates CFR-015 (Database-Only Pattern)

**CFR-015 States**:
> ALL database files MUST be stored in `data/` directory ONLY.
> Database is the single source of truth.
> File-based operations FORBIDDEN.

**Impact**:
- Inconsistency between file and database
- Race conditions
- Data integrity issues
- Workflow automation broken

### 2. Breaks Workflow Automation

**Current (Broken)**:
```
architect creates spec
    ↓
Notification created in database ✅
    ↓
project_manager reads ROADMAP.md file ❌
    ↓
File doesn't have notification data
    ↓
Spec never linked
    ↓
Workflow stalled
```

**Should Be**:
```
architect creates spec
    ↓
Notification created in database ✅
    ↓
orchestrator dispatches notification to project_manager
    ↓
project_manager uses RoadmapDBSkill to read database ✅
    ↓
project_manager sees notification
    ↓
project_manager links spec to roadmap item
    ↓
Workflow continues ✅
```

### 3. Database vs File Divergence

**If both exist**:
- `docs/roadmap/ROADMAP.md` (file) - may be outdated
- `roadmap_items` table (database) - current source of truth

**Problems**:
- project_manager reads file → gets stale data
- Other agents use database → sees current data
- Conflicting views of project status
- Decisions made on wrong information

### 4. No Notification Processing

**Current Flow**:
```
Agents create notifications in database
    ↓
project_manager reads ROADMAP.md file (not database)
    ↓
Notifications never seen
    ↓
Never processed
    ↓
Workflow deadlock
```

**Correct Flow**:
```
Agents create notifications in database
    ↓
orchestrator dispatches to project_manager
    ↓
project_manager uses RoadmapDBSkill
    ↓
Reads notifications from database
    ↓
Processes and approves them
    ↓
Workflow proceeds
```

---

## Impact Assessment

### What Breaks:

1. ❌ **Spec Linking**: architect creates spec → notification ignored → spec never linked to roadmap
2. ❌ **Status Updates**: code_developer completes work → notification ignored → status never updates
3. ❌ **Workflow Automation**: All notifications ignored → complete workflow failure
4. ❌ **Data Consistency**: File and database diverge → conflicting project state
5. ❌ **Agent Coordination**: Agents use database, PM uses file → no shared state

### Severity: 🔴 CRITICAL

**Probability of Deadlock**: 100% (guaranteed)
**Impact**: Complete workflow failure
**Blocks**: ALL roadmap progress

---

## The Fix

### Step 1: Update project_manager.md Prompt

**File**: `.claude/agents/project_manager.md`

**Replace ALL references to `docs/roadmap/ROADMAP.md` with database access**:

#### Before (INCORRECT ❌):
```markdown
**MANDATORY - Read these BEFORE responding to users**:

1. **`docs/roadmap/ROADMAP.md`** 🔴 REQUIRED
   - Master project task list and status
```

#### After (CORRECT ✅):
```markdown
**MANDATORY - Use these BEFORE responding to users**:

1. **RoadmapDBSkill (Database Access)** 🔴 REQUIRED
   - Master project task list and status
   - Access via: `RoadmapDBSkill(agent_name="project_manager")`
   - NEVER read ROADMAP.md file directly (CFR-015 violation)
```

#### Before (INCORRECT ❌):
```markdown
### ⚡ Startup Checklist

Every time you start a session:
- [ ] Read `docs/roadmap/ROADMAP.md` → Understand current project status
```

#### After (CORRECT ✅):
```markdown
### ⚡ Startup Checklist

Every time you start a session:
- [ ] Use RoadmapDBSkill to query database → Understand current project status
- [ ] Check pending notifications → Process orchestrator dispatches
- [ ] NEVER read ROADMAP.md file (use database only)
```

#### Before (INCORRECT ❌):
```markdown
**"What's the project status?"**
→ Read `docs/roadmap/ROADMAP.md`, analyze priorities, provide summary
```

#### After (CORRECT ✅):
```markdown
**"What's the project status?"**
→ Use RoadmapDBSkill.get_all_items(), analyze priorities, provide summary

**Example**:
```python
from roadmap_db_skill import RoadmapDBSkill
skill = RoadmapDBSkill(agent_name="project_manager")
items = skill.get_all_items()
stats = skill.get_stats()
# Analyze and report status
```

### Step 2: Add Database Usage Instructions

Add new section to project_manager.md:

```markdown
## Database-Only Access (CFR-015) 🔴 MANDATORY

### Roadmap Database Access

**NEVER read/write ROADMAP.md file directly!**

Use `RoadmapDBSkill` for all roadmap operations:

```python
import sys
sys.path.insert(0, '.claude/skills/shared/roadmap_database_handling')
from roadmap_db_skill import RoadmapDBSkill

# Initialize
skill = RoadmapDBSkill(agent_name="project_manager")

# Query roadmap
all_items = skill.get_all_items()
next_priority = skill.get_next_priority()
item = skill.get_item_by_id("PRIORITY-27")

# Get pending notifications (from orchestrator)
notifications = skill.get_pending_notifications()
for notif in notifications:
    # Process notification
    skill.approve_notification(notif['id'], "project_manager")

# Update status (project_manager only)
skill.update_status("PRIORITY-27", "✅ Complete", "project_manager")

# Link spec to roadmap
skill.link_spec("PRIORITY-27", "SPEC-115", "project_manager")
```

### Why Database-Only?

1. ✅ Single source of truth
2. ✅ ACID transactions (no race conditions)
3. ✅ Foreign key integrity (specs linked to roadmap)
4. ✅ Notification system integration
5. ✅ Audit trail for all changes
6. ✅ Queryable and automatable
7. ✅ Real-time updates (no file parsing delays)

### File Access is FORBIDDEN

**Never do this**:
```python
# ❌ WRONG - Violates CFR-015
with open("docs/roadmap/ROADMAP.md") as f:
    content = f.read()

# ❌ WRONG - Violates CFR-015
from pathlib import Path
roadmap = Path("docs/roadmap/ROADMAP.md").read_text()
```

**Always do this**:
```python
# ✅ CORRECT - Uses database
skill = RoadmapDBSkill(agent_name="project_manager")
items = skill.get_all_items()
```
```

### Step 3: Add Notification Processing

Add section about processing notifications from orchestrator:

```markdown
## Notification Processing (Orchestrator Integration)

### How Notifications Work

1. **Agents create notifications** in database:
   - architect creates spec → notification for project_manager
   - code_developer completes work → notification for project_manager
   - code_reviewer finds issues → notification for architect

2. **Orchestrator dispatches** notifications:
   - Polls database for pending notifications
   - Routes to target agent (project_manager, architect, etc.)
   - Agents receive and process

3. **project_manager processes** notifications:
   - Links specs to roadmap items
   - Updates roadmap status
   - Approves/processes requests
   - Marks notification as processed

### Processing Notifications

```python
# Get notifications dispatched by orchestrator
skill = RoadmapDBSkill(agent_name="project_manager")
notifications = skill.get_pending_notifications(target_agent="project_manager")

for notif in notifications:
    notification_type = notif['notification_type']

    if notification_type == 'spec_complete':
        # Link spec to roadmap
        item_id = notif['item_id']  # e.g., "PRIORITY-27"
        spec_id = notif['spec_id']  # e.g., "SPEC-115"
        skill.link_spec(item_id, spec_id, "project_manager")

    elif notification_type == 'implementation_complete':
        # Update roadmap status
        item_id = notif['item_id']
        skill.update_status(item_id, "✅ Complete", "project_manager")

    elif notification_type == 'status_update':
        # Process status update request
        item_id = notif['item_id']
        new_status = notif['requested_status']
        skill.update_status(item_id, new_status, "project_manager")

    # Mark notification as processed
    skill.mark_notification_processed(notif['id'], "project_manager")
```

### Notification Types project_manager Handles

- `spec_complete` - architect finished spec, needs linking to roadmap
- `spec_approved` - Spec approved and ready for implementation
- `implementation_complete` - code_developer finished work
- `status_update` - Request to update roadmap status
- `priority_blocked` - Task blocked, needs attention
- `dod_verification_needed` - Implementation needs DoD verification
```

---

## Testing Requirements

### Test 1: Database Access Works
```python
def test_project_manager_uses_database():
    skill = RoadmapDBSkill(agent_name="project_manager")
    items = skill.get_all_items()
    assert len(items) > 0
    assert all('id' in item for item in items)
```

### Test 2: No File Access
```python
def test_no_file_access_in_prompt():
    prompt_path = Path(".claude/agents/project_manager.md")
    content = prompt_path.read_text()

    # Should NOT contain file references
    assert "docs/roadmap/ROADMAP.md" not in content
    assert "Read `docs/roadmap/ROADMAP.md`" not in content

    # Should contain database references
    assert "RoadmapDBSkill" in content
    assert "database" in content.lower()
```

### Test 3: Notification Processing
```python
def test_project_manager_processes_notifications():
    # Create test notification
    create_notification(
        target_agent="project_manager",
        notification_type="spec_complete",
        item_id="TEST-001",
        spec_id="SPEC-999"
    )

    # project_manager should process it
    skill = RoadmapDBSkill(agent_name="project_manager")
    notifications = skill.get_pending_notifications()
    assert len(notifications) > 0

    # Process and verify
    skill.process_notification(notifications[0]['id'])
    item = skill.get_item_by_id("TEST-001")
    assert item['spec_id'] == "SPEC-999"
```

---

## Implementation Plan

### Phase 1: Update Prompt (1 hour)
- [ ] Replace all ROADMAP.md references with RoadmapDBSkill
- [ ] Add database-only usage section
- [ ] Add notification processing section
- [ ] Remove file access instructions

### Phase 2: Add Database Methods (2 hours)
- [ ] Add `get_pending_notifications()` to RoadmapDBSkill
- [ ] Add `mark_notification_processed()` to RoadmapDBSkill
- [ ] Add `link_spec()` method
- [ ] Test all methods

### Phase 3: Test and Validate (1 hour)
- [ ] Test database access works
- [ ] Test notification processing
- [ ] Verify no file access
- [ ] End-to-end workflow test

### Phase 4: Documentation (1 hour)
- [ ] Update CLAUDE.md with corrected pattern
- [ ] Update WORKFLOWS.md
- [ ] Add examples to project_manager.md

**Total Effort**: ~5 hours

---

## Related Issues

This violation is part of a larger pattern:

1. **code_reviewer writes to files** (REVIEW-*.md) instead of database
2. **project_manager reads from files** (ROADMAP.md) instead of database
3. **orchestrator doesn't process notifications** from database

All three must be fixed for workflow automation to work.

---

## Success Criteria

### Fixed When:

- ✅ project_manager.md contains ZERO references to ROADMAP.md file
- ✅ project_manager.md instructs using RoadmapDBSkill exclusively
- ✅ project_manager can read notifications from database
- ✅ project_manager can link specs to roadmap via database
- ✅ project_manager can update status via database
- ✅ No file I/O operations in project_manager workflow
- ✅ End-to-end workflow test passes

---

## Conclusion

**Current State**: project_manager violates CFR-015 by reading ROADMAP.md file

**Correct Pattern**: Use RoadmapDBSkill for database-only access

**Urgency**: 🔴 **CRITICAL** - Blocks workflow automation

**Effort**: ~5 hours

**Next Steps**:
1. Update project_manager.md prompt
2. Add notification processing
3. Test and validate
4. Remove all file references

---

**Last Updated**: 2025-10-23
**Status**: Draft - Needs Implementation
**Related**: PRIORITY 27-30 (workflow issues)
