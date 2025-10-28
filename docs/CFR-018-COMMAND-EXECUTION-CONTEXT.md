# CFR-018: Command Execution Context Budget

**Status**: Active ✅
**Created**: 2025-10-28
**Updated**: 2025-10-28 (Token-based measurements)
**Owner**: All Agents
**Related**: CFR-007 (Context Budget), CFR-017 (Spec Size Limit)

---

## Requirement

**When executing a single command, the total agent infrastructure MUST be ≤60,000 tokens (30% of context budget).**

### Formula (Token-Based)
```
command_tokens + agent_readme_tokens + auto_skills_tokens < 60,000 tokens (30%)
```

Where:
- **command_tokens**: The specific command file (e.g., implement.md) in tokens
- **agent_readme_tokens**: Agent system prompt (README.md) in tokens
- **auto_skills_tokens**: Auto-loaded system skills (estimated ~2,000 tokens)
- **30%**: 60,000 tokens of 200,000 token Claude context

**Budget accounting (Token-based)**:
```
Command:      1,000-1,500 tokens (varies by command)
Agent README: 1,500-2,000 tokens (180 lines × ~10 tokens/line)
Auto-skills:  2,000 tokens (estimated)
────────────────────────────────────────────────────────
Total:        4,500-5,500 tokens (7-9% actual usage) ✅
```

**Reality**: Current commands use 7-9% of budget, leaving 91-93% for work content.

This leaves 140,000 tokens (70% of context) for actual work content: task specifications, code, and execution context.

---

## Why Tokens, Not Lines?

**Previous approach (lines)**: Inaccurate, over-conservative
- Lines vary from 10-200 characters
- No correlation to LLM token usage
- Thought we were using 26-30% budget
- Actually using 7-9% budget!

**Current approach (tokens)**: Accurate measurement
- Tokens are what Claude actually counts
- Direct measurement: ~4 characters per token
- Validated with `coffee_maker/utils/token_counter.py`
- See `TOKEN_VS_LINE_COUNTING_ANALYSIS.md` for full analysis

### Execution Constraint
**Agent MUST terminate (kill itself) after command completes.** No long-running agents, no command loops. Each command invocation = one agent lifecycle.

---

## Execution Model

### Single Command Execution
Commands execute **independently**, NOT in batches. Each command execution must fit the budget:

```
Agent executes: implement(task_id="TASK-8-1")

Context loaded:
1. Command prompt: implement.md (~1,100 tokens)
2. Agent README: .claude/commands/{agent}/README.md (~1,500 tokens)
3. Auto-skills: System-loaded skills (~2,000 tokens)
────────────────────────────────────────────
= Agent Infrastructure: ~4,600 tokens (7.7% of 60K budget) ✅

PLUS work content:
4. Task specification: From database (~6,000-8,000 tokens, CFR-017)
5. Code context: Files being modified (~4,000-6,000 tokens)
6. System prompts: Claude system instructions (~5,000-8,000 tokens)
────────────────────────────────────────────
= Total execution context: ~20,000-28,000 tokens (10-14% of 200K) ✅
```

**Actual measurements** (using token_counter.py):
- architect.design: 4,486 tokens (7.5%)
- code_developer.implement: 4,601 tokens (7.7%)
- code_reviewer.analyze: 4,228 tokens (7.0%)

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

**Incorrect** (previous assumption):
```
❌ Agent loads 3 commands at once: implement + test + finalize
❌ Budget: 3 × 1,200 = 3,600 tokens
```

**Correct** (actual execution):
```
✅ Agent executes ONE command: implement()
✅ Budget: 1,134 (command) + 1,467 (README) + 2,000 (skills) = 4,601 tokens (7.7%) ✅
```

Commands execute separately, so each execution must independently fit the budget.

---

## Budget Breakdown (60,000 Token Limit)

### Formula (Token-Based)
```
command_tokens + agent_readme_tokens + auto_skills_tokens ≤ 60,000
```

### Current State (ALL COMPLIANT ✅)

