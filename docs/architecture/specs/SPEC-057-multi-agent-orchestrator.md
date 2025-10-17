# SPEC-057: Multi-Agent Orchestrator

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**:
- Strategic spec: docs/roadmap/US_057_MULTI_AGENT_ORCHESTRATOR.md
- CFR-000: Prevent File Conflicts at All Costs
- CFR-011: Architect Proactive Spec Creation
- CFR-012: Agent Responsiveness Priority
- CFR-013: All Agents Must Work on roadmap Branch Only
- US-035: Agent Singleton Enforcement
- US-056: Enforce CFR-013 (Daemon on roadmap branch only)

---

## Executive Summary

Transform the current single-agent `code_developer` daemon into a **Multi-Agent Orchestrator** that launches and manages ALL six agents working simultaneously in parallel processes as a coordinated autonomous team.

**Key Transformation**:
```
CURRENT: Single agent (code_developer only) → Sequential execution
FUTURE: Six agents in parallel → 3-6x speedup through simultaneous work
```

**Expected Impact**:
- 3-6x speedup in priority completion (from 6-9 hours to 2-3 hours)
- Zero blocking (architect creates specs ahead of code_developer)
- Continuous QA (assistant demos automatically within 30 minutes)
- Real-time monitoring (project_manager tracks GitHub continuously)
- Weekly code quality improvements (code-searcher + architect collaboration)

---

## Problem Statement

### Current Bottleneck: Sequential Execution

Today's daemon architecture creates artificial bottlenecks by executing work sequentially:

```
SEQUENTIAL (Current):
┌─────────────────────────────────────────────┐
│  code_developer daemon                      │
│                                             │
│  [1. Wait for spec] ──► ⏰ 2 hours          │
│         │                                   │
│         ▼                                   │
│  [2. Implement] ────► ⏰ 4 hours            │
│         │                                   │
│         ▼                                   │
│  [3. Wait for demo] ─► ⏰ 1 hour            │
│         │                                   │
│         ▼                                   │
│  [4. Fix bug] ───────► ⏰ 2 hours           │
│                                             │
│  Total Time: 9 hours                        │
└─────────────────────────────────────────────┘

PARALLEL (Proposed):
┌─────────────────────────────────────────────┐
│  Multi-Agent Orchestrator                   │
│                                             │
│  [architect] ────────► Creating specs       │ ⏰ Concurrent
│  [code_developer] ───► Implementing         │ ⏰ Concurrent
│  [assistant] ────────► Creating demos       │ ⏰ Concurrent
│  [project_manager] ──► Monitoring GitHub    │ ⏰ Concurrent
│  [code-searcher] ────► Analyzing codebase   │ ⏰ Concurrent
│  [ux-design-expert] ─► Reviewing UI/UX      │ ⏰ Concurrent
│                                             │
│  All running simultaneously!                │
│  Total Time: 4 hours (2.25x faster)         │
└─────────────────────────────────────────────┘
```

### Pain Points

1. **Spec Creation Blocking**: code_developer waits for architect (CFR-011 violation)
2. **No Continuous QA**: assistant only runs when manually requested
3. **Reactive Monitoring**: project_manager only checks when user asks
4. **Missed Insights**: code-searcher analysis doesn't inform architecture
5. **Design Feedback Lag**: ux-design-expert consulted too late

---

## Proposed Solution

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────┐
│              AutonomousTeamOrchestrator                   │
│                    (Parent Process)                        │
│                                                           │
│  Responsibilities:                                        │
│  • Launch 6 agent subprocesses                           │
│  • Monitor health (heartbeat checking)                   │
│  • Restart crashed agents                                │
│  • Coordinate graceful shutdown                          │
│  • Enforce CFR-013 (roadmap branch only)                 │
│                                                           │
└─────┬─────┬─────┬─────┬─────┬─────┬────────────────────┘
      │     │     │     │     │     │
      ▼     ▼     ▼     ▼     ▼     ▼
    ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
    │ A │ │ C │ │ P │ │ A │ │ C │ │ U │  Agent Processes
    │ R │ │ D │ │ M │ │ S │ │ S │ │ X │
    │ C │ │ E │ │ A │ │ S │ │ E │ │   │
    │ H │ │ V │ │ N │ │ T │ │ A │ │ D │
    │ I │ │   │ │ A │ │   │ │ R │ │ E │
    │ T │ │   │ │ G │ │   │ │ C │ │ S │
    │ E │ │   │ │ R │ │   │ │ H │ │ I │
    │ C │ │   │ │   │ │   │ │   │ │ G │
    │ T │ │   │ │   │ │   │ │   │ │ N │
    └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘ └─┬─┘
      │     │     │     │     │     │
      └─────┴─────┴─────┴─────┴─────┘
                  │
                  ▼
        ┌─────────────────────┐
        │  Shared State       │
        │  (File-Based IPC)   │
        │                     │
        │  • Status Files     │
        │  • Message Queues   │
        │  • Work Coordination│
        └─────────────────────┘

Legend:
  ARCHITECT    - Proactive spec creation (CFR-011)
  CDEV         - Implementation execution
  PMANAGR      - GitHub monitoring, DoD verification
  ASST         - Demo creation, bug reporting
  CSEARCH      - Weekly code analysis
  UXDESIGN     - Design reviews and guidance
```

### Process Model

**Parent Orchestrator Process**:
- PID: 1000 (example)
- Spawns 6 child processes
- Monitors health via status files
- Restarts crashed children
- Coordinates shutdown

**Child Agent Processes**:
- Each agent runs in separate Python subprocess
- Independent work loops with CFR-012 interruption
- Communicates via file-based messaging
- Writes heartbeat status every 30 seconds
- Enforces CFR-013 (roadmap branch only)

### Inter-Process Communication (IPC)

**File-Based Messaging** (Why: Simple, observable, debuggable, no network ports):

```
data/
├── agent_status/              # Heartbeat and current state
│   ├── architect_status.json
│   ├── code_developer_status.json
│   ├── project_manager_status.json
│   ├── assistant_status.json
│   ├── code_searcher_status.json
│   └── ux_design_expert_status.json
│
└── agent_messages/            # Inter-agent delegation
    ├── architect_inbox/
    │   └── spec_request_20251017_103000.json
    ├── code_developer_inbox/
    │   └── bug_fix_20251017_103100.json
    ├── project_manager_inbox/
    │   └── bug_report_20251017_103200.json
    ├── assistant_inbox/
    │   └── demo_request_20251017_103300.json
    ├── code_searcher_inbox/
    │   └── analysis_request_20251017_103400.json
    └── ux_design_expert_inbox/
        └── design_review_20251017_103500.json
