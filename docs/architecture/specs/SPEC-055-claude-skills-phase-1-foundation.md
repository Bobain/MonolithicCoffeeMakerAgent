# SPEC-055: Claude Skills Integration - Phase 1 (Foundation + High-Value Skills)

**Status**: Draft

**Author**: architect agent

**Date Created**: 2025-10-19

**Last Updated**: 2025-10-19

**Related**: US-055 (PRIORITY 17), SPEC-001 (General Claude Skills Integration), ADR-002 (Integrate Claude Skills)

**Related ADRs**: ADR-002-integrate-claude-skills.md

**Assigned To**: code_developer

---

## Executive Summary

This specification defines Phase 1 of Claude Skills integration: building the **foundation infrastructure** and implementing **3 high-value skills** that deliver immediate 60-70% time savings for code_developer, architect, and project_manager agents. Phase 1 enables Code Execution Tool (available in public beta) for complex multi-step workflows while maintaining 100% backward compatibility with the existing prompt-based system.

**Key Deliverables**:
1. **Infrastructure**: ExecutionController, SkillLoader, SkillRegistry, SkillInvoker, AgentSkillController
2. **code_developer Skills** (3): Test-Driven Implementation, Refactoring, PR Creation
3. **architect Skill** (1): Spec Generator
4. **project_manager Skill** (1): DoD Verification

**Expected Impact**: 60-70% reduction in implementation time for complex priorities, fully automated TDD workflows, and standardized DoD verification.

---

## Problem Statement

### Current Situation

The existing prompt-based system (`.claude/commands/`) works well for:
- ✅ Multi-AI provider support (Claude, Gemini, OpenAI)
- ✅ Creative reasoning and content generation
- ✅ Simple single-step tasks

**Limitations for complex workflows**:
- ❌ Multi-step workflows require multiple separate prompts (no composition)
- ❌ No executable code support (LLM generates code that may have errors)
- ❌ Manual verification required (tests, DoD, PR quality)
- ❌ High time cost for complex priorities (3-6 hours for refactoring)
- ❌ No automatic task-relevance detection (agent must choose prompt explicitly)

**Example Problem**: Refactoring daemon.py (US-013)
- **Current**: 6 hours manual work (analyze → plan → implement → test → commit)
- **With Skills**: 1.5 hours automated (skill handles entire workflow)
- **Time Saved**: 75% reduction (4.5 hours)

### Goal

Implement Claude Skills infrastructure that:
1. **Complements prompts** (not replaces): Skills handle execution, prompts handle reasoning
2. **Reduces time by 60-70%**: Automated multi-step workflows
3. **Maintains backward compatibility**: 100% compatible with existing PromptLoader
4. **Enables composition**: Skills can chain together automatically
5. **Supports Code Execution Tool**: Uses Anthropic's public beta feature

### Non-Goals

**Phase 1 does NOT include**:
- ❌ Migrating existing prompts to skills (prompts stay as-is)
- ❌ Skills for all agents (only code_developer, architect, project_manager in Phase 1)
- ❌ Langfuse integration for skills (Phase 2)
- ❌ Advanced sandboxing (basic security only)
- ❌ Skill marketplace submission (Phase 3)

---

## Requirements

### Functional Requirements

1. **FR-1**: Enable Code Execution Tool with `anthropic-beta: code-execution-2025-08-25` header
2. **FR-2**: Create `.claude/skills/` directory structure (shared + per-agent)
3. **FR-3**: Implement ExecutionController (SKILL_ONLY/PROMPT_ONLY/HYBRID modes)
4. **FR-4**: Implement SkillLoader (loads skills from `.claude/skills/`)
5. **FR-5**: Implement SkillRegistry (automatic skill discovery based on triggers)
6. **FR-6**: Implement SkillInvoker (secure skill execution)
7. **FR-7**: Implement AgentSkillController (per-agent skill orchestration)
8. **FR-8**: Implement Test-Driven Implementation Skill (code_developer)
9. **FR-9**: Implement Refactoring Skill (code_developer)
10. **FR-10**: Implement PR Creation Skill (code_developer)
11. **FR-11**: Implement Spec Generator Skill (architect)
12. **FR-12**: Implement DoD Verification Skill (project_manager)

### Non-Functional Requirements

1. **NFR-1**: Performance: Skill execution < 5 minutes for 90% of skills
2. **NFR-2**: Reliability: >95% success rate for skill execution
3. **NFR-3**: Backward Compatibility: 100% compatible with existing prompts
4. **NFR-4**: Context Budget: Skills must fit within CFR-007 (≤30% agent context)
5. **NFR-5**: Observability: Log all skill executions for debugging
6. **NFR-6**: Security: Sandboxed execution for untrusted code (basic)
7. **NFR-7**: Testability: >80% code coverage for skill infrastructure

### Constraints

- **MUST** maintain multi-AI provider support (prompts still work with Gemini/OpenAI)
- **MUST** use Code Execution Tool (no custom execution environments)
- **MUST** add `pyyaml` dependency (pre-approved for metadata parsing)
- **MUST** work on `roadmap` branch only (CFR-013)
- **MUST NOT** break existing daemon functionality
- **Timeline**: 4 weeks (84-104 hours)

---

## Proposed Solution

### High-Level Approach

Implement a **hybrid architecture** where:
1. **Prompts** handle creative reasoning (multi-provider support maintained)
2. **Skills** handle executable workflows (Claude Code Execution Tool)
3. **ExecutionController** decides which mode to use (SKILL_ONLY/PROMPT_ONLY/HYBRID)

**Key Design Principles**:
- **Complementary, not competing**: Skills + Prompts work together
- **Backward compatible**: Existing PromptLoader unchanged
- **Agent-specific discovery**: Each agent sees only relevant skills
- **Composable**: Skills can chain together (output of skill N → input of skill N+1)
- **Observable**: All executions logged for debugging

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT EXECUTION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │code_developer│  │  architect   │  │project_mgr   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                    │
│         └─────────────────┴──────────────────┘                   │
│                           ▼                                       │
│                ┌─────────────────────┐                          │
│                │ ExecutionController │ ◄── Decides: Skill/Prompt│
│                └─────────┬───────────┘                          │
│                          │                                       │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │SkillLoader  │  │PromptLoader │  │SkillInvoker │            │
│  │  (NEW)      │  │ (Existing)  │  │  (NEW)      │            │
│  └─────┬───────┘  └─────┬───────┘  └─────┬───────┘            │
│        │                │                │                      │
│        ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │SkillRegistry│  │  Prompts    │  │ Code Exec   │            │
│  │  (NEW)      │  │   (MD)      │  │   Tool      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  .claude/skills/       .claude/commands/                         │
│  ├── shared/           ├── *.md                                  │
│  ├── code_developer/   └── PROMPTS_INDEX.md                     │
│  ├── architect/                                                  │
│  └── project_manager/                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Code Execution Tool**: Anthropic's public beta (anthropic-beta: code-execution-2025-08-25)
- **Python 3.9+**: Skill scripts
- **pyyaml**: Skill metadata parsing (SKILL.md frontmatter)
- **Existing**: ClaudeCLIInterface (for API calls)
- **Existing**: PromptLoader (unchanged)

---

## Detailed Design

### Component 1: ExecutionController

**Responsibility**: Unified controller for skills and prompts

**File**: `coffee_maker/autonomous/execution_controller.py`

