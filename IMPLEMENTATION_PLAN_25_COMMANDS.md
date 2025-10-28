# Implementation Plan: 25 Commands with Core + Examples

**Date**: 2025-10-28
**Approach**: Option 2 - Minimal Core + Optional Examples
**Total Files**: 50 (25 cores + 25 examples)
**Goal**: CFR-007 compliance with practical AI support

---

## Overview

### File Structure
```
.claude/commands/v2/
├── code_developer/
│   ├── implement.md              # 60 lines - Core
│   ├── implement_examples.md     # 60 lines - Examples
│   ├── test.md                   # 55 lines - Core
│   ├── test_examples.md          # 55 lines - Examples
│   ├── finalize.md               # 50 lines - Core
│   └── finalize_examples.md      # 50 lines - Examples
├── project_manager/
│   ├── roadmap.md + roadmap_examples.md
│   ├── track.md + track_examples.md
│   ├── plan.md + plan_examples.md
│   └── report.md + report_examples.md
├── architect/
│   ├── design.md + design_examples.md
│   ├── poc.md + poc_examples.md
│   └── adr.md + adr_examples.md
├── code_reviewer/
│   ├── analyze.md + analyze_examples.md
│   ├── security.md + security_examples.md
│   └── fix.md + fix_examples.md
├── orchestrator/
│   ├── agents.md + agents_examples.md
│   ├── assign.md + assign_examples.md
│   ├── route.md + route_examples.md
│   └── worktrees.md + worktrees_examples.md
├── user_listener/
│   └── interact.md + interact_examples.md
├── assistant/
│   ├── docs.md + docs_examples.md
│   ├── demo.md + demo_examples.md
│   ├── bug.md + bug_examples.md
│   └── delegate.md + delegate_examples.md
└── ux_design_expert/
    ├── spec.md + spec_examples.md
    ├── tokens.md + tokens_examples.md
    └── review.md + review_examples.md
```

---

## 25 Commands Breakdown

### CodeDeveloper (3 commands)
1. **implement** - Load spec, generate code, track files
2. **test** - Run pytest with coverage, auto-retry on failure
3. **finalize** - Quality checks (Black, MyPy), commit with conventional message

### ProjectManager (4 commands)
4. **roadmap** - Parse/validate/sync ROADMAP.md with database
5. **track** - Update priority status, calculate progress, send notifications
6. **plan** - Create new priority, generate task breakdown
7. **report** - Generate status report with metrics and health analysis

### Architect (3 commands)
8. **design** - Analyze requirements, check dependencies, generate spec
9. **poc** - Create POC directory structure, setup environment
10. **adr** - Document architectural decision with rationale

### CodeReviewer (3 commands)
11. **analyze** - Run all checks (security, style, tests, complexity), generate quality score
12. **security** - Deep security scan with Bandit, secret detection
13. **fix** - Auto-fix style issues with Black/autoflake

### Orchestrator (4 commands)
14. **agents** - Spawn/kill/monitor agent lifecycle, health checks
15. **assign** - Find parallelizable tasks, check dependencies, assign to agents
16. **route** - Route inter-agent messages from agent_message table
17. **worktrees** - Create/cleanup git worktrees (CFR-013 compliant)

### UserListener (1 command)
18. **interact** - Classify intent, determine agent, route request, format response

### Assistant (4 commands)
19. **docs** - Generate documentation for component/feature
20. **demo** - Create interactive demo with Puppeteer MCP
21. **bug** - Track bug report, link to priority, notify PM
22. **delegate** - Classify request, determine target agent, forward

### UXDesignExpert (3 commands)
23. **spec** - Create UI specification with user flow and accessibility
24. **tokens** - Generate design tokens (colors, spacing, typography), Tailwind config
25. **review** - Validate existing design for WCAG compliance

---

## Core Prompt Template (60 lines)

