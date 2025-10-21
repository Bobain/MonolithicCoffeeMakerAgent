# Skill: Architecture Reuse Check

**Name**: `architecture-reuse-check`
**Owner**: architect agent
**Purpose**: ALWAYS check for existing architectural components before proposing new solutions
**Priority**: CRITICAL - Must run BEFORE any technical spec creation

---

## When to Use This Skill

**MANDATORY** in these situations:
- ✅ Before creating any technical specification
- ✅ Before proposing any new inter-agent communication mechanism
- ✅ Before adding any new infrastructure component
- ✅ Before suggesting external dependencies (git hooks, cron jobs, etc.)
- ✅ When user asks "how should we implement X?"

**Example Trigger**:
> User: "L'architect doit relire tous les commits du code_developer"

**architect's FIRST action**: Run `architecture-reuse-check` skill

---

## Skill Execution Steps

### Step 1: Identify the Problem Domain

**Question**: What architectural concern does this address?

**Common Domains**:
- 🔄 **Inter-agent communication** (agent A needs to notify agent B)
- 📊 **Data sharing** (multiple agents need access to same data)
- ⏰ **Event triggering** (something happens → trigger action)
- 🗄️ **State persistence** (save/load agent state)
- 📝 **Logging/Observability** (track what agents are doing)
- 🔒 **Synchronization** (prevent concurrent access conflicts)
- 🌐 **External integration** (GitHub, Slack, APIs)

**Output**: "This is an **inter-agent communication** problem - code_developer needs to notify architect"

### Step 2: Check Existing Architecture

**CRITICAL**: Read these files FIRST before proposing anything:

1. **Core Architecture**:
   - `.claude/CLAUDE.md` (Agent responsibilities, tool ownership)
   - `docs/architecture/SYSTEM_ARCHITECTURE.md` (System overview)
   - `coffee_maker/autonomous/orchestrator.py` (Agent orchestration)
   - `coffee_maker/autonomous/agents/base_agent.py` (Base agent capabilities)

2. **Existing Components by Domain**:

   | Domain | Existing Component | Location | Usage |
   |--------|-------------------|----------|-------|
   | **Inter-agent communication** | Orchestrator messaging | `orchestrator.py` | `_send_message()`, `_read_messages()` |
   | **File-based messaging** | Message inbox/outbox | `data/agent_messages/{agent}_inbox/` | JSON files |
   | **Status tracking** | Agent status files | `data/agent_status/{agent}_status.json` | Heartbeat, current task |
   | **Singleton enforcement** | AgentRegistry | `agent_registry.py` | `AgentRegistry.register()` |
   | **Git operations** | GitOperations mixin | `daemon_git_ops.py` | `self.git.commit()`, etc. |
   | **Langfuse observability** | Decorators | `langfuse_observe/` | `@observe()`, trace tracking |
   | **Prompt management** | PromptLoader | `autonomous/prompt_loader.py` | `load_prompt()` |
   | **Configuration** | ConfigManager | `config/manager.py` | `ConfigManager.get_api_key()` |
   | **File I/O** | Atomic utilities | `utils/file_io.py` | `read_json()`, `write_json()` |
   | **Notifications** | NotificationSystem | `cli/notifications.py` | Send alerts to user |
   | **GitHub integration** | gh CLI wrapper | `utils/github.py` | PR, issues, CI status |

3. **Architecture Patterns**:
   - **Mixins**: Daemon uses composition (SpecManagerMixin, ImplementationMixin)
   - **Singletons**: Critical resources (AgentRegistry, HTTPConnectionPool)
   - **File-based IPC**: All inter-agent communication via JSON files
   - **Observability-first**: Langfuse decorators everywhere
   - **Asynchronous**: Background agents poll, don't block

**Output Example**:
```
✅ FOUND: Orchestrator messaging system exists!
   - File: coffee_maker/autonomous/orchestrator.py
   - Feature: File-based inter-agent messaging
   - API: BaseAgent._send_message(recipient, message)
   - Storage: data/agent_messages/{agent}_inbox/
   - Format: JSON files with type, sender, recipient, content

✅ FOUND: BaseAgent has messaging capabilities!
   - File: coffee_maker/autonomous/agents/base_agent.py
   - Methods: _send_message(), _read_messages()
   - All agents inherit this (code_developer, architect, etc.)
```

### Step 3: Evaluate Reuse vs New Component

