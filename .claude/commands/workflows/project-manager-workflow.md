---
command: project-manager-workflow
workflow: manage
agent: project_manager
purpose: Complete project management workflow
tables: [roadmap_priority, specs_task, task_dependency, agent_notification]
tools: [file_system, git, github_cli]
duration: 5-30m
---

## Purpose

Execute complete project management workflow: roadmap updates, progress tracking, task planning, and status reporting. This is the PRIMARY workflow command for the project_manager agent, replacing 4 individual commands with one intelligent workflow.

## Workflow Overview

```
manage(action) → ROADMAP | TRACK | PLAN | REPORT → ManageResult
```

**Key Features**:
- **4 workflow actions**: ROADMAP (update/view/validate), TRACK (progress tracking), PLAN (create priorities/tasks), REPORT (status reports)
- **Auto-notifications**: Sends agent notifications for status changes
- **GitHub integration**: Uses `gh` CLI for PR/issue monitoring
- **ROADMAP.md sync**: Keeps database and file in sync
- **Rich result tracking**: Comprehensive ManageResult with notifications sent

## Input Parameters

```yaml
ACTION:
  type: string
  required: true
  enum: [roadmap, track, plan, report]
  description: |
    - roadmap: Update/view/validate ROADMAP.md
    - track: Track progress and send notifications
    - plan: Create new priorities and tasks
    - report: Generate status reports

PRIORITY_ID:
  type: string
  optional: true
  description: Priority to operate on (for track/plan actions)
  example: "PRIORITY-5"

UPDATES:
  type: dict
  optional: true
  description: Updates to apply (for track action)
  example: {"status": "in_progress", "progress": 50}

NOTIFY:
  type: boolean
  default: true
  description: Send agent notifications on changes

AUTO_COMMIT:
  type: boolean
  default: false
  description: Auto-commit ROADMAP.md changes

VERBOSE:
  type: boolean
  default: false
  description: Enable detailed logging
```

## Workflow Execution

### ROADMAP Action

Update, view, or validate ROADMAP.md:

```python
1. Parse docs/roadmap/ROADMAP.md
2. Validate structure and priorities
3. Sync with database (roadmap_priority table)
4. Apply any updates if provided
5. Write back to file if changes made
6. Return validated roadmap data
```

### TRACK Action

Track progress and send notifications:

```python
1. Load priority from database
2. Check for status changes
3. Update task statuses
4. Calculate progress percentage
5. Send notifications to relevant agents
6. Log activity in database
7. Return tracking summary
```

### PLAN Action

Create new priorities and tasks:

```python
1. Validate priority structure
2. Generate priority ID (PRIORITY-N)
3. Create database records
4. Generate task breakdown (TASK-N-M)
5. Update ROADMAP.md
6. Send notifications to architect
7. Return creation summary
```

### REPORT Action

Generate status reports:

```python
1. Query all active priorities
2. Calculate completion percentages
3. Identify blockers and risks
4. Generate markdown report
5. Optionally post to GitHub
6. Return report data
```

## Result Object

```python
@dataclass
class ManageResult:
    action: str  # roadmap | track | plan | report
    status: str  # success | partial | failed
    data: Any  # Action-specific data
    notifications_sent: int  # Count of notifications sent
    tasks_updated: int  # Count of tasks updated
    duration_seconds: float  # Total execution time
    metadata: Dict[str, Any]  # Additional context
```

## Success Criteria

### Full Success (status = "success")

- ✅ Action completed successfully
- ✅ Database updated
- ✅ Notifications sent (if enabled)
- ✅ ROADMAP.md synced (if applicable)

### Partial Success (status = "partial")

- ✅ Action partially completed
- ⚠️ Some operations failed
- ⚠️ Notifications partially sent

### Failure (status = "failed")

- ❌ Critical error occurred
- ❌ Action could not complete

## Database Operations

### Query: Load Priority

```sql
SELECT
    rp.priority_id,
    rp.title,
    rp.status,
    rp.progress,
    rp.assigned_agent,
    rp.metadata
FROM roadmap_priority rp
WHERE rp.priority_id = ?
```

### Update: Priority Status

```sql
UPDATE roadmap_priority
SET
    status = ?,
    progress = ?,
    updated_at = datetime('now'),
    metadata = json_set(metadata, '$.last_tracked', datetime('now'))
WHERE priority_id = ?
```

