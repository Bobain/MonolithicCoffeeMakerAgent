# Workflow Flaw Analysis: Potential Communication Breakdowns

**Date**: 2025-10-23
**Purpose**: Identify communication gaps, deadlocks, and DB vs file inconsistencies that could stall roadmap progress

---

## Executive Summary

This analysis identifies **7 critical workflow flaws** that could prevent roadmap progress:

1. ⚠️ **No notification when code_reviewer completes review** → architect doesn't know about issues
2. ⚠️ **No automatic roadmap status updates** → items stay in wrong status forever
3. ⚠️ **Mixed database/file usage** → data inconsistency and race conditions
4. ⚠️ **Missing project_manager notification processing** → notifications pile up unread
5. ⚠️ **No code_developer completion notification** → no one knows implementation is done
6. ⚠️ **Code review reports only in files** → not integrated with database workflow
7. ⚠️ **No polling/trigger mechanism** → agents don't know when to run

---

## 1. Communication Flow Analysis

### Current Agent Communication Paths

```
┌─────────────┐
│  architect  │ Creates specs → notifications table
└──────┬──────┘
       │
       ├─[notification: spec_complete]───→ project_manager (WHO PROCESSES?)
       │
       └─[notification: spec_approved]───→ project_manager (WHO PROCESSES?)

┌──────────────────┐
│ project_manager  │ Reads notifications (WHEN?)
└────────┬─────────┘
         │
         └─[database: links spec_id to roadmap] → unified_roadmap_specs.db

┌─────────────────┐
│ code_developer  │ Polls database for next task
└────────┬────────┘
         │
         ├─[database: get_next_implementation_task()]
         │
         └─[database: request_review] → commit_reviews table

┌────────────────┐
│ code_reviewer  │ Polls for pending reviews
└────────┬───────┘
         │
         ├─[database: claim_review]
         │
         └─[FILE: write review report] ← NOT IN DATABASE! ⚠️

┌─────────────┐
│  architect  │ Reads review files (WHEN? HOW DOES HE KNOW?)
└─────────────┘
```

### Critical Gaps Identified

#### Gap 1: code_reviewer → architect (No Database Notification)
**Problem**: code_reviewer writes review reports to `docs/code-reviews/REVIEW-*.md` but doesn't notify architect in database.

**Impact**:
- architect doesn't know reviews exist
- Reviews might sit unread for days
- Issues never get addressed
- Quality problems persist

**Current State**:
```python
# code_reviewer completes review
review_skill.complete_review(review_id, "changes_requested", feedback)
# Writes to commit_reviews table with review_status
# But NO notification created for architect! ⚠️
```

**Missing**:
```python
# SHOULD DO:
if status == "changes_requested":
    # Create notification for architect
    notification_db.create_notification(
        target_agent="architect",
        source_agent="code_reviewer",
        notification_type="review_complete_changes_needed",
        item_id=spec_id,
        message=f"Review for {spec_id} requires changes: {feedback}"
    )
```

---

#### Gap 2: code_developer → project_manager (No Completion Notification)
**Problem**: When code_developer completes implementation, no one is notified.

**Impact**:
- Roadmap status never updates to "Complete"
- project_manager doesn't know work is done
- DoD verification never happens
- Items stuck in "In Progress" forever

**Current State**:
```python
# code_developer finishes implementation
# Requests code review
review_skill.request_review(commit_sha, spec_id, ...)
# But NO notification that implementation is COMPLETE! ⚠️
```

**Missing**:
```python
# SHOULD DO:
# After successful tests and commit
notification_db.create_notification(
    target_agent="project_manager",
    source_agent="code_developer",
    notification_type="implementation_complete",
    item_id=roadmap_item_id,
    message=f"Implementation complete for {roadmap_item_id}. Ready for DoD verification."
)
```

---

#### Gap 3: project_manager Notification Processing (Not Implemented)
**Problem**: Notifications pile up in database but no agent processes them.

**Impact**:
- architect notifications never acted on
- Spec links never created in roadmap
- Database fills with unprocessed notifications
- No workflow automation happens

**Current State**:
```sql
-- Notifications table exists
SELECT * FROM notifications WHERE status = 'pending';
-- Returns rows, but WHO READS THEM? ⚠️
```

