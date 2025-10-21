# SPEC-111: Bug Tracking Database and Skill

**Status**: Draft
**Created**: 2025-10-20
**Author**: architect
**Related**: CFR-014 (Orchestrator Database Tracing), PRIORITY 2.11 (Bug Fixing Workflow)

## Problem Statement

Currently, bug tracking relies solely on markdown files (`tickets/BUG-*.md`) created by `BugTracker` class. This approach has limitations:

1. **No Database Persistence** - Violates CFR-014 (all data should be in database)
2. **Limited Querying** - Cannot easily query bugs by status, priority, assignee, or date
3. **No Analytics** - Cannot track bug resolution velocity, patterns, or bottlenecks
4. **No Agent Integration** - No unified skill for agents to report, update, or query bugs
5. **Manual Status Updates** - Agents must manually edit markdown files
6. **No Cross-Reference** - Cannot link bugs to commits, PRs, or ROADMAP priorities

## Proposed Solution

### 1. Bug Tracking Database Schema

Add `bugs` table to existing `data/orchestrator.db` database:

```sql
CREATE TABLE bugs (
    -- Primary identification
    bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_number INTEGER UNIQUE NOT NULL,  -- BUG-001, BUG-002, etc.
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Classification
    priority TEXT NOT NULL,              -- Critical, High, Medium, Low
    status TEXT NOT NULL DEFAULT 'open', -- open, analyzing, in_progress, testing, resolved, closed
    category TEXT,                       -- crash, performance, ui, logic, documentation, etc.

    -- Ownership and tracking
    reporter TEXT NOT NULL,              -- User, assistant, architect, etc.
    assigned_to TEXT DEFAULT 'code_developer',
    discovered_in_priority INTEGER,     -- Which ROADMAP priority revealed the bug

    -- Timestamps (ISO8601 format)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT,

    -- Workflow tracking
    reproduction_steps TEXT,             -- JSON array of steps
    expected_behavior TEXT,
    actual_behavior TEXT,
    root_cause TEXT,
    fix_description TEXT,

    -- Links and references
    related_files TEXT,                  -- JSON array of file paths
    related_commits TEXT,                -- JSON array of commit SHashes
    pr_url TEXT,
    roadmap_priority TEXT,               -- Which priority should fix this

    -- Metrics
    time_to_resolve_ms INTEGER,         -- Time from creation to resolution
    time_to_close_ms INTEGER,           -- Time from creation to closure

    -- Additional context
    ticket_file_path TEXT,               -- Path to markdown ticket file
    metadata TEXT                        -- JSON blob for additional context
);

-- Indexes for fast queries
CREATE INDEX idx_bug_status ON bugs(status);
CREATE INDEX idx_bug_priority ON bugs(priority);
CREATE INDEX idx_bug_assigned_to ON bugs(assigned_to);
CREATE INDEX idx_bug_created_at ON bugs(created_at);
CREATE INDEX idx_bug_reporter ON bugs(reporter);
CREATE INDEX idx_bug_category ON bugs(category);
```

### 2. Analytics Views

#### Bug Resolution Velocity View
```sql
CREATE VIEW bug_resolution_velocity AS
SELECT
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total_bugs,
    SUM(CASE WHEN status = 'resolved' OR status = 'closed' THEN 1 ELSE 0 END) AS resolved,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open,
    AVG(CASE WHEN status = 'resolved' OR status = 'closed' THEN time_to_resolve_ms ELSE NULL END) AS avg_resolution_time_ms
FROM bugs
GROUP BY month
ORDER BY month DESC;
```

#### Bug Priority Distribution View
```sql
CREATE VIEW bug_priority_distribution AS
SELECT
    priority,
    status,
    COUNT(*) AS count,
    AVG(time_to_resolve_ms) AS avg_resolution_time_ms
FROM bugs
GROUP BY priority, status
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;
```

#### Bug Category Analysis View
```sql
CREATE VIEW bug_category_analysis AS
SELECT
    category,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'resolved' OR status = 'closed' THEN 1 ELSE 0 END) AS resolved,
    AVG(time_to_resolve_ms) AS avg_resolution_time_ms
FROM bugs
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total DESC;
```

#### Open Bugs Summary View
```sql
CREATE VIEW open_bugs_summary AS
SELECT
    bug_id,
    bug_number,
    title,
    priority,
    status,
    assigned_to,
    created_at,
    CAST((julianday('now') - julianday(created_at)) * 86400000 AS INTEGER) AS age_ms
FROM bugs
WHERE status NOT IN ('resolved', 'closed')
ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END,
    created_at ASC;
```

### 3. Bug Tracking Skill

Create `.claude/skills/shared/bug-tracking/bug_tracking.py`:

```python
"""Bug Tracking Skill for All Agents.

This skill provides a unified interface for agents to:
- Report new bugs
- Update bug status and information
- Query bugs by various criteria
- Link bugs to commits and PRs

All agents (assistant, code_developer, architect, project_manager) can use this skill.
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from coffee_maker.cli.bug_tracker import BugTracker  # Reuse existing file-based system


@dataclass
class Bug:
    """Bug data model."""
    bug_id: Optional[int]
    bug_number: int
    title: str
    description: str
    priority: str
    status: str
    category: Optional[str]
    reporter: str
    assigned_to: str
    discovered_in_priority: Optional[int]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]
    closed_at: Optional[str]
    reproduction_steps: Optional[str]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    root_cause: Optional[str]
    fix_description: Optional[str]
    related_files: Optional[str]
    related_commits: Optional[str]
    pr_url: Optional[str]
    roadmap_priority: Optional[str]
    time_to_resolve_ms: Optional[int]
    time_to_close_ms: Optional[int]
    ticket_file_path: Optional[str]
    metadata: Optional[str]


class BugTrackingSkill:
    """Unified bug tracking skill for all agents."""

    def __init__(self, db_path: str = "data/orchestrator.db"):
        """Initialize bug tracking skill.

        Args:
            db_path: Path to orchestrator database
        """
        self.db_path = Path(db_path)
        self.file_tracker = BugTracker()  # Reuse existing file-based system
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure bug tracking schema exists in database."""
        # Implementation: Create table if not exists
        pass

    def report_bug(
        self,
        title: str,
        description: str,
        reporter: str,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        reproduction_steps: Optional[List[str]] = None,
        discovered_in_priority: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Report a new bug.

        Args:
            title: Bug title
            description: Bug description
            reporter: Who reported (assistant, code_developer, architect, etc.)
            priority: Bug priority (auto-assessed if not provided)
            category: Bug category (crash, performance, ui, logic, etc.)
            reproduction_steps: Steps to reproduce
            discovered_in_priority: ROADMAP priority where bug was found

        Returns:
            Dictionary with bug_id, bug_number, ticket_file_path
        """
        # 1. Create markdown file using existing BugTracker
        bug_number, ticket_path = self.file_tracker.create_bug_ticket(
            description=description,
            title=title,
            priority=priority,
            reproduction_steps=reproduction_steps,
        )

        # 2. Insert into database
        # Implementation details...

        return {
            "bug_id": bug_id,
            "bug_number": bug_number,
            "ticket_file_path": str(ticket_path),
            "status": "open",
        }

    def update_bug_status(
        self,
        bug_number: int,
        status: str,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Update bug status.

        Args:
            bug_number: Bug number (e.g., 1 for BUG-001)
            status: New status (analyzing, in_progress, testing, resolved, closed)
            assigned_to: Reassign to different agent
            notes: Additional notes about status change

        Returns:
            True if successful
        """
        # Implementation: Update database + markdown file
        pass

    def add_bug_details(
        self,
        bug_number: int,
        root_cause: Optional[str] = None,
        fix_description: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
    ) -> bool:
        """Add analysis details to a bug.

        Args:
            bug_number: Bug number
            root_cause: Root cause analysis
            fix_description: Description of the fix
            expected_behavior: Expected behavior
            actual_behavior: Actual behavior

        Returns:
            True if successful
        """
        # Implementation: Update database + markdown file
        pass

    def link_bug_to_commit(self, bug_number: int, commit_sha: str) -> bool:
        """Link bug to a commit.

        Args:
            bug_number: Bug number
            commit_sha: Git commit SHA

        Returns:
            True if successful
        """
        pass

    def link_bug_to_pr(self, bug_number: int, pr_url: str) -> bool:
        """Link bug to a pull request.

        Args:
            bug_number: Bug number
            pr_url: GitHub PR URL

        Returns:
            True if successful
        """
        pass

    def query_bugs(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Bug]:
        """Query bugs by criteria.

        Args:
            status: Filter by status
            priority: Filter by priority
            assigned_to: Filter by assignee
            category: Filter by category
            limit: Maximum results to return

        Returns:
            List of matching bugs
        """
        pass

    def get_bug_by_number(self, bug_number: int) -> Optional[Bug]:
        """Get bug by bug number.

        Args:
            bug_number: Bug number (e.g., 1 for BUG-001)

        Returns:
            Bug object if found, None otherwise
        """
        pass

    def get_open_bugs_summary(self) -> Dict[str, Any]:
        """Get summary of open bugs.

        Returns:
            Dictionary with counts by priority and status
        """
        pass

    def get_bug_resolution_velocity(self) -> List[Dict[str, Any]]:
        """Get bug resolution velocity over time.

        Returns:
            List of monthly statistics
        """
        pass
```

### 4. Usage Examples

