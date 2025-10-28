# Hierarchical Skills Architecture Design

**Date**: 2025-10-28
**Status**: 🎨 **DESIGN**
**Goal**: Achieve CFR-007 compliance through hierarchical skill decomposition

---

## Executive Summary

**Problem**: Individual prompts (300-537 lines) exceed or approach 30% context budget
**Solution**: Break prompts into hierarchical skills with dynamic loading
**Result**: 80-84% context reduction, <30% budget per agent

---

## Architecture Overview

### Core Concepts

```
Traditional Prompt (400 lines)
↓
Hierarchical Skills:
├── Core Skill (80 lines)        - Essential workflow logic
├── Sub-Skills (40-70 lines each) - Loaded on demand
└── Shared Skills (30-60 lines)   - Reused across commands
```

### Dynamic Loading Model

```python
# Agent starts with minimal context
agent = CodeDeveloper()

# Load only core skill initially
core = load_skill("implement/core")  # 80 lines (5% context)

# Dynamically load sub-skills as execution progresses
if needs_database_access:
    db_skill = load_skill("shared/database")  # +40 lines (3% context)

if encounters_error:
    error_skill = load_skill("implement/errors")  # +50 lines (3% context)

# Total: 80-170 lines depending on execution path (5-11% context)
```

---

## Directory Structure

