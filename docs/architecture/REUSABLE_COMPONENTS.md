# Reusable Architectural Components

**Purpose**: Complete inventory of existing architectural components to ALWAYS check before creating new ones

**Owner**: architect agent (MUST read before any spec creation)

**Last Updated**: 2025-10-18

---

## 🎯 architect's Prime Directive

**BEFORE proposing ANY new architecture solution:**

1. ✅ Read this file
2. ✅ Identify problem domain
3. ✅ Check if existing component exists
4. ✅ Evaluate fitness (0-100%)
5. ✅ REUSE if >90%, EXTEND if 70-89%, ADAPT if 50-69%, NEW only if <50%

**Failure to check = Architectural inconsistency = Technical debt**

---

## 📚 Component Inventory by Domain

### 1. Inter-Agent Communication 🔄

#### Component: Orchestrator File-Based Messaging

**Location**: `coffee_maker/autonomous/orchestrator.py`

**What**: File-based messaging system for agent-to-agent communication

**API**:
```python
# Send message (available in all agents via BaseAgent)
self._send_message("architect", {
    "type": "commit_review_request",
    "priority": "CRITICAL",
    "content": {
        "commit_sha": "a1b2c3d",
        "files_changed": ["file1.py", "file2.py"]
    }
})

# Read messages
messages = self._read_messages(type_filter="commit_review_request")

# Iterate through messages
for message in messages:
    sender = message["sender"]
    content = message["content"]
    # Process message
```

**Storage**: `data/agent_messages/{agent}_inbox/`

**Format**: JSON files with structure:
```json
{
  "message_id": "unique_id",
  "type": "message_type",
  "sender": "code_developer",
  "recipient": "architect",
  "timestamp": "2025-10-18T14:30:00Z",
  "priority": "CRITICAL",
  "content": { ... }
}
```

**When to Use**:
- ✅ Agent A needs to notify Agent B
- ✅ Agent needs to send data to another agent
- ✅ Agent needs to request action from another agent
- ✅ Asynchronous communication (non-blocking)

**Fitness for Common Use Cases**:
- Agent notification: **100%** (perfect fit)
- Event triggering: **100%** (perfect fit)
- Data sharing: **80%** (good, but consider status files for state)
- Synchronous request-response: **60%** (works but latency)

**Examples**:
- code_developer → architect: "Review this commit"
- architect → code_developer: "Fix these bugs"
- architect → reflector: "Remember this pattern"
- assistant → project_manager: "Add this to ROADMAP"

**NEVER Use Instead**:
- ❌ Git hooks (external trigger)
- ❌ Direct function calls between agents
- ❌ Shared memory
- ❌ Database pub/sub
- ❌ WebSockets
- ❌ HTTP APIs between agents

---

### 2. Agent Orchestration 🎭

#### Component: OrchestratorAgent

**Location**: `coffee_maker/autonomous/orchestrator.py`

**What**: Multi-agent orchestrator managing parallel team execution

**API**:
```python
# Launch all agents
orchestrator = OrchestratorAgent()
orchestrator.run_continuous()

# Launch specific agents only
orchestrator = OrchestratorAgent(
    agent_types=[AgentType.ARCHITECT, AgentType.CODE_DEVELOPER]
)
orchestrator.run_continuous()
```

**Features**:
- Launches agents in priority order
- Health monitoring (heartbeat checks every 30s)
- Crash recovery with exponential backoff
- Graceful shutdown coordination
- CFR-013 enforcement (roadmap branch only)

**When to Use**:
- ✅ Need to launch multiple agents
- ✅ Need agent lifecycle management
- ✅ Need health monitoring
- ✅ Need crash recovery

**Fitness for Common Use Cases**:
- Multi-agent coordination: **100%** (perfect fit)
- Single agent launch: **50%** (can use, but overkill)
- Ad-hoc agent invocation: **30%** (use messaging instead)

**NEVER Use Instead**:
- ❌ systemd services
- ❌ supervisor
- ❌ PM2
- ❌ Custom process managers
- ❌ Docker compose with multiple containers per agent

---

### 3. Singleton Enforcement 🔒

#### Component: AgentRegistry

**Location**: `coffee_maker/autonomous/agent_registry.py`

**What**: Ensures only ONE instance of each agent type runs at a time

