# CFR-018: Command Execution Context Budget

**Status**: Active ✅
**Created**: 2025-10-28
**Owner**: All Agents
**Related**: CFR-007 (Context Budget), CFR-017 (Spec Size Limit)

---

## Requirement

**When executing a single command, the total agent infrastructure MUST be ≤480 lines (30% of context budget).**

### Formula (User-Specified)
```
command_prompt + all_prompts_for_this_agent + skills_loaded < 30%
```

Where:
- **command_prompt**: The specific command file (e.g., implement.md)
- **all_prompts_for_this_agent**: Agent system prompt (README.md)
- **skills_loaded**: External skills loaded (target: 0, all embedded)
  - **Assumption**: Auto-loaded system skills ≤10% (160 lines)
  - **Explicit skills**: 0 lines (embedded in commands)
- **30%**: 480 lines of 1,600 line budget

**Budget accounting**:
```
Command + Agent README: ≤20% (320 lines) - under our control
Auto-loaded system skills: ≤10% (160 lines) - assumed
────────────────────────────────────────────────────────
Total: ≤30% (480 lines) ✅
```

This leaves 70% of context (1,120 lines) for actual work content: task specifications, code, and execution context.

### Execution Constraint
**Agent MUST terminate (kill itself) after command completes.** No long-running agents, no command loops. Each command invocation = one agent lifecycle.

---

## Execution Model

### Single Command Execution
Commands execute **independently**, NOT in batches. Each command execution must fit the budget:

```
Agent executes: implement(task_id="TASK-8-1")

Context loaded:
1. Command prompt: implement.md
2. Agent system prompt: .claude/commands/{agent}/README.md
3. Skills: External skills (if loaded)
────────────────────────────────────────────
= Agent Infrastructure (MUST be ≤ 480 lines / 30%)

PLUS work content:
4. Task specification: From database (≤320 lines per CFR-017)
5. Code context: Files being modified (~200-300 lines)
6. System prompts: Claude system instructions
────────────────────────────────────────────
= Total execution context (TARGET: <60% per Anthropic)
```

### Agent Lifecycle (CRITICAL)

**Rule**: Agent MUST terminate after command completes.

```python
# Correct: Agent exits after command
def main():
    result = execute_command("implement", task_id="TASK-8-1")
    save_result(result)
    sys.exit(0)  # ✅ Agent terminates

# Incorrect: Agent stays alive
def main():
    while True:  # ❌ Agent loops forever
        command = get_next_command()
        execute_command(command)
```

**Why**:
- Fresh context for each command
- No context accumulation
- Clean state per execution
- Predictable resource usage
- CFR-000 compliance (prevents conflicts)

### Why Per-Command, Not Per-Agent?

**Incorrect** (my previous assumption):
```
❌ Agent loads 3 commands at once: implement + test + finalize
❌ Budget: 3 × 120 = 360 lines (23%)
```

**Correct** (actual execution):
```
✅ Agent executes ONE command: implement()
✅ Budget: 120 (command) + 537 (agent README) + 0 (skills) = 657 lines (41%) ❌
```

Commands execute separately, so each execution must independently fit the budget.

---

## Budget Breakdown (30% Limit)

### Formula
```
command_lines + agent_readme_lines + skills_lines ≤ 480
```

### Current State (VIOLATES CFR-018)

| Agent | Command | Agent README | Skills | Total | Status |
|-------|---------|--------------|--------|-------|--------|
| code_reviewer | 120 | 537 | 0 | 657 (41%) | ❌ OVER |
| ux_design_expert | 120 | 253 | 0 | 373 (23%) | ✅ OK |
| user_listener | 120 | 188 | 0 | 308 (19%) | ✅ OK |
| assistant | 120 | 159 | 0 | 279 (17%) | ✅ OK |
| code_developer | 120 | ??? | 0 | ??? | ⚠️ UNKNOWN |
| project_manager | 120 | ??? | 0 | ??? | ⚠️ UNKNOWN |
| architect | 120 | ??? | 0 | ??? | ⚠️ UNKNOWN |
| orchestrator | 120 | ??? | 0 | ??? | ⚠️ UNKNOWN |

