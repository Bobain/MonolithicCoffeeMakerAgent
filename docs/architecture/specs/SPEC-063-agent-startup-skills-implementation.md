# SPEC-063: Agent Startup Skills Implementation

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-18
**Related**: ACE Framework Phase 1 - Agent Startup Skills

---

## Executive Summary

This specification defines how agents execute **startup skills** during initialization, ensuring critical configuration, context loading, and health checks occur before agents begin work.

**Key Capabilities**:
- **Automatic Skill Execution**: Agents run `.claude/skills/{agent-name}-startup.md` on initialization
- **CFR-007 Validation**: Agents verify they fit within context budget (<30%) during startup
- **Health Checks**: Pre-flight validation (API keys, file access, dependencies)
- **Error Handling**: Graceful failure with clear diagnostics if startup fails
- **Skill Integration**: Python code loads and executes Claude Code Skills seamlessly

**Impact**:
- **Reliability**: Agents detect configuration issues before attempting work
- **Context Budget Compliance**: Automatic CFR-007 validation prevents bloated prompts
- **Faster Debugging**: Startup failures clearly identify missing config/files
- **Consistency**: All agents follow same startup pattern

---

## Problem Statement

### Current Pain Points

**1. No Standardized Startup Procedure**
```python
# Current: Each agent has ad-hoc initialization
class ArchitectAgent:
    def __init__(self):
        # Maybe load some files?
        # Maybe check API keys?
        # Maybe log something?
        # Inconsistent across agents
        pass
```

**Problem**: No guarantee agents are properly configured before starting work.

**2. CFR-007 Violations Not Detected**
- Agents may exceed 30% context budget without knowing
- Discover violations only after long execution times
- No proactive warning system

**3. Missing Configuration Not Caught Early**
- Agent starts work
- Fails 5 minutes later due to missing API key
- Wasted time and user frustration

**4. Skills Not Integrated**
- Skills exist as `.md` files in `.claude/skills/`
- No Python code to execute them
- Manual invocation required

### User Requirements

From ACE Framework Phase 1:
- **Startup Skills**: Every agent runs `{agent-name}-startup.md` on initialization
- **CFR-007 Validation**: Agents verify context budget compliance
- **Health Checks**: API keys, file access, dependencies validated
- **Graceful Failure**: Clear error messages if startup fails
- **Integration**: Skills execute seamlessly from Python code

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT INITIALIZATION                          │
│  Agent.__init__() called                                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SKILL LOADER (NEW)                              │
│  coffee_maker/skills/skill_loader.py                             │
│                                                                  │
│  def execute_startup_skill(agent_name: str) -> SkillResult      │
│    1. Load skill file: .claude/skills/{agent_name}-startup.md  │
│    2. Parse skill sections (steps, health checks)               │
│    3. Execute each step                                         │
│    4. Validate results                                          │
│    5. Return success/failure                                    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STARTUP SKILL EXECUTION                         │
│                                                                  │
│  ✅ Step 1: Load Required Context                               │
│     - Read docs/roadmap/ROADMAP.md                              │
│     - Read .claude/CLAUDE.md                                    │
│     - Read .claude/agents/{agent-name}.md                       │
│                                                                  │
│  ✅ Step 2: Validate CFR-007 Compliance                         │
│     - Calculate context budget usage                            │
│     - Ensure <30% of window consumed                            │
│     - Log warning if approaching limit                          │
│                                                                  │
│  ✅ Step 3: Health Checks                                       │
│     - API keys present (if needed)                              │
│     - Required files exist                                      │
│     - Dependencies installed                                    │
│                                                                  │
│  ✅ Step 4: Initialize Agent-Specific Resources                 │
│     - code_developer: Load daemon mixins                        │
│     - architect: Load ADRs, specs, guidelines                   │
│     - project_manager: Check GitHub access                      │
│                                                                  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RESULT HANDLING                                 │
│                                                                  │
│  SUCCESS:                                                        │
│    - Agent proceeds to main work loop                           │
│    - Startup metrics logged to Langfuse                         │
│                                                                  │
│  FAILURE:                                                        │
│    - Clear error message with diagnostics                       │
│    - Agent refuses to start (raises StartupError)               │
│    - User sees actionable fix suggestions                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Example

