"""Orchestrator Agent Management Skill.

Enables orchestrator to spawn, monitor, and manage architect and code_developer instances.

CFR-014 Compliant: Uses SQLite database instead of JSON files.

Author: architect + code_developer
Date: 2025-10-20
Related: Parallel execution, autonomous orchestration, CFR-014 compliance
"""

import logging
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OrchestratorAgentManagementSkill:
    """
    Manages agent spawning, monitoring, and cleanup for orchestrator.

    CFR-014 Compliance: All state stored in data/orchestrator.db (agent_lifecycle table).

    Capabilities:
    - Spawn architect/code_developer instances
    - Monitor process status (running/completed/failed)
    - Track active agents (PIDs, tasks, start times)
    - Detect hung processes
    - Clean up resources after completion
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize agent management skill.

        Args:
            db_path: Path to SQLite database (default: data/orchestrator.db)
        """
        self.db_path = db_path or Path("data/orchestrator.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database connection
        self._init_db()

    def _init_db(self):
        """
        Initialize database connection.

        The agent_lifecycle table should already exist (created by orchestrator migrations).
        """
        # Verify database and table exist
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}. "
                f"Run orchestrator migrations first: coffee_maker/orchestrator/migrate_*.py"
            )

        # Test connection and verify table exists
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_lifecycle'")
            if not cursor.fetchone():
                raise RuntimeError("agent_lifecycle table not found. Run orchestrator migrations first.")
        finally:
            conn.close()

        logger.debug(f"Agent management skill initialized with database: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.Connection(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an agent management action.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            Result dict with action output or error
        """
        try:
            if action == "spawn_architect":
                return self._spawn_architect(**kwargs)
            elif action == "spawn_code_developer":
                return self._spawn_code_developer(**kwargs)
            elif action == "spawn_code_developer_bug_fix":
                return self._spawn_code_developer_bug_fix(**kwargs)
            elif action == "spawn_project_manager":
                return self._spawn_project_manager(**kwargs)
            elif action == "spawn_code_reviewer":
                return self._spawn_code_reviewer(**kwargs)
            elif action == "check_status":
                return self._check_status(**kwargs)
            elif action == "get_output":
                return self._get_output(**kwargs)
            elif action == "list_active_agents":
                return self._list_active_agents(**kwargs)
            elif action == "cleanup_agent":
                return self._cleanup_agent(**kwargs)
            elif action == "detect_hung_agents":
                return self._detect_hung_agents(**kwargs)
            elif action == "kill_agent":
                return self._kill_agent(**kwargs)
            else:
                return {"error": f"Unknown action: {action}", "result": None}

        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}", exc_info=True)
            return {"error": str(e), "result": None}

    def _spawn_architect(
        self,
        priority_number: Optional[int] = None,
        priority_name: Optional[str] = None,
        task_type: str = "create_spec",
        auto_approve: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Spawn architect instance for spec creation.

        Args:
            priority_number: Priority number to work on (optional for some task types)
            priority_name: Priority name (e.g., "US-059" or "PRIORITY 59")
            task_type: Type of task (create_spec, refactoring_analysis, etc.)
            auto_approve: Auto-approve architect decisions

        Returns:
            Spawn result with PID and task info
        """
        # Build command
        cmd = ["poetry", "run", "architect"]

        if task_type == "create_spec":
            if priority_number is None:
                raise ValueError("priority_number required for create_spec task type")
            cmd.extend(["create-spec", f"--priority={priority_number}"])
        elif task_type == "refactoring_analysis":
            cmd.extend(["analyze-codebase", "--force"])

        # Spawn process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd(),
        )

        # Track agent in database
        if priority_number:
            task_id = f"spec-{priority_number}"
        else:
            task_id = f"{task_type}-{int(time.time())}"

        spawned_at = datetime.now().isoformat()

        # Insert into agent_lifecycle table
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type, priority_number,
                    spawned_at, started_at, status, command
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process.pid,
                    "architect",
                    task_id,
                    task_type,
                    priority_number,
                    spawned_at,
                    spawned_at,  # started_at = spawned_at initially
                    "spawned",
                    " ".join(cmd),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": process.pid,
            "agent_type": "architect",
            "task_id": task_id,
            "task_type": task_type,
            "priority_number": priority_number,
            "command": " ".join(cmd),
            "started_at": spawned_at,
            "status": "spawned",
        }

        if priority_name:
            logger.info(f"Spawned architect (PID {process.pid}) for {priority_name}")
        elif priority_number:
            logger.info(f"Spawned architect (PID {process.pid}) for PRIORITY {priority_number}")
        else:
            logger.info(f"Spawned architect (PID {process.pid}) for {task_type}")

        return {"error": None, "result": agent_info}

    def _spawn_code_developer(
        self,
        priority_number: int,
        worktree_path: Optional[str] = None,
        auto_approve: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Spawn code_developer instance for implementation.

        Args:
            priority_number: Priority number to implement
            worktree_path: Path to git worktree (for parallel execution)
            auto_approve: Auto-approve code_developer decisions

        Returns:
            Spawn result with PID and task info
        """
        # Build command
        cmd = ["poetry", "run", "code-developer", f"--priority={priority_number}"]

        if auto_approve:
            cmd.append("--auto-approve")

        # Spawn process (in worktree if specified)
        cwd = Path(worktree_path) if worktree_path else Path.cwd()

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )

        # Track agent in database
        task_id = f"impl-{priority_number}"
        spawned_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type, priority_number,
                    spawned_at, started_at, status, command, worktree_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process.pid,
                    "code_developer",
                    task_id,
                    "implementation",
                    priority_number,
                    spawned_at,
                    spawned_at,
                    "spawned",
                    " ".join(cmd),
                    str(worktree_path) if worktree_path else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": process.pid,
            "agent_type": "code_developer",
            "task_id": task_id,
            "priority_number": priority_number,
            "worktree_path": str(worktree_path) if worktree_path else None,
            "command": " ".join(cmd),
            "started_at": spawned_at,
            "status": "spawned",
        }

        logger.info(f"Spawned code_developer (PID {process.pid}) for PRIORITY {priority_number}")

        return {"error": None, "result": agent_info}

    def _spawn_code_developer_bug_fix(
        self,
        bug_number: int,
        bug_title: str,
        auto_approve: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Spawn code_developer instance for bug fix.

        Since code_developer doesn't have a --bug flag, we spawn it in interactive mode
        with a specific task context that focuses on the bug.

        Args:
            bug_number: Bug ticket number (e.g., 66 for BUG-066)
            bug_title: Bug title/description
            auto_approve: Auto-approve code_developer decisions

        Returns:
            Spawn result with PID and task info
        """
        # Build command - use auto-approve mode for autonomous bug fixing
        cmd = ["poetry", "run", "code-developer"]

        if auto_approve:
            cmd.append("--auto-approve")

        # Spawn process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd(),
        )

        # Track agent in database
        task_id = f"bug-{bug_number}"
        spawned_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Store bug info in metadata JSON
            import json

            metadata = json.dumps({"bug_number": bug_number, "bug_title": bug_title})

            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type,
                    spawned_at, started_at, status, command, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process.pid,
                    "code_developer",
                    task_id,
                    "bug_fix",
                    spawned_at,
                    spawned_at,
                    "spawned",
                    " ".join(cmd),
                    metadata,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": process.pid,
            "agent_type": "code_developer",
            "task_id": task_id,
            "task_type": "bug_fix",
            "bug_number": bug_number,
            "bug_title": bug_title,
            "command": " ".join(cmd),
            "started_at": spawned_at,
            "status": "spawned",
        }

        logger.info(f"Spawned code_developer (PID {process.pid}) for BUG-{bug_number:03d}: {bug_title}")

        return {"error": None, "result": agent_info}

    def _spawn_project_manager(
        self, task_type: str = "auto_planning", auto_approve: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """
        Spawn project_manager instance for planning/analysis.

        Args:
            task_type: Type of task (auto_planning, roadmap_health, etc.)
            auto_approve: Auto-approve project_manager decisions

        Returns:
            Spawn result with PID and task info
        """
        # Build command
        cmd = ["poetry", "run", "project-manager"]

        if task_type == "auto_planning":
            cmd.extend(["auto-plan"])
            if auto_approve:
                cmd.append("--auto-approve")
        elif task_type == "roadmap_health":
            cmd.extend(["status"])

        # Spawn process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd(),
        )

        # Track agent in database
        task_id = f"planning-{int(time.time())}"
        spawned_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type,
                    spawned_at, started_at, status, command
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process.pid,
                    "project_manager",
                    task_id,
                    task_type,
                    spawned_at,
                    spawned_at,
                    "spawned",
                    " ".join(cmd),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": process.pid,
            "agent_type": "project_manager",
            "task_id": task_id,
            "task_type": task_type,
            "command": " ".join(cmd),
            "started_at": spawned_at,
            "status": "spawned",
        }

        logger.info(f"Spawned project_manager (PID {process.pid}) for {task_type}")

        return {"error": None, "result": agent_info}

    def _spawn_code_reviewer(self, commit_sha: str = "HEAD", auto_approve: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Spawn code_reviewer instance for commit review.

        Args:
            commit_sha: Commit SHA to review (default: HEAD)
            auto_approve: Auto-approve code_reviewer decisions

        Returns:
            Spawn result with PID and task info
        """
        # Build command
        cmd = ["poetry", "run", "code-reviewer", "review", commit_sha]

        # Spawn process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd(),
        )

        # Track agent in database
        task_id = f"review-{commit_sha[:8]}"
        spawned_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Store commit info in metadata JSON
            import json

            metadata = json.dumps({"commit_sha": commit_sha})

            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type,
                    spawned_at, started_at, status, command, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process.pid,
                    "code_reviewer",
                    task_id,
                    "code_review",
                    spawned_at,
                    spawned_at,
                    "spawned",
                    " ".join(cmd),
                    metadata,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": process.pid,
            "agent_type": "code_reviewer",
            "task_id": task_id,
            "task_type": "code_review",
            "commit_sha": commit_sha,
            "command": " ".join(cmd),
            "started_at": spawned_at,
            "status": "spawned",
        }

        logger.info(f"Spawned code_reviewer (PID {process.pid}) for commit {commit_sha[:8]}")

        return {"error": None, "result": agent_info}

    def _check_status(self, pid: int, **kwargs) -> Dict[str, Any]:
        """
        Check agent status.

        Args:
            pid: Process ID

        Returns:
            Status info (running/completed/failed, exit code, duration)
        """
        # Query database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_lifecycle WHERE pid = ?", (pid,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Agent PID {pid} not found", "result": None}

            # Convert row to dict
            agent_info = dict(row)

            # Check if process still running
            try:
                os.kill(pid, 0)  # Signal 0 = check if process exists
                status = "running"
                exit_code = None
            except OSError:
                # Process finished
                status = (
                    agent_info["status"] if agent_info["status"] in ["completed", "failed", "killed"] else "completed"
                )
                exit_code = agent_info.get("exit_code", 0)

            # Calculate duration
            started_at = datetime.fromisoformat(agent_info["spawned_at"])
            duration = (datetime.now() - started_at).total_seconds()

            result = {
                "pid": pid,
                "status": status,
                "exit_code": exit_code,
                "duration": duration,
                "task_id": agent_info["task_id"],
                "agent_type": agent_info["agent_type"],
            }

            return {"error": None, "result": result}

        finally:
            conn.close()

    def _get_output(self, pid: int, last_n_lines: int = 50, **kwargs) -> Dict[str, Any]:
        """
        Get agent output (stdout/stderr).

        Args:
            pid: Process ID
            last_n_lines: Number of lines to return (from end)

        Returns:
            Output dict with stdout and stderr
        """
        # Query database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_lifecycle WHERE pid = ?", (pid,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Agent PID {pid} not found", "result": None}

            # For now, return placeholder (would need to capture output to file)
            result = {
                "pid": pid,
                "stdout": f"(Output capture not implemented yet for PID {pid})",
                "stderr": "",
                "lines": last_n_lines,
            }

            return {"error": None, "result": result}

        finally:
            conn.close()

    def _list_active_agents(self, include_completed: bool = False, **kwargs) -> Dict[str, Any]:
        """
        List all active agents with auto-cleanup of completed agents.

        Args:
            include_completed: If True, include completed agents (default: False)

        Returns:
            List of active agents with status
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Query active agents (spawned or running status)
            if include_completed:
                cursor.execute("SELECT * FROM agent_lifecycle ORDER BY spawned_at DESC")
            else:
                cursor.execute(
                    "SELECT * FROM agent_lifecycle WHERE status IN ('spawned', 'running') ORDER BY spawned_at DESC"
                )

            rows = cursor.fetchall()

            active_agents = []
            completed_pids = []

            for row in rows:
                agent_info = dict(row)
                pid = agent_info["pid"]

                # Check if still running
                try:
                    os.kill(pid, 0)
                    status = "running"
                except OSError:
                    status = "completed"
                    if agent_info["status"] in ["spawned", "running"]:
                        completed_pids.append(pid)

                # Calculate duration
                started_at = datetime.fromisoformat(agent_info["spawned_at"])
                duration = (datetime.now() - started_at).total_seconds()

                agent_data = {
                    "pid": pid,
                    "agent_type": agent_info["agent_type"],
                    "task_id": agent_info["task_id"],
                    "status": status,
                    "started_at": agent_info["spawned_at"],
                    "duration": duration,
                }

                # Only include running agents unless include_completed is True
                if status == "running" or include_completed:
                    active_agents.append(agent_data)

            # Auto-cleanup completed agents (update status in database)
            if completed_pids:
                completed_at = datetime.now().isoformat()
                placeholders = ",".join("?" * len(completed_pids))
                cursor.execute(
                    f"UPDATE agent_lifecycle SET status = 'completed', completed_at = ? WHERE pid IN ({placeholders})",
                    [completed_at] + completed_pids,
                )
                conn.commit()
                logger.info(f"Auto-cleaned up {len(completed_pids)} completed agents")

            result = {"active_agents": active_agents, "total": len(active_agents)}

            return {"error": None, "result": result}

        finally:
            conn.close()

    def _cleanup_agent(
        self, pid: int, remove_worktree: bool = False, worktree_path: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Clean up agent resources.

        Args:
            pid: Process ID
            remove_worktree: Whether to remove git worktree
            worktree_path: Path to worktree (if remove_worktree=True)

        Returns:
            Cleanup result
        """
        # Query database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_lifecycle WHERE pid = ?", (pid,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Agent PID {pid} not found", "result": None}

            agent_info = dict(row)

            # Update status to completed
            completed_at = datetime.now().isoformat()
            cursor.execute(
                "UPDATE agent_lifecycle SET status = 'completed', completed_at = ? WHERE pid = ?",
                (completed_at, pid),
            )
            conn.commit()

            # Remove worktree if requested
            if remove_worktree and worktree_path:
                try:
                    subprocess.run(
                        ["git", "worktree", "remove", "--force", worktree_path],
                        check=True,
                        capture_output=True,
                    )
                    logger.info(f"Removed worktree: {worktree_path}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to remove worktree: {e}")

            result = {
                "pid": pid,
                "agent_type": agent_info["agent_type"],
                "task_id": agent_info["task_id"],
            }

            return {"error": None, "result": result}

        finally:
            conn.close()

    def _detect_hung_agents(self, timeout_threshold: float = 1800.0, **kwargs) -> Dict[str, Any]:
        """
        Detect hung agents (running longer than threshold).

        Args:
            timeout_threshold: Timeout in seconds (default: 30 minutes)

        Returns:
            List of hung agents
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_lifecycle WHERE status IN ('spawned', 'running')")
            rows = cursor.fetchall()

            hung_agents = []

            for row in rows:
                agent_info = dict(row)
                pid = agent_info["pid"]

                # Check if still running
                try:
                    os.kill(pid, 0)
                except OSError:
                    continue  # Process finished, not hung

                # Calculate duration
                started_at = datetime.fromisoformat(agent_info["spawned_at"])
                duration = (datetime.now() - started_at).total_seconds()

                if duration > timeout_threshold:
                    hung_agents.append(
                        {
                            "pid": pid,
                            "agent_type": agent_info["agent_type"],
                            "task_id": agent_info["task_id"],
                            "duration": duration,
                            "timeout_threshold": timeout_threshold,
                            "recommended_action": "kill",
                        }
                    )

            result = {"hung_agents": hung_agents, "total": len(hung_agents)}

            return {"error": None, "result": result}

        finally:
            conn.close()

    def _kill_agent(self, pid: int, **kwargs) -> Dict[str, Any]:
        """
        Force kill an agent.

        Args:
            pid: Process ID

        Returns:
            Kill result
        """
        # Query database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_lifecycle WHERE pid = ?", (pid,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Agent PID {pid} not found", "result": None}

            agent_info = dict(row)

            # Try to kill
            try:
                os.kill(pid, 9)  # SIGKILL
                logger.warning(f"Killed agent PID {pid} ({agent_info['task_id']})")

                # Update status in database
                completed_at = datetime.now().isoformat()
                cursor.execute(
                    "UPDATE agent_lifecycle SET status = 'killed', exit_code = -9, completed_at = ? WHERE pid = ?",
                    (completed_at, pid),
                )
                conn.commit()

                result = {
                    "pid": pid,
                    "agent_type": agent_info["agent_type"],
                    "task_id": agent_info["task_id"],
                }

                return {"error": None, "result": result}

            except OSError as e:
                return {"error": f"Failed to kill PID {pid}: {e}", "result": None}

        finally:
            conn.close()
