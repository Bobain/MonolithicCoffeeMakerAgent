---
command: code_developer.create_pull_request
agent: code_developer
action: create_pull_request
tables:
  write: [system_audit]
  read: [roadmap_priority, specs_specification]
required_skills: []
required_tools: [database, gh]
---

# Command: code_developer.create_pull_request

## Purpose
Create GitHub pull request using gh CLI with auto-generated title and description from spec.

## Input Parameters

```yaml
priority_id: string      # Required - Priority implemented
branch: string           # Required - Source branch
base_branch: string      # Target branch (default: "main")
title: string            # PR title (auto-generated if not provided)
body: string             # PR description (auto-generated if not provided)
draft: boolean           # Create as draft PR (default: false)
```

## Database Operations

### 1. Get Priority and Spec
```python
from datetime import datetime
import subprocess
import json

def create_pull_request(db: DomainWrapper, params: dict):
    priority_id = params["priority_id"]
    branch = params["branch"]
    base_branch = params.get("base_branch", "main")

    # Get priority and spec for context
    priorities = db.read("roadmap_priority", {"id": priority_id})
    if not priorities:
        return {
            "success": False,
            "error": f"Priority {priority_id} not found"
        }

    priority = priorities[0]

    # Get spec if available
    spec = None
    if priority.get("spec_id"):
        specs = db.read("specs_specification", {"id": priority["spec_id"]})
        if specs:
            spec = specs[0]
```

### 2. Auto-Generate Title
```python
    # Use provided title or auto-generate
    title = params.get("title", f"Implement {priority_id}: {priority.get('title', 'Feature')}")
```

### 3. Auto-Generate PR Description
```python
    # Use provided body or auto-generate from spec
    if params.get("body"):
        body = params["body"]
    else:
        # Generate from priority and spec
        body_parts = [
            "## Summary",
            f"- {priority.get('description', 'Implementation of feature')}",
            ""
        ]

        # Add related info
        body_parts.extend([
            "## Related",
            f"- Priority: {priority_id}",
        ])

        if spec:
            body_parts.extend([
                f"- Spec: {spec['id']}",
                f"- Estimated Hours: {spec.get('estimated_hours', 'N/A')}"
            ])

        # Add footer
        body_parts.extend([
            "",
            "🤖 Generated with [Claude Code](https://claude.com/claude-code)",
            "",
            "Co-Authored-By: code_developer <noreply@anthropic.com>"
        ])

        body = "\n".join(body_parts)
```

### 4. Create PR using gh CLI
```python
    # Build gh command
    cmd = [
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", base_branch,
        "--head", branch
    ]

    if params.get("draft", False):
        cmd.append("--draft")

    # Execute gh CLI
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "success": False,
            "error": f"Failed to create PR: {result.stderr}",
            "stdout": result.stdout
        }
```

### 5. Parse PR Details
```python
    # Parse PR URL from output (e.g., "https://github.com/owner/repo/pull/123")
    pr_url = result.stdout.strip()
    if not pr_url:
        return {
            "success": False,
            "error": "Invalid PR creation response",
            "output": result.stdout
        }

    # Extract PR number
    try:
        pr_number = int(pr_url.split("/")[-1])
    except (ValueError, IndexError):
        return {
            "success": False,
            "error": f"Could not parse PR number from: {pr_url}"
        }
```

### 6. Audit Trail
```python
    # Create audit record for PR creation
    db.write("system_audit", {
        "table_name": "github_prs",
        "item_id": f"PR-{pr_number}",
        "action": "create",
        "field_changed": "pr_url",
        "new_value": pr_url,
        "changed_by": "code_developer",
        "changed_at": datetime.now().isoformat(),
        "metadata": json.dumps({
            "priority_id": priority_id,
            "branch": branch,
            "base": base_branch,
            "title": title
        })
    }, action="create")

    return {
        "success": True,
        "pr_number": pr_number,
        "pr_url": pr_url,
        "title": title,
        "status": "open",
        "base": base_branch,
        "head": branch
    }
```

## Output

```json
{
  "success": true,
  "pr_number": 123,
  "pr_url": "https://github.com/Bobain/MonolithicCoffeeMakerAgent/pull/123",
  "title": "Implement PRIORITY-28: Feature X",
  "status": "open"
}
```

## Success Criteria

- ✅ PR created on GitHub
- ✅ Title auto-generated from spec
- ✅ Description auto-generated with spec context
- ✅ Linked to priority and spec
- ✅ CI checks triggered
- ✅ Audit trail created

## PR Description Template

Auto-generated PR descriptions follow this format:

```markdown
## Summary
- Implementation of authentication system

## Related
- Priority: PRIORITY-28
- Spec: SPEC-131
- Estimated Hours: 8.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: code_developer <noreply@anthropic.com>
```

## GitHub CLI Integration

### Prerequisites
```bash
# gh CLI must be installed and authenticated
gh auth status
```

### Example PR Creation
```bash
gh pr create \
  --title "Implement PRIORITY-28: Feature X" \
  --body "## Summary
- Implemented authentication system
- Added user model and session management
- Tests pass with 92% coverage

## Related
- Priority: PRIORITY-28
- Spec: SPEC-131
- Tasks: TASK-31-1, TASK-31-2, TASK-31-3

🤖 Generated with [Claude Code](https://claude.com/claude-code)" \
  --base main \
  --head roadmap
```

## Workflow

```
1. code_developer completes implementation
2. code_developer commits code to feature branch
3. code_developer calls create_pull_request
4. PR created with auto-generated description
5. GitHub CI checks run automatically
6. project_manager monitors PR status
7. architect reviews and merges
```

## Error Handling

| Error Type | Cause | Resolution |
|------------|-------|------------|
| GitHubAPIError | Rate limit, auth | Wait, check token |
| BranchNotFoundError | Branch doesn't exist | Verify branch name |
| CLINotFoundError | gh not installed | Install GitHub CLI |
| InvalidPriorityError | Priority not found | Verify priority ID |

## Draft PRs

Create as draft for work-in-progress:

```python
create_pull_request(db, {
    "priority_id": "PRIORITY-28",
    "branch": "roadmap",
    "draft": True
})
# Creates draft PR, ready for conversion when complete
```

## Custom PR Description

Provide custom description if auto-generated is insufficient:

```python
create_pull_request(db, {
    "priority_id": "PRIORITY-28",
    "branch": "roadmap",
    "body": """## Summary
Custom implementation details

## Testing
- All tests passing
- Coverage: 92%

## Migration Notes
Database migration required
"""
})
```

## PR Naming Convention

Auto-generated titles follow pattern:
```
Implement {PRIORITY-ID}: {Title from ROADMAP}
```

Examples:
- "Implement PRIORITY-28: User Authentication"
- "Implement PRIORITY-10: Analytics Dashboard"
- "Implement PRIORITY-5: Database Schema"

## Integration with orchestrator

After PR creation:
- **project_manager** monitors PR status
- **project_manager** checks CI results
- **architect** reviews and merges
- **orchestrator** updates roadmap when merged
