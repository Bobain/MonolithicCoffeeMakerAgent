# CFR-000: File Conflict Prevention via Controlled Parallelization

**Version**: 3.0 (Updated for parallel development support)
**Date**: 2025-10-23
**Status**: Active
**Owner**: architect + orchestrator

---

## Core Principle

**AT ANY GIVEN MOMENT, for ANY file in the system:**
- EXACTLY ZERO or ONE agent is writing to that file
- NEVER two or more agents writing to the same file simultaneously

This is achieved through **controlled parallelization with git worktrees**, not strict singleton enforcement.

---

## Parallel Development Model

### Previous Understanding (INCORRECT)

❌ **Old CFR-000**: Only ONE instance of code_developer can run at a time (singleton)

### Current Reality (CORRECT)

✅ **New CFR-000**: Multiple code_developer instances (2-3) ARE allowed, with proper isolation:

```
code_developer instance 1  →  worktree: roadmap-work-42  →  files: coffee_maker/recipes.py
code_developer instance 2  →  worktree: roadmap-work-43  →  files: coffee_maker/notifications.py
code_developer instance 3  →  worktree: roadmap-work-44  →  files: tests/test_database.py

✅ NO FILE CONFLICTS: Each instance works on DIFFERENT files in SEPARATE worktrees
```

---

## How Parallel Development Works

### 1. Architect Decomposes Tasks

The architect analyzes technical specifications and creates `work_sessions`:

```python
# architect creates work sessions for parallel-safe tasks
from coffee_maker.autonomous.unified_database import get_unified_database

db = get_unified_database()
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

# Work session 1: Phase 1 of SPEC-117
cursor.execute("""
    INSERT INTO work_sessions (
        work_id, spec_id, roadmap_item_id, scope, scope_description,
        assigned_files, branch_name, status, created_by, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "WORK-42",
    "SPEC-117",
    "PRIORITY-27",
    "phase",
    "Phase 1: Database schema updates",
    '["coffee_maker/autonomous/unified_database.py"]',
    "roadmap-work-42",
    "pending",
    "architect",
    datetime.now().isoformat()
))

# Work session 2: Phase 2 of SPEC-117 (different files!)
cursor.execute("""
    INSERT INTO work_sessions (
        work_id, spec_id, roadmap_item_id, scope, scope_description,
        assigned_files, branch_name, status, created_by, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "WORK-43",
    "SPEC-117",
    "PRIORITY-27",
    "phase",
    "Phase 2: code_reviewer integration",
    '["coffee_maker/autonomous/code_reviewer.py"]',
    "roadmap-work-43",
    "pending",
    "architect",
    datetime.now().isoformat()
))

conn.commit()
```

**Key:** architect ensures `assigned_files` don't overlap between work sessions!

### 2. Orchestrator Creates Git Worktrees

For each work session, orchestrator creates an isolated git worktree:

```bash
# For WORK-42
git worktree add ../MonolithicCoffeeMakerAgent-work-42 \
    -b roadmap-work-42 \
    roadmap

# For WORK-43
git worktree add ../MonolithicCoffeeMakerAgent-work-43 \
    -b roadmap-work-43 \
    roadmap
```

**Result**: Completely isolated working directories, each on its own branch.

### 3. code_developer Instances Claim Work

Each code_developer instance:
1. Queries available work_sessions
2. Claims one by updating status to "in_progress"
3. Works in its assigned worktree
4. Only touches files in `assigned_files`

```python
# code_developer claims work
cursor.execute("""
    UPDATE work_sessions
    SET status = 'in_progress',
        claimed_by = 'code_developer',
        claimed_at = ?,
        started_at = ?
    WHERE work_id = ? AND status = 'pending'
""", (datetime.now().isoformat(), datetime.now().isoformat(), "WORK-42"))
```

### 4. Orchestrator Merges Completed Work

When work completes:
1. code_developer commits in worktree branch (`roadmap-work-42`)
2. Orchestrator merges to `roadmap` branch
3. Orchestrator cleans up worktree
4. Work session marked as `completed`

```bash
# Merge completed work
git checkout roadmap
git merge --no-ff roadmap-work-42 -m "Merge WORK-42: Phase 1 of SPEC-117"

# Cleanup
git worktree remove ../MonolithicCoffeeMakerAgent-work-42
git branch -D roadmap-work-42
```

---

## Task Granularity

architect can decompose work at multiple levels:

### Level 1: Phase-Based (Recommended)

One work session per phase of a technical spec:

```
SPEC-117: Code Reviewer Database Integration
  ├── WORK-42: Phase 1 (Schema updates)        → Files: unified_database.py
  ├── WORK-43: Phase 2 (code_reviewer changes) → Files: code_reviewer.py
  └── WORK-44: Phase 3 (Testing)               → Files: tests/test_code_reviewer.py

✅ 3 parallel sessions, NO file overlaps
```

### Level 2: Section-Based (Fine-grained)