| Agent | README | Largest Command | Skills | Total | Status |
|-------|--------|-----------------|--------|-------|--------|
| architect | 1,861 | 696 (adr) | 2,000 | 4,557 (7.6%) | ✅ OK |
| code_developer | 1,467 | 1,300 (finalize) | 2,000 | 4,767 (7.9%) | ✅ OK |
| code_reviewer | 1,653 | 599 (security) | 2,000 | 4,252 (7.1%) | ✅ OK |
| project_manager | 1,840 | 722 (report) | 2,000 | 4,562 (7.6%) | ✅ OK |
| orchestrator | 1,789 | 594 (worktrees) | 2,000 | 4,383 (7.3%) | ✅ OK |
| ux_design_expert | 1,731 | 647 (review) | 2,000 | 4,378 (7.3%) | ✅ OK |
| user_listener | 1,523 | ~1,200 (interact) | 2,000 | 4,723 (7.9%) | ✅ OK |
| assistant | 1,289 | ~1,200 (demo) | 2,000 | 4,489 (7.5%) | ✅ OK |

**Measured with**: `coffee_maker/utils/token_counter.py`
**Average usage**: 7.5% of budget
**All agents**: Well under 30% limit ✅

---

## Target Architecture

### Actual Budget Distribution (Token-Based)
```
Command:          1,000-1,500 tokens (varies by complexity)
Agent README:     1,500-2,000 tokens (180 lines × ~10 tokens/line)
Auto-skills:      2,000 tokens (estimated)
────────────────────────────────────────────
Total infrastructure: 4,500-5,500 tokens (7-9%) ✅ Well under 30%
```

This leaves comfortable room for work content:
- Task spec: 6,000-8,000 tokens (~320 lines)
- Code context: 4,000-6,000 tokens
- System prompts: 5,000-8,000 tokens
- Available: ~175,000 tokens (87.5% of context!)
- **Total work**: ~20,000-30,000 tokens (10-15% of context)

---

## Enforcement

### 1. Token-Based Validation (Pre-Execution)

```python
from coffee_maker.utils.token_counter import validate_command_file

def validate_before_execution(agent_type: str, command_name: str) -> None:
    """Validate command context before execution (CFR-018)."""
    usage = validate_command_file(agent_type, command_name)

    if not usage.within_budget:
        raise ContextBudgetViolationError(
            f"CFR-018 VIOLATION: {agent_type}.{command_name} "
            f"exceeds budget: {usage.total_tokens:,} tokens "
            f"({usage.usage_percent:.1f}% of 60,000)\n"
            f"  Command: {usage.command_tokens:,}\n"
            f"  README: {usage.readme_tokens:,}\n"
            f"  Skills: {usage.skills_tokens:,}"
        )

    logger.info(f"✅ {agent_type}.{command_name}: {usage}")
```

### 2. Agent Lifecycle Enforcement

```python
def execute_command_and_exit(command: str, **kwargs) -> None:
    """Execute command and terminate agent (CFR-018)."""
    try:
        # Validate token budget
        validate_before_execution(agent_type, command)

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

### 3. Pre-Commit Hook (Token-Based)

```bash
#!/bin/bash
# Validate all command token budgets before commit

# Run token validator
poetry run python coffee_maker/utils/token_counter.py

if [ $? -ne 0 ]; then
    echo "❌ CFR-018 VIOLATION: One or more commands exceed token budget"
    echo "Run: poetry run python coffee_maker/utils/token_counter.py"
    exit 1
fi

echo "✅ All commands within token budget"
```

### 4. CLI Validation Tool

```bash
# Validate all commands
poetry run python coffee_maker/utils/token_counter.py

# Validate specific agent
poetry run python -c "
from coffee_maker.utils.token_counter import validate_all_commands, generate_budget_report
from pathlib import Path
results = validate_all_commands(Path('.claude/commands/agents'))
print(generate_budget_report(results, show_violations=True))
"
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

### Target Sizes (Token-Based)

```
Agent README:        1,500-2,000 tokens (~180 lines)
Command prompt:      1,000-1,500 tokens (~100-150 lines)
Skills (auto-load):  2,000 tokens (estimated)
────────────────────────────────────────
Per-command total:   4,500-5,500 tokens (7-9%) ✅ Well under 30%
```