**Decision Matrix**:

| Existing Component Fitness | Decision | Action |
|---------------------------|----------|--------|
| **Perfect fit** (90-100%) | ✅ REUSE | Use existing component as-is |
| **Good fit** (70-89%) | ✅ EXTEND | Extend existing component with new feature |
| **Partial fit** (50-69%) | ⚠️ ADAPT | Adapt existing pattern to new use case |
| **Poor fit** (<50%) | ❌ NEW | Justify why existing components don't work, then create new |

**Evaluation Criteria**:
1. **Functionality**: Does existing component provide needed capability?
2. **API Compatibility**: Can we use existing API or need small extension?
3. **Performance**: Does existing component meet performance requirements?
4. **Consistency**: Does reusing maintain architectural consistency?
5. **Maintenance**: Does reusing reduce or increase maintenance burden?

**Example Evaluation**:
```
Problem: code_developer needs to notify architect after commits

Existing Component: Orchestrator messaging
  ✅ Functionality: 100% (exactly what we need - agent A → agent B)
  ✅ API Compatibility: 100% (_send_message() already exists)
  ✅ Performance: 100% (5-30s latency acceptable)
  ✅ Consistency: 100% (same as all other inter-agent communication)
  ✅ Maintenance: 100% (reusing existing code = no new code to maintain)

SCORE: 100% - PERFECT FIT

DECISION: ✅ REUSE orchestrator messaging (no new component needed)
```

### Step 4: Document Reuse Rationale

**ALWAYS include this section in specs**:

```markdown
## Architecture Reuse Analysis

### Existing Components Evaluated

1. **Orchestrator Messaging** (coffee_maker/autonomous/orchestrator.py)
   - **Fitness**: 100% (perfect fit)
   - **Why**: File-based inter-agent messaging exactly matches our need
   - **Decision**: ✅ REUSE

2. **Git Hooks** (external to our architecture)
   - **Fitness**: 20% (external dependency, not part of agent system)
   - **Why**: Would bypass orchestrator, lose observability
   - **Decision**: ❌ REJECT

### Reuse Benefits

- ✅ No new infrastructure code
- ✅ Uses existing `_send_message()` API
- ✅ Full observability (orchestrator dashboard)
- ✅ Consistent with other inter-agent communication
- ✅ Easier to test (mock messages)

### Trade-offs Accepted

- ⚠️ Slight latency (5-30s vs <1s with git hooks)
- ✅ But: Consistency + observability >> slight latency
```

### Step 5: Red Flags - When NOT to Reuse

**Reject reuse if**:
1. ❌ **Performance critical**: Existing component 10x slower than requirement
2. ❌ **Functional mismatch**: Would require extensive hacks to make it work
3. ❌ **Security risk**: Reusing introduces vulnerability
4. ❌ **Technical debt**: Existing component is deprecated/scheduled for removal

**But ALWAYS justify**:
```markdown
## Why NOT Reusing Existing Component X

Problem: Existing component X has these CRITICAL issues:
1. [Issue 1 with evidence]
2. [Issue 2 with evidence]

Alternatives Considered:
- Option A: Extend component X → Rejected because [reason]
- Option B: Adapt pattern from Y → Rejected because [reason]
- Option C: Create new component → ✅ ACCEPTED because [reason]

Justification for New Component:
- [Why new component is necessary]
- [Why cannot adapt existing]
- [Benefits outweigh maintenance cost]
```

---

## Key Architectural Components to ALWAYS Check

### 1. Inter-Agent Communication

**Existing Solution**: Orchestrator file-based messaging

**When to Use**:
- ✅ Agent A needs to notify Agent B
- ✅ Agent needs to send data to another agent
- ✅ Agent needs to request action from another agent

**API**:
```python
# Send message
self._send_message("architect", {
    "type": "commit_review_request",
    "content": {...}
})

# Read messages
messages = self._read_messages(type_filter="commit_review_request")
```

**Location**: `coffee_maker/autonomous/agents/base_agent.py`

**NEVER propose**: Git hooks, direct function calls between agents, shared memory

### 2. Agent Orchestration

**Existing Solution**: OrchestratorAgent

**When to Use**:
- ✅ Need to launch multiple agents
- ✅ Need to coordinate agent lifecycle
- ✅ Need health monitoring and crash recovery

**API**:
```python
orchestrator = OrchestratorAgent()
orchestrator.run_continuous()
```