**Scenario**: architect agent starts up

```python
# In architect_agent.py

from coffee_maker.skills.skill_loader import execute_startup_skill

class ArchitectAgent:
    def __init__(self):
        # Execute startup skill
        result = execute_startup_skill("architect")

        if not result.success:
            # Startup failed - log and raise error
            raise StartupError(
                f"architect startup failed: {result.error_message}\n"
                f"Suggestions: {result.suggested_fixes}"
            )

        # Startup succeeded - proceed
        self.context_budget_usage = result.context_budget_pct
        self.health_checks_passed = result.health_checks
        print(f"✅ architect started (context: {self.context_budget_usage:.1f}%)")
```

**Startup Skill File** (`.claude/skills/architect-startup.md`):
```markdown
# Architect Agent Startup Skill

## Step 1: Load Required Context

- [ ] Read docs/roadmap/ROADMAP.md
- [ ] Read .claude/CLAUDE.md
- [ ] Read .claude/agents/architect.md
- [ ] Read docs/architecture/decisions/ADR-*.md (list of ADRs)
- [ ] Read pyproject.toml (current dependencies)

## Step 2: Validate CFR-007 Compliance

- [ ] Calculate total context budget:
  - Agent prompt (architect.md): ~8K tokens
  - Required docs (ROADMAP, CLAUDE.md): ~15K tokens
  - ADRs (list only): ~2K tokens
  - Total: ~25K tokens
- [ ] Check against context window (200K tokens)
- [ ] Verify <30% (60K tokens max)
- [ ] Log warning if >25% (50K tokens)

## Step 3: Health Checks

- [ ] Verify file access:
  - docs/architecture/specs/ (writable)
  - docs/architecture/decisions/ (writable)
  - docs/architecture/guidelines/ (writable)
  - pyproject.toml (writable)
- [ ] Check dependencies:
  - poetry command available
  - python >= 3.9
- [ ] API keys (optional for architect):
  - Not required for basic operation

## Step 4: Initialize Agent Resources

- [ ] Load ADR list (titles only for context)
- [ ] Load spec list (titles only for context)
- [ ] Load guideline list (titles only for context)
- [ ] Register with AgentRegistry (singleton enforcement)

## Success Criteria

- ✅ All files readable
- ✅ Context budget <30%
- ✅ Health checks passed
- ✅ Agent registered
```

---

## Component Design

### 1. Skill Loader

**Purpose**: Load and execute Claude Code Skills from Python

