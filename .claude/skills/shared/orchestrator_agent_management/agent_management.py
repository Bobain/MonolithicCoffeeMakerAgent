"""Orchestrator Agent Management Skill.

Enables orchestrator to spawn, monitor, and manage architect and code_developer instances
AS CLAUDE CODE SESSIONS (not Python processes).

Architecture:
    All agents are spawned as Claude Code sessions using ClaudeAgentInvoker.
    They are NOT Python processes - they ARE Claude sessions with full tool access.

CFR-014 Compliant: Uses SQLite database instead of JSON files.

Author: architect + code_developer
Date: 2025-10-26 (Updated to use Claude Code sessions)
Related: Parallel execution, autonomous orchestration, CFR-014 compliance, Claude-as-agents architecture
"""

import json
import logging
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Import Claude agent invoker for spawning Claude Code sessions
try:
    from coffee_maker.claude_agent_invoker import get_invoker

    INVOKER_AVAILABLE = True
except ImportError:
    logger.warning("ClaudeAgentInvoker not available - falling back to legacy Python agents")
    INVOKER_AVAILABLE = False


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

        # Store process handles for exit code retrieval
        # Maps PID -> subprocess.Popen object
        self._process_handles: Dict[int, subprocess.Popen] = {}

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
            elif action == "register_agent":
                return self._register_agent(**kwargs)
            elif action == "update_agent_status":
                return self._update_agent_status(**kwargs)
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
        Spawn architect instance AS A CLAUDE CODE SESSION (not a Python process).

        Args:
            priority_number: Priority number to work on (optional for some task types)
            priority_name: Priority name (e.g., "US-059" or "PRIORITY 59")
            task_type: Type of task (create_spec, refactoring_analysis, etc.)
            auto_approve: Auto-approve architect decisions

        Returns:
            Spawn result with invocation_id and task info
        """
        if not INVOKER_AVAILABLE:
            raise RuntimeError("ClaudeAgentInvoker not available - cannot spawn architect")

        # Build prompt for Claude Code session
        if task_type == "create_spec":
            if priority_number is None:
                raise ValueError("priority_number required for create_spec task type")

            prompt = f"""Create technical specification for priority {priority_number}.

## Task

1. Use Read tool to read docs/roadmap/ROADMAP.md and find priority {priority_number}
2. Use Read tool to understand existing architecture (docs/architecture/)
3. Design the solution
4. Use Write tool to create: docs/architecture/specs/SPEC-XXX-{priority_number}.md
5. Include: problem statement, solution, implementation steps, testing, DoD
6. Report "COMPLETE: Spec created for priority {priority_number}"

Start now. When done, exit."""

        elif task_type == "refactoring_analysis":
            prompt = """Analyze codebase for refactoring opportunities.

## Task

1. Use Read/Grep tools to analyze code quality
2. Identify technical debt and improvement opportunities
3. Use Write tool to create refactoring analysis report
4. Report "COMPLETE: Refactoring analysis complete"

Start now. When done, exit."""

        else:
            prompt = f"""Execute {task_type} task as architect.

Use Read, Write, Edit, Bash tools as needed.
Report "COMPLETE: {task_type} complete" when done.