```

**Status File Format**:
```json
{
  "agent_type": "architect",
  "state": "working",
  "current_task": {
    "type": "spec_creation",
    "priority": "US-060",
    "started_at": "2025-10-17T10:30:00",
    "progress": 0.6,
    "estimated_completion": "2025-10-17T11:30:00"
  },
  "last_heartbeat": "2025-10-17T10:45:00",
  "next_check": "2025-10-17T11:45:00",
  "health": "healthy",
  "pid": 12345,
  "metrics": {
    "specs_created_today": 2,
    "specs_pending": 1,
    "work_items_completed": 5
  }
}
```

**Message Format**:
```json
{
  "message_id": "msg_20251017_103000_001",
  "from": "code_developer",
  "to": "assistant",
  "type": "demo_request",
  "priority": "normal",
  "timestamp": "2025-10-17T10:32:00",
  "content": {
    "feature": "US-045",
    "title": "Daemon delegates spec creation to architect",
    "acceptance_criteria": [
      "Daemon detects missing spec",
      "Daemon notifies architect",
      "Architect creates spec"
    ],
    "context": "Feature completed, needs visual demo"
  },
  "expires_at": "2025-10-17T18:00:00"
}
```

---

## Component Design

### 1. AutonomousTeamOrchestrator (Parent Process)

**File**: `coffee_maker/autonomous/orchestrator.py`

**Responsibilities**:
- Launch all 6 agent subprocesses
- Monitor agent health (heartbeat checking every 30 seconds)
- Restart crashed agents (with exponential backoff)
- Coordinate graceful shutdown (SIGTERM to all children)
- Enforce CFR-013 at orchestrator level

**Class Structure**:

```python
class AutonomousTeamOrchestrator:
    """Multi-agent orchestrator managing parallel team execution.

    This orchestrator launches ALL six agents in separate subprocesses and
    coordinates their work through file-based messaging and status tracking.

    Architecture:
        - Parent orchestrator process (this class)
        - 6 child agent processes (architect, code_developer, etc.)
        - File-based IPC (status files + message queues)
        - Health monitoring with automatic restart
        - CFR-013 enforcement (all on roadmap branch)

    Attributes:
        agents: Dictionary mapping AgentType to agent configuration
        processes: Dictionary mapping AgentType to subprocess.Process
        status_dir: Directory for agent status files (data/agent_status/)
        message_dir: Directory for inter-agent messages (data/agent_messages/)
        running: Boolean flag for orchestrator state
        restart_policy: Configuration for crash recovery
    """

    def __init__(
        self,
        status_dir: Path = Path("data/agent_status"),
        message_dir: Path = Path("data/agent_messages"),
        max_restarts_per_agent: int = 3,
        restart_backoff: float = 60.0,  # seconds
    ):
        """Initialize orchestrator with configuration."""
        self.status_dir = Path(status_dir)
        self.message_dir = Path(message_dir)
        self.max_restarts = max_restarts_per_agent
        self.restart_backoff = restart_backoff

        # Create directories
        self.status_dir.mkdir(parents=True, exist_ok=True)
        self.message_dir.mkdir(parents=True, exist_ok=True)

        # Agent configurations
        self.agents = self._initialize_agent_configs()

        # Process tracking
        self.processes: Dict[AgentType, Process] = {}
        self.restart_counts: Dict[AgentType, int] = {}
        self.last_restart: Dict[AgentType, datetime] = {}

        # State
        self.running = False
        self.start_time = None

        # Git manager for CFR-013 enforcement
        self.git = GitManager()

    def _initialize_agent_configs(self) -> Dict[AgentType, Dict]:
        """Initialize configurations for all agents."""
        return {
            AgentType.ARCHITECT: {
                "name": "architect",
                "module": "coffee_maker.autonomous.agents.architect_agent",
                "class": "ArchitectAgent",
                "check_interval": 3600,  # 1 hour
                "priority": 1,  # High priority (creates specs first)
            },
            AgentType.CODE_DEVELOPER: {
                "name": "code_developer",
                "module": "coffee_maker.autonomous.agents.code_developer_agent",
                "class": "CodeDeveloperAgent",
                "check_interval": 300,  # 5 minutes
                "priority": 2,  # Normal priority (waits for specs)
            },
            AgentType.PROJECT_MANAGER: {
                "name": "project_manager",
                "module": "coffee_maker.autonomous.agents.project_manager_agent",
                "class": "ProjectManagerAgent",
                "check_interval": 900,  # 15 minutes
                "priority": 3,  # Background monitoring
            },
            AgentType.ASSISTANT: {
                "name": "assistant",
                "module": "coffee_maker.autonomous.agents.assistant_agent",
                "class": "AssistantAgent",
                "check_interval": 1800,  # 30 minutes
                "priority": 3,  # Background demos
            },
            AgentType.CODE_SEARCHER: {
                "name": "code_searcher",
                "module": "coffee_maker.autonomous.agents.code_searcher_agent",
                "class": "CodeSearcherAgent",
                "check_interval": 86400,  # 24 hours (daily)
                "priority": 4,  # Low priority (weekly analysis)
            },
            AgentType.UX_DESIGN_EXPERT: {
                "name": "ux_design_expert",
                "module": "coffee_maker.autonomous.agents.ux_design_expert_agent",
                "class": "UXDesignExpertAgent",
                "check_interval": 3600,  # 1 hour
                "priority": 4,  # Low priority (reactive reviews)
            },
        }

    def run(self):
        """Launch all agents and monitor their execution.

        This method:
        1. Enforces CFR-013 (roadmap branch only)
        2. Launches all 6 agent subprocesses
        3. Monitors health continuously
        4. Restarts crashed agents
        5. Coordinates graceful shutdown
        """
        logger.info("🚀 Starting Autonomous Team Orchestrator...")

        # CFR-013: Ensure we're on roadmap branch before starting
        self._enforce_cfr_013()

        # Launch all agents
        self._launch_all_agents()

        # Monitor health loop
        self.running = True
        self.start_time = datetime.now()

        try:
            while self.running:
                # Check agent health
                self._check_agent_health()

                # Handle crashed agents
                self._handle_crashed_agents()

                # Sleep before next check
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logger.info("\n⏹️  Orchestrator stopped by user")
        finally:
            self._shutdown_all_agents()

    def _enforce_cfr_013(self):
        """Ensure orchestrator is on roadmap branch (CFR-013).

        Raises:
            CFR013ViolationError: If not on roadmap branch
        """
        current_branch = self.git.get_current_branch()

        if current_branch != "roadmap":
            raise CFR013ViolationError(
                f"CFR-013 VIOLATION: Orchestrator not on roadmap branch!\n\n"
                f"Current branch: {current_branch}\n"
                f"Required branch: roadmap\n\n"
                f"ALL agents MUST work on roadmap branch only.\n"
                f"Run: git checkout roadmap"
            )

        logger.info("✅ CFR-013 verified: On roadmap branch")

    def _launch_all_agents(self):
        """Launch all agent subprocesses in priority order."""
        # Sort by priority (lower number = higher priority)
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: x[1]["priority"]
        )

        for agent_type, config in sorted_agents:
            self._launch_agent(agent_type, config)
            time.sleep(1)  # Stagger launches slightly

    def _launch_agent(self, agent_type: AgentType, config: Dict):
        """Launch a single agent subprocess.

        Args:
            agent_type: Type of agent to launch
            config: Agent configuration dictionary
        """
        try:
            # Create agent process
            process = Process(
                target=self._agent_runner,
                args=(agent_type, config),
                name=f"agent_{config['name']}"
            )

            process.start()
            self.processes[agent_type] = process
            self.restart_counts[agent_type] = 0

            logger.info(
                f"✅ {config['name']} started "
                f"(PID: {process.pid}, Priority: {config['priority']})"
            )

        except Exception as e:
            logger.error(f"❌ Failed to launch {config['name']}: {e}")

    def _agent_runner(self, agent_type: AgentType, config: Dict):
        """Target function for agent subprocess.

        This function runs in the child process and:
        1. Registers agent in singleton registry (CFR-000)
        2. Enforces CFR-013 (roadmap branch only)
        3. Runs agent's continuous work loop
        4. Handles cleanup on exit

        Args:
            agent_type: Type of agent
            config: Agent configuration
        """
        try:
            # Import agent class dynamically
            module = __import__(config["module"], fromlist=[config["class"]])
            agent_class = getattr(module, config["class"])

            # Create agent instance
            agent = agent_class(
                status_dir=self.status_dir,
                message_dir=self.message_dir,
                check_interval=config["check_interval"]
            )

            # Register agent (CFR-000 singleton enforcement)
            with AgentRegistry.register(agent_type):
                logger.info(f"✅ {config['name']} registered in singleton registry")

                # Run agent's continuous loop
                agent.run_continuous()

        except AgentAlreadyRunningError as e:
            logger.error(f"❌ {config['name']} already running: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ {config['name']} crashed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _check_agent_health(self):
        """Monitor agent health via status files and process liveness."""
        for agent_type, process in list(self.processes.items()):
            config = self.agents[agent_type]
            status_file = self.status_dir / f"{config['name']}_status.json"

            # Check process is alive
            if not process.is_alive():
                logger.error(f"❌ {config['name']} process died (PID: {process.pid})")
                continue

            # Check status file exists and is recent
            if status_file.exists():
                try:
                    status = json.loads(status_file.read_text())
                    last_heartbeat = datetime.fromisoformat(status["last_heartbeat"])
                    age_seconds = (datetime.now() - last_heartbeat).total_seconds()

                    # Warn if heartbeat stale (>5 minutes)
                    if age_seconds > 300:
                        logger.warning(
                            f"⚠️  {config['name']} heartbeat stale "
                            f"({age_seconds:.0f}s old)"
                        )

                except Exception as e:
                    logger.error(f"Error reading status for {config['name']}: {e}")

    def _handle_crashed_agents(self):
        """Restart crashed agents with exponential backoff."""
        for agent_type, process in list(self.processes.items()):
            if not process.is_alive():
                config = self.agents[agent_type]

                # Check restart limit
                if self.restart_counts[agent_type] >= self.max_restarts:
                    logger.critical(
                        f"🚨 {config['name']} reached max restarts "
                        f"({self.max_restarts}) - NOT restarting"
                    )
                    continue

                # Check backoff period
                if agent_type in self.last_restart:
                    time_since_restart = (
                        datetime.now() - self.last_restart[agent_type]
                    ).total_seconds()

                    if time_since_restart < self.restart_backoff:
                        logger.info(
                            f"⏳ {config['name']} backoff in progress "
                            f"({time_since_restart:.0f}s / {self.restart_backoff}s)"
                        )
                        continue

                # Restart agent
                logger.warning(f"🔄 Restarting {config['name']}...")
                self._launch_agent(agent_type, config)
                self.restart_counts[agent_type] += 1
                self.last_restart[agent_type] = datetime.now()

    def _shutdown_all_agents(self):
        """Gracefully shutdown all agent subprocesses."""
        logger.info("🛑 Shutting down all agents...")

        for agent_type, process in self.processes.items():
            config = self.agents[agent_type]

            if process.is_alive():
                logger.info(f"Stopping {config['name']}...")
                process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                process.join(timeout=10)

                if process.is_alive():
                    logger.warning(f"Force killing {config['name']}...")
                    process.kill()
                    process.join()

        logger.info("✅ All agents stopped")
```

### 2. BaseAgent (Base Class for All Agents)

**File**: `coffee_maker/autonomous/agents/base_agent.py`

**Responsibilities**:
- Provide common infrastructure for all agents
- Enforce CFR-013 (roadmap branch only)
- Implement CFR-012 (interruption handling)
- Status file writing (heartbeat)
- Message queue management (inbox checking)
- Git operations with branch validation

**Class Structure**:

```python
class BaseAgent(ABC):
    """Abstract base class for all autonomous agents.

    This class provides common infrastructure that ALL agents must have:
    - CFR-013 enforcement (roadmap branch only)
    - CFR-012 interruption handling (urgent requests first)
    - Status file writing (heartbeat every 30 seconds)
    - Message queue management (inbox for inter-agent delegation)
    - Git operations with branch validation

    All agents inherit from this base and implement:
    - _do_background_work(): Main continuous work loop
    - _handle_message(msg): Process inter-agent messages

    Attributes:
        agent_type: Type of this agent (from AgentType enum)
        status_dir: Directory for status files
        message_dir: Directory for message queues
        check_interval: Seconds between background work checks
        git: GitManager instance for git operations
        status_file: Path to this agent's status file
        inbox_dir: Path to this agent's message inbox
    """

    def __init__(
        self,
        agent_type: AgentType,
        status_dir: Path,
        message_dir: Path,
        check_interval: int,
    ):
        """Initialize base agent."""
        self.agent_type = agent_type
        self.status_dir = Path(status_dir)
        self.message_dir = Path(message_dir)
        self.check_interval = check_interval

        # Git manager for CFR-013 enforcement
        self.git = GitManager()

        # Status tracking
        self.status_file = self.status_dir / f"{agent_type.value}_status.json"
        self.current_task = None
        self.metrics = {}

        # Message queue
        self.inbox_dir = self.message_dir / f"{agent_type.value}_inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.running = False
        self.last_heartbeat = None

        logger.info(f"{agent_type.value} initialized")

    def run_continuous(self):
        """Main continuous work loop with CFR-012 interruption handling.

        This method implements the core agent execution pattern:

        1. CFR-012: Check for urgent requests (PRIORITY 1)
           - User requests via user_listener
           - Inter-agent delegation messages

        2. Background work (PRIORITY 2)
           - Agent-specific continuous tasks
           - Implemented by subclass in _do_background_work()

        3. Heartbeat writing (every iteration)
           - Status file with current task, metrics, health

        4. Sleep between iterations
           - Duration determined by check_interval
        """
        self.running = True
        logger.info(f"🤖 {self.agent_type.value} starting continuous loop...")

        # CFR-013: Validate we're on roadmap branch
        self._enforce_cfr_013()

        while self.running:
            try:
                # CFR-012: Check for urgent messages FIRST
                urgent_message = self._check_inbox_urgent()
                if urgent_message:
                    logger.info(
                        f"🚨 {self.agent_type.value} interrupted by urgent message"
                    )
                    self._handle_message(urgent_message)
                    continue  # Skip background work this iteration

                # Normal priority: Check for regular messages
                messages = self._check_inbox()
                for message in messages:
                    self._handle_message(message)

                # Background work (agent-specific)
                self._do_background_work()

                # Write status (heartbeat)
                self._write_status()

                # Sleep before next iteration
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info(f"\n⏹️  {self.agent_type.value} stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ {self.agent_type.value} error: {e}")
                import traceback
                traceback.print_exc()

                # Write error status
                self._write_status(error=str(e))

                # Sleep before retry
                time.sleep(60)

        logger.info(f"🛑 {self.agent_type.value} stopped")

    def _enforce_cfr_013(self):
        """Ensure agent is on roadmap branch (CFR-013).

        Raises:
            CFR013ViolationError: If not on roadmap branch
        """
        current_branch = self.git.get_current_branch()

        if current_branch != "roadmap":
            raise CFR013ViolationError(
                f"CFR-013 VIOLATION: {self.agent_type.value} not on roadmap branch!\n\n"
                f"Current branch: {current_branch}\n"
                f"Required branch: roadmap\n\n"
                f"ALL agents MUST work on roadmap branch only.\n"
                f"Run: git checkout roadmap"
            )

    def _check_inbox_urgent(self) -> Optional[Dict]:
        """Check inbox for URGENT messages only (CFR-012 Priority 1).

        Returns:
            Urgent message dict if found, None otherwise
        """
        for msg_file in self.inbox_dir.glob("urgent_*.json"):
            try:
                message = json.loads(msg_file.read_text())
                msg_file.unlink()  # Remove after reading
                return message
            except Exception as e:
                logger.error(f"Error reading urgent message {msg_file}: {e}")

        return None

    def _check_inbox(self) -> List[Dict]:
        """Check inbox for regular messages.

        Returns:
            List of message dictionaries
        """
        messages = []

        for msg_file in self.inbox_dir.glob("*.json"):
            # Skip urgent messages (handled by _check_inbox_urgent)
            if msg_file.name.startswith("urgent_"):
                continue

            try:
                message = json.loads(msg_file.read_text())
                messages.append(message)
                msg_file.unlink()  # Remove after reading
            except Exception as e:
                logger.error(f"Error reading message {msg_file}: {e}")

        return messages

    def _write_status(self, error: Optional[str] = None):
        """Write status file with current state (heartbeat).

        Args:
            error: Optional error message if agent encountered error
        """
        status = {
            "agent_type": self.agent_type.value,
            "state": "error" if error else ("working" if self.current_task else "idle"),
            "current_task": self.current_task,
            "last_heartbeat": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(seconds=self.check_interval)).isoformat(),
            "health": "unhealthy" if error else "healthy",
            "pid": os.getpid(),
            "metrics": self.metrics,
            "error": error,
        }

        try:
            self.status_file.write_text(json.dumps(status, indent=2))
            self.last_heartbeat = datetime.now()
        except Exception as e:
            logger.error(f"Error writing status: {e}")

    def commit_changes(self, message: str, files: Optional[List[str]] = None):
        """Commit changes with agent identification.

        Args:
            message: Commit message
            files: Optional list of specific files to commit (default: all changes)
        """
        # CFR-013: Ensure still on roadmap branch before commit
        self._enforce_cfr_013()

        # Agent identification in commit message
        full_message = (
            f"{message}\n\n"
            f"🤖 Agent: {self.agent_type.value}\n"
            f"🤖 Generated with Claude Code\n\n"
            f"Co-Authored-By: Claude <noreply@anthropic.com>"
        )

        # Commit changes
        if files:
            for file_path in files:
                self.git.add(file_path)
        else:
            self.git.add_all()

        self.git.commit(full_message)

        # Push to roadmap branch
        self.git.push("roadmap")

        logger.info(f"✅ {self.agent_type.value} committed: {message}")

    @abstractmethod
    def _do_background_work(self):
        """Perform agent-specific background work.

        This method is called once per iteration and should implement
        the agent's continuous work loop logic.

        Subclasses MUST implement this method.

        Example for architect:
            - Check ROADMAP for spec coverage
            - Create missing specs proactively
            - Read code-searcher reports
            - Analyze codebase for refactoring opportunities

        Example for code_developer:
            - Check ROADMAP for next priority
            - Implement if spec exists
            - Run tests
            - Commit changes
        """
        raise NotImplementedError("Subclasses must implement _do_background_work()")

    @abstractmethod
    def _handle_message(self, message: Dict):
        """Handle inter-agent delegation message.

        Args:
            message: Message dictionary with:
                - from: Sending agent type
                - to: This agent (recipient)
                - type: Message type (spec_request, demo_request, etc.)
                - priority: "urgent" or "normal"
                - content: Message-specific payload

        Subclasses MUST implement this method to handle delegation.
        """
        raise NotImplementedError("Subclasses must implement _handle_message()")
