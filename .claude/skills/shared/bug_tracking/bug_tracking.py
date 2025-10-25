"""Bug Tracking Skill - Unified bug tracking interface for all agents.

This skill provides database-backed bug tracking with markdown file synchronization.
It implements SPEC-111 and maintains compatibility with existing BugTracker class.

Architecture:
- SQLite database (data/orchestrator.db) for structured data and analytics
- Markdown files (tickets/BUG-*.md) for human readability
- Bidirectional sync: database ↔ markdown files

Usage:
    >>> from bug_tracking import BugTrackingSkill
    >>> skill = BugTrackingSkill()
    >>> result = skill.report_bug(
    ...     title="Feature X crashes",
    ...     description="System crashes on empty input",
    ...     reporter="assistant",
    ...     priority="High"
    ... )

Related:
    SPEC-111: Bug Tracking Database and Skill
    CFR-014: Orchestrator Database Tracing
    PRIORITY 2.11: Bug Fixing Workflow
"""

import json
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Bug:
    """Bug data model."""

    bug_id: int
    bug_number: int
    title: str
    description: str
    priority: str  # Critical, High, Medium, Low
    status: str  # open, analyzing, in_progress, testing, resolved, closed
    category: Optional[str]
    reporter: str
    assigned_to: str
    discovered_in_priority: Optional[int]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]
    closed_at: Optional[str]
    reproduction_steps: Optional[List[str]]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    root_cause: Optional[str]
    fix_description: Optional[str]
    related_files: Optional[List[str]]
    related_commits: Optional[List[str]]
    pr_url: Optional[str]
    roadmap_priority: Optional[str]
    ticket_file_path: str
    test_file_path: Optional[str]
    test_name: Optional[str]
    metadata: Optional[Dict[str, Any]]


