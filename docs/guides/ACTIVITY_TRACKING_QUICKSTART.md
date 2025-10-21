# Activity Tracking Quick Start Guide

**For**: Developers integrating activity logging into autonomous agents
**Status**: Phases 1-2 Complete (ActivityDB, ActivityLogger, StandupGenerator working)
**Location**: `coffee_maker/autonomous/activity_*.py`

---

## 60-Second Overview

### What is Activity Tracking?

The code_developer daemon now automatically logs its work (commits, tests, PRs, etc.) to a SQLite database and can generate professional daily standup reports using Claude AI.

### For Daemon Integration (Phase 4)

Add 5 lines to daemon.py to start logging all work:

```python
from coffee_maker.autonomous.activity_logger import ActivityLogger

logger = ActivityLogger()
logger.start_priority(priority_number, priority_name)
# ... your existing implementation code ...
logger.complete_priority(priority_number, success=True)
```

### For Chat Integration (Phase 3)

Show yesterday's standup before chat starts:

```python
from coffee_maker.autonomous.standup_generator import StandupGenerator
from datetime import date, timedelta

gen = StandupGenerator()
yesterday = date.today() - timedelta(days=1)
summary = gen.generate_daily_standup(yesterday)
print(summary.summary_text)  # Display standup to user
```

---

## Complete Integration Guide

### Step 1: Import the Logger

```python
from coffee_maker.autonomous.activity_logger import ActivityLogger

logger = ActivityLogger()  # Creates/connects to activity database
```

### Step 2: Mark Priority Start

At the beginning of each priority implementation:

```python
logger.start_priority("9.1", "Enhanced Communication & Daily Standup")
```

### Step 3: Log Work Activities

As you complete work, log each type of activity:

#### Commit
```python
logger.log_commit(
    message="Add activity tracking to daemon",
    files_changed=3,
    lines_added=250,
    lines_removed=10,
    commit_hash="abc123def456"  # optional but recommended
)
```

#### Tests
```python
logger.log_test_run(
    passed=47,
    failed=0,
    skipped=2,
    duration_seconds=12.5,
    test_framework="pytest"
)
```

#### Pull Request
```python
logger.log_pr_created(
    pr_number=42,
    pr_title="Implement Activity Tracking",
    pr_url="https://github.com/org/repo/pull/42",
    branch="feature/activity-tracking"
)
```

#### Branch
```python
logger.log_branch_created(
    branch="feature/activity-tracking",
    description="Activity tracking for daily standups"
)
```

#### Errors
```python
logger.log_error(
    error_message="Database connection timeout after 3 retries",
    error_type="TimeoutError",
    is_blocking=False  # True if it stops progress
)
```

#### Dependencies
```python
logger.log_dependency_installed(
    package_name="anthropic",
    version="0.38.0"
)
```

#### Documentation
```python
logger.log_documentation_updated(
    file_path="docs/ACTIVITY_TRACKING.md",
    description="Added usage examples and architecture overview"
)
```

#### File Changes
```python
logger.log_file_changed(
    file_path="coffee_maker/autonomous/activity_db.py",
    change_type="created",
    description="New SQLite database for activity tracking"
)
```

### Step 4: Mark Priority Complete

At the end of priority implementation:

```python
logger.complete_priority(
    "9.1",
    success=True,  # False if failed
    summary="Activity tracking fully implemented with 40+ tests passing"
)
```

### Step 5: Generate Standup

After a day's work, generate a standup report:

```python
from coffee_maker.autonomous.standup_generator import StandupGenerator
from datetime import date, timedelta

gen = StandupGenerator()
yesterday = date.today() - timedelta(days=1)
summary = gen.generate_daily_standup(yesterday)

print(summary.summary_text)
print("\nMetrics:")
for key, value in summary.metrics.items():
    print(f"  {key}: {value}")
```

---

## Real-World Example

### Daemon Integration Example

```python
# In daemon.py (pseudocode)
from coffee_maker.autonomous.activity_logger import ActivityLogger

logger = ActivityLogger()

for priority in roadmap.get_planned_priorities():
    try:
        # Log start
        logger.start_priority(priority.number, priority.name)

        # Create spec
        spec = architect.create_spec(priority)
        logger.log_file_changed(spec.path, "created")

        # Implement feature
        code_developer.implement(priority, spec)

        # Log commits
        for commit in git.get_recent_commits(3):
            logger.log_commit(
                message=commit.message,
                files_changed=len(commit.files),
                lines_added=commit.additions,
                commit_hash=commit.sha
            )

        # Run tests
        result = subprocess.run(["pytest"], capture_output=True)
        logger.log_test_run(
            passed=result.passed_count,
            failed=result.failed_count,
            duration_seconds=result.duration
        )

        # Create PR
        pr = github.create_pr(priority.branch)
        logger.log_pr_created(
            pr_number=pr.number,
            pr_title=pr.title,
            pr_url=pr.url,
            branch=priority.branch
        )

        # Log completion
        logger.complete_priority(priority.number, success=True)

    except Exception as e:
        logger.log_error(str(e), type(e).__name__, is_blocking=True)
        logger.complete_priority(priority.number, success=False)
```

---

## API Reference

### ActivityLogger Methods