**Location**: `coffee_maker/autonomous/orchestrator.py`

**NEVER propose**: Custom process managers, systemd services, supervisor

### 3. Singleton Enforcement

**Existing Solution**: AgentRegistry

**When to Use**:
- ✅ Ensure only ONE instance of agent type runs
- ✅ Prevent concurrent access conflicts
- ✅ Track which agents are running

**API**:
```python
with AgentRegistry.register(AgentType.ARCHITECT):
    # Agent work here (automatically unregistered on exit)
    pass
```

**Location**: `coffee_maker/autonomous/agent_registry.py`

**NEVER propose**: PID files, lock files, database locks

### 4. Configuration Management

**Existing Solution**: ConfigManager

**When to Use**:
- ✅ Need API keys (Anthropic, OpenAI, Gemini, GitHub)
- ✅ Need environment-specific config
- ✅ Need fallback values

**API**:
```python
api_key = ConfigManager.get_anthropic_api_key()
```

**Location**: `coffee_maker/config/manager.py`

**NEVER propose**: Direct `os.getenv()`, hardcoded values, config files

### 5. File I/O

**Existing Solution**: Atomic file utilities

**When to Use**:
- ✅ Read/write JSON files
- ✅ Atomic writes (prevent corruption)
- ✅ Consistent encoding (UTF-8)

**API**:
```python
from coffee_maker.utils.file_io import read_json, write_json

data = read_json("path/to/file.json")
write_json("path/to/file.json", data)
```

**Location**: `coffee_maker/utils/file_io.py`

**NEVER propose**: Manual `open()` + `json.load()`, non-atomic writes

### 6. Observability

**Existing Solution**: Langfuse decorators

**When to Use**:
- ✅ Track LLM calls
- ✅ Measure latency and costs
- ✅ Debug agent executions

**API**:
```python
from coffee_maker.langfuse_observe import observe

@observe()
def my_function():
    pass
```

**Location**: `coffee_maker/langfuse_observe/`

**NEVER propose**: Custom logging only, print statements, no tracking

### 7. Prompt Management

**Existing Solution**: PromptLoader

**When to Use**:
- ✅ Load prompts for LLM calls
- ✅ Support multiple AI providers (Claude, Gemini, OpenAI)
- ✅ Centralized prompt templates

**API**:
```python
from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

prompt = load_prompt(PromptNames.CREATE_TECHNICAL_SPEC, {
    "PRIORITY_NAME": "PRIORITY 10",
    ...
})
```

**Location**: `coffee_maker/autonomous/prompt_loader.py`

**NEVER propose**: Hardcoded prompts, inline strings, scattered templates

---

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: External Triggers (Git Hooks, Cron)

**Problem**: Bypasses orchestrator, loses observability

**Example (WRONG)**:
```bash
# .git/hooks/post-commit
python -m coffee_maker.architect.review
```

**Correct Solution**:
```python
# Use orchestrator messaging
self._send_message("architect", {...})
```

**Why**: Consistency + observability + easier testing

### ❌ Anti-Pattern 2: Direct Agent Invocation

**Problem**: Breaks singleton enforcement, bypasses orchestrator

**Example (WRONG)**:
```python
from coffee_maker.autonomous.agents.architect_agent import ArchitectAgent

architect = ArchitectAgent()  # ❌ Creates duplicate instance
architect.create_spec(...)
```

**Correct Solution**:
```python
# Send message to architect via orchestrator
self._send_message("architect", {
    "type": "spec_creation_request",
    ...
})
```

**Why**: Singleton enforcement + orchestrator coordination

### ❌ Anti-Pattern 3: Custom Config Loading

**Problem**: Duplicates config logic, no fallbacks, inconsistent

**Example (WRONG)**:
```python
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Missing API key")
```

**Correct Solution**:
```python
from coffee_maker.config.manager import ConfigManager

api_key = ConfigManager.get_anthropic_api_key()  # ✅ Has fallbacks
```

**Why**: Centralized, tested, has fallback logic

### ❌ Anti-Pattern 4: Manual File I/O

**Problem**: No atomic writes, risk of corruption, inconsistent encoding

**Example (WRONG)**:
```python
with open("data.json", "w") as f:
    json.dump(data, f)  # ❌ Not atomic
```

**Correct Solution**:
```python
from coffee_maker.utils.file_io import write_json

write_json("data.json", data)  # ✅ Atomic write
```