**API**:
```python
# Recommended: Context manager (automatic cleanup)
with AgentRegistry.register(AgentType.ARCHITECT):
    # Agent work here
    # Automatically unregistered on exit (even if exception)
    pass

# Manual registration (if context manager not suitable)
registry = AgentRegistry()
try:
    registry.register_agent(AgentType.CODE_DEVELOPER)
    # ... do work ...
finally:
    registry.unregister_agent(AgentType.CODE_DEVELOPER)
```

**Features**:
- Thread-safe locking (`threading.Lock`)
- Singleton pattern (`__new__` method)
- PID tracking (know which process owns agent)
- Timestamp tracking (when agent started)
- Clear error messages: "Agent 'X' already running! PID: 12345"

**When to Use**:
- ✅ Prevent duplicate agent instances
- ✅ Prevent file corruption from concurrent writes
- ✅ Ensure single source of truth
- ✅ Track which agents are running

**Fitness for Common Use Cases**:
- Agent singleton enforcement: **100%** (perfect fit)
- File lock: **70%** (works, but consider using registry)
- Resource lock: **50%** (works for agent-level resources)

**NEVER Use Instead**:
- ❌ PID files (manual, error-prone)
- ❌ File locks (less semantic)
- ❌ Database locks (external dependency)
- ❌ Redis locks (overkill)

---

### 4. Configuration Management ⚙️

#### Component: ConfigManager

**Location**: `coffee_maker/config/manager.py`

**What**: Centralized configuration management with fallbacks

**API**:
```python
from coffee_maker.config.manager import ConfigManager

# Get API keys (with fallback support)
anthropic_key = ConfigManager.get_anthropic_api_key()
openai_key = ConfigManager.get_openai_api_key()
gemini_key = ConfigManager.get_gemini_api_key()
github_token = ConfigManager.get_github_token()

# Raises APIKeyMissingError if not found in any location
```

**Features**:
- Multiple fallback sources (env vars, .env files, config files)
- Caching (load once, reuse)
- Custom exceptions (`ConfigurationError`, `APIKeyMissingError`)
- Comprehensive docstrings

**Fallback Order**:
1. Environment variable (e.g., `ANTHROPIC_API_KEY`)
2. `.env` file in project root
3. User config file (`~/.config/coffee_maker/config.json`)

**When to Use**:
- ✅ Need API keys (Anthropic, OpenAI, Gemini, GitHub)
- ✅ Need environment-specific config
- ✅ Need fallback values
- ✅ Want consistent error handling

**Fitness for Common Use Cases**:
- API key loading: **100%** (perfect fit)
- App configuration: **90%** (extend if needed)
- Secret management: **80%** (works, but consider vault for prod)

**NEVER Use Instead**:
- ❌ Direct `os.getenv("API_KEY")` (no fallbacks)
- ❌ Hardcoded values (security risk)
- ❌ Manual `.env` parsing (reinventing wheel)
- ❌ Config files without fallbacks

---

### 5. File I/O (JSON) 📄

#### Component: Atomic File Utilities

**Location**: `coffee_maker/utils/file_io.py`

**What**: Atomic file read/write operations with proper encoding

**API**:
```python
from coffee_maker.utils.file_io import read_json, write_json

# Read JSON file
data = read_json("path/to/file.json")

# Write JSON file (atomically - no corruption risk)
write_json("path/to/file.json", data)
```

**Features**:
- **Atomic writes**: Temp file + rename (prevents corruption)
- **UTF-8 encoding**: Consistent across all files
- **Standard formatting**: indent=2 for readability
- **Error handling**: Comprehensive exceptions

**Implementation**:
```python
def write_json(file_path: str, data: Dict):
    """Write JSON atomically (no corruption if crash)."""
    temp_file = f"{file_path}.tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    os.rename(temp_file, file_path)  # Atomic operation
```

**When to Use**:
- ✅ Read/write JSON files
- ✅ Config files
- ✅ Data files
- ✅ Status files
- ✅ Any file that must not be corrupted

**Fitness for Common Use Cases**:
- JSON I/O: **100%** (perfect fit)
- Config files: **100%** (perfect fit)
- Status tracking: **100%** (perfect fit)
- Large files (>10MB): **70%** (works, but consider streaming)

