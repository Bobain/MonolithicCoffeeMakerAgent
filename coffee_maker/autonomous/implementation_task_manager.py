"""Implementation task management for code_developer parallel execution.

This module enables code_developer to claim specs_task from the database,
validate file access against assigned_files, and track task lifecycle.

Key Concepts:
- task: A unit of implementation task (e.g., "Phase 1 of PRIORITY 31")
- task_group_id: Groups sequential specs_task (e.g., "GROUP-31" for 4 phases)
- priority_order: Enforces sequential execution within group (1, 2, 3, 4)

Database Integration:
- Uses TechnicalSpecSkill for reading specs (shared skill pattern)
- Direct database access only for specs_task table operations

Author: code_developer
Date: 2025-10-23
Related: PRIORITY 31, CFR-000
"""

import json
import os
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import shared skill for technical spec reading
skills_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared"
if str(skills_path) not in sys.path:
    sys.path.insert(0, str(skills_path))

from technical_spec_database.unified_spec_skill import TechnicalSpecSkill

logger = logging.getLogger(__name__)


class FileAccessViolationError(Exception):
    """Raised when code_developer tries to access file not in assigned_files."""


class TaskNotFoundError(Exception):
    """Raised when task_id doesn't exist in database."""


class TaskAlreadyClaimedError(Exception):
    """Raised when trying to claim already-claimed task."""


