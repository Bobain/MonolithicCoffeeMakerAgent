# Consolidated Commands API Reference

## Overview

Complete API documentation for all 36 consolidated commands across 8 agents.

Each command uses action-based routing where the `action` parameter determines the specific operation to perform.

---

## Return Value Format

All commands return a result dictionary:

```python
{
    "success": bool,           # Command succeeded
    "action": str,             # Action that was performed
    "data": dict | list | any, # Result data (varies by action)
    "error": str,              # Error message (if success=False)
    "timestamp": str,          # ISO timestamp
    "duration_ms": int         # Execution duration
}
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| `MISSING_PARAM` | Required parameter missing | `priority_id` required for roadmap/details |
| `INVALID_VALUE` | Parameter value invalid | `priority_id="INVALID"` doesn't exist |
| `PERMISSION_DENIED` | Insufficient permissions | Try to modify protected file |
| `NOT_FOUND` | Resource not found | Priority doesn't exist |
| `CONFLICT` | Resource conflict | Priority already claimed |
| `INTERNAL_ERROR` | Server error | Database error |

---

## Project Manager Commands

### command: `roadmap`

**Module**: `coffee_maker.commands.consolidated.project_manager_commands.ProjectManagerCommands.roadmap`

#### Action: `list`

List all priorities, optionally filtered by status.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | str | No | None | Filter by status (e.g., "In Progress", "Complete") |
| `assignee` | str | No | None | Filter by assignee |
| `limit` | int | No | None | Limit number of results |
| `offset` | int | No | 0 | Offset for pagination |

**Returns**:
```python
{
    "success": True,
    "action": "list",
    "data": [
        {
            "id": "PRIORITY-28",
            "title": "User Authentication",
            "status": "In Progress",
            "assignee": "code_developer",
            "created_at": "2025-10-01T10:00:00Z",
            "updated_at": "2025-10-27T15:30:00Z"
        },
        ...
    ],
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 45
}
```

**Example**:
```python
result = pm.roadmap(action="list", status="In Progress")
for priority in result["data"]:
    print(f"{priority['id']}: {priority['title']} ({priority['status']})")
