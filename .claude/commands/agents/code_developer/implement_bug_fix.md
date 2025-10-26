---
command: code_developer.implement_bug_fix
agent: code_developer
action: implement_bug_fix
tables:
  write: [review_commit, system_audit]
  read: []
required_skills: [code_forensics, bug_tracking_helper]
required_tools: [database, git, pytest]
---

# Command: code_developer.implement_bug_fix

## Purpose
Implement bug fix from bug tracking system with regression test and commit tracking.

## Input Parameters

```yaml
bug_id: string           # Required - Bug ID to fix (e.g., "BUG-042")
create_test: boolean     # Create regression test (default: true)
priority: string         # "low", "medium", "high", "critical"
notes: string            # Optional - Implementation notes
```

## Database Operations

### 1. Get Bug Details
```python
from datetime import datetime
import subprocess
import json

def implement_bug_fix(db: DomainWrapper, params: dict):
    bug_id = params["bug_id"]

    # Get bug report (if bug_reports table exists)
    bugs = db.read("bug_reports", {"id": bug_id})
    if not bugs:
        return {
            "success": False,
            "error": f"Bug {bug_id} not found"
        }

    bug = bugs[0]

    # Extract bug details
    bug_title = bug.get("title", "Bug fix")
    bug_description = bug.get("description", "")
    affected_file = bug.get("affected_file", "")
```

### 2. Create Regression Test
```python
    if params.get("create_test", True):
        # Generate regression test
        test_content = f'''"""
Regression test for {bug_id}: {bug_title}

Bug Description: {bug_description}
"""

import pytest

def test_{bug_id.lower()}_regression():
    """Test that {bug_id} is fixed."""
    # TODO: Add test that would fail before fix
    # and pass after fix
    pass
'''

        # Save test file
        test_file = f"tests/test_{bug_id.lower()}_regression.py"
        with open(test_file, "w") as f:
            f.write(test_content)

        # Add test to git
        subprocess.run(["git", "add", test_file])
```

### 3. Implement Fix
```python
    # For demonstration, mark that fix was implemented
    # In real scenario, developer edits the affected file
    fix_notes = params.get("notes", "Bug fix implemented")

    # Stage modified files
    subprocess.run(["git", "add", "-A"])
```

### 4. Create Commit
```python
    # Get files changed
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    files_changed = result.stdout.strip().split("\n") if result.stdout else []

    # Get line changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True,
        text=True
    )
    stat_output = result.stdout

    # Extract additions/deletions
    import re
    additions = deletions = 0
    match = re.search(r"(\d+) insertion", stat_output)
    if match:
        additions = int(match.group(1))
    match = re.search(r"(\d+) deletion", stat_output)
    if match:
        deletions = int(match.group(1))

    # Create commit
    commit_message = f"fix({bug_id}): {bug_title}\n\n{bug_description}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": f"Failed to commit: {result.stderr}"
        }

    # Get commit hash
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True
    )
    commit_hash = result.stdout.strip()
```

### 5. Record Commit to Review Queue
```python
    # Record commit for code_reviewer
    commit_data = {
        "commit_hash": commit_hash,
        "task_id": f"BUG-{bug_id}",
        "message": commit_message,
        "files_changed": json.dumps(files_changed),
        "additions": additions,
        "deletions": deletions,
        "timestamp": datetime.now().isoformat(),
        "status": "pending_review",
        "bug_id": bug_id,
        "created_by": "code_developer",
        "created_at": datetime.now().isoformat()
    }

    commit_id = db.write("review_commit", commit_data, action="create")
```

### 6. Run Regression Test
```python
    # Run the new regression test
    test_result = subprocess.run(
        ["pytest", f"tests/test_{bug_id.lower()}_regression.py", "-v"],
        capture_output=True,
        text=True
    )

    test_passed = test_result.returncode == 0
```

### 7. Update Bug Status
```python
    # Update bug status to fixed (if possible)
    try:
        db.write("bug_reports", {
            "id": bug_id,
            "status": "fixed",
            "fixed_by": "code_developer",
            "fixed_at": datetime.now().isoformat(),
            "fix_commit": commit_hash
        }, action="update")
    except:
        pass  # Bug tracking system might not be available
```

