# Database vs File Usage Violations

**Date**: 2025-10-23
**Status**: 🔴 **CRITICAL** - Violations found that break database-only pattern

---

## Executive Summary

**CFR-015 Violation**: code_reviewer writes review reports to **files** instead of **database**, breaking the database-only pattern and preventing workflow automation.

---

## Violations Found

### 🔴 Violation 1: Review Reports Written to Files

**Location**: `coffee_maker/autonomous/code_reviewer.py`

**Lines**:
- **Line 65**: `self.reviews_dir = project_root / "docs" / "code-reviews"`
- **Line 713**: `report_path.write_text(content)` ← Writes review to file
- **Line 943**: `index_path.write_text(content)` ← Updates index file
- **Line 970**: References file path in notification
- **Line 1012**: Prints file path to user

**What happens**:
```python
# code_reviewer.py:713
def _write_review_report(self, report: ReviewReport) -> Path:
    """Write review report to markdown file."""
    # ...
    report_path.write_text(content)  # ❌ WRITES TO FILE!
    return report_path
```

**Impact**:
1. ❌ Review data not queryable in database
2. ❌ Can't JOIN reviews with specs/roadmap
3. ❌ architect doesn't get notification (no database trigger)
4. ❌ No automated workflow possible
5. ❌ Race conditions between file writes and database reads
6. ❌ Data inconsistency risk

---

### 🔴 Violation 2: Review Index in Files

**Location**: `coffee_maker/autonomous/code_reviewer.py:943`

**What happens**:
```python
def _update_review_index(self, report: ReviewReport):
    """Update the review index file."""
    # ...
    index_path.write_text(content)  # ❌ WRITES TO FILE!
```

**Impact**:
- Index is file-based, not database
- Can't query "all reviews for SPEC-115"
- Can't query "all reviews with score < 70"
- Must parse files manually

---

## Why This Breaks Workflow

### Broken Flow: code_reviewer → architect

**Current (Broken)**:
```
code_reviewer completes review
    ↓
Writes to docs/code-reviews/REVIEW-*.md  ← FILE
    ↓
??? How does architect know review exists ???
    ↓
architect must manually check directory
    ↓
architect reads file manually
    ↓
No automated feedback loop
```

**Should Be**:
```
code_reviewer completes review
    ↓
Inserts into review_reports table  ← DATABASE
    ↓
Database trigger creates notification
    ↓
architect receives notification
    ↓
architect queries database for review details
    ↓
architect acts on feedback
    ↓
Automated feedback loop works!
```

---

## Database Schema Needed

### New Table: review_reports

```sql
CREATE TABLE IF NOT EXISTS review_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_review_id INTEGER NOT NULL,       -- Links to commit_reviews
    commit_sha TEXT NOT NULL,
    spec_id TEXT,                            -- Links to technical_specs

    -- Report metadata
    date TEXT NOT NULL,
    reviewer TEXT NOT NULL DEFAULT 'code_reviewer',
    review_duration_seconds REAL,

    -- Metrics
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER,
    quality_score INTEGER NOT NULL,          -- 0-100
    approved BOOLEAN NOT NULL,

    -- Issues (JSON)
    issues TEXT,                             -- JSON array of Issue objects
    style_compliance TEXT,                   -- JSON dict
    architecture_compliance TEXT,            -- JSON dict

    -- Content
    overall_assessment TEXT NOT NULL,
    full_report_markdown TEXT,               -- Full markdown content

    -- Architect follow-up
    needs_architect_review BOOLEAN DEFAULT 0,
    architect_reviewed_at TEXT,
    architect_notes TEXT,

    created_at TEXT NOT NULL,

    FOREIGN KEY (commit_review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_review_reports_score ON review_reports(quality_score);
CREATE INDEX idx_review_reports_spec ON review_reports(spec_id);
CREATE INDEX idx_review_reports_needs_review ON review_reports(needs_architect_review);
CREATE INDEX idx_review_reports_approved ON review_reports(approved);
```

### Trigger: Auto-notify architect on issues

```sql
CREATE TRIGGER notify_architect_on_review_issues
AFTER INSERT ON review_reports
WHEN NEW.quality_score < 80 OR NEW.approved = 0
BEGIN
    INSERT INTO notifications (
        target_agent, source_agent, notification_type,
        item_id, message, status, created_at
    ) VALUES (
        'architect',
        'code_reviewer',
        'review_changes_needed',
        NEW.spec_id,
        'Review #' || NEW.id || ' found issues (score: ' || NEW.quality_score || '). Review needed.',
        'pending',
        datetime('now')
    );

    UPDATE review_reports
    SET needs_architect_review = 1
    WHERE id = NEW.id;
END;
```

---

## Fix Implementation

### Step 1: Add review_reports table