```

### 3. Agent Implementations

Each agent inherits from `BaseAgent` and implements:
- `_do_background_work()`: Continuous work loop
- `_handle_message()`: Inter-agent message handling

#### 3.1 ArchitectAgent

**File**: `coffee_maker/autonomous/agents/architect_agent.py`

**Continuous Work Loop**:
1. Check ROADMAP for spec coverage (CFR-011)
2. Create specs for next 3-5 priorities proactively
3. Read new code-searcher reports
4. Analyze codebase weekly for refactoring opportunities
5. Update spec coverage report

```python
class ArchitectAgent(BaseAgent):
    """Architect agent - Proactive technical specification creation.

    Responsibilities (CFR-011):
    - Create specs for next 3-5 priorities BEFORE code_developer needs them
    - Read code-searcher reports daily, integrate findings
    - Analyze codebase weekly for refactoring opportunities
    - Document architectural decisions in ADRs
    - Manage dependencies (with user approval)

    Continuous Loop:
    1. Morning: Check ROADMAP spec coverage
    2. Create missing specs (top priority)
    3. Read code-searcher reports
    4. Weekly: Analyze codebase directly
    5. Handle urgent spec requests (CFR-012)
    """

    def __init__(self, status_dir: Path, message_dir: Path, check_interval: int):
        super().__init__(
            agent_type=AgentType.ARCHITECT,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval
        )

        self.roadmap = RoadmapParser("docs/roadmap/ROADMAP.md")
        self.specs_dir = Path("docs/architecture/specs")
        self.last_analysis_date = None

    def _do_background_work(self):
        """Proactive spec creation and code quality analysis."""
        # CFR-011 Part 1: Proactive spec creation
        self._ensure_spec_coverage()

        # CFR-011 Part 2: Read code-searcher reports
        self._read_code_searcher_reports()

        # CFR-011 Part 3: Weekly codebase analysis
        if self._should_analyze_codebase():
            self._analyze_codebase()

    def _ensure_spec_coverage(self):
        """Ensure specs exist for next 3-5 priorities (CFR-011)."""
        self.current_task = {
            "type": "spec_coverage_check",
            "started_at": datetime.now().isoformat()
        }

        # Get upcoming priorities
        upcoming = self.roadmap.get_next_n_planned(5)

        # Check which ones have specs
        missing_specs = []
        for priority in upcoming:
            spec_file = self._find_spec(priority)
            if not spec_file:
                missing_specs.append(priority)

        # CFR-011 enforcement: More than 2 missing = violation
        if len(missing_specs) > 2:
            logger.warning(
                f"⚠️  CFR-011: {len(missing_specs)} specs missing "
                f"(target: max 2 missing)"
            )

        # Create missing specs proactively
        for priority in missing_specs[:3]:  # Create top 3
            self._create_technical_spec(priority)

        # Update metrics
        self.metrics["specs_created_today"] = self.metrics.get("specs_created_today", 0)
        self.metrics["spec_coverage"] = len(upcoming) - len(missing_specs)

    def _create_technical_spec(self, priority: Dict):
        """Create technical specification for a priority."""
        self.current_task = {
            "type": "spec_creation",
            "priority": priority["name"],
            "started_at": datetime.now().isoformat()
        }

        logger.info(f"📝 Creating spec for {priority['name']}...")

        # Load prompt template
        prompt = load_prompt(
            PromptNames.CREATE_TECHNICAL_SPEC,
            {
                "PRIORITY_NAME": priority["name"],
                "PRIORITY_TITLE": priority["title"],
                "PRIORITY_CONTEXT": priority.get("description", "")
            }
        )

        # Execute with Claude API
        claude = ClaudeAPI()
        result = claude.execute(prompt)

        # Spec is created by Claude directly in docs/architecture/specs/
        # We just need to commit it
        spec_file = self._find_spec(priority)
        if spec_file:
            self.commit_changes(
                f"docs: Add technical spec for {priority['name']}",
                files=[str(spec_file)]
            )

            self.metrics["specs_created_today"] += 1
            logger.info(f"✅ Spec created: {spec_file}")
        else:
            logger.error(f"❌ Spec creation failed for {priority['name']}")

    def _read_code_searcher_reports(self):
        """Read new code-searcher reports (CFR-011 Part 2)."""
        # Find new reports
        reports_dir = Path("docs")
        new_reports = []

        for report_file in reports_dir.glob("*_AUDIT_*.md"):
            # Check if we've read this report
            # (Implementation detail: track read reports in state file)
            if self._is_new_report(report_file):
                new_reports.append(report_file)

        for report_file in reports_dir.glob("*_ANALYSIS_*.md"):
            if self._is_new_report(report_file):
                new_reports.append(report_file)

        if new_reports:
            logger.info(f"📊 Reading {len(new_reports)} new code-searcher reports...")

            for report_file in new_reports:
                self._integrate_code_searcher_findings(report_file)
                self._mark_report_read(report_file)

    def _analyze_codebase(self):
        """Analyze codebase for refactoring opportunities (CFR-011 Part 3)."""
        self.current_task = {
            "type": "codebase_analysis",
            "started_at": datetime.now().isoformat()
        }

        logger.info("🔍 Analyzing codebase for refactoring opportunities...")

        # Analyze large files
        self._find_large_files()

        # Analyze complexity
        self._find_complex_modules()

        # Analyze duplication
        self._find_duplicate_code()

        self.last_analysis_date = datetime.now()

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages."""
        msg_type = message.get("type")

        if msg_type == "spec_request":
            # code_developer needs a spec urgently
            priority = message["content"]["priority"]
            self._create_technical_spec(priority)

        elif msg_type == "dependency_request":
            # code_developer needs a new dependency
            package = message["content"]["package"]
            self._evaluate_dependency(package)

        else:
            logger.warning(f"Unknown message type: {msg_type}")
```

#### 3.2 CodeDeveloperAgent

**File**: `coffee_maker/autonomous/agents/code_developer_agent.py`

**Continuous Work Loop**:
1. Sync with roadmap branch (CFR-013)
2. Get next planned priority
3. Check spec exists (should be ready due to architect!)
4. Implement priority
5. Run tests
6. Commit to roadmap branch
7. Notify assistant for demo

```python
class CodeDeveloperAgent(BaseAgent):
    """Code developer agent - Autonomous implementation execution.

    Responsibilities:
    - Implement priorities from ROADMAP (same as current daemon)
    - Stay on roadmap branch (CFR-013)
    - Frequent commits with agent identification
    - Notify assistant when features complete
    - Run tests before committing

    Continuous Loop:
    1. Sync with roadmap branch
    2. Get next planned priority
    3. Ensure spec exists (wait for architect if needed)
    4. Implement priority
    5. Run tests
    6. Commit changes
    7. Notify assistant for demo
    """

    def __init__(self, status_dir: Path, message_dir: Path, check_interval: int):
        super().__init__(
            agent_type=AgentType.CODE_DEVELOPER,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval
        )

        self.roadmap = RoadmapParser("docs/roadmap/ROADMAP.md")
        self.claude = ClaudeAPI()
        self.attempted_priorities = {}

    def _do_background_work(self):
        """Implement next planned priority."""
        # Sync with roadmap branch
        self.git.pull("roadmap")
        self.roadmap.reload()

        # Get next priority
        next_priority = self.roadmap.get_next_planned_priority()

        if not next_priority:
            logger.info("✅ No more planned priorities - all done!")
            return

        self.current_task = {
            "type": "implementation",
            "priority": next_priority["name"],
            "started_at": datetime.now().isoformat()
        }

        # Check spec exists
        spec_file = self._find_spec(next_priority)
        if not spec_file:
            logger.warning(f"⚠️  Spec missing for {next_priority['name']}")
            self._request_spec_from_architect(next_priority)
            return  # Wait for architect to create spec

        # Implement priority
        logger.info(f"⚙️  Implementing {next_priority['name']}...")

        success = self._implement_priority(next_priority, spec_file)

        if success:
            # Notify assistant to create demo
            self._notify_assistant_demo_needed(next_priority)

            # Update metrics
            self.metrics["priorities_completed"] = self.metrics.get("priorities_completed", 0) + 1
        else:
            logger.error(f"❌ Implementation failed for {next_priority['name']}")

    def _implement_priority(self, priority: Dict, spec_file: Path) -> bool:
        """Implement a priority using Claude API."""
        # Load implementation prompt
        prompt = load_prompt(
            PromptNames.IMPLEMENT_FEATURE,
            {
                "PRIORITY_NAME": priority["name"],
                "PRIORITY_TITLE": priority["title"],
                "SPEC_FILE": str(spec_file)
            }
        )

        # Execute with Claude
        result = self.claude.execute(prompt)

        # Run tests
        test_result = self._run_tests()
        if not test_result:
            logger.error("❌ Tests failed!")
            return False

        # Commit changes
        self.commit_changes(f"feat: Implement {priority['name']}")

        return True

    def _request_spec_from_architect(self, priority: Dict):
        """Send urgent message to architect requesting spec."""
        message = {
            "message_id": f"spec_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "from": "code_developer",
            "to": "architect",
            "type": "spec_request",
            "priority": "urgent",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "priority": priority,
                "reason": "Implementation blocked - spec missing"
            }
        }

        # Write to architect's inbox as URGENT
        architect_inbox = self.message_dir / "architect_inbox"
        msg_file = architect_inbox / f"urgent_{message['message_id']}.json"
        msg_file.write_text(json.dumps(message, indent=2))

        logger.info(f"📨 Sent urgent spec request to architect for {priority['name']}")

    def _notify_assistant_demo_needed(self, priority: Dict):
        """Notify assistant that feature is complete and needs demo."""
        message = {
            "message_id": f"demo_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "from": "code_developer",
            "to": "assistant",
            "type": "demo_request",
            "priority": "normal",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "feature": priority["name"],
                "title": priority["title"],
                "acceptance_criteria": priority.get("acceptance_criteria", [])
            }
        }

        # Write to assistant's inbox
        assistant_inbox = self.message_dir / "assistant_inbox"
        msg_file = assistant_inbox / f"{message['message_id']}.json"
        msg_file.write_text(json.dumps(message, indent=2))

        logger.info(f"📨 Notified assistant: demo needed for {priority['name']}")

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages."""
        msg_type = message.get("type")

        if msg_type == "bug_fix_request":
            # assistant found a bug during demo
            bug_info = message["content"]
            self._fix_bug(bug_info)

        else:
            logger.warning(f"Unknown message type: {msg_type}")
