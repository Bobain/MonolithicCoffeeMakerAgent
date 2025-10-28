---
command: code-developer-workflow
workflow: work
agent: code_developer
purpose: Complete autonomous development workflow
tables: [specs_task, implementation_file, test_execution, quality_check]
tools: [file_system, git, pytest, black, mypy]
duration: 30-120m
---

## Purpose

Execute complete development workflow for a task: load specification → generate code → run tests → quality checks → commit changes. This is the PRIMARY workflow command for the code_developer agent, replacing 6 individual commands with one intelligent workflow.

## Workflow Overview

```
work(task_id) → Load → Code → Test → Quality → Commit → WorkResult
```

**Key Features**:
- **5 execution modes**: AUTO (full workflow), STEP (interactive), TEST_ONLY, COMMIT_ONLY, CODE_ONLY
- **Smart test auto-retry**: Automatically retries tests up to 3 times on failure
- **Auto-generated commits**: Creates conventional commit messages from changes
- **Graceful degradation**: Non-critical failures don't block completion
- **Rich result tracking**: Comprehensive WorkResult object with all metadata

## Input Parameters

```yaml
TASK_ID:
  type: string
  required: true
  description: Task identifier to implement
  example: "TASK-1"

MODE:
  type: string
  default: "auto"
  enum: [auto, step, test-only, commit-only, code-only]
  description: |
    - auto: Full autonomous workflow
    - step: Interactive step-by-step
    - test-only: Run tests only
    - commit-only: Commit existing changes
    - code-only: Generate code without testing

SKIP_TESTS:
  type: boolean
  default: false
  description: Skip test execution (for rapid prototyping)

SKIP_QUALITY:
  type: boolean
  default: false
  description: Skip quality checks (Black, MyPy)

AUTO_COMMIT:
  type: boolean
  default: true
  description: Automatically commit on success

COMMIT_MESSAGE:
  type: string
  optional: true
  description: Custom commit message (otherwise auto-generated)

VERBOSE:
  type: boolean
  default: false
  description: Enable detailed logging
```

## Workflow Execution

### AUTO Mode (Default)

Complete autonomous workflow:

```python
1. Load task specification from database
2. Analyze complexity and determine approach
3. Generate code implementation
4. Run test suite (with auto-retry up to 3 times)
5. Run quality checks (Black, MyPy, type hints)
6. Auto-generate commit message
7. Create git commit
8. Return comprehensive WorkResult
```

### STEP Mode

Interactive step-by-step with user confirmations:

```python
1. Load task → [User confirms]
2. Generate code → [User reviews]
3. Run tests → [User confirms]
4. Quality checks → [User confirms]
5. Commit → [User confirms]
```

### Specialized Modes

- **TEST_ONLY**: Skip code generation, run tests on existing changes
- **COMMIT_ONLY**: Skip all work, commit existing staged changes
- **CODE_ONLY**: Generate code without tests or quality checks (fast iteration)

## Result Object

```python
@dataclass
class WorkResult:
    status: WorkStatus  # SUCCESS, PARTIAL, FAILED
    task_id: str
    steps_completed: List[str]  # ["load", "code", "test", "quality", "commit"]
    steps_failed: List[str]  # Failed steps
    files_changed: List[str]  # Files modified
    tests_run: int  # Total tests executed
    tests_passed: int  # Tests that passed
    commit_sha: Optional[str]  # Git commit SHA
    duration_seconds: float  # Total execution time
    error_message: Optional[str]  # Error details if failed
    metadata: Dict[str, Any]  # Additional context
```

### WorkStatus Enum

```python
class WorkStatus(Enum):
    SUCCESS = "success"    # All steps completed
    PARTIAL = "partial"    # Some steps completed, some failed
    FAILED = "failed"      # Critical failure, nothing completed
```

## Success Criteria

### Full Success (STATUS = SUCCESS)

- ✅ Task specification loaded
- ✅ Code generated and files written
- ✅ All tests passing
- ✅ Quality checks passed
- ✅ Git commit created

### Partial Success (STATUS = PARTIAL)

- ✅ Task loaded and code generated
- ⚠️ Tests failing OR quality checks failing
- ⚠️ Commit skipped or failed
- **Action**: Review failures in `steps_failed` list

### Failure (STATUS = FAILED)

- ❌ Critical error in workflow execution
- ❌ Task not found or invalid
- ❌ Code generation failed
- **Action**: Check `error_message` for details

## Database Operations

### Query: Load Task Specification

```sql
SELECT
    st.task_id,
    st.spec_id,
    st.description,
    st.assigned_to,
    st.status,
    st.complexity_score,
    st.metadata
FROM specs_task st
WHERE st.task_id = ?
```