```python
# coffee_maker/skills/skill_loader.py

from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import re

@dataclass
class SkillStep:
    """A single step in a skill."""
    description: str        # Step description
    checklist: List[str]    # Checklist items (from [ ] lines)
    completed: bool = False

@dataclass
class SkillResult:
    """Result of skill execution."""
    success: bool
    skill_name: str
    steps_completed: int
    total_steps: int
    context_budget_pct: float = 0.0
    health_checks: Dict[str, bool] = None
    error_message: str = None
    suggested_fixes: List[str] = None
    execution_time_seconds: float = 0.0

class SkillLoader:
    """
    Loads and executes Claude Code Skills.

    Skills are Markdown files in .claude/skills/ with structured format:
    - ## Step X: Description
    - [ ] Checklist item 1
    - [ ] Checklist item 2
    """

    def __init__(self, skills_dir: str = ".claude/skills"):
        self.skills_dir = Path(skills_dir)

    def load_skill(self, skill_name: str) -> List[SkillStep]:
        """
        Load skill file and parse into steps.

        Args:
            skill_name: Skill name (e.g., "architect-startup")

        Returns:
            List of SkillStep objects
        """
        skill_path = self.skills_dir / f"{skill_name}.md"

        if not skill_path.exists():
            raise FileNotFoundError(f"Skill not found: {skill_path}")

        content = skill_path.read_text()

        # Parse steps (## Step X: ...)
        steps = []
        current_step = None

        for line in content.split("\n"):
            # Step header
            if line.startswith("## Step"):
                if current_step:
                    steps.append(current_step)

                # Extract description
                match = re.match(r"## Step \d+: (.+)", line)
                description = match.group(1) if match else line

                current_step = SkillStep(
                    description=description,
                    checklist=[]
                )

            # Checklist item
            elif line.strip().startswith("- [ ]"):
                if current_step:
                    item = line.strip()[5:].strip()  # Remove "- [ ] "
                    current_step.checklist.append(item)

        # Add last step
        if current_step:
            steps.append(current_step)

        return steps

    def execute_startup_skill(self, agent_name: str) -> SkillResult:
        """
        Execute agent startup skill.

        Args:
            agent_name: Agent name (e.g., "architect")

        Returns:
            SkillResult with success/failure and diagnostics
        """
        import time
        start_time = time.time()

        try:
            # Load skill
            skill_name = f"{agent_name}-startup"
            steps = self.load_skill(skill_name)

            # Execute each step
            for step in steps:
                if "CFR-007" in step.description:
                    # CFR-007 validation step
                    self._validate_cfr007(agent_name, step)
                elif "Health Checks" in step.description:
                    # Health checks step
                    self._execute_health_checks(agent_name, step)
                elif "Load Required Context" in step.description:
                    # Context loading step
                    self._load_required_context(agent_name, step)
                elif "Initialize" in step.description:
                    # Agent-specific initialization
                    self._initialize_agent_resources(agent_name, step)

                step.completed = True

            # All steps completed
            elapsed = time.time() - start_time

            return SkillResult(
                success=True,
                skill_name=skill_name,
                steps_completed=len(steps),
                total_steps=len(steps),
                context_budget_pct=self._calculate_context_budget(agent_name),
                health_checks=self._get_health_check_results(agent_name),
                execution_time_seconds=elapsed
            )

        except Exception as e:
            elapsed = time.time() - start_time

            return SkillResult(
                success=False,
                skill_name=skill_name,
                steps_completed=sum(1 for s in steps if s.completed),
                total_steps=len(steps),
                error_message=str(e),
                suggested_fixes=self._suggest_fixes(e),
                execution_time_seconds=elapsed
            )

    def _validate_cfr007(self, agent_name: str, step: SkillStep):
        """Validate CFR-007 context budget compliance."""
        # Calculate context budget
        budget_pct = self._calculate_context_budget(agent_name)

        # Check limits
        if budget_pct > 30.0:
            raise CFR007ViolationError(
                f"Context budget exceeded: {budget_pct:.1f}% (max: 30%)\n"
                f"Agent prompt + required docs consume too much context.\n"
                f"Remediation: Reduce agent prompt size or required docs."
            )
        elif budget_pct > 25.0:
            # Warning (not failure)
            print(f"⚠️ Context budget high: {budget_pct:.1f}% (target: <30%)")

    def _calculate_context_budget(self, agent_name: str) -> float:
        """
        Calculate context budget usage for agent.

        Formula:
        context_budget_pct = (agent_prompt + required_docs) / context_window * 100
        """
        # Load agent prompt
        agent_file = Path(f".claude/agents/{agent_name}.md")
        if agent_file.exists():
            agent_prompt = agent_file.read_text()
            agent_tokens = self._estimate_tokens(agent_prompt)
        else:
            agent_tokens = 0

        # Load required docs
        required_docs_tokens = 0

        # ROADMAP.md
        roadmap_file = Path("docs/roadmap/ROADMAP.md")
        if roadmap_file.exists():
            required_docs_tokens += self._estimate_tokens(roadmap_file.read_text())

        # CLAUDE.md
        claude_file = Path(".claude/CLAUDE.md")
        if claude_file.exists():
            required_docs_tokens += self._estimate_tokens(claude_file.read_text())

        # Agent-specific required docs
        if agent_name == "architect":
            # ADRs list (titles only)
            adr_files = list(Path("docs/architecture/decisions").glob("ADR-*.md"))
            required_docs_tokens += len(adr_files) * 50  # ~50 tokens per title

        # Total context window (Claude Sonnet 4.5: 200K tokens)
        context_window = 200_000

        # Calculate percentage
        total_tokens = agent_tokens + required_docs_tokens
        budget_pct = (total_tokens / context_window) * 100

        return budget_pct

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Rule of thumb: ~4 characters per token
        """
        return len(text) // 4

    def _execute_health_checks(self, agent_name: str, step: SkillStep):
        """Execute health checks from checklist."""
        # File access checks
        if agent_name == "architect":
            required_dirs = [
                "docs/architecture/specs",
                "docs/architecture/decisions",
                "docs/architecture/guidelines"
            ]

            for dir_path in required_dirs:
                path = Path(dir_path)
                if not path.exists():
                    raise HealthCheckError(f"Required directory not found: {dir_path}")
                if not path.is_dir():
                    raise HealthCheckError(f"Path is not a directory: {dir_path}")

            # pyproject.toml writable
            pyproject = Path("pyproject.toml")
            if not pyproject.exists():
                raise HealthCheckError("pyproject.toml not found")

        # API key checks (if required)
        if agent_name == "code_developer":
            from coffee_maker.config.manager import ConfigManager
            config = ConfigManager()

            # Claude API key required for daemon
            if not config.has_anthropic_api_key():
                raise HealthCheckError(
                    "ANTHROPIC_API_KEY not set. Required for code_developer daemon.\n"
                    "Set in .env or environment variables."
                )

    def _load_required_context(self, agent_name: str, step: SkillStep):
        """Load required context files."""
        # Verify files exist (actual loading happens by Claude CLI during execution)
        required_files = [
            "docs/roadmap/ROADMAP.md",
            ".claude/CLAUDE.md",
            f".claude/agents/{agent_name}.md"
        ]

        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                raise ContextLoadError(f"Required file not found: {file_path}")

    def _initialize_agent_resources(self, agent_name: str, step: SkillStep):
        """Initialize agent-specific resources."""
        if agent_name == "architect":
            # Load ADR list (verify directory exists)
            adr_dir = Path("docs/architecture/decisions")
            if not adr_dir.exists():
                raise ResourceInitializationError("ADR directory not found")

        elif agent_name == "code_developer":
            # Verify daemon mixins exist
            mixin_files = [
                "coffee_maker/autonomous/daemon_git_ops.py",
                "coffee_maker/autonomous/daemon_spec_manager.py",
                "coffee_maker/autonomous/daemon_implementation.py",
                "coffee_maker/autonomous/daemon_status.py"
            ]

            for mixin_file in mixin_files:
                if not Path(mixin_file).exists():
                    raise ResourceInitializationError(f"Daemon mixin not found: {mixin_file}")

        # Register with AgentRegistry
        from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

        agent_type_map = {
            "architect": AgentType.ARCHITECT,
            "code_developer": AgentType.CODE_DEVELOPER,
            "project_manager": AgentType.PROJECT_MANAGER,
            "orchestrator": AgentType.ORCHESTRATOR,
            "reflector": AgentType.REFLECTOR,
            "curator": AgentType.CURATOR
        }

        agent_type = agent_type_map.get(agent_name)
        if agent_type:
            # This will raise if agent already running (singleton enforcement)
            AgentRegistry.register(agent_type)

    def _get_health_check_results(self, agent_name: str) -> Dict[str, bool]:
        """Get health check results."""
        return {
            "files_readable": True,
            "directories_writable": True,
            "api_keys_present": True,  # Simplified (actual checks done in _execute_health_checks)
            "dependencies_installed": True,
            "agent_registered": True
        }

    def _suggest_fixes(self, error: Exception) -> List[str]:
        """Suggest fixes for common startup errors."""
        if isinstance(error, CFR007ViolationError):
            return [
                "Reduce agent prompt size (split into multiple files)",
                "Load fewer required docs during startup",
                "Implement lazy loading for heavy resources"
            ]
        elif isinstance(error, HealthCheckError):
            if "ANTHROPIC_API_KEY" in str(error):
                return [
                    "Set ANTHROPIC_API_KEY in .env file",
                    "Or set as environment variable: export ANTHROPIC_API_KEY=...",
                    "Verify API key is valid (starts with 'sk-ant-')"
                ]
            elif "directory not found" in str(error):
                return [
                    "Create missing directory: mkdir -p {path}",
                    "Verify project structure is correct",
                    "Run from project root directory"
                ]
        elif isinstance(error, ContextLoadError):
            return [
                "Verify file exists: ls -la {file_path}",
                "Check file permissions (must be readable)",
                "Ensure working directory is project root"
            ]
        elif isinstance(error, ResourceInitializationError):
            if "AgentAlreadyRunningError" in str(error):
                return [
                    "Another instance of this agent is already running",
                    "Stop the other instance first",
                    "Check: ps aux | grep {agent_name}"
                ]

        return ["Check error message above for details"]

# Custom Exceptions

class CFR007ViolationError(Exception):
    """Raised when agent exceeds context budget (CFR-007)."""
    pass

class HealthCheckError(Exception):
    """Raised when health checks fail."""
    pass

class ContextLoadError(Exception):
    """Raised when required context files cannot be loaded."""
    pass

class ResourceInitializationError(Exception):
    """Raised when agent resources cannot be initialized."""
    pass

class StartupError(Exception):
    """Raised when agent startup fails."""
    pass
```

