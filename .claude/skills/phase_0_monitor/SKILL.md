---
description: Monitor Phase 0 progress across all parallel work streams
time_savings: 17-27 minutes per check
---

# Phase 0 Monitor Skill

## What This Skill Does

Tracks real-time progress of Phase 0 implementation across all parallel work streams (code_developer and architect). Detects blockers, alerts on delays, generates comprehensive status reports.

**Key Capabilities**:
- Check git commits since last update
- Parse commit messages for completed user stories
- Read developer_status.json for active work
- Run test suite to verify passing status
- Update PHASE_0_PROGRESS_TRACKER.md automatically
- Detect blockers (stalled work, failing tests, dependency issues)
- Generate daily status reports

## When To Use

**Automated Schedule**:
- Every 6 hours (via cron or scheduled task)
- Before daily standup meetings

**Manual Triggers**:
- User asks "What's the status?"
- User asks "Are we on track?"
- User asks "Any blockers?"
- Before weekly retrospectives

## Time Savings

**Before** (Manual monitoring):
- Git commit review: 5-7 min
- Status file parsing: 3-5 min
- Test suite check: 2-3 min
- Blocker detection: 4-6 min
- Report generation: 3-6 min
- Total: 17-27 minutes per check

**After** (Automated skill):
- Execution time: <2 minutes
- Savings: 15-25 minutes per check
- Monthly savings: 10-15 hours (assuming 4 checks/day)

## Instructions

### Step 1: Check Git Activity

```bash
# Check commits since last check (stored in data/phase_0_monitor/last_check.txt)
LAST_CHECK=$(cat data/phase_0_monitor/last_check.txt 2>/dev/null || echo "24 hours ago")

git log --oneline --since="$LAST_CHECK" --all --author="Claude" > data/phase_0_monitor/recent_commits.txt

# Parse for user story completions
grep -E "US-[0-9]{3}" data/phase_0_monitor/recent_commits.txt | \
  grep -E "(feat|fix|docs):" > data/phase_0_monitor/completed_stories.txt
```

### Step 2: Parse Developer Status

```bash
# Read current developer status
python scripts/status_parser.py data/agent_status/developer_status.json > data/phase_0_monitor/current_status.json

# Extract active work
# {
#   "agent": "code_developer",
#   "user_story": "US-091",
#   "progress": "60%",
#   "time_elapsed": "2h 15m",
#   "last_update": "2025-10-18T15:30:00"
# }
```

### Step 3: Run Test Suite Check

```bash
# Quick test suite check (unit tests only for speed)
pytest tests/unit/ --quiet --exitfirst > data/phase_0_monitor/test_results.txt 2>&1
TEST_STATUS=$?

if [ $TEST_STATUS -eq 0 ]; then
  echo "PASSING" > data/phase_0_monitor/test_status.txt
else
  echo "FAILING" > data/phase_0_monitor/test_status.txt
  echo "BLOCKER: Tests failing - check data/phase_0_monitor/test_results.txt"
fi
```

### Step 4: Detect Blockers

```bash
python scripts/blocker_detector.py
```

**Blocker Detection Logic** (in blocker_detector.py):

```python
# Check 1: Work stalled >12 hours?
if time_since_last_commit > 12 hours and status == "in_progress":
    blocker = {
        "type": "STALLED_WORK",
        "user_story": current_us,
        "duration": time_stalled,
        "severity": "CRITICAL"
    }

# Check 2: Tests failing?
if test_status == "FAILING":
    blocker = {
        "type": "TEST_FAILURES",
        "severity": "CRITICAL",
        "details": parse_pytest_output()
    }

# Check 3: Dependency blocking progress?
# Example: US-092 depends on US-091, but US-091 not complete
if us_blocked_by_dependency():
    blocker = {
        "type": "DEPENDENCY_BLOCK",
        "blocked_us": "US-092",
        "blocking_us": "US-091",
        "severity": "HIGH"
    }

# Check 4: CFR-007 violations during migration?
if cfr007_violations > 0:
    blocker = {
        "type": "CFR007_VIOLATION",
        "count": violations,
        "severity": "MEDIUM"
    }
```

### Step 5: Update Progress Tracker

