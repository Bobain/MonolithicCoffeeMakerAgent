"""Work management for code_developer parallel execution.

This module enables code_developer to claim works from the database,
validate file access against assigned_files, and track work lifecycle.

Key Concepts:
- work: A unit of implementation work (e.g., "Phase 1 of PRIORITY 31")
- related_works_id: Groups sequential works (e.g., "GROUP-31" for 4 phases)
- priority_order: Enforces sequential execution within group (1, 2, 3, 4)

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 31, CFR-000
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FileAccessViolationError(Exception):
    """Raised when code_developer tries to access file not in assigned_files."""


class WorkNotFoundError(Exception):
    """Raised when work_id doesn't exist in database."""


class WorkAlreadyClaimedError(Exception):
    """Raised when trying to claim already-claimed work."""


class WorkManager:
    """Manages work integration for code_developer.

    Provides atomic work claiming, file access validation,
    and lifecycle management for parallel development.

    Key Features:
    - Enforces sequential execution within related_works_id groups
    - Atomic claiming (race-safe)
    - File access validation
    """

    def __init__(self, db_path: str):
        """Initialize WorkManager.

        Args:
            db_path: Path to SQLite database with works table
        """
        self.db_path = db_path
        self.current_work: Optional[Dict[str, Any]] = None
        self.assigned_files: List[str] = []

    def query_next_work_for_priority(self, priority_number: int) -> Optional[Dict[str, Any]]:
        """Query next work for priority (respecting sequential ordering).

        Args:
            priority_number: ROADMAP priority number (e.g., 31)

        Returns:
            Next pending work in sequence, or None if:
            - All works completed
            - Waiting for earlier work in sequence to complete

        Example:
            priority_number=31
            works in GROUP-31: [WORK-31-1, WORK-31-2, WORK-31-3, WORK-31-4]

            If WORK-31-1 is completed, returns WORK-31-2
            If WORK-31-1 is in_progress, returns None (wait for it)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all works for this priority
        cursor.execute(
            """
            SELECT * FROM works
            WHERE priority_number = ?
            ORDER BY priority_order ASC
        """,
            (priority_number,),
        )

        works = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not works:
            return None

        # Find next pending work in sequence
        for work in works:
            if work["status"] == "pending" and work["claimed_by"] is None:
                return work
            elif work["status"] in ["pending", "in_progress"]:
                # Earlier work not completed yet - must wait
                if work["status"] == "in_progress":
                    logger.info(
                        f"Waiting for {work['work_id']} (priority_order={work['priority_order']}) "
                        f"to complete before starting next work"
                    )
                return None

        # All works completed
        return None

    def query_available_works(self, related_works_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query available works from database.

        Args:
            related_works_id: Filter by related_works_id (e.g., "GROUP-31")

        Returns:
            List of available works (status='pending', respecting sequential order)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if related_works_id:
            cursor.execute(
                """
                SELECT * FROM works
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                  AND related_works_id = ?
                ORDER BY priority_order ASC
            """,
                (related_works_id,),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM works
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                ORDER BY related_works_id, priority_order ASC
            """
            )

        works = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return works

    def claim_work(self, work_id: str) -> bool:
        """Atomically claim a work (race-safe).

        Args:
            work_id: Work ID to claim (e.g., "WORK-31-1")

        Returns:
            True if claimed successfully, False if already claimed

        Raises:
            WorkNotFoundError: If work_id doesn't exist
            WorkAlreadyClaimedError: If already claimed by this instance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if work exists
            cursor.execute(
                "SELECT status, claimed_by, priority_order, related_works_id FROM works WHERE work_id = ?",
                (work_id,),
            )
            result = cursor.fetchone()

            if not result:
                raise WorkNotFoundError(f"work {work_id} not found")

            status, claimed_by, priority_order, related_works_id = result

            if claimed_by == "code_developer" and self.current_work:
                raise WorkAlreadyClaimedError(f"work {work_id} already claimed by this instance")

            # Validate sequential ordering: check if earlier works in group are completed
            if priority_order > 1:
                cursor.execute(
                    """
                    SELECT work_id, status, priority_order FROM works
                    WHERE related_works_id = ?
                      AND priority_order < ?
                    ORDER BY priority_order ASC
                """,
                    (related_works_id, priority_order),
                )

                earlier_works = cursor.fetchall()

                for earlier_work_id, earlier_status, earlier_order in earlier_works:
                    if earlier_status != "completed":
                        logger.error(
                            f"Cannot claim {work_id} (order={priority_order}) - "
                            f"earlier work {earlier_work_id} (order={earlier_order}) not completed (status={earlier_status})"
                        )
                        conn.close()
                        return False

            # ATOMIC claim operation
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE works
                SET status = 'in_progress',
                    claimed_by = 'code_developer',
                    claimed_at = ?
                WHERE work_id = ?
                  AND status = 'pending'
                  AND claimed_by IS NULL
            """,
                (now, work_id),
            )

            rows_affected = cursor.rowcount

            if rows_affected == 0:
                # Claim failed (another instance claimed it)
                logger.warning(f"Failed to claim work {work_id} - already claimed")
                conn.close()
                return False

            # Load full work data
            cursor.execute("SELECT * FROM works WHERE work_id = ?", (work_id,))
            conn.row_factory = sqlite3.Row
            cursor_with_factory = conn.cursor()
            cursor_with_factory.execute("SELECT * FROM works WHERE work_id = ?", (work_id,))
            self.current_work = dict(cursor_with_factory.fetchone())

            # Parse assigned_files
            self.assigned_files = json.loads(self.current_work["assigned_files"])

            conn.commit()
            logger.info(
                f"✅ Successfully claimed work {work_id} "
                f"(group={related_works_id}, order={priority_order}) "
                f"with {len(self.assigned_files)} assigned files"
            )
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error claiming work {work_id}: {e}")
            raise
        finally:
            conn.close()

    def validate_file_access(self, file_path: str) -> bool:
        """Validate file access against assigned_files.

        Args:
            file_path: Path to file being accessed

        Returns:
            True if file in assigned_files, False otherwise

        Raises:
            FileAccessViolationError: If file not in assigned_files
        """
        if not self.current_work:
            # No work active, allow all files (legacy mode)
            return True

        # Normalize file path
        file_path = str(Path(file_path))

        # Check if file in assigned_files
        for assigned_file in self.assigned_files:
            assigned_path = str(Path(assigned_file))
            if file_path == assigned_path or file_path.endswith(assigned_path):
                return True

        # File not in assigned_files
        raise FileAccessViolationError(
            f"File access violation: {file_path} not in assigned_files for "
            f"work {self.current_work['work_id']}.\n"
            f"Assigned files: {self.assigned_files}"
        )

    def update_work_status(
        self,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Update work status in database.

        Args:
            status: New status (in_progress/completed/failed)
            error_message: Error message (when status='failed')

        Note:
            Commits are tracked separately in the commits table.
            A work can have multiple commits.
        """
        if not self.current_work:
            raise ValueError("No active work to update")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if status == "in_progress":
            cursor.execute(
                """
                UPDATE works
                SET status = ?,
                    started_at = ?
                WHERE work_id = ?
            """,
                (status, now, self.current_work["work_id"]),
            )
        elif status == "completed":
            cursor.execute(
                """
                UPDATE works
                SET status = ?,
                    completed_at = ?
                WHERE work_id = ?
            """,
                (status, now, self.current_work["work_id"]),
            )
        elif status == "failed":
            cursor.execute(
                """
                UPDATE works
                SET status = ?,
                    completed_at = ?
                WHERE work_id = ?
            """,
                (status, now, self.current_work["work_id"]),
            )
            logger.error(f"work {self.current_work['work_id']} failed: {error_message}")

        conn.commit()
        conn.close()

        logger.info(f"Updated work {self.current_work['work_id']} status to {status}")

    def record_commit(self, commit_sha: str, commit_message: str) -> None:
        """Record a commit for current work.

        Args:
            commit_sha: Git commit SHA
            commit_message: Commit message

        Note:
            A work can have multiple commits.
            This enables code_reviewer to review all commits for a work.
        """
        if not self.current_work:
            raise ValueError("No active work to record commit for")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO commits (work_id, commit_sha, commit_message, committed_at)
            VALUES (?, ?, ?, ?)
        """,
            (self.current_work["work_id"], commit_sha, commit_message, now),
        )

        conn.commit()
        conn.close()

        logger.info(f"Recorded commit {commit_sha[:8]} for work {self.current_work['work_id']}")

    def read_technical_spec_for_work(self) -> str:
        """Read technical spec section for current work.

        Uses unified-spec-skill to read from database.
        Reads only the section specified in work.scope_description.

        Returns:
            Markdown content of spec section

        Example:
            work.scope_description = "Phase 2: /implementation"
            → Returns content of /implementation section only
        """
        if not self.current_work:
            raise ValueError("No active work")

        spec_id = self.current_work["spec_id"]
        scope_description = self.current_work["scope_description"]

        # Parse section path from scope_description
        # Format: "Phase 2: /implementation" or "Section: /api_design, /implementation"
        import re

        section_paths = re.findall(r"/\w+", scope_description)

        if not section_paths:
            # No section specified, read entire spec
            return self._read_full_spec(spec_id)

        # Read specific sections using unified-spec-skill
        # For now, read from database directly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT content, spec_type FROM technical_specs WHERE id = ?",
            (spec_id,),
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Technical spec {spec_id} not found")

        content, spec_type = result

        if spec_type != "hierarchical":
            # Non-hierarchical spec, return full content
            return content

        # Parse hierarchical spec JSON
        spec_json = json.loads(content)

        # Extract requested sections
        section_content = []
        for section_path in section_paths:
            section_key = section_path.lstrip("/")
            if section_key in spec_json:
                section_content.append(f"## {section_path}")
                section_content.append(spec_json[section_key])
            else:
                logger.warning(f"Section {section_path} not found in spec {spec_id}")

        return "\n\n".join(section_content)

    def _read_full_spec(self, spec_id: str) -> str:
        """Read full technical spec (all sections).

        Args:
            spec_id: Technical spec ID

        Returns:
            Complete spec content as markdown
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT content, spec_type FROM technical_specs WHERE id = ?",
            (spec_id,),
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Technical spec {spec_id} not found")

        content, spec_type = result

        if spec_type != "hierarchical":
            return content

        # Hierarchical spec - combine all sections
        spec_json = json.loads(content)
        sections = []
        for section_key, section_content in spec_json.items():
            sections.append(f"## /{section_key}")
            sections.append(section_content)

        return "\n\n".join(sections)
