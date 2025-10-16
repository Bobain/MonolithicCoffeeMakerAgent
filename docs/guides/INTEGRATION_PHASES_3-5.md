# PRIORITY 9 Integration Phases 3-5: Implementation Guide

**Status**: Phases 1-2 Complete; Phases 3-5 In Progress
**Estimated Total Time**: 5-8 hours remaining
**Owner**: code_developer (autonomous daemon)

---

## Overview

This guide details the three remaining phases needed to fully integrate activity tracking into the autonomous system:

1. **Phase 3**: Project Manager Integration (2-3 hours)
   - Modify chat_interface.py to display daily standups
   - Detect first chat of day
   - Generate and display standup reports

2. **Phase 4**: Daemon Integration (1-2 hours)
   - Modify daemon.py to log all work
   - Automatically capture commits, tests, PRs
   - Track priority start/completion

3. **Phase 5**: Testing & Polish (2-3 hours)
   - End-to-end testing
   - Performance optimization
   - Documentation updates

---

## Phase 3: Project Manager Integration

### Goal
Display daily standup report at the beginning of the first chat of the day.

### Requirements
1. Detect when it's a new day (first chat after midnight or 12+ hours since last chat)
2. Generate standup for yesterday
3. Display standup before chat starts
4. Track last chat timestamp for detection

### Implementation Locations

**File 1**: `coffee_maker/cli/chat_interface.py` (or equivalent project_manager UI)

```python
# At the top of the file
from coffee_maker.autonomous.standup_generator import StandupGenerator
from datetime import date, timedelta
import json
from pathlib import Path

# Add to chat initialization
def initialize_daily_standup():
    """Display standup at start of first chat of day."""

    # Load last chat timestamp
    last_chat_file = Path("data/last_chat_timestamp.json")

    try:
        if last_chat_file.exists():
            with open(last_chat_file, "r") as f:
                data = json.load(f)
                last_chat = datetime.fromisoformat(data["timestamp"])
        else:
            last_chat = datetime.now() - timedelta(hours=25)
    except:
        last_chat = datetime.now() - timedelta(hours=25)

    # Check if it's a new day (12+ hours or new calendar day)
    now = datetime.now()
    hours_since_chat = (now - last_chat).total_seconds() / 3600
    new_day = hours_since_chat >= 12 or now.date() > last_chat.date()

    if new_day:
        # Generate and display standup
        gen = StandupGenerator()
        yesterday = date.today() - timedelta(days=1)
        summary = gen.generate_daily_standup(yesterday)

        print("\n" + "=" * 70)
        print(summary.summary_text)
        print("=" * 70 + "\n")

    # Update timestamp
    last_chat_file.parent.mkdir(parents=True, exist_ok=True)
    with open(last_chat_file, "w") as f:
        json.dump({"timestamp": now.isoformat()}, f)

# Call at chat start
initialize_daily_standup()
```

### Test Script (Phase 3)

```python
# tests/integration/test_standup_display.py

def test_standup_displayed_at_chat_start():
    """Test that standup is displayed at chat start."""

    from coffee_maker.autonomous.standup_generator import StandupGenerator
    from datetime import date, timedelta

    gen = StandupGenerator()
    yesterday = date.today() - timedelta(days=1)
    summary = gen.generate_daily_standup(yesterday)

    # Verify standup contains expected sections
    assert "📊 Yesterday's Accomplishments:" in summary.summary_text
    assert "📈 Metrics:" in summary.summary_text
    assert "🎯 Next Steps:" in summary.summary_text

    # Verify metrics are calculated
    assert summary.metrics["total_activities"] >= 0
    assert "commits" in summary.metrics
```

### Success Criteria

- [ ] Standup displayed on first chat of day
- [ ] Standup includes yesterday's activities
- [ ] Metrics correctly calculated
- [ ] User can see professional formatted report
- [ ] No standup shown if <12 hours since last chat

---

## Phase 4: Daemon Integration

### Goal
Automatically log all code_developer activities during priority implementation.

