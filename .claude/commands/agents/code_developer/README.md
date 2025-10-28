# Code Developer Agent

**Role**: Autonomous implementation from ROADMAP
**Interaction**: Backend only (no UI)
**Owner**: code_developer
**CFR Compliance**: CFR-001, CFR-008, CFR-013, CFR-017, CFR-018

---

## Purpose

The code_developer agent is responsible for autonomous implementation of tasks from technical specifications. It:

- Loads tasks from the database with linked specifications (≤320 lines per CFR-017)
- Generates or modifies code files based on spec requirements
- Integrates with Git workflow (conventional commits, CFR-013 compliance)
- Runs automated tests with coverage tracking (≥90% target)
- Performs quality checks (Black formatting, MyPy type checking)
- Tracks all implementation metrics in database

**Key Principle**: Autonomous execution. Code developer works independently from specs without human intervention during implementation.

**Lifecycle**: Agent executes ONE command, then terminates (CFR-018). No long-running processes.

---

## Commands (3)

### implement
Implement task from technical specification: load spec (CFR-017 validated), generate/modify code, integrate with git workflow, track changes.
- **Input**: task_id (TASK-N-M format)
- **Output**: Files changed, lines added/deleted, tests passed, commit SHA
- **Duration**: 5-30 minutes depending on complexity
- **Budget**: 120 lines + 180 (this README) = 300 lines (19%) ✅

### test
Run pytest with coverage, auto-retry failed tests up to 3 times, record metrics, ensure ≥90% coverage.
- **Input**: target path (file/directory/all)
- **Output**: Tests run/passed/failed, coverage %, retry attempts
- **Duration**: 1-5 minutes depending on test suite size
- **Budget**: 120 lines + 180 (this README) = 300 lines (19%) ✅

### finalize
Run quality checks (Black, MyPy), generate conventional commit message, create git commit with 🤖 footer, verify all checks pass.
- **Input**: task_id
- **Output**: Black passed, MyPy passed, commit created, commit SHA
- **Duration**: 1-3 minutes
- **Budget**: 120 lines + 180 (this README) = 300 lines (19%) ✅

---

## Key Workflows

### Implementation Workflow
```
1. implement(task_id) → Load spec, generate code, stage files
2. test(target) → Run pytest, validate coverage ≥90%
3. finalize(task_id) → Quality checks, commit with conventional message
```

**Autonomous Loop** (orchestrator-managed):
```
while tasks_available:
    task = get_next_task()
    implement(task.id)  # Agent spawns, executes, exits
    test(".")           # Agent spawns, executes, exits
    finalize(task.id)   # Agent spawns, executes, exits
```

### Git Integration (CFR-013)
- **Branch**: Always work on `roadmap` branch (or `roadmap-implementation_task-*` worktree)
- **Commits**: Conventional format with 🤖 footer and Co-Authored-By line
- **No feature branches**: Orchestrator manages worktree isolation

### Quality Standards
- **Code style**: Black formatting (120 char line length)
- **Type checking**: MyPy strict mode
- **Test coverage**: ≥90% required
- **Commit format**: Conventional commits (feat/fix/refactor/test/docs/chore)

---

## Database Tables

### Primary Tables
- **specs_task**: Task definitions with linked specifications
- **technical_spec**: Specifications (≤320 lines per CFR-017)
- **implementation_log**: Tracks files changed, lines added/deleted, commit SHA

### Metrics Tables
- **test_execution_log**: Test runs, pass/fail counts, coverage percentages
- **coverage_history**: Coverage trends over time
- **finalization_log**: Quality check results (Black, MyPy), commit status

### Query Patterns
```sql
-- Load task with spec (implement command)
SELECT st.task_id, ts.content, LENGTH(ts.content)/20 as spec_lines
FROM specs_task st
JOIN technical_spec ts ON st.spec_id = ts.spec_id
WHERE st.task_id = ? AND ts.content IS NOT NULL

-- Validate CFR-017
-- Raise error if spec_lines > 320
```

---

## Error Handling

### Common Errors
- **SpecTooLarge**: Spec >320 lines (CFR-017 violation) → Notify architect
- **TestsFailed**: Tests broken → Fix implementation, retry
- **BlackFailed**: Formatting issues → Auto-fix with `black .`
- **MyPyFailed**: Type errors → Manual fixes required
- **GitError**: Commit/stage failed → Resolve conflicts

### Recovery Strategy
1. Save error state to database
2. Notify orchestrator/project_manager
3. Log detailed error information
4. Exit cleanly (sys.exit(1))

---

## CFR Compliance

### CFR-001: Document Ownership
Owns: `.claude/**`, `coffee_maker/**`, `tests/**`, `scripts/**`

### CFR-008: Architect Creates Specs
NEVER creates specs. Only implements from architect-created specs.

### CFR-013: Roadmap Branch Only
Always works on `roadmap` branch or orchestrator-managed worktree branches.

### CFR-017: Spec Size Limit
Validates specs ≤320 lines before implementation. Rejects oversized specs.

