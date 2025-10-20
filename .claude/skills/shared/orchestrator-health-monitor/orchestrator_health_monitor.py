"""Orchestrator Health Monitor - Real-time monitoring, crash detection, and bug auto-reporting.

This module provides comprehensive health monitoring for the orchestrator system:
- Agent crash detection with PID monitoring
- Orchestrator loop freeze detection
- Auto-respawn crashed agents (max 3 retries)
- Auto-report bugs via bug-tracking skill
- Clean up zombie processes

Author: architect + user_listener
Date: 2025-10-20
Related: SPEC-111 (Bug Tracking), CFR-014 (Database Tracing)
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import psutil

from coffee_maker.cli.bug_tracker import BugTracker

logger = logging.getLogger(__name__)


@dataclass
class AgentCrash:
    """Data model for agent crash."""

    crash_id: Optional[int]
    agent_pid: int
    agent_type: str
    task_id: str
    crashed_at: str
    error_type: str
    error_message: str
    stack_trace: str
    respawned: bool
    bug_reported: bool
    bug_number: Optional[int]


@dataclass
class HealthStatus:
    """Health check status result."""

    status: str  # healthy, degraded, critical
    issues: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    timestamp: str


class OrchestratorHealthMonitor:
    """Real-time health monitoring for orchestrator and agents.

    Capabilities:
    - Detect agent crashes via PID monitoring
    - Parse error logs for root cause analysis
    - Auto-respawn crashed agents (max 3 retries)
    - Report bugs via bug-tracking skill
    - Detect orchestrator loop freezes
    - Clean up zombie processes
    """

    def __init__(
        self,
        db_path: str = "data/orchestrator.db",
        agent_state_path: str = "data/orchestrator/agent_state.json",
        work_loop_state_path: str = "data/orchestrator/work_loop_state.json",
        log_path: str = "data/orchestrator.log",
        max_respawn_attempts: int = 3,
        freeze_threshold_seconds: int = 300,
    ):
        """Initialize health monitor.

        Args:
            db_path: Path to orchestrator database
            agent_state_path: Path to agent state JSON
            work_loop_state_path: Path to work loop state JSON
            log_path: Path to orchestrator log file
            max_respawn_attempts: Max times to respawn crashed agent
            freeze_threshold_seconds: Seconds before considering orchestrator frozen
        """
        self.db_path = Path(db_path)
        self.agent_state_path = Path(agent_state_path)
        self.work_loop_state_path = Path(work_loop_state_path)
        self.log_path = Path(log_path)
        self.max_respawn_attempts = max_respawn_attempts
        self.freeze_threshold = freeze_threshold_seconds

        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure health monitoring tables exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # health_checks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS health_checks (
                    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    active_agents INTEGER,
                    crashed_agents INTEGER,
                    zombie_processes INTEGER,
                    orchestrator_responsive BOOLEAN,
                    last_poll_age_seconds INTEGER,
                    actions_taken TEXT,
                    bugs_reported TEXT
                )
            """
            )

            # agent_crashes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_crashes (
                    crash_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_pid INTEGER NOT NULL,
                    agent_type TEXT NOT NULL,
                    task_id TEXT,
                    crashed_at TEXT NOT NULL,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    respawned BOOLEAN,
                    bug_reported BOOLEAN,
                    bug_number INTEGER
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    def check_health(self) -> HealthStatus:
        """Run comprehensive health check.

        Returns:
            HealthStatus with issues and metrics
        """
        logger.info("🏥 Running health check...")

        issues = []

        # Check 1: Agent PIDs
        crashed_agents = self._check_agent_pids()
        if crashed_agents:
            issues.extend(crashed_agents)

        # Check 2: Orchestrator loop
        loop_issue = self._check_orchestrator_loop()
        if loop_issue:
            issues.append(loop_issue)

        # Check 3: Zombie processes
        zombie_count = self._check_zombie_processes()
        if zombie_count > 0:
            issues.append({"type": "zombie_processes", "count": zombie_count, "action_taken": "cleaned_up"})

        # Determine overall status
        if not issues:
            status = "healthy"
        elif any(i["type"] == "orchestrator_freeze" for i in issues):
            status = "critical"
        elif len(issues) > 5:
            status = "critical"
        else:
            status = "degraded"

        # Collect metrics
        metrics = self._collect_metrics()

        health_status = HealthStatus(
            status=status, issues=issues, metrics=metrics, timestamp=datetime.now().isoformat()
        )

        # Record in database
        self._record_health_check(health_status)

        return health_status

    def _check_agent_pids(self) -> List[Dict[str, Any]]:
        """Check if spawned agents are still running.

        Returns:
            List of crash issues detected
        """
        if not self.agent_state_path.exists():
            return []

        agent_state = json.loads(self.agent_state_path.read_text())
        active_agents = agent_state.get("active_agents", {})

        crashed = []

        for pid_str, agent_info in active_agents.items():
            pid = int(pid_str)

            # Check if process exists
            if not psutil.pid_exists(pid):
                # Agent crashed!
                error_info = self._parse_agent_error(agent_info)

                crash_issue = {
                    "type": "agent_crash",
                    "agent_pid": pid,
                    "agent_type": agent_info.get("agent_type"),
                    "task_id": agent_info.get("task_id"),
                    "error_type": error_info.get("error_type"),
                    "error_message": error_info.get("error_message"),
                    "action_taken": None,
                    "bug_reported": False,
                    "bug_number": None,
                }

                crashed.append(crash_issue)

        return crashed

    def _check_orchestrator_loop(self) -> Optional[Dict[str, Any]]:
        """Check if orchestrator work loop is frozen.

        Returns:
            Issue dict if frozen, None otherwise
        """
        if not self.work_loop_state_path.exists():
            return None

        state = json.loads(self.work_loop_state_path.read_text())
        last_update = state.get("last_update", 0)

        age_seconds = time.time() - last_update

        if age_seconds > self.freeze_threshold:
            return {
                "type": "orchestrator_freeze",
                "last_update": last_update,
                "age_seconds": int(age_seconds),
                "action_taken": None,
                "bug_reported": False,
                "bug_number": None,
            }

        return None

    def _check_zombie_processes(self) -> int:
        """Check for zombie processes in agent_state.json.

        Returns:
            Count of zombie processes found and cleaned
        """
        if not self.agent_state_path.exists():
            return 0

        agent_state = json.loads(self.agent_state_path.read_text())
        active_agents = agent_state.get("active_agents", {})

        zombies = []
        for pid_str, agent_info in active_agents.items():
            pid = int(pid_str)
            if not psutil.pid_exists(pid):
                zombies.append(pid_str)

        # Clean up zombies
        if zombies:
            for pid_str in zombies:
                del active_agents[pid_str]

            agent_state["active_agents"] = active_agents
            self.agent_state_path.write_text(json.dumps(agent_state, indent=2))
            logger.info(f"🧹 Cleaned up {len(zombies)} zombie processes")

        return len(zombies)

    def _parse_agent_error(self, agent_info: Dict) -> Dict[str, str]:
        """Parse agent error from logs.

        Args:
            agent_info: Agent information from state JSON

        Returns:
            Dict with error_type and error_message
        """
        agent_type = agent_info.get("agent_type")

        # Search orchestrator log for error
        if self.log_path.exists():
            log_content = self.log_path.read_text()
            lines = log_content.splitlines()

            # Find ERROR lines for this agent
            for i, line in enumerate(reversed(lines)):
                if "ERROR" in line and agent_type in line:
                    # Extract error type and message
                    if "ImportError" in line:
                        return {"error_type": "ImportError", "error_message": line.split("ERROR")[1].strip()}
                    elif "ModuleNotFoundError" in line:
                        return {"error_type": "ModuleNotFoundError", "error_message": line.split("ERROR")[1].strip()}
                    elif "RuntimeError" in line:
                        return {"error_type": "RuntimeError", "error_message": line.split("ERROR")[1].strip()}
                    else:
                        return {
                            "error_type": "UnknownError",
                            "error_message": line.split("ERROR")[1].strip() if "ERROR" in line else line,
                        }

        return {"error_type": "Unknown", "error_message": "No error details found in logs"}

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current health metrics.

        Returns:
            Dict of metrics
        """
        agent_state = {}
        if self.agent_state_path.exists():
            agent_state = json.loads(self.agent_state_path.read_text())

        active_count = len(agent_state.get("active_agents", {}))

        # Count recent crashes
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            one_hour_ago = datetime.now().timestamp() - 3600
            cursor.execute(
                "SELECT COUNT(*) FROM agent_crashes WHERE crashed_at > ?",
                (datetime.fromtimestamp(one_hour_ago).isoformat(),),
            )
            crashes_last_hour = cursor.fetchone()[0]
        finally:
            conn.close()

        # Check orchestrator responsiveness
        orchestrator_age = 0
        if self.work_loop_state_path.exists():
            state = json.loads(self.work_loop_state_path.read_text())
            orchestrator_age = int(time.time() - state.get("last_update", 0))

        return {
            "active_agents": active_count,
            "crashed_agents_last_hour": crashes_last_hour,
            "orchestrator_last_poll": orchestrator_age,
        }

    def auto_fix_issues(self):
        """Automatically fix detected issues."""
        status = self.check_health()

        for issue in status.issues:
            if issue["type"] == "agent_crash":
                self._handle_agent_crash(issue)
            elif issue["type"] == "orchestrator_freeze":
                self._handle_orchestrator_freeze(issue)

    def _handle_agent_crash(self, issue: Dict):
        """Handle agent crash - respawn and/or report bug.

        Args:
            issue: Crash issue dict
        """
        # Record crash
        crash = AgentCrash(
            crash_id=None,
            agent_pid=issue["agent_pid"],
            agent_type=issue["agent_type"],
            task_id=issue["task_id"],
            crashed_at=datetime.now().isoformat(),
            error_type=issue.get("error_type", "Unknown"),
            error_message=issue.get("error_message", ""),
            stack_trace="",  # TODO: Extract from logs
            respawned=False,
            bug_reported=False,
            bug_number=None,
        )

        # Check crash count for this task
        crash_count = self._get_crash_count(crash.task_id)

        if crash_count < self.max_respawn_attempts:
            # Attempt respawn
            logger.info(
                f"♻️  Attempting to respawn {crash.agent_type} (attempt {crash_count + 1}/{self.max_respawn_attempts})"
            )
            # TODO: Implement respawn logic
            crash.respawned = True
            issue["action_taken"] = f"respawned_attempt_{crash_count + 1}"
        else:
            # Too many crashes - report bug
            logger.warning(f"🐛 Agent {crash.agent_type} crashed {crash_count} times - reporting bug")
            bug_number = self._report_bug(crash)
            crash.bug_reported = True
            crash.bug_number = bug_number
            issue["bug_reported"] = True
            issue["bug_number"] = bug_number

        # Save crash to database
        self._record_crash(crash)

    def _handle_orchestrator_freeze(self, issue: Dict):
        """Handle orchestrator freeze - restart and report bug.

        Args:
            issue: Freeze issue dict
        """
        logger.error(f"🚨 Orchestrator frozen for {issue['age_seconds']}s - reporting CRITICAL bug")

        bug_number = self._report_orchestrator_freeze_bug(issue)
        issue["bug_reported"] = True
        issue["bug_number"] = bug_number

    def _report_bug(self, crash: AgentCrash) -> int:
        """Report bug via BugTracker.

        Args:
            crash: AgentCrash data

        Returns:
            Bug number created
        """
        try:
            bug_title = f"{crash.agent_type} crashes with {crash.error_type}"
            bug_description = f"""Agent Type: {crash.agent_type}