```

#### 3.3 ProjectManagerAgent

**File**: `coffee_maker/autonomous/agents/project_manager_agent.py`

**Continuous Work Loop**:
1. Monitor GitHub (PRs, issues, CI/CD)
2. Check ROADMAP health (stalled priorities)
3. Verify DoD when requested (not continuous)
4. Generate weekly status reports
5. Warn users about blockers proactively

#### 3.4 AssistantAgent

**File**: `coffee_maker/autonomous/agents/assistant_agent.py`

**Continuous Work Loop**:
1. Check for completed features without demos
2. Create visual demos with Puppeteer
3. Test features, detect bugs
4. Provide comprehensive bug reports to project_manager
5. Mark features verified when demos pass

#### 3.5 CodeSearcherAgent

**File**: `coffee_maker/autonomous/agents/code_searcher_agent.py`

**Continuous Work Loop**:
1. Weekly: Security audit
2. Weekly: Dependency analysis
3. Weekly: Code duplication detection
4. Daily: Recent commit pattern analysis
5. Present findings to assistant → project_manager

#### 3.6 UXDesignExpertAgent

**File**: `coffee_maker/autonomous/agents/ux_design_expert_agent.py`

**Continuous Work Loop**:
1. Review recent UI/UX changes
2. Analyze design quality
3. Provide proactive feedback
4. Answer design questions when delegated

---

## Data Structures

### AgentStatus

```python
@dataclass
class AgentStatus:
    """Agent status for health monitoring."""

    agent_type: AgentType
    state: str  # "idle", "working", "error"
    current_task: Optional[Dict]
    last_heartbeat: datetime
    next_check: datetime
    health: str  # "healthy", "unhealthy"
    pid: int
    metrics: Dict[str, int]
    error: Optional[str] = None