### CFR-018: Command Execution Context
Each command execution: `command (120) + README (180) = 300 lines (19%)` ✅

---

## Context Budget Validation

```
Per-command execution:
- Command prompt: 120 lines (7.5%)
- Agent README (this file): 180 lines (11%)
- Skills: 0 lines (all embedded)
────────────────────────────────────────────
Infrastructure: 300 lines (19%) ✅ Under 30%

Work context:
- Task spec: 320 lines (20%, CFR-017)
- Code context: 200 lines (13%)
- System prompts: 300 lines (19%)
────────────────────────────────────────────
Total execution: 1,120 lines (70%) ✅ Under 80%
```

**Validation**: All 3 commands comply with CFR-018 (< 30% infrastructure budget).

---

## Practical Examples

### Example: Loading Task with Spec
```python
# How to load task from database
import sqlite3

conn = sqlite3.connect("data/development.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT
        st.task_id,
        st.title,
        st.estimated_hours,
        ts.content as spec_content,
        ts.spec_id
    FROM specs_task st
    JOIN technical_spec ts ON st.spec_id = ts.spec_id
    WHERE st.task_id = ? AND st.status = 'todo'
""", (task_id,))

task = cursor.fetchone()
if not task:
    raise TaskNotFoundError(f"Task {task_id} not found or not in 'todo' status")

# Validate CFR-017: spec must be ≤40,000 tokens
from coffee_maker.utils.token_counter import estimate_tokens_from_text
spec_tokens = estimate_tokens_from_text(task['spec_content'])
if spec_tokens > 40_000:
    raise SpecTooLargeError(f"Spec has {spec_tokens:,} tokens (max: 40,000)")
```

### Example: Implementation Pattern (Keep-Alive)
```python
# code_developer now uses keep-alive optimization
def _do_background_work(self):
    """Process multiple priorities in one session if context < 50%."""

    # Track tokens across tasks
    cumulative_input_tokens = 0
    tasks_in_session = 0

    while True:
        # Get next task
        task = get_next_task()
        if not task:
            break

        # Implement task
        success, input_tokens, output_tokens = implement_task(task)

        # Track usage
        cumulative_input_tokens += input_tokens
        tasks_in_session += 1

        # Check if we should continue
        if cumulative_input_tokens >= 100_000:  # 50% of 200K
            logger.info(f"Context limit reached - ending session after {tasks_in_session} tasks")
            break

        logger.info(f"♻️ Keep-alive: Continuing to next task (saves ~4K tokens)")
```

### Example: Test Execution with Coverage
```python
# Run tests with coverage tracking
import subprocess

result = subprocess.run(
    ["pytest", "tests/unit/", "--cov=coffee_maker", "--cov-report=term"],
    capture_output=True,
    text=True,
    timeout=300
)

# Parse coverage from output
import re
coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", result.stdout)
if coverage_match:
    coverage_pct = int(coverage_match.group(1))

    if coverage_pct < 90:
        logger.warning(f"⚠️ Coverage {coverage_pct}% < 90% target")
    else:
        logger.info(f"✅ Coverage {coverage_pct}% ≥ 90% target")
```

### Example: Conventional Commit Format
```bash
# Format that code_developer uses for commits
git commit -m "$(cat <<'EOF'
feat: Implement agent keep-alive optimization

Agents now process multiple tasks in one session if context < 50%.
Saves ~4,000 tokens per task by not respawning.

- Added cumulative token tracking
- Modified background work loop
- Added session summary logging

Fixes: #123
Implements: TASK-104-2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Integration Points

### With architect
- Loads specs via `specs_task.spec_id` join to `technical_spec`
- Validates CFR-017: spec ≤40,000 tokens before implementation
- Notifies architect if spec too large

### With project_manager
- Updates task status: `todo` → `in_progress` → `completed`
- Reports metrics: files changed, lines added/deleted, coverage %
- Sends `task_complete` message when done

### With database
```sql
-- Update task status during implementation
UPDATE specs_task
SET status = 'in_progress',
    started_at = CURRENT_TIMESTAMP,
    assigned_agent = 'code_developer'
WHERE task_id = ?;

-- Record implementation metrics
INSERT INTO implementation_log (
    task_id, files_changed, lines_added, lines_deleted,
    commit_sha, coverage_pct, duration_seconds
) VALUES (?, ?, ?, ?, ?, ?, ?);

-- Mark task complete
UPDATE specs_task
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE task_id = ?;
```

---

## Related Documents

- **Specs**: See `docs/architecture/specs/` for technical specifications
- **Workflows**: See `docs/WORKFLOWS.md` for detailed implementation workflows
- **CFRs**: See `docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md`
- **Agent Ownership**: See `docs/AGENT_OWNERSHIP.md`
- **CFR-017**: Token-based spec size limits

---

**Version**: 1.1.0
**Last Updated**: 2025-10-28
**Tokens**: ~1,700 (estimated with enhancements)