#### Assistant Reporting a Bug
```python
from bug_tracking import BugTrackingSkill

skill = BugTrackingSkill()
result = skill.report_bug(
    title="Orchestrator crashes when ROADMAP.md is missing",
    description="If ROADMAP.md is deleted, orchestrator crashes instead of creating it",
    reporter="assistant",
    priority="High",
    category="crash",
    discovered_in_priority=20,
)
# Returns: {"bug_id": 1, "bug_number": 1, "ticket_file_path": "tickets/BUG-001.md"}
```

#### Code Developer Updating Status
```python
skill.update_bug_status(
    bug_number=1,
    status="in_progress",
    notes="Reproduced locally, working on fix",
)
```

#### Architect Querying Bugs
```python
# Get all open High priority bugs
bugs = skill.query_bugs(status="open", priority="High")

# Get bugs assigned to code_developer
bugs = skill.query_bugs(assigned_to="code_developer")

# Get summary
summary = skill.get_open_bugs_summary()
# Returns: {"critical": 2, "high": 5, "medium": 3, "low": 1}
```

## Implementation Plan

### Phase 1: Database Schema (PRIORITY 1)
1. ✅ Write migration script `scripts/migrate_bugs_to_db.py`
2. ✅ Add `bugs` table to `data/orchestrator.db`
3. ✅ Create views for analytics
4. ✅ Migrate existing tickets to database

### Phase 2: Bug Tracking Skill (PRIORITY 2)
1. ✅ Create `.claude/skills/shared/bug-tracking/bug_tracking.py`
2. ✅ Implement `report_bug()`, `update_bug_status()`, `query_bugs()`
3. ✅ Implement database + markdown file sync
4. ✅ Add comprehensive tests

### Phase 3: Agent Integration (PRIORITY 3)
1. ✅ Update assistant to use skill for bug reports
2. ✅ Update code_developer to use skill for bug updates
3. ✅ Update project_manager to query bugs
4. ✅ Update architect to link bugs to specs

### Phase 4: Dashboard & Analytics (PRIORITY 4)
1. ✅ Add bug tracking panel to orchestrator dashboard
2. ✅ Display bug resolution velocity
3. ✅ Show open bugs by priority

## Acceptance Criteria

1. ✅ Bugs table exists in `data/orchestrator.db`
2. ✅ All analytics views created and functional
3. ✅ BugTrackingSkill implements all methods
4. ✅ Skill creates both database records AND markdown files
5. ✅ All agents can report, update, and query bugs
6. ✅ Migration script successfully migrates existing tickets
7. ✅ Tests cover all skill methods
8. ✅ Dashboard displays bug metrics

## Testing Strategy

### Unit Tests
- Test database schema creation
- Test bug creation (database + file)
- Test status updates
- Test query methods
- Test PR/commit linking

### Integration Tests
- Test assistant reporting bug → code_developer fixing → PR creation flow
- Test bug analytics views
- Test migration of existing tickets

### Manual Tests
- Verify markdown files stay in sync with database
- Verify dashboard displays correct metrics
- Verify agents can query and update bugs

## Migration Strategy

### Existing Tickets
1. Scan `tickets/` directory for existing BUG-*.md files
2. Parse each ticket and extract metadata
3. Insert into database with original timestamps
4. Preserve ticket files (no deletion)

### Backward Compatibility
- Keep existing `BugTracker` class functional
- New `BugTrackingSkill` wraps and extends `BugTracker`
- Markdown files remain source of truth for human readability
- Database is source of truth for querying and analytics

## Security Considerations

1. **SQL Injection**: Use parameterized queries
2. **File Path Injection**: Validate and sanitize file paths
3. **Access Control**: No sensitive data in bug descriptions
4. **Database Permissions**: Read/write only for orchestrator

## Performance Considerations

1. **Indexes**: Critical for fast queries on status, priority, assignee
2. **Batch Operations**: Support bulk updates for migration
3. **Connection Pooling**: Reuse database connections
4. **File I/O**: Minimize markdown file reads/writes

## Future Enhancements

1. **Bug Relationships**: Link bugs to each other (duplicate, related, blocks)
2. **Bug Notifications**: Alert agents when assigned to bug
3. **Bug Templates**: Category-specific bug report templates
4. **Automated Bug Detection**: Code reviewer auto-creates bugs
5. **Bug Prediction**: ML model to predict bug category and priority

## References

- CFR-014: Orchestrator Database Tracing
- SPEC-110: Orchestrator Database Tracing
- PRIORITY 2.11: Bug Fixing Workflow
- Existing: `coffee_maker/cli/bug_tracker.py`
- Existing: `.claude/skills/assistant/bug-analyzer/bug_analyzer.py`

---

**Implementation Status**: Draft (waiting for architect approval)
**Estimated Effort**: 2-3 days
**Dependencies**: SPEC-110 (Orchestrator Database)
**Blocks**: None