**Critical Issue**: code_reviewer agent README is 537 lines (34% budget), leaving NO room for command!

---

## Target Architecture

### Ideal Budget Distribution
```
Command prompt:       100-120 lines (6-7.5%)
Agent system prompt:  150-200 lines (9-12.5%)
Skills:               0 lines (embedded)
────────────────────────────────────────────
Total infrastructure: 250-320 lines (16-20%) ✅ Well under 30%
```

This leaves comfortable room for:
- Task spec: 320 lines (20%)
- Code context: 300 lines (19%)
- System prompts: 300 lines (19%)
- Other: 320 lines (20%)
- **Total**: ~1,560 lines (98% utilization, optimal)

---

## Enforcement

### 1. Agent Lifecycle Enforcement

```python
def execute_command_and_exit(command: str, **kwargs) -> None:
    """Execute command and terminate agent (CFR-018)."""
    try:
        # Load context (command + agent README)
        validate_command_context(command, agent_type)

        # Execute command
        result = run_command(command, **kwargs)

        # Save result
        save_to_database(result)

        # Log success
        logger.info(f"Command {command} completed successfully")

        # Exit cleanly
        sys.exit(0)  # ✅ Agent terminates after command

    except Exception as e:
        logger.error(f"Command {command} failed: {e}")
        sys.exit(1)  # Agent terminates on error

# NEVER do this:
# while True: execute_command()  # ❌ Violates CFR-018
```

### 2. Validation Before Command Execution

```python
def validate_command_context(command: str, agent_type: str) -> None:
    """Validate CFR-018: Command execution context budget."""

    # Load sizes
    command_lines = count_lines(f".claude/commands/v2/{agent_type}/{command}.md")
    agent_readme_lines = count_lines(f".claude/commands/agents/{agent_type}/README.md")
    skills_lines = 0  # Embedded skills, none external

    total_lines = command_lines + agent_readme_lines + skills_lines
    MAX_LINES = 480  # 30% of 1,600

    if total_lines > MAX_LINES:
        raise ContextBudgetViolationError(
            f"CFR-018 VIOLATION: {agent_type}.{command}() exceeds 30% budget\n"
            f"  Command: {command_lines} lines\n"
            f"  Agent README: {agent_readme_lines} lines\n"
            f"  Skills: {skills_lines} lines\n"
            f"  Total: {total_lines} lines ({total_lines/16:.0%})\n"
            f"  Max: {MAX_LINES} lines (30%)\n\n"
            f"Actions:\n"
            f"  1. Compress agent README to ≤200 lines\n"
            f"  2. Reduce command to ≤100 lines if needed\n"
            f"  3. Remove external skill dependencies"
        )

    if total_lines > 400:  # Warning at 25%
        logger.warning(
            f"CFR-018 WARNING: {agent_type}.{command}() using {total_lines} lines "
            f"({total_lines/16:.0%}). Consider compression."
        )
```

### 3. Pre-Commit Hook

```bash
#!/bin/bash
# Check all command + agent README combinations

for agent_dir in .claude/commands/agents/*/; do
    agent=$(basename "$agent_dir")
    agent_readme="$agent_dir/README.md"
    agent_lines=$(wc -l < "$agent_readme" | tr -d ' ')

    for cmd in .claude/commands/v2/$agent/*.md; do
        cmd_lines=$(wc -l < "$cmd" | tr -d ' ')
        total=$((agent_lines + cmd_lines))

        if [ "$total" -gt 480 ]; then
            echo "❌ CFR-018 VIOLATION: $agent/$(basename $cmd) = $total lines (max: 480)"
            exit 1
        fi
    done
done
```

---

## Implementation Strategy

### Agent-by-Agent Approach

**Work systematically through each agent**:

1. **Create/compress agent README** (150-200 lines max)
   - Agent purpose and role (20-30 lines)
   - Command list with 1-line descriptions (80-100 lines)
   - Key workflows (30-40 lines)
   - Database tables (20-30 lines)