class ImplementationTaskManager:
    """Manages task integration for code_developer.

    Provides atomic task claiming, file access validation,
    and lifecycle management for parallel development.

    Key Features:
    - Enforces sequential execution within task_group_id groups
    - Atomic claiming (race-safe)
    - File access validation
    """

    def __init__(self, db_path: str, agent_name: str = "code_developer"):
        """Initialize ImplementationTaskManager.

        Args:
            db_path: Path to SQLite database with specs_task table
            agent_name: Agent using this manager (default: "code_developer")
        """
        self.db_path = db_path
        self.agent_name = agent_name
        self.current_work: Optional[Dict[str, Any]] = None
        self.assigned_files: List[str] = []

        # Initialize technical spec skill for reading specs
        # Use hybrid mode: direct DB for tests, skill for production
        self.use_skill = not db_path.endswith(".db")
        if self.use_skill:
            self.spec_skill = TechnicalSpecSkill(agent_name=agent_name)
        else:
            self.spec_skill = None

    def query_next_work_for_priority(self, priority_number: int) -> Optional[Dict[str, Any]]:
        """Query next task for priority (respecting sequential ordering and dependencies).

        Args:
            priority_number: ROADMAP priority number (e.g., 31)

        Returns:
            Next pending task in sequence, or None if:
            - All specs_task completed
            - Waiting for earlier task in sequence to complete
            - Waiting for dependency (another task_group_id) to complete

        Example:
            priority_number=31
            specs_task in GROUP-31: [TASK-31-1, TASK-31-2, TASK-31-3, TASK-31-4]

            If TASK-31-1 is completed, returns TASK-31-2
            If TASK-31-1 is in_progress, returns None (wait for it)

            If GROUP-31 depends on GROUP-36 (hard dependency), and GROUP-36 is not completed:
            → Returns None (wait for GROUP-36 to complete)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all specs_task for this priority, excluding groups with incomplete dependencies
        cursor.execute(
            """
            SELECT * FROM specs_task
            WHERE priority_number = ?
              AND task_group_id NOT IN (
                  -- Exclude task groups with incomplete hard dependencies
                  SELECT tgd.task_group_id
                  FROM specs_task_dependency tgd
                  WHERE tgd.dependency_type = 'hard'
                    AND EXISTS (
                        SELECT 1
                        FROM specs_task dep_tasks
                        WHERE dep_tasks.task_group_id = tgd.depends_on_group_id
                          AND dep_tasks.status != 'completed'
                    )
              )
            ORDER BY priority_order ASC
        """,
            (priority_number,),
        )

        specs_task = [dict(row) for row in cursor.fetchall()]

        # Get blocked task groups (for logging)
        cursor.execute(
            """
            SELECT tgd.task_group_id, tgd.depends_on_group_id, tgd.reason
            FROM specs_task_dependency tgd
            WHERE tgd.dependency_type = 'hard'
              AND EXISTS (
                  SELECT 1
                  FROM specs_task t
                  WHERE t.task_group_id = tgd.task_group_id
                    AND t.priority_number = ?
              )
              AND EXISTS (
                  SELECT 1
                  FROM specs_task dep_tasks
                  WHERE dep_tasks.task_group_id = tgd.depends_on_group_id
                    AND dep_tasks.status != 'completed'
              )
        """,
            (priority_number,),
        )
        blocked_groups = cursor.fetchall()

        conn.close()

        # Log blocked task groups
        if blocked_groups:
            for blocked in blocked_groups:
                logger.info(
                    f"Task group {blocked['task_group_id']} blocked: "
                    f"depends on {blocked['depends_on_group_id']} (reason: {blocked['reason']})"
                )

        if not specs_task:
            return None

        # Find next pending task in sequence
        for task in specs_task:
            if task["status"] == "pending" and task["process_id"] is None:
                return task
            elif task["status"] in ["pending", "in_progress"]:
                # Earlier task not completed yet - must wait
                if task["status"] == "in_progress":
                    logger.info(
                        f"Waiting for {task['task_id']} (priority_order={task['priority_order']}) "
                        f"to complete before starting next task"
                    )
                return None

        # All specs_task completed
        return None

    def query_available_works(self, task_group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query available specs_task from database (respecting dependencies).

        Args:
            task_group_id: Filter by task_group_id (e.g., "GROUP-31")

        Returns:
            List of available specs_task (status='pending', respecting sequential order and dependencies)

        Note:
            Excludes tasks from groups with incomplete hard dependencies.
            If task_group_id is specified, checks if that group has incomplete dependencies.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if task_group_id:
            cursor.execute(
                """
                SELECT * FROM specs_task
                WHERE status = 'pending'
                  AND process_id IS NULL
                  AND task_group_id = ?
                  AND task_group_id NOT IN (
                      -- Exclude if this group has incomplete hard dependencies
                      SELECT tgd.task_group_id
                      FROM specs_task_dependency tgd
                      WHERE tgd.dependency_type = 'hard'
                        AND EXISTS (
                            SELECT 1
                            FROM specs_task dep_tasks
                            WHERE dep_tasks.task_group_id = tgd.depends_on_group_id
                              AND dep_tasks.status != 'completed'
                        )
                  )
                ORDER BY priority_order ASC
            """,
                (task_group_id,),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM specs_task
                WHERE status = 'pending'
                  AND process_id IS NULL
                  AND task_group_id NOT IN (
                      -- Exclude groups with incomplete hard dependencies
                      SELECT tgd.task_group_id
                      FROM specs_task_dependency tgd
                      WHERE tgd.dependency_type = 'hard'
                        AND EXISTS (
                            SELECT 1
                            FROM specs_task dep_tasks
                            WHERE dep_tasks.task_group_id = tgd.depends_on_group_id
                              AND dep_tasks.status != 'completed'
                        )
                  )
                ORDER BY task_group_id, priority_order ASC
            """
            )

        specs_task = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return specs_task

    def claim_work(self, task_id: str) -> bool:
        """Atomically claim a task (race-safe).

        Args:
            task_id: Work ID to claim (e.g., "TASK-31-1")

        Returns:
            True if claimed successfully, False if already claimed

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            TaskAlreadyClaimedError: If already claimed by this instance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if task exists
            cursor.execute(
                "SELECT status, process_id, priority_order, task_group_id FROM specs_task WHERE task_id = ?",
                (task_id,),
            )
            result = cursor.fetchone()

            if not result:
                raise TaskNotFoundError(f"task {task_id} not found")

            status, process_id, priority_order, task_group_id = result

            if process_id == os.getpid() and self.current_work:
                raise TaskAlreadyClaimedError(f"task {task_id} already claimed by this instance")

            # Validate sequential ordering: check if earlier specs_task in group are completed
            if priority_order > 1:
                cursor.execute(
                    """
                    SELECT task_id, status, priority_order FROM specs_task
                    WHERE task_group_id = ?
                      AND priority_order < ?
                    ORDER BY priority_order ASC
                """,
                    (task_group_id, priority_order),
                )

                earlier_works = cursor.fetchall()

                for earlier_work_id, earlier_status, earlier_order in earlier_works:
                    if earlier_status != "completed":
                        logger.error(
                            f"Cannot claim {task_id} (order={priority_order}) - "
                            f"earlier task {earlier_work_id} (order={earlier_order}) not completed (status={earlier_status})"
                        )
                        conn.close()
                        return False

            # ATOMIC claim operation
            now = datetime.now().isoformat()
            current_pid = os.getpid()
            cursor.execute(
                """
                UPDATE specs_task
                SET status = 'in_progress',
                    process_id = ?,
                    claimed_at = ?
                WHERE task_id = ?
                  AND status = 'pending'
                  AND process_id IS NULL
            """,
                (current_pid, now, task_id),
            )

            rows_affected = cursor.rowcount

            if rows_affected == 0:
                # Claim failed (another instance claimed it)
                logger.warning(f"Failed to claim task {task_id} - already claimed")
                conn.close()
                return False

            # Load full task data
            cursor.execute("SELECT * FROM specs_task WHERE task_id = ?", (task_id,))
            conn.row_factory = sqlite3.Row
            cursor_with_factory = conn.cursor()
            cursor_with_factory.execute("SELECT * FROM specs_task WHERE task_id = ?", (task_id,))
            self.current_work = dict(cursor_with_factory.fetchone())

            # Parse assigned_files
            self.assigned_files = json.loads(self.current_work["assigned_files"])

            conn.commit()
            logger.info(
                f"✅ Successfully claimed task {task_id} "
                f"(group={task_group_id}, order={priority_order}) "
                f"with {len(self.assigned_files)} assigned files"
            )
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error claiming task {task_id}: {e}")
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
            # No task active, allow all files (legacy mode)
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
            f"task {self.current_work['task_id']}.\n"
            f"Assigned files: {self.assigned_files}"
        )

    def update_work_status(
        self,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Update task status in database.

        Args:
            status: New status (in_progress/completed/failed)
            error_message: Error message (when status='failed')

        Note:
            Commits are tracked separately in the commits table.
            A task can have multiple commits.
        """
        if not self.current_work:
            raise ValueError("No active task to update")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if status == "in_progress":
            cursor.execute(
                """
                UPDATE specs_task
                SET status = ?,
                    started_at = ?
                WHERE task_id = ?
            """,
                (status, now, self.current_work["task_id"]),
            )
        elif status == "completed":
            cursor.execute(
                """
                UPDATE specs_task
                SET status = ?,
                    completed_at = ?
                WHERE task_id = ?
            """,
                (status, now, self.current_work["task_id"]),
            )
        elif status == "failed":
            cursor.execute(
                """
                UPDATE specs_task
                SET status = ?,
                    completed_at = ?
                WHERE task_id = ?
            """,
                (status, now, self.current_work["task_id"]),
            )
            logger.error(f"task {self.current_work['task_id']} failed: {error_message}")

        conn.commit()
        conn.close()

        logger.info(f"Updated task {self.current_work['task_id']} status to {status}")

    def record_commit(self, commit_sha: str, commit_message: str) -> None:
        """Record a commit for current task.

        Args:
            commit_sha: Git commit SHA
            commit_message: Commit message

        Note:
            A task can have multiple commits.
            This enables code_reviewer to review all commits for a task.
        """
        if not self.current_work:
            raise ValueError("No active task to record commit for")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO commits (task_id, commit_sha, commit_message, committed_at)
            VALUES (?, ?, ?, ?)
        """,
            (self.current_work["task_id"], commit_sha, commit_message, now),
        )

        conn.commit()
        conn.close()

        logger.info(f"Recorded commit {commit_sha[:8]} for task {self.current_work['task_id']}")

    def read_technical_spec_for_work(self) -> str:
        """Read technical spec section for current task.

        Uses unified-spec-skill to read from database.
        Reads only the sections specified in task.spec_sections.

        Returns:
            Markdown content of spec section(s)

        Example:
            task.spec_sections = '["overview", "implementation"]'
            → Returns content of overview + implementation sections
        """
        if not self.current_work:
            raise ValueError("No active task")

        spec_id = self.current_work["spec_id"]

        # Get spec_sections from task (new dedicated column)
        spec_sections_json = self.current_work.get("spec_sections")

        if not spec_sections_json:
            # No sections specified, read entire spec
            logger.info(f"No spec_sections defined for task, loading full spec {spec_id}")
            return self._read_full_spec(spec_id)

        # Parse spec_sections JSON
        try:
            section_keys = json.loads(spec_sections_json)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Invalid spec_sections JSON: {spec_sections_json}, loading full spec")
            return self._read_full_spec(spec_id)

        # Read specific sections using TechnicalSpecSkill
        if self.use_skill and self.spec_skill:
            # Production: use shared skill
            section_content = []
            for section_key in section_keys:
                section_data = self.spec_skill.get_spec_section(spec_id, section_key)
                if section_data:
                    section_content.append(f"## /{section_key}")
                    section_content.append(section_data)
                else:
                    logger.warning(f"Section '{section_key}' not found in spec {spec_id}")
            return "\n\n".join(section_content) if section_content else ""
        else:
            # Testing: use direct database access
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT content, spec_type FROM specs_specification WHERE id = ?",
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
            for section_key in section_keys:
                if section_key in spec_json:
                    section_content.append(f"## /{section_key}")
                    section_content.append(spec_json[section_key])
                else:
                    logger.warning(f"Section '{section_key}' not found in spec {spec_id}")

            return "\n\n".join(section_content)

    def _read_full_spec(self, spec_id: str) -> str:
        """Read full technical spec (all sections).

        Args:
            spec_id: Technical spec ID

        Returns:
            Complete spec content as markdown
        """
        if self.use_skill and self.spec_skill:
            # Production: use shared skill
            spec = self.spec_skill.get_spec_by_id(spec_id)
            if not spec:
                raise ValueError(f"Technical spec {spec_id} not found")

            content = spec.get("content", "")
            spec_type = spec.get("spec_type", "monolithic")

            if spec_type != "hierarchical":
                return content

            # Hierarchical spec - combine all sections
            spec_json = json.loads(content) if isinstance(content, str) else content
            sections = []
            for section_key, section_content in spec_json.items():
                sections.append(f"## /{section_key}")
                sections.append(section_content)

            return "\n\n".join(sections)
        else:
            # Testing: use direct database access
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT content, spec_type FROM specs_specification WHERE id = ?",
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