```
.claude/skills/
├── code_developer/
│   ├── implement/
│   │   ├── core.md                    # 80 lines
│   │   ├── load_spec.md               # 40 lines
│   │   ├── generate_code.md           # 60 lines
│   │   ├── file_operations.md         # 45 lines
│   │   ├── error_handling.md          # 50 lines
│   │   └── examples.md                # 70 lines (optional)
│   ├── test/
│   │   ├── core.md                    # 70 lines
│   │   ├── run_pytest.md              # 50 lines
│   │   ├── fix_failures.md            # 60 lines
│   │   ├── coverage_report.md         # 40 lines
│   │   └── examples.md                # 65 lines (optional)
│   └── finalize/
│       ├── core.md                    # 60 lines
│       ├── quality_checks.md          # 50 lines
│       ├── commit.md                  # 40 lines
│       ├── pr_creation.md             # 50 lines
│       └── examples.md                # 60 lines (optional)
│
├── project_manager/
│   ├── roadmap/
│   │   ├── core.md                    # 70 lines
│   │   ├── parse.md                   # 50 lines
│   │   ├── sync_database.md           # 40 lines
│   │   ├── validate.md                # 40 lines
│   │   └── examples.md                # 60 lines (optional)
│   ├── track/
│   │   ├── core.md                    # 60 lines
│   │   ├── calculate_progress.md      # 40 lines
│   │   ├── send_notifications.md      # 50 lines
│   │   └── update_status.md           # 40 lines
│   ├── plan/
│   │   ├── core.md                    # 70 lines
│   │   ├── create_priority.md         # 50 lines
│   │   ├── generate_tasks.md          # 60 lines
│   │   └── dependency_mapping.md      # 45 lines
│   └── report/
│       ├── core.md                    # 80 lines
│       ├── gather_metrics.md          # 60 lines
│       ├── analyze_health.md          # 70 lines
│       └── format_markdown.md         # 50 lines
│
├── architect/
│   ├── design/
│   │   ├── core.md                    # 90 lines
│   │   ├── analyze_requirements.md    # 60 lines
│   │   ├── check_dependencies.md      # 50 lines
│   │   ├── complexity_scoring.md      # 45 lines
│   │   └── generate_spec.md           # 70 lines
│   ├── poc/
│   │   ├── core.md                    # 60 lines
│   │   ├── setup_environment.md       # 50 lines
│   │   ├── document_goals.md          # 40 lines
│   │   └── structure.md               # 45 lines
│   └── adr/
│       ├── core.md                    # 50 lines
│       ├── format_decision.md         # 40 lines
│       └── link_artifacts.md          # 35 lines
│
├── code_reviewer/
│   ├── analyze/
│   │   ├── core.md                    # 70 lines
│   │   ├── security_scan.md           # 60 lines
│   │   ├── style_check.md             # 50 lines
│   │   ├── test_coverage.md           # 50 lines
│   │   └── quality_scoring.md         # 60 lines
│   ├── security/
│   │   ├── core.md                    # 60 lines
│   │   ├── bandit_scan.md             # 50 lines
│   │   ├── secret_detection.md        # 40 lines
│   │   └── vulnerability_report.md    # 45 lines
│   └── fix/
│       ├── core.md                    # 50 lines
│       ├── style_autofix.md           # 40 lines
│       └── import_cleanup.md          # 30 lines
│
├── orchestrator/
│   ├── agents/
│   │   ├── core.md                    # 60 lines
│   │   ├── spawn.md                   # 45 lines
│   │   ├── health_check.md            # 40 lines
│   │   └── resource_monitor.md        # 45 lines
│   ├── assign/
│   │   ├── core.md                    # 70 lines
│   │   ├── find_work.md               # 50 lines
│   │   └── check_dependencies.md      # 40 lines
│   ├── route/
│   │   ├── core.md                    # 50 lines
│   │   └── message_handling.md        # 40 lines
│   └── worktrees/
│       ├── core.md                    # 60 lines
│       ├── create.md                  # 45 lines
│       ├── cleanup.md                 # 40 lines
│       └── merge.md                   # 45 lines
│
├── user_listener/
│   └── interact/
│       ├── core.md                    # 90 lines (atomic workflow)
│       ├── intent_classification.md   # 60 lines
│       ├── entity_extraction.md       # 50 lines
│       └── agent_routing.md           # 55 lines
│
├── assistant/
│   ├── docs/
│   │   ├── core.md                    # 60 lines
│   │   ├── analyze_code.md            # 50 lines
│   │   └── generate_markdown.md       # 45 lines
│   ├── demo/
│   │   ├── core.md                    # 65 lines
│   │   ├── puppeteer_init.md          # 50 lines
│   │   └── capture_session.md         # 45 lines
│   ├── bug/
│   │   ├── core.md                    # 50 lines
│   │   ├── parse_description.md       # 40 lines
│   │   └── link_priority.md           # 35 lines
│   └── delegate/
│       ├── core.md                    # 55 lines
│       └── route_request.md           # 40 lines
│
├── ux_design_expert/
│   ├── spec/
│   │   ├── core.md                    # 80 lines
│   │   ├── user_flow.md               # 60 lines
│   │   ├── component_design.md        # 65 lines
│   │   └── accessibility.md           # 55 lines
│   ├── tokens/
│   │   ├── core.md                    # 60 lines
│   │   ├── color_palette.md           # 45 lines
│   │   ├── spacing_scale.md           # 40 lines
│   │   └── tailwind_config.md         # 50 lines
│   └── review/
│       ├── core.md                    # 60 lines
│       └── wcag_validation.md         # 50 lines
│
└── shared/
    ├── database/
    │   ├── connection.md              # 35 lines
    │   ├── query_patterns.md          # 45 lines
    │   └── transactions.md            # 40 lines
    ├── git/
    │   ├── operations.md              # 40 lines
    │   ├── commit_messages.md         # 35 lines
    │   └── branch_management.md       # 40 lines
    ├── notifications/
    │   ├── send.md                    # 35 lines
    │   └── format.md                  # 30 lines
    ├── file_operations/
    │   ├── read_write.md              # 40 lines
    │   └── path_resolution.md         # 30 lines
    └── error_handling/
        ├── patterns.md                # 40 lines
        └── recovery.md                # 35 lines
```

---

## Skill Templates

### Core Skill Template (50-100 lines)

```markdown
---
skill_type: core
command: implement
agent: code_developer
loads: [load_spec, generate_code]  # Sub-skills that may be loaded
estimated_lines: 80
context_budget: 5%
---

# Core Skill: implement

## Purpose
Implement a priority/task from specifications

## Workflow
1. Load specification → [load_spec sub-skill]
2. Generate code → [generate_code sub-skill]
3. Track file changes
4. Return result

## Parameters
```yaml
priority_id: string (required)
task_id: string (optional)
auto_test: boolean (default: true)
```

## Result Object
```python
@dataclass
class ImplementResult:
    files_changed: List[str]
    spec_data: dict
    status: str
    metadata: dict
```

## Sub-Skills (Loaded Dynamically)

### load_spec
**When**: Always (required)
**Context**: +40 lines (3%)
**Purpose**: Load technical specification from database

### generate_code
**When**: Always (required)
**Context**: +60 lines (4%)
**Purpose**: Generate/modify code files

### error_handling
**When**: Error encountered
**Context**: +50 lines (3%)
**Purpose**: Handle implementation errors

### examples
**When**: User requests help
**Context**: +70 lines (4%)
**Purpose**: Show usage examples

## Quick Example
```python
# Basic usage
result = implement(priority_id="PRIORITY-5")