```

### AgentMessage

```python
@dataclass
class AgentMessage:
    """Inter-agent delegation message."""

    message_id: str
    from_agent: AgentType
    to_agent: AgentType
    type: str  # "spec_request", "demo_request", "bug_report", etc.
    priority: str  # "urgent", "normal"
    timestamp: datetime
    content: Dict
    expires_at: Optional[datetime] = None
```

### CoordinationState

```python
@dataclass
class CoordinationState:
    """Shared coordination state."""

    active_agents: List[AgentType]
    work_queue: List[Dict]  # Prioritized work items
    locks: Dict[str, AgentType]  # File locks: {file_path: owner}
    last_sync: datetime
```

---

## Implementation Plan

### Phase 1: Orchestrator Foundation (Days 1-3)

**Day 1: Core Orchestrator**
- Create `coffee_maker/autonomous/orchestrator.py`
- Implement `AutonomousTeamOrchestrator` class
- Multi-process launching with `multiprocessing.Process`
- Basic health monitoring (process liveness)
- Graceful shutdown logic

**Day 2: Agent Base Class**
- Create `coffee_maker/autonomous/agents/base_agent.py`
- Implement `BaseAgent` abstract class
- CFR-013 enforcement in base class
- CFR-012 interruption handling pattern
- Status file writing (heartbeat)
- Message queue management

**Day 3: Shared State Infrastructure**
- Create `data/agent_status/` directory structure
- Create `data/agent_messages/` directory structure
- Implement status file schema validation
- Implement message queue utilities
- Add error handling and logging

### Phase 2: Agent Migration (Days 4-8)

**Day 4-5: Migrate code_developer**
- Extract daemon logic into `CodeDeveloperAgent`
- Inherit from `BaseAgent`
- Implement `_do_background_work()` (same as current daemon)
- Implement `_handle_message()` for inter-agent messages
- Test in orchestrator (single agent)

**Day 6-7: Create architect Agent**
- Implement `ArchitectAgent` with CFR-011 logic
- Morning ROADMAP spec coverage check
- Proactive spec creation loop
- Daily code-searcher report reading
- Weekly codebase analysis
- Test in orchestrator (2 agents: architect + code_developer)

**Day 8: Create project_manager Agent**
- Implement `ProjectManagerAgent`
- GitHub monitoring loop (gh cli)
- ROADMAP health checks
- DoD verification on request (Puppeteer)
- Test in orchestrator (3 agents)

### Phase 3: Complete Agent Team (Days 9-10)

**Day 9: Create assistant Agent**
- Implement `AssistantAgent`
- Demo creation loop (Puppeteer)
- Bug detection and comprehensive reporting
- Feature verification tracking
- Test in orchestrator (4 agents)

**Day 10: Create remaining agents**
- Implement `CodeSearcherAgent` (weekly analysis)
- Implement `UXDesignExpertAgent` (reactive + proactive reviews)
- Test in orchestrator (all 6 agents)

### Phase 4: Coordination Layer (Days 11-12)

**Day 11: Inter-Agent Messaging**
- Implement message priority system (urgent vs normal)
- Implement message expiration
- Add message delivery confirmation
- Test agent-to-agent delegation flows

**Day 12: Health Monitoring & Recovery**
- Implement heartbeat staleness detection
- Implement automatic restart with exponential backoff
- Implement restart limits (max 3 per agent)
- Add crash history tracking
- Test crash recovery scenarios

### Phase 5: Testing & Documentation (Days 13-14)

**Day 13: Integration Testing**
- Test multi-agent coordination
- Test CFR-011 compliance (architect proactive)
- Test CFR-012 compliance (interruption handling)
- Test CFR-013 compliance (all on roadmap branch)
- Test crash recovery
- Performance benchmarks

**Day 14: Documentation & Deployment**
- Update `.claude/CLAUDE.md` with orchestrator architecture
- Update agent README files
- Create migration guide
- Update CFR document with CFR-014 (multi-agent rules)
- Deploy orchestrator

### Phase 6: Validation (Day 15)

**Day 15: 24-Hour Run Validation**
- Start orchestrator with all 6 agents
- Monitor for 24 hours
- Verify:
  - Zero crashes or automatic recovery
  - architect creates specs proactively (CFR-011)
  - assistant creates demos automatically
  - project_manager monitors continuously
  - All agents respect CFR-013
  - Zero file conflicts (CFR-000)
  - Priority completion time reduced by 50%

---

## Testing Strategy

### Unit Tests

**Test Files**:
- `tests/unit/orchestrator/test_orchestrator.py`
- `tests/unit/orchestrator/test_base_agent.py`
- `tests/unit/orchestrator/test_agent_messaging.py`

**Key Test Cases**:

```python
def test_orchestrator_launches_all_agents():
    """Test orchestrator launches all 6 agents."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()  # Non-blocking test mode

    assert len(orchestrator.processes) == 6
    assert all(p.is_alive() for p in orchestrator.processes.values())

def test_orchestrator_restarts_crashed_agent():
    """Test orchestrator restarts crashed agent."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Simulate crash
    architect_process = orchestrator.processes[AgentType.ARCHITECT]
    architect_process.terminate()

    # Wait for restart
    time.sleep(90)  # Backoff + restart

    # Verify restarted
    new_process = orchestrator.processes[AgentType.ARCHITECT]
    assert new_process.is_alive()
    assert new_process.pid != architect_process.pid