**File**: `coffee_maker/autonomous/unified_database.py`

Add table creation in `_init_database()`:

```python
# Review reports table (was file-based, now database)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        commit_review_id INTEGER NOT NULL,
        commit_sha TEXT NOT NULL,
        spec_id TEXT,
        date TEXT NOT NULL,
        reviewer TEXT NOT NULL DEFAULT 'code_reviewer',
        review_duration_seconds REAL,
        files_changed INTEGER,
        lines_added INTEGER,
        lines_deleted INTEGER,
        quality_score INTEGER NOT NULL,
        approved BOOLEAN NOT NULL,
        issues TEXT,
        style_compliance TEXT,
        architecture_compliance TEXT,
        overall_assessment TEXT NOT NULL,
        full_report_markdown TEXT,
        needs_architect_review BOOLEAN DEFAULT 0,
        architect_reviewed_at TEXT,
        architect_notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (commit_review_id) REFERENCES commit_reviews(id) ON DELETE CASCADE,
        FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
    )
""")

# Indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_score ON review_reports(quality_score)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_spec ON review_reports(spec_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reports_needs_review ON review_reports(needs_architect_review)")
```

### Step 2: Update code_reviewer to use database

**File**: `coffee_maker/autonomous/code_reviewer.py`

Replace file writing with database insertion:

```python
def _write_review_report(self, report: ReviewReport, commit_review_id: int) -> int:
    """Write review report to DATABASE (not files).

    Returns:
        review_report_id: ID of inserted report
    """
    from coffee_maker.autonomous.unified_database import get_unified_database

    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    # Serialize complex objects to JSON
    issues_json = json.dumps([
        {
            'severity': issue.severity,
            'category': issue.category,
            'file_path': issue.file_path,
            'line_number': issue.line_number,
            'description': issue.description,
            'recommendation': issue.recommendation,
            'effort_estimate': issue.effort_estimate
        }
        for issue in report.issues
    ])

    style_json = json.dumps(report.style_compliance)
    arch_json = json.dumps(report.architecture_compliance)

    # Generate full markdown for backward compatibility
    full_markdown = self._generate_markdown_report(report)

    cursor.execute("""
        INSERT INTO review_reports (
            commit_review_id, commit_sha, spec_id, date, reviewer,
            review_duration_seconds, files_changed, lines_added, lines_deleted,
            quality_score, approved, issues, style_compliance,
            architecture_compliance, overall_assessment,
            full_report_markdown, needs_architect_review, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        commit_review_id,
        report.commit_sha,
        self._get_spec_id_for_commit(commit_review_id),  # Helper method
        report.date.isoformat(),
        'code_reviewer',
        report.review_duration_seconds,
        report.files_changed,
        report.lines_added,
        report.lines_deleted,
        report.quality_score,
        1 if report.approved else 0,
        issues_json,
        style_json,
        arch_json,
        report.overall_assessment,
        full_markdown,
        1 if (report.quality_score < 80 or not report.approved) else 0,
        datetime.now().isoformat()
    ))

    review_report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    logger.info(f"✅ Saved review report #{review_report_id} to database")

    # Still notify architect for high-severity issues
    if report.quality_score < 80 or not report.approved:
        self._notify_architect_of_issues(review_report_id, report)

    return review_report_id
```

### Step 3: Add architect notification

```python
def _notify_architect_of_issues(self, review_report_id: int, report: ReviewReport) -> None:
    """Notify architect when review finds issues."""
    from coffee_maker.autonomous.unified_database import get_unified_database

    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    spec_id = self._get_spec_id_for_commit(report.commit_sha)

    # Count issues by severity
    critical = sum(1 for i in report.issues if i.severity == 'CRITICAL')
    high = sum(1 for i in report.issues if i.severity == 'HIGH')

    message = (
        f"CODE REVIEW NEEDS ATTENTION\n"
        f"- Review Report ID: #{review_report_id}\n"
        f"- Commit: {report.commit_sha[:8]}\n"
        f"- Spec: {spec_id}\n"
        f"- Quality Score: {report.quality_score}/100\n"
        f"- Status: {'CHANGES REQUESTED' if not report.approved else 'APPROVED WITH NOTES'}\n"
        f"- Critical Issues: {critical}\n"
        f"- High Issues: {high}\n"
        f"\nQuery: SELECT * FROM review_reports WHERE id = {review_report_id}"
    )

    cursor.execute("""
        INSERT INTO notifications (
            target_agent, source_agent, notification_type,
            item_id, message, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'architect',
        'code_reviewer',
        'review_changes_needed' if not report.approved else 'review_notes',
        str(review_report_id),
        message,
        'pending',
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    logger.info(f"📬 Notified architect about review #{review_report_id}")
```

### Step 4: Add architect query methods

