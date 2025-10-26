# Database Schema Guide

**Purpose**: Provide clear guidance on database table purposes and usage patterns.

**CRITICAL**: Always consult this guide before implementing database-related features!

---

## Core Principle: Database-First Architecture

✅ **CORRECT**: Store data in database, generate views/files as needed
❌ **WRONG**: Store data in files, sync to database

---

## technical_specs Table

**Purpose**: Store complete technical specification content in database (NO FILES!)

### Schema
```sql
CREATE TABLE technical_specs (
    id TEXT PRIMARY KEY,              -- SPEC-116
    spec_number INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    roadmap_item_id TEXT,             -- Links to roadmap item
    status TEXT NOT NULL DEFAULT 'draft',
    spec_type TEXT DEFAULT 'monolithic',  -- 'monolithic' or 'hierarchical'

    -- CONTENT STORAGE (PRIMARY)
    content TEXT,                     -- ✅ FULL spec content stored here!

    -- FILE SYSTEM (LEGACY - DO NOT USE FOR NEW SPECS)
    file_path TEXT,                   -- ❌ Legacy field, ignore for new specs

    -- METADATA
    total_phases INTEGER,             -- For hierarchical: number of phases
    phase_files TEXT,                 -- For hierarchical: JSON array of phase names
    current_phase_status TEXT,        -- Phase status: 'in_progress', 'completed'
    phase TEXT,                       -- Current phase number

    estimated_hours REAL,
    actual_hours REAL,
    dependencies TEXT,                -- JSON array of spec dependencies
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    started_at TEXT
);
```

### Content Storage Strategy

#### Monolithic Specs
Store as plain markdown in `content` column:

```python
content = """# SPEC-116: User Authentication

## Overview
Complete authentication system...

## Requirements
- Login/logout
- Session management
...
"""

db.create_technical_spec(
    spec_type="monolithic",
    content=content  # ✅ Store entire spec here
)
```

#### Hierarchical Specs
Store as **JSON** in `content` column:

```python
content = json.dumps({
    "overview": "High-level system description...",
    "phases": [
        {
            "number": 1,
            "name": "database-layer",
            "description": "Create database models and migrations",
            "hours": 2.0,
            "content": "## Phase 1: Database Layer\n\n### Models\n..."
        },
        {
            "number": 2,
            "name": "api-layer",
            "description": "Implement REST API endpoints",
            "hours": 3.0,
            "content": "## Phase 2: API Layer\n\n### Endpoints\n..."
        }
    ],
    "architecture": "Overall architecture decisions...",
    "technology_stack": "Python, FastAPI, PostgreSQL..."
})

db.create_technical_spec(
    spec_type="hierarchical",
    content=content,  # ✅ JSON with all phases
    total_phases=2,
    phase_files=json.dumps(["phase1-database-layer", "phase2-api-layer"])
)
```

### Reading Specs

```python
# Get spec from database
spec = db.get_technical_spec(roadmap_item_id="US-116")

if spec["spec_type"] == "hierarchical":
    data = json.loads(spec["content"])
    current_phase = data["phases"][0]  # Progressive disclosure
    print(current_phase["content"])
else:
    print(spec["content"])  # Full monolithic spec
```

### ❌ DO NOT DO THIS

```python
# WRONG: Creating files on disk
spec_file = Path("docs/architecture/specs/SPEC-116.md")
spec_file.write_text(content)  # ❌ NO! Store in database!

# WRONG: Using file_path for new specs
db.create_technical_spec(
    file_path="docs/architecture/specs/SPEC-116.md",  # ❌ Legacy field
    content=None  # ❌ Missing content!
)
```

---

## implementation_tasks Table

**Purpose**: Break technical specs into atomic, scoped implementation tasks for parallel execution.

### Schema
```sql
CREATE TABLE implementation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL UNIQUE,    -- TASK-31-1
    spec_id TEXT NOT NULL,            -- SPEC-116 (FK to technical_specs)

    -- TASK SCOPE
    scope TEXT NOT NULL,              -- 'database-layer', 'api-endpoints'
    scope_description TEXT,           -- What this task implements
    assigned_files TEXT,              -- JSON: Files this task modifies

    -- GIT WORKTREE
    branch_name TEXT NOT NULL UNIQUE, -- roadmap-implementation_task-TASK-31-1
    worktree_path TEXT,               -- /path/to/worktree

    -- STATUS TRACKING
    status TEXT NOT NULL DEFAULT 'pending',
    claimed_by TEXT,                  -- code_developer
    claimed_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    commit_sha TEXT,
    merged_at TEXT,

    created_by TEXT NOT NULL DEFAULT 'architect',
    created_at TEXT NOT NULL,

    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE CASCADE
);
```