### Insert: Notification

```sql
INSERT INTO agent_notification (
    notification_id, agent_type, priority, message,
    metadata, created_at, status
) VALUES (?, ?, ?, ?, ?, datetime('now'), 'pending')
```

### Query: Task Dependencies

```sql
SELECT
    td.from_task_id,
    td.to_task_id,
    td.dependency_type,
    st.status as dependent_status
FROM task_dependency td
JOIN specs_task st ON td.to_task_id = st.task_id
WHERE td.from_task_id = ?
```

## Error Handling

| Error | Cause | Recovery | Status |
|-------|-------|----------|--------|
| Priority not found | Invalid PRIORITY_ID | Verify ID exists | failed |
| ROADMAP parse error | Malformed markdown | Fix ROADMAP.md syntax | failed |
| Database sync failed | Concurrent updates | Retry with lock | partial |
| Notification failed | Agent not available | Log and continue | partial |
| GitHub API error | Rate limit or auth | Retry or skip GitHub | partial |

## Examples

### Example 1: Update ROADMAP

```python
result = workflow.manage(
    action="roadmap",
    priority_id="PRIORITY-5",
    updates={"status": "in_progress"},
    notify=True
)
```

**Result**:
```python
ManageResult(
    action="roadmap",
    status="success",
    data={
        "priority_id": "PRIORITY-5",
        "title": "Implement Authentication System",
        "status": "in_progress",
        "progress": 30
    },
    notifications_sent=2,  # architect + code_developer
    tasks_updated=1,
    duration_seconds=2.3,
    metadata={"roadmap_updated": True, "file_synced": True}
)
```

### Example 2: Track Progress

```python
result = workflow.manage(
    action="track",
    priority_id="PRIORITY-5",
    updates={"progress": 50, "status": "in_progress"},
    notify=True
)
```

**Result**:
```python
ManageResult(
    action="track",
    status="success",
    data={
        "priority_id": "PRIORITY-5",
        "previous_progress": 30,
        "current_progress": 50,
        "status": "in_progress",
        "tasks_completed": 3,
        "tasks_remaining": 3
    },
    notifications_sent=1,  # architect notified
    tasks_updated=3,
    duration_seconds=1.8,
    metadata={"milestone": "50% complete"}
)
```

### Example 3: Create Plan

```python
result = workflow.manage(
    action="plan",
    priority_id="PRIORITY-6",
    updates={
        "title": "Add OAuth2 Support",
        "description": "Implement OAuth2 authentication flow",
        "assigned_agent": "code_developer"
    },
    notify=True
)
```

**Result**:
```python
ManageResult(
    action="plan",
    status="success",
    data={
        "priority_id": "PRIORITY-6",
        "title": "Add OAuth2 Support",
        "tasks_created": 5,
        "task_ids": ["TASK-6-1", "TASK-6-2", "TASK-6-3", "TASK-6-4", "TASK-6-5"]
    },
    notifications_sent=2,  # architect + code_developer
    tasks_updated=0,
    duration_seconds=3.5,
    metadata={"roadmap_updated": True, "dependencies_mapped": True}
)
```

### Example 4: Generate Report

```python
result = workflow.manage(
    action="report",
    verbose=True
)
```

**Result**:
```python
ManageResult(
    action="report",
    status="success",
    data={
        "report_type": "status",
        "total_priorities": 12,
        "completed": 5,
        "in_progress": 4,
        "blocked": 1,
        "pending": 2,
        "completion_rate": 41.7,
        "report_path": "reports/status-20251028.md"
    },
    notifications_sent=0,
    tasks_updated=0,
    duration_seconds=5.2,
    metadata={"github_posted": False}
)
```

## Notification Types

### Status Change Notifications

```python
# Sent when priority status changes
{
    "agent_type": "architect",
    "priority": "high",
    "message": "PRIORITY-5 status changed: pending → in_progress",
    "metadata": {
        "priority_id": "PRIORITY-5",
        "old_status": "pending",
        "new_status": "in_progress"
    }
}
```

### Progress Milestone Notifications

```python
# Sent at 25%, 50%, 75%, 100% completion
{
    "agent_type": "code_developer",
    "priority": "medium",
    "message": "PRIORITY-5 reached 50% completion",
    "metadata": {
        "priority_id": "PRIORITY-5",
        "progress": 50,
        "tasks_completed": 3,
        "tasks_remaining": 3
    }
}
```