```python
logger = ActivityLogger()

# Priority management
logger.start_priority(priority_number: str, priority_name: str)
logger.complete_priority(
    priority_number: str,
    success: bool = True,
    summary: Optional[str] = None
) -> None

# Work logging (all return activity_id: int)
logger.log_commit(
    message: str,
    files_changed: int = 0,
    lines_added: int = 0,
    lines_removed: int = 0,
    commit_hash: Optional[str] = None
) -> int

logger.log_test_run(
    passed: int,
    failed: int,
    skipped: int = 0,
    duration_seconds: float = 0,
    test_framework: str = "pytest"
) -> int

logger.log_pr_created(
    pr_number: int,
    pr_title: str,
    pr_url: str,
    branch: str
) -> int

logger.log_branch_created(
    branch: str,
    description: Optional[str] = None
) -> int

logger.log_error(
    error_message: str,
    error_type: Optional[str] = None,
    is_blocking: bool = False
) -> int

logger.log_dependency_installed(
    package_name: str,
    version: Optional[str] = None
) -> int

logger.log_documentation_updated(
    file_path: str,
    description: Optional[str] = None
) -> int

logger.log_file_changed(
    file_path: str,
    change_type: str,
    description: Optional[str] = None
) -> int
```

### StandupGenerator Methods

```python
gen = StandupGenerator()

# Generate standup report
summary = gen.generate_daily_standup(
    target_date: date,
    force_regenerate: bool = False
) -> DailySummary

# DailySummary attributes
summary.date  # str: YYYY-MM-DD
summary.summary_text  # str: Markdown formatted report
summary.metrics  # dict: {commits, test_runs, prs_created, ...}
summary.activities  # List[Activity]: All activities for the day
summary.generated_at  # str: ISO 8601 timestamp
```

### ActivityDB Methods

```python
db = ActivityDB()

# Log activities (advanced - normally use ActivityLogger)
db.log_activity(
    activity_type: str,
    title: str,
    description: Optional[str] = None,
    priority_number: Optional[str] = None,
    priority_name: Optional[str] = None,
    metadata: Optional[Dict] = None,
    outcome: str = "success",
    session_id: Optional[str] = None
) -> int

# Query activities
db.get_activities(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    activity_type: Optional[str] = None,
    priority_number: Optional[str] = None,
    limit: int = 100
) -> List[Activity]

db.get_activity(activity_id: int) -> Optional[Activity]

# Get metrics
db.get_daily_metrics(target_date: date) -> Dict[str, int]
```

---

## Database Storage

### Default Location
```
data/activity.db
```

### Custom Location
```python
from coffee_maker.autonomous.activity_logger import ActivityLogger
from coffee_maker.autonomous.activity_db import ActivityDB

db = ActivityDB(db_path="/custom/path/activity.db")
logger = ActivityLogger(db=db)
```

---

## Configuration

### Anthropic API Key (Required for Claude Summaries)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Model Used
- **Model**: claude-3-5-sonnet-20241022
- **Max tokens**: 2000
- **Temperature**: 0.7

### Fallback Behavior
If Claude API fails, `StandupGenerator` automatically generates a template-based summary with basic metrics.

---

## Best Practices

### 1. Always Set Priority Context

```python
# Good - priority context set
logger.start_priority("2.5", "CI Testing")
logger.log_commit(message="Add test")
# Commit automatically tagged with priority 2.5

# Avoid - no context
logger.log_commit(message="Add test")
# Commit has no priority information
```

### 2. Log Commits Immediately After Push

```python
# After git push
git_log = subprocess.run(["git", "log", "-1", "--format=%H %s"], capture_output=True)
sha, message = git_log.stdout.split(maxsplit=1)

logger.log_commit(
    message=message.strip(),
    files_changed=3,
    lines_added=120,
    commit_hash=sha
)
```

### 3. Group Related Activities with Sessions

Sessions are automatically managed but can be tracked:

```python
logger.start_priority("2.5", "Feature X")
session_id = logger.current_session_id

logger.log_commit(message="Part 1")
logger.log_commit(message="Part 2")
logger.log_test_run(passed=50, failed=0)

# All activities grouped under session_id
```

### 4. Log Errors for Debugging

```python
try:
    result = run_tests()
except Exception as e:
    logger.log_error(
        error_message=str(e),
        error_type=type(e).__name__,
        is_blocking=not result.partial_success
    )
```

---

## Troubleshooting

### Issue: "No Anthropic API key found"

**Solution**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python your_script.py
```

### Issue: Activities not showing in queries

**Debug**:
```python
db = ActivityDB()
activities = db.get_activities(limit=10)
print(f"Total activities: {len(activities)}")
for a in activities:
    print(f"  - {a.created_at}: {a.title}")
```

### Issue: Database locked

**Cause**: Long-running process holding database

**Solution**: Already handled with WAL mode and timeouts. If persists:
```python
# Check for stuck processes
db.db_path  # Check this file's modification time
```

---

## Testing Your Integration

### Manual Test

```python
#!/usr/bin/env python3
from coffee_maker.autonomous.activity_logger import ActivityLogger
from coffee_maker.autonomous.standup_generator import StandupGenerator
from datetime import date

# Log some activities
logger = ActivityLogger()
logger.start_priority("TEST", "Integration Test")
logger.log_commit(message="Test commit", files_changed=1, lines_added=10)
logger.log_test_run(passed=5, failed=0)
logger.complete_priority("TEST", success=True)

# Generate standup
gen = StandupGenerator()
summary = gen.generate_daily_standup(date.today())

print("SUCCESS!" if summary.metrics['total_activities'] > 0 else "FAILED!")
```

### Automated Test

```bash
pytest tests/unit/test_activity_db.py -v
pytest tests/unit/test_standup_generator.py -v
```

---

## Next Steps

1. **Phase 3**: Integrate into chat_interface.py for daily standups
2. **Phase 4**: Integrate into daemon.py for automatic activity logging
3. **Phase 5**: Add analytics dashboard and reporting

---

## Support

- **Code**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/coffee_maker/autonomous/`
- **Tests**: `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/tests/unit/test_activity_db.py`
- **Demo**: `docs/demos/priority-9-daily-standup-demo.md`