```markdown
# {command}

## Purpose
[1-2 sentences describing what this command does]

## Parameters
```yaml
param1: type = default  # Description
param2: type  # Required parameter
```

## Workflow
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]
5. Return result

## Database Query
```sql
-- [Description]
SELECT field1, field2, field3
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.foreign_id
WHERE condition = ?
```

## Result Object
```python
@dataclass
class {Command}Result:
    field1: type
    field2: type
    status: str  # "success" | "partial" | "failed"
    metadata: dict
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| ErrorType1 | Why it happens | What to do |
| ErrorType2 | Why it happens | What to do |

## Example
```python
result = command(param="value")
# {Command}Result(
#   field1="value",
#   status="success"
# )
```

## Database Connection
Use: `with get_connection() as conn:` (connection pooling)

## Related Commands
- other_command1() - What it does
- other_command2() - What it does

---
Estimated lines: 60
Context: ~4%
For examples: See {command}_examples.md
```

---

## Examples File Template (60 lines)

```markdown
# {command} - Examples & Patterns

## Example 1: Basic Usage
```python
result = command(param="value")
assert result.status == "success"
```

## Example 2: Advanced Usage
```python
result = command(
    param1="value1",
    param2="value2",
    option=True
)
```

## Example 3: Error Handling
```python
result = command(param="value")
if result.status == "failed":
    print(f"Error: {result.metadata['error']}")
    # Recovery steps
```

## Example 4: Integration Pattern
```python
# Combining with other commands
result1 = command1(param="value")
if result1.status == "success":
    result2 = command2(data=result1.field1)
```

## Pattern: [Common Use Case]
[Description of pattern]
[Code example]

## Pattern: [Another Use Case]
[Description]
[Code example]

## Common Issues
- Issue 1: Cause and solution
- Issue 2: Cause and solution
- Issue 3: Cause and solution

## Performance Tips
- Tip 1
- Tip 2
- Tip 3

## Edge Cases
- Edge case 1 and how to handle
- Edge case 2 and how to handle