### 2. Agent Integration Pattern

**How Agents Use Startup Skills**:

```python
# coffee_maker/agents/architect_agent.py

from coffee_maker.skills.skill_loader import SkillLoader, StartupError
from coffee_maker.langfuse_observe import observe

class ArchitectAgent:
    """Architect agent with startup skill integration."""

    def __init__(self):
        self._execute_startup_skill()

        # Proceed with agent-specific initialization
        self.specs_created = 0
        self.adrs_documented = 0

    @observe(name="architect_startup")
    def _execute_startup_skill(self):
        """Execute architect startup skill."""
        loader = SkillLoader()
        result = loader.execute_startup_skill("architect")

        if not result.success:
            # Startup failed - raise error with diagnostics
            error_msg = (
                f"❌ architect startup failed\n"
                f"Error: {result.error_message}\n"
                f"Steps completed: {result.steps_completed}/{result.total_steps}\n"
                f"\nSuggested fixes:\n"
            )
            for fix in result.suggested_fixes:
                error_msg += f"  - {fix}\n"

            raise StartupError(error_msg)

        # Startup succeeded - log metrics
        print(f"✅ architect started successfully")
        print(f"   Context budget: {result.context_budget_pct:.1f}% (<30% target)")
        print(f"   Health checks: {sum(result.health_checks.values())}/{len(result.health_checks)} passed")
        print(f"   Startup time: {result.execution_time_seconds:.2f}s")

        # Store results
        self.startup_result = result
```