2. **Revise each command** (120 lines each)
   - Move detailed command info FROM agent README TO command file
   - Embed essential skills directly in command
   - Validate: `README_lines + command_lines < 480` ✅

3. **Validate per-command budget**:
   ```python
   for each command:
       assert agent_readme_lines + command_lines < 480
   ```

### Move Details to Commands, Not Agent README

**Agent README**: High-level overview only
```markdown
# Code Reviewer Agent

## Purpose
Automated code quality analysis and review.

## Commands
- analyze: Comprehensive code review with quality score
- security: Deep security scan with Bandit
- fix: Auto-fix style issues
[...]

## Key Workflows
Review lifecycle: detect → analyze → report → notify

## Database
Tables: review_commit, review_code_review, review_issue
```

**Command Files**: Full implementation details
```markdown
# analyze

## Purpose
Run comprehensive code review: security, style, coverage, types, complexity.

[120 lines of detailed workflow, examples, error handling]
```

**Benefit**: Agent README stays small, commands have full detail needed for execution.

### Compression Techniques

1. **Remove redundancy**: Don't repeat command details in README and command files
2. **One-line command summaries**: In README, just purpose (not full workflow)
3. **Compress tables**: List table names only (no column details)
4. **Reference, don't duplicate**: "See CFR-017" instead of repeating CFR content
5. **Essential only**: If not needed during execution, don't include it

### Target Sizes

```
Agent README:        150-200 lines (9-12%)
Command prompt:      100-120 lines (6-7%)
Skills (embedded):   0 lines
────────────────────────────────────────
Per-command total:   250-320 lines (16-20%) ✅ Well under 30%
```

---

## Examples

### ✅ Good Example: assistant.docs()

```
Command: docs.md = 120 lines (7.5%)
Agent README: 159 lines (10%)
Skills: 0 lines
────────────────────────────────────
Total: 279 lines (17%) ✅ GOOD

Work context available:
- Remaining budget: 1,321 lines (83%)
- Can load large specs, code, examples
```

### ❌ Bad Example: code_reviewer.analyze()

```
Command: analyze.md = 120 lines (7.5%)
Agent README: 537 lines (34%) ❌ README ALONE EXCEEDS 30%!
Skills: 0 lines
────────────────────────────────────
Total: 657 lines (41%) ❌ OVER BUDGET

Work context constrained:
- Remaining budget: 943 lines (59%)
- Limits spec size, code context
- Violates CFR-018
```

**Fix**: Compress code_reviewer README to 200 lines
```
Command: analyze.md = 120 lines (7.5%)
Agent README: 200 lines (12.5%) ✅ COMPRESSED
Skills: 0 lines
────────────────────────────────────
Total: 320 lines (20%) ✅ COMPLIANT

Work context restored:
- Remaining budget: 1,280 lines (80%)
- Full spec + code + examples
```

---

## Related CFRs

- **CFR-007**: Agent Context Budget (30% for commands)
- **CFR-017**: Spec Size Limit (20% for specifications)

---

## FAQ

### Q: Why per-command, not per-agent?

**A**: Commands execute independently. Agent doesn't load all commands at once, only the one being executed.

### Q: What counts as "agent system prompt"?

**A**: The agent's README.md file that describes role, behavior, and available commands. Loaded every time agent executes any command.

### Q: Can I split agent README into multiple files?

**A**: Only if you DON'T load the extra files during command execution. The 30% limit applies to LOADED context only.

### Q: What if my agent legitimately needs more context?

**A**: Compress the agent README. 200 lines is enough for:
- Agent purpose (20 lines)
- Command summaries (120 lines)
- Workflows (40 lines)
- Database schema (20 lines)

Detailed command docs go in the command files themselves (120 lines each).

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2025-10-28 | Initial CFR creation |

---

**Last Updated**: 2025-10-28
**Status**: Active ✅
**Compliance Required**: All commands from 2025-10-28 onwards