Start now. When done, exit."""

        # Generate task_id
        if priority_number:
            task_id = f"spec-{priority_number}"
        else:
            task_id = f"{task_type}-{int(time.time())}"

        spawned_at = datetime.now().isoformat()

        # Spawn Claude Code session in background thread
        invoker = get_invoker()

        def run_session():
            """Run Claude session with streaming and track in database."""
            try:
                # Invoke agent with streaming (allows real-time monitoring)
                success = False
                error_msg = None

                for msg in invoker.invoke_agent_streaming("architect", prompt, timeout=1800):
                    # Log streaming messages for observability
                    if msg.message_type == "message":
                        logger.debug(f"[architect/{task_id}] 💬 {msg.content[:100]}")
                    elif msg.message_type == "tool_use":
                        tool_name = msg.metadata.get("name", "unknown")
                        logger.info(f"[architect/{task_id}] 🔧 Using tool: {tool_name}")
                    elif msg.message_type == "result":
                        # Final result received
                        success = msg.metadata.get("stop_reason") != "error"
                        if not success:
                            error_msg = msg.metadata.get("error", "Unknown error")
                        logger.info(f"[architect/{task_id}] 🏁 Session complete (success={success})")

                # Update database with result
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = ?, completed_at = ?, exit_code = ?
                        WHERE task_id = ?
                        """,
                        (
                            "completed" if success else "failed",
                            datetime.now().isoformat(),
                            0 if success else 1,
                            task_id,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()

                if success:
                    logger.info(f"✅ Architect session completed for {task_id}")
                else:
                    logger.error(f"❌ Architect session failed for {task_id}: {error_msg}")

            except Exception as e:
                logger.error(f"❌ Architect session crashed for {task_id}: {e}", exc_info=True)
                # Mark as failed in database
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = 'failed', completed_at = ?, exit_code = 1
                        WHERE task_id = ?
                        """,
                        (datetime.now().isoformat(), task_id),
                    )
                    conn.commit()
                finally:
                    conn.close()

        # Start session in background thread
        thread = Thread(target=run_session, daemon=True)
        thread.start()

        # Track in database immediately (use thread.ident as pseudo-PID)
        pseudo_pid = thread.ident or 0

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
                    pseudo_pid,
                    "architect",
                    task_id,
                    task_type,
                    priority_number,
                    spawned_at,
                    spawned_at,
                    "running",
                    f"claude --agent architect (session)",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": pseudo_pid,  # Thread ID as pseudo-PID
            "agent_type": "architect",
            "task_id": task_id,
            "task_type": task_type,
            "priority_number": priority_number,
            "command": f"claude --agent architect",
            "started_at": spawned_at,
            "status": "running",
        }

        if priority_name:
            logger.info(f"🚀 Spawned architect Claude session for {priority_name}")
        elif priority_number:
            logger.info(f"🚀 Spawned architect Claude session for PRIORITY {priority_number}")
        else:
            logger.info(f"🚀 Spawned architect Claude session for {task_type}")

        return {"error": None, "result": agent_info}

    def _spawn_code_developer(
        self,
        priority_number: int,
        worktree_path: Optional[str] = None,
        auto_approve: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Spawn code_developer instance AS A CLAUDE CODE SESSION (not a Python process).

        Args:
            priority_number: Priority number to implement
            worktree_path: Path to git worktree (for parallel execution)
            auto_approve: Auto-approve code_developer decisions

        Returns:
            Spawn result with invocation_id and task info
        """
        if not INVOKER_AVAILABLE:
            raise RuntimeError("ClaudeAgentInvoker not available - cannot spawn code_developer")

        # Build prompt for Claude Code session
        prompt = f"""Implement priority {priority_number}.

## Task

1. Use Read tool to read docs/roadmap/ROADMAP.md and find priority {priority_number}
2. Use Read tool to find and read the technical spec (docs/architecture/specs/SPEC-*-{priority_number}.md)
3. Use Read tool to understand existing code
4. Use Write/Edit tools to implement the feature following the spec
5. Use Bash tool to run: pytest
6. If tests pass: Use Bash to commit: git add . && git commit -m "feat: Implement priority {priority_number}"
7. Report "COMPLETE: Priority {priority_number} implemented"

Start now. When done, exit."""

        # Generate task_id
        task_id = f"impl-{priority_number}"
        spawned_at = datetime.now().isoformat()

        # Spawn Claude Code session in background thread
        invoker = get_invoker()

        # Determine working directory
        Path(worktree_path) if worktree_path else Path.cwd()

        def run_session():
            """Run Claude session with streaming and track in database."""
            try:
                # Change to worktree directory if needed
                original_cwd = os.getcwd()
                if worktree_path:
                    os.chdir(worktree_path)

                try:
                    # Invoke agent with streaming (allows real-time monitoring)
                    success = False
                    error_msg = None

                    for msg in invoker.invoke_agent_streaming("code-developer", prompt, timeout=3600):
                        # Log streaming messages for observability
                        if msg.message_type == "message":
                            logger.debug(f"[code-developer/{task_id}] 💬 {msg.content[:100]}")
                        elif msg.message_type == "tool_use":
                            tool_name = msg.metadata.get("name", "unknown")
                            logger.info(f"[code-developer/{task_id}] 🔧 Using tool: {tool_name}")
                        elif msg.message_type == "result":
                            # Final result received
                            success = msg.metadata.get("stop_reason") != "error"
                            if not success:
                                error_msg = msg.metadata.get("error", "Unknown error")
                            logger.info(f"[code-developer/{task_id}] 🏁 Session complete (success={success})")

                    # Update database with result
                    conn = self._get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            UPDATE agent_lifecycle
                            SET status = ?, completed_at = ?, exit_code = ?
                            WHERE task_id = ?
                            """,
                            (
                                "completed" if success else "failed",
                                datetime.now().isoformat(),
                                0 if success else 1,
                                task_id,
                            ),
                        )
                        conn.commit()
                    finally:
                        conn.close()

                    if success:
                        logger.info(f"✅ Code developer session completed for {task_id}")
                    else:
                        logger.error(f"❌ Code developer session failed for {task_id}: {error_msg}")

                finally:
                    # Restore original directory
                    os.chdir(original_cwd)

            except Exception as e:
                logger.error(f"❌ Code developer session crashed for {task_id}: {e}", exc_info=True)
                # Mark as failed in database
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = 'failed', completed_at = ?, exit_code = 1
                        WHERE task_id = ?
                        """,
                        (datetime.now().isoformat(), task_id),
                    )
                    conn.commit()
                finally:
                    conn.close()

        # Start session in background thread
        thread = Thread(target=run_session, daemon=True)
        thread.start()

        # Track in database immediately (use thread.ident as pseudo-PID)
        pseudo_pid = thread.ident or 0

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
                    pseudo_pid,
                    "code_developer",
                    task_id,
                    "implementation",
                    priority_number,
                    spawned_at,
                    spawned_at,
                    "running",
                    f"claude --agent code-developer (session)",
                    str(worktree_path) if worktree_path else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": pseudo_pid,  # Thread ID as pseudo-PID
            "agent_type": "code_developer",
            "task_id": task_id,
            "priority_number": priority_number,
            "worktree_path": str(worktree_path) if worktree_path else None,
            "command": f"claude --agent code-developer",
            "started_at": spawned_at,
            "status": "running",
        }

        logger.info(f"🚀 Spawned code_developer Claude session for PRIORITY {priority_number}")

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
        Spawn project_manager instance AS A CLAUDE CODE SESSION (not a Python process).

        Args:
            task_type: Type of task (auto_planning, roadmap_health, etc.)
            auto_approve: Auto-approve project_manager decisions

        Returns:
            Spawn result with invocation_id and task info
        """
        if not INVOKER_AVAILABLE:
            raise RuntimeError("ClaudeAgentInvoker not available - cannot spawn project_manager")

        # Build prompt for Claude Code session
        if task_type == "auto_planning":
            prompt = """Analyze roadmap and create strategic plan.