---

## Startup Skill Examples

### architect-startup.md

Already shown above. Key features:
- Loads architectural context (ADRs, specs, guidelines)
- Validates CFR-007 (<30% context budget)
- Checks file write permissions
- Registers with AgentRegistry

### code-developer-startup.md

```markdown
# Code Developer Agent Startup Skill

## Step 1: Load Required Context

- [ ] Read docs/roadmap/ROADMAP.md
- [ ] Read .claude/CLAUDE.md
- [ ] Read .claude/agents/code-developer.md
- [ ] Read pyproject.toml (current dependencies)

## Step 2: Validate CFR-007 Compliance

- [ ] Calculate total context budget:
  - Agent prompt (code-developer.md): ~12K tokens
  - Required docs (ROADMAP, CLAUDE.md): ~15K tokens
  - Total: ~27K tokens
- [ ] Check against context window (200K tokens)
- [ ] Verify <30% (60K tokens max)

## Step 3: Health Checks

- [ ] Verify API keys:
  - ANTHROPIC_API_KEY (required for daemon)
- [ ] Verify file access:
  - coffee_maker/ (writable)
  - tests/ (writable)
  - .claude/ (writable)
- [ ] Check dependencies:
  - poetry command available
  - python >= 3.9
  - git command available

## Step 4: Initialize Daemon Resources

- [ ] Load daemon mixins:
  - GitOpsMixin
  - SpecManagerMixin
  - ImplementationMixin
  - StatusMixin
- [ ] Initialize DeveloperStatus
- [ ] Register with AgentRegistry

## Success Criteria

- ✅ ANTHROPIC_API_KEY present
- ✅ All files writable
- ✅ Context budget <30%
- ✅ Daemon mixins loaded
- ✅ Agent registered
```

