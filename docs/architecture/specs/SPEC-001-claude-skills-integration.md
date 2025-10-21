# SPEC-001: Claude Skills Integration

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-17
**Related**: Multi-AI Provider Support (PRIORITY 8), Prompt Management System

---

## Executive Summary

This specification defines the technical architecture for integrating **Claude Skills** into the MonolithicCoffeeMakerAgent multi-agent system. Skills will complement (not replace) the existing prompt-based system, providing executable code capabilities, better composability, and enhanced multi-agent coordination.

**Key Goals**:
1. Integrate Skills alongside existing PromptLoader system
2. Enable agent-specific skill discovery and invocation
3. Support skill composition for complex workflows
4. Maintain backward compatibility with current prompts
5. Prepare for Langfuse integration (Phase 2)

---

## Problem Statement

### Current System Limitations

**Existing Prompt System** (`.claude/commands/`):
- ✅ Centralized prompt templates
- ✅ Multi-AI provider support (Claude, Gemini, OpenAI)
- ✅ Variable substitution
- ❌ No executable code support (prompts are text-only)
- ❌ Limited composability (prompts don't stack)
- ❌ No automatic task-relevance detection
- ❌ Agent must explicitly choose which prompt to use

**Claude Skills Advantages**:
- ✅ Executable code (Python, shell scripts) for reliable operations
- ✅ Automatic invocation based on task relevance
- ✅ Composability (multiple skills stack automatically)
- ✅ Portable across Claude platforms (Desktop, Code, API)
- ✅ Bundled resources (includes docs, examples, scripts)

### Use Cases for Skills

| Use Case | Current (Prompts) | With Skills |
|----------|-------------------|-------------|
| **Complex calculations** | LLM generates code → may have errors | Skill executes pre-tested code → reliable |
| **Multi-step workflows** | Single large prompt → hard to maintain | Multiple skills compose automatically |
| **Agent-specific capabilities** | Hardcoded in agent logic | Skill auto-loads when relevant |
| **Code execution** | LLM writes code → user approves → runs | Skill code is pre-approved → runs securely |
| **Resource bundling** | Prompts reference external docs | Skill bundles docs + code + examples |

**Example**: `code-searcher` analyzing security vulnerabilities
- **Current**: Prompt with instructions → LLM generates analysis logic → may miss edge cases
- **With Skills**: Security audit skill with pre-tested regex patterns + CVE database → reliable detection

---

## Proposed Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT EXECUTION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ user_listener│  │  architect   │  │code_developer│  ...      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                    │
│         └─────────────────┴──────────────────┘                   │
│                           ▼                                       │
│                ┌─────────────────────┐                          │
│                │   SkillRegistry     │ ◄── Agent discovers skills│
│                │  (Agent-Specific)   │                          │
│                └─────────┬───────────┘                          │
│                          │                                       │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ SkillLoader │  │PromptLoader │  │ SkillInvoker│            │
│  │  (Unified)  │  │  (Existing) │  │  (Executor) │            │
│  └─────┬───────┘  └─────┬───────┘  └─────┬───────┘            │
│        │                │                │                      │
└────────┼────────────────┼────────────────┼──────────────────────┘
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  .claude/skills/       .claude/commands/    .claude/mcp/         │
│  ├── shared/           ├── *.md             └── *.json           │
│  │   ├── git-ops/                                                │
│  │   ├── testing/                                                │
│  │   └── analysis/                                               │
│  ├── user_listener/                                              │
│  ├── architect/                                                  │
│  ├── code_developer/                                             │
│  ├── project_manager/                                            │
│  ├── assistant/                                                  │
│  ├── code-searcher/                                              │
│  └── ux-design-expert/                                           │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY LAYER (Phase 2)                  │
│                         Langfuse                                 │
│  - Skill execution tracking                                      │
│  - Performance metrics                                           │
│  - Skill version management                                      │
│  - Prompt/Skill usage analytics                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
.claude/
├── skills/                        # Claude Skills (NEW)
│   ├── shared/                    # Skills available to ALL agents
│   │   ├── git-operations/
│   │   │   ├── SKILL.md           # Skill metadata
│   │   │   ├── commit.py          # Executable code
│   │   │   ├── branch.py
│   │   │   └── examples/
│   │   ├── testing-automation/
│   │   │   ├── SKILL.md
│   │   │   ├── pytest_runner.py
│   │   │   └── coverage_report.py
│   │   ├── code-analysis/
│   │   │   ├── SKILL.md
│   │   │   ├── security_audit.py
│   │   │   └── dependency_check.py
│   │   └── documentation-gen/
│   │       ├── SKILL.md
│   │       ├── adr_template.py
│   │       └── spec_template.py
│   │
│   ├── user_listener/             # Agent-specific skills
│   │   ├── intent-parsing/
│   │   │   ├── SKILL.md
│   │   │   └── parse_request.py
│   │   └── delegation-router/
│   │       ├── SKILL.md
│   │       └── route_to_agent.py
│   │
│   ├── architect/
│   │   ├── dependency-analysis/
│   │   │   ├── SKILL.md
│   │   │   ├── check_security.py
│   │   │   ├── check_license.py
│   │   │   └── cve_database.json
│   │   ├── adr-generator/
│   │   │   ├── SKILL.md
│   │   │   └── generate_adr.py
│   │   └── spec-validator/
│   │       ├── SKILL.md
│   │       └── validate_spec.py
│   │
│   ├── code_developer/
│   │   ├── code-generation/
│   │   │   ├── SKILL.md
│   │   │   └── generate_boilerplate.py
│   │   ├── test-generation/
│   │   │   ├── SKILL.md
│   │   │   └── generate_tests.py
│   │   └── refactoring-assistant/
│   │       ├── SKILL.md
│   │       └── extract_mixin.py
│   │
│   ├── project_manager/
│   │   ├── roadmap-parser/
│   │   │   ├── SKILL.md
│   │   │   └── parse_priorities.py
│   │   ├── github-monitor/
│   │   │   ├── SKILL.md
│   │   │   └── check_pr_status.py
│   │   └── notification-generator/
│   │       ├── SKILL.md
│   │       └── send_notification.py
│   │
│   ├── assistant/
│   │   ├── demo-creator/
│   │   │   ├── SKILL.md
│   │   │   └── create_puppeteer_demo.py
│   │   ├── bug-analyzer/
│   │   │   ├── SKILL.md
│   │   │   └── analyze_bug.py
│   │   └── doc-search/
│   │       ├── SKILL.md
│   │       └── search_docs.py
│   │
│   ├── code-searcher/
│   │   ├── security-audit/
│   │   │   ├── SKILL.md
│   │   │   ├── scan_vulnerabilities.py
│   │   │   └── cve_patterns.json
│   │   ├── dependency-tracer/
│   │   │   ├── SKILL.md
│   │   │   └── trace_dependencies.py
│   │   └── pattern-detector/
│   │       ├── SKILL.md
│   │       └── detect_antipatterns.py
│   │
│   └── ux-design-expert/
│       ├── tailwind-generator/
│       │   ├── SKILL.md
│       │   └── generate_classes.py
│       └── chart-designer/
│           ├── SKILL.md
│           └── design_chart.py
│
├── commands/                      # Existing prompts (KEEP)
│   ├── *.md
│   └── PROMPTS_INDEX.md
│
└── mcp/                           # MCP configs
    └── puppeteer.json
```

---

## Technical Design

### 1. Unified Skill/Prompt System

**Design Principle**: Skills and Prompts are **complementary**, not competing systems.

```python
# coffee_maker/autonomous/execution_controller.py (NEW)

from typing import Optional, Union, List
from pathlib import Path
from enum import Enum


class ExecutionMode(Enum):
    """Execution mode for tasks."""
    PROMPT_ONLY = "prompt"       # Use prompt template
    SKILL_ONLY = "skill"         # Use skill with executable code
    HYBRID = "hybrid"            # Use both (skill for execution, prompt for guidance)


class ExecutionController:
    """Unified controller for skills and prompts.

    This controller decides when to use skills vs. prompts:
    - Skills: When executable code is needed (calculations, security scans, etc.)
    - Prompts: When LLM reasoning is needed (creative writing, analysis)
    - Hybrid: When both are needed (skill provides data, prompt interprets)

    Example:
        >>> controller = ExecutionController(agent_type=AgentType.ARCHITECT)
        >>> result = controller.execute(
        ...     task="analyze dependency security",
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
        """Execute task using skills, prompts, or both.

        Args:
            task: Description of task to execute
            mode: Execution mode (prompt, skill, hybrid)
            context: Additional context for execution

        Returns:
            ExecutionResult with output, metadata, and metrics
        """
        if mode == ExecutionMode.SKILL_ONLY:
            return self._execute_skill(task, context)
        elif mode == ExecutionMode.PROMPT_ONLY:
            return self._execute_prompt(task, context)
        else:  # HYBRID
            return self._execute_hybrid(task, context)

    def _execute_skill(self, task: str, context: dict) -> ExecutionResult:
        """Execute skill with executable code."""
        # 1. Discover relevant skills
        skills = self.skill_registry.find_skills_for_task(task)

        if not skills:
            raise NoSkillFoundError(f"No skill found for task: {task}")

        # 2. Invoke skills (may compose multiple)
        invoker = SkillInvoker(self.agent_type)
        result = invoker.invoke(skills, context)

        return ExecutionResult(
            output=result.output,
            skills_used=skills,
            execution_time=result.duration,
            mode=ExecutionMode.SKILL_ONLY
        )

    def _execute_prompt(self, task: str, context: dict) -> ExecutionResult:
        """Execute prompt with LLM reasoning."""
        # Use existing PromptLoader
        prompt = self.prompt_loader.load(task, context)

        # Execute via Claude CLI/API
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        cli = ClaudeCLIInterface()
        result = cli.execute_prompt(prompt)

        return ExecutionResult(
            output=result,
            prompts_used=[task],
            execution_time=0,  # Tracked separately
            mode=ExecutionMode.PROMPT_ONLY
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
            skills_used=skill_result.skills_used,
            prompts_used=prompt_result.prompts_used,
            execution_time=skill_result.execution_time,
            mode=ExecutionMode.HYBRID
        )
```

### 2. Skill Loader (Similar to PromptLoader)

```python
# coffee_maker/autonomous/skill_loader.py (NEW)

from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class SkillMetadata:
    """Metadata for a Claude Skill."""

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.skill_md = skill_path / "SKILL.md"
        self.metadata = self._parse_metadata()

    def _parse_metadata(self) -> dict:
        """Parse SKILL.md file for metadata.

        Expected format:
        ---
        name: dependency-analysis
        version: 1.0.0
        agent: architect
        scope: shared  # or agent-specific
        triggers:
          - "analyze dependency"
          - "check package security"
          - "evaluate license"
        requires:
          - python>=3.9
          - requests
        ---
        """
        if not self.skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found: {self.skill_md}")

        content = self.skill_md.read_text()

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml
                return yaml.safe_load(parts[1])

        return {}

    @property
    def name(self) -> str:
        return self.metadata.get("name", self.skill_path.name)

    @property
    def version(self) -> str:
        return self.metadata.get("version", "1.0.0")

    @property
    def agent(self) -> str:
        return self.metadata.get("agent", "shared")

    @property
    def triggers(self) -> List[str]:
        """Task descriptions that trigger this skill."""
        return self.metadata.get("triggers", [])

    @property
    def requires(self) -> List[str]:
        """Dependencies required by this skill."""
        return self.metadata.get("requires", [])


class SkillLoader:
    """Load Claude Skills from .claude/skills/ directory.

    Similar to PromptLoader but for executable skills.

    Example:
        >>> loader = SkillLoader(agent_type=AgentType.ARCHITECT)
        >>> skills = loader.list_available_skills()
        >>> skill = loader.load("dependency-analysis")
    """

    def __init__(self, agent_type: AgentType, skills_dir: Optional[Path] = None):
        self.agent_type = agent_type
        self.skills_dir = skills_dir or Path(".claude/skills")
        self.shared_skills_dir = self.skills_dir / "shared"
        self.agent_skills_dir = self.skills_dir / agent_type.value

    def list_available_skills(self) -> List[SkillMetadata]:
        """List all skills available to this agent.

        Returns:
            List of SkillMetadata (shared + agent-specific)
        """
        skills = []

        # 1. Load shared skills
        if self.shared_skills_dir.exists():
            for skill_path in self.shared_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    skills.append(SkillMetadata(skill_path))

        # 2. Load agent-specific skills
        if self.agent_skills_dir.exists():
            for skill_path in self.agent_skills_dir.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    skills.append(SkillMetadata(skill_path))

        return skills

    def load(self, skill_name: str) -> SkillMetadata:
        """Load a specific skill by name.

        Args:
            skill_name: Name of skill (e.g., "dependency-analysis")

        Returns:
            SkillMetadata object

        Raises:
            FileNotFoundError: If skill doesn't exist
        """
        # Try agent-specific first
        agent_skill_path = self.agent_skills_dir / skill_name
        if agent_skill_path.exists():
            return SkillMetadata(agent_skill_path)

        # Fall back to shared
        shared_skill_path = self.shared_skills_dir / skill_name
        if shared_skill_path.exists():
            return SkillMetadata(shared_skill_path)

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


class SkillRegistry:
    """Registry for agent-specific skill discovery.

    This class maintains a cache of available skills and provides
    fast lookup for task-to-skill mapping.

    Example:
        >>> registry = SkillRegistry(AgentType.ARCHITECT)
        >>> skills = registry.find_skills_for_task("analyze dependency security")
        >>> # Returns: [SkillMetadata(dependency-analysis)]
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
        """Find skills relevant to a task description.

        Uses fuzzy matching on skill triggers.

        Args:
            task: Task description (e.g., "analyze dependency security")

        Returns:
            List of relevant SkillMetadata objects
        """
        from difflib import get_close_matches

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

### 3. Skill Invoker (Executor)

```python
# coffee_maker/autonomous/skill_invoker.py (NEW)

import subprocess
import json
from pathlib import Path
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class SkillExecutionResult:
    """Result of skill execution."""

    def __init__(
        self,
        output: Any,
        exit_code: int,
        duration: float,
        skill_name: str,
        errors: List[str] = None
    ):
        self.output = output
        self.exit_code = exit_code
        self.duration = duration
        self.skill_name = skill_name
        self.errors = errors or []

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def __repr__(self):
        return (
            f"SkillExecutionResult(skill={self.skill_name}, "
            f"success={self.success}, duration={self.duration:.2f}s)"
        )


class SkillInvoker:
    """Execute Claude Skills with sandboxing and security.

    This class provides secure execution of skill code with:
    - Sandboxing (limited file system access)
    - Timeout enforcement
    - Resource limits (memory, CPU)
    - Error handling and retry logic

    Example:
        >>> invoker = SkillInvoker(AgentType.ARCHITECT)
        >>> result = invoker.invoke([skill_metadata], context={"package": "redis"})
        >>> print(result.output)
    """

    def __init__(
        self,
        agent_type: AgentType,
        timeout: int = 300,  # 5 minutes default
        enable_sandbox: bool = True
    ):
        self.agent_type = agent_type
        self.timeout = timeout
        self.enable_sandbox = enable_sandbox

    def invoke(
        self,
        skills: List[SkillMetadata],
        context: Dict[str, Any]
    ) -> SkillExecutionResult:
        """Invoke skills with context.

        Skills are executed in order (composition).
        Output of skill N becomes input to skill N+1.

        Args:
            skills: List of skills to execute (in order)
            context: Execution context (variables, data)

        Returns:
            SkillExecutionResult with combined output
        """
        import time
        start = time.time()

        # Execute skills in sequence
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
        """Execute a single skill.

        Skills can be Python scripts, shell scripts, or other executables.
        """
        import time
        start = time.time()

        # Find executable in skill directory
        skill_dir = skill.skill_path

        # Try Python script first
        py_script = skill_dir / f"{skill.name}.py"
        if py_script.exists():
            return self._execute_python_skill(py_script, context)

        # Try shell script
        sh_script = skill_dir / f"{skill.name}.sh"
        if sh_script.exists():
            return self._execute_shell_skill(sh_script, context)

        raise FileNotFoundError(f"No executable found in {skill_dir}")

    def _execute_python_skill(
        self,
        script_path: Path,
        context: Dict[str, Any]
    ) -> SkillExecutionResult:
        """Execute Python skill script."""
        import time
        start = time.time()

        # Write context to temp file (JSON)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(context, f)
            context_file = f.name

        try:
            # Execute skill with context
            cmd = [
                "python",
                str(script_path),
                "--context", context_file
            ]

            if self.enable_sandbox:
                # TODO: Add sandbox (firejail, docker, etc.)
                pass

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start

            # Parse output (assume JSON)
            try:
                output = json.loads(result.stdout)
            except json.JSONDecodeError:
                output = result.stdout

            return SkillExecutionResult(
                output=output,
                exit_code=result.returncode,
                duration=duration,
                skill_name=script_path.stem,
                errors=[result.stderr] if result.stderr else []
            )

        finally:
            # Clean up temp file
            Path(context_file).unlink(missing_ok=True)

    def _execute_shell_skill(
        self,
        script_path: Path,
        context: Dict[str, Any]
    ) -> SkillExecutionResult:
        """Execute shell skill script."""
        # Similar to Python, but use bash
        import time
        start = time.time()

        # Convert context to env vars
        env = {k: str(v) for k, v in context.items()}

        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env=env
        )

        duration = time.time() - start

        return SkillExecutionResult(
            output=result.stdout,
            exit_code=result.returncode,
            duration=duration,
            skill_name=script_path.stem,
            errors=[result.stderr] if result.stderr else []
        )
```

### 4. Agent-Specific Integration

Each agent gets a **SkillController** that manages skill discovery and invocation.

```python
# coffee_maker/autonomous/agent_skill_controller.py (NEW)

from typing import Optional, List
from coffee_maker.autonomous.skill_loader import SkillLoader, SkillRegistry
from coffee_maker.autonomous.skill_invoker import SkillInvoker
from coffee_maker.autonomous.agent_registry import AgentType


class AgentSkillController:
    """Skill controller for a specific agent.

    Each agent instance gets its own controller that:
    1. Discovers available skills (shared + agent-specific)
    2. Automatically invokes relevant skills based on task
    3. Composes multiple skills when needed
    4. Tracks skill usage for observability

    Example (architect agent):
        >>> controller = AgentSkillController(AgentType.ARCHITECT)
        >>> result = controller.execute_task(
        ...     "analyze redis package security",
        ...     context={"package_name": "redis", "version": "5.0.0"}
        ... )
        >>> print(result.output)  # Security report from dependency-analysis skill
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
        """Execute task using relevant skills.

        This method:
        1. Finds skills matching task description
        2. Invokes skills in composition order
        3. Returns combined result

        Args:
            task_description: Natural language task description
            context: Additional context for execution

        Returns:
            SkillExecutionResult with output and metadata
        """
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

        # 3. Track usage (for Langfuse integration)
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
        """Track skill usage for observability (Langfuse integration)."""
        # TODO: Implement Langfuse tracking in Phase 2
        from coffee_maker.langfuse_observe import observe_skill_execution

        observe_skill_execution(
            agent_type=self.agent_type,
            skill_names=[s.name for s in skills],
            duration=result.duration,
            success=result.success,
            errors=result.errors
        )
```

---

## Agent-Specific Skills Architecture

### Decision Framework: When to Use Skills vs. Prompts

| Agent | Use Skills For | Use Prompts For | Hybrid Use Cases |
|-------|---------------|-----------------|------------------|
| **user_listener** | Intent parsing (NLP), delegation routing | User conversation, clarification questions | Parse intent with skill → Generate response with prompt |
| **architect** | Dependency security scans, license checks, CVE lookup | ADR writing, design discussions, justifications | Scan with skill → Write ADR with prompt |
| **code_developer** | Boilerplate generation, test scaffolding, mixin extraction | Complex implementation logic, refactoring decisions | Generate tests with skill → Implement logic with prompt |
| **project_manager** | ROADMAP parsing, GitHub API calls, notification sending | Strategic planning, priority decisions | Fetch PR status with skill → Analyze blockers with prompt |
| **assistant** | Demo creation (Puppeteer), bug detection, doc search | Bug analysis, comprehensive reporting | Detect bug with skill → Analyze root cause with prompt |
| **code-searcher** | Security audits, dependency tracing, pattern detection | Forensic analysis, recommendations | Scan code with skill → Explain findings with prompt |
| **ux-design-expert** | Tailwind class generation, chart rendering | Design critique, layout suggestions | Generate classes with skill → Explain design with prompt |

### Skill Invocation Pattern (Per Agent)

Each agent follows this pattern:

```python
# Example: architect agent using skills

from coffee_maker.autonomous.agent_skill_controller import AgentSkillController
from coffee_maker.autonomous.agent_registry import AgentType


class ArchitectAgent:
    """Architect agent with skill support."""

    def __init__(self):
        # Initialize skill controller
        self.skill_controller = AgentSkillController(AgentType.ARCHITECT)

    def evaluate_dependency(self, package_name: str, version: str) -> dict:
        """Evaluate dependency using skills + prompts.

        Workflow:
        1. Use dependency-analysis skill to scan security/licenses
        2. Use prompt to write justification
        3. Request user approval via user_listener
        """
        # STEP 1: Execute skill to get data
        skill_result = self.skill_controller.execute_task(
            task_description="analyze dependency security and licensing",
            context={
                "package_name": package_name,
                "version": version
            }
        )

        # skill_result.output contains:
        # {
        #   "security": {"cves": [], "vulnerabilities": []},
        #   "licensing": {"license": "MIT", "compatible": true},
        #   "maintenance": {"last_update": "2025-09-01", "active": true}
        # }

        # STEP 2: Use prompt to interpret results
        from coffee_maker.autonomous.prompt_loader import load_prompt, PromptNames

        prompt = load_prompt("evaluate-dependency", {
            "PACKAGE_NAME": package_name,
            "VERSION": version,
            "SECURITY_REPORT": json.dumps(skill_result.output["security"]),
            "LICENSE_REPORT": json.dumps(skill_result.output["licensing"]),
            "MAINTENANCE_REPORT": json.dumps(skill_result.output["maintenance"])
        })

        # Execute prompt (LLM provides recommendation)
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
        cli = ClaudeCLIInterface()
        recommendation = cli.execute_prompt(prompt)

        return {
            "data": skill_result.output,
            "recommendation": recommendation
        }
```

### Skill Naming Conventions

**Format**: `<domain>-<action>` (kebab-case)

Examples:
- `dependency-analysis` (not `analyze_dependency`)
- `git-operations` (not `GitOps`)
- `security-audit` (not `securityAudit`)

**Directory Structure**:
```
.claude/skills/architect/dependency-analysis/
├── SKILL.md                    # Metadata (triggers, version, etc.)
├── check_security.py           # Security check script
├── check_license.py            # License check script
├── cve_database.json           # CVE data (bundled resource)
└── examples/
    └── redis_analysis.json     # Example output
```

### Skill Metadata Structure

**SKILL.md Format** (YAML frontmatter):

```yaml
---
name: dependency-analysis
version: 1.0.0
agent: architect
scope: agent-specific  # or "shared"
description: >
  Analyzes Python package dependencies for security vulnerabilities,
  licensing compatibility, and maintenance status.

triggers:
  - "analyze dependency"
  - "check package security"
  - "evaluate license compatibility"
  - "assess dependency risk"

requires:
  - python>=3.9
  - requests
  - packaging

inputs:
  package_name:
    type: string
    required: true
    description: Name of package (e.g., "redis")

  version:
    type: string
    required: true
    description: Package version (e.g., "5.0.0")

outputs:
  security:
    type: object
    description: Security report with CVEs

  licensing:
    type: object
    description: License compatibility report

  maintenance:
    type: object
    description: Package maintenance status

examples:
  - task: "analyze redis 5.0.0 security"
    context:
      package_name: "redis"
      version: "5.0.0"
    expected_output: "examples/redis_analysis.json"

author: architect agent
created: 2025-10-17
updated: 2025-10-17
---

# Dependency Analysis Skill

This skill analyzes Python package dependencies for:
1. **Security**: CVE lookup, vulnerability scanning
2. **Licensing**: License compatibility check
3. **Maintenance**: Activity status, last update

## Usage

The architect agent uses this skill when evaluating new dependencies:

```python
result = skill_controller.execute_task(
    "analyze redis package security",
    context={"package_name": "redis", "version": "5.0.0"}
)
```

## How It Works

1. **check_security.py**: Queries CVE databases, checks for known vulnerabilities
2. **check_license.py**: Parses package metadata, validates license compatibility
3. **cve_database.json**: Local cache of CVE data (updated weekly)

## Output Format

```json
{
  "security": {
    "cves": [],
    "vulnerabilities": [],
    "score": 10.0
  },
  "licensing": {
    "license": "MIT",
    "compatible": true
  },
  "maintenance": {
    "last_update": "2025-09-01",
    "active": true,
    "maintainers": 15
  }
}
```
```

### Parameter Passing

Skills receive context via **JSON file** (for security):

```python
# check_security.py

import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True, help="Path to context JSON")
    args = parser.parse_args()

    # Load context
    with open(args.context) as f:
        context = json.load(f)

    package_name = context["package_name"]
    version = context["version"]

    # Perform security check
    result = check_security(package_name, version)

    # Output result (JSON to stdout)
    print(json.dumps(result, indent=2))


def check_security(package_name: str, version: str) -> dict:
    """Check package security (CVEs, vulnerabilities)."""
    # Implementation...
    return {
        "cves": [],
        "vulnerabilities": [],
        "score": 10.0
    }


if __name__ == "__main__":
    main()
```

### Result Handling

Skills output **JSON to stdout** (parsed by SkillInvoker):

```python
# In agent code:
result = skill_controller.execute_task("analyze redis security", {...})

# result.output is parsed JSON:
print(result.output["security"]["score"])  # 10.0
print(result.success)  # True
print(result.duration)  # 2.35 (seconds)
```

---

## Migration Path

### Phase 1: Pilot Skills (2-3 weeks)

**Goal**: Validate skills integration with minimal disruption

1. **Create 2-3 pilot skills** (don't migrate prompts yet):
   - `architect/dependency-analysis` (security scans)
   - `code-searcher/security-audit` (code vulnerability scans)
   - `assistant/demo-creator` (Puppeteer automation)

2. **Implement core infrastructure**:
   - SkillLoader, SkillRegistry, SkillInvoker
   - AgentSkillController for each agent
   - Update agent configs to enable skills

3. **Test in production**:
   - architect uses dependency-analysis for new packages
   - code-searcher uses security-audit for code analysis
   - assistant uses demo-creator for visual demos

4. **Measure success**:
   - Skills execute reliably (>95% success rate)
   - Performance acceptable (<5s for most skills)
   - No regression in agent functionality

### Phase 2: Gradual Skill Addition (1-2 months)

**Goal**: Add more skills where executable code provides value

**Migration Criteria** (when to create a skill):
- ✅ Task requires **reliable calculations** (not creative reasoning)
- ✅ Task involves **external API calls** (GitHub, PyPI, CVE databases)
- ✅ Task requires **file/code parsing** (regex, AST analysis)
- ✅ Task is **repetitive** (same logic, different inputs)
- ❌ Task requires **creative writing** (ADRs, specs, documentation)
- ❌ Task is **one-off** (not reusable)

**Skill Creation Process**:
1. Identify task suitable for skill (see criteria)
2. Create skill directory in `.claude/skills/<agent>/<skill-name>/`
3. Write SKILL.md with metadata
4. Implement executable code (Python/shell)
5. Add examples and tests
6. Update agent to use skill
7. Monitor via Langfuse (Phase 2)

**Example Migration**: `create-technical-spec` prompt → hybrid approach
- **Keep prompt** (for creative spec writing)
- **Add skill**: `spec-validator` (validate spec format, check for required sections)
- **Result**: Prompt writes spec, skill validates it

### Phase 3: Prompt-Skill Coexistence (Ongoing)

**Goal**: Skills and prompts work together (not replacing each other)

**Coexistence Strategy**:

| Capability | Approach |
|------------|----------|
| **Creative writing** | Prompts ONLY (ADRs, specs, docs) |
| **Data extraction** | Skills ONLY (parsing, API calls) |
| **Complex reasoning** | Prompts ONLY (architectural decisions) |
| **Calculations** | Skills ONLY (security scores, dependency graphs) |
| **Validation** | Skills ONLY (format checks, linting) |
| **Analysis** | HYBRID (skill extracts data → prompt interprets) |

**No Prompt Deprecation**: Existing prompts remain in `.claude/commands/` indefinitely. Skills complement prompts, not replace them.

### Backward Compatibility

**100% Backward Compatible**:
- Existing PromptLoader API unchanged
- Agents can use prompts without skills
- Skills are opt-in (agents enable via config)
- No breaking changes to agent interfaces

**Configuration**:
```yaml
# .claude/agents/architect.yaml
skills:
  enabled: true  # Enable skill support (default: false for backward compat)
  allowed_skills:
    - dependency-analysis
    - adr-generator
    - spec-validator
```

---

## Maintainability Analysis

### Code Organization

**Separation of Concerns**:
```
coffee_maker/autonomous/
├── execution_controller.py    # Unified skill/prompt execution
├── skill_loader.py            # Skill discovery and loading
├── skill_invoker.py           # Skill execution with sandboxing
├── agent_skill_controller.py  # Per-agent skill management
├── prompt_loader.py           # Existing (unchanged)
└── claude_cli_interface.py    # Existing (unchanged)
```

**Clear Responsibilities**:
- **ExecutionController**: Decides skill vs. prompt
- **SkillLoader**: Finds and loads skills
- **SkillInvoker**: Executes skills securely
- **AgentSkillController**: Per-agent skill orchestration
- **PromptLoader**: (Existing) Loads prompts

### Documentation Requirements

**Required Documentation**:

1. **User Guide** (`docs/SKILLS_USER_GUIDE.md`):
   - What are skills and when to use them
   - How to create a new skill
   - Skill metadata format
   - Examples for each agent

2. **Developer Guide** (`docs/SKILLS_DEVELOPER_GUIDE.md`):
   - Architecture overview
   - API documentation
   - Testing strategies
   - Debugging skills

3. **Migration Guide** (`docs/SKILLS_MIGRATION_GUIDE.md`):
   - How to migrate prompts to skills (when beneficial)
   - Backward compatibility guarantees
   - Deprecation policy (none for now)

4. **Per-Agent Skill Catalog** (`docs/skills/<agent>_skills.md`):
   - List of skills available to each agent
   - Usage examples
   - Trigger phrases

5. **ADR** (`docs/architecture/decisions/ADR-002-integrate-claude-skills.md`):
   - Context, decision, consequences
   - Why skills complement prompts
   - Alternatives considered

### Monitoring and Observability

**Langfuse Integration** (Phase 2):

```python
# coffee_maker/langfuse_observe/skill_tracking.py (NEW)

from langfuse.decorators import observe


@observe(name="skill_execution")
def observe_skill_execution(
    agent_type: str,
    skill_names: list[str],
    duration: float,
    success: bool,
    errors: list[str]
):
    """Track skill execution in Langfuse.

    Metrics tracked:
    - Execution time per skill
    - Success/failure rate
    - Error patterns
    - Skill composition patterns
    - Agent usage patterns
    """
    from langfuse import Langfuse

    langfuse = Langfuse()
    langfuse.track(
        name="skill_execution",
        properties={
            "agent_type": agent_type,
            "skills": skill_names,
            "duration_seconds": duration,
            "success": success,
            "errors": errors
        }
    )
```

**Dashboards**:
- **Skill Performance**: Execution time, success rate per skill
- **Agent Usage**: Which agents use which skills most
- **Composition Patterns**: Common skill combinations
- **Error Analysis**: Skill failures, common error types

### Technical Debt Considerations

**Potential Debt**:

1. **Skill Proliferation**: Too many skills → hard to maintain
   - **Mitigation**: Strict skill creation criteria (see Phase 2)
   - **Review**: Monthly skill audit (remove unused skills)

2. **Skill Versioning**: Breaking changes in skills → agent failures
   - **Mitigation**: Semantic versioning in SKILL.md
   - **Review**: Version compatibility matrix

3. **Sandbox Complexity**: Skill execution sandboxing adds overhead
   - **Mitigation**: Start without sandbox, add if needed
   - **Review**: Security audit in 6 months

4. **Prompt-Skill Overlap**: Confusion about when to use which
   - **Mitigation**: Clear decision framework (see above)
   - **Review**: Update guidelines based on usage patterns

**Debt Monitoring**:
- Track skill count per agent (alert if >20)
- Track skill execution failures (alert if >5% failure rate)
- Track skill usage (deprecate skills with <10 uses/month)

---

## Rollout Plan

### Phase 1: Infrastructure (Week 1-2)

**Deliverables**:
- ✅ SkillLoader implementation
- ✅ SkillRegistry implementation
- ✅ SkillInvoker implementation
- ✅ AgentSkillController implementation
- ✅ ExecutionController implementation
- ✅ Unit tests (>80% coverage)

**Tasks**:
1. code_developer implements core classes
2. architect reviews code quality
3. code_developer writes tests
4. project_manager verifies DoD

### Phase 2: Pilot Skills (Week 3-4)

**Deliverables**:
- ✅ `architect/dependency-analysis` skill
- ✅ `code-searcher/security-audit` skill
- ✅ `assistant/demo-creator` skill
- ✅ Agent integration (architect, code-searcher, assistant)
- ✅ Integration tests

**Tasks**:
1. code_developer creates skill directories
2. code_developer implements skill scripts
3. code_developer updates agents to use skills
4. assistant tests skills with real tasks
5. project_manager verifies in production

### Phase 3: Documentation (Week 5)

**Deliverables**:
- ✅ User guide
- ✅ Developer guide
- ✅ Migration guide
- ✅ Per-agent skill catalogs
- ✅ ADR-002

**Tasks**:
1. project_manager creates documentation structure
2. architect writes technical docs (ADR, developer guide)
3. assistant writes user guide (examples, tutorials)
4. project_manager reviews and publishes

### Phase 4: Gradual Expansion (Month 2-3)

**Deliverables**:
- ✅ 2-3 skills per agent (15-20 total)
- ✅ Skill composition examples
- ✅ Performance benchmarks
- ✅ Langfuse integration (Phase 2)

**Tasks**:
1. Agents request new skills via ROADMAP
2. code_developer implements approved skills
3. Agents integrate and test
4. project_manager monitors usage via Langfuse

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Skill execution failures** | High (agents blocked) | Medium | Robust error handling, fallback to prompts |
| **Sandbox bypass** | High (security) | Low | Code review, security audit, sandboxing |
| **Skill proliferation** | Medium (maintenance burden) | High | Strict creation criteria, monthly audits |
| **Prompt-skill confusion** | Medium (developer confusion) | Medium | Clear guidelines, decision framework |
| **Performance regression** | Low (slower execution) | Low | Performance benchmarks, monitoring |
| **Langfuse integration delay** | Low (no observability) | Medium | Manual logging until Phase 2 complete |

---

## Success Metrics

**Pilot Phase (Month 1)**:
- ✅ 3 pilot skills implemented
- ✅ All 3 skills execute successfully (>95% success rate)
- ✅ Agents adopt skills (>10 uses per skill in month 1)
- ✅ No production incidents

**Expansion Phase (Month 2-3)**:
- ✅ 15-20 skills across all agents
- ✅ Skill usage grows 20% month-over-month
- ✅ Agent efficiency improves (measured via task completion time)
- ✅ Developer satisfaction (survey: >8/10)

**Maturity Phase (Month 6+)**:
- ✅ Skills integrated in all critical workflows
- ✅ Langfuse dashboards show skill performance
- ✅ Skill library stable (low churn)
- ✅ No major refactoring needed

---

## Open Questions

1. **Sandbox Technology**: Which sandboxing approach? (firejail, docker, pypy sandbox)
   - **Recommendation**: Start without sandbox, add if security concerns arise
   - **Revisit**: After 3 months of production use

2. **Skill Sharing**: Should skills be shareable across projects?
   - **Recommendation**: Keep project-specific for now
   - **Revisit**: If other projects request skills, create shared skill registry

3. **Skill Marketplace**: Should we create a public skill marketplace?
   - **Recommendation**: No (too early)
   - **Revisit**: After 6 months if skills prove valuable

4. **Skill Versioning**: How to handle breaking changes?
   - **Recommendation**: Semantic versioning in SKILL.md, agents pin versions
   - **Revisit**: If version conflicts emerge

---

## Next Steps

**Immediate (This Week)**:
1. architect creates this spec → project_manager reviews
2. User approves spec via user_listener
3. project_manager adds PRIORITY to ROADMAP

**Short-term (Next 2 Weeks)**:
1. code_developer implements Phase 1 (infrastructure)
2. code_developer implements Phase 2 (pilot skills)
3. architect reviews code quality

**Medium-term (Next 1-2 Months)**:
1. project_manager creates documentation
2. Agents gradually add skills
3. Langfuse integration (Phase 2)

---

## Appendix A: Example Skills

### A.1 architect/dependency-analysis

**SKILL.md**:
```yaml
---
name: dependency-analysis
version: 1.0.0
agent: architect
scope: agent-specific
triggers:
  - "analyze dependency"
  - "check package security"
---
```

**check_security.py**:
```python
import json
import argparse
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    package = context["package_name"]
    version = context["version"]

    # Check CVEs
    cves = check_cves(package, version)

    # Check license
    license_info = check_license(package)

    # Check maintenance
    maintenance = check_maintenance(package)

    result = {
        "security": {"cves": cves},
        "licensing": license_info,
        "maintenance": maintenance
    }

    print(json.dumps(result, indent=2))

def check_cves(package: str, version: str) -> list:
    # Query CVE database...
    return []

def check_license(package: str) -> dict:
    # Query PyPI for license...
    return {"license": "MIT", "compatible": True}

def check_maintenance(package: str) -> dict:
    # Query PyPI for last update...
    return {"last_update": "2025-09-01", "active": True}

if __name__ == "__main__":
    main()
```

### A.2 code-searcher/security-audit

**SKILL.md**:
```yaml
---
name: security-audit
version: 1.0.0
agent: code-searcher
scope: agent-specific
triggers:
  - "security audit"
  - "find vulnerabilities"
  - "scan for CVEs"
---
```

**scan_vulnerabilities.py**:
```python
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    codebase_path = context.get("codebase_path", ".")

    # Scan for common vulnerabilities
    results = scan_codebase(Path(codebase_path))

    print(json.dumps(results, indent=2))

def scan_codebase(path: Path) -> dict:
    vulnerabilities = []

    # Scan for SQL injection
    # Scan for XSS
    # Scan for insecure deserialization
    # etc.

    return {
        "vulnerabilities": vulnerabilities,
        "score": 10.0,
        "scanned_files": 150
    }

if __name__ == "__main__":
    main()
```

### A.3 assistant/demo-creator

**SKILL.md**:
```yaml
---
name: demo-creator
version: 1.0.0
agent: assistant
scope: agent-specific
triggers:
  - "create demo"
  - "show how it works"
  - "visual demonstration"
---
```

**create_puppeteer_demo.py**:
```python
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    args = parser.parse_args()

    with open(args.context) as f:
        context = json.load(f)

    feature_name = context["feature_name"]
    url = context.get("url", "http://localhost:8000")

    # Create Puppeteer demo
    demo_result = create_demo(feature_name, url)

    print(json.dumps(demo_result, indent=2))

def create_demo(feature: str, url: str) -> dict:
    # Use Puppeteer MCP to create demo
    # 1. Navigate to URL
    # 2. Interact with feature
    # 3. Take screenshots
    # 4. Generate video

    return {
        "screenshots": ["demo_1.png", "demo_2.png"],
        "video": "demo.mp4",
        "steps": ["Step 1", "Step 2", "Step 3"]
    }

if __name__ == "__main__":
    main()
```

---

## Appendix B: Skills vs. Prompts Decision Tree

```
Task to implement?
    │
    ├─ Requires reliable calculation? ────────────── YES → Use SKILL
    │                                                NO ↓
    ├─ Requires external API call? ────────────── YES → Use SKILL
    │                                                NO ↓
    ├─ Requires file/code parsing? ────────────── YES → Use SKILL
    │                                                NO ↓
    ├─ Repetitive task (same logic)? ─────────── YES → Use SKILL
    │                                                NO ↓
    ├─ Requires creative writing? ────────────── YES → Use PROMPT
    │                                                NO ↓
    ├─ Requires complex reasoning? ───────────── YES → Use PROMPT
    │                                                NO ↓
    ├─ One-off task? ─────────────────────────── YES → Use PROMPT
    │                                                NO ↓
    └─ Need both data + interpretation? ──────── YES → Use HYBRID
```

---

## Conclusion

This specification provides a comprehensive technical architecture for integrating Claude Skills into the MonolithicCoffeeMakerAgent system. Skills will **complement** (not replace) the existing prompt system, providing executable code capabilities where reliability matters, while prompts continue to handle creative reasoning and analysis.

**Key Takeaways**:
1. **Complementary**: Skills + Prompts work together (hybrid approach)
2. **Gradual**: Pilot skills first, expand based on success
3. **Backward Compatible**: No breaking changes to existing system
4. **Observable**: Langfuse integration for monitoring (Phase 2)
5. **Agent-Specific**: Each agent gets relevant skills automatically

**Implementation Ready**: This spec can be handed to code_developer for implementation.

---

**Status**: Ready for review by project_manager and user approval