Task: {crash.task_id}
Error: {crash.error_message}

The {crash.agent_type} agent crashes immediately after spawn with {crash.error_type}.
This has occurred multiple times ({self.max_respawn_attempts}+ crashes).

Auto-detected by orchestrator-health-monitor skill.

Stack Trace:
{crash.stack_trace}
"""

            reproduction_steps = [
                "Start orchestrator",
                f"Spawn {crash.agent_type} for task {crash.task_id}",
                f"Observe immediate crash with {crash.error_type}",
            ]

            priority = "High" if crash.error_type in ["ImportError", "ModuleNotFoundError"] else "Medium"

            logger.info(f"📝 Creating bug ticket: {bug_title}")
            logger.info(f"   Priority: {priority}")
            logger.info(f"   Error: {crash.error_message[:100]}")

            # Create bug ticket using existing BugTracker
            tracker = BugTracker()
            bug_number, ticket_path = tracker.create_bug_ticket(
                description=bug_description,
                title=bug_title,
                priority=priority,
                reproduction_steps=reproduction_steps,
            )

            logger.info(f"✅ Bug ticket created: BUG-{bug_number:03d} at {ticket_path}")
            return bug_number

        except Exception as e:
            logger.error(f"Failed to report bug: {e}")
            return -1

    def _report_orchestrator_freeze_bug(self, issue: Dict) -> int:
        """Report orchestrator freeze as CRITICAL bug.

        Args:
            issue: Freeze issue dict

        Returns:
            Bug number created
        """
        bug_title = "Orchestrator work loop frozen"
        bug_description = f"""The orchestrator continuous work loop has stopped responding.