**Interface**:
```python
from enum import Enum
from typing import Optional, Union
from dataclasses import dataclass


class ExecutionMode(Enum):
    """Execution mode for tasks."""
    PROMPT_ONLY = "prompt"       # Use prompt template (multi-provider)
    SKILL_ONLY = "skill"         # Use skill with Code Execution Tool (Claude only)
    HYBRID = "hybrid"            # Use both (skill for execution, prompt for reasoning)


@dataclass
class ExecutionResult:
    """Result of execution (skill or prompt)."""
    output: any
    mode: ExecutionMode
    skills_used: list[str]
    prompts_used: list[str]
    execution_time: float
    success: bool
    errors: list[str]


class ExecutionController:
    """Unified controller for skills and prompts.

    Example:
        >>> controller = ExecutionController(agent_type=AgentType.CODE_DEVELOPER)
        >>> result = controller.execute(
        ...     task="refactor daemon.py using mixins",
        ...     mode=ExecutionMode.SKILL_ONLY
        ... )
    """

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.skill_loader = SkillLoader(agent_type)
        self.prompt_loader = PromptLoader()
        self.skill_registry = SkillRegistry(agent_type)

    def execute(
        self,
        task: str,
        mode: ExecutionMode = ExecutionMode.HYBRID,
        context: Optional[dict] = None
    ) -> ExecutionResult:
        """Execute task using skills, prompts, or both."""
        if mode == ExecutionMode.SKILL_ONLY:
            return self._execute_skill(task, context)
        elif mode == ExecutionMode.PROMPT_ONLY:
            return self._execute_prompt(task, context)
        else:  # HYBRID
            return self._execute_hybrid(task, context)

    def _execute_skill(self, task: str, context: dict) -> ExecutionResult:
        """Execute skill with Code Execution Tool."""
        # 1. Discover relevant skills
        skills = self.skill_registry.find_skills_for_task(task)

        if not skills:
            raise NoSkillFoundError(f"No skill found for task: {task}")

        # 2. Invoke skills (may compose multiple)
        invoker = SkillInvoker(self.agent_type)
        result = invoker.invoke(skills, context)

        return ExecutionResult(
            output=result.output,
            mode=ExecutionMode.SKILL_ONLY,
            skills_used=[s.name for s in skills],
            prompts_used=[],
            execution_time=result.duration,
            success=result.success,
            errors=result.errors
        )

    def _execute_prompt(self, task: str, context: dict) -> ExecutionResult:
        """Execute prompt with LLM reasoning (existing)."""
        # Use existing PromptLoader (unchanged)
        prompt = self.prompt_loader.load(task, context)

        # Execute via Claude CLI/API
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        cli = ClaudeCLIInterface()
        result = cli.execute_prompt(prompt)

        return ExecutionResult(
            output=result,
            mode=ExecutionMode.PROMPT_ONLY,
            skills_used=[],
            prompts_used=[task],
            execution_time=0,  # Tracked separately
            success=True,
            errors=[]
        )

    def _execute_hybrid(self, task: str, context: dict) -> ExecutionResult:
        """Execute skill + prompt (skill provides data, prompt interprets)."""
        # 1. Execute skill to get data
        skill_result = self._execute_skill(task, context)

        # 2. Use prompt to interpret skill output
        context["skill_output"] = skill_result.output
        prompt_result = self._execute_prompt(task, context)

        return ExecutionResult(
            output=prompt_result.output,
            mode=ExecutionMode.HYBRID,
            skills_used=skill_result.skills_used,
            prompts_used=prompt_result.prompts_used,
            execution_time=skill_result.execution_time,
            success=skill_result.success and prompt_result.success,
            errors=skill_result.errors + prompt_result.errors
        )
```

**Implementation Notes**:
- **Backward compatible**: PromptLoader API unchanged
- **Decision logic**: Agent specifies mode explicitly (no auto-detection in Phase 1)
- **Hybrid mode**: Skill output becomes context for prompt (data + reasoning)
- **Error handling**: Graceful fallback to prompts if skill fails

---

### Component 2: SkillLoader

**Responsibility**: Load skills from `.claude/skills/` directory

**File**: `coffee_maker/autonomous/skill_loader.py`

**Interface**:
```python
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import yaml


@dataclass
class SkillMetadata:
    """Metadata for a Claude Skill."""
    name: str
    version: str
    agent: str
    scope: str  # "shared" or "agent-specific"
    description: str
    triggers: List[str]  # Task descriptions that trigger this skill
    requires: List[str]  # Dependencies (Python packages)
    skill_path: Path

    @classmethod
    def from_skill_md(cls, skill_path: Path) -> 'SkillMetadata':
        """Parse SKILL.md file for metadata."""
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found: {skill_md}")

        content = skill_md.read_text()

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                return cls(
                    name=metadata.get("name", skill_path.name),
                    version=metadata.get("version", "1.0.0"),
                    agent=metadata.get("agent", "shared"),
                    scope=metadata.get("scope", "shared"),
                    description=metadata.get("description", ""),
                    triggers=metadata.get("triggers", []),
                    requires=metadata.get("requires", []),
                    skill_path=skill_path
                )

        raise ValueError(f"Invalid SKILL.md format: {skill_md}")


class SkillLoader:
    """Load Claude Skills from .claude/skills/ directory.

    Example:
        >>> loader = SkillLoader(agent_type=AgentType.CODE_DEVELOPER)
        >>> skills = loader.list_available_skills()
        >>> skill = loader.load("test-driven-implementation")
    """

    def __init__(self, agent_type: AgentType, skills_dir: Optional[Path] = None):
        self.agent_type = agent_type
        self.skills_dir = skills_dir or Path(".claude/skills")
        self.shared_skills_dir = self.skills_dir / "shared"
        self.agent_skills_dir = self.skills_dir / agent_type.value.replace("_", "-")

    def list_available_skills(self) -> List[SkillMetadata]:
        """List all skills available to this agent (shared + agent-specific)."""
        skills = []

        # 1. Load shared skills
        if self.shared_skills_dir.exists():
            for skill_path in self.shared_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    skills.append(SkillMetadata.from_skill_md(skill_path))

        # 2. Load agent-specific skills
        if self.agent_skills_dir.exists():
            for skill_path in self.agent_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    skills.append(SkillMetadata.from_skill_md(skill_path))

        return skills

    def load(self, skill_name: str) -> SkillMetadata:
        """Load a specific skill by name."""
        # Try agent-specific first
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata.from_skill_md(agent_skill_path)

        # Fall back to shared
        shared_skill_path = self.shared_skills_dir / skill_name
        if shared_skill_path.exists():
            return SkillMetadata.from_skill_md(shared_skill_path)

        raise FileNotFoundError(
            f"Skill '{skill_name}' not found for agent {self.agent_type.value}"
        )

    def skill_exists(self, skill_name: str) -> bool:
        """Check if skill exists for this agent."""
        try:
            self.load(skill_name)
            return True
        except FileNotFoundError:
            return False
```

**Implementation Notes**:
- **YAML frontmatter**: Uses `pyyaml` to parse SKILL.md metadata
- **Agent-specific precedence**: Agent-specific skills override shared skills
- **Lazy loading**: Skills loaded on-demand (CFR-007 context budget)
- **Validation**: Checks SKILL.md format, raises clear errors

---

### Component 3: SkillRegistry

**Responsibility**: Automatic skill discovery based on task triggers

**File**: `coffee_maker/autonomous/skill_registry.py`