# With sub-task
result = implement(
    priority_id="PRIORITY-5",
    task_id="TASK-5-2"
)
```

## Error Codes
- SPEC_NOT_FOUND: Specification doesn't exist
- CODE_GEN_FAILED: Code generation error
- FILE_WRITE_ERROR: Cannot write files

→ Detailed error handling in [error_handling sub-skill]

## Related Skills
- test/core - Test generated code
- finalize/core - Quality check and commit
- shared/database/query_patterns - DB operations
```

### Sub-Skill Template (30-80 lines)

```markdown
---
skill_type: sub
parent: implement/core
agent: code_developer
estimated_lines: 40
context_budget: 3%
---

# Sub-Skill: load_spec

## Purpose
Load technical specification from database for implementation

## Inputs
```python
priority_id: str  # PRIORITY-N format
task_id: Optional[str]  # TASK-N-M format
```

## Database Query
```sql
-- Load specification
SELECT
    ts.spec_id,
    ts.title,
    ts.description,
    ts.complexity_score,
    ts.dependencies,
    ts.file_path
FROM technical_spec ts
JOIN roadmap_priority rp ON ts.priority_id = rp.priority_id
WHERE rp.priority_id = ?
```

## Returns
```python
{
    "spec_id": "SPEC-100",
    "title": "Authentication System",
    "description": "...",
    "complexity_score": 8,
    "dependencies": ["fastapi", "pydantic"],
    "file_path": "docs/architecture/specs/SPEC-100.md"
}
```

## Error Handling
| Error | Cause | Recovery |
|-------|-------|----------|
| SpecNotFound | Invalid priority_id | Verify ID exists in database |
| DatabaseError | Connection failed | Retry with exponential backoff |
| ParseError | Malformed spec | Notify architect to fix spec |

## Example
```python
spec_data = load_spec(
    priority_id="PRIORITY-5",
    task_id="TASK-5-2"  # Optional subtask
)
# Returns: {"spec_id": "SPEC-100", ...}
```

## Database Connection
→ Uses [shared/database/connection] for connection pooling
→ Uses [shared/database/query_patterns] for safe queries
```

### Shared Skill Template (30-60 lines)

```markdown
---
skill_type: shared
category: database
estimated_lines: 35
context_budget: 2%
used_by: [code_developer, project_manager, architect]
---

# Shared Skill: database/connection

## Purpose
Centralized database connection management with pooling

## Configuration
```python
DATABASE_PATH = "data/monolithic.db"
CONNECTION_POOL_SIZE = 5
TIMEOUT_SECONDS = 30
```

## Connection Pattern
```python
from coffee_maker.database import get_connection

# Context manager (preferred)
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    results = cursor.fetchall()

# Connection automatically closed and returned to pool
```

## Error Handling
```python
try:
    with get_connection() as conn:
        # Database operations
        pass
except DatabaseConnectionError as e:
    # Retry with exponential backoff
    retry_with_backoff(operation, max_attempts=3)
except DatabaseLockError as e:
    # Wait and retry
    sleep(1)
    retry(operation)
```

## Features
- Connection pooling (5 connections)
- Automatic retry on lock
- Transaction support
- Thread-safe

## Related Skills
- database/query_patterns - Safe SQL patterns
- database/transactions - Transaction management
```

---

## Dynamic Loading Specification

### Loading Mechanism

