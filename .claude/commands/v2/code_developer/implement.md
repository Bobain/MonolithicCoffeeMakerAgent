# implement

## Purpose
Implement task from technical specification: load spec (CFR-017 validated), generate/modify code files, integrate with git workflow, track all changes.

## Parameters
```yaml
task_id: str  # Required, format: TASK-N-M
auto_test: bool = true  # Run tests after implementation
auto_commit: bool = false  # Create git commit
verbose: bool = false  # Detailed logging
```

## Workflow
1. Load task from specs_task table (JOIN technical_spec)
2. Validate spec size ≤320 lines (CFR-017 enforcement)
3. Analyze requirements and complexity
4. Generate or modify code files
5. Stage changes with git (if auto_commit or manual prep)
6. Run tests if auto_test=true
7. Generate conventional commit message
8. Create commit if auto_commit=true
9. Track implementation in database
10. Return ImplementResult

## Git Integration (EMBEDDED - Essential Workflow)

### Stage Files
```bash
# Stage specific files
git add {file1} {file2} {file3}

# Stage all changes (use with caution)
git add .

# Check what will be committed
git diff --cached --name-only
```

### Generate Conventional Commit Message
**Format**: `{type}({scope}): {description}`

**Commit Types**:
- `feat`: New feature or capability
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `test`: Test additions or fixes
- `docs`: Documentation only
- `chore`: Build/tooling changes

**Scope**: Module or component (e.g., `auth`, `database`, `api`)

**Message Template**:
```bash
git commit -m "$(cat <<'EOF'
{type}({scope}): {One-line description}

{Optional: Multi-line detailed explanation of changes}

{Optional: Breaking changes, migration notes}

Implements: {task_id}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Example Commit Messages**:
```
feat(auth): Implement OAuth2 authentication flow

- Add OAuth2Provider model
- Create token exchange endpoint
- Implement session management

Implements: TASK-8-1

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Verify Commit
```bash
# Check commit was created
git status

# View last commit
git log -1 --oneline

# View commit details
git show HEAD --stat
```

### CFR-013 Compliance
- Always work on `roadmap` branch (or `roadmap-implementation_task-*` worktree branch)
- NEVER create feature branches
- Orchestrator manages worktree isolation

## Database Operations
```sql
-- Load task with spec
SELECT st.task_id, st.spec_id, st.description,
       ts.content, ts.complexity_score, ts.dependencies,
       LENGTH(ts.content) / 20 as spec_lines
FROM specs_task st
JOIN technical_spec ts ON st.spec_id = ts.spec_id
WHERE st.task_id = ?

-- Validate CFR-017
-- If spec_lines > 320, RAISE ERROR

-- Track implementation
INSERT INTO implementation_log (
    log_id, task_id, files_changed, lines_added,
    lines_deleted, commit_sha, status, timestamp
) VALUES (?, ?, ?, ?, ?, ?, 'completed', datetime('now'))

-- Update task status
UPDATE specs_task
SET status = 'completed', completed_at = datetime('now')
WHERE task_id = ?
```

## Result Object
```python
@dataclass
class ImplementResult:
    task_id: str
    spec_id: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    tests_passed: bool
    commit_created: bool
    commit_sha: str  # None if not committed
    status: str  # "success" | "partial" | "failed"
```

## Error Handling
| Error | Cause | Action |
|-------|-------|--------|
| TaskNotFound | Invalid task_id | Verify task exists in database |
| SpecTooLarge | Spec >320 lines (CFR-017) | Notify architect to compress spec |
| SpecNotFound | Missing technical_spec | Notify architect to create spec |
| TestsFailed | Tests broken | Fix implementation before commit |
| GitError | Commit/stage failed | Check git status, resolve conflicts |
| CodeGenError | Unable to generate code | Review spec clarity, request architect help |

## Example
```python
result = implement(
    task_id="TASK-8-1",
    auto_test=True,
    auto_commit=True
)
# ImplementResult(
#   task_id="TASK-8-1",
#   spec_id="SPEC-042",
#   files_changed=["coffee_maker/auth/oauth2.py", "tests/test_oauth2.py"],
#   lines_added=245,
#   lines_deleted=12,
#   tests_passed=True,
#   commit_created=True,
#   commit_sha="abc123def",
#   status="success"
# )
```

## Related Commands
- test() - Run tests with coverage
- finalize() - Quality checks and final commit

---
Estimated: 120 lines | Context: 7.5% | Self-contained: Yes ✅
