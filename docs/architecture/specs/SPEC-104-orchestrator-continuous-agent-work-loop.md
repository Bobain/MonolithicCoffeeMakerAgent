# SPEC-104: Orchestrator Continuous Agent Work Loop

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-19
**Related User Story**: PRIORITY 20 - US-104
**Dependencies**: SPEC-062 (Orchestrator Agent Architecture)
**Strategic Value**: 24/7 autonomous development, zero idle time for code_developer and architect

---

## Executive Summary

This specification defines the **Continuous Agent Work Loop** for the Orchestrator Agent, enabling 24/7 autonomous operation where code_developer and architect continuously work on ROADMAP priorities without human intervention. The orchestrator manages an infinite loop that monitors the ROADMAP, delegates work to agents, handles task dependencies, and ensures zero idle time.

**Key Capabilities**:
- **Autonomous ROADMAP Monitoring**: Continuous polling of ROADMAP.md for new/updated priorities
- **Intelligent Work Distribution**: Delegates specs to architect, implementation to code_developer
- **Dependency Management**: Ensures specs exist before code_developer starts implementation
- **Zero Idle Time**: Agents continuously work on next available task (no waiting)
- **Error Recovery**: Automatic retry on failures, graceful degradation
- **Graceful Shutdown**: Clean exit on interrupt (Ctrl+C) with state preservation