```

**Errors**:
- `INVALID_VALUE` - Invalid status filter

---

#### Action: `details`

Get detailed information about a priority.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier (e.g., "PRIORITY-28") |

**Returns**:
```python
{
    "success": True,
    "action": "details",
    "data": {
        "id": "PRIORITY-28",
        "title": "User Authentication",
        "description": "Implement user login and authentication",
        "status": "In Progress",
        "assignee": "code_developer",
        "created_at": "2025-10-01T10:00:00Z",
        "updated_at": "2025-10-27T15:30:00Z",
        "estimated_completion": "2025-11-15",
        "tags": ["auth", "security", "critical"],
        "related_specs": ["SPEC-100", "SPEC-105"],
        "test_coverage": 85
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 30
}
```

**Example**:
```python
result = pm.roadmap(action="details", priority_id="PRIORITY-28")
if result["success"]:
    priority = result["data"]
    print(f"Title: {priority['title']}")
    print(f"Status: {priority['status']}")
    print(f"Coverage: {priority['test_coverage']}%")
```

**Errors**:
- `MISSING_PARAM` - `priority_id` not provided
- `NOT_FOUND` - Priority doesn't exist

---

#### Action: `update`

Update priority metadata.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |
| `metadata` | dict | Yes | - | Metadata to update |
| `assignee` | str | No | - | New assignee |
| `status` | str | No | - | New status |
| `estimated_completion` | str | No | - | ISO date for completion |

**Returns**:
```python
{
    "success": True,
    "action": "update",
    "data": {
        "id": "PRIORITY-28",
        "updated_fields": ["assignee", "estimated_completion"],
        "new_values": {
            "assignee": "code_developer",
            "estimated_completion": "2025-11-15"
        }
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 25
}
```

**Example**:
```python
result = pm.roadmap(
    action="update",
    priority_id="PRIORITY-28",
    metadata={"status": "blocked", "notes": "Waiting on spec"},
    assignee="architect"
)
```

**Errors**:
- `MISSING_PARAM` - `priority_id` or `metadata` not provided
- `NOT_FOUND` - Priority doesn't exist
- `INVALID_VALUE` - Invalid metadata

---

#### Action: `status`

Check current status of a priority.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |

**Returns**:
```python
{
    "success": True,
    "action": "status",
    "data": {
        "priority_id": "PRIORITY-28",
        "current_status": "In Progress",
        "progress": 65,
        "assignee": "code_developer",
        "estimated_completion": "2025-11-15",
        "blocked": False,
        "blocking_issues": []
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 20
}
```

**Example**:
```python
result = pm.roadmap(action="status", priority_id="PRIORITY-28")
status = result["data"]
print(f"Status: {status['current_status']}")
print(f"Progress: {status['progress']}%")
```

---

### command: `status`

**Module**: `coffee_maker.commands.consolidated.project_manager_commands.ProjectManagerCommands.status`

#### Action: `developer`

Get developer status (which agents are running, what they're doing).

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "action": "developer",
    "data": {
        "agents": {
            "code_developer": {
                "status": "running",
                "current_task": "TASK-31-1",
                "priority": "PRIORITY-10",
                "started_at": "2025-10-27T14:00:00Z",
                "elapsed": "1h 35m"
            },
            "architect": {
                "status": "idle",
                "last_task": "SPEC-105",
                "last_completed": "2025-10-27T12:30:00Z"
            }
        }
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 50
}
```

---

#### Action: `notifications`

Get all notifications.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `unread_only` | bool | No | True | Only unread notifications |
| `limit` | int | No | 50 | Max notifications to return |

**Returns**:
```python
{
    "success": True,
    "action": "notifications",
    "data": [
        {
            "id": 1,
            "title": "Priority 28 blocked",
            "message": "Code review needed",
            "level": "warning",
            "read": False,
            "created_at": "2025-10-27T15:00:00Z"
        }
    ],
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 30
}
```

---

#### Action: `read`

Mark notification as read.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `notification_id` | int | Yes | - | Notification ID |

**Returns**:
```python
{
    "success": True,
    "action": "read",
    "data": {"notification_id": 1, "marked_read": True},
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 15
}
```

---

### command: `dependencies`

**Module**: `coffee_maker.commands.consolidated.project_manager_commands.ProjectManagerCommands.dependencies`

#### Action: `check`

Check if a dependency is approved for use.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `package_name` | str | Yes | - | Package name (e.g., "numpy") |
| `version` | str | No | None | Package version |

**Returns**:
```python
{
    "success": True,
    "action": "check",
    "data": {
        "package": "numpy",
        "version": "1.24.0",
        "status": "approved",
        "approved_by": "architect",
        "approved_at": "2025-10-15T10:00:00Z",
        "tier": "core",
        "max_version": "2.0.0"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 25
}
```

---

#### Action: `add`

Add a new dependency (requires pre-approval).

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `package_name` | str | Yes | - | Package name |
| `version` | str | Yes | - | Package version |
| `purpose` | str | No | - | Why this dependency |

**Returns**:
```python
{
    "success": True,
    "action": "add",
    "data": {
        "package": "pandas",
        "version": "2.0.0",
        "added_at": "2025-10-27T15:35:00Z",
        "status": "added"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 40
}
```

---

#### Action: `list`

List all dependencies.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tier` | str | No | None | Filter by tier (core, optional, dev) |

**Returns**:
```python
{
    "success": True,
    "action": "list",
    "data": [
        {
            "package": "numpy",
            "version": "1.24.0",
            "tier": "core",
            "purpose": "Data processing"
        },
        {
            "package": "pytest",
            "version": "7.0.0",
            "tier": "dev",
            "purpose": "Testing"
        }
    ],
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 30
}
```

---

### command: `github`

**Module**: `coffee_maker.commands.consolidated.project_manager_commands.ProjectManagerCommands.github`

#### Action: `monitor_pr`

Monitor a pull request.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `pr_number` | int | Yes | - | GitHub PR number |

**Returns**:
```python
{
    "success": True,
    "action": "monitor_pr",
    "data": {
        "pr_number": 42,
        "title": "Add Authentication",
        "status": "open",
        "created_by": "code_developer",
        "created_at": "2025-10-27T10:00:00Z",
        "checks": {
            "ci": "passing",
            "tests": "passing",
            "coverage": "85%"
        }
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 200
}
```

---

#### Action: `track_issue`

Track a GitHub issue.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `issue_number` | int | Yes | - | GitHub issue number |

**Returns**:
```python
{
    "success": True,
    "action": "track_issue",
    "data": {
        "issue_number": 15,
        "title": "Bug in authentication",
        "status": "open",
        "priority": "high",
        "assigned_to": "code_developer"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 150
}
```

---

#### Action: `sync`

Sync GitHub status with local database.

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "action": "sync",
    "data": {
        "prs_synced": 5,
        "issues_synced": 12,
        "last_sync": "2025-10-27T15:35:00Z"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 500
}
```

---

### command: `stats`

**Module**: `coffee_maker.commands.consolidated.project_manager_commands.ProjectManagerCommands.stats`

#### Action: `roadmap`

Get ROADMAP statistics.

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "action": "roadmap",
    "data": {
        "total_priorities": 50,
        "in_progress": 3,
        "completed": 30,
        "blocked": 2,
        "pending": 15,
        "average_completion_time": "8.5 days",
        "completion_rate": "85%"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 80
}
```

---

#### Action: `feature`

Get feature statistics.

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "action": "feature",
    "data": {
        "total_features": 48,
        "completed": 40,
        "in_development": 5,
        "planned": 3,
        "average_implementation_time": "5 days",
        "test_coverage": "87%"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 100
}
```

---

#### Action: `spec`

Get specification statistics.

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "action": "spec",
    "data": {
        "total_specs": 120,
        "complete": 95,
        "draft": 20,
        "archived": 5,
        "average_spec_size": "2500 words",
        "spec_coverage": "79%"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 90
}
```

---

#### Action: `audit`

Get audit trail.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `days` | int | No | 30 | Days to look back |

**Returns**:
```python
{
    "success": True,
    "action": "audit",
    "data": {
        "period": "last 30 days",
        "events": 450,
        "by_type": {
            "create": 45,
            "update": 200,
            "delete": 5,
            "approve": 50
        },
        "by_agent": {
            "code_developer": 180,
            "architect": 150,
            "project_manager": 120
        }
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 200
}
```

---

## Code Developer Commands

### command: `implement`

**Module**: `coffee_maker.commands.consolidated.code_developer_commands.CodeDeveloperCommands.implement`

#### Action: `claim`

Claim a priority to work on.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |
| `force_claim` | bool | No | False | Override existing claim |
| `estimated_start` | str | No | None | ISO date to start |

**Returns**:
```python
{
    "success": True,
    "action": "claim",
    "data": {
        "priority_id": "PRIORITY-10",
        "claimed_by": "code_developer",
        "claimed_at": "2025-10-27T15:35:00Z",
        "estimated_start": "2025-10-28T09:00:00Z"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 45
}
```

---

#### Action: `load`

Load technical specification for a priority.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |

**Returns**:
```python
{
    "success": True,
    "action": "load",
    "data": {
        "priority_id": "PRIORITY-10",
        "spec_id": "SPEC-100",
        "title": "User Authentication",
        "sections": ["overview", "api_design", "database"],
        "spec_content": "..."
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 100
}
```

---

#### Action: `update_status`

Update implementation status.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |
| `status` | str | Yes | - | New status (claiming, in_progress, testing, ready_review, complete) |
| `progress` | int | No | None | Progress percentage (0-100) |

**Returns**:
```python
{
    "success": True,
    "action": "update_status",
    "data": {
        "priority_id": "PRIORITY-10",
        "previous_status": "claiming",
        "new_status": "in_progress",
        "updated_at": "2025-10-27T15:35:00Z"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 30
}
```

---

#### Action: `record_commit`

Record a git commit.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `commit_sha` | str | Yes | - | Git commit SHA |
| `commit_message` | str | Yes | - | Commit message |
| `files_modified` | list | No | None | List of modified files |

**Returns**:
```python
{
    "success": True,
    "action": "record_commit",
    "data": {
        "commit_sha": "abc123def456",
        "recorded_at": "2025-10-27T15:35:00Z",
        "priority_id": "PRIORITY-10"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 40
}
```

---

#### Action: `complete`

Mark implementation as complete.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `priority_id` | str | Yes | - | Priority identifier |

**Returns**:
```python
{
    "success": True,
    "action": "complete",
    "data": {
        "priority_id": "PRIORITY-10",
        "completed_at": "2025-10-27T15:35:00Z",
        "total_duration": "3 days 4 hours"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 50
}
```

---

### command: `test`

**Module**: `coffee_maker.commands.consolidated.code_developer_commands.CodeDeveloperCommands.test`

#### Action: `run`

Run test suite.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | str | No | "tests/" | Path to run tests from |
| `pattern` | str | No | None | Test pattern (e.g., "test_*.py") |

**Returns**:
```python
{
    "success": True,
    "action": "run",
    "data": {
        "total": 150,
        "passed": 145,
        "failed": 5,
        "skipped": 0,
        "coverage": "87%",
        "duration": "45.2 seconds"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 45200
}
```

---

#### Action: `fix`

Debug and fix test failures.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `test_file` | str | No | None | Specific test file |
| `failures_only` | bool | No | True | Only show failures |

**Returns**:
```python
{
    "success": True,
    "action": "fix",
    "data": {
        "failures_found": 5,
        "fixed": 3,
        "remaining": 2,
        "fixes": [
            {
                "test": "test_auth_login",
                "issue": "Mock not configured",
                "fix": "Added mock setup"
            }
        ]
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 120
}
```

---

#### Action: `coverage`

Generate coverage report.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_percentage` | int | No | 80 | Minimum coverage percentage |
| `path` | str | No | None | Path to analyze |

**Returns**:
```python
{
    "success": True,
    "action": "coverage",
    "data": {
        "overall": "87%",
        "by_module": {
            "coffee_maker/auth.py": "92%",
            "coffee_maker/api.py": "78%",
            "coffee_maker/models.py": "88%"
        },
        "uncovered_lines": 245
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 3000
}
```

---

### command: `git`

**Module**: `coffee_maker.commands.consolidated.code_developer_commands.CodeDeveloperCommands.git`

#### Action: `commit`

Create git commit.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `message` | str | Yes | - | Commit message |
| `co_author` | str | No | None | Co-author (for collaborative commits) |

**Returns**:
```python
{
    "success": True,
    "action": "commit",
    "data": {
        "commit_sha": "abc123def456",
        "message": "feat: Add authentication",
        "files_committed": 12,
        "inserted": 450,
        "deleted": 30
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 200
}
```

---

#### Action: `push`

Push to remote repository.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `branch` | str | No | "roadmap" | Branch to push |

**Returns**:
```python
{
    "success": True,
    "action": "push",
    "data": {
        "branch": "roadmap",
        "commits_pushed": 3,
        "last_commit": "abc123def456"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 1500
}
```

---

#### Action: `create_pr`

Create pull request.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | str | Yes | - | PR title |
| `description` | str | Yes | - | PR description |
| `base_branch` | str | No | "main" | Base branch |

**Returns**:
```python
{
    "success": True,
    "action": "create_pr",
    "data": {
        "pr_number": 42,
        "pr_url": "https://github.com/user/repo/pull/42",
        "title": "Add Authentication",
        "created_at": "2025-10-27T15:35:00Z"
    },
    "timestamp": "2025-10-27T15:35:00Z",
    "duration_ms": 500
}
```

---

## Additional Commands (Summary)

The remaining commands (Architect, Code Reviewer, Orchestrator, Assistant, User Listener, UX Design Expert) follow the same pattern with action-based routing.

See `docs/CONSOLIDATED_COMMANDS_USER_GUIDE.md` for detailed examples of all commands.

---

## Migration from Old API

### Finding Legacy Commands

```python
from coffee_maker.commands.consolidated.migration import find_legacy_commands

findings = find_legacy_commands("coffee_maker/")
for finding in findings:
    print(f"{finding['file']}: {finding['command']} -> {finding['replacement']}")
```

### Automated Migration

```python
from coffee_maker.commands.consolidated.migration import CodeMigrator

migrator = CodeMigrator("coffee_maker/")
migrator.migrate_all()
```

### Manual Migration

Replace old commands with new consolidated commands:

```python
# Old
pm.check_priority_status("PRIORITY-28")

# New
pm.roadmap(action="status", priority_id="PRIORITY-28")
```

---

## Performance Characteristics

- **Average latency**: 30-100ms for most operations
- **Database operations**: 10-50ms
- **External API calls** (GitHub): 200-2000ms
- **Git operations**: 500-2000ms

---

## Backward Compatibility

All old commands are automatically aliased to new consolidated commands with deprecation warnings:

```python
# This still works:
pm.check_priority_status("PRIORITY-28")

# But generates warning:
# DeprecationWarning: check_priority_status is deprecated,
# use roadmap(action="status", priority_id="PRIORITY-28") instead
```

---

## Error Handling Example

```python
try:
    result = pm.roadmap(action="details", priority_id="PRIORITY-999")

    if not result.get("success"):
        error = result.get("error")
        print(f"Error: {error}")
    else:
        priority = result["data"]
        print(f"Found: {priority['title']}")

except Exception as e:
    print(f"Exception: {e}")
```

---

**Last Updated**: 2025-10-27
**Version**: 2.0 (Consolidated Architecture)