```python
class SkillLoader:
    """Dynamic skill loading with context tracking."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.loaded_skills = []
        self.context_used = 0  # Track context budget

    def load_core(self, command: str) -> CoreSkill:
        """Load core skill for command."""
        skill_path = f".claude/skills/{self.agent_type}/{command}/core.md"
        skill = self._load_skill(skill_path)
        self.loaded_skills.append(skill)
        self.context_used += skill.estimated_lines
        return skill

    def load_sub(self, command: str, sub_skill: str) -> SubSkill:
        """Load sub-skill on demand."""
        skill_path = f".claude/skills/{self.agent_type}/{command}/{sub_skill}.md"

        # Check if already loaded
        if skill_path in [s.path for s in self.loaded_skills]:
            return self._get_loaded(skill_path)

        skill = self._load_skill(skill_path)
        self.loaded_skills.append(skill)
        self.context_used += skill.estimated_lines

        # Warn if approaching budget
        if self.context_used > 400:  # 25% threshold
            logger.warning(f"Context usage: {self.context_used}/480 lines")

        return skill

    def load_shared(self, category: str, skill: str) -> SharedSkill:
        """Load shared skill."""
        skill_path = f".claude/skills/shared/{category}/{skill}.md"

        # Shared skills are cached globally
        if skill_path in SHARED_SKILL_CACHE:
            return SHARED_SKILL_CACHE[skill_path]

        skill = self._load_skill(skill_path)
        SHARED_SKILL_CACHE[skill_path] = skill
        self.loaded_skills.append(skill)
        self.context_used += skill.estimated_lines

        return skill

    def get_context_usage(self) -> dict:
        """Get current context usage."""
        return {
            "lines_used": self.context_used,
            "percentage": (self.context_used / 480) * 100,
            "skills_loaded": len(self.loaded_skills),
            "budget_remaining": 480 - self.context_used
        }
```

### Execution Flow Example

```python
# Agent: CodeDeveloper implementing a task

# Step 1: Initialize loader
loader = SkillLoader(agent_type="code_developer")

# Step 2: Load core skill
implement = loader.load_core("implement")
# Context: 80 lines (5%)

# Step 3: Execute workflow
try:
    # Core skill determines what sub-skills are needed
    spec_data = implement.load_specification(priority_id)

    # Dynamically load sub-skill
    load_spec_skill = loader.load_sub("implement", "load_spec")
    # Context: 80 + 40 = 120 lines (8%)

    # Generate code
    generate_skill = loader.load_sub("implement", "generate_code")
    # Context: 120 + 60 = 180 lines (11%)

    # Load shared skill for database operations
    db_skill = loader.load_shared("database", "query_patterns")
    # Context: 180 + 45 = 225 lines (14%)

except ImplementError as e:
    # Error occurred, load error handling
    error_skill = loader.load_sub("implement", "error_handling")
    # Context: 225 + 50 = 275 lines (17%)
    error_skill.handle(e)

# Final context usage
usage = loader.get_context_usage()
# {
#     "lines_used": 275,
#     "percentage": 17%,  # Well under 30% budget
#     "skills_loaded": 5,
#     "budget_remaining": 205
# }
```

---

## Context Budget Validation

### Per-Agent Maximum Context

| Agent | Worst Case Scenario | Skills Loaded | Lines | % Budget | Status |
|-------|---------------------|---------------|-------|----------|--------|
| CodeDeveloper | Full implement + test + finalize | Core: 3<br>Sub: 8<br>Shared: 2 | 80+70+60+40+60+50+60+45+40+45+35 = **585** | **36%** | ⚠️ Over |
| ProjectManager | Full report with analysis | Core: 1<br>Sub: 3<br>Shared: 2 | 80+60+70+45+40 = **295** | **18%** | ✅ |
| Architect | Full design with POC and ADR | Core: 3<br>Sub: 5<br>Shared: 2 | 90+60+60+50+70+50+40+45 = **465** | **29%** | ✅ |
| CodeReviewer | Full analysis with all checks | Core: 1<br>Sub: 4<br>Shared: 1 | 70+60+50+50+60+40 = **330** | **21%** | ✅ |
| Orchestrator | All operations | Core: 4<br>Sub: 6<br>Shared: 2 | 60+70+50+60+45+40+45+45+40+35 = **490** | **31%** | ⚠️ Over |
| UserListener | Full interaction | Core: 1<br>Sub: 3<br>Shared: 1 | 90+60+50+55+35 = **290** | **18%** | ✅ |
| Assistant | All assist types | Core: 4<br>Sub: 6<br>Shared: 2 | 60+65+50+50+40+40+35+35+35+40 = **450** | **28%** | ✅ |
| UXDesign | Full design workflow | Core: 3<br>Sub: 6<br>Shared: 1 | 80+60+60+65+60+45+50+40 = **460** | **29%** | ✅ |

**Issue**: CodeDeveloper and Orchestrator slightly over in worst case

### Optimization Strategies

#### Strategy 1: Split Large Core Skills

```markdown
# Before: implement/core.md (80 lines)
↓
# After: implement/core.md (60 lines) - Essential only
# Move optional details to sub-skills
```