One work session per major section in hierarchical spec:

```
SPEC-117 (hierarchical):
  /overview       → WORK-42 (docs updates)
  /api_design     → WORK-43 (API implementation)
  /implementation → WORK-44 (core logic)
  /testing        → WORK-45 (tests)
```

### Level 3: Module-Based (Ultra-fine-grained)

One work session per independent module:

```
PRIORITY-27:
  ├── WORK-42: coffee_maker/autonomous/database.py
  ├── WORK-43: coffee_maker/autonomous/code_reviewer.py
  └── WORK-44: tests/integration/test_workflow.py
```

**Rule**: architect chooses granularity based on file dependencies and spec structure.

---

## Safety Constraints

### 1. File Conflict Detection (architect's responsibility)

Before creating work_sessions, architect MUST verify file independence:

```python
# Check for file overlaps
files_work_42 = ["coffee_maker/autonomous/unified_database.py"]
files_work_43 = ["coffee_maker/autonomous/code_reviewer.py"]

overlap = set(files_work_42) & set(files_work_43)

if overlap:
    raise ValueError(f"File conflict detected: {overlap}. Cannot parallelize.")
```

**Tools**: architect uses codebase analysis to identify file dependencies.

### 2. Maximum Concurrent Sessions

**Hard Limit**: 3 concurrent code_developer instances maximum

**Rationale**:
- 1 instance (baseline): No parallelization
- 2 instances: 75% velocity increase (good)
- 3 instances: 150% velocity increase (diminishing returns)
- 4+ instances: Resource exhaustion, merge complexity

**Enforcement**:

```python
# In orchestrator
max_concurrent_sessions = 3

active_sessions = cursor.execute("""
    SELECT COUNT(*) FROM work_sessions
    WHERE status = 'in_progress'
""").fetchone()[0]

if active_sessions >= max_concurrent_sessions:
    print("⚠️  Maximum concurrent sessions reached, wait for completion")
```

### 3. Work Session Timeout (Stale Detection)

If a work session is `in_progress` for >24 hours with no commits, it's considered stale:

```python
# Reset stale work sessions
from datetime import timedelta

threshold = (datetime.now() - timedelta(hours=24)).isoformat()

cursor.execute("""
    UPDATE work_sessions
    SET status = 'pending',
        claimed_by = NULL,
        claimed_at = NULL,
        started_at = NULL
    WHERE status = 'in_progress'
    AND claimed_at < ?
""", (threshold,))

logger.warning(f"Reset {cursor.rowcount} stale work sessions")
```

### 4. Merge Conflict Handling

If orchestrator detects merge conflicts:
1. **Auto-merge fails**: orchestrator pauses
2. **Manual resolution required**: architect notified
3. **Resolution**: architect merges manually, updates work_session
4. **Prevention**: architect improves task separation for future

---

## Branch Naming Convention

**Format**: `roadmap-work-{work_id}`

**Examples**:
- `roadmap-work-42` (for WORK-42)
- `roadmap-work-43` (for WORK-43)
- `roadmap-work-100` (for WORK-100)

**Why not `feature/us-{number}`?**
- Old convention, not tied to database
- `work_id` is database-tracked primary key
- Enables precise tracking and stale detection

**Base Branch**: Always `roadmap`

```bash
# ✅ Correct
git worktree add ../MonolithicCoffeeMakerAgent-work-42 -b roadmap-work-42 roadmap

# ❌ Incorrect (old convention)
git worktree add ../MonolithicCoffeeMakerAgent-wt42 -b feature/us-042 roadmap
```

---

## Database Schema

### work_sessions Table

```sql
CREATE TABLE work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT NOT NULL UNIQUE,               -- "WORK-42"
    spec_id TEXT NOT NULL,                      -- "SPEC-117"
    roadmap_item_id TEXT,                       -- "PRIORITY-27"
    scope TEXT NOT NULL,                        -- "phase", "section", "module"
    scope_description TEXT,                     -- Human-readable
    assigned_files TEXT,                        -- JSON array of file paths
    branch_name TEXT NOT NULL UNIQUE,           -- "roadmap-work-42"
    worktree_path TEXT,                         -- Path to worktree
    status TEXT NOT NULL DEFAULT 'pending',     -- "pending", "in_progress", "completed"
    claimed_by TEXT,                            -- "code_developer"
    claimed_at TEXT,                            -- Timestamp
    started_at TEXT,                            -- Timestamp
    completed_at TEXT,                          -- Timestamp
    commit_sha TEXT,                            -- Final commit
    merged_at TEXT,                             -- When merged
    created_by TEXT NOT NULL DEFAULT 'architect',
    created_at TEXT NOT NULL,

    FOREIGN KEY (spec_id) REFERENCES technical_specs(id),
    FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id)
);
```