class BugTrackingSkill:
    """Unified bug tracking interface using SQLite + markdown files.

    This skill provides:
    - Database-backed bug tracking (structured queries, analytics)
    - Markdown file generation (human readability, git-trackable)
    - Bidirectional sync (database ↔ markdown)
    - Parser for existing markdown bugs
    - Editor for bug updates

    Attributes:
        db_path: Path to SQLite database
        tickets_dir: Path to markdown tickets directory
    """

    def __init__(self, db_path: str = "data/orchestrator.db", tickets_dir: str = "tickets"):
        """Initialize bug tracking skill.

        Args:
            db_path: Path to SQLite database
            tickets_dir: Path to tickets directory
        """
        self.db_path = Path(db_path)
        self.tickets_dir = Path(tickets_dir)

        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema with bugs table and analytics views."""
        schema_sql = """
        -- Enable WAL mode for concurrent access
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;

        -- Bugs table
        CREATE TABLE IF NOT EXISTS bugs (
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
            reproduction_steps TEXT,
            expected_behavior TEXT,
            actual_behavior TEXT,
            root_cause TEXT,
            fix_description TEXT,
            related_files TEXT,
            related_commits TEXT,
            pr_url TEXT,
            roadmap_priority TEXT,
            time_to_resolve_ms INTEGER,
            time_to_close_ms INTEGER,
            ticket_file_path TEXT,
            test_file_path TEXT,
            test_name TEXT,
            metadata TEXT
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_bug_status ON bugs(status);
        CREATE INDEX IF NOT EXISTS idx_bug_priority ON bugs(priority);
        CREATE INDEX IF NOT EXISTS idx_bug_assigned_to ON bugs(assigned_to);
        CREATE INDEX IF NOT EXISTS idx_bug_created_at ON bugs(created_at);
        CREATE INDEX IF NOT EXISTS idx_bug_reporter ON bugs(reporter);
        CREATE INDEX IF NOT EXISTS idx_bug_category ON bugs(category);

        -- Analytics view: Bug resolution velocity
        CREATE VIEW IF NOT EXISTS bug_resolution_velocity AS
        SELECT
            strftime('%Y-%m', created_at) AS month,
            COUNT(*) AS total_bugs,
            SUM(CASE WHEN status = 'resolved' OR status = 'closed' THEN 1 ELSE 0 END) AS resolved,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open,
            AVG(CASE WHEN status = 'resolved' OR status = 'closed' THEN time_to_resolve_ms ELSE NULL END) AS avg_resolution_time_ms
        FROM bugs
        GROUP BY month
        ORDER BY month DESC;

        -- Analytics view: Bug priority distribution
        CREATE VIEW IF NOT EXISTS bug_priority_distribution AS
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

        -- Analytics view: Bug category analysis
        CREATE VIEW IF NOT EXISTS bug_category_analysis AS
        SELECT
            category,
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'resolved' OR status = 'closed' THEN 1 ELSE 0 END) AS resolved,
            AVG(time_to_resolve_ms) AS avg_resolution_time_ms
        FROM bugs
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY total DESC;

        -- Analytics view: Open bugs summary
        CREATE VIEW IF NOT EXISTS open_bugs_summary AS
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
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("Bug tracking database initialized")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize bug tracking database: {e}")
            raise

    def report_bug(
        self,
        title: str,
        description: str,
        reporter: str,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        reproduction_steps: Optional[List[str]] = None,
        discovered_in_priority: Optional[int] = None,
        assigned_to: str = "code_developer",
    ) -> Dict[str, Any]:
        """Report a new bug.

        Args:
            title: Bug title (concise)
            description: Detailed description
            reporter: Reporter name (assistant, user, architect, etc.)
            priority: Critical, High, Medium, Low (auto-assessed if None)
            category: crash, performance, ui, logic, etc.
            reproduction_steps: List of reproduction steps
            discovered_in_priority: ROADMAP priority number where bug was found
            assigned_to: Agent to assign bug to

        Returns:
            Dict with bug_id, bug_number, ticket_file_path, status
        """
        # Auto-assess priority if not provided
        if priority is None:
            priority = self._assess_priority(description)

        # Get next bug number
        bug_number = self._get_next_bug_number()

        # Create timestamp
        now = datetime.now().isoformat()

        # Serialize lists
        repro_steps_json = json.dumps(reproduction_steps) if reproduction_steps else None

        # Generate ticket file path
        ticket_path = self.tickets_dir / f"BUG-{bug_number:03d}.md"

        # Insert into database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO bugs (
                        bug_number, title, description, priority, status, category,
                        reporter, assigned_to, discovered_in_priority, created_at, updated_at,
                        reproduction_steps, ticket_file_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bug_number,
                        title,
                        description,
                        priority,
                        "open",
                        category,
                        reporter,
                        assigned_to,
                        discovered_in_priority,
                        now,
                        now,
                        repro_steps_json,
                        str(ticket_path),
                    ),
                )
                bug_id = cursor.lastrowid
                conn.commit()

                # Generate markdown ticket
                self._write_markdown_ticket(
                    bug_number=bug_number,
                    title=title,
                    description=description,
                    priority=priority,
                    status="open",
                    category=category,
                    reporter=reporter,
                    assigned_to=assigned_to,
                    created_at=now,
                    reproduction_steps=reproduction_steps or [],
                )

                logger.info(f"Bug reported: BUG-{bug_number:03d} ({priority}) - {title}")

                return {
                    "bug_id": bug_id,
                    "bug_number": bug_number,
                    "ticket_file_path": str(ticket_path),
                    "status": "open",
                }

        except sqlite3.Error as e:
            logger.error(f"Failed to report bug: {e}")
            raise

    def update_bug_status(
        self,
        bug_number: int,
        status: str,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Update bug status.

        Args:
            bug_number: Bug number
            status: New status (open, analyzing, in_progress, testing, resolved, closed)
            assigned_to: Reassign to different agent
            notes: Status change notes

        Returns:
            True if successful
        """
        now = datetime.now().isoformat()

        # Calculate resolution/close times
        resolved_at = now if status == "resolved" else None
        closed_at = now if status == "closed" else None

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update database
                update_fields = ["status = ?", "updated_at = ?"]
                update_values = [status, now]

                if assigned_to:
                    update_fields.append("assigned_to = ?")
                    update_values.append(assigned_to)

                if resolved_at:
                    update_fields.append("resolved_at = ?")
                    update_values.append(resolved_at)
                    # Calculate time to resolve
                    cursor = conn.execute("SELECT created_at FROM bugs WHERE bug_number = ?", (bug_number,))
                    row = cursor.fetchone()
                    if row:
                        created = datetime.fromisoformat(row[0])
                        resolved = datetime.fromisoformat(resolved_at)
                        time_to_resolve_ms = int((resolved - created).total_seconds() * 1000)
                        update_fields.append("time_to_resolve_ms = ?")
                        update_values.append(time_to_resolve_ms)

                if closed_at:
                    update_fields.append("closed_at = ?")
                    update_values.append(closed_at)

                update_values.append(bug_number)
                sql = f"UPDATE bugs SET {', '.join(update_fields)} WHERE bug_number = ?"

                conn.execute(sql, update_values)
                conn.commit()

                # Update markdown ticket
                self._update_markdown_status(bug_number, status)

                logger.info(f"Bug BUG-{bug_number:03d} status updated to: {status}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Failed to update bug status: {e}")
            return False

    def add_bug_details(
        self,
        bug_number: int,
        root_cause: Optional[str] = None,
        fix_description: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        test_file_path: Optional[str] = None,
        test_name: Optional[str] = None,
    ) -> bool:
        """Add bug details (root cause, fix, behaviors, tests).

        Args:
            bug_number: Bug number
            root_cause: Root cause analysis
            fix_description: How the bug was fixed
            expected_behavior: What should happen
            actual_behavior: What actually happens
            test_file_path: Path to regression test file
            test_name: Name of regression test function

        Returns:
            True if successful
        """
        now = datetime.now().isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                update_fields = ["updated_at = ?"]
                update_values = [now]

                if root_cause:
                    update_fields.append("root_cause = ?")
                    update_values.append(root_cause)

                if fix_description:
                    update_fields.append("fix_description = ?")
                    update_values.append(fix_description)

                if expected_behavior:
                    update_fields.append("expected_behavior = ?")
                    update_values.append(expected_behavior)

                if actual_behavior:
                    update_fields.append("actual_behavior = ?")
                    update_values.append(actual_behavior)

                if test_file_path:
                    update_fields.append("test_file_path = ?")
                    update_values.append(test_file_path)

                if test_name:
                    update_fields.append("test_name = ?")
                    update_values.append(test_name)

                update_values.append(bug_number)
                sql = f"UPDATE bugs SET {', '.join(update_fields)} WHERE bug_number = ?"

                conn.execute(sql, update_values)
                conn.commit()

                # Update markdown ticket (if needed)
                self._update_markdown_details(
                    bug_number,
                    root_cause,
                    fix_description,
                    expected_behavior,
                    actual_behavior,
                    test_file_path,
                    test_name,
                )

                logger.info(f"Bug BUG-{bug_number:03d} details updated")
                return True

        except sqlite3.Error as e:
            logger.error(f"Failed to add bug details: {e}")
            return False

    def link_bug_to_commit(self, bug_number: int, commit_sha: str) -> bool:
        """Link bug to git commit.

        Args:
            bug_number: Bug number
            commit_sha: Git commit SHA

        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get existing commits
                cursor = conn.execute(
                    "SELECT related_commits FROM bugs WHERE bug_number = ?",
                    (bug_number,),
                )
                row = cursor.fetchone()
                if not row:
                    return False

                commits = json.loads(row[0]) if row[0] else []
                if commit_sha not in commits:
                    commits.append(commit_sha)

                # Update database
                conn.execute(
                    "UPDATE bugs SET related_commits = ?, updated_at = ? WHERE bug_number = ?",
                    (json.dumps(commits), datetime.now().isoformat(), bug_number),
                )
                conn.commit()

                logger.info(f"Bug BUG-{bug_number:03d} linked to commit {commit_sha}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Failed to link bug to commit: {e}")
            return False

    def link_bug_to_pr(self, bug_number: int, pr_url: str) -> bool:
        """Link bug to GitHub PR.

        Args:
            bug_number: Bug number
            pr_url: GitHub PR URL

        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE bugs SET pr_url = ?, updated_at = ? WHERE bug_number = ?",
                    (pr_url, datetime.now().isoformat(), bug_number),
                )
                conn.commit()

                logger.info(f"Bug BUG-{bug_number:03d} linked to PR: {pr_url}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Failed to link bug to PR: {e}")
            return False

    def query_bugs(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Query bugs with filters.

        Args:
            status: Filter by status
            priority: Filter by priority
            assigned_to: Filter by assignee
            category: Filter by category
            limit: Max results

        Returns:
            List of bug dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                where_clauses = []
                params = []

                if status:
                    where_clauses.append("status = ?")
                    params.append(status)

                if priority:
                    where_clauses.append("priority = ?")
                    params.append(priority)

                if assigned_to:
                    where_clauses.append("assigned_to = ?")
                    params.append(assigned_to)

                if category:
                    where_clauses.append("category = ?")
                    params.append(category)

                where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
                params.append(limit)

                cursor = conn.execute(
                    f"SELECT * FROM bugs {where_sql} ORDER BY created_at DESC LIMIT ?",
                    params,
                )

                return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"Failed to query bugs: {e}")
            return []

    def get_bug_by_number(self, bug_number: int) -> Optional[Dict[str, Any]]:
        """Get bug by number.

        Args:
            bug_number: Bug number

        Returns:
            Bug dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM bugs WHERE bug_number = ?", (bug_number,))
                row = cursor.fetchone()
                return dict(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Failed to get bug: {e}")
            return None

    def get_open_bugs_summary(self) -> Dict[str, int]:
        """Get summary of open bugs by priority.

        Returns:
            Dict with counts: {"critical": 2, "high": 5, "medium": 3, "low": 1}
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT priority, COUNT(*) as count
                    FROM bugs
                    WHERE status NOT IN ('resolved', 'closed')
                    GROUP BY priority
                    """
                )

                summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
                for row in cursor.fetchall():
                    priority = row[0].lower()
                    count = row[1]
                    if priority in summary:
                        summary[priority] = count

                return summary

        except sqlite3.Error as e:
            logger.error(f"Failed to get bugs summary: {e}")
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}

    def get_bug_resolution_velocity(self) -> List[Dict[str, Any]]:
        """Get bug resolution velocity by month.

        Returns:
            List of monthly stats
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM bug_resolution_velocity")
                return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"Failed to get resolution velocity: {e}")
            return []

    def _get_next_bug_number(self) -> int:
        """Get next available bug number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT MAX(bug_number) FROM bugs")
                max_num = cursor.fetchone()[0]
                return (max_num or 0) + 1

        except sqlite3.Error as e:
            logger.error(f"Failed to get next bug number: {e}")
            return 1

    def _assess_priority(self, description: str) -> str:
        """Auto-assess bug priority from description."""
        description_lower = description.lower()

        critical_keywords = [
            "crash",
            "crashes",
            "data loss",
            "security",
            "critical",
            "broken",
        ]
        high_keywords = ["error", "exception", "fails", "blocks", "prevents"]

        for keyword in critical_keywords:
            if keyword in description_lower:
                return "Critical"

        for keyword in high_keywords:
            if keyword in description_lower:
                return "High"

        return "Medium"

    def _write_markdown_ticket(
        self,
        bug_number: int,
        title: str,
        description: str,
        priority: str,
        status: str,
        category: Optional[str],
        reporter: str,
        assigned_to: str,
        created_at: str,
        reproduction_steps: List[str],
    ) -> None:
        """Write markdown ticket file."""
        status_emoji = {
            "open": "🔴",
            "analyzing": "🔍",
            "in_progress": "🟡",
            "testing": "🧪",
            "resolved": "✅",
            "closed": "⚫",
        }.get(status, "🔴")

        steps = "\n".join(f"{i+1}. {step}" for i, step in enumerate(reproduction_steps))
        if not steps:
            steps = "_To be determined during analysis_"

        category_line = f"\n**Category**: {category}" if category else ""

        content = f"""# BUG-{bug_number:03d}: {title}

**Status**: {status_emoji} {status.replace('_', ' ').title()}
**Priority**: {priority}
**Created**: {created_at}
**Reporter**: {reporter}
**Assigned**: {assigned_to}{category_line}

## Description

{description}

## Reproduction Steps

{steps}

## Expected Behavior

_To be determined during analysis_

## Actual Behavior

_To be determined during analysis_

## Definition of Done

- [ ] Bug reproduced locally
- [ ] Root cause identified
- [ ] Technical specification written
- [ ] Fix implemented
- [ ] Regression tests added
- [ ] All tests passing
- [ ] No regressions in existing functionality
- [ ] Documentation updated if needed
- [ ] PR created and reviewed
- [ ] User validated fix

## Analysis (code_developer)

_Phase 1: Analysis - To be filled by code_developer_

## Technical Spec (code_developer)

_Phase 2: Technical Spec - To be filled by code_developer_

## Implementation (code_developer)

_Phase 3: Implementation - To be filled by code_developer_

## Testing Results (code_developer)

_Phase 4: Testing - To be filled by code_developer_

## Regression Test

**Test File**: _Path to test file (e.g., `tests/test_bug_{bug_number:03d}_{title.lower().replace(' ', '_')[:30]}.py`)_

**Test Name**: _Test function name (e.g., `test_bug_{bug_number:03d}_reproduction`)_

**Coverage**:
- [ ] Bug reproduction test added (fails before fix, passes after fix)
- [ ] Edge cases covered
- [ ] Test runs in CI/CD pipeline
- [ ] Test documentation added

**Notes**: _Additional testing notes, edge cases, or related tests_

## PR Link

_Phase 5: PR Creation - To be filled by code_developer_

---

**Workflow**: User → project-manager → code_developer → Analysis → Tech Spec → Implementation → Testing → Regression Test → PR → Done
"""

        ticket_path = self.tickets_dir / f"BUG-{bug_number:03d}.md"
        ticket_path.write_text(content)
        logger.debug(f"Markdown ticket written: {ticket_path}")

    def _update_markdown_status(self, bug_number: int, status: str) -> None:
        """Update status in markdown ticket."""
        ticket_path = self.tickets_dir / f"BUG-{bug_number:03d}.md"

        if not ticket_path.exists():
            logger.warning(f"Ticket file not found: {ticket_path}")
            return

        status_emoji = {
            "open": "🔴",
            "analyzing": "🔍",
            "in_progress": "🟡",
            "testing": "🧪",
            "resolved": "✅",
            "closed": "⚫",
        }.get(status, "🔴")

        content = ticket_path.read_text()
        updated = re.sub(
            r"(\*\*Status\*\*:)\s*[🔴🔍🟡🧪✅⚫]?\s*\w+",
            rf"\1 {status_emoji} {status.replace('_', ' ').title()}",
            content,
            count=1,
        )
        ticket_path.write_text(updated)
        logger.debug(f"Markdown status updated: BUG-{bug_number:03d} → {status}")

    def _update_markdown_details(
        self,
        bug_number: int,
        root_cause: Optional[str],
        fix_description: Optional[str],
        expected_behavior: Optional[str],
        actual_behavior: Optional[str],
        test_file_path: Optional[str],
        test_name: Optional[str],
    ) -> None:
        """Update details in markdown ticket."""
        ticket_path = self.tickets_dir / f"BUG-{bug_number:03d}.md"

        if not ticket_path.exists():
            logger.warning(f"Ticket file not found: {ticket_path}")
            return

        content = ticket_path.read_text()

        if expected_behavior:
            content = re.sub(
                r"## Expected Behavior\n\n.*?\n\n",
                f"## Expected Behavior\n\n{expected_behavior}\n\n",
                content,
                flags=re.DOTALL,
            )

        if actual_behavior:
            content = re.sub(
                r"## Actual Behavior\n\n.*?\n\n",
                f"## Actual Behavior\n\n{actual_behavior}\n\n",
                content,
                flags=re.DOTALL,
            )

        if test_file_path:
            content = re.sub(
                r"\*\*Test File\*\*:.*",
                f"**Test File**: `{test_file_path}`",
                content,
            )

        if test_name:
            content = re.sub(
                r"\*\*Test Name\*\*:.*",
                f"**Test Name**: `{test_name}`",
                content,
            )

        ticket_path.write_text(content)
        logger.debug(f"Markdown details updated: BUG-{bug_number:03d}")
