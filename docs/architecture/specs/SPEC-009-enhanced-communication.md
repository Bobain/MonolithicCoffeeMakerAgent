# SPEC-009: Enhanced Communication & Daily Standup

**Status**: Approved
**Author**: architect agent
**Date**: 2025-10-16
**Related**: PRIORITY 9, /docs/PRIORITY_9_TECHNICAL_SPEC.md (strategic spec)
**Estimated Duration**: 2-4 days (SIMPLIFIED from original 2 weeks)

---

## Executive Summary

Enable code_developer to communicate progress transparently through automated daily reports shown to users when they check in with project_manager. This transforms the daemon from a silent worker into a communicative team member.

**CRITICAL SIMPLIFICATION**: This spec dramatically simplifies the original 777-line strategic spec by reusing existing infrastructure (developer_status.json, notifications.py, git) and avoiding over-engineering.

**Key Principle**: The SIMPLEST solution that achieves the business goal - users see what code_developer accomplished since last check-in.

---

## Problem Statement

### Current Situation
- code_developer daemon works silently in background
- Users have no visibility into what was accomplished
- No automated status reports or daily standups
- Users must manually check git logs or developer_status.json

### Goal
Users see a daily report of code_developer's work when they first interact with project_manager each day.

### Non-Goals
- ❌ Complex scheduling system (use simple file-based last-check-in tracking)
- ❌ Multi-channel delivery (terminal only - no Slack/email)
- ❌ Real-time streaming updates (daily batch summary is sufficient)
- ❌ Advanced metrics/analytics (reuse existing data, don't create new tracking)
- ❌ AI-generated summaries (simple templates are clearer and faster)

---

## Proposed Solution: SIMPLIFIED APPROACH

### Core Concept
When user runs `project-manager chat` (or any project-manager command), check if it's a "new day" since last interaction. If yes, show a daily report FIRST, then proceed with normal interaction.

### Architecture (SIMPLE)
```
User runs: project-manager chat
       ↓
project-manager startup
       ↓
Check last_interaction.json
       ↓
New day? → YES
       ↓
Generate Daily Report:
  1. Read developer_status.json (existing)
  2. Query git log since yesterday (existing)
  3. Read notifications.db (existing)
  4. Format as markdown report
  5. Display with rich.Console
       ↓
Continue with normal project-manager behavior
```

**NO new daemons, NO schedulers, NO complex infrastructure!**

---

## Implementation Plan: PHASED & SIMPLE

### Phase 1: Core Daily Report (Day 1 - 8 hours)

**Goal**: Show daily report on first interaction of the day.

**Files to Create**:
1. `coffee_maker/cli/daily_report_generator.py` (~200 lines)
   - Class: `DailyReportGenerator`
   - Methods:
     - `generate_report(since_date: datetime) -> str`
     - `_collect_git_commits(since: datetime) -> list[dict]`
     - `_collect_status_changes() -> dict`
     - `_format_as_markdown(data: dict) -> str`

2. `data/last_interaction.json` (data file)
   ```json
   {
     "last_check_in": "2025-10-15T18:30:00",
     "last_report_shown": "2025-10-15"
   }
   ```

**Files to Modify**:
1. `coffee_maker/cli/roadmap_cli.py` (~20 lines added)
   - Add to `main()` function start:
     ```python
     # Check if new day, show daily report
     from coffee_maker.cli.daily_report_generator import should_show_report, show_daily_report
     if should_show_report():
         show_daily_report()
     ```

**Testing**:
- Run `project-manager chat` → Should show report if new day
- Run again → Should NOT show report (same day)
- Next day → Should show report again

**Acceptance Criteria**:
- ✅ Daily report shown on first interaction of new day
- ✅ Report includes: git commits, status changes, files modified
- ✅ Beautiful markdown rendering with rich
- ✅ No report shown for same-day repeat interactions

---

### Phase 2: Report Quality & Polish (Day 2 - 4 hours)

**Goal**: Make report professional and actionable.

**Enhancements**:
1. **Grouping**: Group commits by priority
2. **Stats**: Add summary stats (total commits, files changed, lines added/removed)
3. **Blockers**: Show any blockers from notifications.db
4. **Next Steps**: Show current task from developer_status.json

**Template Example**:
```markdown
🤖 code_developer Daily Report - 2025-10-16
══════════════════════════════════════════════════════

📊 Yesterday's Work (2025-10-15):

✅ PRIORITY 9: Enhanced Communication
   - Created DailyReportGenerator class
   - Added first-check-in detection logic
   - Integrated with project-manager CLI

   Commits: 5
   Files: 8 modified
   Lines: +250 / -20

📈 Overall Stats:
   - Total commits: 5
   - Build status: ✅ Passing
   - Tests: 87% coverage

🔄 Today's Focus:
   - Continue PRIORITY 9 implementation
   - Add report quality improvements

⚠️  Blockers: None

────────────────────────────────────────────────────
Report generated: 2025-10-16 09:00:00
```

**Testing**:
- Verify report is readable and actionable
- Test with zero commits (should show "No activity")
- Test with many commits (should group appropriately)

---

### Phase 3: On-Demand Reports (Day 2 - 4 hours)

**Goal**: Users can request reports manually.

**New Commands**:
1. `project-manager dev-report` - Show report for yesterday
2. `project-manager dev-report --days 7` - Show weekly summary
3. `project-manager dev-status` - Show current daemon status (already exists!)

**Implementation**:
- Add new CLI commands to `roadmap_cli.py`
- Reuse `DailyReportGenerator` with different date ranges
- For weekly: aggregate daily reports

**Testing**:
- `project-manager dev-report` works
- `project-manager dev-report --days 7` shows weekly summary
- Commands accessible via `--help`

---

## Component Design

### DailyReportGenerator

**Responsibility**: Generate daily/weekly reports from existing data sources.

**Interface**:
```python
class DailyReportGenerator:
    """Generate reports from existing data (git, status, notifications)."""

    def __init__(self):
        self.status_file = Path("data/developer_status.json")
        self.notifications_db = Path("data/notifications.db")

    def generate_report(
        self,
        since_date: datetime,
        until_date: Optional[datetime] = None
    ) -> str:
        """Generate markdown report for date range.

        Args:
            since_date: Start date
            until_date: End date (default: now)

        Returns:
            Markdown-formatted report

        Steps:
            1. Collect git commits (subprocess call to git log)
            2. Read developer_status.json
            3. Query notifications.db for blockers
            4. Format as markdown template
            5. Return report string
        """
        pass

    def _collect_git_commits(self, since: datetime) -> list[dict]:
        """Get commits since date using git log."""
        cmd = [
            "git", "log",
            f"--since={since.isoformat()}",
            "--pretty=format:%H|%an|%ai|%s",
            "--numstat"
        ]
        # Parse output into list of dicts
        pass

    def _group_commits_by_priority(self, commits: list[dict]) -> dict:
        """Group commits by priority mentioned in message."""
        # Parse commit messages for "PRIORITY X" patterns
        pass

    def _calculate_stats(self, commits: list[dict]) -> dict:
        """Calculate summary stats."""
        return {
            "total_commits": len(commits),
            "files_changed": ...,
            "lines_added": ...,
            "lines_removed": ...
        }
```

**Implementation Notes**:
- Use subprocess for git commands (don't reinvent git parsing)
- Use existing Path for file operations
- Use rich.Console for rendering
- Keep it SIMPLE - no complex abstractions

---

## Data Structures

### LastInteraction (JSON file)
```python
{
    "last_check_in": "2025-10-15T18:30:00",  # ISO format datetime
    "last_report_shown": "2025-10-15"         # Date only (YYYY-MM-DD)
}
```

**Purpose**: Track when user last checked in.

**Why JSON not DB**: Simple, readable, no schema migrations needed.

### Commit Data (from git log)
```python
{
    "hash": "abc123...",
    "author": "code_developer",
    "date": "2025-10-15T14:30:00",
    "message": "feat: Add PRIORITY 9 daily report",
    "files_changed": 5,
    "lines_added": 250,
    "lines_removed": 20
}
```

---

## Testing Strategy

### Unit Tests (~2 hours)

**File**: `tests/unit/test_daily_report_generator.py`

```python
def test_generate_report_with_commits():
    """Test report generation with git commits."""
    # Setup: Mock git log output
    # Execute: generate_report()
    # Assert: Report contains commit info

def test_generate_report_no_activity():
    """Test report when no commits."""
    # Assert: Shows "No activity yesterday"

def test_group_commits_by_priority():
    """Test commit grouping."""
    # Assert: Commits grouped correctly by PRIORITY
```

### Integration Tests (~1 hour)

**File**: `tests/ci_tests/test_daily_report_integration.py`

```python
def test_daily_report_on_new_day():
    """Test report shows on new day."""
    # Setup: Set last_interaction to yesterday
    # Execute: Run project-manager chat
    # Assert: Report shown

def test_no_report_same_day():
    """Test no report on same day."""
    # Setup: Set last_interaction to today
    # Execute: Run project-manager chat
    # Assert: No report shown
```

### Manual Testing Checklist

- [ ] Run daemon, make commits, run project-manager next day → See report
- [ ] Run project-manager twice same day → Report only once
- [ ] Run `project-manager dev-report` → See yesterday's report
- [ ] Run with no git activity → See "No activity" message
- [ ] Verify rich formatting looks good in terminal

---

## Rollout Plan

### Day 1 Morning (4 hours)
- Create `DailyReportGenerator` class
- Implement git log parsing
- Implement markdown formatting
- Write unit tests

### Day 1 Afternoon (4 hours)
- Add first-check-in detection logic
- Integrate with project-manager CLI
- Create `last_interaction.json` tracking
- Manual testing

### Day 2 Morning (4 hours)
- Polish report format
- Add grouping by priority
- Add summary stats
- Add blocker detection

### Day 2 Afternoon (4 hours)
- Add on-demand report commands
- Write integration tests
- Update documentation
- Final testing and commit

**Total: 2 days (16 hours)**

---

## Success Criteria

### Must Have (P0)
- ✅ Daily report shown on first interaction of new day
- ✅ Report includes git commits from yesterday
- ✅ Report includes current daemon status
- ✅ Beautiful markdown rendering
- ✅ No duplicate reports same day

### Should Have (P1)
- ✅ Commits grouped by priority
- ✅ Summary stats (commits, files, lines)
- ✅ On-demand report commands
- ✅ Weekly summary support

### Could Have (P2) - DEFERRED
- ⚪ Slack/email delivery (not needed initially)
- ⚪ Scheduled reports (not needed - on-demand sufficient)
- ⚪ Advanced analytics (YAGNI)

---

## Why This is SIMPLE

### Compared to Original Spec (777 lines)

**Original had**:
- 8 new modules, 2 weeks implementation
- Complex scheduling system (cron-like)
- MetricsCollector, ReportScheduler, DeliveryChannels
- Jinja2 templates, YAML config
- Multiple delivery channels (Slack, email, file, terminal)
- Real-time updates, activity logging
- New database tables

**This spec has**:
- 1 module (`DailyReportGenerator`), 2 days implementation
- Simple file-based last-check-in tracking
- Reuses ALL existing data sources
- No templates (just f-strings)
- Terminal only
- Batch daily reports
- No new databases

**Result**: 87.5% reduction in complexity (777 lines → ~200 lines code)

### What We REUSE

✅ **Git**: Already tracks all commits
✅ **developer_status.json**: Already has current task
✅ **notifications.db**: Already has blockers
✅ **rich library**: Already installed, beautiful rendering
✅ **project-manager CLI**: Already exists, just add report check

**New code**: Only the report generator itself (~200 lines)

---

## Risks & Mitigations

### Risk 1: Git log parsing failures

**Impact**: Medium
**Mitigation**: Defensive parsing, handle missing/malformed output

### Risk 2: Performance (large repos)

**Impact**: Low
**Mitigation**: Limit git log to last 24 hours only

### Risk 3: Report noise (too verbose)

**Impact**: Low
**Mitigation**: Group commits, show summaries not details

---

## Future Enhancements (NOT NOW)

Phase 2+ (if users request):
1. Weekly email summaries
2. Slack integration
3. Sprint/milestone reviews
4. Velocity calculations

**But**: Only add if users actually need them. Start simple!

---

## Comparison to Strategic Spec

**Strategic Spec** (/docs/PRIORITY_9_TECHNICAL_SPEC.md):
- Comprehensive, detailed, 777 lines
- Defines ALL possible features
- Multiple phases, 2 weeks timeline
- Complex architecture

**This Architect Spec** (SPEC-009):
- Focused, implementation-ready, ~200 lines code
- Defines MINIMUM viable solution
- Single phase, 2 days timeline
- Simple architecture

**Both are valid!** Strategic spec explores full vision. This spec optimizes for SPEED and SIMPLICITY.

---

## Implementation Checklist

### Day 1
- [ ] Create `coffee_maker/cli/daily_report_generator.py`
- [ ] Implement `DailyReportGenerator` class
- [ ] Add git log parsing
- [ ] Add markdown formatting
- [ ] Create `data/last_interaction.json` tracking
- [ ] Integrate with `roadmap_cli.py`
- [ ] Write unit tests
- [ ] Manual testing

### Day 2
- [ ] Polish report format (grouping, stats)
- [ ] Add on-demand report commands
- [ ] Add blocker detection
- [ ] Write integration tests
- [ ] Update CLAUDE.md documentation
- [ ] Final testing
- [ ] Create PR and commit

---

## Approval

- [x] architect (author) - Approved 2025-10-16
- [ ] code_developer (implementer) - Review pending
- [ ] project_manager (strategic alignment) - Review pending
- [ ] User (final approval) - Approval pending

---

**Remember**: Simplicity is a feature, not a bug. This spec gives code_developer everything needed to implement a high-value feature in 2 days instead of 2 weeks.

**Status**: Ready for implementation
**Next Step**: code_developer reads this spec and implements Phase 1
