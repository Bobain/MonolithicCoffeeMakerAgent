# PRIORITY 31 Refactoring Summary

## What Was Changed

### Conceptual Model Change

**BEFORE (WRONG):**
- work_sessions: Pre-split subtasks
- Database tracking of subtask pool
- code_developers claim subtasks atomically

**AFTER (CORRECT):**
- works: Independent units grouped by related_works_id
- Sequential ordering within groups (priority_order)
- Parallelization across different groups (orchestrator decision)

### Database Schema

**works table:**
```sql
CREATE TABLE works (
    work_id TEXT PRIMARY KEY,
    priority_number INTEGER NOT NULL,          -- NEW: Links to ROADMAP PRIORITY
    related_works_id TEXT NOT NULL,            -- NEW: Groups sequential works
    priority_order INTEGER NOT NULL,           -- NEW: Order within group
    spec_id TEXT NOT NULL,
    scope_description TEXT NOT NULL,
    assigned_files TEXT NOT NULL,
    status TEXT NOT NULL,
    claimed_by TEXT,
    claimed_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,

    UNIQUE(related_works_id, priority_order)   -- NEW: Enforces ordering
)
```

**commits table (NEW):**
```sql
CREATE TABLE commits (
    commit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT NOT NULL,                     -- Foreign key to works
    commit_sha TEXT NOT NULL,
    commit_message TEXT,
    committed_at TEXT NOT NULL,
    reviewed_by TEXT,                          -- For code_reviewer
    review_status TEXT,                        -- For code_reviewer
    review_notes TEXT,                         -- For code_reviewer

    FOREIGN KEY (work_id) REFERENCES works(work_id)
)
```

### Key Concepts

1. **related_works_id**: Groups sequential works (e.g., "GROUP-31" for 4 phases of PRIORITY 31)
2. **priority_order**: Enforces sequential execution within group (1, 2, 3, 4)
3. **Separate commits table**: A work can have multiple commits
4. **code_reviewer sync**: code_reviewer reads from commits table using work_id foreign key

### Code Changes

- `work_session_manager.py` → `work_manager.py`
  - `WorkSessionManager` → `WorkManager`
  - Added `query_next_work_for_priority()` - respects sequential ordering
  - Added `record_commit()` - tracks commits for code_reviewer
  - Removed `commit_sha` from `update_work_status()`

- `daemon.py`:
  - `work_session_id` → `work_id` parameter
  - `_run_work_session_mode()` → `_run_work_mode()`
  - Calls `work_manager.record_commit()` after git commit
  - `_build_work_session_prompt()` → `_build_work_prompt()`
  - `_build_work_session_commit_message()` → `_build_work_commit_message()`

- `daemon_cli.py`:
  - `--work-session` → `--work` argument
  - Example: `code-developer --work WORK-31-1`

### Migrations

1. `migrate_work_sessions_to_works.py` - Adds new columns, renames table
2. `migrate_remove_commit_sha_create_commits_table.py` - Removes commit_sha, creates commits table

### What Still Needs To Be Done

1. **Update tests:**
   - Rename `test_work_session_manager.py` → `test_work_manager.py`
   - Update all test cases for new works model
   - Test `related_works_id` and `priority_order` logic
   - Test `record_commit()` method
   - Test sequential ordering enforcement

2. **Delete old file:**
   - Remove `work_session_manager.py` (replaced by `work_manager.py`)

3. **Run tests and verify:**
   - `poetry run pytest tests/unit/test_work_manager.py -v`
   - Ensure all 25+ tests pass

## Usage Examples

### Sequential Works (Same Group)

```python
# architect creates 4 sequential works:
WORK-31-1: Phase 1 - WorkManager class
  - related_works_id: "GROUP-31"
  - priority_order: 1

WORK-31-2: Phase 2 - Daemon integration
  - related_works_id: "GROUP-31"
  - priority_order: 2

# code_developer MUST do them in order (1 → 2 → 3 → 4)
```

### Parallel Works (Different Groups)

```python
# architect determines PRIORITY 25 and 26 can be parallelized:
PRIORITY 25: Feature A
  - related_works_id: "GROUP-25"
  - assigned_files: [feature_a.py]

PRIORITY 26: Feature B
  - related_works_id: "GROUP-26"
  - assigned_files: [feature_b.py]

# orchestrator spawns 2 code_developers in parallel:
code-developer --work WORK-25-1  # Terminal 1
code-developer --work WORK-26-1  # Terminal 2
```

## Key Differences

| Aspect | OLD (work_sessions) | NEW (works) |
|--------|-------------------|-------------|
| Granularity | Pre-split subtasks | Complete works with sequential ordering |
| Grouping | None | related_works_id |
| Ordering | None | priority_order |
| Commits | Single commit_sha | Multiple commits in separate table |
| Parallelization | Pool-based claiming | orchestrator + architect decision |
| code_reviewer | No sync mechanism | Reads from commits table via work_id FK |

## Related Files

- CFR-000-PARALLEL-DEVELOPMENT.md (needs update)
- SPEC-131 (original spec - now outdated)
- SPEC-132 (architect work creation - needs update)
- ROADMAP.md PRIORITY 31-34