**Why**: Prevents corruption, consistent encoding

---

## Skill Output Format

When running this skill, architect MUST output:

```markdown
## 🔍 Architecture Reuse Check (Skill: architecture-reuse-check)

### Problem Domain
[Inter-agent communication / Data sharing / Event triggering / etc.]

### Existing Components Evaluated

#### Component 1: [Name]
- **Location**: [File path]
- **Functionality**: [What it provides]
- **Fitness Score**: [0-100%]
- **Decision**: [✅ REUSE / ⚠️ EXTEND / ❌ REJECT]
- **Rationale**: [Why?]

#### Component 2: [Name]
...

### Final Decision

**Chosen Approach**: [Reuse component X / Extend component Y / Create new component Z]

**Justification**:
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Reuse Benefits**:
- ✅ [Benefit 1]
- ✅ [Benefit 2]

**Trade-offs Accepted**:
- ⚠️ [Trade-off 1]
- ✅ But: [Why acceptable]
```

---

## Example: Commit Review Use Case

**Trigger**: User asks "architect doit relire tous les commits du code_developer"

### ❌ WRONG (Without Skill)

```markdown
## Technical Specification: Commit Review

### Architecture

Use git post-commit hooks to trigger architect review:

1. Create .git/hooks/post-commit
2. Hook spawns architect subprocess
3. architect performs review
...
```

**Problem**: Didn't check for existing inter-agent communication! Proposed external trigger (git hook) instead of using orchestrator.

### ✅ CORRECT (With Skill)

```markdown
## 🔍 Architecture Reuse Check

### Problem Domain
**Inter-agent communication** - code_developer needs to notify architect after commits

### Existing Components Evaluated

#### Component 1: Orchestrator Messaging
- **Location**: coffee_maker/autonomous/orchestrator.py
- **Functionality**: File-based inter-agent messaging via JSON files
- **Fitness Score**: 100%
- **API**: _send_message(recipient, message), _read_messages()
- **Decision**: ✅ REUSE
- **Rationale**:
  - Exactly matches our need (agent A → agent B)
  - Already exists in BaseAgent (all agents inherit)
  - Full observability via orchestrator dashboard
  - Consistent with all other inter-agent communication

#### Component 2: Git Hooks
- **Location**: External (.git/hooks/)
- **Functionality**: Trigger actions on git events
- **Fitness Score**: 20%
- **Decision**: ❌ REJECT
- **Rationale**:
  - External to our agent system (bypasses orchestrator)
  - No observability (subprocess not tracked)
  - Platform-specific (bash vs cmd)
  - Inconsistent with our architecture patterns

### Final Decision

**Chosen Approach**: ✅ REUSE orchestrator messaging

**Justification**:
1. Orchestrator messaging is a PERFECT fit (100% functional match)
2. No new code needed (_send_message() already exists)
3. Maintains architectural consistency
4. Full observability and debugging support

**Reuse Benefits**:
- ✅ No new infrastructure code
- ✅ Uses existing BaseAgent API
- ✅ Visible in orchestrator dashboard
- ✅ Easier to test (mock JSON messages)
- ✅ Platform-agnostic (Python only)

**Trade-offs Accepted**:
- ⚠️ Slight latency (5-30s polling vs <1s git hook)
- ✅ But: Consistency + observability >> slight latency

---

## Technical Specification

### Architecture (Using Existing Components)

**Component**: Orchestrator messaging (coffee_maker/autonomous/orchestrator.py)

**Workflow**:
1. code_developer commits code
2. code_developer sends message to architect:
   ```python
   self._send_message("architect", {
       "type": "commit_review_request",
       "content": {"commit_sha": "a1b2c3d", ...}
   })
   ```
3. architect polls inbox, reads messages
4. architect reviews commit, updates skills
5. architect sends feedback messages to recipients

**No git hooks needed** - pure orchestrator messaging!
```

---

## Skill Success Metrics

### Quantitative

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Reuse Rate** | >80% | % of specs that reuse existing components |
| **New Components** | <20% | % of specs that create new components |
| **Justification Quality** | 100% | % of new components with proper justification |

### Qualitative

- ✅ Architect ALWAYS checks existing components first
- ✅ No duplicate infrastructure (e.g., two messaging systems)
- ✅ Architectural consistency maintained
- ✅ Technical debt reduced (fewer components to maintain)