### Blocker Notifications

```python
# Sent when tasks become blocked
{
    "agent_type": "architect",
    "priority": "urgent",
    "message": "TASK-5-2 blocked by dependency TASK-4-3",
    "metadata": {
        "task_id": "TASK-5-2",
        "blocker_id": "TASK-4-3",
        "blocker_status": "pending"
    }
}
```

## GitHub Integration

### Monitor Pull Requests

```bash
# Check PR status for priority
gh pr list --search "PRIORITY-5" --json number,title,state,checks

# Get PR details
gh pr view 123 --json title,body,state,mergeable,checks
```

### Monitor Issues

```bash
# List issues for priority
gh issue list --label "PRIORITY-5" --json number,title,state,assignees

# Close completed issues
gh issue close 42 --comment "Completed in PRIORITY-5"
```

### Post Status Updates

```bash
# Comment on PR with status
gh pr comment 123 --body "PRIORITY-5: 50% complete, 3/6 tasks done"

# Create milestone update issue
gh issue create --title "PRIORITY-5 Status Update" --body "..."
```

## Implementation Notes

### ROADMAP.md Structure

```markdown
## PRIORITY-5: Implement Authentication System
**Status**: IN_PROGRESS | **Progress**: 50% | **Assigned**: code_developer

### Description
Implement complete authentication system with JWT tokens

### Tasks
- [x] TASK-5-1: Create user model and database schema
- [x] TASK-5-2: Implement JWT token generation
- [x] TASK-5-3: Add authentication middleware
- [ ] TASK-5-4: Implement refresh token logic
- [ ] TASK-5-5: Add rate limiting
- [ ] TASK-5-6: Write comprehensive tests
```

### Database Sync Algorithm

```python
1. Parse ROADMAP.md → extract priorities
2. Query database → get existing priorities
3. Compare:
   - New in file → INSERT to database
   - Changed in file → UPDATE in database
   - Removed from file → MARK deleted in database
4. Write changes back to ROADMAP.md
5. Log sync activity
```

### Progress Calculation

```python
def calculate_progress(priority_id):
    tasks = query_tasks(priority_id)
    completed = sum(1 for t in tasks if t.status == "completed")
    total = len(tasks)
    return (completed / total * 100) if total > 0 else 0
```

## Integration with Other Workflows

### → Architect (spec creation)

```python
# Project manager creates plan, notifies architect
pm_result = project_manager.manage(
    action="plan",
    priority_id="PRIORITY-6"
)
# Architect auto-notified, creates specs
```

### → Code Developer (task assignment)

```python
# Project manager tracks progress
pm_result = project_manager.manage(
    action="track",
    priority_id="PRIORITY-5",
    updates={"status": "in_progress"}
)
# Developer receives notification, starts work
```

### → Code Reviewer (quality tracking)

```python
# Project manager monitors quality
pm_result = project_manager.manage(action="report")
# Includes quality metrics from reviewer
```

## Performance Expectations

| Action | Duration | Database Ops | Notifications |
|--------|----------|--------------|---------------|
| roadmap | 2-5s | 5-20 queries | 0-2 sent |
| track | 1-3s | 2-10 queries | 1-3 sent |
| plan | 3-10s | 10-30 inserts | 2-4 sent |
| report | 5-15s | 50-200 queries | 0-1 sent |

## Best Practices

1. **Use roadmap action** for ROADMAP.md updates
2. **Use track action** for regular progress monitoring (daily)
3. **Use plan action** for new priority creation
4. **Use report action** for status reports (weekly)
5. **Enable notify=True** for team awareness
6. **Use auto_commit=True** cautiously (manual review preferred)
7. **Check notifications_sent** to ensure team notified
8. **Review metadata** for sync and GitHub operation status

## Related Commands

- `architect.spec()` - Create specs for planned priorities
- `developer.work()` - Implement tracked tasks
- `reviewer.review()` - Review completed work
- `orchestrator.coordinate()` - Manage parallel execution

---

**Workflow Reduction**: This single `manage()` command replaces:
1. `update_roadmap()`
2. `track_progress()`
3. `create_priority()`
4. `generate_report()`

**Context Savings**: ~300 lines vs ~1,800 lines (4 commands)