**NEVER Use Instead**:
- ❌ Manual `open() + json.load()` (not atomic)
- ❌ `json.dump()` directly (corruption risk if crash)
- ❌ Different encoding per file (inconsistency)

---

### 6. Observability 📊

#### Component: Langfuse Decorators

**Location**: `coffee_maker/langfuse_observe/`

**What**: LLM call tracking with Langfuse

**API**:
```python
from coffee_maker.langfuse_observe import observe

@observe()
def create_technical_spec(priority_name: str):
    """Create spec (tracked by Langfuse)."""
    # LLM calls inside this function are tracked
    spec = llm.invoke(prompt)
    return spec
```

**Features**:
- Automatic LLM call tracking
- Latency measurement
- Cost tracking
- Token usage
- Error tracking
- Trace visualization

**When to Use**:
- ✅ Any function that calls LLM
- ✅ Need to measure performance
- ✅ Need to track costs
- ✅ Need to debug LLM interactions

**Fitness for Common Use Cases**:
- LLM call tracking: **100%** (perfect fit)
- General function tracking: **80%** (works, but overhead)
- Performance profiling: **70%** (works for LLM, not CPU-bound)

**NEVER Use Instead**:
- ❌ Manual logging only (no structured data)
- ❌ print statements (not queryable)
- ❌ No tracking at all (blind to costs/performance)

---

### 7. Prompt Management 📝

#### Component: PromptLoader

**Location**: `coffee_maker/autonomous/prompt_loader.py`

**What**: Centralized prompt template management

**API**:
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

# Load prompt with variable substitution
prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": "PRIORITY 10",
    "SPEC_FILENAME": "SPEC-010.md",
    "PRIORITY_CONTEXT": "..."
})