---

## Examples (Token-Based Measurements)

### ✅ Excellent Example: code_reviewer.analyze()

```
Command: analyze.md = 575 tokens
Agent README: 1,653 tokens
Auto-skills: 2,000 tokens
────────────────────────────────────
Total: 4,228 tokens (7.0%) ✅ EXCELLENT

Work context available:
- Remaining budget: 195,772 tokens (97.9%)
- Can load large specs (8K tokens)
- Full code context (6K tokens)
- System prompts (8K tokens)
- Still 170K+ tokens free!
```

### ✅ Good Example: code_developer.implement()

```
Command: implement.md = 1,134 tokens
Agent README: 1,467 tokens
Auto-skills: 2,000 tokens
────────────────────────────────────
Total: 4,601 tokens (7.7%) ✅ GOOD

Work context available:
- Remaining budget: 195,399 tokens (97.7%)
- Comfortable room for all work content
```

###  Previous Bad Example (Line-Based): code_reviewer.analyze()

```
Line estimate (OLD): 657 lines (41% of 480) ❌ OVER!
Token reality (NEW): 4,228 tokens (7.0% of 60K) ✅ FINE!

Difference: Thought we were over budget by 37%,
            actually well under budget by 23%!
```

**Lesson**: Line counting was massively misleading. Token counting reveals truth.

---

## Runtime Token Reporting

### Agent Self-Reporting Requirement

**Agents MUST report their token usage at the beginning and end of each command execution.**

### At Command Start (Pre-Execution)

```python
def execute_command(agent_type: str, command_name: str, **kwargs):
    """Execute command with token tracking."""
    # 1. Estimate tokens
    usage = validate_command_file(agent_type, command_name)

    # 2. Report estimated usage
    logger.info(
        f"🚀 {agent_type}.{command_name} STARTING\n"
        f"   Estimated context: {usage.total_tokens:,} tokens ({usage.usage_percent:.1f}%)\n"
        f"   - Command: {usage.command_tokens:,}\n"
        f"   - README: {usage.readme_tokens:,}\n"
        f"   - Skills: {usage.skills_tokens:,}"
    )

    start_time = time.time()
    # ... execute command ...
```

### At Command End (Post-Execution)

```python
    # ... after execution ...

    # 3. Extract actual usage from API response
    actual_input = response.usage.input_tokens
    actual_output = response.usage.output_tokens
    duration = time.time() - start_time

    # 4. Report actual usage
    logger.info(
        f"✅ {agent_type}.{command_name} COMPLETED ({duration:.1f}s)\n"
        f"   Actual tokens:\n"
        f"   - Input:  {actual_input:,} (estimate: {usage.total_tokens:,}, "
        f"accuracy: {usage.total_tokens/actual_input*100:.1f}%)\n"
        f"   - Output: {actual_output:,}\n"
        f"   - Total:  {actual_input + actual_output:,}\n"
        f"   Context used: {(actual_input + actual_output)/200000*100:.1f}% of 200K"
    )

    # 5. Store in database for analysis
    store_token_usage(
        agent_type=agent_type,
        command_name=command_name,
        estimated_input=usage.total_tokens,
        actual_input=actual_input,
        actual_output=actual_output,
        duration=duration
    )
```

### Example Output

```
🚀 code_developer.implement STARTING
   Estimated context: 4,601 tokens (7.7%)
   - Command: 1,134
   - README: 1,467
   - Skills: 2,000

... execution ...

✅ code_developer.implement COMPLETED (23.4s)
   Actual tokens:
   - Input:  4,823 (estimate: 4,601, accuracy: 95.4%)
   - Output: 2,156
   - Total:  6,979
   Context used: 3.5% of 200K
```

### Benefits

1. **Visibility**: See actual token usage in real-time
2. **Validation**: Verify estimates against reality
3. **Optimization**: Identify commands that need compression
4. **Trending**: Track token usage over time
5. **Debugging**: Spot context bloat early

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