def test_agent_enforces_cfr_013():
    """Test agent enforces CFR-013 (roadmap branch only)."""
    # Switch to wrong branch
    git = GitManager()
    git.checkout("main")

    # Should raise violation when starting
    agent = ArchitectAgent(...)
    with pytest.raises(CFR013ViolationError):
        agent.run_continuous()

def test_agent_prioritizes_urgent_messages():
    """Test agent handles urgent messages first (CFR-012)."""
    agent = CodeDeveloperAgent(...)

    # Send urgent message
    urgent_msg = {
        "type": "bug_fix_request",
        "priority": "urgent",
        "content": {"bug_id": "BUG-001"}
    }
    agent._write_urgent_message(urgent_msg)

    # Agent should interrupt background work
    agent._check_inbox_urgent()
    # Verify urgent message handled first
```

### Integration Tests

**Test Files**:
- `tests/integration/orchestrator/test_multi_agent_coordination.py`

**Key Test Cases**:

```python
def test_architect_creates_spec_before_code_developer_needs_it():
    """Test architect creates specs proactively (CFR-011)."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Wait for architect to check ROADMAP and create specs
    time.sleep(3600)  # 1 hour

    # Verify specs created for upcoming priorities
    roadmap = RoadmapParser("docs/roadmap/ROADMAP.md")
    next_5 = roadmap.get_next_priorities(5)

    for priority in next_5:
        spec_path = f"docs/architecture/specs/SPEC-{priority['number']}.md"
        assert Path(spec_path).exists(), f"Spec missing for {priority['name']}"

def test_assistant_creates_demo_after_code_developer_completes():
    """Test assistant creates demo automatically."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Wait for code_developer to complete priority
    time.sleep(7200)  # 2 hours

    # Verify assistant created demo
    demo_log = Path("data/demos/US-057_demo.json")
    assert demo_log.exists()

    demo_data = json.loads(demo_log.read_text())
    assert demo_data["status"] in ["success", "bugs_found"]

def test_zero_file_conflicts_between_agents():
    """Test no file conflicts occur between agents (CFR-000)."""
    orchestrator = AutonomousTeamOrchestrator()
    orchestrator.run()

    # Run for 1 hour
    time.sleep(3600)

    # Check for git conflicts
    git = GitManager()
    status = git.status()
    assert "conflict" not in status.lower()

    # Check for file corruption
    # (Implementation: verify key files parse correctly)
    roadmap = RoadmapParser("docs/roadmap/ROADMAP.md")
    assert roadmap.is_valid()
```

### Performance Benchmarks

**Metrics to Track**:

1. **Priority Completion Time**
   - Baseline (sequential): 6-9 hours per priority
   - Target (parallel): 2-3 hours per priority (3x speedup)

2. **Spec Creation Lag**
   - Baseline (reactive): code_developer blocks 1-2 hours
   - Target (proactive): zero blocking (CFR-011)

3. **Demo Creation Time**
   - Baseline (manual): User requests → 1 hour delay
   - Target (automatic): 30 minutes after completion

4. **Bug Detection Time**
   - Baseline (manual): Days/weeks after release
   - Target (continuous): Within 1 hour of completion

5. **Code Quality Improvement**
   - Baseline: Ad-hoc refactoring
   - Target: Weekly code-searcher analysis → architect integration

---

## Error Handling & Resilience

### 1. Agent Crash Detection

**Mechanism**: Orchestrator monitors process liveness and heartbeat staleness

```python
def _check_agent_health(self):
    """Monitor agent health."""
    for agent_type, process in self.processes.items():
        # Check 1: Process alive
        if not process.is_alive():
            logger.error(f"❌ {agent_type} process died")
            self._mark_for_restart(agent_type)

        # Check 2: Heartbeat recent (<5 minutes)
        status = self._read_status(agent_type)
        if status:
            age = datetime.now() - status["last_heartbeat"]
            if age.total_seconds() > 300:
                logger.warning(f"⚠️  {agent_type} heartbeat stale")
                self._mark_for_restart(agent_type)