**File**: `.claude/skills/shared/code_review_tracking/review_tracking_skill.py`

```python
def get_reviews_needing_architect_attention(self) -> List[Dict]:
    """Get reviews that need architect follow-up.

    For use by architect to find reviews requiring action.

    Returns:
        List of review reports needing attention
    """
    try:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                rr.*,
                cr.spec_id,
                ts.title as spec_title
            FROM review_reports rr
            INNER JOIN commit_reviews cr ON rr.commit_review_id = cr.id
            LEFT JOIN technical_specs ts ON cr.spec_id = ts.id
            WHERE rr.needs_architect_review = 1
            AND rr.architect_reviewed_at IS NULL
            ORDER BY rr.created_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    except sqlite3.Error as e:
        logger.error(f"Error getting reviews needing attention: {e}")
        return []

def mark_review_addressed_by_architect(self, review_report_id: int, notes: str) -> bool:
    """Mark that architect has reviewed and addressed issues.

    Args:
        review_report_id: ID of review report
        notes: Architect's notes on actions taken

    Returns:
        True if successful
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE review_reports
            SET needs_architect_review = 0,
                architect_reviewed_at = ?,
                architect_notes = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), notes, review_report_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            logger.info(f"✅ Marked review #{review_report_id} as addressed by architect")

        return success

    except sqlite3.Error as e:
        logger.error(f"Error marking review addressed: {e}")
        return False
```

---

## Migration Plan

### Phase 1: Add Database Table (No Breaking Changes)

1. Add `review_reports` table to unified_database.py
2. Add indexes
3. Create migration script
4. Deploy schema changes

### Phase 2: Update code_reviewer to Write Both (Transition)

1. Modify code_reviewer to write to BOTH database AND files
2. Test dual-writing works
3. Deploy and monitor

### Phase 3: Switch to Database-Only (Breaking Change)

1. Update code_reviewer to write ONLY to database
2. Update architect to read from database
3. Archive old file-based reviews
4. Deploy

### Phase 4: Cleanup (Optional)

1. Remove file-writing code
2. Add database-only validation
3. Update documentation

---

## Benefits After Fix

### ✅ Automated Workflow
```
code_reviewer completes review
    ↓ (automatic)
Review saved to database
    ↓ (trigger fires)
Notification created for architect
    ↓ (automatic)
architect receives notification
    ↓ (manual)
architect queries review details
    ↓ (manual)
architect addresses issues
```

### ✅ Query Capability
```sql
-- Find all reviews for a spec
SELECT * FROM review_reports WHERE spec_id = 'SPEC-115';

-- Find low-quality reviews
SELECT * FROM review_reports WHERE quality_score < 70;

-- Find reviews needing architect attention
SELECT * FROM review_reports WHERE needs_architect_review = 1;

-- Get review statistics by spec
SELECT spec_id, AVG(quality_score), COUNT(*)
FROM review_reports
GROUP BY spec_id;
```

### ✅ No File Race Conditions
- Single source of truth (database)
- ACID transactions
- No file system delays
- No write conflicts

### ✅ Integrated Workflow
- Review reports JOIN with specs
- Review reports JOIN with roadmap
- Full traceability
- Automated metrics

---

## Testing Requirements

### Test 1: Review Written to Database
```python
def test_review_saved_to_database():
    # Perform review
    report = reviewer.review_commit("abc123")

    # Verify in database
    review_reports = db.query("SELECT * FROM review_reports WHERE commit_sha = ?", "abc123")
    assert len(review_reports) == 1
    assert review_reports[0]['quality_score'] == report.quality_score
```

### Test 2: Architect Notification Created
```python
def test_architect_notified_on_low_score():
    # Review with low score
    report = reviewer.review_commit("abc123")
    report.quality_score = 65

    # Verify notification
    notifications = db.query("""
        SELECT * FROM notifications
        WHERE target_agent = 'architect'
        AND notification_type = 'review_changes_needed'
    """)
    assert len(notifications) == 1
```

### Test 3: architect Can Query Reviews
```python
def test_architect_queries_reviews():
    skill = CodeReviewTrackingSkill(agent_name="architect")

    reviews = skill.get_reviews_needing_architect_attention()
    assert len(reviews) > 0
    assert reviews[0]['needs_architect_review'] == 1
```

---

## Conclusion

**Current State**: Code reviews written to files, breaking database-only pattern

**Fix Required**: Move review reports to database with proper notification integration

**Urgency**: 🔴 **HIGH** - Blocks automated workflow and architect notification

**Effort**: ~4 hours for full implementation and testing

**Next Steps**:
1. Review this document
2. Approve database schema
3. Create implementation ticket
4. Implement Phase 1 (schema)
5. Test and deploy

---

**Last Updated**: 2025-10-23
**Status**: Draft - Awaiting Approval