**Interface**:
```python
from typing import Dict, List
from difflib import get_close_matches


class SkillRegistry:
    """Registry for agent-specific skill discovery.

    Example:
        >>> registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        >>> skills = registry.find_skills_for_task("implement feature with tests")
        >>> # Returns: [SkillMetadata(test-driven-implementation)]
    """

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.loader = SkillLoader(agent_type)
        self._cache = self._build_cache()

    def _build_cache(self) -> Dict[str, List[SkillMetadata]]:
        """Build trigger → skill mapping cache."""
        cache = {}

        for skill in self.loader.list_available_skills():
            for trigger in skill.triggers:
                if trigger not in cache:
                    cache[trigger] = []
                cache[trigger].append(skill)

        return cache

    def find_skills_for_task(self, task: str) -> List[SkillMetadata]:
        """Find skills relevant to a task description (fuzzy matching)."""
        # Exact match first
        if task in self._cache:
            return self._cache[task]

        # Fuzzy match on triggers
        triggers = list(self._cache.keys())
        matches = get_close_matches(task, triggers, n=3, cutoff=0.6)

        skills = []
        for match in matches:
            skills.extend(self._cache[match])

        # Remove duplicates
        return list({skill.name: skill for skill in skills}.values())

    def refresh(self):
        """Refresh skill cache (call after adding new skills)."""
        self._cache = self._build_cache()
```

**Implementation Notes**:
- **Fuzzy matching**: Uses `difflib.get_close_matches()` (60% similarity threshold)
- **Cache**: Pre-builds trigger → skill mapping at startup
- **Refresh**: Can reload skills without restarting agent
- **Deduplication**: Returns unique skills only

---

### Component 4: SkillInvoker

**Responsibility**: Execute skills using Code Execution Tool

**File**: `coffee_maker/autonomous/skill_invoker.py`

**Interface**:
```python
from dataclasses import dataclass
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""
    output: Any
    exit_code: int
    duration: float
    skill_name: str
    errors: List[str]

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class SkillInvoker:
    """Execute Claude Skills with Code Execution Tool.

    Example:
        >>> invoker = SkillInvoker(AgentType.CODE_DEVELOPER)
        >>> result = invoker.invoke([skill_metadata], context={"priority": "US-055"})
        >>> print(result.output)
    """

    def __init__(
        self,
        agent_type: AgentType,
        timeout: int = 300  # 5 minutes default
    ):
        self.agent_type = agent_type
        self.timeout = timeout

    def invoke(
        self,
        skills: List[SkillMetadata],
        context: Dict[str, Any]
    ) -> SkillExecutionResult:
        """Invoke skills with context (skills execute in composition order)."""
        import time
        start = time.time()

        # Execute skills in sequence (composition)
        current_context = context.copy()
        outputs = []
        errors = []

        for skill in skills:
            try:
                result = self._execute_single_skill(skill, current_context)
                outputs.append(result.output)

                # Pass output to next skill
                current_context["previous_skill_output"] = result.output

                if not result.success:
                    errors.append(f"{skill.name}: {result.errors}")

            except Exception as e:
                logger.error(f"Skill {skill.name} failed: {e}")
                errors.append(f"{skill.name}: {str(e)}")

        duration = time.time() - start

        return SkillExecutionResult(
            output=outputs[-1] if outputs else None,
            exit_code=0 if not errors else 1,
            duration=duration,
            skill_name=", ".join([s.name for s in skills]),
            errors=errors
        )

    def _execute_single_skill(
        self,
        skill: SkillMetadata,
        context: Dict[str, Any]
    ) -> SkillExecutionResult:
        """Execute a single skill using Code Execution Tool."""
        import time
        start = time.time()

        # Read skill code
        skill_code = self._read_skill_code(skill)

        # Execute with Code Execution Tool
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        cli = ClaudeCLIInterface()

        # Enable Code Execution Tool
        cli.enable_code_execution()

        # Build prompt for Code Execution Tool
        prompt = f"""
Execute this skill code with the provided context:

**Skill**: {skill.name}
**Context**: {context}

**Code**:
```python
{skill_code}
```

Execute the code and return the output as JSON.
"""

        # Execute
        result = cli.execute_prompt(prompt)

        duration = time.time() - start

        return SkillExecutionResult(
            output=result,
            exit_code=0,
            duration=duration,
            skill_name=skill.name,
            errors=[]
        )

    def _read_skill_code(self, skill: SkillMetadata) -> str:
        """Read skill code from skill directory."""
        # Find Python script in skill directory
        skill_dir = skill.skill_path

        py_script = skill_dir / f"{skill.name}.py"
        if py_script.exists():
            return py_script.read_text()

        raise FileNotFoundError(f"No Python script found in {skill_dir}")
```

**Implementation Notes**:
- **Code Execution Tool**: Uses `anthropic-beta: code-execution-2025-08-25` header
- **Composition**: Skills execute in sequence (output N → input N+1)
- **Timeout**: 5 minutes default (prevents hanging)
- **Error handling**: Catches exceptions, logs errors, continues to next skill
- **Security**: Uses Code Execution Tool's built-in sandboxing (no custom sandbox in Phase 1)

---

### Component 5: AgentSkillController

**Responsibility**: Per-agent skill orchestration

**File**: `coffee_maker/autonomous/agent_skill_controller.py`

**Interface**:
```python
class AgentSkillController:
    """Skill controller for a specific agent.

    Example (code_developer):
        >>> controller = AgentSkillController(AgentType.CODE_DEVELOPER)
        >>> result = controller.execute_task(
        ...     "implement feature with tests",
        ...     context={"priority": "US-055", "files": ["daemon.py"]}
        ... )
        >>> print(result.output)  # TDD workflow result
    """

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.loader = SkillLoader(agent_type)
        self.registry = SkillRegistry(agent_type)
        self.invoker = SkillInvoker(agent_type)

    def execute_task(
        self,
        task_description: str,
        context: Optional[dict] = None
    ) -> SkillExecutionResult:
        """Execute task using relevant skills."""
        # 1. Find relevant skills
        skills = self.registry.find_skills_for_task(task_description)

        if not skills:
            raise NoSkillFoundError(
                f"No skills found for task: {task_description}\n"
                f"Available skills: {self.list_skills()}"
            )

        # 2. Invoke skills
        context = context or {}
        context["task_description"] = task_description
        context["agent_type"] = self.agent_type.value

        result = self.invoker.invoke(skills, context)

        # 3. Track usage (for Langfuse integration in Phase 2)
        self._track_usage(skills, result)

        return result

    def list_skills(self) -> List[str]:
        """List all skills available to this agent."""
        skills = self.loader.list_available_skills()
        return [skill.name for skill in skills]

    def has_skill(self, skill_name: str) -> bool:
        """Check if agent has access to a skill."""
        return self.loader.skill_exists(skill_name)

    def _track_usage(
        self,
        skills: List[SkillMetadata],
        result: SkillExecutionResult
    ):
        """Track skill usage for observability (Phase 2: Langfuse integration)."""
        # TODO: Implement Langfuse tracking in Phase 2
        logger.info(
            f"Agent {self.agent_type.value} executed skills: "
            f"{[s.name for s in skills]} "
            f"(duration: {result.duration:.2f}s, success: {result.success})"
        )
```

**Implementation Notes**:
- **Per-agent**: Each agent gets its own controller
- **Discovery**: Automatically finds relevant skills based on task
- **Tracking**: Logs execution for debugging (Langfuse in Phase 2)
- **Error handling**: Provides clear error messages with available skills