**Key Fields**:
- `work_id`: Unique identifier (WORK-42, WORK-43, etc.)
- `assigned_files`: JSON array ensuring file isolation
- `branch_name`: Git branch for this work (`roadmap-work-42`)
- `status`: Lifecycle tracking (pending → in_progress → completed)
- `claimed_at`: For stale detection (>24h = stale)

---

## Workflow Examples

### Example 1: Parallel Phase Implementation

**Scenario**: SPEC-117 has 3 independent phases

```
1. architect creates work sessions:
   - WORK-42: Phase 1 (database schema)
   - WORK-43: Phase 2 (code_reviewer logic)
   - WORK-44: Phase 3 (testing)

2. orchestrator creates worktrees:
   - roadmap-work-42 → ../MonolithicCoffeeMakerAgent-work-42
   - roadmap-work-43 → ../MonolithicCoffeeMakerAgent-work-43
   - roadmap-work-44 → ../MonolithicCoffeeMakerAgent-work-44

3. code_developer instances claim work:
   - Instance 1 claims WORK-42
   - Instance 2 claims WORK-43
   - Instance 3 claims WORK-44

4. Parallel development (2-4 hours each):
   - Instance 1 works in work-42 worktree
   - Instance 2 works in work-43 worktree
   - Instance 3 works in work-44 worktree

5. orchestrator merges sequentially:
   - Merge roadmap-work-42 → roadmap
   - Merge roadmap-work-43 → roadmap
   - Merge roadmap-work-44 → roadmap

6. Cleanup:
   - Remove worktrees
   - Mark work_sessions as completed
   - Delete temporary branches

✅ Result: 3 phases completed in ~4 hours instead of ~12 hours (3x speedup)
```

### Example 2: Section-Based Parallelization

**Scenario**: Hierarchical spec with independent sections

```
SPEC-120 (hierarchical):
  /overview          → WORK-50 (Instance 1)
  /api_design        → WORK-51 (Instance 2)
  /implementation    → WORK-52 (Instance 3)

Each section touches different files, safe to parallelize.
```

---

## Benefits

1. **Velocity**: 2-3x faster development with parallelization
2. **Safety**: NO file conflicts (each instance isolated)
3. **Flexibility**: architect controls granularity
4. **Tracking**: Database tracks all work sessions
5. **Recovery**: Stale detection prevents stuck work
6. **Merge Control**: orchestrator handles merging sequentially

---

## Limitations

1. **architect's burden**: Must analyze file dependencies
2. **Not all work is parallelizable**: Some specs are monolithic
3. **Merge conflicts possible**: If architect missed dependency
4. **Resource usage**: Each instance consumes CPU/memory
5. **Complexity**: More moving parts than singleton model

---

## Comparison: Old vs New

| Aspect | Old (Singleton) | New (Parallel) |
|--------|----------------|----------------|
| **Instances** | 1 code_developer only | 2-3 code_developers |
| **Velocity** | Baseline (1x) | 2-3x faster |
| **Isolation** | N/A (only one instance) | Git worktrees |
| **Branch Naming** | N/A | `roadmap-work-{id}` |
| **File Conflicts** | Impossible (one instance) | Prevented (architect validation) |
| **Tracking** | `implementation_started_at` | `work_sessions` table |
| **Stale Detection** | Per roadmap_item | Per work_session |
| **architect Role** | Not involved | Creates work_sessions |
| **orchestrator Role** | Minimal | Creates worktrees, merges |

---

## Updated CFR-000 Statement

**CFR-000: File Conflict Prevention via Controlled Parallelization**

**Rule**: Multiple code_developer instances (2-3) MAY run concurrently, PROVIDED:

1. **Isolation**: Each instance works in separate git worktree
2. **File Independence**: architect verifies NO file overlap between tasks
3. **Database Tracking**: Each instance claims unique `work_session`
4. **Branch Isolation**: Each instance uses `roadmap-work-{work_id}` branch
5. **orchestrator Control**: orchestrator creates worktrees and merges sequentially
6. **Stale Detection**: work_sessions >24h in progress are reset

**Enforcement**:
- architect creates work_sessions with non-overlapping `assigned_files`
- orchestrator creates isolated worktrees for each work_session
- code_developer claims work_session before starting
- orchestrator merges completed work sequentially (no concurrent merges)

**Result**: NO file conflicts, increased velocity, maintained safety.

---

## Migration Path

For existing code using `implementation_started_at` in `roadmap_items`:
- Keep for backward compatibility
- Use `work_sessions` for NEW parallel work
- Gradually migrate to work_sessions model

---

## See Also

- **GUIDELINE-008**: Git Worktree Best Practices
- **SPEC-108**: Parallel Agent Execution
- **parallel_execution_coordinator.py**: Implementation
- **CFR-013**: Git Workflow (worktree integration)

---

**Version History**:
- v1.0 (2025-10-19): Initial singleton enforcement
- v2.0 (2025-10-20): Added worktree support
- v3.0 (2025-10-23): **Full parallel development model with work_sessions**