### Requirements
1. Log priority start/completion
2. Capture git commits with metadata
3. Log test runs automatically
4. Track PR creation
5. Log errors and blockers

### Implementation Location

**File**: `coffee_maker/autonomous/daemon.py`

```python
# At the top of daemon.py
from coffee_maker.autonomous.activity_logger import ActivityLogger
import subprocess
import re

class DaemonWithActivityLogging:
    """Daemon that logs all development activities."""

    def __init__(self):
        self.logger = ActivityLogger()
        self.priority_count = 0

    def implement_priority(self, priority):
        """Implement a priority and log all activities."""

        try:
            # Log priority start
            self.logger.start_priority(priority.number, priority.name)
            print(f"Started {priority.number}: {priority.name}")

            # Create technical spec (if needed)
            if priority.needs_spec:
                spec = self.create_spec(priority)
                self.logger.log_file_changed(
                    file_path=spec.path,
                    change_type="created",
                    description=f"Technical specification for {priority.name}"
                )

            # Implement feature
            self.implement_code(priority)

            # Capture commits and log them
            self._log_recent_commits(priority)

            # Run tests
            test_result = self.run_tests()
            if test_result:
                self.logger.log_test_run(
                    passed=test_result.passed,
                    failed=test_result.failed,
                    skipped=test_result.skipped,
                    duration_seconds=test_result.duration,
                    test_framework="pytest"
                )

            # Create PR
            pr = self.create_pull_request(priority)
            if pr:
                self.logger.log_pr_created(
                    pr_number=pr.number,
                    pr_title=pr.title,
                    pr_url=pr.url,
                    branch=priority.branch
                )

            # Log completion
            self.logger.complete_priority(
                priority.number,
                success=True,
                summary=f"Successfully implemented {priority.name}"
            )

            self.priority_count += 1

        except Exception as e:
            # Log error
            self.logger.log_error(
                error_message=str(e),
                error_type=type(e).__name__,
                is_blocking=True
            )

            self.logger.complete_priority(
                priority.number,
                success=False,
                summary=f"Failed: {str(e)}"
            )

            raise

    def _log_recent_commits(self, priority, count=5):
        """Log recent commits for this priority."""

        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%H|%s|%an"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return

            # Parse commits
            commits = result.stdout.strip().split("\n")
            for commit_line in reversed(commits):  # Oldest first
                if not commit_line:
                    continue

                sha, message, author = commit_line.split("|", 2)

                # Get diff stats
                diff_result = subprocess.run(
                    ["git", "show", sha, "--shortstat"],
                    capture_output=True,
                    text=True
                )

                # Parse file/line changes
                files_changed = 0
                lines_added = 0
                lines_removed = 0

                if diff_result.returncode == 0:
                    # Example: "5 files changed, 250 insertions(+), 30 deletions(-)"
                    match = re.search(r"(\d+) files? changed", diff_result.stdout)
                    if match:
                        files_changed = int(match.group(1))

                    match = re.search(r"(\d+) insertions?", diff_result.stdout)
                    if match:
                        lines_added = int(match.group(1))

                    match = re.search(r"(\d+) deletions?", diff_result.stdout)
                    if match:
                        lines_removed = int(match.group(1))

                # Log commit
                self.logger.log_commit(
                    message=message[:200],
                    files_changed=files_changed,
                    lines_added=lines_added,
                    lines_removed=lines_removed,
                    commit_hash=sha
                )

        except Exception as e:
            self.logger.log_error(
                f"Failed to log commits: {str(e)}",
                "CommitLoggingError",
                is_blocking=False
            )

    def run_tests(self):
        """Run tests and return results."""

        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse test output
            passed = len(re.findall(r"PASSED", result.stdout))
            failed = len(re.findall(r"FAILED", result.stdout))
            skipped = len(re.findall(r"SKIPPED", result.stdout))

            class TestResult:
                def __init__(self, passed, failed, skipped):
                    self.passed = passed
                    self.failed = failed
                    self.skipped = skipped
                    self.duration = 0  # Could parse from output

            return TestResult(passed, failed, skipped)

        except Exception as e:
            self.logger.log_error(
                f"Test run failed: {str(e)}",
                "TestExecutionError",
                is_blocking=False
            )
            return None
```