---

## Phase 1 Skills Specifications

### Skill 1: Test-Driven Implementation (code_developer)

**Location**: `.claude/skills/code-developer/test-driven-implementation/`

**Purpose**: Automated TDD workflow (write tests → implement → verify coverage)

**SKILL.md**:
```yaml
---
name: test-driven-implementation
version: 1.0.0
agent: code-developer
scope: agent-specific
description: >
  Automated Test-Driven Development workflow: analyze requirements,
  write comprehensive tests, implement feature, verify 80%+ coverage.

triggers:
  - "implement feature with tests"
  - "test-driven development"
  - "TDD workflow"
  - "implement with TDD"

requires:
  - pytest>=7.0
  - pytest-cov>=4.0

inputs:
  priority:
    type: string
    required: true
    description: Priority to implement (e.g., "US-055")

  spec_path:
    type: string
    required: false
    description: Path to technical spec (if exists)

  files:
    type: list[string]
    required: false
    description: Files to modify (if known)

outputs:
  tests_created:
    type: list[string]
    description: List of test files created

  code_modified:
    type: list[string]
    description: List of code files modified

  coverage:
    type: float
    description: Code coverage percentage

  tests_passing:
    type: bool
    description: All tests passing?

author: architect agent
created: 2025-10-19
---

# Test-Driven Implementation Skill

Automated TDD workflow for code_developer.

## Workflow

1. **Analyze Requirements**: Read spec, understand acceptance criteria
2. **Write Tests**: Create comprehensive test suite (unit + integration)
3. **Run Tests**: Verify tests fail (red phase)
4. **Implement**: Write code to make tests pass
5. **Verify Coverage**: Check 80%+ coverage
6. **Refactor**: Clean up code while keeping tests green
7. **Commit**: Commit with descriptive message

## Expected Time Savings

- **Manual TDD**: 3-4 hours per feature
- **With Skill**: 1-1.5 hours per feature
- **Time Saved**: 50-60% reduction
```

**test-driven-implementation.py**:
```python
"""
Test-Driven Implementation Skill for code_developer.
Automated TDD workflow: tests → implementation → coverage → commit.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute TDD workflow."""
    priority = context["priority"]
    spec_path = context.get("spec_path")
    files = context.get("files", [])

    print(f"Starting TDD workflow for {priority}")

    # Step 1: Analyze requirements
    requirements = analyze_requirements(priority, spec_path)

    # Step 2: Write tests
    tests = write_tests(requirements, files)

    # Step 3: Run tests (expect failures)
    run_tests_expect_fail(tests)

    # Step 4: Implement code
    implementation = implement_code(requirements, tests)

    # Step 5: Verify coverage
    coverage = verify_coverage(tests, implementation)

    # Step 6: Refactor (if needed)
    refactor_if_needed(implementation)

    # Step 7: Commit
    commit_changes(priority, tests, implementation)

    return {
        "tests_created": tests,
        "code_modified": implementation,
        "coverage": coverage,
        "tests_passing": True
    }


def analyze_requirements(priority: str, spec_path: str) -> Dict[str, Any]:
    """Analyze requirements from spec and ROADMAP."""
    # Read spec if exists
    # Read ROADMAP for acceptance criteria
    # Extract functional requirements
    # Identify test scenarios
    pass


def write_tests(requirements: Dict[str, Any], files: list) -> list:
    """Write comprehensive test suite."""
    # Create test files (unit + integration)
    # Write test cases for each requirement
    # Include edge cases and error scenarios
    pass


def run_tests_expect_fail(tests: list) -> bool:
    """Run tests and expect failures (red phase)."""
    # pytest tests
    # Verify tests fail (as expected)
    pass


def implement_code(requirements: Dict[str, Any], tests: list) -> list:
    """Implement code to make tests pass."""
    # Write implementation
    # Run tests iteratively
    # Fix until all tests pass
    pass


def verify_coverage(tests: list, implementation: list) -> float:
    """Verify code coverage >= 80%."""
    # pytest --cov
    # Check coverage percentage
    # Warn if < 80%
    pass


def refactor_if_needed(implementation: list):
    """Refactor code while keeping tests green."""
    # Identify refactoring opportunities
    # Apply refactorings
    # Re-run tests after each refactoring
    pass


def commit_changes(priority: str, tests: list, implementation: list):
    """Commit changes with descriptive message."""
    # git add tests
    # git add implementation
    # git commit -m "feat: Implement {priority} with TDD"
    pass


if __name__ == "__main__":
    # Load context from stdin or file
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 50-60% reduction (3-4 hours → 1-1.5 hours)

---

### Skill 2: Refactoring (code_developer)

**Location**: `.claude/skills/code-developer/refactoring/`

**Purpose**: Automated refactoring with test verification

**SKILL.md**:
```yaml
---
name: refactoring
version: 1.0.0
agent: code-developer
scope: agent-specific
description: >
  Automated refactoring workflow: analyze code, plan refactoring,
  apply transformations, verify tests pass, commit changes.

triggers:
  - "refactor code"
  - "extract mixin"
  - "split file"
  - "automated refactoring"

requires:
  - pytest>=7.0
  - radon>=6.0  # Code complexity metrics

inputs:
  files:
    type: list[string]
    required: true
    description: Files to refactor

  refactoring_type:
    type: string
    required: true
    description: Type of refactoring (extract_mixin, split_file, rename, etc.)

  target:
    type: string
    required: false
    description: Target for refactoring (class name, method name, etc.)

outputs:
  files_modified:
    type: list[string]
    description: Files modified during refactoring

  tests_passing:
    type: bool
    description: All tests still pass?

  complexity_before:
    type: float
    description: Cyclomatic complexity before refactoring

  complexity_after:
    type: float
    description: Cyclomatic complexity after refactoring

author: architect agent
created: 2025-10-19
---

# Refactoring Skill

Automated refactoring workflow for code_developer.

## Workflow

1. **Analyze Code**: Measure complexity, identify smells
2. **Plan Refactoring**: Choose transformations
3. **Run Tests**: Verify tests pass before refactoring
4. **Apply Transformations**: Extract mixins, split files, rename, etc.
5. **Run Tests**: Verify tests still pass after refactoring
6. **Measure Improvement**: Compare complexity before/after
7. **Commit**: Commit with refactoring description

## Expected Time Savings

- **Manual Refactoring**: 6 hours (daemon.py example)
- **With Skill**: 1.5 hours
- **Time Saved**: 75% reduction
```

**refactoring.py**:
```python
"""
Refactoring Skill for code_developer.
Automated refactoring: analyze → plan → transform → test → commit.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute refactoring workflow."""
    files = context["files"]
    refactoring_type = context["refactoring_type"]
    target = context.get("target")

    print(f"Starting refactoring: {refactoring_type} on {files}")

    # Step 1: Analyze code
    complexity_before = analyze_complexity(files)

    # Step 2: Plan refactoring
    plan = plan_refactoring(files, refactoring_type, target)

    # Step 3: Run tests (verify pass before refactoring)
    run_tests_expect_pass()

    # Step 4: Apply transformations
    modified = apply_transformations(plan)

    # Step 5: Run tests (verify still pass after refactoring)
    run_tests_expect_pass()

    # Step 6: Measure improvement
    complexity_after = analyze_complexity(modified)

    # Step 7: Commit
    commit_refactoring(refactoring_type, modified, complexity_before, complexity_after)

    return {
        "files_modified": modified,
        "tests_passing": True,
        "complexity_before": complexity_before,
        "complexity_after": complexity_after
    }


