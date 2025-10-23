"""Work session management for code_developer parallel execution.

This module enables code_developer to claim work_sessions from the database,
validate file access against assigned_files, and track work_session lifecycle.

Author: code_developer (implementing SPEC-131)
Date: 2025-10-23
Related: PRIORITY 31, SPEC-131, CFR-000
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


class WorkSessionNotFoundError(Exception):
    """Raised when work_session_id doesn't exist in database."""


class WorkSessionAlreadyClaimedError(Exception):
    """Raised when trying to claim already-claimed work_session."""


class WorkSessionManager:
    """Manages work_session integration for code_developer.

    Provides atomic work_session claiming, file access validation,
    and lifecycle management for parallel development.
    """

    def __init__(self, db_path: str):
        """Initialize WorkSessionManager.

        Args:
            db_path: Path to SQLite database with work_sessions table
        """
        self.db_path = db_path
        self.current_work_session: Optional[Dict[str, Any]] = None
        self.assigned_files: List[str] = []

    def query_available_work_sessions(self, scope: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query available work_sessions from database.

        Args:
            scope: Filter by scope (phase/section/module) or None for all

        Returns:
            List of available work_sessions (status='pending')
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if scope:
            cursor.execute(
                """
                SELECT * FROM work_sessions
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                  AND scope = ?
                ORDER BY created_at ASC
            """,
                (scope,),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM work_sessions
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                ORDER BY created_at ASC
            """
            )

        work_sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return work_sessions

    def claim_work_session(self, work_id: str) -> bool:
        """Atomically claim a work_session (race-safe).

        Args:
            work_id: Work session ID to claim

        Returns:
            True if claimed successfully, False if already claimed

        Raises:
            WorkSessionNotFoundError: If work_id doesn't exist
            WorkSessionAlreadyClaimedError: If already claimed by this instance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if work_session exists
            cursor.execute(
                "SELECT status, claimed_by FROM work_sessions WHERE work_id = ?",
                (work_id,),
            )
            result = cursor.fetchone()

            if not result:
                raise WorkSessionNotFoundError(f"work_session {work_id} not found")

            status, claimed_by = result

            if claimed_by == "code_developer" and self.current_work_session:
                raise WorkSessionAlreadyClaimedError(f"work_session {work_id} already claimed by this instance")

            # ATOMIC claim operation
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE work_sessions
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
                logger.warning(f"Failed to claim work_session {work_id} - already claimed")
                conn.close()
                return False

            # Load full work_session data
            cursor.execute("SELECT * FROM work_sessions WHERE work_id = ?", (work_id,))
            conn.row_factory = sqlite3.Row
            cursor_with_factory = conn.cursor()
            cursor_with_factory.execute("SELECT * FROM work_sessions WHERE work_id = ?", (work_id,))
            self.current_work_session = dict(cursor_with_factory.fetchone())

            # Parse assigned_files
            self.assigned_files = json.loads(self.current_work_session["assigned_files"])

            conn.commit()
            logger.info(
                f"✅ Successfully claimed work_session {work_id} with " f"{len(self.assigned_files)} assigned files"
            )
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error claiming work_session {work_id}: {e}")
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
        if not self.current_work_session:
            # No work_session active, allow all files (legacy mode)
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
            f"work_session {self.current_work_session['work_id']}.\n"
            f"Assigned files: {self.assigned_files}"
        )

    def update_work_session_status(
        self,
        status: str,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update work_session status in database.

        Args:
            status: New status (in_progress/completed/failed)
            commit_sha: Git commit SHA (when status='completed')
            error_message: Error message (when status='failed')
        """
        if not self.current_work_session:
            raise ValueError("No active work_session to update")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if status == "in_progress":
            cursor.execute(
                """
                UPDATE work_sessions
                SET status = ?,
                    started_at = ?
                WHERE work_id = ?
            """,
                (status, now, self.current_work_session["work_id"]),
            )
        elif status == "completed":
            cursor.execute(
                """
                UPDATE work_sessions
                SET status = ?,
                    completed_at = ?,
                    commit_sha = ?
                WHERE work_id = ?
            """,
                (status, now, commit_sha, self.current_work_session["work_id"]),
            )
        elif status == "failed":
            # Store error in scope_description (or add error_message column)
            cursor.execute(
                """
                UPDATE work_sessions
                SET status = ?,
                    completed_at = ?
                WHERE work_id = ?
            """,
                (status, now, self.current_work_session["work_id"]),
            )
            logger.error(f"work_session {self.current_work_session['work_id']} " f"failed: {error_message}")

        conn.commit()
        conn.close()

        logger.info(f"Updated work_session {self.current_work_session['work_id']} " f"status to {status}")

    def read_technical_spec_for_work(self) -> str:
        """Read technical spec section for current work_session.

        Uses unified-spec-skill to read from database.
        Reads only the section specified in work_session.scope_description.

        Returns:
            Markdown content of spec section

        Example:
            work_session.scope_description = "Phase 2: /implementation"
            → Returns content of /implementation section only
        """
        if not self.current_work_session:
            raise ValueError("No active work_session")

        spec_id = self.current_work_session["spec_id"]
        scope_description = self.current_work_session["scope_description"]

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