# Prompt loaded from .claude/commands/create-technical-spec.md
```

**Prompt Location**: `.claude/commands/*.md`

**Variable Format**: `$VARIABLE_NAME` in templates

**Features**:
- Centralized prompts (single source of truth)
- Multi-AI provider support (Claude, Gemini, OpenAI)
- Variable substitution
- Future: Langfuse integration (Phase 2)

**When to Use**:
- ✅ Any LLM prompt
- ✅ Reusable prompt templates
- ✅ Multi-provider support needed
- ✅ Want centralized prompt management

**Fitness for Common Use Cases**:
- Prompt loading: **100%** (perfect fit)
- One-off prompts: **80%** (can still use, but may be overkill)
- Dynamic prompts: **90%** (excellent with variable substitution)

**NEVER Use Instead**:
- ❌ Hardcoded prompts in code (not reusable)
- ❌ Inline strings (scattered, hard to maintain)
- ❌ Prompts in database (adds complexity)

---

### 8. Git Operations 🌿

#### Component: GitOperations Mixin

**Location**: `coffee_maker/autonomous/daemon_git_ops.py`

**What**: Git operations wrapper for agents

**API**:
```python
# Available in agents via mixin
self.git.get_current_branch()
self.git.commit(message)
self.git.push(branch)
self.git.get_commit_message(sha)
self.git.show(sha)  # Get commit diff
```

**Features**:
- Wraps common git operations
- Error handling
- CFR-013 enforcement (roadmap branch only)
- Atomic operations

**When to Use**:
- ✅ Need to interact with git
- ✅ Check current branch
- ✅ Commit code
- ✅ Read commit history

**Fitness for Common Use Cases**:
- Git operations: **100%** (perfect fit)
- Complex git workflows: **70%** (may need direct git CLI)

**NEVER Use Instead**:
- ❌ Direct `subprocess.run(["git", "..."])` (no error handling)
- ❌ GitPython library (adds dependency)

---

### 9. GitHub Integration 🐙

#### Component: gh CLI Wrapper

**Location**: `coffee_maker/utils/github.py`

**What**: GitHub operations via gh CLI

**API**:
```python
from coffee_maker.utils.github import (
    get_pr_status,
    create_pr,
    get_issue_details,
    check_ci_status
)

# Get PR status
pr = get_pr_status(pr_number=123)

# Create PR
pr_url = create_pr(
    title="feat: New feature",
    body="Description...",
    base="main",
    head="feature-branch"
)
```

**Features**:
- Wraps `gh` CLI (official GitHub tool)
- PR operations
- Issue operations
- CI/CD status checks
- Error handling

**When to Use**:
- ✅ Need to interact with GitHub
- ✅ Create/update PRs
- ✅ Read issue details
- ✅ Check CI status

**Fitness for Common Use Cases**:
- GitHub operations: **100%** (perfect fit)
- Advanced GitHub API: **70%** (may need direct API)

**NEVER Use Instead**:
- ❌ Direct API calls (gh CLI is simpler)
- ❌ Manual curl commands (error-prone)
- ❌ PyGithub library (adds heavy dependency)

---

### 10. Notifications 🔔

#### Component: NotificationSystem

**Location**: `coffee_maker/cli/notifications.py`

**What**: Send notifications to user

**API**:
```python
from coffee_maker.cli.notifications import send_notification

# Send notification
send_notification(
    agent="architect",
    message="Technical spec created for PRIORITY 10",
    priority="NORMAL",
    details={"spec_file": "SPEC-010.md"}
)
```

**Storage**: `data/notifications.json`

**Features**:
- File-based storage (observable)
- Priority levels (CRITICAL, HIGH, NORMAL, LOW)
- Timestamp tracking
- Agent attribution

**When to Use**:
- ✅ Notify user of important events
- ✅ Alert user of errors
- ✅ Provide status updates

**Fitness for Common Use Cases**:
- User notifications: **100%** (perfect fit)
- Inter-agent notifications: **50%** (use messaging instead)

**NEVER Use Instead**:
- ❌ Email (too heavyweight, requires SMTP)
- ❌ Slack API (external dependency)
- ❌ SMS (overkill)

---

### 11. Status Tracking 📈

#### Component: Agent Status Files

**Location**: `data/agent_status/{agent}_status.json`

**What**: Track current agent state and health

**API**:
```python
# Written by BaseAgent automatically
# Read by orchestrator for health checks
# Read by user_listener for status queries
```

**Format**:
```json
{
  "agent_type": "architect",
  "state": "working",
  "current_task": {
    "type": "spec_creation",
    "priority": "PRIORITY 10",
    "started_at": "2025-10-18T14:30:00Z"
  },
  "last_heartbeat": "2025-10-18T14:35:00Z",
  "metrics": {
    "tasks_completed": 5,
    "uptime_seconds": 3600
  }
}
```

**When to Use**:
- ✅ Track agent health
- ✅ Show current task
- ✅ Provide status to orchestrator
- ✅ Show user what agents are doing

**Fitness for Common Use Cases**:
- Agent status: **100%** (perfect fit)
- Complex state machines: **60%** (works, but may need extension)

---

### 12. ROADMAP Management 📋

#### Component: ROADMAP.md

**Location**: `docs/roadmap/ROADMAP.md`

**What**: Single source of truth for project priorities

**Format**:
```markdown
### PRIORITY 10: Feature Name
**Status**: 📝 Planned / 🔄 In Progress / ✅ Complete
**Priority**: HIGH / MEDIUM / LOW
**Estimated Effort**: 8-12 hours
**Owner**: code_developer
**Technical Spec**: docs/architecture/specs/SPEC-010.md

**Description**:
[What needs to be done]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
```

**When to Use**:
- ✅ All project planning
- ✅ Priority tracking
- ✅ Work assignment
- ✅ Status visibility

**Owners**:
- **project_manager**: Strategic updates (add/remove priorities)
- **code_developer**: Status updates (Planned → In Progress → Complete)

**NEVER Use Instead**:
- ❌ Jira (external tool, not observable)
- ❌ Trello (external tool, not version controlled)
- ❌ GitHub Projects (not integrated with agents)

---

## 🚫 Common Anti-Patterns (NEVER Do These)

### Anti-Pattern 1: External Event Triggers

**❌ WRONG**:
```bash
# .git/hooks/post-commit
python -m coffee_maker.architect.review
```

**✅ CORRECT**:
```python
# Use orchestrator messaging
self._send_message("architect", {"type": "commit_review_request"})
```

**Why**: Consistency, observability, easier testing

---

### Anti-Pattern 2: Direct Agent Invocation

**❌ WRONG**:
```python
from coffee_maker.autonomous.agents.architect_agent import ArchitectAgent

architect = ArchitectAgent()  # Duplicate instance!
architect.create_spec(...)
```

**✅ CORRECT**:
```python
# Send message via orchestrator
self._send_message("architect", {"type": "spec_creation_request"})
```

**Why**: Singleton enforcement, orchestrator coordination

---

### Anti-Pattern 3: Manual Config Loading

**❌ WRONG**:
```python
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing API key")
```

**✅ CORRECT**:
```python
from coffee_maker.config.manager import ConfigManager
api_key = ConfigManager.get_anthropic_api_key()
```

**Why**: Centralized, tested, has fallback logic

---

### Anti-Pattern 4: Non-Atomic File Writes

**❌ WRONG**:
```python
with open("data.json", "w") as f:
    json.dump(data, f)  # Risk of corruption if crash
```

**✅ CORRECT**:
```python
from coffee_maker.utils.file_io import write_json
write_json("data.json", data)  # Atomic write
```

**Why**: Prevents corruption, consistent encoding

---

### Anti-Pattern 5: Hardcoded Prompts

**❌ WRONG**:
```python
prompt = f"""Create a technical spec for {priority_name}.
Include architecture, implementation plan, and tests."""
```

**✅ CORRECT**:
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames
prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": priority_name
})
```

**Why**: Centralized, reusable, multi-provider support

---

### Anti-Pattern 6: Custom Process Management

**❌ WRONG**:
```python
import subprocess
subprocess.Popen(["python", "-m", "coffee_maker.agents.architect"])
```

**✅ CORRECT**:
```python
# Use orchestrator
orchestrator = OrchestratorAgent()
orchestrator.run_continuous()
```

**Why**: Health monitoring, crash recovery, coordination

---

## 📊 Component Selection Matrix

| Need | Recommended Component | Fitness | Alternative (if <70%) |
|------|---------------------|---------|---------------------|
| **Agent → Agent communication** | Orchestrator messaging | 100% | N/A (no better option) |
| **Agent lifecycle** | OrchestratorAgent | 100% | N/A (no better option) |
| **Prevent duplicate agents** | AgentRegistry | 100% | N/A (no better option) |
| **API keys** | ConfigManager | 100% | N/A (no better option) |
| **JSON I/O** | file_io.py utilities | 100% | N/A (no better option) |
| **LLM tracking** | Langfuse decorators | 100% | Manual logging (30%) |
| **Prompts** | PromptLoader | 100% | Hardcoded (20%) |
| **Git operations** | GitOperations mixin | 100% | Direct subprocess (60%) |
| **GitHub operations** | gh CLI wrapper | 100% | Direct API (70%) |
| **User notifications** | NotificationSystem | 100% | print statements (10%) |
| **Agent status** | Status files | 100% | Custom solution (40%) |
| **Project planning** | ROADMAP.md | 100% | External tool (30%) |

**Guidance**: If fitness <70%, document why existing component insufficient before proposing new one!

---

## 🎓 architect Training Checklist

Before creating ANY technical specification, architect MUST:

- [ ] Read `.claude/CLAUDE.md` (agent responsibilities, tool ownership)
- [ ] Read `docs/architecture/SYSTEM_ARCHITECTURE.md` (system overview)
- [ ] Read `docs/architecture/REUSABLE_COMPONENTS.md` (THIS FILE)
- [ ] Read `.claude/skills/architecture-reuse-check.md` (reuse skill)
- [ ] Identify problem domain (communication / config / etc.)
- [ ] Check component selection matrix (above)
- [ ] Evaluate existing component fitness (0-100%)
- [ ] If <90% fit: Document why insufficient
- [ ] If proposing NEW component: Justify with evidence

**Failure to complete = SPEC REJECTED**

---

## 📚 Further Reading

- [ADR-011: Orchestrator-Based Commit Review](./decisions/ADR-011-orchestrator-based-commit-review.md) - Example of correct component reuse
- [COMMIT_REVIEW_TRIGGER_COMPARISON.md](./COMMIT_REVIEW_TRIGGER_COMPARISON.md) - Git hooks vs orchestrator comparison
- [architecture-reuse-check skill](./../.claude/skills/architecture-reuse-check.md) - Skill for evaluating reuse

---

**Remember**: ALWAYS check existing components BEFORE proposing new ones! ♻️

**architect's Prime Directive**: Don't Repeat Yourself (DRY) - applies to architecture too!