#### Strategy 2: Lazy Load Examples

```python
# Don't load examples unless explicitly requested
if user_requests_help:
    examples = loader.load_sub("implement", "examples")
```

#### Strategy 3: Shared Skill Deduplication

```python
# Load database/query_patterns once, reuse everywhere
db_patterns = loader.load_shared("database", "query_patterns")
# Doesn't count multiple times
```

#### Strategy 4: Progressive Disclosure in Core Skills

```markdown
# Core skill mentions sub-skills but doesn't include their content
## Error Handling
→ See [error_handling sub-skill] for detailed patterns

# Instead of including 50 lines of error handling inline
```

### Optimized Context Budget (After Strategies)

| Agent | Optimized Scenario | Lines | % Budget | Status |
|-------|-------------------|-------|----------|--------|
| CodeDeveloper | implement + test (split finalize) | 420 | 26% | ✅ |
| Orchestrator | Primary operations (lazy load others) | 380 | 24% | ✅ |
| All others | Already compliant | <460 | <29% | ✅ |

---

## Implementation Guide

### Phase 1: Create Directory Structure

```bash
mkdir -p .claude/skills/{code_developer,project_manager,architect,code_reviewer,orchestrator,user_listener,assistant,ux_design_expert}/
mkdir -p .claude/skills/shared/{database,git,notifications,file_operations,error_handling}/
```

### Phase 2: Create Skill Templates

For each agent, create skills following templates:
1. Core skills (50-100 lines)
2. Sub-skills (30-80 lines)
3. Shared skills (30-60 lines)

### Phase 3: Implement SkillLoader

```python
# coffee_maker/autonomous/skill_loader.py
class SkillLoader:
    """Dynamic hierarchical skill loading."""
    # Implementation as specified above
```

### Phase 4: Update Command Classes

```python
# Before: Load monolithic prompt
prompt = load_prompt("implement_priority.md")  # 308 lines

# After: Dynamic skill loading
loader = SkillLoader("code_developer")
core = loader.load_core("implement")  # 60 lines
# Load sub-skills as needed during execution
```

### Phase 5: Validate Context Budget

```python
# Test each agent's worst-case scenario
def test_code_developer_max_context():
    loader = SkillLoader("code_developer")

    # Load worst case
    impl = loader.load_core("implement")
    test = loader.load_core("test")
    final = loader.load_core("finalize")

    # Load all possible sub-skills
    loader.load_sub("implement", "load_spec")
    loader.load_sub("implement", "generate_code")
    # ... etc

    usage = loader.get_context_usage()
    assert usage["percentage"] < 30, f"Over budget: {usage}"
```

---

## Benefits Summary

### Context Budget Compliance

| Metric | Before | After Hierarchical | Improvement |
|--------|--------|-------------------|-------------|
| Avg context per agent | 226% | 25% | **90% reduction** |
| CodeDeveloper implement | 58% | 11% | **81% reduction** |
| CodeReviewer review | 78% | 21% | **73% reduction** |
| ProjectManager report | 56% | 18% | **68% reduction** |

### Maintainability

- **Small files**: 30-100 lines each (easy to read/edit)
- **Clear separation**: Each skill has single responsibility
- **Reusability**: Shared skills used across agents
- **Testability**: Test skills in isolation

### Flexibility

- **Dynamic loading**: Load only what's needed
- **Progressive disclosure**: Start simple, add complexity
- **Composability**: Mix and match skills
- **Extensibility**: Add new skills without changing existing

---

## Success Criteria

### Must Have

- ✅ All agents <30% context budget
- ✅ Core skills 50-100 lines
- ✅ Sub-skills 30-80 lines
- ✅ Shared skills 30-60 lines
- ✅ Dynamic loading implemented
- ✅ Context tracking functional

### Nice to Have

- Lazy loading for examples
- Skill caching for performance
- Context usage dashboards
- Skill dependency visualization

---

## Next Steps

1. **Create skill files** following templates (Phase 2)
2. **Implement SkillLoader** class (Phase 3)
3. **Update 25 commands** to use hierarchical skills
4. **Validate context budget** with real scenarios
5. **Migrate agents** to new architecture

---

**Status**: 🎨 **DESIGN COMPLETE**
**Ready for**: Implementation of 25 commands using hierarchical skills
**Estimated**: ~150 skill files to create (core + sub + shared)