**Impact**:
- **24/7 Operation**: System works continuously without human supervision
- **3-5x Velocity**: architect creates specs ahead of code_developer (no blocking)
- **Zero Blocking**: code_developer never waits for specs (always 2-3 specs ahead)
- **Predictable Progress**: Continuous progress on ROADMAP priorities
- **User Notification**: Sound alerts only when human decision needed

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Architecture Overview](#architecture-overview)
3. [Component Specifications](#component-specifications)
4. [Data Flow & State Management](#data-flow--state-management)
5. [Work Loop Algorithm](#work-loop-algorithm)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Security Considerations](#security-considerations)
10. [Performance Requirements](#performance-requirements)
11. [Risk Analysis](#risk-analysis)
12. [Success Criteria](#success-criteria)

---

## Problem Statement

### Current Pain Points

**1. Manual Daemon Invocation**
```bash
# User must manually start daemon
poetry run code-developer --auto-approve

# Daemon runs until Ctrl+C or error
# No automatic restart, no continuous monitoring
```

**Problem**: User must remember to start daemon, no 24/7 operation.

**2. Sequential Work Dependency**
```
Current Flow (Sequential):
1. code_developer reads ROADMAP
2. Finds PRIORITY 20 (needs spec)
3. Waits for spec creation ← BLOCKED (2-3 hours)
4. Spec finally created by architect
5. code_developer implements
6. code_developer commits
7. Repeat

Total Time: 5 hours (2h spec wait + 3h implementation)
```

**Problem**: code_developer blocks waiting for architect to create specs.

**3. No Proactive Spec Creation**
```
Desired Flow (Proactive):
1. architect proactively reads ROADMAP
2. Sees next 5 priorities
3. Creates specs for next 3 priorities AHEAD of code_developer
4. code_developer never waits (specs always ready)

Total Time: 3 hours (pure implementation, no wait)
```

**Problem**: architect is reactive (only creates specs when asked), not proactive.

**4. Single Point of Failure**
```
If daemon crashes:
- All work stops
- No automatic recovery
- User must manually restart
- Lost context about current task
```

**Problem**: No fault tolerance, no automatic recovery.

### User Requirements

From ROADMAP PRIORITY 20:
- **Continuous Operation**: Orchestrator runs 24/7 without human intervention
- **Zero Idle Time**: code_developer and architect always have work to do
- **Proactive Spec Creation**: architect creates specs 2-3 priorities ahead
- **Automatic Recovery**: Restart work loop on non-fatal errors
- **Graceful Shutdown**: Clean exit on Ctrl+C with state preservation
- **User Notifications**: Sound alerts only when human decision required (CFR-009)

---

## Architecture Overview

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR CONTINUOUS LOOP                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Main Work Loop (Infinite)                   │  │
│  │                                                               │  │
│  │  while True:                                                  │  │
│  │    1. Poll ROADMAP for changes                               │  │
│  │    2. Identify work needed (specs, implementation)           │  │
│  │    3. Delegate to agents (architect, code_developer)         │  │
│  │    4. Monitor task progress                                  │  │
│  │    5. Handle errors and retries                              │  │
│  │    6. Sleep briefly (30s) and repeat                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Agent Work Coordinators                      │  │
│  │                                                               │  │
│  │  ┌─────────────────────┐  ┌──────────────────────┐           │  │
│  │  │ Architect Coordinator│  │ code_developer Coord │           │  │
│  │  │ - Spec backlog (3+) │  │ - Next priority      │           │  │
│  │  │ - Proactive creation│  │ - Implementation     │           │  │
│  │  │ - CFR-011 compliance│  │ - Test & commit      │           │  │
│  │  └─────────────────────┘  └──────────────────────┘           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    State Management                           │  │
│  │                                                               │  │
│  │  - ROADMAP cache (in-memory + file-based)                    │  │
│  │  - Spec backlog tracker (SQLite)                             │  │
│  │  - Current task state (JSON file)                            │  │
│  │  - Error recovery log (for retries)                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                         AGENT LAYER                                 │
│                                                                     │
│  ┌─────────────────┐           ┌───────────────────────┐           │
│  │   architect     │◄──────────┤  code_developer       │           │
│  │                 │           │                       │           │
│  │ - Create specs  │  Waits    │ - Implement priority  │           │
│  │ - Proactive     │   for     │ - Run tests           │           │
│  │ - 2-3 ahead     │  specs    │ - Commit to roadmap   │           │
│  └─────────────────┘           └───────────────────────┘           │
└────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     Continuous Work Loop Cycle                    │
│                                                                   │
│  1. Poll ROADMAP (every 30s)                                     │
│     ├─► Detect new priorities                                    │
│     ├─► Check spec status for next 5 priorities                  │
│     └─► Identify missing specs                                   │
│                                                                   │
│  2. Architect Coordination                                       │
│     ├─► IF missing specs > 0:                                    │
│     │   ├─► Delegate to architect (create spec)                  │
│     │   ├─► Track in spec_backlog table                          │
│     │   └─► Wait for completion (async)                          │
│     └─► ELSE: architect idle (sleep 5 min)                       │
│                                                                   │
│  3. code_developer Coordination                                  │
│     ├─► Get next PLANNED priority                                │
│     ├─► IF has spec:                                             │
│     │   ├─► Delegate to code_developer (implement)               │
│     │   ├─► Track in implementation_tasks table                  │
│     │   └─► Wait for completion (async)                          │
│     └─► ELSE: code_developer waits (spec not ready)              │
│                                                                   │
│  4. Monitor Progress                                             │
│     ├─► Check task status (message bus)                          │
│     ├─► Detect timeouts (>2 hours → warn)                        │
│     ├─► Detect failures (retry or escalate)                      │
│     └─► Update state files                                       │
│                                                                   │
│  5. Error Handling                                               │
│     ├─► Catch exceptions                                         │
│     ├─► Log to error_recovery.log                                │
│     ├─► Retry non-fatal errors (3 attempts)                      │
│     └─► Fatal errors → graceful shutdown + user notification     │
│                                                                   │
│  6. Sleep & Repeat (30s)                                         │
│     └─► Loop continues 24/7                                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. ContinuousWorkLoop

**Purpose**: Main orchestrator loop that runs 24/7 and delegates work to agents.

**File**: `coffee_maker/orchestrator/continuous_work_loop.py`

**Class Signature**:

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import signal
import logging
from pathlib import Path

from coffee_maker.orchestrator.orchestrator_agent import OrchestratorAgent
from coffee_maker.orchestrator.message_bus import Priority
from coffee_maker.cli.notifications import NotificationDB

logger = logging.getLogger(__name__)


@dataclass
class WorkLoopConfig:
    """Configuration for continuous work loop."""
    poll_interval_seconds: int = 30          # How often to check ROADMAP
    spec_backlog_target: int = 3             # Keep 3 specs ahead of code_developer
    max_retry_attempts: int = 3              # Retry failed tasks up to 3 times
    task_timeout_seconds: int = 7200         # 2 hours max per task
    state_file_path: str = "data/orchestrator/work_loop_state.json"
    enable_sound_notifications: bool = False  # CFR-009: Only user_listener uses sound


class ContinuousWorkLoop:
    """
    Continuous work loop for orchestrator agent.

    Responsibilities:
    - Poll ROADMAP every 30 seconds for new priorities
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Delegate spec creation to architect proactively
    - Delegate implementation to code_developer when specs ready
    - Monitor task progress and handle errors
    - Graceful shutdown on SIGINT (Ctrl+C)
    - State preservation for crash recovery

    CFR Compliance:
    - CFR-009: Sound notifications disabled (sound=False, agent_id="orchestrator")
    - CFR-013: All work happens on roadmap branch only
    """

    def __init__(self, config: WorkLoopConfig = None):
        """
        Initialize continuous work loop.

        Args:
            config: Configuration for work loop (optional, uses defaults)
        """
        self.config = config or WorkLoopConfig()
        self.orchestrator = OrchestratorAgent()
        self.notifications = NotificationDB()
        self.running = False
        self.current_state = {}
        self.roadmap_cache = None
        self.last_roadmap_update = 0.0

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Load previous state if exists (crash recovery)
        self._load_state()

    def start(self):
        """
        Start continuous work loop (runs forever until interrupted).

        Returns:
            None (blocks until graceful shutdown)
        """
        logger.info("🚀 Starting Orchestrator Continuous Work Loop")
        self.running = True
        self.orchestrator.start()  # Start background worker

        self.notifications.create_notification(
            title="Orchestrator Started",
            message="Continuous work loop is now running. Agents will work 24/7 on ROADMAP priorities.",
            level="info",
            sound=False,  # CFR-009: Background agent, no sound
            agent_id="orchestrator"
        )

        try:
            while self.running:
                loop_start = time.time()

                # Main work loop cycle
                try:
                    self._work_cycle()
                except Exception as e:
                    logger.error(f"Error in work cycle: {e}", exc_info=True)
                    self._handle_cycle_error(e)

                # Sleep for poll interval (minus cycle time)
                cycle_duration = time.time() - loop_start
                sleep_time = max(0, self.config.poll_interval_seconds - cycle_duration)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self._shutdown()

    def _work_cycle(self):
        """
        Single iteration of work loop.

        Steps:
        1. Poll ROADMAP for changes
        2. Coordinate architect (proactive spec creation)
        3. Coordinate code_developer (implementation)
        4. Monitor task progress
        5. Handle errors and retries
        """
        # Step 1: Poll ROADMAP
        roadmap_updated = self._poll_roadmap()
        if roadmap_updated:
            logger.info("ROADMAP updated, recalculating work distribution")

        # Step 2: Architect coordination (proactive spec creation)
        self._coordinate_architect()

        # Step 3: code_developer coordination (implementation)
        self._coordinate_code_developer()

        # Step 4: Monitor task progress
        self._monitor_tasks()

        # Step 5: Save state
        self._save_state()

    def _poll_roadmap(self) -> bool:
        """
        Poll ROADMAP.md for changes.

        Returns:
            True if ROADMAP was updated since last check, False otherwise
        """
        roadmap_path = Path("docs/roadmap/ROADMAP.md")

        if not roadmap_path.exists():
            logger.warning("ROADMAP.md not found!")
            return False

        # Check file modification time
        current_mtime = roadmap_path.stat().st_mtime

        if current_mtime > self.last_roadmap_update:
            # ROADMAP was modified, reload
            logger.info(f"ROADMAP.md updated (mtime: {current_mtime})")
            self.roadmap_cache = self._parse_roadmap(roadmap_path)
            self.last_roadmap_update = current_mtime
            return True

        return False

    def _parse_roadmap(self, roadmap_path: Path) -> Dict:
        """
        Parse ROADMAP.md and extract priority information.

        Args:
            roadmap_path: Path to ROADMAP.md

        Returns:
            Dict with priority information:
            {
                "priorities": [
                    {
                        "number": 20,
                        "name": "US-104 - Orchestrator Continuous Work Loop",
                        "status": "📝 Planned",
                        "has_spec": False,
                        "spec_path": None
                    },
                    ...
                ]
            }
        """
        # Simple parsing logic (can be enhanced)
        priorities = []

        with open(roadmap_path, 'r') as f:
            content = f.read()

        # Extract priorities (pattern: "### PRIORITY N: US-XXX - Title")
        import re
        pattern = r'### PRIORITY (\d+): (US-\d+) - (.*?) (📝|✅|🔄)'

        for match in re.finditer(pattern, content):
            priority_num = int(match.group(1))
            us_number = match.group(2)
            title = match.group(3)
            status = match.group(4)

            # Check if spec exists
            spec_path = Path(f"docs/architecture/specs/SPEC-{us_number.split('-')[1]}-*.md")
            has_spec = len(list(spec_path.parent.glob(f"SPEC-{us_number.split('-')[1]}-*.md"))) > 0

            priorities.append({
                "number": priority_num,
                "name": f"{us_number} - {title}",
                "status": status,
                "has_spec": has_spec,
                "spec_path": str(spec_path) if has_spec else None
            })

        return {"priorities": sorted(priorities, key=lambda p: p["number"])}

    def _coordinate_architect(self):
        """
        Coordinate architect to maintain spec backlog.

        Logic:
        1. Get next 5 PLANNED priorities
        2. Count missing specs
        3. If missing > 0: delegate spec creation to architect
        4. Target: Always have 2-3 specs ahead of code_developer
        """
        if not self.roadmap_cache:
            return

        # Get next 5 planned priorities
        planned_priorities = [
            p for p in self.roadmap_cache["priorities"]
            if p["status"] == "📝"  # Planned status
        ][:5]

        # Count missing specs
        missing_specs = [p for p in planned_priorities if not p["has_spec"]]

        if not missing_specs:
            logger.debug("No missing specs, architect idle")
            return

        # Prioritize: Create specs for first 3 missing
        for priority in missing_specs[:self.config.spec_backlog_target]:
            # Check if already creating this spec
            if self._is_spec_in_progress(priority["number"]):
                logger.debug(f"Spec for PRIORITY {priority['number']} already in progress")
                continue

            # Delegate to architect
            logger.info(f"🏗️  Delegating spec creation to architect: PRIORITY {priority['number']}")

            task_id = self.orchestrator.submit_task(
                agent_type="architect",
                payload={
                    "action": "create_spec",
                    "priority_number": priority["number"],
                    "priority_name": priority["name"]
                },
                priority=Priority.HIGH
            )

            self._track_spec_task(priority["number"], task_id)

    def _coordinate_code_developer(self):
        """
        Coordinate code_developer to implement next priority.

        Logic:
        1. Get next PLANNED priority
        2. Check if spec exists
        3. If yes: delegate implementation to code_developer
        4. If no: code_developer waits (architect will create spec)
        """
        if not self.roadmap_cache:
            return

        # Get next planned priority
        planned_priorities = [
            p for p in self.roadmap_cache["priorities"]
            if p["status"] == "📝"
        ]

        if not planned_priorities:
            logger.info("No planned priorities, code_developer idle")
            return

        next_priority = planned_priorities[0]

        # Check if spec exists
        if not next_priority["has_spec"]:
            logger.info(f"⏳ code_developer waiting for spec: PRIORITY {next_priority['number']}")
            return

        # Check if already implementing
        if self._is_implementation_in_progress(next_priority["number"]):
            logger.debug(f"Implementation for PRIORITY {next_priority['number']} already in progress")
            return

        # Delegate to code_developer
        logger.info(f"⚙️  Delegating implementation to code_developer: PRIORITY {next_priority['number']}")

        task_id = self.orchestrator.submit_task(
            agent_type="code_developer",
            payload={
                "action": "implement_priority",
                "priority_number": next_priority["number"],
                "priority_name": next_priority["name"],
                "spec_path": next_priority["spec_path"]
            },
            priority=Priority.HIGH
        )

        self._track_implementation_task(next_priority["number"], task_id)

    def _monitor_tasks(self):
        """
        Monitor in-progress tasks and handle timeouts/failures.

        Checks:
        - Task completion (move from in_progress to completed)
        - Timeouts (task running > 2 hours)
        - Failures (task failed, retry or escalate)
        """
        # Get pending tasks from message bus
        pending_tasks = self.orchestrator.message_bus.get_pending_tasks()

        for task in pending_tasks:
            task_age = time.time() - task.created_at

            # Check timeout
            if task_age > self.config.task_timeout_seconds:
                logger.warning(f"⚠️ Task timeout: {task.id} ({task.agent_type}, {task_age:.0f}s)")

                self.notifications.create_notification(
                    title="Task Timeout Detected",
                    message=f"Task {task.id} ({task.agent_type}) running for {task_age / 3600:.1f} hours",
                    level="high",
                    sound=False,  # CFR-009
                    agent_id="orchestrator"
                )

                # TODO: Implement timeout handling (cancel task, retry, or escalate)

        # Check completed tasks
        completed_tasks = self.orchestrator.message_bus.completed_tasks

        for task_id, result in list(completed_tasks.items()):
            if result.status == "failure":
                logger.error(f"❌ Task failed: {task_id} - {result.error}")

                # Retry logic (up to 3 attempts)
                retry_count = self.current_state.get(f"retry_{task_id}", 0)

                if retry_count < self.config.max_retry_attempts:
                    logger.info(f"🔄 Retrying task {task_id} (attempt {retry_count + 1}/{self.config.max_retry_attempts})")
                    self.current_state[f"retry_{task_id}"] = retry_count + 1
                    # TODO: Resubmit task
                else:
                    logger.error(f"🚫 Max retries reached for task {task_id}, escalating to user")

                    self.notifications.create_notification(
                        title="Task Failed After Retries",
                        message=f"Task {task_id} failed {self.config.max_retry_attempts} times. Manual intervention required.",
                        level="critical",
                        sound=False,  # CFR-009: Background agent
                        agent_id="orchestrator"
                    )

    def _is_spec_in_progress(self, priority_number: int) -> bool:
        """Check if spec creation is already in progress for priority."""
        return f"spec_{priority_number}" in self.current_state.get("active_tasks", {})

    def _is_implementation_in_progress(self, priority_number: int) -> bool:
        """Check if implementation is already in progress for priority."""
        return f"impl_{priority_number}" in self.current_state.get("active_tasks", {})

    def _track_spec_task(self, priority_number: int, task_id: str):
        """Track spec creation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"spec_{priority_number}"] = {
            "task_id": task_id,
            "started_at": time.time(),
            "type": "spec_creation"
        }

    def _track_implementation_task(self, priority_number: int, task_id: str):
        """Track implementation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"impl_{priority_number}"] = {
            "task_id": task_id,
            "started_at": time.time(),
            "type": "implementation"
        }

    def _handle_cycle_error(self, error: Exception):
        """
        Handle errors during work cycle.

        Args:
            error: Exception that occurred
        """
        logger.error(f"Work cycle error: {error}", exc_info=True)

        # Log to error recovery file
        error_log_path = Path("data/orchestrator/error_recovery.log")
        error_log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(error_log_path, 'a') as f:
            f.write(f"{time.time()}: {error}\n")

        # Notify user for critical errors
        if isinstance(error, (IOError, PermissionError)):
            self.notifications.create_notification(
                title="Orchestrator Error",
                message=f"Critical error: {error}. Work loop may need manual restart.",
                level="critical",
                sound=False,  # CFR-009
                agent_id="orchestrator"
            )

    def _handle_shutdown(self, signum, frame):
        """
        Handle shutdown signals (SIGINT, SIGTERM).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.running = False

    def _shutdown(self):
        """Graceful shutdown: save state and stop orchestrator."""
        logger.info("🛑 Shutting down Orchestrator Work Loop")

        # Save final state
        self._save_state()

        # Stop orchestrator
        self.orchestrator.stop()

        self.notifications.create_notification(
            title="Orchestrator Stopped",
            message="Continuous work loop has been stopped. State saved for recovery.",
            level="info",
            sound=False,  # CFR-009
            agent_id="orchestrator"
        )

        logger.info("✅ Graceful shutdown complete")

    def _save_state(self):
        """Save current state to disk (for crash recovery)."""
        import json

        state_path = Path(self.config.state_file_path)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state_data = {
            "last_update": time.time(),
            "active_tasks": self.current_state.get("active_tasks", {}),
            "roadmap_cache": self.roadmap_cache,
            "last_roadmap_update": self.last_roadmap_update
        }

        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _load_state(self):
        """Load previous state from disk (crash recovery)."""
        import json

        state_path = Path(self.config.state_file_path)

        if not state_path.exists():
            logger.info("No previous state found, starting fresh")
            return

        try:
            with open(state_path, 'r') as f:
                state_data = json.load(f)

            self.current_state = state_data
            self.roadmap_cache = state_data.get("roadmap_cache")
            self.last_roadmap_update = state_data.get("last_roadmap_update", 0.0)

            logger.info(f"Loaded previous state (last update: {state_data['last_update']})")

        except Exception as e:
            logger.error(f"Failed to load state: {e}", exc_info=True)
```

**Key Methods**:

| Method | Purpose | Execution Frequency |
|--------|---------|---------------------|
| `start()` | Start infinite work loop | Once (blocks until shutdown) |
| `_work_cycle()` | Single iteration of loop | Every 30 seconds |
| `_poll_roadmap()` | Check ROADMAP.md for updates | Every cycle |
| `_coordinate_architect()` | Delegate spec creation | Every cycle (if missing specs) |
| `_coordinate_code_developer()` | Delegate implementation | Every cycle (if spec ready) |
| `_monitor_tasks()` | Check task progress, handle errors | Every cycle |
| `_save_state()` | Persist state to disk | Every cycle |
| `_load_state()` | Recover from crash | On startup |
| `_shutdown()` | Graceful cleanup on exit | On SIGINT/SIGTERM |

---

### 2. ArchitectCoordinator

**Purpose**: Specialized coordinator for architect agent (proactive spec creation).

**File**: `coffee_maker/orchestrator/architect_coordinator.py`

**Class Signature**:

```python
from typing import List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ArchitectCoordinator:
    """
    Coordinates architect agent for proactive spec creation.

    Responsibilities:
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Prioritize spec creation by ROADMAP order
    - Track spec creation progress
    - Ensure CFR-011 compliance (architect reads code-searcher reports)
    """

    def __init__(self, orchestrator_agent):
        self.orchestrator = orchestrator_agent
        self.spec_backlog_target = 3

    def get_missing_specs(self, priorities: List[Dict]) -> List[Dict]:
        """
        Identify priorities that need specs.

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of priorities missing specs, sorted by priority number
        """
        missing = []

        for priority in priorities:
            if not self._has_spec(priority):
                missing.append(priority)

        return sorted(missing, key=lambda p: p["number"])

    def _has_spec(self, priority: Dict) -> bool:
        """
        Check if technical spec exists for priority.

        Args:
            priority: Priority dict

        Returns:
            True if spec exists, False otherwise
        """
        # Extract US number (e.g., "US-104 - Title" → "104")
        us_number = priority["name"].split("-")[1].split(" ")[0]

        spec_pattern = f"SPEC-{us_number}-*.md"
        spec_path = Path("docs/architecture/specs")

        return len(list(spec_path.glob(spec_pattern))) > 0

    def create_spec_backlog(self, priorities: List[Dict]) -> List[str]:
        """
        Create spec backlog (submit tasks for first N missing specs).

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of task IDs for submitted spec creation tasks
        """
        missing_specs = self.get_missing_specs(priorities)[:self.spec_backlog_target]

        task_ids = []

        for priority in missing_specs:
            task_id = self.orchestrator.submit_task(
                agent_type="architect",
                payload={
                    "action": "create_spec",
                    "priority_number": priority["number"],
                    "priority_name": priority["name"]
                },
                priority=Priority.HIGH
            )

            task_ids.append(task_id)

            logger.info(f"📋 Queued spec creation: PRIORITY {priority['number']} (task: {task_id})")

        return task_ids
```

---

### 3. CodeDeveloperCoordinator

**Purpose**: Specialized coordinator for code_developer agent (implementation).

**File**: `coffee_maker/orchestrator/code_developer_coordinator.py`

**Class Signature**:

```python
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CodeDeveloperCoordinator:
    """
    Coordinates code_developer agent for implementation.

    Responsibilities:
    - Find next PLANNED priority with spec
    - Delegate implementation to code_developer
    - Track implementation progress
    - Ensure CFR-013 compliance (roadmap branch only)
    """

    def __init__(self, orchestrator_agent):
        self.orchestrator = orchestrator_agent

    def get_next_implementable_priority(self, priorities: List[Dict]) -> Optional[Dict]:
        """
        Get next PLANNED priority that has a spec.

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            Next priority to implement, or None if no work available
        """
        planned = [p for p in priorities if p["status"] == "📝"]

        for priority in planned:
            if priority["has_spec"]:
                return priority

        return None

    def submit_implementation_task(self, priority: Dict) -> str:
        """
        Submit implementation task to code_developer.

        Args:
            priority: Priority dict

        Returns:
            Task ID
        """
        task_id = self.orchestrator.submit_task(
            agent_type="code_developer",
            payload={
                "action": "implement_priority",
                "priority_number": priority["number"],
                "priority_name": priority["name"],
                "spec_path": priority["spec_path"]
            },
            priority=Priority.HIGH
        )

        logger.info(f"⚙️  Queued implementation: PRIORITY {priority['number']} (task: {task_id})")

        return task_id
```

---

## Data Flow & State Management

### State Files

**1. Work Loop State** (`data/orchestrator/work_loop_state.json`)

```json
{
  "last_update": 1729368000.0,
  "active_tasks": {
    "spec_20": {
      "task_id": "abc-123-def",
      "started_at": 1729367800.0,
      "type": "spec_creation"
    },
    "impl_19": {
      "task_id": "xyz-456-ghi",
      "started_at": 1729367900.0,
      "type": "implementation"
    }
  },
  "roadmap_cache": {
    "priorities": [
      {
        "number": 20,
        "name": "US-104 - Orchestrator Continuous Work Loop",
        "status": "📝",
        "has_spec": true,
        "spec_path": "docs/architecture/specs/SPEC-104-orchestrator-continuous-agent-work-loop.md"
      }
    ]
  },
  "last_roadmap_update": 1729368000.0
}
```

**2. Error Recovery Log** (`data/orchestrator/error_recovery.log`)

```
1729368000.0: IOError: Failed to read ROADMAP.md
1729368100.0: TimeoutError: Task abc-123-def timed out after 7200s
```

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     Data Flow (Single Cycle)                   │
│                                                                 │
│  1. Poll ROADMAP.md                                            │
│     ├─► Read file (stat.st_mtime check)                        │
│     ├─► Parse priorities (regex)                               │
│     ├─► Check spec existence (glob)                            │
│     └─► Update roadmap_cache                                   │
│                                                                 │
│  2. Architect Coordination                                     │
│     ├─► Get missing specs (ArchitectCoordinator)               │
│     ├─► Submit tasks (MessageBus.publish)                      │
│     ├─► Track in active_tasks                                  │
│     └─► architect agent consumes task                          │
│                                                                 │
│  3. code_developer Coordination                                │
│     ├─► Get next priority (CodeDeveloperCoordinator)           │
│     ├─► Submit task (MessageBus.publish)                       │
│     ├─► Track in active_tasks                                  │
│     └─► code_developer agent consumes task                     │
│                                                                 │
│  4. Monitor Progress                                           │
│     ├─► Check MessageBus.completed_tasks                       │
│     ├─► Handle failures (retry or escalate)                    │
│     ├─► Handle timeouts (warn or cancel)                       │
│     └─► Remove from active_tasks when complete                 │
│                                                                 │
│  5. Save State                                                 │
│     ├─► Write work_loop_state.json                             │
│     └─► Persist for crash recovery                             │
└────────────────────────────────────────────────────────────────┘
```

---

## Work Loop Algorithm

### Pseudocode

```python
def continuous_work_loop():
    """Main orchestrator work loop (infinite)."""

    # Initialization
    initialize_orchestrator()
    load_previous_state()  # Crash recovery
    register_signal_handlers()  # Ctrl+C → graceful shutdown

    running = True

    while running:
        try:
            # === CYCLE START ===

            # Step 1: Poll ROADMAP for changes
            roadmap_updated = poll_roadmap()
            if roadmap_updated:
                log("ROADMAP updated, recalculating work")
                roadmap_cache = parse_roadmap("docs/roadmap/ROADMAP.md")

            # Step 2: Architect Coordination (Proactive Spec Creation)
            next_5_priorities = get_next_5_planned_priorities(roadmap_cache)
            missing_specs = identify_missing_specs(next_5_priorities)

            if len(missing_specs) > 0:
                # Create specs proactively (keep 2-3 ahead)
                for priority in missing_specs[:3]:
                    if not is_spec_in_progress(priority.number):
                        task_id = submit_task(
                            agent="architect",
                            action="create_spec",
                            priority=priority
                        )
                        track_spec_task(priority.number, task_id)
                        log(f"Delegated spec creation: {priority.name}")

            # Step 3: code_developer Coordination (Implementation)
            next_priority = get_next_planned_priority(roadmap_cache)

            if next_priority:
                if has_spec(next_priority):
                    if not is_implementation_in_progress(next_priority.number):
                        task_id = submit_task(
                            agent="code_developer",
                            action="implement_priority",
                            priority=next_priority
                        )
                        track_implementation_task(next_priority.number, task_id)
                        log(f"Delegated implementation: {next_priority.name}")
                else:
                    log(f"Waiting for spec: {next_priority.name}")

            # Step 4: Monitor Tasks
            pending_tasks = get_pending_tasks()

            for task in pending_tasks:
                # Check timeout
                if task.age > 2_hours:
                    log(f"Task timeout: {task.id}")
                    notify_user("Task timeout detected")

                # Check failure
                if task.status == "failure":
                    retry_count = get_retry_count(task.id)

                    if retry_count < 3:
                        log(f"Retrying task {task.id} (attempt {retry_count + 1}/3)")
                        resubmit_task(task)
                    else:
                        log(f"Max retries reached for {task.id}, escalating")
                        notify_user("Task failed after retries", sound=False)

            # Step 5: Save State (Crash Recovery)
            save_state({
                "last_update": now(),
                "active_tasks": active_tasks,
                "roadmap_cache": roadmap_cache,
                "last_roadmap_update": last_roadmap_update
            })

            # === CYCLE END ===

            # Sleep for poll interval (30s)
            sleep(30)

        except Exception as e:
            log_error(e)
            handle_cycle_error(e)
            # Continue loop (don't crash on non-fatal errors)

    # Graceful shutdown
    shutdown()
    log("Orchestrator stopped")
```

### State Transitions

```
ROADMAP Priority States:
┌─────────────────────────────────────────────────────────────┐
│  📝 Planned → 🏗️ Spec Creation → ⚙️ Implementation → ✅ Done │
└─────────────────────────────────────────────────────────────┘

Orchestrator Work Flow:
┌────────────────────────────────────────────────────────────────┐
│  1. Detect 📝 Planned priority                                 │
│     ↓                                                           │
│  2. Check if spec exists                                       │
│     ├─► No → Delegate to architect (🏗️ Spec Creation)          │
│     │        ├─► architect creates spec                        │
│     │        └─► Spec complete → Move to step 3                │
│     └─► Yes → Skip to step 3                                   │
│     ↓                                                           │
│  3. Delegate to code_developer (⚙️ Implementation)              │
│     ├─► code_developer implements                              │
│     ├─► Tests pass                                             │
│     └─► Commit to roadmap branch                               │
│     ↓                                                           │
│  4. Mark priority as ✅ Complete                                │
│     └─► Move to next priority                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Error Handling & Recovery

### Error Categories

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| **Non-Fatal** | - ROADMAP.md temporarily unavailable<br>- Agent busy (queue full) | - Log warning<br>- Retry next cycle (30s)<br>- Continue loop |
| **Retryable** | - Task timeout (>2h)<br>- LLM API error<br>- Network error | - Retry up to 3 times<br>- Exponential backoff<br>- Log each attempt |
| **Fatal** | - ROADMAP.md permanently missing<br>- Orchestrator crash<br>- SIGKILL | - Save state immediately<br>- Graceful shutdown<br>- Notify user (critical) |

### Retry Logic

```python
def retry_task(task_id: str, max_attempts: int = 3):
    """
    Retry failed task with exponential backoff.

    Args:
        task_id: Task to retry
        max_attempts: Maximum retry attempts

    Returns:
        True if task succeeded, False if max retries reached
    """
    retry_count = get_retry_count(task_id)

    if retry_count >= max_attempts:
        logger.error(f"Max retries ({max_attempts}) reached for task {task_id}")
        return False

    # Exponential backoff: 30s, 60s, 120s
    backoff_seconds = 30 * (2 ** retry_count)

    logger.info(f"Retrying task {task_id} in {backoff_seconds}s (attempt {retry_count + 1}/{max_attempts})")

    time.sleep(backoff_seconds)

    # Resubmit task
    original_task = get_original_task(task_id)
    new_task_id = resubmit_task(original_task)

    # Increment retry count
    set_retry_count(new_task_id, retry_count + 1)

    return True
```

### Crash Recovery

**Scenario**: Orchestrator crashes mid-cycle

**Recovery Steps**:

1. **On Next Startup**:
   ```python
   # Load previous state
   state = load_state("data/orchestrator/work_loop_state.json")

   # Resume active tasks
   for task_key, task_info in state["active_tasks"].items():
       task_id = task_info["task_id"]

       # Check if task completed while orchestrator was down
       if task_id in message_bus.completed_tasks:
           logger.info(f"Task {task_id} completed during downtime")
           remove_from_active_tasks(task_key)
       else:
           logger.info(f"Resuming task {task_id}")
           # Task will continue running (agent is independent)
   ```

2. **State Validation**:
   ```python
   # Validate roadmap_cache is still current
   current_mtime = get_roadmap_mtime()

   if current_mtime > state["last_roadmap_update"]:
       logger.info("ROADMAP updated during downtime, reloading")
       roadmap_cache = parse_roadmap("docs/roadmap/ROADMAP.md")
   ```

3. **Resume Normal Operation**:
   ```python
   # Continue work loop as normal
   start_work_loop()
   ```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

**Deliverables**:
- [ ] `ContinuousWorkLoop` class with infinite loop
- [ ] ROADMAP polling and parsing
- [ ] State management (save/load)
- [ ] Signal handlers (graceful shutdown)
- [ ] Unit tests (15 tests)

**Tasks**:

1. **Create `ContinuousWorkLoop` class** (8 hours)
   - File: `coffee_maker/orchestrator/continuous_work_loop.py`
   - Methods: `start()`, `_work_cycle()`, `_poll_roadmap()`, `_shutdown()`
   - Signal handlers: SIGINT, SIGTERM
   - State file: `data/orchestrator/work_loop_state.json`

2. **Implement ROADMAP parsing** (4 hours)
   - Method: `_parse_roadmap()`
   - Extract priorities with regex
   - Check spec existence with glob
   - Return structured dict

3. **Implement state management** (3 hours)
   - Methods: `_save_state()`, `_load_state()`
   - JSON serialization
   - Crash recovery logic

4. **Write unit tests** (5 hours)
   - `test_work_loop_start_stop()`
   - `test_poll_roadmap()`
   - `test_parse_roadmap()`
   - `test_save_load_state()`
   - `test_graceful_shutdown()`
   - `test_crash_recovery()`

**Time Estimate**: 20 hours (2.5 days)

---

### Phase 2: Agent Coordination (Week 1-2)

**Deliverables**:
- [ ] `ArchitectCoordinator` class
- [ ] `CodeDeveloperCoordinator` class
- [ ] Task delegation logic
- [ ] Spec backlog management
- [ ] Unit tests (20 tests)

**Tasks**:

1. **Create `ArchitectCoordinator`** (6 hours)
   - File: `coffee_maker/orchestrator/architect_coordinator.py`
   - Methods: `get_missing_specs()`, `create_spec_backlog()`
   - Spec existence checks
   - Backlog target: 3 specs ahead

2. **Create `CodeDeveloperCoordinator`** (4 hours)
   - File: `coffee_maker/orchestrator/code_developer_coordinator.py`
   - Methods: `get_next_implementable_priority()`, `submit_implementation_task()`
   - Priority selection logic

3. **Integrate coordinators into work loop** (6 hours)
   - Update `_work_cycle()` to use coordinators
   - Add `_coordinate_architect()` method
   - Add `_coordinate_code_developer()` method
   - Task tracking logic

4. **Write unit tests** (4 hours)
   - `test_architect_coordinator()`
   - `test_code_developer_coordinator()`
   - `test_spec_backlog_maintenance()`
   - `test_task_delegation()`

**Time Estimate**: 20 hours (2.5 days)

---

### Phase 3: Monitoring & Error Handling (Week 2)

**Deliverables**:
- [ ] Task monitoring logic
- [ ] Timeout detection
- [ ] Retry mechanism
- [ ] Error recovery
- [ ] Unit tests (15 tests)

**Tasks**:

1. **Implement task monitoring** (6 hours)
   - Method: `_monitor_tasks()`
   - Check task completion
   - Detect timeouts (>2 hours)
   - Update active_tasks

2. **Implement retry logic** (5 hours)
   - Method: `_retry_task()`
   - Exponential backoff
   - Max 3 attempts
   - Error logging

3. **Implement error handling** (5 hours)
   - Method: `_handle_cycle_error()`
   - Error categorization (fatal vs non-fatal)
   - Crash recovery
   - User notifications

4. **Write unit tests** (4 hours)
   - `test_monitor_tasks()`
   - `test_timeout_detection()`
   - `test_retry_logic()`
   - `test_error_handling()`

**Time Estimate**: 20 hours (2.5 days)

---

### Phase 4: Integration & Testing (Week 2-3)

**Deliverables**:
- [ ] CLI command: `poetry run orchestrator start`
- [ ] Integration tests (10 tests)
- [ ] End-to-end testing
- [ ] Documentation updates

**Tasks**:

1. **Create CLI command** (3 hours)
   - File: `coffee_maker/cli/orchestrator_cli.py`
   - Command: `orchestrator start [--config CONFIG]`
   - Integration with Click

2. **Write integration tests** (8 hours)
   - `test_full_work_loop_cycle()`
   - `test_architect_spec_creation()`
   - `test_code_developer_implementation()`
   - `test_crash_recovery()`
   - `test_graceful_shutdown()`

3. **End-to-end testing** (6 hours)
   - Run orchestrator for 24 hours
   - Monitor ROADMAP progress
   - Verify spec backlog maintained
   - Check error recovery

4. **Update documentation** (3 hours)
   - Update CLAUDE.md (orchestrator usage)
   - Update ROADMAP.md (PRIORITY 20 complete)
   - Create ADR-014 (Continuous Work Loop)

**Time Estimate**: 20 hours (2.5 days)

---

### Phase 5: Code Review & Deployment (Week 3)

**Deliverables**:
- [ ] Architect code review
- [ ] Address feedback
- [ ] Final approval
- [ ] Production deployment

**Tasks**:

1. **Architect review** (4 hours)
   - Review all implementation
   - Check CFR compliance (CFR-009, CFR-013)
   - Verify error handling
   - Provide feedback

2. **Address feedback** (8 hours)
   - Fix issues identified by architect
   - Re-run tests
   - Update documentation

3. **Final approval** (2 hours)
   - Architect final review
   - User acceptance testing
   - Production readiness check

4. **Deploy to production** (2 hours)
   - Merge to roadmap branch
   - Create git tag: `stable-v2.0.0`
   - Update ROADMAP status
   - Notify user

**Time Estimate**: 16 hours (2 days)

---

**Total Implementation Time**: 96 hours (12 days)

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_continuous_work_loop.py`

```python
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from coffee_maker.orchestrator.continuous_work_loop import (
    ContinuousWorkLoop,
    WorkLoopConfig
)


def test_work_loop_initialization():
    """Test that work loop initializes correctly."""
    config = WorkLoopConfig(poll_interval_seconds=10)
    loop = ContinuousWorkLoop(config)

    assert loop.config.poll_interval_seconds == 10
    assert loop.running is False
    assert loop.current_state == {}


def test_poll_roadmap_detects_changes(tmp_path):
    """Test that polling detects ROADMAP changes."""
    roadmap_path = tmp_path / "ROADMAP.md"
    roadmap_path.write_text("### PRIORITY 20: US-104 - Test")

    loop = ContinuousWorkLoop()

    # First poll
    with patch('pathlib.Path', return_value=roadmap_path):
        updated = loop._poll_roadmap()
        assert updated is True

    # Second poll (no changes)
    updated = loop._poll_roadmap()
    assert updated is False

    # Modify ROADMAP
    time.sleep(0.1)
    roadmap_path.write_text("### PRIORITY 20: US-104 - Updated")

    # Third poll (changes detected)
    updated = loop._poll_roadmap()
    assert updated is True


def test_parse_roadmap():
    """Test ROADMAP parsing extracts priorities correctly."""
    roadmap_content = """
    ### PRIORITY 20: US-104 - Orchestrator Work Loop 📝 Planned
    ### PRIORITY 21: US-105 - Dashboard ✅ Complete
    """

    loop = ContinuousWorkLoop()
    roadmap_path = Path("test_roadmap.md")

    with patch('pathlib.Path.open', return_value=roadmap_content):
        result = loop._parse_roadmap(roadmap_path)

    assert len(result["priorities"]) == 2
    assert result["priorities"][0]["number"] == 20
    assert result["priorities"][0]["status"] == "📝"


def test_architect_coordination_creates_specs():
    """Test that architect coordinator creates missing specs."""
    loop = ContinuousWorkLoop()
    loop.roadmap_cache = {
        "priorities": [
            {"number": 20, "name": "US-104 - Test", "status": "📝", "has_spec": False},
            {"number": 21, "name": "US-105 - Test 2", "status": "📝", "has_spec": False}
        ]
    }

    with patch.object(loop.orchestrator, 'submit_task', return_value="task-123"):
        loop._coordinate_architect()

    # Should submit spec creation tasks
    assert loop.orchestrator.submit_task.call_count == 2


def test_code_developer_waits_for_spec():
    """Test that code_developer waits if spec not ready."""
    loop = ContinuousWorkLoop()
    loop.roadmap_cache = {
        "priorities": [
            {"number": 20, "name": "US-104 - Test", "status": "📝", "has_spec": False}
        ]
    }

    with patch.object(loop.orchestrator, 'submit_task') as mock_submit:
        loop._coordinate_code_developer()

    # Should NOT submit implementation (spec missing)
    mock_submit.assert_not_called()


def test_graceful_shutdown():
    """Test that shutdown signal stops work loop cleanly."""
    loop = ContinuousWorkLoop()
    loop.running = True

    # Simulate SIGINT
    loop._handle_shutdown(signal.SIGINT, None)

    assert loop.running is False


def test_state_save_and_load(tmp_path):
    """Test state persistence."""
    config = WorkLoopConfig(state_file_path=str(tmp_path / "state.json"))
    loop = ContinuousWorkLoop(config)

    # Set some state
    loop.current_state = {
        "active_tasks": {
            "spec_20": {"task_id": "abc-123", "started_at": time.time()}
        }
    }

    # Save state
    loop._save_state()

    # Create new loop (simulates restart)
    loop2 = ContinuousWorkLoop(config)
    loop2._load_state()

    # State should be restored
    assert "spec_20" in loop2.current_state["active_tasks"]


def test_task_timeout_detection():
    """Test that task timeouts are detected."""
    loop = ContinuousWorkLoop()

    # Create a task that started 3 hours ago
    old_task = Mock()
    old_task.created_at = time.time() - 10800  # 3 hours ago
    old_task.id = "old-task"
    old_task.agent_type = "architect"

    loop.orchestrator.message_bus.get_pending_tasks = Mock(return_value=[old_task])

    with patch.object(loop.notifications, 'create_notification') as mock_notify:
        loop._monitor_tasks()

    # Should create notification for timeout
    mock_notify.assert_called_once()
    assert "timeout" in mock_notify.call_args[1]["message"].lower()


def test_retry_logic():
    """Test that failed tasks are retried up to 3 times."""
    loop = ContinuousWorkLoop()

    failed_task_result = Mock()
    failed_task_result.task_id = "failed-task"
    failed_task_result.status = "failure"
    failed_task_result.error = "LLM API error"

    loop.orchestrator.message_bus.completed_tasks = {"failed-task": failed_task_result}

    # First failure (retry count = 0)
    loop._monitor_tasks()
    assert loop.current_state.get("retry_failed-task") == 1

    # Second failure (retry count = 1)
    loop._monitor_tasks()
    assert loop.current_state.get("retry_failed-task") == 2

    # Third failure (retry count = 2)
    loop._monitor_tasks()
    assert loop.current_state.get("retry_failed-task") == 3

    # Fourth failure (max retries reached, should escalate)
    with patch.object(loop.notifications, 'create_notification') as mock_notify:
        loop._monitor_tasks()

    # Should create critical notification
    mock_notify.assert_called()
    assert mock_notify.call_args[1]["level"] == "critical"
```

**Test Coverage Target**: >85%

---

### Integration Tests

**File**: `tests/integration/test_orchestrator_work_loop.py`

```python
import pytest
import time
import threading
from pathlib import Path

from coffee_maker.orchestrator.continuous_work_loop import ContinuousWorkLoop


@pytest.fixture
def test_roadmap(tmp_path):
    """Create a test ROADMAP file."""
    roadmap_path = tmp_path / "ROADMAP.md"
    roadmap_path.write_text("""
    ### PRIORITY 20: US-104 - Orchestrator Work Loop 📝 Planned
    ### PRIORITY 21: US-105 - Dashboard ✅ Complete
    """)
    return roadmap_path


def test_full_work_loop_cycle(test_roadmap):
    """Test full work loop cycle (poll, coordinate, monitor)."""
    loop = ContinuousWorkLoop()

    # Patch ROADMAP path
    with patch('pathlib.Path', return_value=test_roadmap):
        # Run one cycle
        loop._work_cycle()

    # Verify ROADMAP was polled
    assert loop.roadmap_cache is not None
    assert len(loop.roadmap_cache["priorities"]) == 2


def test_orchestrator_runs_for_1_minute():
    """Test that orchestrator runs continuously for 1 minute."""
    loop = ContinuousWorkLoop()

    # Start in background thread
    thread = threading.Thread(target=loop.start, daemon=True)
    thread.start()

    # Let it run for 1 minute
    time.sleep(60)

    # Stop
    loop.running = False
    thread.join(timeout=5)

    # Verify it ran multiple cycles
    assert loop.roadmap_cache is not None


def test_crash_recovery():
    """Test that orchestrator recovers from crash."""
    config = WorkLoopConfig(state_file_path="test_state.json")

    # Run first instance
    loop1 = ContinuousWorkLoop(config)
    loop1.current_state = {
        "active_tasks": {
            "spec_20": {"task_id": "abc-123", "started_at": time.time()}
        }
    }
    loop1._save_state()

    # Simulate crash (instance stops)
    del loop1

    # Start second instance (recovery)
    loop2 = ContinuousWorkLoop(config)
    loop2._load_state()

    # State should be restored
    assert "spec_20" in loop2.current_state["active_tasks"]
```

---

## Security Considerations

### 1. File System Access

**Risk**: Orchestrator reads/writes multiple files (ROADMAP, state, specs)

**Mitigation**:
- Validate all file paths (no directory traversal)
- Use `pathlib.Path.resolve()` to canonicalize paths
- Check file permissions before read/write
- Limit state file size (prevent disk exhaustion)

```python
def _safe_read_roadmap(self, roadmap_path: Path) -> str:
    """Safely read ROADMAP with validation."""
    # Resolve to absolute path
    abs_path = roadmap_path.resolve()

    # Check within project directory
    if not str(abs_path).startswith(str(Path.cwd())):
        raise SecurityError("ROADMAP path outside project directory")

    # Check file size (max 10MB)
    if abs_path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError("ROADMAP file too large (>10MB)")

    return abs_path.read_text()
```

### 2. Agent Isolation

**Risk**: Agents could interfere with each other's work

**Mitigation**:
- Use AgentRegistry singleton (US-035) to enforce one instance per agent
- Message bus provides isolation (pub/sub topics)
- State files use agent-specific namespaces

### 3. Error Propagation

**Risk**: Fatal errors crash entire orchestrator

**Mitigation**:
- Catch all exceptions in work cycle
- Separate fatal from non-fatal errors
- Graceful degradation (continue loop on non-fatal)
- Save state before exit

### 4. User Notification Security

**Risk**: Sensitive information in notifications

**Mitigation**:
- CFR-009 compliance: `sound=False` for background agents
- Sanitize error messages (no stack traces with secrets)
- Log sensitive data only to secure log files

---

## Performance Requirements

### Response Times

| Operation | Target | Acceptable | Unacceptable |
|-----------|--------|------------|--------------|
| **Poll ROADMAP** | <100ms | <500ms | >1s |
| **Parse ROADMAP** | <200ms | <1s | >2s |
| **Delegate Task** | <50ms | <200ms | >500ms |
| **Save State** | <100ms | <300ms | >1s |
| **Work Cycle** | <1s | <3s | >5s |

### Resource Limits

| Resource | Limit | Monitoring |
|----------|-------|------------|
| **CPU** | <5% (idle), <20% (active) | `psutil.cpu_percent()` |
| **Memory** | <100MB | `psutil.Process().memory_info()` |
| **Disk I/O** | <10 MB/hour | State file size tracking |
| **Network** | 0 (local only) | N/A |

### Scalability

| Metric | Current | Target (1 year) |
|--------|---------|-----------------|
| **ROADMAP Priorities** | 50-100 | 500+ |
| **Concurrent Tasks** | 2-3 | 10+ |
| **Work Loop Uptime** | Hours | Weeks/Months |

---

## Risk Analysis

### High Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **ROADMAP Parsing Breaks** | Work loop stops | Medium | - Robust regex patterns<br>- Fallback to previous cache<br>- User notification |
| **Message Bus Failure** | All delegation stops | Low | - SQLite persistence<br>- Automatic recovery<br>- State preservation |
| **Infinite Loop (No Work)** | CPU waste | Medium | - Sleep 5 minutes when idle<br>- Detect no-work condition<br>- Graceful idle mode |

### Medium Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Spec Backlog Overflow** | Too many specs created | Low | - Limit backlog to 3<br>- Check code_developer capacity |
| **Task Timeout False Positives** | Valid tasks canceled | Medium | - 2-hour timeout (generous)<br>- Warn before cancel<br>- Manual override |

### Low Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **State File Corruption** | Lost progress | Low | - JSON validation on load<br>- Backup previous state<br>- Atomic writes |

---

## Success Criteria

### Functional Criteria

1. **✅ 24/7 Operation**
   - Orchestrator runs continuously for >7 days without restart
   - Automatic recovery from non-fatal errors
   - Graceful shutdown on interrupt

2. **✅ Zero Idle Time**
   - code_developer never waits for specs (>95% utilization)
   - architect maintains 2-3 spec backlog at all times
   - Work loop detects new priorities within 30 seconds

3. **✅ Proactive Spec Creation**
   - architect creates specs BEFORE code_developer needs them
   - Spec backlog maintained: 2-3 specs ahead
   - No blocking waits for spec creation

4. **✅ Error Recovery**
   - Non-fatal errors handled gracefully (loop continues)
   - Failed tasks retried up to 3 times
   - State preserved on crash (recovery on restart)

5. **✅ User Experience**
   - CFR-009 compliance: Silent operation (no sound alerts)
   - Critical errors notify user appropriately
   - Progress visible in ROADMAP status updates

### Performance Criteria

1. **✅ Work Cycle Performance**
   - Cycle time: <3 seconds (p95)
   - ROADMAP polling: <500ms (p95)
   - State save: <300ms (p95)

2. **✅ Resource Efficiency**
   - CPU: <5% idle, <20% active
   - Memory: <100MB
   - Disk I/O: <10 MB/hour

3. **✅ Scalability**
   - Handles 100+ priorities in ROADMAP
   - Supports 10+ concurrent tasks
   - Runs for weeks without restart

### Quality Criteria

1. **✅ Test Coverage**
   - Unit tests: >85% coverage
   - Integration tests: 10+ scenarios
   - End-to-end test: 24-hour continuous run

2. **✅ Code Quality**
   - Passes all pre-commit hooks (black, mypy, etc.)
   - Architect code review approved
   - CFR compliance verified (CFR-009, CFR-013)

3. **✅ Documentation**
   - CLAUDE.md updated with usage instructions
   - ADR-014 created (Continuous Work Loop)
   - ROADMAP.md updated (PRIORITY 20 ✅)

---

## Appendix A: CLI Usage

### Starting the Orchestrator

```bash
# Start continuous work loop (runs forever)
poetry run orchestrator start

# Start with custom config
poetry run orchestrator start --config custom_config.json

# Start in background (daemon mode)
nohup poetry run orchestrator start > orchestrator.log 2>&1 &
```

### Monitoring Progress

```bash
# Check orchestrator status
poetry run orchestrator status

# View recent notifications
poetry run project-manager notifications --agent orchestrator

# Check ROADMAP progress
cat docs/roadmap/ROADMAP.md | grep "📝\|🔄\|✅"
```

### Stopping the Orchestrator

```bash
# Graceful shutdown (Ctrl+C)
# Press Ctrl+C in terminal where orchestrator is running

# Force stop (if Ctrl+C doesn't work)
pkill -TERM -f "orchestrator start"
```

---

## Appendix B: Configuration Options

### WorkLoopConfig

```python
@dataclass
class WorkLoopConfig:
    """Configuration for continuous work loop."""

    # How often to poll ROADMAP.md for changes (seconds)
    poll_interval_seconds: int = 30

    # How many specs to keep ahead of code_developer
    spec_backlog_target: int = 3

    # Maximum retry attempts for failed tasks
    max_retry_attempts: int = 3

    # Task timeout (seconds) - 2 hours default
    task_timeout_seconds: int = 7200

    # State file path (for crash recovery)
    state_file_path: str = "data/orchestrator/work_loop_state.json"

    # Enable sound notifications (CFR-009: should be False)
    enable_sound_notifications: bool = False
```

### Custom Config Example

```json
{
  "poll_interval_seconds": 60,
  "spec_backlog_target": 5,
  "max_retry_attempts": 5,
  "task_timeout_seconds": 10800,
  "state_file_path": "/custom/path/state.json",
  "enable_sound_notifications": false
}
```

---

## Appendix C: Troubleshooting

### Issue: Work loop stops after a few cycles

**Symptoms**: Orchestrator exits unexpectedly

**Possible Causes**:
- Fatal error in work cycle
- ROADMAP.md missing or corrupted
- Message bus failure

**Solution**:
1. Check error log: `data/orchestrator/error_recovery.log`
2. Verify ROADMAP exists: `ls docs/roadmap/ROADMAP.md`
3. Check state file: `cat data/orchestrator/work_loop_state.json`
4. Restart orchestrator with verbose logging: `poetry run orchestrator start --verbose`

---

### Issue: code_developer not starting implementation

**Symptoms**: Specs created but implementation doesn't start

**Possible Causes**:
- Spec path not detected correctly
- code_developer agent not running
- Task submission failing

**Solution**:
1. Check if spec exists: `ls docs/architecture/specs/SPEC-*`
2. Verify code_developer registered: `poetry run project-manager agents`
3. Check message bus queue: `poetry run orchestrator status --queue`
4. Manual delegation: `poetry run orchestrator delegate --agent code_developer --priority 20`

---

### Issue: High CPU usage

**Symptoms**: Orchestrator consuming >50% CPU

**Possible Causes**:
- Poll interval too short (thrashing)
- Infinite loop without sleep
- Message bus queue overflow

**Solution**:
1. Check config: `poll_interval_seconds` should be ≥30
2. Monitor work cycle time: Should be <3s
3. Check active tasks: `poetry run orchestrator status --tasks`
4. Restart with longer poll interval: `--config {"poll_interval_seconds": 60}`

---

**End of Specification**

---

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/continuous_work_loop.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/architect_coordinator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/orchestrator/code_developer_coordinator.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/cli/orchestrator_cli.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/unit/test_continuous_work_loop.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/integration/test_orchestrator_work_loop.py`

**Next Steps**:
1. Review and approve this specification
2. Create ADR-014: Continuous Work Loop Architecture Decision
3. Assign implementation to code_developer (PRIORITY 20)
4. Begin Phase 1 implementation (Core Infrastructure)