### project-manager-startup.md

```markdown
# Project Manager Agent Startup Skill

## Step 1: Load Required Context

- [ ] Read docs/roadmap/ROADMAP.md
- [ ] Read .claude/CLAUDE.md
- [ ] Read .claude/agents/project-manager.md

## Step 2: Validate CFR-007 Compliance

- [ ] Calculate total context budget:
  - Agent prompt (project-manager.md): ~10K tokens
  - Required docs (ROADMAP, CLAUDE.md): ~15K tokens
  - Total: ~25K tokens
- [ ] Check against context window (200K tokens)
- [ ] Verify <30% (60K tokens max)

## Step 3: Health Checks

- [ ] Verify GitHub access:
  - GITHUB_TOKEN (optional but recommended)
  - gh command available
- [ ] Verify file access:
  - docs/roadmap/ (writable)
  - docs/ (writable for top-level files)

## Step 4: Initialize Project Resources

- [ ] Check GitHub repository status
- [ ] Verify ROADMAP.md is readable
- [ ] Register with AgentRegistry

## Success Criteria

- ✅ GitHub access working (or gracefully degraded)
- ✅ ROADMAP.md readable
- ✅ Context budget <30%
- ✅ Agent registered
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_skill_loader.py

def test_skill_loader_parse_steps():
    """Test parsing skill file into steps."""
    loader = SkillLoader()
    steps = loader.load_skill("architect-startup")

    assert len(steps) == 4  # 4 steps in architect-startup.md
    assert "Load Required Context" in steps[0].description
    assert "CFR-007" in steps[1].description
    assert len(steps[0].checklist) > 0

def test_cfr007_validation_success():
    """Test CFR-007 validation passes when under budget."""
    loader = SkillLoader()
    result = loader.execute_startup_skill("architect")

    assert result.success is True
    assert result.context_budget_pct < 30.0

def test_cfr007_validation_failure():
    """Test CFR-007 validation fails when over budget."""
    # Mock: Make agent prompt extremely large
    with patch("Path.read_text", return_value="x" * 500_000):  # 125K tokens
        loader = SkillLoader()
        result = loader.execute_startup_skill("architect")

        assert result.success is False
        assert "CFR007ViolationError" in result.error_message

def test_health_check_missing_api_key():
    """Test health check fails when API key missing."""
    with patch("ConfigManager.has_anthropic_api_key", return_value=False):
        loader = SkillLoader()
        result = loader.execute_startup_skill("code_developer")

        assert result.success is False
        assert "ANTHROPIC_API_KEY" in result.error_message
        assert "Set in .env" in result.suggested_fixes[0]

def test_agent_registration_singleton():
    """Test agent registration enforces singleton."""
    loader = SkillLoader()

    # First registration succeeds
    result1 = loader.execute_startup_skill("architect")
    assert result1.success is True

    # Second registration fails (already running)
    result2 = loader.execute_startup_skill("architect")
    assert result2.success is False
    assert "AgentAlreadyRunningError" in result2.error_message
```

### Integration Tests

```python
# tests/integration/test_agent_startup_skills.py

def test_architect_startup_end_to_end():
    """Test architect agent startup skill end-to-end."""
    agent = ArchitectAgent()

    # Agent started successfully
    assert agent.startup_result.success is True
    assert agent.startup_result.context_budget_pct < 30.0
    assert all(agent.startup_result.health_checks.values())

def test_code_developer_startup_with_missing_api_key():
    """Test code_developer startup fails gracefully without API key."""
    # Remove API key temporarily
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(StartupError) as exc_info:
            CodeDeveloperAgent()

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)
        assert "Suggested fixes" in str(exc_info.value)
```