def analyze_complexity(files: List[str]) -> float:
    """Measure cyclomatic complexity using radon."""
    # radon cc --average
    # Return average complexity
    pass


def plan_refactoring(
    files: List[str],
    refactoring_type: str,
    target: str
) -> Dict[str, Any]:
    """Plan refactoring transformations."""
    # Identify code to extract/move
    # Determine new structure
    # Generate transformation plan
    pass


def apply_transformations(plan: Dict[str, Any]) -> List[str]:
    """Apply refactoring transformations."""
    if plan["type"] == "extract_mixin":
        return extract_mixin(plan)
    elif plan["type"] == "split_file":
        return split_file(plan)
    elif plan["type"] == "rename":
        return rename(plan)
    else:
        raise ValueError(f"Unknown refactoring type: {plan['type']}")


def extract_mixin(plan: Dict[str, Any]) -> List[str]:
    """Extract mixin from monolithic class."""
    # Identify methods to extract
    # Create new mixin file
    # Update original class to use mixin
    # Update imports
    pass


def split_file(plan: Dict[str, Any]) -> List[str]:
    """Split large file into smaller modules."""
    # Identify logical groupings
    # Create new files
    # Move code
    # Update imports
    pass


def rename(plan: Dict[str, Any]) -> List[str]:
    """Rename class/method/variable."""
    # Find all references
    # Update all references
    # Update imports
    pass


def run_tests_expect_pass():
    """Run tests and expect all to pass."""
    # pytest
    # Raise exception if any fail
    pass


def commit_refactoring(
    refactoring_type: str,
    modified: List[str],
    complexity_before: float,
    complexity_after: float
):
    """Commit refactoring with metrics."""
    message = f"""refactor: {refactoring_type}

Complexity: {complexity_before:.2f} → {complexity_after:.2f}
Files modified: {len(modified)}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    # git add modified
    # git commit -m message
    pass


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 75% reduction (6 hours → 1.5 hours)

---

### Skill 3: PR Creation (code_developer)

**Location**: `.claude/skills/code-developer/pr-creation/`

**Purpose**: Automated PR creation with ROADMAP linking

**SKILL.md**:
```yaml
---
name: pr-creation
version: 1.0.0
agent: code-developer
scope: agent-specific
description: >
  Automated PR creation: analyze commits, generate description,
  link to ROADMAP, create PR with proper formatting.

triggers:
  - "create pull request"
  - "create PR"
  - "open pull request"

requires:
  - gh>=2.0  # GitHub CLI

inputs:
  priority:
    type: string
    required: true
    description: Priority implemented (e.g., "US-055")

  branch:
    type: string
    required: false
    description: Source branch (default: roadmap)

  target_branch:
    type: string
    required: false
    description: Target branch (default: main)

outputs:
  pr_url:
    type: string
    description: URL of created PR

  pr_number:
    type: int
    description: PR number

author: architect agent
created: 2025-10-19
---

# PR Creation Skill

Automated PR creation for code_developer.

## Workflow

1. **Analyze Commits**: Review git history since last PR
2. **Extract Changes**: Identify files changed, tests added
3. **Generate Description**: Summary, test plan, ROADMAP links
4. **Create PR**: Use `gh pr create` with formatted body
5. **Link to ROADMAP**: Update ROADMAP with PR link

## Expected Time Savings

- **Manual PR Creation**: 15-20 minutes
- **With Skill**: <3 minutes
- **Time Saved**: 85% reduction
```

**pr-creation.py**:
```python
"""
PR Creation Skill for code_developer.
Automated PR creation: analyze → describe → create → link.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute PR creation workflow."""
    priority = context["priority"]
    branch = context.get("branch", "roadmap")
    target_branch = context.get("target_branch", "main")

    print(f"Creating PR for {priority} ({branch} → {target_branch})")

    # Step 1: Analyze commits
    commits = analyze_commits(branch, target_branch)

    # Step 2: Extract changes
    changes = extract_changes(commits)

    # Step 3: Generate description
    description = generate_pr_description(priority, changes)

    # Step 4: Create PR
    pr_url, pr_number = create_pr(priority, branch, target_branch, description)

    # Step 5: Link to ROADMAP
    link_to_roadmap(priority, pr_url)

    return {
        "pr_url": pr_url,
        "pr_number": pr_number
    }


def analyze_commits(branch: str, target_branch: str) -> list:
    """Analyze commits since last merge."""
    # git log target_branch..branch
    # Extract commit messages
    pass


def extract_changes(commits: list) -> Dict[str, Any]:
    """Extract file changes, tests added, etc."""
    # git diff target_branch..branch --stat
    # Identify files changed
    # Count tests added
    pass


def generate_pr_description(priority: str, changes: Dict[str, Any]) -> str:
    """Generate PR description with summary, test plan, ROADMAP link."""
    summary = f"""## Summary

Implements {priority}

**Files Changed**: {changes['files_changed']}
**Tests Added**: {changes['tests_added']}
**Coverage**: {changes['coverage']}%

## Changes

{changes['description']}

## Test Plan

- [x] Unit tests pass ({changes['unit_tests']} tests)
- [x] Integration tests pass ({changes['integration_tests']} tests)
- [x] Coverage >= 80% (current: {changes['coverage']}%)
- [x] Pre-commit hooks pass

## ROADMAP

Closes: {priority}

See: docs/roadmap/ROADMAP.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"""
    return summary


def create_pr(
    priority: str,
    branch: str,
    target_branch: str,
    description: str
) -> tuple[str, int]:
    """Create PR using GitHub CLI."""
    title = f"feat: Implement {priority}"

    # gh pr create --title "..." --body "..." --base target_branch --head branch
    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--title", title,
            "--body", description,
            "--base", target_branch,
            "--head", branch
        ],
        capture_output=True,
        text=True
    )

    # Extract PR URL from output
    pr_url = result.stdout.strip()
    pr_number = extract_pr_number(pr_url)

    return pr_url, pr_number


def extract_pr_number(pr_url: str) -> int:
    """Extract PR number from URL."""
    # Parse URL, extract number
    pass


def link_to_roadmap(priority: str, pr_url: str):
    """Update ROADMAP with PR link."""
    # Read ROADMAP.md
    # Find priority
    # Add PR link
    # Commit update
    pass


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 85% reduction (15-20 minutes → <3 minutes)

---

### Skill 4: Spec Generator (architect)

**Location**: `.claude/skills/architect/spec-generator/`

**Purpose**: Automated technical spec generation

**SKILL.md**:
```yaml
---
name: spec-generator
version: 1.0.0
agent: architect
scope: agent-specific
description: >
  Automated technical spec generation: analyze requirements,
  research architecture, generate comprehensive spec following template.

triggers:
  - "create technical spec"
  - "generate spec"
  - "write technical specification"

requires:
  - none

inputs:
  priority:
    type: string
    required: true
    description: Priority to spec (e.g., "US-055")

  strategic_spec_path:
    type: string
    required: false
    description: Path to project_manager's strategic spec (if exists)

outputs:
  spec_path:
    type: string
    description: Path to generated spec file

  spec_sections:
    type: list[string]
    description: Sections included in spec

author: architect agent
created: 2025-10-19
---

# Spec Generator Skill

Automated technical spec generation for architect.

## Workflow

1. **Analyze Requirements**: Read ROADMAP, strategic spec
2. **Research Architecture**: Review existing code, patterns
3. **Generate Spec**: Follow SPEC-000-template.md structure
4. **Validate Completeness**: Check all required sections
5. **Save Spec**: Write to docs/architecture/specs/

## Expected Time Savings

- **Manual Spec Creation**: 3 hours
- **With Skill**: 1 hour
- **Time Saved**: 67% reduction
```

**spec-generator.py**:
```python
"""
Spec Generator Skill for architect.
Automated spec generation: analyze → research → generate → validate.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute spec generation workflow."""
    priority = context["priority"]
    strategic_spec = context.get("strategic_spec_path")

    print(f"Generating technical spec for {priority}")

    # Step 1: Analyze requirements
    requirements = analyze_requirements(priority, strategic_spec)

    # Step 2: Research architecture
    architecture = research_architecture(requirements)

    # Step 3: Generate spec
    spec_content = generate_spec(priority, requirements, architecture)

    # Step 4: Validate completeness
    validate_spec(spec_content)

    # Step 5: Save spec
    spec_path = save_spec(priority, spec_content)

    return {
        "spec_path": str(spec_path),
        "spec_sections": extract_sections(spec_content)
    }


def analyze_requirements(priority: str, strategic_spec: str) -> Dict[str, Any]:
    """Analyze requirements from ROADMAP and strategic spec."""
    # Read ROADMAP.md
    # Read strategic spec if exists
    # Extract acceptance criteria
    # Identify constraints
    pass


def research_architecture(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Research existing architecture and patterns."""
    # Read .claude/CLAUDE.md
    # Review existing code patterns
    # Identify reusable components
    # Check ADRs for past decisions
    pass


