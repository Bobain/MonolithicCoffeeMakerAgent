# Bug Tracking Skill

**Purpose**: Unified bug tracking interface for all agents (assistant, code_developer, architect, project_manager)

**Database**: Uses `data/orchestrator.db` for tracking, maintains markdown files for readability

**Related**: SPEC-111 (Bug Tracking Database and Skill), CFR-014 (Database Tracing)

---

## Quick Start

```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()

# Report a bug
result = skill.report_bug(
    title="Feature X crashes on edge case",
    description="When user provides empty input, the system crashes",
    reporter="assistant",
    priority="High",
    category="crash",
)

# Update status
skill.update_bug_status(bug_number=1, status="in_progress")

# Query bugs
open_bugs = skill.query_bugs(status="open", priority="High")
```

---

## Core Methods

### 1. Report Bug

```python
result = skill.report_bug(
    title: str,                           # Bug title (concise)
    description: str,                     # Detailed description
    reporter: str,                        # assistant, code_developer, architect, etc.
    priority: Optional[str] = None,       # Critical, High, Medium, Low (auto-assessed)
    category: Optional[str] = None,       # crash, performance, ui, logic, etc.
    reproduction_steps: Optional[List[str]] = None,
    discovered_in_priority: Optional[int] = None,  # ROADMAP priority
)

# Returns:
# {
#     "bug_id": 1,
#     "bug_number": 1,
#     "ticket_file_path": "tickets/BUG-001.md",
#     "status": "open"
# }
```

### 2. Update Bug Status

```python
skill.update_bug_status(
    bug_number: int,                      # Bug number (e.g., 1 for BUG-001)
    status: str,                          # open, analyzing, in_progress, testing, resolved, closed
    assigned_to: Optional[str] = None,    # Reassign to different agent
    notes: Optional[str] = None,          # Status change notes
)
```

**Status Workflow:**
- `open` → `analyzing` → `in_progress` → `testing` → `resolved` → `closed`

### 3. Add Bug Details

```python
skill.add_bug_details(
    bug_number: int,
    root_cause: Optional[str] = None,         # Root cause analysis
    fix_description: Optional[str] = None,    # How it was fixed
    expected_behavior: Optional[str] = None,  # What should happen
    actual_behavior: Optional[str] = None,    # What actually happens
)
```

### 4. Link Bug to Commit

```python
skill.link_bug_to_commit(
    bug_number: int,
    commit_sha: str,                      # Git commit SHA
)
```

### 5. Link Bug to PR

```python
skill.link_bug_to_pr(
    bug_number: int,
    pr_url: str,                          # GitHub PR URL
)
```

### 6. Query Bugs

```python
bugs = skill.query_bugs(
    status: Optional[str] = None,         # Filter by status
    priority: Optional[str] = None,       # Filter by priority
    assigned_to: Optional[str] = None,    # Filter by assignee
    category: Optional[str] = None,       # Filter by category
    limit: int = 50,                      # Max results
)
```

### 7. Get Bug by Number

```python
bug = skill.get_bug_by_number(bug_number=1)
```

### 8. Get Open Bugs Summary

```python
summary = skill.get_open_bugs_summary()
# Returns: {"critical": 2, "high": 5, "medium": 3, "low": 1}
```

### 9. Get Bug Resolution Velocity

```python
velocity = skill.get_bug_resolution_velocity()
# Returns: [
#     {"month": "2025-10", "total_bugs": 10, "resolved": 8, "open": 2, "avg_resolution_time_ms": 86400000},
#     ...
# ]
```

---

## Agent-Specific Usage

### Assistant

**When to use:**
- User reports a bug
- You notice unexpected behavior during interaction

**Example:**
```python
# User says: "The orchestrator keeps crashing when ROADMAP.md is missing"
result = skill.report_bug(
    title="Orchestrator crashes when ROADMAP.md is missing",
    description="User reports that orchestrator crashes instead of creating ROADMAP.md when file is deleted",
    reporter="assistant",
    priority="High",
    category="crash",
    reproduction_steps=["Delete ROADMAP.md", "Start orchestrator", "Observe crash"],
)

# Notify user
print(f"Bug {result['bug_number']} created: {result['ticket_file_path']}")
```

### Code Developer

**When to use:**
- Starting work on a bug fix
- Found root cause
- Completed fix
- Linking to commit/PR