**Missing**:
- No `project_manager` daemon or scheduled task
- No notification polling mechanism
- No automatic roadmap updates

**Needed**:
```python
# project_manager should have:
def process_pending_notifications():
    """Process all pending notifications."""
    db = get_unified_database()

    notifications = get_pending_notifications(target_agent="project_manager")

    for notif in notifications:
        if notif['notification_type'] == 'spec_complete':
            # Link spec to roadmap
            link_spec_to_roadmap(notif['item_id'], notif['spec_id'])
        elif notif['notification_type'] == 'implementation_complete':
            # Update roadmap status
            update_roadmap_status(notif['item_id'], "✅ Complete")

        mark_notification_processed(notif['id'])
```

---

## 2. Database vs File Usage Inconsistency

### Database-Only (Correct Pattern ✅)
- `technical_specs` table - specs stored in database
- `roadmap_items` table - roadmap in database
- `commit_reviews` table - review tracking in database
- `notifications` table - inter-agent messages

### File-Only (Problematic Pattern ⚠️)
- `docs/code-reviews/REVIEW-*.md` - review reports as files
- `docs/code-reviews/INDEX.md` - review index as file
- No database link between review report and commit_reviews entry

### Problems with Mixed Approach

1. **Race Conditions**
   - File written but database not updated
   - Database updated but file not written
   - Inconsistent state

2. **No Query Ability**
   - Can't JOIN review reports with specs
   - Can't find "all reviews with changes_requested for SPEC-115"
   - Must scan files manually

3. **No Notification Integration**
   - Files don't trigger notifications
   - architect doesn't know reviews exist
   - Breaks automation

### Recommended Fix

**Option A: Store review reports in database**
```sql
CREATE TABLE review_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_review_id INTEGER NOT NULL,
    spec_id TEXT,
    quality_score INTEGER,
    issues_found TEXT,  -- JSON array
    recommendations TEXT,
    full_report TEXT,  -- Full markdown content
    created_at TEXT NOT NULL,
    FOREIGN KEY (commit_review_id) REFERENCES commit_reviews(id)
);
```

**Option B: Add database entries for file-based reviews**
```sql
-- Link existing file reviews to database
ALTER TABLE commit_reviews ADD COLUMN report_file_path TEXT;
ALTER TABLE commit_reviews ADD COLUMN quality_score INTEGER;
ALTER TABLE commit_reviews ADD COLUMN needs_architect_review BOOLEAN DEFAULT 0;
```

---

## 3. Missing Workflow Triggers

### Problem: No Event-Driven Architecture

Current design requires **polling**:
- code_developer polls for `get_next_implementation_task()`
- code_reviewer polls for `get_pending_reviews()`
- project_manager would need to poll for `get_pending_notifications()`

**Issues**:
- Wasted CPU cycles
- Delayed responses (poll interval)
- No real-time workflow

### Recommended: Event-Driven Notifications

**Option A: File-based triggers** (simple)
```bash
# When architect completes spec
touch data/events/spec_complete_SPEC-115.trigger

# project_manager watches directory
inotifywait -m data/events/ | while read event; do
    process_event "$event"
done
```

**Option B: Database triggers** (better)
```sql
CREATE TRIGGER notify_spec_complete
AFTER UPDATE ON technical_specs
WHEN NEW.status = 'complete' AND OLD.status != 'complete'
BEGIN
    INSERT INTO notifications (
        target_agent, source_agent, notification_type,
        item_id, message, status, created_at
    ) VALUES (
        'project_manager', 'architect', 'spec_complete',
        NEW.id,
        'Spec ' || NEW.id || ' is complete and ready to link to roadmap',
        'pending',
        datetime('now')
    );
END;
```

**Option C: Agent orchestrator** (most robust)
```python
# New: orchestrator daemon
class WorkflowOrchestrator:
    def run(self):
        while True:
            # Check for pending notifications
            self.process_notifications()

            # Check for stale reviews/specs
            self.recover_stale_items()

            # Check for ready-to-implement tasks
            self.notify_code_developer_if_tasks_ready()

            time.sleep(60)  # Check every minute
```

---

## 4. Deadlock Scenarios

