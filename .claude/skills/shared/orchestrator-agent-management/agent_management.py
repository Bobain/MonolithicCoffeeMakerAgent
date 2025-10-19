"""Orchestrator Agent Management Skill.

Enables orchestrator to spawn, monitor, and manage architect and code_developer instances.

Author: architect + code_developer
Date: 2025-10-19
Related: Parallel execution, autonomous orchestration
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OrchestratorAgentManagementSkill:
    """
    Manages agent spawning, monitoring, and cleanup for orchestrator.

    Capabilities:
    - Spawn architect/code_developer instances
    - Monitor process status (running/completed/failed)
    - Track active agents (PIDs, tasks, start times)
    - Detect hung processes
    - Clean up resources after completion
    """

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize agent management skill.

        Args:
            state_file: Path to state file (default: data/orchestrator/agent_state.json)
        """
        self.state_file = state_file or Path("data/orchestrator/agent_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self.state = self._load_state()

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
            elif action == "spawn_project_manager":
                return self._spawn_project_manager(**kwargs)
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
        task_type: str = "create_spec",
        auto_approve: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Spawn architect instance for spec creation.

        Args:
            priority_number: Priority number to work on (optional for some task types)
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

        # Track agent
        if priority_number:
            task_id = f"spec-{priority_number}"
        else:
            task_id = f"{task_type}-{int(time.time())}"

        agent_info = {
            "pid": process.pid,
            "agent_type": "architect",
            "task_id": task_id,
            "task_type": task_type,
            "priority_number": priority_number,
            "command": " ".join(cmd),
            "started_at": datetime.now().isoformat(),
            "status": "running",
        }

        self.state["active_agents"][str(process.pid)] = agent_info
        self._save_state()

        if priority_number:
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

        # Track agent
        task_id = f"impl-{priority_number}"
        agent_info = {
            "pid": process.pid,
            "agent_type": "code_developer",
            "task_id": task_id,
            "priority_number": priority_number,
            "worktree_path": str(worktree_path) if worktree_path else None,
            "command": " ".join(cmd),
            "started_at": datetime.now().isoformat(),
            "status": "running",
        }

        self.state["active_agents"][str(process.pid)] = agent_info
        self._save_state()

        logger.info(f"Spawned code_developer (PID {process.pid}) for PRIORITY {priority_number}")

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
        elif task_type == "roadmap_health":
            cmd.extend(["roadmap-health"])

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

        # Track agent
        task_id = f"planning-{int(time.time())}"
        agent_info = {
            "pid": process.pid,
            "agent_type": "project_manager",
            "task_id": task_id,
            "task_type": task_type,
            "command": " ".join(cmd),
            "started_at": datetime.now().isoformat(),
            "status": "running",
        }

        self.state["active_agents"][str(process.pid)] = agent_info
        self._save_state()

        logger.info(f"Spawned project_manager (PID {process.pid}) for {task_type}")

        return {"error": None, "result": agent_info}

    def _check_status(self, pid: int, **kwargs) -> Dict[str, Any]:
        """
        Check agent status.

        Args:
            pid: Process ID

        Returns:
            Status info (running/completed/failed, exit code, duration)
        """
        pid_str = str(pid)

        if pid_str not in self.state["active_agents"]:
            return {"error": f"Agent PID {pid} not found", "result": None}

        agent_info = self.state["active_agents"][pid_str]

        # Check if process still running
        try:
            os.kill(pid, 0)  # Signal 0 = check if process exists
            status = "running"
            exit_code = None
        except OSError:
            # Process finished
            status = "completed"  # Will check exit code below
            exit_code = agent_info.get("exit_code", 0)

        # Calculate duration
        started_at = datetime.fromisoformat(agent_info["started_at"])
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

    def _get_output(self, pid: int, last_n_lines: int = 50, **kwargs) -> Dict[str, Any]:
        """
        Get agent output (stdout/stderr).

        Args:
            pid: Process ID
            last_n_lines: Number of lines to return (from end)

        Returns:
            Output dict with stdout and stderr
        """
        pid_str = str(pid)

        if pid_str not in self.state["active_agents"]:
            return {"error": f"Agent PID {pid} not found", "result": None}

        # For now, return placeholder (would need to capture output to file)
        result = {
            "pid": pid,
            "stdout": f"(Output capture not implemented yet for PID {pid})",
            "stderr": "",
            "lines": last_n_lines,
        }

        return {"error": None, "result": result}

    def _list_active_agents(self, **kwargs) -> Dict[str, Any]:
        """
        List all active agents.

        Returns:
            List of active agents with status
        """
        active_agents = []

        for pid_str, agent_info in list(self.state["active_agents"].items()):
            pid = int(pid_str)

            # Check if still running
            try:
                os.kill(pid, 0)
                status = "running"
            except OSError:
                status = "completed"

            # Calculate duration
            started_at = datetime.fromisoformat(agent_info["started_at"])
            duration = (datetime.now() - started_at).total_seconds()

            active_agents.append(
                {
                    "pid": pid,
                    "agent_type": agent_info["agent_type"],
                    "task_id": agent_info["task_id"],
                    "status": status,
                    "started_at": agent_info["started_at"],
                    "duration": duration,
                }
            )

        result = {"active_agents": active_agents, "total": len(active_agents)}

        return {"error": None, "result": result}

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
        pid_str = str(pid)

        if pid_str not in self.state["active_agents"]:
            return {"error": f"Agent PID {pid} not found", "result": None}

        # Remove from state
        agent_info = self.state["active_agents"].pop(pid_str)
        self._save_state()

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

        result = {"pid": pid, "agent_type": agent_info["agent_type"], "task_id": agent_info["task_id"]}

        return {"error": None, "result": result}

    def _detect_hung_agents(self, timeout_threshold: float = 1800.0, **kwargs) -> Dict[str, Any]:
        """
        Detect hung agents (running longer than threshold).

        Args:
            timeout_threshold: Timeout in seconds (default: 30 minutes)

        Returns:
            List of hung agents
        """
        hung_agents = []

        for pid_str, agent_info in self.state["active_agents"].items():
            pid = int(pid_str)

            # Check if still running
            try:
                os.kill(pid, 0)
            except OSError:
                continue  # Process finished, not hung

            # Calculate duration
            started_at = datetime.fromisoformat(agent_info["started_at"])
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

    def _kill_agent(self, pid: int, **kwargs) -> Dict[str, Any]:
        """
        Force kill an agent.

        Args:
            pid: Process ID

        Returns:
            Kill result
        """
        pid_str = str(pid)

        if pid_str not in self.state["active_agents"]:
            return {"error": f"Agent PID {pid} not found", "result": None}

        agent_info = self.state["active_agents"][pid_str]

        # Try to kill
        try:
            os.kill(pid, 9)  # SIGKILL
            logger.warning(f"Killed agent PID {pid} ({agent_info['task_id']})")

            # Mark as failed
            agent_info["status"] = "killed"
            agent_info["exit_code"] = -9
            self._save_state()

            result = {"pid": pid, "agent_type": agent_info["agent_type"], "task_id": agent_info["task_id"]}

            return {"error": None, "result": result}

        except OSError as e:
            return {"error": f"Failed to kill PID {pid}: {e}", "result": None}

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}, using empty state")

        return {"active_agents": {}, "completed_agents": []}

    def _save_state(self):
        """Save state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