## Task

1. Use Read tool to read docs/roadmap/ROADMAP.md
2. Analyze current priorities and progress
3. Use Bash tool with gh to check GitHub status (PRs, issues)
4. Create planning recommendations
5. Use Edit tool to update roadmap if needed
6. Report "COMPLETE: Planning complete"

Start now. When done, exit."""

        elif task_type == "roadmap_health":
            prompt = """Check roadmap health and report status.

## Task

1. Use Read tool to read docs/roadmap/ROADMAP.md
2. Analyze priorities (planned, in-progress, completed)
3. Identify blockers or issues
4. Report health metrics and recommendations
5. Report "COMPLETE: Health check complete"

Start now. When done, exit."""

        else:
            prompt = f"""Execute {task_type} task as project_manager.

Use Read, Write, Edit, Bash tools as needed.
Report "COMPLETE: {task_type} complete" when done.

Start now. When done, exit."""

        # Generate task_id
        task_id = f"planning-{int(time.time())}"
        spawned_at = datetime.now().isoformat()

        # Spawn Claude Code session in background thread
        invoker = get_invoker()

        def run_session():
            """Run Claude session and track in database."""
            try:
                # Invoke agent (blocking call)
                result = invoker.invoke_agent("project-manager", prompt, timeout=1800)

                # Get invocation_id from result
                result.metadata.get("invocation_id")

                # Update database with result
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = ?, completed_at = ?, exit_code = ?
                        WHERE task_id = ?
                        """,
                        (
                            "completed" if result.success else "failed",
                            datetime.now().isoformat(),
                            0 if result.success else 1,
                            task_id,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()

                if result.success:
                    logger.info(f"✅ Project manager session completed for {task_id}")
                else:
                    logger.error(f"❌ Project manager session failed for {task_id}: {result.error}")

            except Exception as e:
                logger.error(f"❌ Project manager session crashed for {task_id}: {e}", exc_info=True)
                # Mark as failed in database
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = 'failed', completed_at = ?, exit_code = 1
                        WHERE task_id = ?
                        """,
                        (datetime.now().isoformat(), task_id),
                    )
                    conn.commit()
                finally:
                    conn.close()

        # Start session in background thread
        thread = Thread(target=run_session, daemon=True)
        thread.start()

        # Track in database immediately (use thread.ident as pseudo-PID)
        pseudo_pid = thread.ident or 0

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
                    pseudo_pid,
                    "project_manager",
                    task_id,
                    task_type,
                    spawned_at,
                    spawned_at,
                    "running",
                    f"claude --agent project-manager (session)",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": pseudo_pid,  # Thread ID as pseudo-PID
            "agent_type": "project_manager",
            "task_id": task_id,
            "task_type": task_type,
            "command": f"claude --agent project-manager",
            "started_at": spawned_at,
            "status": "running",
        }

        logger.info(f"🚀 Spawned project_manager Claude session for {task_type}")

        return {"error": None, "result": agent_info}

    def _spawn_code_reviewer(self, commit_sha: str = "HEAD", auto_approve: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Spawn code_reviewer instance AS A CLAUDE CODE SESSION (not a Python process).

        Args:
            commit_sha: Commit SHA to review (default: HEAD)
            auto_approve: Auto-approve code_reviewer decisions

        Returns:
            Spawn result with invocation_id and task info
        """
        if not INVOKER_AVAILABLE:
            raise RuntimeError("ClaudeAgentInvoker not available - cannot spawn code_reviewer")

        # Build prompt for Claude Code session
        prompt = f"""Review commit {commit_sha}.

## Task

1. Use Bash tool to get commit details: git show {commit_sha}
2. Analyze code changes for:
   - Code quality issues
   - Style guide compliance
   - Potential bugs
   - Security concerns
   - Test coverage
3. Use Write tool to create review report (if needed)
4. Report "COMPLETE: Review complete for {commit_sha}"

Start now. When done, exit."""

        # Generate task_id
        task_id = f"review-{commit_sha[:8]}"
        spawned_at = datetime.now().isoformat()

        # Spawn Claude Code session in background thread
        invoker = get_invoker()

        def run_session():
            """Run Claude session and track in database."""
            try:
                # Invoke agent (blocking call)
                result = invoker.invoke_agent("code-reviewer", prompt, timeout=900)

                # Get invocation_id from result
                result.metadata.get("invocation_id")

                # Update database with result
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = ?, completed_at = ?, exit_code = ?
                        WHERE task_id = ?
                        """,
                        (
                            "completed" if result.success else "failed",
                            datetime.now().isoformat(),
                            0 if result.success else 1,
                            task_id,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()

                if result.success:
                    logger.info(f"✅ Code reviewer session completed for {task_id}")
                else:
                    logger.error(f"❌ Code reviewer session failed for {task_id}: {result.error}")

            except Exception as e:
                logger.error(f"❌ Code reviewer session crashed for {task_id}: {e}", exc_info=True)
                # Mark as failed in database
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET status = 'failed', completed_at = ?, exit_code = 1
                        WHERE task_id = ?
                        """,
                        (datetime.now().isoformat(), task_id),
                    )
                    conn.commit()
                finally:
                    conn.close()

        # Start session in background thread
        thread = Thread(target=run_session, daemon=True)
        thread.start()

        # Track in database immediately (use thread.ident as pseudo-PID)
        pseudo_pid = thread.ident or 0

        # Store commit info in metadata JSON
        metadata = json.dumps({"commit_sha": commit_sha})

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type,
                    spawned_at, started_at, status, command, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pseudo_pid,
                    "code_reviewer",
                    task_id,
                    "code_review",
                    spawned_at,
                    spawned_at,
                    "running",
                    f"claude --agent code-reviewer (session)",
                    metadata,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        agent_info = {
            "pid": pseudo_pid,  # Thread ID as pseudo-PID
            "agent_type": "code_reviewer",
            "task_id": task_id,
            "task_type": "code_review",
            "commit_sha": commit_sha,
            "command": f"claude --agent code-reviewer",
            "started_at": spawned_at,
            "status": "running",
        }

        logger.info(f"🚀 Spawned code_reviewer Claude session for commit {commit_sha[:8]}")

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

            # Check if we have process handle
            process = self._process_handles.get(pid)
            exit_code = None
            stdout_output = None
            stderr_output = None

            if process:
                # Poll the process to get exit code
                exit_code = process.poll()

                if exit_code is not None:
                    # Process finished - read output
                    try:
                        stdout_output, stderr_output = process.communicate(timeout=1)
                    except subprocess.TimeoutExpired:
                        # If somehow it's still outputting, kill it
                        process.kill()
                        stdout_output, stderr_output = process.communicate()

                    # Update database with exit code and output
                    cursor.execute(
                        """
                        UPDATE agent_lifecycle
                        SET exit_code = ?, stdout_output = ?, stderr_output = ?,
                            status = ?, completed_at = ?
                        WHERE pid = ?
                        """,
                        (
                            exit_code,
                            stdout_output,
                            stderr_output,
                            "completed" if exit_code == 0 else "failed",
                            datetime.now().isoformat(),
                            pid,
                        ),
                    )
                    conn.commit()

                    # Remove from process handles
                    del self._process_handles[pid]

                    # Log failure details
                    if exit_code != 0:
                        logger.error(f"Agent {agent_info['agent_type']} (PID {pid}) failed with exit code {exit_code}")
                        if stderr_output:
                            logger.error(f"Error output: {stderr_output[:500]}")  # First 500 chars

                    status = "completed" if exit_code == 0 else "failed"
                else:
                    # Still running
                    status = "running"
            else:
                # No process handle - check if process exists via OS
                try:
                    os.kill(pid, 0)  # Signal 0 = check if process exists
                    status = "running"
                except OSError:
                    # Process finished but we don't have handle
                    status = agent_info.get("status", "completed")
                    exit_code = agent_info.get("exit_code")

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

            # Include output if available
            if stdout_output:
                result["stdout"] = stdout_output
            if stderr_output:
                result["stderr"] = stderr_output

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
            cursor.execute("SELECT stdout_output, stderr_output FROM agent_lifecycle WHERE pid = ?", (pid,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Agent PID {pid} not found", "result": None}

            stdout = row["stdout_output"] or ""
            stderr = row["stderr_output"] or ""

            # Limit to last N lines if requested
            if last_n_lines and stdout:
                stdout_lines = stdout.splitlines()
                if len(stdout_lines) > last_n_lines:
                    stdout = "\n".join(stdout_lines[-last_n_lines:])

            if last_n_lines and stderr:
                stderr_lines = stderr.splitlines()
                if len(stderr_lines) > last_n_lines:
                    stderr = "\n".join(stderr_lines[-last_n_lines:])

            result = {
                "pid": pid,
                "stdout": stdout,
                "stderr": stderr,
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

    def _register_agent(
        self,
        pid: int,
        agent_type: str,
        task_id: str,
        task_type: str,
        priority_number: Optional[int] = None,
        command: Optional[str] = None,
        worktree_path: Optional[str] = None,
        worktree_branch: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Register an already-spawned agent in the database.

        This is used by ParallelExecutionCoordinator which spawns processes directly.

        Args:
            pid: Process ID
            agent_type: Type of agent (code_developer, architect, etc.)
            task_id: Task identifier (e.g., impl-24, spec-031)
            task_type: Type of task (implementation, create_spec, etc.)
            priority_number: Priority number (optional)
            command: Command used to spawn agent (optional)
            worktree_path: Path to git worktree (optional)
            worktree_branch: Git branch name (optional)

        Returns:
            Registration result
        """
        spawned_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_lifecycle (
                    pid, agent_type, task_id, task_type, priority_number,
                    spawned_at, started_at, status, command, worktree_path, worktree_branch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    agent_type,
                    task_id,
                    task_type,
                    priority_number,
                    spawned_at,
                    spawned_at,
                    "spawned",
                    command,
                    worktree_path,
                    worktree_branch,
                ),
            )
            conn.commit()

            agent_info = {
                "pid": pid,
                "agent_type": agent_type,
                "task_id": task_id,
                "task_type": task_type,
                "priority_number": priority_number,
                "started_at": spawned_at,
                "status": "spawned",
            }

            logger.info(f"Registered {agent_type} (PID {pid}) for task {task_id}")

            return {"error": None, "result": agent_info}

        finally:
            conn.close()

    def _update_agent_status(
        self, task_id: str, status: str, exit_code: Optional[int] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Update agent status in the database.

        Args:
            task_id: Task identifier (e.g., impl-24-parallel, spec-031)
            status: New status (completed, failed, running, etc.)
            exit_code: Process exit code (optional)

        Returns:
            Update result
        """
        completed_at = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Build update query based on provided parameters
            update_fields = ["status = ?"]
            update_values = [status]

            if status in ["completed", "failed", "killed"]:
                update_fields.append("completed_at = ?")
                update_values.append(completed_at)

            if exit_code is not None:
                update_fields.append("exit_code = ?")
                update_values.append(exit_code)

            update_values.append(task_id)

            cursor.execute(
                f"UPDATE agent_lifecycle SET {', '.join(update_fields)} WHERE task_id = ?",
                update_values,
            )
            conn.commit()

            # Verify update
            cursor.execute("SELECT * FROM agent_lifecycle WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()

            if not row:
                return {"error": f"Task {task_id} not found", "result": None}

            agent_info = dict(row)

            logger.info(f"Updated agent {agent_info['agent_type']} (task: {task_id}) status to {status}")

            return {"error": None, "result": agent_info}

        finally:
            conn.close()