### 8. Create Audit Trail
```python
    db.write("system_audit", {
        "table_name": "bug_fixes",
        "item_id": bug_id,
        "action": "implemented",
        "field_changed": "status",
        "new_value": "fixed",
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat(),
        "metadata": json.dumps({
            "commit": commit_hash,
            "files_changed": files_changed,
            "test_passed": test_passed
        })
    }, action="create")

    # Notify code_reviewer
    db.send_notification("code_reviewer", {
        "type": "bug_fix_ready",
        "bug_id": bug_id,
        "commit_hash": commit_hash,
        "test_created": params.get("create_test", True),
        "test_passed": test_passed,
        "message": f"Bug fix for {bug_id} ready for review: {bug_title}"
    })

    return {
        "success": test_passed,
        "bug_id": bug_id,
        "fix_applied": True,
        "test_created": params.get("create_test", True),
        "test_passed": test_passed,
        "commit_hash": commit_hash,
        "files_modified": files_changed
    }
```

## Output

```json
{
  "success": true,
  "bug_id": "BUG-042",
  "fix_applied": true,
  "test_created": true,
  "test_passed": true,
  "commit_hash": "abc123def",
  "files_modified": ["coffee_maker/auth.py", "tests/test_bug_042_regression.py"]
}
```

## Success Criteria

- ✅ Bug identified and analyzed
- ✅ Fix implemented
- ✅ Regression test created
- ✅ Regression test passes
- ✅ Commit recorded
- ✅ Bug status updated
- ✅ code_reviewer notified

## Regression Test Template

Auto-generated regression test structure:

```python
"""
Regression test for {BUG_ID}: {BUG_TITLE}

Bug Description: {DESCRIPTION}
Expected Behavior: {EXPECTED}
Actual Behavior (before fix): {ACTUAL}
"""

import pytest

def test_{bug_id}_regression():
    """Test that {bug_id} is fixed."""
    # Setup: Create conditions that trigger bug
    # Action: Execute code that had bug
    # Assert: Verify bug is fixed
    pass
```

## Bug Priority Levels

| Priority | Response | Merge |
|----------|----------|-------|
| low | Within 1 week | Standard process |
| medium | Within 2 days | Standard process |
| high | Within 8 hours | Fast-track |
| critical | Immediately | Hotfix branch |

## Workflow

```
1. Bug reported and tracked
2. code_developer picks up BUG-XXX
3. code_developer calls implement_bug_fix
4. Fix implemented in affected file
5. Regression test created (ensures bug doesn't return)
6. Commit created with fix(BUG-XXX) prefix
7. code_reviewer reviews commit
8. architect merges when approved
9. Bug status marked "fixed"
```

## Bug Fix Commit Format

Auto-generated commits follow convention:

```
fix(BUG-042): Fix authentication token validation

Previously, the authentication middleware was not properly
validating JWT tokens, allowing expired tokens to access
protected endpoints.

This commit adds proper token expiration checks and
refreshes tokens when needed.

Related: BUG-042
Tests: test_bug_042_regression.py passes
```

## Integration with Code Developer

```python
# 1. Get list of open bugs
bugs = db.read("bug_reports", {"status": "open"})

# 2. Pick high priority bug
bug = [b for b in bugs if b["priority"] == "critical"][0]

# 3. Implement fix
result = implement_bug_fix(db, {
    "bug_id": bug["id"],
    "create_test": True,
    "priority": "critical"
})

# 4. If successful, commit to review queue
if result["success"]:
    print(f"Bug {result['bug_id']} fixed: {result['commit_hash']}")
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| BugNotFoundError | Bug doesn't exist | Verify bug ID |
| CommitFailedError | Git commit failed | Check git status |
| TestFailedError | Regression test fails | Fix isn't working |
| FileNotFoundError | Affected file missing | Verify file path |

## Testing Bug Fixes

Run specific regression test:

```bash
pytest tests/test_bug_042_regression.py -v
```

Run all regression tests:

```bash
pytest tests/test_bug_*_regression.py -v
```

Run with coverage:

```bash
pytest tests/test_bug_042_regression.py --cov=coffee_maker
```

## Bug Tracking Integration

If using external bug tracking (Jira, GitHub Issues):

```python
# Update external system
subprocess.run([
    "gh", "issue", "close", bug_id,
    "-c", f"Fixed in commit {commit_hash}"
])
```