def generate_spec(
    priority: str,
    requirements: Dict[str, Any],
    architecture: Dict[str, Any]
) -> str:
    """Generate comprehensive spec following template."""
    # Load SPEC-000-template.md
    # Fill in all sections:
    #   - Executive Summary
    #   - Problem Statement
    #   - Requirements
    #   - Proposed Solution
    #   - Detailed Design
    #   - Testing Strategy
    #   - Rollout Plan
    #   - Risks & Mitigations
    # Use architecture research for design decisions
    pass


def validate_spec(spec_content: str) -> bool:
    """Validate spec has all required sections."""
    required_sections = [
        "Executive Summary",
        "Problem Statement",
        "Requirements",
        "Proposed Solution",
        "Detailed Design",
        "Testing Strategy",
        "Rollout Plan",
        "Risks & Mitigations"
    ]

    for section in required_sections:
        if section not in spec_content:
            raise ValueError(f"Missing required section: {section}")

    return True


def save_spec(priority: str, spec_content: str) -> Path:
    """Save spec to docs/architecture/specs/."""
    spec_dir = Path("docs/architecture/specs")
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Extract spec number from priority (e.g., US-055 → SPEC-055)
    spec_num = priority.replace("US-", "SPEC-")
    spec_filename = f"{spec_num}-{priority.lower().replace(' ', '-')}.md"
    spec_path = spec_dir / spec_filename

    spec_path.write_text(spec_content)

    return spec_path


def extract_sections(spec_content: str) -> list:
    """Extract section names from spec."""
    # Parse markdown headers
    # Return list of section names
    pass


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 67% reduction (3 hours → 1 hour)

---

### Skill 5: DoD Verification (project_manager)

**Location**: `.claude/skills/project-manager/dod-verification/`

**Purpose**: Automated DoD verification with Puppeteer + tests

**SKILL.md**:
```yaml
---
name: dod-verification
version: 1.0.0
agent: project-manager
scope: agent-specific
description: >
  Automated Definition of Done verification: run tests, check coverage,
  verify Puppeteer scenarios, capture evidence, generate report.

triggers:
  - "verify definition of done"
  - "check DoD"
  - "verify priority complete"
  - "DoD verification"

requires:
  - pytest>=7.0
  - pytest-cov>=4.0
  - puppeteer (MCP)

inputs:
  priority:
    type: string
    required: true
    description: Priority to verify (e.g., "US-055")

  puppeteer_scenarios:
    type: list[string]
    required: false
    description: Puppeteer test scenarios (if applicable)

outputs:
  tests_passing:
    type: bool
    description: All tests pass?

  coverage:
    type: float
    description: Code coverage percentage

  puppeteer_results:
    type: dict
    description: Puppeteer test results

  evidence:
    type: list[string]
    description: Evidence files (screenshots, logs)

  dod_verified:
    type: bool
    description: All DoD criteria met?

author: architect agent
created: 2025-10-19
---

# DoD Verification Skill

Automated DoD verification for project_manager.

## Workflow

1. **Run Tests**: Execute pytest with coverage
2. **Verify Coverage**: Check >= 80%
3. **Run Puppeteer**: Execute browser tests (if applicable)
4. **Capture Evidence**: Screenshots, logs, test reports
5. **Generate Report**: DoD verification report
6. **Tag Commit**: Create dod-verified-* tag

## Expected Time Savings

- **Manual DoD Verification**: 1 hour
- **With Skill**: 15 minutes
- **Time Saved**: 75% reduction
```

**dod-verification.py**:
```python
"""
DoD Verification Skill for project_manager.
Automated DoD verification: tests → coverage → puppeteer → evidence → report.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List


def main(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute DoD verification workflow."""
    priority = context["priority"]
    puppeteer_scenarios = context.get("puppeteer_scenarios", [])

    print(f"Verifying DoD for {priority}")

    # Step 1: Run tests
    tests_passing = run_tests()

    # Step 2: Verify coverage
    coverage = verify_coverage()

    # Step 3: Run Puppeteer (if applicable)
    puppeteer_results = run_puppeteer(puppeteer_scenarios) if puppeteer_scenarios else {}

    # Step 4: Capture evidence
    evidence = capture_evidence(priority)

    # Step 5: Generate report
    report = generate_dod_report(
        priority,
        tests_passing,
        coverage,
        puppeteer_results,
        evidence
    )

    # Step 6: Tag commit
    tag_commit(priority, report)

    # Determine if DoD verified
    dod_verified = (
        tests_passing and
        coverage >= 80.0 and
        (not puppeteer_scenarios or puppeteer_results.get("all_passed", False))
    )

    return {
        "tests_passing": tests_passing,
        "coverage": coverage,
        "puppeteer_results": puppeteer_results,
        "evidence": evidence,
        "dod_verified": dod_verified
    }


def run_tests() -> bool:
    """Run pytest and check all pass."""
    result = subprocess.run(
        ["pytest", "-v"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def verify_coverage() -> float:
    """Verify code coverage >= 80%."""
    result = subprocess.run(
        ["pytest", "--cov", "--cov-report=term"],
        capture_output=True,
        text=True
    )

    # Parse coverage from output
    # Extract percentage (e.g., "TOTAL    1234    123    90%")
    for line in result.stdout.split("\n"):
        if "TOTAL" in line:
            parts = line.split()
            coverage_str = parts[-1].replace("%", "")
            return float(coverage_str)

    return 0.0


def run_puppeteer(scenarios: List[str]) -> Dict[str, Any]:
    """Run Puppeteer test scenarios."""
    # Execute each scenario with Puppeteer MCP
    # Capture results, screenshots
    # Return pass/fail for each scenario
    results = {}

    for scenario in scenarios:
        # Run scenario
        passed = execute_puppeteer_scenario(scenario)
        results[scenario] = passed

    results["all_passed"] = all(results.values())

    return results


def execute_puppeteer_scenario(scenario: str) -> bool:
    """Execute a single Puppeteer scenario."""
    # Use Puppeteer MCP to run scenario
    # Return True if passed, False if failed
    pass


def capture_evidence(priority: str) -> List[str]:
    """Capture evidence files (screenshots, logs, reports)."""
    evidence_dir = Path(f"evidence/{priority}")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence = []

    # Copy test reports
    # Copy Puppeteer screenshots
    # Copy logs

    return evidence


def generate_dod_report(
    priority: str,
    tests_passing: bool,
    coverage: float,
    puppeteer_results: Dict[str, Any],
    evidence: List[str]
) -> str:
    """Generate DoD verification report."""
    report = f"""# DoD Verification Report - {priority}

**Date**: {datetime.now().isoformat()}
**Verified By**: project_manager (automated)

## Test Results

- **Tests Passing**: {'✅ Yes' if tests_passing else '❌ No'}
- **Coverage**: {coverage:.1f}% {'✅' if coverage >= 80 else '❌'}

## Puppeteer Results

"""

    if puppeteer_results:
        for scenario, passed in puppeteer_results.items():
            if scenario != "all_passed":
                report += f"- **{scenario}**: {'✅ Passed' if passed else '❌ Failed'}\n"
    else:
        report += "No Puppeteer scenarios\n"

    report += f"""

## Evidence

{len(evidence)} evidence files captured:
"""

    for file in evidence:
        report += f"- {file}\n"

    report += f"""

## DoD Status

**Verified**: {'✅ All criteria met' if all([tests_passing, coverage >= 80]) else '❌ Criteria not met'}
"""

    # Save report
    report_path = Path(f"evidence/{priority}/DOD_REPORT.md")
    report_path.write_text(report)

    return report


def tag_commit(priority: str, report: str):
    """Tag commit with dod-verified-* tag."""
    tag_name = f"dod-verified-{priority.lower()}"

    subprocess.run([
        "git", "tag", "-a", tag_name, "-m",
        f"DoD verified for {priority}\n\n{report}"
    ])

    subprocess.run(["git", "push", "origin", tag_name])


if __name__ == "__main__":
    context = json.load(sys.stdin)
    result = main(context)
    print(json.dumps(result, indent=2))
```