```

### 2. Automatic Restart with Exponential Backoff

**Mechanism**: Restart crashed agents with increasing delays

```python
def _restart_agent(self, agent_type: AgentType):
    """Restart crashed agent with exponential backoff."""
    restart_count = self.restart_counts[agent_type]

    # Check restart limit
    if restart_count >= self.max_restarts:
        logger.critical(f"🚨 {agent_type} max restarts reached - NOT restarting")
        self._notify_user_persistent_failure(agent_type)
        return

    # Calculate backoff delay
    backoff = self.restart_backoff * (2 ** restart_count)
    logger.info(f"⏳ Waiting {backoff}s before restarting {agent_type}...")
    time.sleep(backoff)

    # Launch new process
    self._launch_agent(agent_type, self.agents[agent_type])
    self.restart_counts[agent_type] += 1
    self.last_restart[agent_type] = datetime.now()
```

### 3. Graceful Degradation

**Principle**: If one agent fails, others continue working

**Example**:
- architect crashes → code_developer waits for specs but continues monitoring
- assistant crashes → demos paused but implementation continues
- code-searcher crashes → analysis paused but team continues

**Implementation**:
- Each agent is independent subprocess
- No shared state dependencies (file-based only)
- Clear fallback behaviors when dependencies unavailable

### 4. State Recovery After Crashes

**Mechanism**: Agents resume from status files

```python
def run_continuous(self):
    """Resume work from last status."""
    # Load previous state
    if self.status_file.exists():
        previous_status = json.loads(self.status_file.read_text())

        # Resume incomplete task if any
        if previous_status.get("current_task"):
            logger.info(f"Resuming task: {previous_status['current_task']}")
            self.current_task = previous_status["current_task"]

    # Continue normal loop
    while self.running:
        ...
```

### 5. Deadlock Detection & Resolution

**Potential Deadlock**: Agent A waits for Agent B, Agent B waits for Agent A

**Prevention Strategy**:
1. **No Synchronous Waiting**: Agents never block on other agents
2. **Message Timeouts**: Messages expire after reasonable time
3. **Priority System**: CFR-012 ensures urgent messages processed
4. **Fallback Behaviors**: If dependency unavailable, skip and continue

**Example**:
```python
# ❌ BAD: Synchronous waiting (deadlock risk)
def _implement_priority(self, priority):
    while not spec_exists(priority):
        wait_for_architect()  # BLOCKS FOREVER if architect crashes

    implement(priority)

# ✅ GOOD: Asynchronous with timeout
def _implement_priority(self, priority):
    if not spec_exists(priority):
        self._request_spec_from_architect(priority)
        return  # Skip this iteration, will retry next time

    implement(priority)
```

---

## Migration Path

### Strategy: Gradual Rollout (Recommended)

**Week 1: Orchestrator + 2 Agents**
```bash
poetry run orchestrator --agents=architect,code_developer
```
- Validate basic multi-agent coordination
- Verify CFR-011 (architect proactive spec creation)
- Verify CFR-013 (both on roadmap branch)
- Verify zero file conflicts

**Week 2: Add assistant**
```bash
poetry run orchestrator --agents=architect,code_developer,assistant
```
- Validate demo creation workflow
- Verify bug reporting to project_manager
- Measure demo creation lag (<30 minutes)

**Week 3: Add project_manager**
```bash
poetry run orchestrator --agents=architect,code_developer,assistant,project_manager
```
- Validate GitHub monitoring
- Verify DoD verification workflow
- Measure monitoring coverage

**Week 4: Full Team**
```bash
poetry run orchestrator  # All 6 agents
```
- Add code-searcher and ux-design-expert
- Validate full team coordination
- Measure overall speedup (target: 3x)
- Run 24-hour validation

### Backward Compatibility

**Legacy Mode**: Keep current daemon as fallback

```bash
# Old way (single agent) - DEPRECATED but available
poetry run code-developer --auto-approve

# New way (multi-agent) - RECOMMENDED
poetry run orchestrator --auto-approve
```

**Why Keep Legacy**:
- Fallback if orchestrator has issues
- Easier debugging (single agent simpler)
- Gradual user adoption

**Deprecation Timeline**:
- Week 1-4: Both modes available
- Week 5: Orchestrator becomes default
- Week 6+: Legacy mode removed if orchestrator stable

### CLI Interface

```bash
# Start full team
poetry run orchestrator

# Start specific agents only
poetry run orchestrator --agents=architect,code_developer

# View agent status
poetry run orchestrator status

# Stop all agents
poetry run orchestrator stop

# Restart specific agent
poetry run orchestrator restart architect

# View agent logs
poetry run orchestrator logs architect