---
Estimated lines: 60
Context: ~4%
Load when: AI needs help or user requests examples
```

---

## Implementation Phases

### Phase 1: Create Directory Structure ✅
```bash
mkdir -p .claude/commands/v2/{code_developer,project_manager,architect,code_reviewer,orchestrator,user_listener,assistant,ux_design_expert}
```

### Phase 2: Create Core Prompts (Priority)
**Order**: Create in usage frequency order
1. CodeDeveloper: implement, test, finalize (most used)
2. ProjectManager: roadmap, track, plan, report
3. CodeReviewer: analyze, security, fix
4. Architect: design, poc, adr
5. Orchestrator: agents, assign, route, worktrees
6. UserListener: interact
7. Assistant: docs, demo, bug, delegate
8. UXDesignExpert: spec, tokens, review

**Estimated time**: 25 files × 30 min = 12.5 hours (1.5 days)

### Phase 3: Create Example Files
**Order**: Same as Phase 2
**Estimated time**: 25 files × 20 min = 8.5 hours (1 day)

### Phase 4: Implement Smart Loading Logic
**File**: `coffee_maker/commands/loader.py`

```python
class CommandLoader:
    """Smart command prompt loader with context tracking."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.loaded_prompts = {}
        self.context_lines = 0

    def load_command(self, command: str, load_examples: bool = False) -> str:
        """Load command prompt, optionally with examples."""
        # Load core
        core_path = f".claude/commands/v2/{self.agent_type}/{command}.md"
        core_content = self._read_file(core_path)
        self.loaded_prompts[command] = core_content
        self.context_lines += self._count_lines(core_content)

        # Load examples if requested
        if load_examples:
            examples_path = f".claude/commands/v2/{self.agent_type}/{command}_examples.md"
            examples_content = self._read_file(examples_path)
            self.loaded_prompts[f"{command}_examples"] = examples_content
            self.context_lines += self._count_lines(examples_content)

        return core_content

    def get_context_usage(self) -> dict:
        """Get current context usage statistics."""
        return {
            "lines": self.context_lines,
            "percentage": (self.context_lines / 1600) * 100,
            "prompts_loaded": len(self.loaded_prompts),
            "budget_remaining": 1600 - self.context_lines,
            "under_30_percent": self.context_lines < 480
        }
```

**Estimated time**: 4 hours

### Phase 5: Create Command Classes
**Directory**: `coffee_maker/commands/v2/`

Each command class:
```python
class ImplementCommand:
    """Implement a task from specification."""

    def __init__(self, db_path: Optional[str] = None):
        self.db = Database(db_path)
        self.loader = CommandLoader("code_developer")

    def execute(self, task_id: str, **kwargs) -> ImplementResult:
        """Execute implement command."""
        # Load prompt
        prompt = self.loader.load_command("implement")

        # Execute logic using prompt guidance
        try:
            # Implementation...
            return ImplementResult(...)
        except Exception as e:
            # Load examples for help
            examples = self.loader.load_command("implement", load_examples=True)
            # Retry with examples context
            return self._retry_with_examples(task_id, **kwargs)
```

**Estimated time**: 25 classes × 1 hour = 25 hours (3 days)

### Phase 6: Create Tests
**File**: `tests/unit/test_v2_commands.py`

Test each command:
- Core functionality
- Error handling
- Result object structure
- Context budget validation

**Estimated time**: 8 hours (1 day)

### Phase 7: Context Budget Validation
Run tests to verify:
- Normal usage: <25% context
- With examples: <30% context
- Document actual usage patterns

**Estimated time**: 4 hours

---

## Total Effort Estimate

| Phase | Tasks | Time | Status |
|-------|-------|------|--------|
| Phase 1 | Directory structure | 0.5h | Ready |
| Phase 2 | 25 core prompts | 12.5h | Ready to start |
| Phase 3 | 25 example files | 8.5h | After Phase 2 |
| Phase 4 | Smart loader | 4h | After Phase 2 |
| Phase 5 | 25 command classes | 25h | After Phase 2 |
| Phase 6 | Test suite | 8h | After Phase 5 |
| Phase 7 | Validation | 4h | After Phase 6 |
| **Total** | | **62.5h** | **~8 days** |

---

## Context Budget Targets

| Agent | Commands | Normal | With Examples | Target |
|-------|----------|--------|---------------|--------|
| CodeDeveloper | 3 | 180 lines (11%) | 240 lines (15%) | <30% ✅ |
| ProjectManager | 2-3 | 165 lines (10%) | 220 lines (14%) | <30% ✅ |
| Architect | 2-3 | 175 lines (11%) | 230 lines (14%) | <30% ✅ |
| CodeReviewer | 2 | 130 lines (8%) | 190 lines (12%) | <30% ✅ |
| Orchestrator | 2-3 | 160 lines (10%) | 215 lines (13%) | <30% ✅ |
| UserListener | 1 | 60 lines (4%) | 120 lines (8%) | <30% ✅ |
| Assistant | 1-2 | 110 lines (7%) | 170 lines (11%) | <30% ✅ |
| UXDesignExpert | 2 | 125 lines (8%) | 185 lines (12%) | <30% ✅ |

---

## Success Criteria

### Must Have
- ✅ All 25 core prompts created (60 lines each)
- ✅ All 25 example files created (60 lines each)
- ✅ Smart loader implemented with context tracking
- ✅ All 25 command classes functional
- ✅ Context budget <30% per agent (normal usage)
- ✅ 100% test coverage

### Nice to Have
- Context usage dashboard
- Automatic example loading when AI detects errors
- Prompt versioning
- Usage analytics

---

## Migration Strategy

### Step 1: Create v2 commands alongside existing
Keep old commands working during development

### Step 2: Test v2 commands thoroughly
Validate functionality and context budget

### Step 3: Update agents to use v2
One agent at a time, with fallback to old commands

### Step 4: Deprecate old commands
After all agents migrated and tested

### Step 5: Cleanup
Remove old command files, ultra-consolidated workflow commands

---

## Next Steps

1. **Create directory structure** (Phase 1)
2. **Start with CodeDeveloper core prompts** (highest priority)
3. **Implement smart loader** (parallel with Phase 2)
4. **Create command classes** (as prompts are ready)
5. **Continuous testing and validation**

---

**Status**: 📋 **READY TO START**
**Approach**: Option 2 - Minimal Core + Optional Examples
**Total effort**: ~8 days
**First task**: Create directory structure and CodeDeveloper core prompts