**Expected Time Savings**: 75% reduction (1 hour → 15 minutes)

---

## Testing Strategy

### Unit Tests

**Test files**: `tests/unit/test_skill_*.py`

**Test cases**:

**ExecutionController**:
1. `test_execute_skill_only()` - SKILL_ONLY mode executes skills
2. `test_execute_prompt_only()` - PROMPT_ONLY mode uses prompts
3. `test_execute_hybrid()` - HYBRID mode combines both
4. `test_fallback_to_prompt_on_skill_failure()` - Graceful fallback

**SkillLoader**:
1. `test_list_available_skills()` - Returns shared + agent-specific skills
2. `test_load_skill()` - Loads skill by name
3. `test_skill_exists()` - Checks skill existence
4. `test_parse_skill_md()` - Parses YAML frontmatter

**SkillRegistry**:
1. `test_find_skills_exact_match()` - Finds skills by exact trigger
2. `test_find_skills_fuzzy_match()` - Finds skills by fuzzy matching
3. `test_refresh_cache()` - Refreshes skill cache
4. `test_no_skills_found()` - Raises error if no skills match

**SkillInvoker**:
1. `test_invoke_single_skill()` - Executes single skill
2. `test_invoke_multiple_skills()` - Composes multiple skills
3. `test_skill_timeout()` - Enforces timeout
4. `test_skill_error_handling()` - Catches exceptions

**AgentSkillController**:
1. `test_execute_task()` - Executes task with skills
2. `test_list_skills()` - Lists available skills
3. `test_has_skill()` - Checks skill availability
4. `test_track_usage()` - Logs skill usage

### Integration Tests

**Test files**: `tests/integration/test_skills_integration.py`

**Test cases**:
1. `test_tdd_skill_end_to_end()` - TDD workflow from start to finish
2. `test_refactoring_skill_end_to_end()` - Refactoring workflow
3. `test_pr_creation_skill_end_to_end()` - PR creation workflow
4. `test_spec_generator_skill_end_to_end()` - Spec generation workflow
5. `test_dod_verification_skill_end_to_end()` - DoD verification workflow
6. `test_skill_composition()` - Multiple skills chained together
7. `test_backward_compatibility()` - Existing prompts still work

### Performance Tests

**Test files**: `tests/performance/test_skills_performance.py`

**Test cases**:
1. `test_skill_execution_time()` - < 5 minutes for 90% of skills
2. `test_skill_discovery_speed()` - < 100ms for skill lookup
3. `test_context_budget()` - Skills fit in ≤30% context window
4. `test_skill_composition_overhead()` - Minimal overhead for chaining

### Manual Testing

1. **Enable Code Execution Tool**: Verify `anthropic-beta: code-execution-2025-08-25` header works
2. **Create `.claude/skills/` structure**: Verify directories created correctly
3. **Run TDD skill**: Implement a simple feature using TDD workflow
4. **Run refactoring skill**: Refactor a small file (e.g., extract method)
5. **Run PR creation skill**: Create a PR for a test priority
6. **Run spec generator skill**: Generate a spec for a test priority
7. **Run DoD verification skill**: Verify DoD for a completed priority
8. **Test skill composition**: Chain multiple skills together
9. **Test backward compatibility**: Verify existing prompts still work

---

## Rollout Plan

### Week 1: Infrastructure

**Goal**: Implement core skill infrastructure

**Timeline**: 5 days (32-40 hours)

**Tasks**:
1. Add `pyyaml` dependency (via architect approval)
2. Create `.claude/skills/` directory structure
3. Implement ExecutionController (8 hours)
4. Implement SkillLoader (6 hours)
5. Implement SkillRegistry (6 hours)
6. Implement SkillInvoker (8 hours)
7. Implement AgentSkillController (4 hours)
8. Write unit tests (8 hours)
9. Update agent base class to support skills (4 hours)

**Success Criteria**:
- All infrastructure classes implemented
- Unit tests passing (>80% coverage)
- Agents can load and execute skills
- Backward compatible (prompts still work)

---

### Week 2: code_developer Skills (Part 1)

**Goal**: Implement TDD and Refactoring skills

**Timeline**: 5 days (24-32 hours)

**Tasks**:
1. Create TDD skill directory + SKILL.md (2 hours)
2. Implement TDD skill script (10 hours)
3. Test TDD skill (4 hours)
4. Create Refactoring skill directory + SKILL.md (2 hours)
5. Implement Refactoring skill script (10 hours)
6. Test Refactoring skill (4 hours)
7. Integration tests (4 hours)

**Success Criteria**:
- TDD skill reduces implementation time by 50%+
- Refactoring skill reduces refactoring time by 75%
- Both skills tested and working
- code_developer can use skills autonomously

---

### Week 3: code_developer Skills (Part 2) + architect Skill

**Goal**: Implement PR Creation and Spec Generator skills

**Timeline**: 5 days (24-32 hours)

**Tasks**:
1. Create PR Creation skill directory + SKILL.md (2 hours)
2. Implement PR Creation skill script (8 hours)
3. Test PR Creation skill (4 hours)
4. Create Spec Generator skill directory + SKILL.md (2 hours)
5. Implement Spec Generator skill script (10 hours)
6. Test Spec Generator skill (4 hours)
7. Integration tests (4 hours)