---

## Integration with architect Agent

### When architect Creates a Spec

```python
# coffee_maker/autonomous/agents/architect_agent.py

class ArchitectAgent(BaseAgent):
    def create_technical_spec(self, priority_name: str):
        """Create technical specification for a priority.

        MANDATORY: Run architecture-reuse-check skill FIRST!
        """

        # STEP 1: Run architecture-reuse-check skill (MANDATORY)
        logger.info("🔍 Running architecture-reuse-check skill...")
        reuse_analysis = self._run_architecture_reuse_check(priority_name)

        # STEP 2: Create spec using reuse analysis
        logger.info("📝 Creating technical spec based on reuse analysis...")
        spec_content = self._generate_spec_with_reuse(priority_name, reuse_analysis)

        # STEP 3: Write spec file
        self._write_spec_file(priority_name, spec_content)

    def _run_architecture_reuse_check(self, priority_name: str) -> Dict:
        """Run architecture-reuse-check skill.

        Returns:
            Reuse analysis with existing components evaluated
        """

        # Invoke skill (loads from .claude/skills/architecture-reuse-check.md)
        skill_prompt = load_skill("architecture-reuse-check", {
            "PRIORITY_NAME": priority_name,
            "PROBLEM_DESCRIPTION": self._extract_problem_description(priority_name)
        })

        # Execute skill with LLM
        reuse_analysis = self.llm.invoke(skill_prompt)

        return reuse_analysis
```

---

## Skill Checklist (architect Must Complete)

Before proposing ANY new architecture:

- [ ] ✅ Read `.claude/CLAUDE.md` (agent responsibilities, existing tools)
- [ ] ✅ Read `docs/architecture/SYSTEM_ARCHITECTURE.md` (system overview)
- [ ] ✅ Read `coffee_maker/autonomous/orchestrator.py` (orchestration)
- [ ] ✅ Read `coffee_maker/autonomous/agents/base_agent.py` (base capabilities)
- [ ] ✅ Identify problem domain (communication / data sharing / event trigger / etc.)
- [ ] ✅ Search for existing components in that domain
- [ ] ✅ Evaluate fitness (0-100%) for each existing component
- [ ] ✅ Choose: REUSE (>90%) / EXTEND (70-89%) / ADAPT (50-69%) / NEW (<50%)
- [ ] ✅ Document reuse analysis in spec
- [ ] ✅ If NEW component: Justify why existing components insufficient

**Failure to complete checklist = SPEC REJECTED**

---

## References

- [ADR-011: Orchestrator-Based Commit Review](../../docs/architecture/decisions/ADR-011-orchestrator-based-commit-review.md) - Example of correct reuse
- [ADR-010: Architect Commit Review](../../docs/architecture/decisions/ADR-010-code-architect-commit-review-skills-maintenance.md) - Initially proposed git hooks (wrong), corrected by ADR-011
- [Orchestrator Implementation](../../coffee_maker/autonomous/orchestrator.py) - Inter-agent messaging
- [BaseAgent](../../coffee_maker/autonomous/agents/base_agent.py) - Agent capabilities

---

## Appendix: Reuse Decision Tree

```
New requirement received
    │
    ├─ STEP 1: What domain?
    │   ├─ Inter-agent communication → Check orchestrator
    │   ├─ Configuration → Check ConfigManager
    │   ├─ File I/O → Check file_io.py
    │   └─ etc.
    │
    ├─ STEP 2: Existing component found?
    │   ├─ YES → Evaluate fitness (0-100%)
    │   │   ├─ >90% → ✅ REUSE as-is
    │   │   ├─ 70-89% → ⚠️ EXTEND with new feature
    │   │   ├─ 50-69% → ⚠️ ADAPT pattern
    │   │   └─ <50% → Document why insufficient, then propose NEW
    │   │
    │   └─ NO → Can we adapt existing pattern?
    │       ├─ YES → ⚠️ ADAPT
    │       └─ NO → Document alternatives considered, then propose NEW
    │
    └─ STEP 3: Document reuse analysis
        ├─ Existing components evaluated
        ├─ Fitness scores
        ├─ Decision (REUSE/EXTEND/ADAPT/NEW)
        └─ Justification
```

---

**Remember**: "Don't Repeat Yourself" applies to architecture too! ♻️

**architect's Prime Directive**: ALWAYS check existing architecture BEFORE proposing new solutions!