**Example:**
```python
# Starting analysis
skill.update_bug_status(bug_number=1, status="analyzing", notes="Reproducing locally")

# Found root cause
skill.add_bug_details(
    bug_number=1,
    root_cause="Missing null check in ROADMAP parser",
    expected_behavior="Should create ROADMAP.md if missing",
    actual_behavior="Raises FileNotFoundError",
)

# Implementing fix
skill.update_bug_status(bug_number=1, status="in_progress")

# Completed fix
skill.update_bug_status(bug_number=1, status="testing")
skill.link_bug_to_commit(bug_number=1, commit_sha="abc123")

# PR created
skill.link_bug_to_pr(bug_number=1, pr_url="https://github.com/user/repo/pull/42")
skill.update_bug_status(bug_number=1, status="resolved")
```

### Architect

**When to use:**
- Querying bugs related to a spec
- Linking bugs to ROADMAP priorities
- Analyzing bug patterns

**Example:**
```python
# Find bugs related to orchestrator
bugs = skill.query_bugs(category="orchestrator", status="open")

# Check if bug already exists before creating spec
existing = skill.query_bugs(
    status="open",
    priority="High",
)

# Get velocity for planning
velocity = skill.get_bug_resolution_velocity()
```

### Project Manager

**When to use:**
- Checking project health
- Reporting bug status
- Identifying bottlenecks

**Example:**
```python
# Daily standup
summary = skill.get_open_bugs_summary()
print(f"Open bugs: {sum(summary.values())}")
print(f"Critical: {summary['critical']}, High: {summary['high']}")

# Check code_developer workload
dev_bugs = skill.query_bugs(assigned_to="code_developer", status="in_progress")
print(f"code_developer has {len(dev_bugs)} bugs in progress")
```

---

## Bug Categories

- `crash` - Application crashes or hangs
- `performance` - Slow execution or resource issues
- `ui` - User interface problems
- `logic` - Incorrect behavior or calculations
- `documentation` - Missing or incorrect docs
- `security` - Security vulnerabilities
- `integration` - Problems with external systems
- `data` - Data corruption or loss

---

## Bug Priorities

- `Critical` - System unusable, data loss, security issue
- `High` - Major functionality broken, workaround exists
- `Medium` - Feature partially broken, minor impact
- `Low` - Cosmetic issue, nice-to-have fix

---

## Best Practices

1. **Always provide reproduction steps** when reporting bugs
2. **Update status regularly** so others know progress
3. **Add root cause** when found - helps prevent similar bugs
4. **Link to commits/PRs** for traceability
5. **Query before creating** to avoid duplicates
6. **Use meaningful categories** for better analytics

---

## Database Schema

```sql
-- Main bugs table
CREATE TABLE bugs (
    bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_number INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    category TEXT,
    reporter TEXT NOT NULL,
    assigned_to TEXT DEFAULT 'code_developer',
    discovered_in_priority INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT,
    -- ... additional fields
);

-- Analytics views
CREATE VIEW bug_resolution_velocity AS ...
CREATE VIEW bug_priority_distribution AS ...
CREATE VIEW bug_category_analysis AS ...
CREATE VIEW open_bugs_summary AS ...
```

---

## File Structure

```
.claude/skills/shared/bug-tracking/
├── bug-tracking.md          # This file (instructions)
├── bug_tracking.py          # Skill implementation
└── README.md                # Usage examples

tickets/                      # Markdown bug tickets
├── BUG-001.md
├── BUG-002.md
└── ...

data/orchestrator.db         # SQLite database
└── bugs table               # Bug tracking data
```

---

## Implementation Status

**Status**: ✅ Implemented

**Phase 1**: Database Schema ✅ (SPEC-111 defined)
**Phase 2**: Skill Implementation ✅ (Complete - see bug_tracking.py)
**Phase 3**: Agent Integration ⏳ (In progress)
**Phase 4**: Dashboard Integration ⏳ (Pending)

**Files**:
- `bug_tracking.py` - Main skill implementation ✅
- `bug_parser.py` - Markdown parser for migration ✅
- `README.md` - Usage examples and API docs ✅

---

## Testing

Run tests:
```bash
pytest tests/unit/test_bug_tracking_skill.py
pytest tests/integration/test_bug_workflow.py
```

---

## References

- **SPEC-111**: Bug Tracking Database and Skill (technical specification)
- **CFR-014**: Orchestrator Database Tracing
- **PRIORITY 2.11**: Bug Fixing Workflow
- **Existing**: `coffee_maker/cli/bug_tracker.py` (file-based system)

---

**Last Updated**: 2025-10-20
**Maintainer**: architect + code_developer
**Status**: ✅ Production Ready