### Deadlock 1: Spec Never Linked to Roadmap

**Sequence**:
1. architect creates SPEC-116 for PRIORITY-27
2. Notification created: `spec_complete`
3. project_manager never processes notification ❌
4. Roadmap item PRIORITY-27 has `spec_id = NULL`
5. code_developer queries `get_next_implementation_task()`
6. Query requires `spec_id IS NOT NULL` → PRIORITY-27 not found
7. **Task never implemented despite having complete spec!**

**Root Cause**: Missing notification processing loop

---

### Deadlock 2: Review Never Read by architect

**Sequence**:
1. code_developer implements SPEC-116
2. code_reviewer finds issues, marks `changes_requested`
3. Review written to file `docs/code-reviews/REVIEW-abc123.md`
4. No notification sent to architect ❌
5. architect never reads review file
6. Issues never addressed
7. code_developer moves to next task
8. **Bug ships to production!**

**Root Cause**: File-based communication without notification

---

### Deadlock 3: Implementation Complete but Status Never Updates

**Sequence**:
1. code_developer completes PRIORITY-27 implementation
2. All tests pass
3. Code committed and reviewed
4. No notification of completion ❌
5. Roadmap still shows "🔄 In Progress"
6. project_manager thinks work is ongoing
7. DoD verification never triggered
8. **Task appears incomplete forever**

**Root Cause**: No completion notification mechanism

---

## 5. Data Consistency Issues

### Issue 1: Roadmap.md vs Database Divergence

**If both exist**:
- `docs/roadmap/ROADMAP.md` (file)
- `roadmap_items` table (database)

**Which is source of truth?**
- If database → must regenerate file
- If file → must parse and update database
- If both → risk of divergence

**Current Approach**: Database is source of truth (CFR-015)

**Potential Problems**:
- Old ROADMAP.md files might exist
- Scripts might read wrong source
- Agents might write to wrong location

**Verification Needed**:
```bash
# Check if file-based roadmap code still exists
grep -r "docs/roadmap/ROADMAP.md" coffee_maker/ --include="*.py"
```

---

### Issue 2: Spec Files vs Database

**Similar problem**:
- `docs/architecture/specs/SPEC-*.md` (files, backup only)
- `technical_specs` table (database, source of truth)

**Risk**: Agent reads file instead of database

**Mitigation**: Clear in code comments, but needs enforcement

---

## 6. Missing Workflows

### 6.1 DoD Verification Workflow

**Problem**: No automated DoD verification flow

**Needed**:
```
code_developer completes work
    ↓
Notification: implementation_complete
    ↓
project_manager receives notification
    ↓
project_manager triggers Puppeteer tests
    ↓
If DoD met: Update roadmap status to "✅ Complete"
If DoD failed: Create notification for code_developer to fix
```

**Currently**: Manual process, no automation

---

### 6.2 Review Feedback Loop

**Problem**: No closed-loop for code review issues

**Needed**:
```
code_reviewer finds issues
    ↓
Notification: review_changes_requested
    ↓
architect receives notification
    ↓
architect reads review report (from database or file)
    ↓
architect updates spec or creates bug ticket
    ↓
Notification: spec_updated
    ↓
code_developer re-implements
```

**Currently**: code_reviewer writes file, then nothing happens

---

### 6.3 Stuck Task Recovery

**Problem**: No mechanism to detect permanently stuck tasks

**Needed**:
```python
def detect_stuck_tasks():
    """Find roadmap items that haven't progressed in >7 days."""

    stuck = db.query("""
        SELECT * FROM roadmap_items
        WHERE status IN ('🔄 In Progress', '📝 Planned')
        AND datetime(updated_at) < datetime('now', '-7 days')
    """)

    for item in stuck:
        # Notify project_manager
        create_notification(
            target_agent="project_manager",
            notification_type="task_stuck",
            item_id=item['id'],
            message=f"Task {item['id']} hasn't progressed in 7+ days"
        )
```

---

## 7. Recommendations

### Priority 1: Critical (Blocks All Progress)

1. **Implement project_manager notification processor**
   ```python
   # New: coffee_maker/autonomous/notification_processor.py
   class NotificationProcessor:
       def process_all_pending(self):
           """Process all pending notifications for project_manager."""
   ```