# Health check
poetry run orchestrator health
```

---

## Risks & Mitigations

### Risk 1: Process Complexity

**Risk**: Managing 6 subprocesses is complex, more failure points

**Impact**: High (system stability)

**Mitigation**:
1. Robust health monitoring (heartbeat every 30 seconds)
2. Automatic restart with exponential backoff
3. Status dashboard showing all agents
4. Comprehensive logging with agent identification
5. Crash history tracking for pattern analysis

### Risk 2: File Conflicts

**Risk**: Multiple agents modifying same files → merge conflicts

**Impact**: Critical (CFR-000 violation, data corruption)

**Mitigation**:
1. Strict CFR-000 file ownership enforcement in all agents
2. Each agent owns specific directories (ownership matrix)
3. READ-ONLY access for non-owners (enforced by base class)
4. Runtime checks before file modifications
5. Git status checks before commits (detect conflicts early)

### Risk 3: Message Queue Overload

**Risk**: Too many messages between agents → performance degradation

**Impact**: Medium (responsiveness)

**Mitigation**:
1. Priority-based message queuing (urgent vs normal)
2. Inbox size limits (max 100 messages per agent)
3. Automatic cleanup of old messages (>24 hours)
4. Message expiration timestamps
5. CFR-012 ensures urgent messages processed first

### Risk 4: Cost (API Usage)

**Risk**: 6 agents running continuously → high API costs

**Impact**: High (operational cost)

**Mitigation**:
1. Smart sleep intervals (agents check hourly/daily, not every second)
2. Batch operations where possible (combine multiple prompts)
3. Cache frequently accessed data (ROADMAP, specs)
4. Use Claude CLI for some agents (subscription vs API)
5. Budget monitoring and alerts

### Risk 5: Debugging Difficulty

**Risk**: Bugs in multi-agent system harder to debug than single agent

**Impact**: Medium (development velocity)

**Mitigation**:
1. Comprehensive Langfuse observability for all agents
2. Detailed logging with agent identification in every log line
3. Status files capture full agent state at any moment
4. Crash history tracked per agent with full context
5. Trace execution flows across agents

### Risk 6: CFR-013 Violation

**Risk**: Agent accidentally switches branches → work scattered

**Impact**: Critical (breaks coordination)

**Mitigation**:
1. CFR-013 enforcement in BaseAgent (checked before every operation)
2. Pre-commit hook prevents commits on wrong branch
3. Orchestrator validates branch before launching agents
4. Runtime monitoring of current branch
5. Clear error messages if violation detected

---

## Success Criteria

### Functional Requirements

- [ ] Orchestrator launches all 6 agents in separate subprocesses
- [ ] Each agent runs continuous work loop with CFR-012 interruption handling
- [ ] Agent health monitoring with automatic restart on crash
- [ ] Status files written by all agents (heartbeat every 30 seconds)
- [ ] Inter-agent messaging works (delegation flows verified)
- [ ] CFR-000 file ownership enforced (zero conflicts observed)
- [ ] CFR-013 enforced (all agents on roadmap branch, verified continuously)
- [ ] CLI interface for orchestrator control (status, restart, logs)
- [ ] Graceful shutdown of all agents (SIGTERM handled properly)

### Performance Requirements

- [ ] architect creates 3-5 specs ahead of code_developer (CFR-011 verified)
- [ ] code_developer implementation time unchanged (~4 hours/priority)
- [ ] assistant creates demo within 30 minutes of completion (measured)
- [ ] project_manager checks GitHub every 15 minutes (verified)
- [ ] code-searcher runs weekly analysis automatically (scheduled)
- [ ] Overall priority completion time reduced by 50% (3x speedup minimum)

### Quality Requirements

- [ ] Zero merge conflicts between agents (CFR-000 compliance)
- [ ] All commits include agent identification (traceable)
- [ ] All agents respond to urgent requests within 2 minutes (CFR-012)
- [ ] Status dashboard shows all agent states in real-time
- [ ] Langfuse tracking for all agent executions (observability)
- [ ] Comprehensive logging with agent identification (debuggable)

---

## Definition of Done

### Code Complete

- [ ] `AutonomousTeamOrchestrator` class implemented
- [ ] `BaseAgent` abstract class implemented
- [ ] All 6 agent classes implemented (architect, code_developer, etc.)
- [ ] Status file infrastructure complete
- [ ] Inter-agent messaging system complete
- [ ] CFR enforcement in all agents (CFR-000, CFR-012, CFR-013)
- [ ] CLI interface for orchestrator complete

### Tests Pass

- [ ] Unit tests: 100% coverage for orchestrator core
- [ ] Unit tests: BaseAgent and agent implementations
- [ ] Integration tests: Multi-agent coordination scenarios
- [ ] Integration tests: CFR enforcement (all CFRs verified)
- [ ] Integration tests: Crash recovery scenarios
- [ ] Performance benchmarks: 3x speedup minimum

### Documentation

- [ ] `.claude/CLAUDE.md` updated with orchestrator architecture
- [ ] Agent README files updated with usage examples
- [ ] `TEAM_COLLABORATION.md` updated with multi-agent workflows
- [ ] CFR document updated with CFR-014 (multi-agent orchestration rules)
- [ ] Migration guide written (gradual rollout strategy)
- [ ] Troubleshooting guide written (common issues and solutions)

### Deployment

- [ ] Orchestrator deployed and running
- [ ] All 6 agents operational
- [ ] Status dashboard showing all agents
- [ ] Monitoring and alerting configured (Langfuse + logs)
- [ ] User notified of new multi-agent system
- [ ] Training materials provided (how to use orchestrator CLI)

### Validation

- [ ] Orchestrator runs for 24 hours without crashes
- [ ] architect creates specs proactively (zero blocking observed)
- [ ] assistant creates demos automatically (within 30 minutes)
- [ ] project_manager monitors GitHub continuously (every 15 minutes)
- [ ] All agents respect CFR-013 (verified: stayed on roadmap branch)
- [ ] Zero merge conflicts observed (CFR-000 compliance)
- [ ] Priority completion time reduced by 50% (measured: 3x speedup)

---

## Related Work

**Prerequisites**:
- US-056: Enforce CFR-013 (Daemon on roadmap branch only) 🚨 **MUST BE COMPLETE**
- US-035: Agent Singleton Enforcement (CFR-000 foundation)

**Builds On**:
- US-045: Daemon delegates spec creation to architect (architect agent foundation)
- US-027: Roadmap branch as single source of truth (CFR-013 foundation)
- US-024: Frequent roadmap sync (coordination foundation)
- CFR-011: Architect proactive spec creation (architect work loop)
- CFR-012: Agent responsiveness priority (interruption handling)

**Enables**:
- US-058+: Future priorities implemented 3-6x faster
- Continuous QA with automatic demos (assistant agent)
- Proactive architecture with specs always ready (architect agent)
- Real-time project monitoring (project_manager agent)
- Weekly codebase improvements (code-searcher + architect collaboration)

---

## Estimated Timeline

### Week 1: Foundation (Days 1-3)

- **Day 1**: Orchestrator core (multi-process management)
- **Day 2**: BaseAgent class (CFR enforcement, status, messaging)
- **Day 3**: Shared state infrastructure (directories, schemas)

### Week 2: Agent Migration (Days 4-8)

- **Day 4-5**: CodeDeveloperAgent (extract daemon logic)
- **Day 6-7**: ArchitectAgent (CFR-011 proactive spec creation)
- **Day 8**: ProjectManagerAgent (GitHub monitoring)

### Week 3: Complete Team + Testing (Days 9-15)

- **Day 9**: AssistantAgent (demo creation, bug reporting)
- **Day 10**: CodeSearcherAgent + UXDesignExpertAgent
- **Day 11-12**: Coordination layer (messaging, health monitoring)
- **Day 13**: Integration testing
- **Day 14**: Documentation and deployment
- **Day 15**: 24-hour validation run

**Total**: 15 working days (3 weeks)

---

## Appendix: Code Skeletons

### A. Orchestrator Skeleton

```python
# coffee_maker/autonomous/orchestrator.py

class AutonomousTeamOrchestrator:
    def __init__(self, ...):
        # Initialize configurations
        # Create directories
        # Setup agent configs

    def run(self):
        # Enforce CFR-013
        # Launch all agents
        # Monitor health loop
        # Handle crashes
        # Shutdown gracefully

    def _launch_all_agents(self):
        # Launch in priority order

    def _launch_agent(self, agent_type, config):
        # Create subprocess
        # Start agent_runner

    def _agent_runner(self, agent_type, config):
        # Register in singleton (CFR-000)
        # Enforce CFR-013
        # Run agent continuous loop

    def _check_agent_health(self):
        # Check process alive
        # Check heartbeat recent

    def _handle_crashed_agents(self):
        # Restart with exponential backoff
        # Check restart limits
```

### B. BaseAgent Skeleton

```python
# coffee_maker/autonomous/agents/base_agent.py

class BaseAgent(ABC):
    def __init__(self, agent_type, status_dir, message_dir, check_interval):
        # Initialize common state

    def run_continuous(self):
        # CFR-013: Validate roadmap branch
        # Loop:
        #   CFR-012: Check urgent messages first
        #   Check regular messages
        #   Do background work
        #   Write status (heartbeat)
        #   Sleep

    def _enforce_cfr_013(self):
        # Check current branch
        # Raise if not roadmap

    def _check_inbox_urgent(self):
        # Check for urgent_*.json files

    def _check_inbox(self):
        # Check for *.json files (not urgent)

    def _write_status(self, error=None):
        # Write status file with heartbeat

    def commit_changes(self, message, files=None):
        # Enforce CFR-013
        # Add agent identification
        # Commit and push to roadmap

    @abstractmethod
    def _do_background_work(self):
        # Subclass implements

    @abstractmethod
    def _handle_message(self, message):
        # Subclass implements
```

---

**End of Technical Specification**

**Next Steps**:
1. Review this spec with user for approval
2. Create ADR-057 documenting orchestrator architecture decision
3. Begin implementation in Phase 1 (Days 1-3)
4. Weekly status updates to user on progress

**Questions for User**:
1. Should we start with gradual rollout (2 agents first) or full team (6 agents)?
2. What is the acceptable API cost budget per day for 6 agents?
3. Should we implement legacy mode (single agent) for backward compatibility?

**Estimated Implementation Effort**: 3 weeks (15 working days)
**Expected Speedup**: 3-6x (from 6-9 hours to 2-3 hours per priority)
**Risk Level**: Medium-High (complex architecture, but mitigations in place)