### Integration Checklist

- [ ] Import ActivityLogger at top of daemon.py
- [ ] Create logger instance in daemon __init__
- [ ] Call start_priority at beginning of implement_priority()
- [ ] Log commits after git operations
- [ ] Log test results after pytest runs
- [ ] Log PR creation after GitHub operations
- [ ] Log errors in exception handlers
- [ ] Call complete_priority at end of implement_priority()
- [ ] All tests still pass
- [ ] No performance degradation

### Test Script (Phase 4)

```python
# tests/integration/test_daemon_activity_logging.py

def test_daemon_logs_activities():
    """Test that daemon logs activities during priority implementation."""

    from coffee_maker.autonomous.activity_db import ActivityDB
    from coffee_maker.autonomous.activity_logger import ActivityLogger
    from datetime import date

    db = ActivityDB()
    logger = ActivityLogger(db=db)

    # Simulate priority work
    logger.start_priority("TEST.1", "Test Priority")
    logger.log_commit(message="Test commit", files_changed=1, lines_added=10)
    logger.log_test_run(passed=5, failed=0)
    logger.complete_priority("TEST.1", success=True)

    # Verify activities logged
    activities = db.get_activities(priority_number="TEST.1", limit=100)
    assert len(activities) >= 4  # start + commit + test + complete

    # Verify priority context
    assert all(a.priority_number == "TEST.1" for a in activities)
```

---

## Phase 5: Testing & Polish

### Goal
Ensure all functionality works together in production scenarios.

### Testing Strategy

#### 1. Unit Tests (Already Complete)
- ActivityDB: 30+ tests ✅
- ActivityLogger: 10+ tests ✅
- StandupGenerator: 10+ tests ✅

#### 2. Integration Tests (Phase 5)

```python
# tests/integration/test_priority9_e2e.py

def test_complete_workflow():
    """Test complete PRIORITY 9 workflow."""

    from coffee_maker.autonomous.activity_logger import ActivityLogger
    from coffee_maker.autonomous.standup_generator import StandupGenerator
    from coffee_maker.autonomous.activity_db import ActivityDB
    from datetime import date
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.db")
        db = ActivityDB(db_path=db_path)
        logger = ActivityLogger(db=db)

        # Simulate full day
        logger.start_priority("1", "Feature A")

        for i in range(3):
            logger.log_commit(
                message=f"Commit {i}",
                files_changed=1,
                lines_added=50,
                commit_hash=f"abc{i}"
            )

        logger.log_test_run(passed=20, failed=0)
        logger.complete_priority("1", success=True)

        logger.start_priority("2", "Feature B")
        logger.log_commit(message="Commit B", files_changed=2, lines_added=100)
        logger.log_test_run(passed=25, failed=0)
        logger.log_pr_created(1, "Feature B PR", "http://example.com", "feature-b")
        logger.complete_priority("2", success=True)

        # Generate standup
        gen = StandupGenerator()
        summary = gen.generate_daily_standup(date.today())

        # Verify
        assert summary.metrics["total_activities"] >= 10
        assert summary.metrics["commits"] >= 4
        assert summary.metrics["test_runs"] >= 2
        assert summary.metrics["prs_created"] >= 1
        assert summary.metrics["priorities_completed"] >= 2
        assert "Feature A" in summary.summary_text or "commit" in summary.summary_text.lower()
```

#### 3. Performance Tests