2. **Add code_reviewer → architect notification**
   ```python
   # In review_tracking_skill.complete_review()
   if status == "changes_requested":
       self._notify_architect_of_issues(review_id, spec_id, feedback)
   ```

3. **Add code_developer → project_manager completion notification**
   ```python
   # After successful implementation
   self._notify_implementation_complete(roadmap_item_id, commit_sha)
   ```

### Priority 2: High (Improves Reliability)

4. **Store review reports in database**
   - Add `review_reports` table
   - Link to `commit_reviews`
   - Enable querying and notifications

5. **Add workflow orchestrator daemon**
   - Polls for notifications every 60 seconds
   - Processes project_manager notifications
   - Resets stale items
   - Detects stuck tasks

6. **Add database triggers for auto-notifications**
   - Trigger on spec complete
   - Trigger on review complete
   - Trigger on status changes

### Priority 3: Medium (Prevents Issues)

7. **Add roadmap consistency checker**
   ```python
   def verify_roadmap_consistency():
       """Check for orphaned specs, missing links, etc."""
   ```

8. **Add workflow monitoring dashboard**
   - Show pending notifications
   - Show stuck tasks
   - Show review backlog

9. **Document and enforce database-only pattern**
   - Update agent prompts
   - Add validation checks
   - Prevent file writes

---

## 8. Testing Recommendations

### Test Scenarios

1. **End-to-End Workflow Test**
   ```python
   def test_complete_workflow():
       # architect creates spec
       spec_id = architect.create_spec(...)

       # Verify notification created
       assert notification_exists(target="project_manager", type="spec_complete")

       # project_manager processes
       pm.process_notifications()

       # Verify spec linked to roadmap
       assert roadmap_item_has_spec(item_id, spec_id)

       # code_developer finds task
       task = cd.get_next_task()
       assert task is not None

       # ... continue full workflow
   ```

2. **Deadlock Detection Test**
   ```python
   def test_no_notifications_processed():
       # Create spec, don't process notifications
       # Verify code_developer can't find task
       # Detect and report deadlock
   ```

3. **Stale Item Recovery Test**
   ```python
   def test_recover_stale_items():
       # Create items 25 hours ago
       # Run recovery
       # Verify items reset
   ```

---

## 9. Implementation Plan

### Phase 1: Critical Fixes (Week 1)
- [ ] Implement project_manager notification processor
- [ ] Add code_reviewer → architect notification
- [ ] Add code_developer → project_manager completion notification
- [ ] Test end-to-end workflow

### Phase 2: Reliability (Week 2)
- [ ] Move review reports to database
- [ ] Implement workflow orchestrator daemon
- [ ] Add database triggers
- [ ] Add stuck task detection

### Phase 3: Monitoring (Week 3)
- [ ] Build workflow dashboard
- [ ] Add consistency checker
- [ ] Document database-only enforcement
- [ ] Create monitoring alerts

---

## 10. Success Criteria

### Workflow is Fixed When:

1. ✅ architect creates spec → project_manager automatically links to roadmap (within 5 minutes)
2. ✅ code_developer can find task immediately after spec linked
3. ✅ code_reviewer completes review → architect notified automatically
4. ✅ code_developer completes implementation → roadmap status updates automatically
5. ✅ No tasks stuck in wrong status for >24 hours
6. ✅ All notifications processed within 5 minutes
7. ✅ Zero database/file inconsistencies
8. ✅ All workflows traceable in database

---

## Conclusion

**Current State**: Multiple communication gaps could cause complete workflow deadlock.

**Risk Level**: 🔴 **CRITICAL** - Roadmap could stall completely

**Root Causes**:
1. Missing notification processing loop (project_manager)
2. Incomplete notification creation (code_reviewer, code_developer)
3. Mixed database/file usage breaking automation
4. No event-driven triggers

**Next Steps**:
1. Review this analysis with team
2. Prioritize fixes
3. Implement Phase 1 critical fixes
4. Test end-to-end workflow
5. Deploy and monitor

---

**Last Updated**: 2025-10-23
**Reviewed By**: [Pending]
**Status**: Draft - Awaiting Team Review