**Success Criteria**:
- PR Creation skill creates PRs in <3 minutes
- Spec Generator skill generates specs in 1 hour (vs 3 hours manual)
- Both skills tested and working
- architect can use Spec Generator autonomously

---

### Week 4: project_manager Skill + Documentation

**Goal**: Implement DoD Verification skill and complete documentation

**Timeline**: 5 days (20-28 hours)

**Tasks**:
1. Create DoD Verification skill directory + SKILL.md (2 hours)
2. Implement DoD Verification skill script (12 hours)
3. Test DoD Verification skill (4 hours)
4. Integration tests (4 hours)
5. Performance tests (4 hours)
6. Documentation (SKILLS_USER_GUIDE.md, SKILLS_DEVELOPER_GUIDE.md) (8 hours)
7. Create ADR-002 (Integrate Claude Skills) (4 hours)

**Success Criteria**:
- DoD Verification skill verifies DoD in 15 minutes (vs 1 hour manual)
- All 5 Phase 1 skills operational
- Comprehensive documentation complete
- ADR-002 created and approved

---

## Risks & Mitigations

### Risk 1: Code Execution Tool Reliability

**Description**: Code Execution Tool may fail or produce errors

**Likelihood**: Medium

**Impact**: High (skills blocked)

**Mitigation**:
- Robust error handling in SkillInvoker
- Fallback to prompts on failure (HYBRID mode)
- Timeout enforcement (5 minutes)
- Log all executions for debugging
- Monitor Code Execution Tool status (Anthropic status page)

---

### Risk 2: Context Budget Violation (CFR-007)

**Description**: Skills may exceed 30% context window budget

**Likelihood**: Medium

**Impact**: High (agent cannot function)

**Mitigation**:
- Lazy loading (load skills on-demand)
- Minimal SKILL.md metadata
- Skills execute externally (Code Execution Tool)
- Monitor context usage during testing
- Optimize skill code size

---

### Risk 3: Skill Execution Failures

**Description**: Skills may fail due to bugs, missing dependencies, etc.

**Likelihood**: Medium

**Impact**: Medium (workflow interrupted)

**Mitigation**:
- Comprehensive testing (unit + integration)
- Dependency checks in SKILL.md
- Graceful error handling
- Detailed error messages
- Fallback to manual workflow

---

### Risk 4: Backward Compatibility Breaking

**Description**: Skills integration may break existing prompts

**Likelihood**: Low

**Impact**: High (existing workflows broken)

**Mitigation**:
- 100% backward compatible design
- PromptLoader unchanged
- ExecutionController supports PROMPT_ONLY mode
- Integration tests verify prompts still work
- Gradual rollout (prompts first, skills optional)

---

### Risk 5: Performance Regression

**Description**: Skill execution may be slower than manual workflows

**Likelihood**: Low

**Impact**: Medium (defeats purpose of automation)

**Mitigation**:
- Performance benchmarks (< 5 minutes for 90% of skills)
- Optimize skill code
- Parallel execution where possible
- Monitor execution times
- Adjust timeout if needed

---

## Observability

### Metrics

**Metrics to track**:
- `skill.execution_time` (histogram) - Skill execution duration
- `skill.success_rate` (gauge) - Percentage of successful executions
- `skill.usage_count` (counter) - Number of times each skill used
- `skill.error_rate` (gauge) - Percentage of failed executions
- `skill.composition_count` (counter) - Number of composed skill executions
- `context.budget_usage` (gauge) - Context window usage percentage

### Logs

**Logs to emit**:
- INFO: Skill execution started (skill name, task, context)
- INFO: Skill execution completed (duration, success)
- WARNING: Skill execution slow (>5 minutes)
- ERROR: Skill execution failed (error message, stack trace)
- ERROR: Code Execution Tool unavailable
- DEBUG: Skill discovery (skills found for task)

### Alerts

**Alerts to configure**:
- Skill success rate < 90% (skills failing frequently)
- Skill execution time > 10 minutes (timeout approaching)
- Context budget > 30% (CFR-007 violation)
- Code Execution Tool unavailable (dependency down)

---

## Documentation

### User Documentation

**Files to create**:
1. `docs/SKILLS_USER_GUIDE.md` - How to use skills as an agent
2. `docs/skills/code-developer-skills.md` - code_developer skill catalog
3. `docs/skills/architect-skills.md` - architect skill catalog
4. `docs/skills/project-manager-skills.md` - project_manager skill catalog

**Content**:
- What are skills and when to use them
- How to invoke skills (via ExecutionController)
- Skill metadata format (SKILL.md)
- Examples for each skill
- Troubleshooting common issues

### Developer Documentation

**Files to create**:
1. `docs/SKILLS_DEVELOPER_GUIDE.md` - How to create new skills
2. `docs/architecture/decisions/ADR-002-integrate-claude-skills.md` - Architectural decision record

**Content**:
- Skills architecture overview
- API documentation (ExecutionController, SkillLoader, etc.)
- How to create a new skill (step-by-step)
- Testing strategies
- Debugging skills
- Best practices

---

## Security Considerations

1. **Code Execution Sandboxing**: Code Execution Tool provides built-in sandboxing
2. **Input Validation**: Validate all skill inputs (prevent injection attacks)
3. **Dependency Security**: Check `requires` in SKILL.md for vulnerabilities
4. **Access Control**: Skills have same permissions as agent (no elevation)
5. **Audit Trail**: Log all skill executions for compliance

---

## Cost Estimate

**Infrastructure**:
- Code Execution Tool: Included in Claude API (no extra cost)
- Development time: 84-104 hours (4 weeks)

**Development**:
- Week 1 (Infrastructure): 32-40 hours
- Week 2 (TDD + Refactoring): 24-32 hours
- Week 3 (PR + Spec Generator): 24-32 hours
- Week 4 (DoD + Docs): 20-28 hours

**Total**: 100-132 hours

**Ongoing**:
- Skill maintenance: 2 hours/month
- New skill creation: 8-12 hours/skill

---

## Future Enhancements (Phase 2+)

**Phase 2** (US-056):
1. ROADMAP Health Skill (project_manager)
2. Architecture Analysis Skill (architect)
3. Demo Creation Skill (assistant)
4. Bug Analysis Skill (assistant)
5. Security Audit Skill (code-searcher)
6. Dependency Impact Skill (architect)

**Phase 3** (US-057):
1. Code Forensics Skill (code-searcher)
2. Design System Skill (ux-design-expert)
3. Visual Regression Skill (ux-design-expert)
4. Performance tuning
5. Context budget optimization
6. Documentation completion

---

## References

- [SPEC-001: Claude Skills Integration (General)](docs/architecture/specs/SPEC-001-claude-skills-integration.md)
- [US-055: Claude Skills Integration - Phase 1](docs/roadmap/ROADMAP.md#us-055)
- [Code Execution Tool Documentation](https://docs.anthropic.com/claude/docs/code-execution)
- [Anthropic Beta Headers](https://docs.anthropic.com/claude/docs/beta-headers)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-19 | Created Phase 1 spec | architect |
| 2025-10-19 | Status: Draft | architect |

---

## Approval

- [ ] architect (author)
- [ ] code_developer (implementer)
- [ ] project_manager (strategic alignment)
- [ ] User (final approval)

**Approval Date**: TBD

---

**Status**: Ready for review by project_manager and user approval
