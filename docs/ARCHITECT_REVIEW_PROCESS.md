# Architect Code Review Process

## Overview

The architect periodically reviews code review reports to identify patterns, issues, and opportunities for spec improvements. **The architect decides what needs attention - there is NO auto-flagging.**

## Key Principle

**The architect is autonomous and proactive.** The architect:
- Reads `review_reports` table on their own schedule
- Decides which reviews need attention based on their judgment
- Is not automatically notified for every low quality score
- Can prioritize reviews by quality score, spec, or other criteria

## Review Workflow

### 1. Architect Queries Reviews

```python
from coffee_maker.autonomous.unified_database import get_unified_database

db = get_unified_database()
conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all unreviewed reports, worst quality first
cursor.execute("""
    SELECT
        rr.id,
        rr.commit_sha,
        rr.spec_id,
        rr.quality_score,
        rr.approved,
        rr.overall_assessment,
        rr.created_at,
        s.title as spec_title
    FROM review_reports rr
    LEFT JOIN technical_specs s ON rr.spec_id = s.id
    WHERE rr.architect_reviewed_at IS NULL
    ORDER BY rr.quality_score ASC
""")

reviews = [dict(row) for row in cursor.fetchall()]
```

### 2. Architect Reads Report Details

```python
# Get full review report
cursor.execute("""
    SELECT
        full_report_markdown,
        issues,
        style_compliance,
        architecture_compliance
    FROM review_reports
    WHERE id = ?
""", (review_id,))

review = dict(cursor.fetchone())

# Read markdown report
print(review['full_report_markdown'])

# Parse issues JSON
import json
issues = json.loads(review['issues'])
for issue in issues:
    print(f"{issue['severity']}: {issue['description']}")
```

### 3. Architect Decides Action

Based on review content, architect may:

**Option A: Update Spec**
- Spec was unclear → Add clarification
- Spec missed requirement → Add requirement
- Spec had wrong assumptions → Fix spec

**Option B: Create Bug Ticket**
- Implementation bug (not spec issue)
- Create ticket for code_developer to fix

**Option C: Accept As-Is**
- Quality score acceptable
- Issues are minor
- Code is good enough

**Option D: Request Changes**
- Serious implementation issues
- Need code_developer to fix before merge

### 4. Architect Marks Review

```python
# Mark review as checked by architect
cursor.execute("""
    UPDATE review_reports
    SET architect_reviewed_at = ?,
        architect_notes = ?
    WHERE id = ?
""", (
    datetime.now().isoformat(),
    "Updated SPEC-117 Section 3.2 to clarify error handling requirements",
    review_id
))
conn.commit()
```

## Fields: `needs_architect_review`

The `needs_architect_review` field is **MANUALLY** set by code_reviewer:

```python
# code_reviewer can optionally flag for architect attention
cursor.execute("""
    UPDATE review_reports
    SET needs_architect_review = 1
    WHERE id = ?
""", (review_id,))
```

**Use cases for manual flagging:**
- Critical security issue found
- Major architectural violation
- Spec contradiction discovered
- Pattern of repeated issues

**Default value**: `0` (false) - architect reviews on their schedule

## Notification Protocol

### Code_reviewer → Architect (Optional)

code_reviewer CAN create notifications for critical issues:

```python
# Only for critical/urgent issues
if has_critical_security_issue:
    cursor.execute("""
        INSERT INTO notifications (
            target_agent, source_agent, notification_type,
            item_id, message, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'architect',
        'code_reviewer',
        'critical_review_issue',
        review_id,
        f"CRITICAL security issue in review #{review_id}",
        'pending',
        datetime.now().isoformat()
    ))
```

**But this is OPTIONAL and RARE.** Most reviews are handled by architect's regular polling.

## Architect's Regular Review Schedule

Recommended schedule for architect to check reviews:

- **Daily**: Check for reviews with `quality_score < 60` (serious issues)
- **Weekly**: Review all unreviewed reports to identify patterns
- **After spec creation**: Check reviews for specs you recently wrote

```python
# Daily check (serious issues only)
cursor.execute("""
    SELECT * FROM review_reports
    WHERE architect_reviewed_at IS NULL
    AND quality_score < 60
    ORDER BY created_at DESC
""")

# Weekly pattern analysis
cursor.execute("""
    SELECT
        spec_id,
        AVG(quality_score) as avg_score,
        COUNT(*) as review_count
    FROM review_reports
    WHERE created_at > date('now', '-7 days')
    GROUP BY spec_id
    ORDER BY avg_score ASC
""")
```

## Benefits of Architect-Driven Review

1. **Autonomy**: architect controls review schedule
2. **Prioritization**: architect decides what's important
3. **Pattern Recognition**: architect can spot trends across reviews
4. **Context**: architect knows which specs need attention
5. **No Noise**: Not notified for every medium-quality review

## Example Queries

### Find reviews for a specific spec
```sql
SELECT * FROM review_reports
WHERE spec_id = 'SPEC-117'
AND architect_reviewed_at IS NULL
ORDER BY created_at DESC;
```

### Find unapproved reviews
```sql
SELECT * FROM review_reports
WHERE approved = 0
AND architect_reviewed_at IS NULL
ORDER BY quality_score ASC;
```

### Find manually flagged reviews
```sql
SELECT * FROM review_reports
WHERE needs_architect_review = 1
AND architect_reviewed_at IS NULL;
```

### Get review statistics by spec
```sql
SELECT
    spec_id,
    COUNT(*) as total_reviews,
    AVG(quality_score) as avg_score,
    SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END) as approved_count
FROM review_reports
GROUP BY spec_id
ORDER BY avg_score ASC;
```

## Summary

- ❌ **NO** auto-flagging based on quality_score < 80
- ❌ **NO** automatic notifications for every review
- ✅ architect queries review_reports on their schedule
- ✅ architect decides which reviews need attention
- ✅ code_reviewer can manually flag critical issues (rare)
- ✅ architect controls review priority and timing

The architect is an autonomous agent who manages their own workload and priorities.