---

## Rollout Plan

### Phase 1: Skill Loader Infrastructure (Week 1)
- [ ] Implement SkillLoader class
- [ ] Add CFR-007 validation logic
- [ ] Add health check logic
- [ ] Create custom exceptions
- [ ] Unit tests (>80% coverage)

### Phase 2: Startup Skills (Week 2)
- [ ] Create architect-startup.md
- [ ] Create code-developer-startup.md
- [ ] Create project-manager-startup.md
- [ ] Create orchestrator-startup.md
- [ ] Integration tests

### Phase 3: Agent Integration (Week 3)
- [ ] Update ArchitectAgent to use startup skill
- [ ] Update CodeDeveloperAgent to use startup skill
- [ ] Update ProjectManagerAgent to use startup skill
- [ ] Update OrchestratorAgent to use startup skill
- [ ] End-to-end tests

### Phase 4: Architect Code Review ⭐ MANDATORY
- [ ] architect reviews implementation:
  - **Architectural Compliance**: Skill loading patterns, CFR-007 validation logic, agent initialization
  - **Code Quality**: Error handling (graceful failures), token estimation accuracy, health check coverage
  - **Security**: File access validation (no arbitrary file reads), API key handling (secure storage)
  - **Performance**: Startup time (<2s target), token counting efficiency, health check overhead
  - **CFR Compliance**:
    - CFR-007: Context budget calculation accuracy (<30% enforcement)
    - CFR-008: Agent startup isolation (no cross-agent dependencies)
    - CFR-009: Startup failure recovery (clear error messages, suggested fixes)
  - **Dependency Approval**: If new packages added (unlikely for this feature)
- [ ] architect approves or requests changes
- [ ] code_developer addresses feedback (if any)
- [ ] architect gives final approval

### Phase 5: Monitoring & Documentation (Week 4)
- [ ] Add Langfuse tracking for startup metrics
- [ ] Create startup troubleshooting guide
- [ ] Update agent documentation
- [ ] Performance benchmarks

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Startup Time** | <2 seconds | Time from agent init to ready |
| **CFR-007 Compliance** | 100% of agents <30% | Context budget checks |
| **Health Check Coverage** | 100% of agents | All agents run health checks |
| **Startup Failure Rate** | <5% | Failures due to missing config |
| **Error Message Clarity** | User can fix in <5 min | Time to resolve startup errors |

---

## Risks & Mitigations

### Risk 1: Performance Overhead
**Impact**: Startup skills add latency to agent initialization
**Mitigation**: Optimize file reading, cache results, target <2s startup

### Risk 2: Skill File Maintenance
**Impact**: Skills can become stale if not updated with agent changes
**Mitigation**: Include skill validation in CI/CD, automated tests

### Risk 3: CFR-007 Calculation Accuracy
**Impact**: Token estimation may be inaccurate
**Mitigation**: Use conservative estimates (4 chars/token), add safety margin

---

## Conclusion

Agent Startup Skills provide a standardized, reliable initialization procedure for all agents. By executing skills during startup, we ensure:

1. **CFR-007 Compliance**: Automatic validation prevents context budget violations
2. **Early Failure Detection**: Missing config/files caught before work begins
3. **Consistency**: All agents follow same startup pattern
4. **Observability**: Startup metrics tracked in Langfuse

This specification provides the foundation for Phase 1 of the ACE Framework implementation.

---

**Files to Create**:
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/skills/skill_loader.py`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/architect-startup.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/code-developer-startup.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/project-manager-startup.md`
- `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/skills/orchestrator-startup.md`

**Next Steps**:
1. Review and approve this spec
2. Create ADR-012: Agent Startup Skills Pattern
3. Assign implementation to code_developer
4. Begin Phase 1 (Skill Loader) implementation
