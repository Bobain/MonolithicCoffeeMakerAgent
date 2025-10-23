# Bug Tracking Skill - README

**Status**: ✅ Implemented
**Database**: `data/orchestrator.db` (SQLite)
**Markdown**: `tickets/BUG-*.md` (synced bidirectionally)

---

## Quick Start

```python
# 1. Import the skill
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bug_tracking import BugTrackingSkill

# 2. Initialize
skill = BugTrackingSkill()

# 3. Report a bug
result = skill.report_bug(
    title="ROADMAP parser misses double-hash priorities",
    description="Parser only reads ### but ROADMAP has ## US-XXX entries",
    reporter="orchestrator",
    priority="Critical",
    category="logic",
    reproduction_steps=[
        "Add ## US-110 to ROADMAP.md",
        "Run RoadmapParser.get_priorities()",
        "Observe US-110 is missing from results"
    ]
)

print(f"Created BUG-{result['bug_number']:03d}")
# Output: Created BUG-067

# 4. Update status
skill.update_bug_status(bug_number=67, status="in_progress")

# 5. Add details
skill.add_bug_details(
    bug_number=67,
    root_cause="Regex pattern only matches ### not ##",
    test_file_path="tests/test_bug_067_roadmap_parser.py",
    test_name="test_roadmap_parser_double_hash_support"
)

# 6. Query bugs
open_bugs = skill.query_bugs(status="open", priority="Critical")
print(f"Open critical bugs: {len(open_bugs)}")

# 7. Link to commit/PR
skill.link_bug_to_commit(bug_number=67, commit_sha="abc123def")
skill.link_bug_to_pr(bug_number=67, pr_url="https://github.com/user/repo/pull/42")

# 8. Mark resolved
skill.update_bug_status(bug_number=67, status="resolved")
```

---

## Importing Existing Tickets

If you have existing `BUG-*.md` files, import them into the database:

```python
from bug_tracking import BugTrackingSkill
from bug_parser import BugTicketParser

skill = BugTrackingSkill()
parser = BugTicketParser()

# Import all tickets
from pathlib import Path
stats = parser.import_all_tickets(Path("tickets"), skill)

print(f"Imported: {stats['imported']}")
print(f"Skipped: {stats['skipped']}")
print(f"Errors: {stats['errors']}")
```

---

## Agent-Specific Examples

### Orchestrator

When spawning code_developer for bug fixes:

```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()

# Update bug to in_progress when spawning agent
skill.update_bug_status(
    bug_number=66,
    status="in_progress",
    notes="Spawned code_developer (PID 12345)"
)
```

### Code Developer

During bug fix workflow:

```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()

# 1. Start analysis
skill.update_bug_status(bug_number=66, status="analyzing")

# 2. Add findings
skill.add_bug_details(
    bug_number=66,
    root_cause="Two separate parsers with different regex patterns",
    expected_behavior="Parser should read both ## and ### formats",
    actual_behavior="Parser only reads ### format"
)

# 3. Start implementation
skill.update_bug_status(bug_number=66, status="in_progress")

# 4. Add test
skill.add_bug_details(
    bug_number=66,
    test_file_path="tests/test_bug_066_roadmap_parser.py",
    test_name="test_mixed_hash_formats"
)

# 5. Link commit
skill.link_bug_to_commit(bug_number=66, commit_sha="abc123")

# 6. Testing
skill.update_bug_status(bug_number=66, status="testing")

# 7. Create PR
skill.link_bug_to_pr(
    bug_number=66,
    pr_url="https://github.com/Bobain/MonolithicCoffeeMakerAgent/pull/42"
)

# 8. Resolved
skill.update_bug_status(bug_number=66, status="resolved")
```

### Assistant

When user reports a bug:

```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()

# User says: "The orchestrator crashes when I delete ROADMAP.md"
result = skill.report_bug(
    title="Orchestrator crashes when ROADMAP.md missing",
    description="User reports orchestrator crashes instead of creating ROADMAP when file is deleted",
    reporter="assistant",
    priority="High",
    category="crash",
    reproduction_steps=[
        "Delete docs/roadmap/ROADMAP.md",
        "Start orchestrator with: poetry run orchestrator start",
        "Observe crash: FileNotFoundError"
    ]
)

# Notify user
print(f"""
🐛 Bug Reported: BUG-{result['bug_number']:03d}
Priority: High
Status: Open
Ticket: {result['ticket_file_path']}

code_developer has been notified and will fix this soon!
""")
```

### Project Manager

For project health reports:

```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()

# Daily standup
summary = skill.get_open_bugs_summary()
total_open = sum(summary.values())

print(f"""
📊 Bug Report:
Critical: {summary['critical']}
High: {summary['high']}
Medium: {summary['medium']}
Low: {summary['low']}
Total Open: {total_open}
""")

# Check velocity
velocity = skill.get_bug_resolution_velocity()
if velocity:
    latest = velocity[0]
    print(f"""
🚀 Resolution Velocity (this month):
Total: {latest['total_bugs']}
Resolved: {latest['resolved']}
Open: {latest['open']}
Avg Resolution Time: {latest['avg_resolution_time_ms'] / 3600000:.1f} hours
""")
```

---

## Database Schema

The skill uses SQLite with the following schema:

```sql
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
    reproduction_steps TEXT,  -- JSON array
    expected_behavior TEXT,
    actual_behavior TEXT,
    root_cause TEXT,
    fix_description TEXT,
    related_files TEXT,       -- JSON array
    related_commits TEXT,     -- JSON array
    pr_url TEXT,
    roadmap_priority TEXT,
    time_to_resolve_ms INTEGER,
    time_to_close_ms INTEGER,
    ticket_file_path TEXT,
    test_file_path TEXT,
    test_name TEXT,
    metadata TEXT             -- JSON object
);
```

