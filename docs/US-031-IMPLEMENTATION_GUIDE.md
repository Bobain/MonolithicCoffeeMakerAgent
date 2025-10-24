# US-031: Implementation Guide - Custom AI Development Environment

**Status**: Complete
**Created**: 2025-10-23
**Related**: US-031 - Custom AI Development Environment

## Overview

This document provides comprehensive technical details on how the MonolithicCoffeeMakerAgent system is implemented, covering all major components, architectures, and integration points.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [CLI Interfaces](#cli-interfaces)
3. [Autonomous Daemon](#autonomous-daemon)
4. [Agent System](#agent-system)
5. [Project Management](#project-management)
6. [Multi-AI Provider Support](#multi-ai-provider-support)
7. [MCP Integration](#mcp-integration)
8. [Observability](#observability)
9. [Database Architecture](#database-architecture)
10. [Git Workflow](#git-workflow)

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├───────────────┬─────────────────┬──────────────┬────────────────┤
│ user-listener │ project-manager │ code-developer│ architect     │
│     (CLI)     │      (CLI)      │    (Daemon)  │    (CLI)      │
└───────┬───────┴────────┬────────┴──────┬───────┴───────┬────────┘
        │                │               │               │
        └────────────────┼───────────────┼───────────────┘
                         │               │
                    ┌────▼───────────────▼────┐
                    │   Agent Registry        │
                    │   (Singleton Mgmt)      │
                    └────┬───────────────┬────┘
                         │               │
        ┌────────────────┼───────────────┼────────────────┐
        │                │               │                │
   ┌────▼────┐     ┌────▼────┐     ┌───▼───┐      ┌────▼────┐
   │ Claude  │     │ OpenAI  │     │Gemini │      │  MCP    │
   │Provider │     │Provider │     │Provider│     │ Servers │
   └────┬────┘     └────┬────┘     └───┬───┘      └────┬────┘
        │                │               │               │
        └────────────────┼───────────────┼───────────────┘
                         │               │
                    ┌────▼───────────────▼────┐
                    │  Notification Database  │
                    │      (SQLite/WAL)       │
                    └─────────────────────────┘
```

### Key Design Principles

1. **Autonomy**: Agents operate independently with minimal human intervention
2. **Observability**: All actions tracked via Langfuse and SQLite
3. **Multi-Provider**: Support Claude, OpenAI, Gemini with fallback
4. **Singleton Enforcement**: CFR-000 ensures one agent instance per type
5. **Database-First**: SQLite WAL mode for concurrent access (CFR-014)

---

## CLI Interfaces

### 1. user-listener (Primary UI)

**Purpose**: Main entry point for user interactions, routes to specialized agents

**Implementation**: `coffee_maker/cli/user_listener.py`

**Key Features**:
- Rich console UI with syntax highlighting
- Multi-line input support
- Command history
- Agent routing based on intent
- User story detection (US-033 ✅)

**Usage**:
```bash
poetry run user-listener

# Interactive commands:
/help           # Show help
/clear          # Clear screen
/exit           # Exit
/US "story"     # Add user story
```

**Architecture**:
```python
from coffee_maker.cli.user_listener import UserListener
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

class UserListener:
    def __init__(self):
        self.console = Console()  # Rich console
        self.classifier = RequestClassifier()  # Intent detection
        self.agent_registry = AgentRegistry()

    def run(self):
        """Main loop"""
        while True:
            user_input = self.session.prompt("You: ")

            # Detect intent
            intent = self.classifier.classify(user_input)

            # Route to appropriate agent
            if intent == "code_search":
                self.delegate_to_code_searcher(user_input)
            elif intent == "architecture":
                self.delegate_to_architect(user_input)
            elif intent == "project_management":
                self.delegate_to_project_manager(user_input)
            else:
                self.delegate_to_assistant(user_input)
```

**Configuration**:
- Prompts: `.claude/commands/user-listener.md`
- Agent routing rules in `RequestClassifier`

---

### 2. project-manager (ROADMAP Management)

**Purpose**: Manage ROADMAP.md, notifications, and project status

**Implementation**: `coffee_maker/cli/roadmap_cli.py`

**Key Commands**:
```bash
# View roadmap
poetry run project-manager view          # All priorities
poetry run project-manager view 25       # Specific priority

# Developer status
poetry run project-manager developer-status  # Real-time dashboard

# Notifications
poetry run project-manager notifications     # List pending
poetry run project-manager respond 5 approve # Respond

# AI Chat (Phase 2)
poetry run project-manager chat              # Interactive AI session

# Metrics (US-015)
poetry run project-manager metrics           # Velocity tracking
poetry run project-manager summary           # Recent completions
poetry run project-manager calendar          # Upcoming deliverables

# Spec Management (US-016, US-047, US-049)
poetry run project-manager spec 25           # Generate spec
poetry run project-manager spec-status       # Coverage report
poetry run project-manager spec-diff 25      # Compare to impl
```

**Architecture**:
```python
from coffee_maker.cli.roadmap_cli import RoadmapCLI
from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.db.notification_db import NotificationDB

class RoadmapCLI:
    def __init__(self):
        self.roadmap_path = "docs/roadmap/ROADMAP.md"
        self.parser = RoadmapParser()
        self.notification_db = NotificationDB()

    def view_priority(self, priority_id: str):
        """View specific priority"""
        roadmap = self.parser.parse_file(self.roadmap_path)
        priority = roadmap.find_priority(priority_id)

        # Rich console output
        self.console.print(Panel(
            priority.format_markdown(),
            title=f"PRIORITY {priority_id}"
        ))

    def check_notifications(self):
        """List pending notifications"""
        notifications = self.notification_db.get_pending()

        for notif in notifications:
            self.console.print(f"[{notif.id}] {notif.title}")
            self.console.print(f"    {notif.message}")
```

**Database Integration**:
- Notifications: SQLite database with WAL mode
- Concurrent access: `@with_retry` decorator
- Schema: `coffee_maker/db/notification_db.py`

---

### 3. code-developer (Autonomous Daemon)

**Purpose**: Implement features autonomously from ROADMAP.md

**Implementation**: `coffee_maker/autonomous/daemon_cli.py` + `daemon.py`

**Usage**:
```bash
# Interactive mode (asks for approval)
poetry run code-developer

# Autonomous mode (full automation)
poetry run code-developer --auto-approve

# Specific priority only
poetry run code-developer --priority 25

# API mode (uses Anthropic API instead of CLI)
poetry run code-developer --use-api

# Verbose logging
poetry run code-developer --verbose

# Skip PR creation
poetry run code-developer --no-pr
```

**Workflow**:
```python
from coffee_maker.autonomous.daemon import AutonomousDaemon
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

class AutonomousDaemon:
    def run(self):
        """Main daemon loop"""
        # Singleton enforcement (CFR-000)
        with AgentRegistry.register(AgentType.CODE_DEVELOPER):
            while True:
                # 1. Find next priority
                priority = self.find_next_planned_priority()

                if not priority:
                    self.logger.info("No planned priorities found")
                    break

                # 2. Create notification for approval
                notif_id = self.create_approval_notification(priority)

                # 3. Wait for approval (unless --auto-approve)
                if not self.auto_approve:
                    response = self.wait_for_approval(notif_id)
                    if response != "approve":
                        continue

                # 4. Implement priority
                try:
                    self.implement_priority(priority)

                    # 5. Run tests
                    self.run_tests()

                    # 6. Verify DoD with Puppeteer
                    if priority.has_web_interface:
                        self.verify_dod_with_puppeteer(priority)

                    # 7. Create commit + PR
                    self.create_commit(priority)
                    if not self.no_pr:
                        self.create_pull_request(priority)

                    # 8. Mark complete
                    self.mark_priority_complete(priority)

                except Exception as e:
                    self.create_error_notification(priority, e)

                # 9. Sleep before next iteration
                time.sleep(self.sleep_seconds)
```

**Claude CLI Integration**:
```python
from coffee_maker.autonomous.claude_cli_interface import ClaudeCliInterface

class ClaudeCliInterface:
    def execute_prompt(self, prompt: str) -> str:
        """Execute prompt via Claude CLI"""
        # Write prompt to temp file
        prompt_file = self.write_temp_prompt(prompt)

        # Execute: claude chat < prompt.txt
        result = subprocess.run(
            [self.claude_path, "chat"],
            stdin=open(prompt_file),
            capture_output=True,
            text=True
        )

        return result.stdout
```

**Prompts Used**:
- `.claude/commands/implement-feature.md` - Implementation instructions
- `.claude/commands/verify-dod-puppeteer.md` - DoD verification
- `.claude/commands/implement-documentation.md` - Documentation priorities

---

### 4. architect (Technical Design)

**Purpose**: Create specifications, ADRs, and technical designs

**Implementation**: `coffee_maker/cli/architect_cli.py`

**Usage**:
```bash
# Create technical spec
poetry run architect create-spec 25

# Weekly codebase analysis (CFR-011)
poetry run architect analyze-codebase

# Daily integration workflow (CFR-011)
poetry run architect daily-integration

# Check CFR-011 compliance
poetry run architect cfr-011-status
```

**Architecture**:
```python
from coffee_maker.cli.architect_cli import ArchitectCLI
from coffee_maker.autonomous.agent_registry import AgentType

class ArchitectCLI:
    @click.command()
    @click.argument("priority_id")
    def create_spec(self, priority_id: str):
        """Create technical specification"""
        # Load priority from ROADMAP
        priority = self.roadmap_parser.find_priority(priority_id)

        # Load prompt
        prompt = load_prompt(
            PromptNames.CREATE_SPEC,
            {
                "priority_id": priority_id,
                "description": priority.description,
                "acceptance_criteria": priority.acceptance_criteria
            }
        )

        # Execute via Claude
        spec_content = self.claude_interface.execute(prompt)

        # Write to docs/architecture/specs/
        spec_path = f"docs/architecture/specs/SPEC-{priority_id:03d}.md"
        with open(spec_path, "w") as f:
            f.write(spec_content)

        print(f"✅ Created spec: {spec_path}")
```

---

### 5. code-reviewer (Quality Assurance)

**Purpose**: Review commits, check style compliance, notify architect

**Implementation**: `coffee_maker/autonomous/code_reviewer.py`

**Usage**:
```bash
# Review specific commits
poetry run code-reviewer review HEAD~1..HEAD

# Review PR
poetry run code-reviewer review-pr 123

# Check style guide compliance
poetry run code-reviewer check-style
```

**Integration**:
- Runs automatically via git hooks (planned)
- Creates notifications for architect
- Stores results in SQLite database

---

### 6. orchestrator (Parallel Execution)

**Purpose**: Run multiple priorities in parallel using git worktrees

**Implementation**: `coffee_maker/cli/orchestrator_cli.py`

**Usage**:
```bash
# Run priorities in parallel
poetry run orchestrator parallel-priorities 10 11 12

# Monitor status
poetry run orchestrator status

# Health check
poetry run orchestrator health-check
```

**Architecture** (CFR-014):
```python
from coffee_maker.cli.orchestrator_cli import Orchestrator
from coffee_maker.db.orchestrator_db import OrchestratorDB

class Orchestrator:
    def parallel_priorities(self, priority_ids: List[int]):
        """Execute priorities in parallel"""
        # Database tracking (CFR-014)
        self.db = OrchestratorDB()

        for priority_id in priority_ids:
            # Create git worktree
            branch = f"roadmap-{priority_id}"
            worktree_path = f"/tmp/{branch}"

            subprocess.run([
                "git", "worktree", "add",
                worktree_path,
                "-b", branch,
                "roadmap"
            ])

            # Start code_developer in worktree
            process = subprocess.Popen([
                "poetry", "run", "code-developer",
                "--auto-approve",
                "--priority", str(priority_id)
            ], cwd=worktree_path)

            # Track in database
            self.db.add_worker(
                priority_id=priority_id,
                branch=branch,
                worktree_path=worktree_path,
                pid=process.pid
            )

        # Monitor progress
        self.monitor_workers()
```

**Database Schema** (CFR-014):
```sql
-- coffee_maker/db/orchestrator_db.py
CREATE TABLE workers (
    id INTEGER PRIMARY KEY,
    priority_id INTEGER NOT NULL,
    branch TEXT NOT NULL,
    worktree_path TEXT NOT NULL,
    pid INTEGER NOT NULL,
    status TEXT NOT NULL,  -- running, complete, error
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

---

## Autonomous Daemon

### Implementation Flow

```
┌──────────────────────────────────────────────────────────┐
│                    Daemon Lifecycle                      │
└──────────────────────────────────────────────────────────┘

1. Startup
   ├─ Register singleton (AgentRegistry)
   ├─ Load configuration
   ├─ Connect to notification database
   └─ Load ROADMAP.md

2. Main Loop
   ├─ Find next 📝 Planned priority
   ├─ Create approval notification
   ├─ Wait for user response (unless --auto-approve)
   │  ├─ Approved → Continue
   │  ├─ Rejected → Skip to next
   │  └─ Modified → Use modified instructions
   │
   ├─ Implement Priority
   │  ├─ Load technical spec (if exists)
   │  ├─ Load prompt template
   │  ├─ Execute via Claude CLI or API
   │  └─ Monitor output
   │
   ├─ Run Tests
   │  ├─ pytest
   │  ├─ black --check
   │  └─ mypy
   │
   ├─ Verify DoD (if web feature)
   │  ├─ Launch Puppeteer
   │  ├─ Test acceptance criteria
   │  ├─ Take screenshots
   │  └─ Check console errors
   │
   ├─ Create Commit
   │  ├─ git add .
   │  ├─ Generate commit message
   │  ├─ git commit (with 🤖 footer)
   │  └─ git push
   │
   ├─ Create PR (unless --no-pr)
   │  ├─ gh pr create
   │  └─ Link to priority
   │
   ├─ Mark Complete
   │  └─ Update ROADMAP.md: 📝 Planned → ✅ Complete
   │
   └─ Sleep (default 30s)

3. Shutdown
   ├─ Save state
   ├─ Close database connections
   └─ Unregister singleton
```

### Singleton Enforcement (CFR-000)

**Problem**: Multiple daemon instances cause:
- File conflicts (editing same files)
- Duplicate work (implementing same priority twice)
- Resource waste (multiple Claude API calls)

**Solution**: `AgentRegistry` singleton manager

**Implementation**: `coffee_maker/autonomous/agent_registry.py`

```python
from enum import Enum
from contextlib import contextmanager
import os
import psutil

class AgentType(Enum):
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    CODE_REVIEWER = "code_reviewer"
    ORCHESTRATOR = "orchestrator"
    ASSISTANT = "code_searcher"
    UX_DESIGNER = "ux_designer"

class AgentRegistry:
    """Singleton registry for agent instances"""

    _instance = None
    _active_agents: Dict[AgentType, AgentInstance] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    @contextmanager
    def register(cls, agent_type: AgentType):
        """Context manager for agent registration"""
        registry = cls()

        # Check if already running
        if agent_type in registry._active_agents:
            existing = registry._active_agents[agent_type]

            # Check if process still alive
            if psutil.pid_exists(existing.pid):
                raise AgentAlreadyRunningError(
                    f"{agent_type.value} already running (PID: {existing.pid})"
                )
            else:
                # Stale entry, remove it
                del registry._active_agents[agent_type]

        # Register new instance
        instance = AgentInstance(
            agent_type=agent_type,
            pid=os.getpid(),
            started_at=datetime.now()
        )
        registry._active_agents[agent_type] = instance

        try:
            yield registry
        finally:
            # Unregister on exit
            if agent_type in registry._active_agents:
                del registry._active_agents[agent_type]

# Usage in daemon
from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

def main():
    with AgentRegistry.register(AgentType.CODE_DEVELOPER):
        daemon = AutonomousDaemon()
        daemon.run()
```

**Tests**: `tests/unit/test_agent_registry.py` (30+ tests)

---

## Agent System

### Agent Types

1. **user_listener** - Primary UI, routes to other agents
2. **code_developer** - Autonomous implementation
3. **project_manager** - ROADMAP management
4. **architect** - Technical specs, ADRs
5. **code-reviewer** - Quality assurance
6. **assistant (with code analysis skills)** - Deep code analysis
7. **orchestrator** - Parallel execution

### Agent Routing

**Implementation**: `coffee_maker/cli/request_classifier.py`

```python
from enum import Enum

class IntentType(Enum):
    CODE_SEARCH = "code_search"
    ARCHITECTURE = "architecture"
    PROJECT_MANAGEMENT = "project_management"
    USER_STORY = "user_story"
    GENERAL = "general"

class RequestClassifier:
    def classify(self, user_input: str) -> IntentType:
        """Classify user intent using AI"""

        # Use Claude to classify
        prompt = f"""
        Classify the following user request:
        "{user_input}"

        Intent types:
        - code_search: Finding code, functions, classes
        - architecture: Design decisions, specs, ADRs
        - project_management: ROADMAP, priorities, status
        - user_story: Feature requests
        - general: Other questions

        Return only the intent type.
        """

        intent = self.claude_interface.execute(prompt).strip()
        return IntentType(intent)
```

**Routing Table**:

| Intent | Agent | Example |
|--------|-------|---------|
| code_search | assistant (with code analysis skills) | "Find all singleton patterns" |
| architecture | architect | "Create spec for priority 25" |
| project_management | project_manager | "Show ROADMAP status" |
| user_story | project_manager | "I want email notifications" |
| general | assistant | "What is Python?" |

---

## Project Management

### ROADMAP.md Structure

**Location**: `docs/roadmap/ROADMAP.md`

**Format**:
```markdown
## PRIORITY 25: Skill Loading Enhancement

**Status**: ✅ Complete
**Type**: Enhancement / Technical Debt
**Estimated Duration**: 1-2 days
**Impact**: ⭐⭐⭐⭐ (High)
**Dependencies**: PRIORITY 24 ✅
**Assigned**: code_developer
**Completion**: 2025-10-16

### User Story
> "As a developer, I want skills to load via proper Python imports..."

### Description
Refactor skill loading to use Python imports instead of shell scripts.

### Acceptance Criteria
- [ ] Skills loaded via Python imports
- [ ] No shell script wrappers
- [ ] 100% test coverage
- [ ] Documentation updated

### Technical Requirements
...

### Testing Strategy
...

### Definition of Done
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] PR reviewed and merged
```

### Parsing

**Implementation**: `coffee_maker/autonomous/roadmap_parser.py`

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Priority:
    number: int
    title: str
    status: str  # 📝 Planned, 🏗️ In Progress, ✅ Complete
    type: str
    duration: str
    impact: int
    dependencies: List[int]
    assigned: str
    description: str
    acceptance_criteria: List[str]
    definition_of_done: List[str]

class RoadmapParser:
    def parse_file(self, path: str) -> Roadmap:
        """Parse ROADMAP.md file"""
        with open(path) as f:
            content = f.read()

        priorities = []

        # Split by priority headers
        for section in content.split("## PRIORITY"):
            if not section.strip():
                continue

            priority = self.parse_priority_section(section)
            priorities.append(priority)

        return Roadmap(priorities=priorities)

    def parse_priority_section(self, section: str) -> Priority:
        """Parse individual priority"""
        lines = section.split("\n")

        # Extract header: "25: Skill Loading Enhancement"
        header = lines[0]
        number, title = header.split(":", 1)
        number = int(number.strip())
        title = title.strip()

        # Extract metadata
        metadata = {}
        for line in lines[1:]:
            if line.startswith("**"):
                key, value = line.split(":", 1)
                key = key.strip("*").strip()
                value = value.strip()
                metadata[key] = value

        # Extract sections
        description = self.extract_section(lines, "### Description")
        acceptance_criteria = self.extract_checklist(lines, "### Acceptance Criteria")
        definition_of_done = self.extract_checklist(lines, "### Definition of Done")

        return Priority(
            number=number,
            title=title,
            status=metadata.get("Status", "📝 Planned"),
            type=metadata.get("Type", ""),
            duration=metadata.get("Estimated Duration", ""),
            impact=self.parse_impact(metadata.get("Impact", "")),
            dependencies=self.parse_dependencies(metadata.get("Dependencies", "")),
            assigned=metadata.get("Assigned", ""),
            description=description,
            acceptance_criteria=acceptance_criteria,
            definition_of_done=definition_of_done
        )
```

### User Story Detection (US-033 ✅)

**Implementation**: `coffee_maker/cli/user_story_detector.py`

```python
from dataclasses import dataclass

@dataclass
class UserStory:
    actor: str
    goal: str
    benefit: str
    confidence: float

class UserStoryDetector:
    def detect(self, text: str) -> Optional[UserStory]:
        """Detect user story in text"""

        # Formal format: "As a X I want Y so that Z"
        formal_match = re.match(
            r"As a (?P<actor>[\w\s]+) I want (?P<goal>[^,]+)(?:, | so that | because )(?P<benefit>.+)",
            text,
            re.IGNORECASE
        )

        if formal_match:
            return UserStory(
                actor=formal_match.group("actor").strip(),
                goal=formal_match.group("goal").strip(),
                benefit=formal_match.group("benefit").strip(),
                confidence=0.95
            )

        # Informal format: "I want..." - use AI
        prompt = f"""
        Analyze this text for user story components:
        "{text}"

        If this is a feature request, extract:
        - Actor (who)
        - Goal (what they want)
        - Benefit (why)
        - Confidence (0-1)

        Return JSON:
        {{"actor": "...", "goal": "...", "benefit": "...", "confidence": 0.8}}

        If not a user story, return: {{"confidence": 0}}
        """

        response = self.ai_provider.execute(prompt)
        data = json.loads(response)

        if data["confidence"] > 0.7:
            return UserStory(**data)

        return None
```

**Integration in user_listener**:
```python
def process_user_input(self, text: str):
    """Process user input"""

    # Check for user story
    user_story = self.user_story_detector.detect(text)

    if user_story and user_story.confidence > 0.7:
        # Show confirmation
        self.console.print(Panel(
            f"Actor: {user_story.actor}\n"
            f"Goal: {user_story.goal}\n"
            f"Benefit: {user_story.benefit}",
            title="Detected User Story"
        ))

        response = Prompt.ask("Add to ROADMAP?", choices=["y", "n", "e"])

        if response == "y":
            # Delegate to project_manager
            self.delegate_to_project_manager(
                f"Add user story: {user_story}"
            )
        elif response == "e":
            # Edit before adding
            edited = self.edit_user_story(user_story)
            self.delegate_to_project_manager(
                f"Add user story: {edited}"
            )
    else:
        # Normal routing
        intent = self.classifier.classify(text)
        self.route_to_agent(intent, text)
```

---

## Multi-AI Provider Support

**Implementation**: PRIORITY 8 ✅

**Location**: `coffee_maker/ai_providers/`

### Architecture

```
coffee_maker/ai_providers/
├── base.py                     # Abstract base class
├── provider_factory.py         # Factory pattern
├── provider_config.py          # Configuration
├── fallback_strategy.py        # Automatic fallback
└── providers/
    ├── claude_provider.py      # Anthropic Claude
    ├── openai_provider.py      # OpenAI GPT
    └── gemini_provider.py      # Google Gemini
```

### Base Interface

```python
from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Abstract base for AI providers"""

    @abstractmethod
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute prompt, return response"""
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token counts"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return model name"""
        pass
```

### Claude Provider

```python
from anthropic import Anthropic

class ClaudeProvider(AIProvider):
    def __init__(self, model: str = "claude-sonnet-4-5"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def execute(self, prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        # Sonnet 4.5 pricing
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
```

### Provider Factory

```python
class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> AIProvider:
        """Create provider instance"""

        if provider_name == "claude":
            return ClaudeProvider()
        elif provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "gemini":
            return GeminiProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
```

### Fallback Strategy

```python
class FallbackStrategy:
    def __init__(self, config: dict):
        self.config = config
        self.providers = [
            ProviderFactory.create(name)
            for name in config["fallback_strategy"]["order"]
        ]

    def execute_with_fallback(self, prompt: str, **kwargs) -> str:
        """Try providers in order until success"""

        last_error = None

        for provider in self.providers:
            try:
                response = provider.execute(prompt, **kwargs)
                return response

            except RateLimitError as e:
                # Rate limit - try next provider
                logger.warning(f"{provider.get_model_name()} rate limited, trying next")
                last_error = e
                continue

            except Exception as e:
                # Other error - try next provider
                logger.error(f"{provider.get_model_name()} failed: {e}")
                last_error = e
                continue

        # All providers failed
        raise AllProviders FailedError(
            f"All providers failed. Last error: {last_error}"
        )
```

### Configuration

**File**: `config/ai_providers.yaml`

```yaml
providers:
  claude:
    enabled: true
    model: "claude-sonnet-4-5-20250929"
    api_key_env: "ANTHROPIC_API_KEY"
    cost_per_million_input: 3.0
    cost_per_million_output: 15.0
    max_tokens: 8192
    timeout: 300

  openai:
    enabled: true
    model: "gpt-4-turbo"
    api_key_env: "OPENAI_API_KEY"
    cost_per_million_input: 10.0
    cost_per_million_output: 30.0
    max_tokens: 4096
    timeout: 300

  gemini:
    enabled: true
    model: "gemini-2.0-flash-exp"
    api_key_env: "GOOGLE_API_KEY"
    cost_per_million_input: 0.075
    cost_per_million_output: 0.3
    max_tokens: 8192
    timeout: 300

fallback_strategy:
  enabled: true
  order: ["claude", "openai", "gemini"]
  max_retries: 3
  retry_delay: 2.0
```

**Usage**:
```python
from coffee_maker.ai_providers.provider_factory import ProviderFactory
from coffee_maker.ai_providers.fallback_strategy import FallbackStrategy

# Direct usage
provider = ProviderFactory.create("claude")
response = provider.execute("Write a haiku about coding")

# With fallback
strategy = FallbackStrategy(config)
response = strategy.execute_with_fallback("Write a haiku about coding")
```

---

## MCP Integration

### Puppeteer MCP

**Purpose**: Browser automation for DoD verification

**Configuration**: `.claude/mcp/puppeteer.json`

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {
        "PUPPETEER_LAUNCH_OPTIONS": "{\"headless\": true}"
      }
    }
  }
}
```

**Available Tools**:
- `puppeteer_navigate(url)` - Navigate to URL
- `puppeteer_screenshot(selector, name)` - Take screenshot
- `puppeteer_click(selector)` - Click element
- `puppeteer_fill(selector, value)` - Fill input
- `puppeteer_evaluate(script)` - Run JavaScript

**Usage in DoD Verification**:

**Prompt**: `.claude/commands/verify-dod-puppeteer.md`

```markdown
# Verify Definition of Done - Puppeteer

You are verifying the DoD for:
**PRIORITY {priority_number}: {title}**

## Acceptance Criteria
{acceptance_criteria}

## Instructions

1. **Navigate to Application**:
   Use `puppeteer_navigate` to go to the web interface.

2. **Test Each Criterion**:
   For each acceptance criterion:
   - Navigate to relevant page/section
   - Perform required interactions
   - Take screenshot as evidence
   - Check for console errors

3. **Create Report**:
   Document results:
   - ✅ Pass or ❌ Fail for each criterion
   - Screenshots with descriptions
   - Any console errors found
   - Performance observations

4. **Final Recommendation**:
   - PASS: All criteria met, no blocking issues
   - FAIL: Critical criteria not met or blocking issues
```

**Implementation in Daemon**:
```python
def verify_dod_with_puppeteer(self, priority: Priority):
    """Verify DoD using Puppeteer"""

    # Generate verification prompt
    prompt_path = ".claude/commands/verify-dod-puppeteer.md"
    prompt = self.load_prompt(
        prompt_path,
        {
            "priority_number": priority.number,
            "title": priority.title,
            "acceptance_criteria": priority.acceptance_criteria
        }
    )

    # Execute via Claude CLI (MCP auto-loaded)
    result = self.claude_interface.execute(prompt)

    # Parse result
    if "PASS" in result:
        self.logger.info("✅ DoD verification passed")
        return True
    else:
        self.logger.error("❌ DoD verification failed")
        self.create_notification(
            title="DoD Verification Failed",
            message=result
        )
        return False
```

**PuppeteerClient Utility**:

**Location**: `coffee_maker/autonomous/puppeteer_client.py`

```python
class PuppeteerClient:
    """Utility for Puppeteer operations"""

    @staticmethod
    def generate_verification_prompt(
        priority_number: int,
        title: str,
        acceptance_criteria: List[str],
        web_url: str = "http://localhost:8501"
    ) -> str:
        """Generate DoD verification prompt"""

        criteria_text = "\n".join([
            f"- {criterion}"
            for criterion in acceptance_criteria
        ])

        return f"""
        Verify Definition of Done for PRIORITY {priority_number}

        Title: {title}
        URL: {web_url}

        Acceptance Criteria:
        {criteria_text}

        Test each criterion systematically using Puppeteer.
        Take screenshots as evidence.
        Report PASS or FAIL.
        """
```

---

## Observability

### Langfuse Integration

**Status**: Planned (Phase 2)

**Purpose**: Track all agent interactions, performance, costs

**Implementation** (Planned):
```python
from langfuse.decorators import observe

@observe(name="implement_priority")
def implement_priority(priority_id: int):
    """Implement a priority"""

    # All steps automatically tracked:
    # - Prompts sent
    # - Responses received
    # - Tokens used
    # - Cost incurred
    # - Time elapsed
    # - Errors encountered

    priority = roadmap_parser.find_priority(priority_id)
    result = claude_interface.execute(prompt)
    return result
```

### Developer Status Dashboard

**Command**: `poetry run project-manager developer-status`

**Output**:
```
┌─────────────────────────────────────────┐
│      Code Developer Status              │
├─────────────────────────────────────────┤
│ Status:          Running                │
│ Current:         PRIORITY 26            │
│ Title:           Skill Loading          │
│ Progress:        60% (3/5 criteria)     │
│ Time Elapsed:    1h 23m 45s             │
│ CPU Usage:       45%                    │
│ Memory:          512 MB                 │
│ PID:             12345                  │
├─────────────────────────────────────────┤
│ Recent Activity:                        │
│  - 13:45: Tests passing                 │
│  - 13:30: Implementation complete       │
│  - 13:00: Started PRIORITY 26           │
└─────────────────────────────────────────┘
```

**Implementation**:
```python
import psutil

def show_developer_status():
    """Show developer status dashboard"""

    # Check if daemon running
    registry = AgentRegistry()
    developer = registry.get_agent(AgentType.CODE_DEVELOPER)

    if not developer:
        console.print("[red]Code developer not running[/red]")
        return

    # Get process info
    process = psutil.Process(developer.pid)
    cpu = process.cpu_percent(interval=1)
    memory = process.memory_info().rss / (1024 * 1024)  # MB

    # Get current priority from database
    status = daemon_status_db.get_latest()

    # Display dashboard
    console.print(Panel(
        f"Status: {status.state}\n"
        f"Current: PRIORITY {status.priority_id}\n"
        f"Title: {status.priority_title}\n"
        f"Progress: {status.progress}%\n"
        f"Time: {status.elapsed_time}\n"
        f"CPU: {cpu}%\n"
        f"Memory: {memory:.0f} MB\n"
        f"PID: {developer.pid}",
        title="Code Developer Status"
    ))
```

---

## Database Architecture

### Overview (CFR-014)

**Principle**: ALL orchestrator activities tracked in SQLite. JSON files FORBIDDEN.

**Database**: `data/orchestrator.db`

**Mode**: WAL (Write-Ahead Logging) for concurrent access

### Schema

```sql
-- Workers table
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority_id INTEGER NOT NULL,
    branch TEXT NOT NULL,
    worktree_path TEXT NOT NULL,
    pid INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('running', 'complete', 'error', 'stopped')),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    cpu_percent REAL,
    memory_mb REAL,
    last_heartbeat TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    priority_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected', 'expired')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    response_text TEXT
);

-- Daemon status table
CREATE TABLE daemon_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL CHECK(state IN ('idle', 'working', 'waiting', 'error')),
    priority_id INTEGER,
    priority_title TEXT,
    progress INTEGER,  -- 0-100
    current_step TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Database Access Pattern

**Decorator**: `@with_retry` for resilience

```python
from functools import wraps
import sqlite3
import time

def with_retry(max_retries: int = 3, delay: float = 0.5):
    """Retry database operations on lock"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        last_error = e
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise

            raise last_error

        return wrapper
    return decorator
```

**Usage**:
```python
class OrchestratorDB:
    def __init__(self, db_path: str = "data/orchestrator.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode

    @with_retry(max_retries=5)
    def add_worker(self, priority_id: int, branch: str, worktree_path: str, pid: int):
        """Add worker to database"""
        self.conn.execute(
            "INSERT INTO workers (priority_id, branch, worktree_path, pid, status) "
            "VALUES (?, ?, ?, ?, 'running')",
            (priority_id, branch, worktree_path, pid)
        )
        self.conn.commit()

    @with_retry(max_retries=5)
    def update_worker_status(self, worker_id: int, status: str):
        """Update worker status"""
        self.conn.execute(
            "UPDATE workers SET status = ?, completed_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (status, worker_id)
        )
        self.conn.commit()
```

---

## Git Workflow

### CFR-013: Git Workflow Standard

**Principle**: ALL agents work on `roadmap` branch ONLY. NO feature branches.

**Exception**: orchestrator may create temporary `roadmap-*` worktree branches for parallel execution.

### Branching Model

```
main (production)
└── roadmap (development)
    ├── roadmap-10 (temporary worktree)
    ├── roadmap-11 (temporary worktree)
    └── roadmap-12 (temporary worktree)
```

### Workflow

**1. Standard Development** (code_developer):
```bash
# Always work on roadmap branch
git checkout roadmap

# Make changes
# ...

# Commit with template
git commit -m "$(cat <<'EOF'
feat(PRIORITY 25): Refactor skill loading to use Python imports

- Remove shell script wrappers
- Add proper error handling
- Update documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Push
git push origin roadmap

# Create PR (when priority complete)
gh pr create --title "PRIORITY 25: Skill Loading" --body "..."
```

**2. Parallel Development** (orchestrator):
```bash
# Create worktrees
git worktree add /tmp/roadmap-10 -b roadmap-10 roadmap
git worktree add /tmp/roadmap-11 -b roadmap-11 roadmap
git worktree add /tmp/roadmap-12 -b roadmap-12 roadmap

# Run code_developer in each
cd /tmp/roadmap-10 && poetry run code-developer --auto-approve --priority 10 &
cd /tmp/roadmap-11 && poetry run code-developer --auto-approve --priority 11 &
cd /tmp/roadmap-12 && poetry run code-developer --auto-approve --priority 12 &

# Wait for completion
wait

# Merge back to roadmap (architect role)
git checkout roadmap
git merge --no-ff roadmap-10
git merge --no-ff roadmap-11
git merge --no-ff roadmap-12

# Cleanup worktrees (orchestrator role)
git worktree remove /tmp/roadmap-10
git worktree remove /tmp/roadmap-11
git worktree remove /tmp/roadmap-12

# Delete remote branches
git push origin --delete roadmap-10
git push origin --delete roadmap-11
git push origin --delete roadmap-12
```

### Commit Message Template

```
<type>(<scope>): <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance

**Examples**:
```
feat(PRIORITY 25): Refactor skill loading to use Python imports

- Remove shell script wrappers
- Add proper error handling
- Update documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Conclusion

The MonolithicCoffeeMakerAgent system provides:

1. **Feature Parity** with Claude CLI and Claude Desktop
2. **Custom Enhancements** for project management and autonomy
3. **Multi-AI Provider** support with automatic fallback
4. **Specialized Agents** for different tasks
5. **Robust Architecture** with singleton enforcement and database tracking
6. **Observability** through metrics and status dashboards
7. **Git Workflow** compliance with CFR-013

All components work together to create a fully customized AI development environment tailored to the project's needs.

---

## See Also

- [US-031 Feature Comparison](US-031-FEATURE_COMPARISON.md) - Compare with Claude CLI/Desktop
- [US-031 User Guide](US-031-USER_GUIDE.md) - How to use the system
- [US-031 Quick Start](US-031-QUICK_START.md) - Get started in 5 minutes

**Status**: Documentation Complete ✅
**Last Updated**: 2025-10-23