### Usage Pattern

**Architect creates spec → Architect creates tasks:**

```python
# 1. Create hierarchical spec in database
spec_id = db.create_technical_spec(
    spec_number=116,
    title="User Authentication",
    roadmap_item_id="US-116",
    spec_type="hierarchical",
    content=json.dumps({
        "phases": [
            {"name": "database-layer", "hours": 2},
            {"name": "api-layer", "hours": 3}
        ]
    }),
    total_phases=2
)

# 2. Create implementation tasks from spec phases
db.create_implementation_task(
    task_id="TASK-116-1",
    spec_id="SPEC-116",
    scope="database-layer",
    scope_description="Create User and Session models, migrations",
    assigned_files=json.dumps([
        "coffee_maker/models/user.py",
        "migrations/001_create_users.py"
    ]),
    branch_name="roadmap-implementation_task-TASK-116-1"
)

db.create_implementation_task(
    task_id="TASK-116-2",
    spec_id="SPEC-116",
    scope="api-layer",
    scope_description="Implement login/logout endpoints",
    assigned_files=json.dumps([
        "coffee_maker/api/auth.py",
        "tests/test_auth_api.py"
    ]),
    branch_name="roadmap-implementation_task-TASK-116-2"
)
```

**code_developer implements tasks:**

```python
# 1. Query for pending tasks
tasks = db.get_pending_tasks()

# 2. Claim task
task = tasks[0]
db.claim_task(task["task_id"], agent_name="code_developer")

# 3. Get spec content for this task's scope
spec = db.get_technical_spec(spec_id=task["spec_id"])
spec_data = json.loads(spec["content"])

# Find the phase matching this task's scope
phase = next(p for p in spec_data["phases"] if p["name"] == task["scope"])

# 4. Implement using phase content
print(phase["content"])  # Progressive disclosure!

# 5. Mark complete
db.complete_task(task["task_id"], commit_sha="abc123")
```

### Progressive Disclosure Benefits

- **Context Reduction**: code_developer only loads ONE phase at a time
- **Parallel Execution**: Multiple tasks can run simultaneously in different worktrees
- **Clear Boundaries**: Each task has explicit scope and assigned files

---

## Key Design Principles

### 1. Database is Source of Truth
- ✅ Store data in database
- ✅ Generate files/views as needed (optional)
- ❌ Never require files to exist

### 2. Atomic Transactions
- All spec+task creation should be atomic
- Rollback if any step fails

### 3. Foreign Key Integrity
- `implementation_tasks.spec_id` → `technical_specs.id`
- Cascade deletes

### 4. JSON for Complex Data
- Use JSON for arrays and nested structures
- Parse/validate when reading
- Store serialized when writing

---

## Migration Pattern

When adding new columns:

```python
# Good migration comment
"""
Add hierarchical spec support to technical_specs table.

ARCHITECTURE NOTE:
These columns support hierarchical specs stored as JSON in the content column.
The content column stores the ENTIRE spec - no files needed!

Example content:
{
    "overview": "...",
    "phases": [...]
}
"""
```

---

## Common Mistakes to Avoid

❌ **Storing specs in files**
```python
# WRONG
Path("docs/architecture/specs/SPEC-116.md").write_text(content)
```

❌ **Using file_path for new specs**
```python
# WRONG
db.create_technical_spec(file_path="...", content=None)
```

❌ **Not using implementation_tasks**
```python
# WRONG - trying to implement entire spec at once
# Should break into tasks for parallel execution
```

✅ **Correct: Database-first**
```python
# RIGHT
db.create_technical_spec(content=json.dumps({...}))
```

---

## Verification Checklist

Before implementing spec-related features:

- [ ] Checked this guide
- [ ] Verified table schema in database
- [ ] Confirmed content storage strategy
- [ ] Planned for JSON parsing (if hierarchical)
- [ ] Designed task breakdown (if using implementation_tasks)
- [ ] No file creation required

---

**Last Updated**: 2025-10-24
**Author**: architect
**Related**: PRIORITY 25, CFR-016