### Insert: Track File Changes

```sql
INSERT INTO implementation_file (
    file_id, task_id, file_path, operation, lines_added, lines_removed, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Record Test Execution

```sql
INSERT INTO test_execution (
    execution_id, task_id, test_command, total_tests, passed, failed,
    skipped, duration_seconds, output, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
```

### Insert: Quality Check Results

```sql
INSERT INTO quality_check (
    check_id, task_id, check_type, status, issues_found, output, created_at
) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
```

## Smart Features

### Auto-Retry on Test Failure

```python
# Automatically retry tests up to 3 times
attempt = 1
while attempt <= 3:
    result = run_tests()
    if result.passed == result.total:
        break
    if attempt < 3:
        logger.info(f"Tests failed, retrying ({attempt}/3)")
    attempt += 1
```

### Auto-Generated Commit Messages

```python
# Analyzes changes and generates conventional commit message
def generate_commit_message(files_changed, spec_description):
    # Determines commit type: feat, fix, refactor, test, docs
    # Generates concise message with scope
    # Example: "feat(auth): Implement JWT token validation"
```

### Graceful Degradation

```python
# Non-critical failures don't stop workflow
try:
    quality_result = run_quality_checks()
    result.steps_completed.append("quality")
except Exception as e:
    result.steps_failed.append("quality")
    logger.warning(f"Quality checks failed: {e}")
    # Workflow continues to commit step
```

## Error Handling

| Error | Cause | Recovery | Status |
|-------|-------|----------|--------|
| Task not found | Invalid TASK_ID | Verify task exists in database | FAILED |
| Spec load failed | Database error | Check database connectivity | FAILED |
| Code gen failed | Invalid spec or file write error | Review spec, check file permissions | FAILED |
| Tests failed (3x) | Code errors or test failures | Review test output, fix code | PARTIAL |
| Quality check failed | Style/type violations | Run Black/MyPy manually | PARTIAL |
| Commit failed | Git error or no changes | Check git status, stage changes | PARTIAL |

## Examples

### Example 1: Full AUTO Workflow

```bash
# Execute complete autonomous workflow
workflow.work(task_id="TASK-42")
```

**Result**:
```python
WorkResult(
    status=WorkStatus.SUCCESS,
    task_id="TASK-42",
    steps_completed=["load", "code", "test", "quality", "commit"],
    steps_failed=[],
    files_changed=["coffee_maker/auth/jwt_validator.py", "tests/unit/test_jwt_validator.py"],
    tests_run=15,
    tests_passed=15,
    commit_sha="abc123def456",
    duration_seconds=45.3,
    error_message=None,
    metadata={"spec_id": "SPEC-100", "complexity": "medium"}
)
```

### Example 2: STEP Mode (Interactive)

```bash
# Interactive mode with confirmations
workflow.work(task_id="TASK-43", mode="step")
```

**Execution**:
```
✓ Task loaded: SPEC-100 - Implement JWT validation
Continue with code generation? [Y/n]: y

✓ Code generated: 2 files changed
Review changes? [Y/n]: y

✓ Tests run: 15 passed / 15 total
Continue with quality checks? [Y/n]: y

✓ Quality checks passed
Commit changes? [Y/n]: y

✓ Committed: abc123def
```

### Example 3: TEST_ONLY Mode

```bash
# Run tests on existing code changes
workflow.work(task_id="TASK-44", mode="test-only")
```

**Result**:
```python
WorkResult(
    status=WorkStatus.PARTIAL,
    task_id="TASK-44",
    steps_completed=["test"],
    steps_failed=[],
    files_changed=[],  # No new files changed
    tests_run=20,
    tests_passed=18,
    commit_sha=None,
    duration_seconds=5.2,
    metadata={"failed_tests": ["test_edge_case_1", "test_edge_case_2"]}
)
```

### Example 4: Skip Tests (Rapid Prototyping)

```bash
# Generate code quickly without testing
workflow.work(task_id="TASK-45", skip_tests=True, auto_commit=False)
```

**Result**:
```python
WorkResult(
    status=WorkStatus.SUCCESS,
    task_id="TASK-45",
    steps_completed=["load", "code"],
    steps_failed=[],
    files_changed=["coffee_maker/prototype.py"],
    tests_run=0,
    tests_passed=0,
    commit_sha=None,
    duration_seconds=8.1,
    metadata={"skipped": ["test", "quality", "commit"]}
)
```

### Example 5: Partial Success (Tests Failing)

```bash
# Tests fail after 3 retries
workflow.work(task_id="TASK-46")
```

**Result**:
```python
WorkResult(
    status=WorkStatus.PARTIAL,
    task_id="TASK-46",
    steps_completed=["load", "code"],
    steps_failed=["test"],
    files_changed=["coffee_maker/feature.py"],
    tests_run=10,
    tests_passed=8,
    commit_sha=None,
    error_message="Tests failed after 3 attempts: 2 failures",
    duration_seconds=30.5,
    metadata={"retry_count": 3, "failed_tests": ["test_edge_case", "test_validation"]}
)
```

## Implementation Notes

### Task Loading

```python
# Load from database with comprehensive spec
task_data = self.commands.implement(
    action="load_task",
    task_id=task_id
)

# Extracts:
# - spec_id: Link to technical specification
# - description: What to implement
# - complexity_score: Estimated complexity (1-10)
# - dependencies: Other tasks that must complete first
# - metadata: Additional context (files, patterns, etc.)
```

### Code Generation

```python
# Generate code using consolidated commands
code_result = self.commands.implement(
    action="write_code",
    task_id=task_id,
    spec_data=spec_data
)

# Tracks:
# - files_changed: List of modified file paths
# - lines_added: Total lines added
# - lines_removed: Total lines removed
# - operation: create | update | delete
```

### Test Execution

```python
# Run pytest with comprehensive tracking
test_result = self.commands.test(
    action="run_suite",
    task_id=task_id
)

# Returns:
# - total: Total test count
# - passed: Tests that passed
# - failed: Tests that failed
# - skipped: Skipped tests
# - duration: Test execution time
# - output: Full pytest output
```

### Quality Checks

```python
# Run Black, MyPy, type hint validation
quality_result = self.commands.quality(
    action="check_all",
    task_id=task_id
)

# Checks:
# - Black formatting (autofix enabled)
# - MyPy type checking
# - Type hint coverage (100% required)
# - Line length (120 chars max)
```

### Git Operations

```python
# Auto-generate conventional commit message
commit_message = self._generate_commit_message(
    files_changed=result.files_changed,
    task_description=task_data["description"]
)

# Commit with standard footer
commit_result = self.commands.git(
    action="commit",
    message=commit_message,
    files=result.files_changed
)

# Returns commit SHA
```

## Integration with Other Workflows

### → Architect (spec creation)

```python
# Architect creates spec, developer implements it
architect.spec(priority_id="PRIORITY-5")  # Creates SPEC-100
developer.work(task_id="TASK-42")  # Implements SPEC-100
```

### → Code Reviewer (post-commit review)

```python
# Developer commits, reviewer checks quality
result = developer.work(task_id="TASK-42")
if result.status == WorkStatus.SUCCESS:
    reviewer.review(target=result.commit_sha, scope="full")
```

### → Project Manager (progress tracking)

```python
# Project manager tracks workflow completion
result = developer.work(task_id="TASK-42")
project_manager.manage(
    action="track",
    priority_id="PRIORITY-5",
    updates={"task_status": result.status}
)
```

## Performance Expectations

| Mode | Duration | Files Changed | Tests Run |
|------|----------|---------------|-----------|
| AUTO (simple) | 15-30m | 1-3 files | 5-20 tests |
| AUTO (medium) | 30-60m | 3-8 files | 20-50 tests |
| AUTO (complex) | 60-120m | 8-15 files | 50-100 tests |
| STEP | Varies | Varies | Varies |
| TEST_ONLY | 1-10m | 0 files | 5-100 tests |
| CODE_ONLY | 5-15m | 1-8 files | 0 tests |

## Best Practices

1. **Use AUTO mode** for routine tasks (80% of work)
2. **Use STEP mode** for complex/risky changes requiring review
3. **Use TEST_ONLY** after manual code edits
4. **Use CODE_ONLY** for rapid prototyping, then run TEST_ONLY
5. **Use skip_tests=True** sparingly, always test before committing to main
6. **Check WorkResult.status** and handle PARTIAL appropriately
7. **Review WorkResult.metadata** for additional context on failures
8. **Enable verbose=True** for debugging workflow issues

## Related Commands

- `architect.spec()` - Create technical specification before implementation
- `reviewer.review()` - Review code quality after commit
- `project_manager.manage()` - Track progress and send notifications
- `orchestrator.coordinate()` - Manage parallel task execution across agents

---

**Workflow Reduction**: This single `work()` command replaces:
1. `load_task()`
2. `write_code()`
3. `run_tests()`
4. `check_quality()`
5. `commit_changes()`
6. `update_status()`

**Context Savings**: ~400 lines vs ~2,500 lines (6 commands)