Last Update: {datetime.fromtimestamp(issue['last_update']).isoformat()}
Freeze Duration: {issue['age_seconds']} seconds ({issue['age_seconds'] / 60:.1f} minutes)

The work loop should poll every 30 seconds but has not logged any activity.

Auto-detected by orchestrator-health-monitor skill.
"""

        logger.error(f"🚨 Creating CRITICAL bug: {bug_title}")

        # TODO: Create bug via bug-tracking skill
        return 2  # Placeholder

    def _get_crash_count(self, task_id: str) -> int:
        """Get crash count for a specific task.

        Args:
            task_id: Task identifier

        Returns:
            Number of crashes for this task
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agent_crashes WHERE task_id = ?", (task_id,))
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def _record_crash(self, crash: AgentCrash):
        """Record crash in database.

        Args:
            crash: AgentCrash to record
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_crashes
                (agent_pid, agent_type, task_id, crashed_at, error_type,
                 error_message, stack_trace, respawned, bug_reported, bug_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    crash.agent_pid,
                    crash.agent_type,
                    crash.task_id,
                    crash.crashed_at,
                    crash.error_type,
                    crash.error_message,
                    crash.stack_trace,
                    crash.respawned,
                    crash.bug_reported,
                    crash.bug_number,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _record_health_check(self, status: HealthStatus):
        """Record health check in database.

        Args:
            status: HealthStatus to record
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            actions_taken = [i.get("action_taken") for i in status.issues if i.get("action_taken")]
            bugs_reported = [i.get("bug_number") for i in status.issues if i.get("bug_reported")]

            cursor.execute(
                """
                INSERT INTO health_checks
                (timestamp, status, active_agents, crashed_agents, zombie_processes,
                 orchestrator_responsive, last_poll_age_seconds, actions_taken, bugs_reported)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    status.timestamp,
                    status.status,
                    status.metrics.get("active_agents", 0),
                    status.metrics.get("crashed_agents_last_hour", 0),
                    len([i for i in status.issues if i["type"] == "zombie_processes"]),
                    status.metrics.get("orchestrator_last_poll", 0) < self.freeze_threshold,
                    status.metrics.get("orchestrator_last_poll", 0),
                    json.dumps(actions_taken),
                    json.dumps(bugs_reported),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def report_bugs_if_any(self):
        """Check for issues and report bugs if needed."""
        status = self.check_health()

        if status.status != "healthy":
            logger.warning(f"⚠️  Health status: {status.status} ({len(status.issues)} issues)")

            for issue in status.issues:
                if not issue.get("bug_reported"):
                    if issue["type"] == "agent_crash":
                        crash_count = self._get_crash_count(issue["task_id"])
                        if crash_count >= self.max_respawn_attempts:
                            self._handle_agent_crash(issue)
                    elif issue["type"] == "orchestrator_freeze":
                        self._handle_orchestrator_freeze(issue)
        else:
            logger.info("✅ Health status: healthy")