```python
# tests/performance/test_activity_tracking_performance.py

def test_activity_logging_performance():
    """Ensure activity logging doesn't slow down daemon."""

    from coffee_maker.autonomous.activity_logger import ActivityLogger
    import time

    logger = ActivityLogger()
    logger.start_priority("PERF", "Performance Test")

    # Log 100 commits
    start = time.time()
    for i in range(100):
        logger.log_commit(
            message=f"Commit {i}",
            files_changed=2,
            lines_added=50,
            commit_hash=f"sha{i:06d}"
        )
    elapsed = time.time() - start

    # Should be fast (< 1 second for 100 commits)
    assert elapsed < 1.0, f"Logging too slow: {elapsed:.2f}s"

    logger.complete_priority("PERF", success=True)
```

### Performance Optimization Checklist

- [ ] ActivityDB queries use indices efficiently
- [ ] No N+1 query problems
- [ ] Batch operations where possible
- [ ] Claude API response cached appropriately
- [ ] Database size remains reasonable (<100MB/year)
- [ ] Standup generation <5 seconds

### Documentation Updates

```python
# Update /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/.claude/CLAUDE.md

## Recent Developments (Add to Important Context section)

4. **✅ PRIORITY 9 Phases 1-2 Complete**
   - ActivityDB: SQLite activity tracking with WAL mode
   - ActivityLogger: High-level logging interface
   - StandupGenerator: Claude-powered daily reports
   - 40+ tests passing, foundation ready
   - Phases 3-5 (integration) in progress

5. **⏳ PRIORITY 9 Phases 3-5 (In Progress)**
   - Phase 3: Chat integration (display daily standup)
   - Phase 4: Daemon integration (automatic logging)
   - Phase 5: Testing & polish
   - Estimated completion: 5-8 hours
```

---

## Success Criteria for Each Phase

### Phase 3 Success
- Standup displayed at first chat of day
- Metrics accurately calculated
- No performance impact
- User sees professional report

### Phase 4 Success
- All daemon work automatically logged
- Commits captured with metadata
- Tests tracked with results
- PRs recorded with numbers/URLs
- No impact on daemon speed

### Phase 5 Success
- 100+ integration tests passing
- Performance within budget (<5s overhead per day)
- Documentation complete
- Ready for production use

---

## Risk Mitigation

### Risk 1: Claude API Rate Limits
**Mitigation**: Implement caching and fallback template generation
- Already implemented in StandupGenerator

### Risk 2: Database Corruption
**Mitigation**: WAL mode + timeout handling
- Already implemented in ActivityDB

### Risk 3: Performance Impact
**Mitigation**: Batch operations, indexed queries
- Monitor in Phase 5 testing

### Risk 4: Integration Issues
**Mitigation**: Comprehensive integration tests before merging
- Covered in Phase 5

---

## Timeline Estimate

```
Phase 3 (Chat Integration):       2-3 hours
  - Modify chat_interface.py
  - Handle timestamp tracking
  - Display formatting

Phase 4 (Daemon Integration):     1-2 hours
  - Modify daemon.py
  - Add logging calls
  - Commit capture logic

Phase 5 (Testing & Polish):       2-3 hours
  - Integration tests
  - Performance validation
  - Documentation updates

Total:                            5-8 hours
```

---

## Deployment Strategy

### Rollout Plan

1. **Merge Phase 3**: Chat integration (low risk)
2. **Merge Phase 4**: Daemon integration (moderate risk)
3. **Merge Phase 5**: Testing & polish (no risk)

### Rollback Plan

If issues occur:
1. Revert last commit: `git revert HEAD`
2. Create issue in ROADMAP
3. Investigate problem
4. Create fix branch and retry

---

## Next Steps

1. **Today**: Complete Phase 1-2 demos (assistant working on this)
2. **Tomorrow**: Start Phase 3 implementation
3. **Day 3**: Phase 4 implementation
4. **Day 4**: Phase 5 testing and polish
5. **Day 5**: Merge and celebrate!

---

## Support & Questions

For questions during implementation:

1. Check this guide for context
2. Review unit tests for examples
3. Check `/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/docs/demos/priority-9-daily-standup-demo.md`
4. Run quickstart examples

**All components are designed to work together seamlessly!** 🚀