```bash
python scripts/update_progress_tracker.py
```

**Updates** `docs/roadmap/PHASE_0_PROGRESS_TRACKER.md`:
- Last Updated timestamp
- Overall progress percentage
- Time spent and remaining
- User story status changes
- Velocity metrics
- Active blockers
- Weekly summary

### Step 6: Generate Status Report

```bash
python scripts/report_generator.py > docs/roadmap/PHASE_0_DAILY_STATUS_$(date +%Y-%m-%d).md
```

**Report Format**:
```markdown
# Phase 0 Daily Status - YYYY-MM-DD

## Progress Summary
- Completed: X / 16 user stories (XX%)
- In Progress: Y user stories (code_developer: A, architect: B)
- Planned: Z user stories

## Completed Today
- US-XXX: [skill name] - [time spent]

## Active Work
- code_developer: US-XXX ([skill]) - XX% complete
- architect: US-XXX ([skill]) - XX% complete

## Blockers
- [List of blockers from Step 4]

## Velocity
- Stories/day: X.X (target: 0.8)
- On track for Week 4 completion: YES/NO

## Next 24 Hours
- code_developer: [Expected work]
- architect: [Expected work]
```

### Step 7: Alert on Critical Issues

```python
# If critical blockers detected, warn user
if critical_blockers:
    from coffee_maker.cli.ai_service import AIService
    service = AIService()

    for blocker in critical_blockers:
        service.warn_user(
            title=f"PHASE 0 BLOCKER: {blocker['type']}",
            message=blocker['description'],
            priority="critical",
            context=blocker
        )
```

## Scripts Required

### 1. scripts/status_parser.py

Parse developer_status.json and extract relevant info.

### 2. scripts/blocker_detector.py

Detect blockers using logic from Step 4.

### 3. scripts/update_progress_tracker.py

Update PHASE_0_PROGRESS_TRACKER.md with latest data.

### 4. scripts/report_generator.py

Generate daily status report from monitoring data.

### 5. scripts/git_monitor.py

Monitor git activity and parse commit messages.

## Data Directory Structure

```
data/phase_0_monitor/
├── last_check.txt           # Timestamp of last monitoring run
├── recent_commits.txt       # Git commits since last check
├── completed_stories.txt    # Parsed user story completions
├── current_status.json      # Developer status snapshot
├── test_results.txt         # Latest test run output
├── test_status.txt          # PASSING or FAILING
├── blockers.json            # Detected blockers
└── velocity_metrics.json    # Historical velocity data
```

## Success Criteria

- [ ] Monitoring runs every 6 hours automatically
- [ ] Blockers detected within 30 minutes of occurrence
- [ ] Progress tracker updated within 5 minutes of completion
- [ ] Daily status reports generated before 9am
- [ ] Critical blockers trigger immediate user warnings
- [ ] All monitoring data persisted for retrospectives

## Integration Points

- Cron job: `0 */6 * * * cd /path/to/project && poetry run phase-0-monitor`
- GitHub Actions: Run on push to roadmap branch
- Notification system: coffee_maker.cli.notifications
- Status tracking: coffee_maker.autonomous.developer_status

## Example Execution

```bash
# Manual execution
poetry run phase-0-monitor

# Output:
Checking git activity... 2 new commits found
Parsing developer status... code_developer working on US-091 (60% complete)
Running test suite... PASSING (127 tests)
Detecting blockers... 0 critical, 0 high, 1 medium
Updating progress tracker... Updated
Generating status report... Created docs/roadmap/PHASE_0_DAILY_STATUS_2025-10-18.md
Total time: 1m 23s

# Blockers detected
MEDIUM: US-091 progress at 60% for 6 hours (expected completion in 2-3 hours)
```

## Notes

- Monitor MUST be lightweight (<2 min execution)
- Use cached data where possible (git log --since)
- Avoid full codebase scans (use incremental updates)
- Priority: Accuracy > Speed (better to take 3 min and be accurate)
- Store historical data for trend analysis

---

**Maintained By**: project_manager agent
**Execution Frequency**: Every 6 hours + on-demand
**Dependencies**: git, pytest, python 3.11+, poetry