### Analytics Views

- `bug_resolution_velocity` - Monthly resolution stats
- `bug_priority_distribution` - Bugs by priority and status
- `bug_category_analysis` - Bugs by category
- `open_bugs_summary` - Current open bugs with age

---

## Status Workflow

```
open → analyzing → in_progress → testing → resolved → closed
  ↓                                            ↓
  └──────────────────────────────────────────┘
         (can go back to open if reopened)
```

### Status Definitions

- **open**: Bug reported, awaiting analysis
- **analyzing**: code_developer analyzing root cause
- **in_progress**: Fix being implemented
- **testing**: Fix complete, running tests
- **resolved**: Tests pass, PR created
- **closed**: PR merged, bug fully resolved

---

## Priority Guidelines

- **Critical**: System unusable, data loss, security issue
  - Example: "Orchestrator crashes on startup"

- **High**: Major functionality broken, workaround exists
  - Example: "Parser misses some ROADMAP entries"

- **Medium**: Feature partially broken, minor impact
  - Example: "Status emoji incorrect in notifications"

- **Low**: Cosmetic issue, nice-to-have fix
  - Example: "Typo in log message"

---

## Category Guidelines

- `crash` - Application crashes or hangs
- `performance` - Slow execution or resource issues
- `ui` - User interface problems
- `logic` - Incorrect behavior or calculations
- `documentation` - Missing or incorrect docs
- `security` - Security vulnerabilities
- `integration` - Problems with external systems
- `data` - Data corruption or loss

---

## Best Practices

### 1. Always Provide Reproduction Steps

```python
# Good
reproduction_steps=[
    "Start orchestrator",
    "Delete ROADMAP.md while running",
    "Wait 30 seconds for next poll",
    "Observe crash"
]

# Bad
reproduction_steps=["It crashes sometimes"]
```

### 2. Update Status Regularly

```python
# After each phase
skill.update_bug_status(66, "analyzing")    # Starting work
skill.update_bug_status(66, "in_progress")  # Implementing fix
skill.update_bug_status(66, "testing")      # Running tests
skill.update_bug_status(66, "resolved")     # Fix complete
```

### 3. Link Everything

```python
# Link to commits
skill.link_bug_to_commit(66, "abc123")
skill.link_bug_to_commit(66, "def456")  # Multiple commits OK

# Link to PR
skill.link_bug_to_pr(66, "https://github.com/user/repo/pull/42")
```

### 4. Add Tests

```python
# Always add regression test
skill.add_bug_details(
    bug_number=66,
    test_file_path="tests/test_bug_066_roadmap_parser.py",
    test_name="test_double_hash_support"
)
```

### 5. Query Before Creating

```python
# Check for duplicates
existing = skill.query_bugs(
    status="open",
    priority="Critical"
)

# Check if similar bug exists
for bug in existing:
    if "roadmap parser" in bug['title'].lower():
        print(f"Similar bug exists: BUG-{bug['bug_number']:03d}")
```

---

## Files

```
.claude/skills/shared/bug-tracking/
├── README.md              # This file
├── bug-tracking.md        # Skill instructions (for agents)
├── bug_tracking.py        # Main implementation
└── bug_parser.py          # Parser for existing markdown files

tickets/                   # Markdown tickets (auto-generated)
├── BUG-001.md
├── BUG-002.md
└── ...

data/orchestrator.db       # SQLite database
└── bugs table             # Bug data + analytics views
```

---

## Testing

```bash
# Run unit tests
pytest tests/unit/test_bug_tracking_skill.py -v

# Run integration tests
pytest tests/integration/test_bug_workflow.py -v

# Test parser
pytest tests/unit/test_bug_parser.py -v
```

---

## Migration from BugTracker

If you're using the old `coffee_maker/cli/bug_tracker.py`:

```python
from bug_tracking import BugTrackingSkill
from bug_parser import BugTicketParser
from pathlib import Path

# 1. Initialize new skill
skill = BugTrackingSkill()
parser = BugTicketParser()

# 2. Import all existing tickets
stats = parser.import_all_tickets(Path("tickets"), skill)
print(f"Migrated {stats['imported']} bugs to database")

# 3. Verify
all_bugs = skill.query_bugs(limit=1000)
print(f"Total bugs in database: {len(all_bugs)}")

# 4. Start using new skill!
result = skill.report_bug(
    title="Test bug after migration",
    description="Verifying new system works",
    reporter="system"
)
```

---

## Troubleshooting

### Database locked

If you get "database is locked" errors:

```python
# Check for long-running queries
# The skill uses WAL mode which should prevent locks

# If stuck, can try:
import sqlite3
conn = sqlite3.connect("data/orchestrator.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.close()
```

### Markdown file out of sync

If markdown file doesn't match database:

```python
# Re-sync from database
bug = skill.get_bug_by_number(66)
skill._write_markdown_ticket(
    bug_number=bug['bug_number'],
    title=bug['title'],
    description=bug['description'],
    priority=bug['priority'],
    status=bug['status'],
    category=bug['category'],
    reporter=bug['reporter'],
    assigned_to=bug['assigned_to'],
    created_at=bug['created_at'],
    reproduction_steps=[]
)
```

---

## References

- **SPEC-111**: Bug Tracking Database and Skill
- **CFR-014**: Orchestrator Database Tracing
- **PRIORITY 2.11**: Bug Fixing Workflow
- **Old System**: `coffee_maker/cli/bug_tracker.py` (file-based)

---

**Last Updated**: 2025-10-20
**Status**: ✅ Production Ready
**Maintainer**: architect + code_developer
