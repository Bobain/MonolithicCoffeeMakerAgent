# Database Structure - Agent Data Flow

This document shows the complete database structure used by the autonomous agents and how data flows between them.

## Database: `data/unified_roadmap_specs.db`

**Single source of truth for roadmap, specs, reviews, and notifications.**

---

## Core Tables and Agent Access

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         UNIFIED DATABASE SCHEMA                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ roadmap_items                                    [project_manager: WRITE]  │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      TEXT   "PRIORITY-27", "US-062"              │
│ • item_type                    TEXT   "priority", "user_story"             │
│ • number                       TEXT   "27", "062"                          │
│ • title                        TEXT   Item description                     │
│ • status                       TEXT   "📝 Planned", "🔄 In Progress", etc  │
│ • spec_id (FK)                 TEXT   → technical_specs.id                 │
│ • content                      TEXT   Full markdown content                │
│ • estimated_hours              TEXT   Time estimate                        │
│ • dependencies                 TEXT   Dependency info                      │
│ • priority_order                INT    Display order                        │
│ • implementation_started_at    TEXT   When code_developer claimed (stale)  │
│ • updated_at                   TEXT   Last modification timestamp          │
│ • updated_by                   TEXT   Agent who updated                    │
├────────────────────────────────────────────────────────────────────────────┤
│ Read: All agents                                                           │
│ Write: project_manager ONLY                                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ spec_id (FK)
                                    ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ technical_specs                                      [architect: WRITE]    │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      TEXT   "SPEC-115", "SPEC-116"              │
│ • spec_number                  INT    115, 116 (UNIQUE)                    │
│ • title                        TEXT   Spec title                          │
│ • roadmap_item_id (FK)         TEXT   → roadmap_items.id (bidirectional)  │
│ • status                       TEXT   "draft", "in_progress", "complete"  │
│ • spec_type                    TEXT   "monolithic", "hierarchical"        │
│ • phase                        TEXT   Phase grouping (MOVED from roadmap) │
│ • file_path                    TEXT   Backup file reference               │
│ • content                      TEXT   Full content (JSON for hierarchical)│
│ • dependencies                 TEXT   JSON array of spec IDs              │
│ • estimated_hours              REAL   Architect's time estimate           │
│ • actual_hours                 REAL   Actual time spent                   │
│ • started_at                   TEXT   When architect started (stale)      │
│ • updated_at                   TEXT   Last modification                   │
│ • updated_by                   TEXT   Agent who updated                   │
├────────────────────────────────────────────────────────────────────────────┤
│ Read: All agents                                                           │
│ Write: architect ONLY                                                      │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ spec_id (FK)
                                    ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ commit_reviews                                  [code_developer: WRITE]   │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      INT    Auto-increment                       │
│ • commit_sha                   TEXT   Git commit SHA (UNIQUE)             │
│ • spec_id (FK)                 TEXT   → technical_specs.id                │
│ • branch                       TEXT   "roadmap" (default)                 │
│ • description                  TEXT   What was implemented                │
│ • files_changed                TEXT   JSON array of file paths            │
│ • requested_by                 TEXT   "code_developer"                    │
│ • requested_at                 TEXT   When review requested               │
│ • review_status                TEXT   "pending", "in_progress", etc       │
│ • reviewer                     TEXT   "code_reviewer"                     │
│ • claimed_at                   TEXT   When code_reviewer claimed (stale)  │
│ • reviewed_at                  TEXT   When review completed               │
│ • review_feedback              TEXT   Feedback from code_reviewer         │
│ • related_pr                   TEXT   Optional PR link                    │
├────────────────────────────────────────────────────────────────────────────┤
│ Write: code_developer (create review requests)                            │
│ Update: code_reviewer (claim, complete, add feedback)                     │
│ Read: All agents                                                           │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ commit_review_id (FK)
                                    ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ review_reports                                   [code_reviewer: WRITE]   │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      INT    Auto-increment                       │
│ • commit_review_id (FK)        INT    → commit_reviews.id                 │
│ • commit_sha                   TEXT   Git commit SHA                      │
│ • spec_id (FK)                 TEXT   → technical_specs.id                │
│                                                                             │
│ [Report Metadata]                                                          │
│ • date                         TEXT   Review date                         │
│ • reviewer                     TEXT   "code_reviewer"                     │
│ • review_duration_seconds      REAL   How long review took                │
│                                                                             │
│ [Metrics]                                                                  │
│ • files_changed                INT    Number of files                     │
│ • lines_added                  INT    Lines added                         │
│ • lines_deleted                INT    Lines deleted                       │
│ • quality_score                INT    0-100 score                         │
│ • approved                     BOOL   Pass/fail                           │
│                                                                             │
│ [Issues - JSON]                                                            │
│ • issues                       TEXT   JSON array of Issue objects         │
│ • style_compliance             TEXT   JSON dict of style checks           │
│ • architecture_compliance      TEXT   JSON dict of architecture checks    │
│                                                                             │
│ [Content]                                                                  │
│ • overall_assessment           TEXT   Summary feedback                    │
│ • full_report_markdown         TEXT   Complete review report              │
│                                                                             │
│ [Architect Follow-up]                                                      │
│ • needs_architect_review       BOOL   Manually set by code_reviewer       │
│ • architect_reviewed_at        TEXT   When architect checked              │
│ • architect_notes              TEXT   Architect's feedback                │
│                                                                             │
│ • created_at                   TEXT   Report creation time                │
├────────────────────────────────────────────────────────────────────────────┤
│ Write: code_reviewer ONLY                                                  │
│ Read: All agents (especially architect for quality < 80)                  │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ review_comments                                  [code_reviewer: WRITE]   │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      INT    Auto-increment                       │
│ • commit_review_id (FK)        INT    → commit_reviews.id                 │
│ • file_path                    TEXT   Which file                          │
│ • line_number                  INT    Which line (optional)               │
│ • comment_type                 TEXT   "issue", "suggestion", "praise"     │
│ • comment_text                 TEXT   The feedback                        │
│ • severity                     TEXT   "critical", "high", "medium", "low" │
│ • created_at                   TEXT   When comment added                  │
├────────────────────────────────────────────────────────────────────────────┤
│ Write: code_reviewer ONLY                                                  │
│ Read: All agents                                                           │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ notifications                                   [orchestrator: DISPATCH]   │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      INT    Auto-increment                       │
│ • target_agent                 TEXT   Who should handle this              │
│ • source_agent                 TEXT   Who sent this                       │
│ • notification_type            TEXT   "spec_complete", "status_update"    │
│ • item_id                      TEXT   Related item (spec_id, roadmap_id)  │
│ • message                      TEXT   Context/details                     │
│ • status                       TEXT   "pending", "processed", "ignored"   │
│ • created_at                   TEXT   When created                        │
│ • processed_at                 TEXT   When handled                        │
│ • processed_by                 TEXT   Who handled it                      │
│ • notes                        TEXT   Processing notes                    │
├────────────────────────────────────────────────────────────────────────────┤
│ Write: Any agent can create notifications                                  │
│ Read: orchestrator (polls and dispatches to target_agent)                 │
│ Update: orchestrator (marks as processed)                                  │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ audit_trail                                      [All agents: WRITE]      │
├────────────────────────────────────────────────────────────────────────────┤
│ • id (PK)                      INT    Auto-increment                       │
│ • table_name                   TEXT   "roadmap_items", "technical_specs"  │
│ • item_id                      TEXT   Which item was modified             │
│ • action                       TEXT   "create", "update", "delete"        │
│ • field_changed                TEXT   Which field                         │
│ • old_value                    TEXT   Previous value                      │
│ • new_value                    TEXT   New value                           │
│ • changed_by                   TEXT   Agent who made change               │
│ • changed_at                   TEXT   When changed                        │
├────────────────────────────────────────────────────────────────────────────┤
│ Write: Automatic on all table modifications                               │
│ Read: All agents (for history/debugging)                                  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT WORKFLOW AND DATA FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STEP 1: project_manager creates roadmap items                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    project_manager
         │
         │ CREATE
         ↓
    roadmap_items
         ├─ id: "PRIORITY-27"
         ├─ title: "Update code_reviewer to Use Database"
         ├─ status: "📝 Planned"
         ├─ spec_id: NULL  ← No spec yet!
         └─ implementation_started_at: NULL

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STEP 2: architect creates technical specification                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    architect
         │
         │ CREATE
         ↓
    technical_specs
         ├─ id: "SPEC-117"  ← Spec created
         ├─ title: "Code Reviewer Database Integration"
         ├─ roadmap_item_id: "PRIORITY-27"  ← Links back
         ├─ status: "draft" → "in_progress" → "complete"
         ├─ phase: "Phase 3"  ← NEW: Phase at spec level
         ├─ content: { overview, api_design, implementation... }
         ├─ started_at: "2025-10-23T10:00:00"  ← Stale detection
         └─ estimated_hours: 10.5

         │
         │ NOTIFY
         ↓
    notifications
         ├─ target_agent: "project_manager"
         ├─ source_agent: "architect"
         ├─ notification_type: "spec_complete"
         ├─ item_id: "SPEC-117"
         └─ status: "pending"

         ↓
    orchestrator (polls notifications)
         │
         │ DISPATCH to project_manager
         ↓
    project_manager
         │
         │ UPDATE roadmap_items
         ↓
    roadmap_items
         ├─ id: "PRIORITY-27"
         ├─ spec_id: "SPEC-117"  ← NOW LINKED!
         └─ status: "📝 Planned" (ready for implementation)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STEP 3: code_developer implements the specification                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    code_developer
         │
         │ 1. Query next planned item with spec
         ↓
    roadmap_items (JOIN technical_specs)
         │ WHERE status = "📝 Planned"
         │ AND spec_id IS NOT NULL
         │ AND technical_specs.status = "complete"
         │
         │ RESULT: PRIORITY-27 + SPEC-117
         ↓
    code_developer
         │
         │ 2. CLAIM work (stale detection)
         ↓
    roadmap_items
         ├─ implementation_started_at: "2025-10-23T12:00:00"  ← Claimed
         └─ status: "🔄 In Progress"

         ↓
    code_developer
         │ 3. Read hierarchical spec
         ↓
    technical_specs
         │ Load spec content:
         │  - get_spec_overview("SPEC-117")
         │  - get_spec_section("SPEC-117", "implementation")
         │  - get_spec_implementation_details("SPEC-117")
         ↓
    code_developer
         │ 4. Implement code
         │ 5. Make git commit
         ↓
    git commit abc1234
         │
         │ 6. REQUEST REVIEW
         ↓
    commit_reviews
         ├─ commit_sha: "abc1234"
         ├─ spec_id: "SPEC-117"
         ├─ description: "Implemented database integration"
         ├─ files_changed: ["code_reviewer.py", "database.py"]
         ├─ requested_by: "code_developer"
         ├─ review_status: "pending"
         └─ related_pr: "PR #42"

         │
         │ 7. RELEASE work claim
         ↓
    roadmap_items
         └─ implementation_started_at: NULL  ← Released

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STEP 4: code_reviewer reviews the commit                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    code_reviewer
         │
         │ 1. Find pending reviews
         ↓
    commit_reviews
         │ WHERE review_status = "pending"
         │ RESULT: commit abc1234, spec SPEC-117
         ↓
    code_reviewer
         │
         │ 2. CLAIM review (stale detection)
         ↓
    commit_reviews
         ├─ review_status: "in_progress"
         ├─ reviewer: "code_reviewer"
         └─ claimed_at: "2025-10-23T13:00:00"  ← Claimed

         ↓
    code_reviewer
         │ 3. Read spec to understand requirements
         ↓
    technical_specs ("SPEC-117")
         │ Load requirements to compare against implementation
         ↓
    code_reviewer
         │ 4. Run static analysis (radon, mypy, bandit)
         │ 5. Check style guide compliance
         │ 6. Verify against spec requirements
         ↓
    review_comments
         ├─ commit_review_id: 42
         ├─ file_path: "code_reviewer.py"
         ├─ line_number: 125
         ├─ comment_type: "issue"
         ├─ comment_text: "Missing error handling"
         └─ severity: "medium"

         ↓
    code_reviewer
         │ 7. Generate quality score (0-100)
         │ 8. Create comprehensive report
         ↓
    review_reports
         ├─ commit_review_id: 42
         ├─ commit_sha: "abc1234"
         ├─ spec_id: "SPEC-117"
         ├─ quality_score: 75
         ├─ approved: false
         ├─ issues: "[{type:'medium', ...}, ...]"
         ├─ needs_architect_review: false  ← Manual field
         └─ overall_assessment: "3 medium issues need addressing"

         ↓
    commit_reviews
         ├─ review_status: "changes_requested"
         ├─ reviewed_at: "2025-10-23T13:15:00"
         └─ review_feedback: "See review_reports for details"

         │
         │ 9. OPTIONAL: code_reviewer can notify architect if critical
         │    (architect also reads reviews independently)
         ↓
    notifications (optional)
         ├─ target_agent: "architect"
         ├─ source_agent: "code_reviewer"
         ├─ notification_type: "review_complete"
         ├─ item_id: "SPEC-117"
         └─ message: "Review complete for SPEC-117"

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STEP 5: orchestrator dispatches notifications                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    orchestrator (continuous polling)
         │
         │ Poll notifications table every N seconds
         ↓
    notifications (WHERE status = "pending")
         │
         │ Found: architect notification
         ↓
    orchestrator
         │
         │ DISPATCH to architect agent
         ↓
    architect
         │
         │ 1. Read review report
         ↓
    review_reports (WHERE needs_architect_review = true)
         │
         │ 2. Review issues
         │ 3. Decide: update spec or provide guidance
         ↓
    technical_specs
         │ OPTIONAL: Update spec with clarifications
         ↓
    review_reports
         ├─ architect_reviewed_at: "2025-10-23T14:00:00"
         └─ architect_notes: "Added error handling section to spec"

         ↓
    notifications
         └─ status: "processed"  ← Marked done
```

---

## Foreign Key Relationships

```
roadmap_items.spec_id  ─────────→  technical_specs.id
                                            │
                                            ↓
technical_specs.roadmap_item_id  ─────→  roadmap_items.id
                      (bidirectional relationship)

technical_specs.id  ←─────────  commit_reviews.spec_id
                                        │
                                        ↓
commit_reviews.id  ←──────────  review_reports.commit_review_id
                                        │
                                        ↓
commit_reviews.id  ←──────────  review_comments.commit_review_id

technical_specs.id  ←─────────  review_reports.spec_id
```

---

## Agent Access Control Matrix

| Table              | project_manager | architect | code_developer | code_reviewer | All Agents |
|--------------------|-----------------|-----------|----------------|---------------|------------|
| **roadmap_items**      | READ + WRITE    | READ      | READ + claim   | READ          | READ       |
| **technical_specs**    | READ            | READ + WRITE | READ        | READ          | READ       |
| **commit_reviews**     | READ            | READ      | READ + CREATE  | READ + UPDATE | READ       |
| **review_reports**     | READ            | READ + annotate | READ    | READ + WRITE  | READ       |
| **review_comments**    | READ            | READ      | READ           | READ + WRITE  | READ       |
| **notifications**      | READ + CREATE   | READ + CREATE | READ + CREATE | READ + CREATE | READ + CREATE |
| **audit_trail**        | READ            | READ      | READ           | READ          | READ       |

---

## Key Design Patterns

### 1. **Bidirectional Linking** (roadmap_items ↔ technical_specs)
- `roadmap_items.spec_id` → `technical_specs.id`
- `technical_specs.roadmap_item_id` → `roadmap_items.id`
- Enables querying from either direction

### 2. **Stale Work Detection** (24-hour threshold)
- `roadmap_items.implementation_started_at` - code_developer claims work
- `technical_specs.started_at` - architect claims spec work
- `commit_reviews.claimed_at` - code_reviewer claims review work
- Orchestrator runs `reset_stale_*()` methods to recover abandoned work

### 3. **Phase Granularity** (moved to technical_specs)
- One roadmap item can have multiple specs
- Each spec can be in a different phase
- Example: PRIORITY-27 might have SPEC-117 (Phase 3) and SPEC-118 (Phase 4)

### 4. **Notification Dispatch** (orchestrator-centric)
- All agents write to `notifications` table
- Orchestrator polls and dispatches to `target_agent`
- Prevents notification processing deadlock

### 5. **Quality Feedback Loop**
- architect periodically reads `review_reports` to identify issues
- architect decides which reviews need attention
- architect updates specs based on learnings
- Continuous improvement cycle

---

## Stale Recovery Mechanisms

```python
# Called periodically by orchestrator

# 1. Reset stale implementations (>24h in progress)
roadmap_db.reset_stale_implementations(stale_hours=24)
# Clears: roadmap_items.implementation_started_at

# 2. Reset stale spec work (>24h architect working)
spec_skill.reset_stale_specs(stale_hours=24)
# Clears: technical_specs.started_at
# Changes: technical_specs.status "in_progress" → "draft"

# 3. Reset stale code reviews (>24h code_reviewer working)
review_skill.reset_stale_reviews(stale_hours=24)
# Clears: commit_reviews.claimed_at
# Changes: commit_reviews.review_status "in_progress" → "pending"
```

---

## Example Query Patterns

### Find next implementation task for code_developer:
```sql
SELECT
    r.id as roadmap_id,
    r.title,
    s.id as spec_id,
    s.content,
    s.phase
FROM roadmap_items r
INNER JOIN technical_specs s ON r.spec_id = s.id
WHERE
    (r.status LIKE '%📝%' OR r.status LIKE '%Planned%')
    AND s.status IN ('complete', 'approved')
    AND r.implementation_started_at IS NULL  -- Not claimed
ORDER BY r.priority_order ASC
LIMIT 1;
```

### Find reviews needing code_reviewer attention:
```sql
SELECT
    cr.id,
    cr.commit_sha,
    cr.spec_id,
    s.title as spec_title,
    cr.files_changed
FROM commit_reviews cr
LEFT JOIN technical_specs s ON cr.spec_id = s.id
WHERE cr.review_status = 'pending'
ORDER BY cr.requested_at ASC;
```

### Find reviews for architect to review:
```sql
-- Architect reviews all reports, prioritizing by quality score
SELECT
    rr.id,
    rr.commit_sha,
    rr.spec_id,
    rr.quality_score,
    rr.overall_assessment,
    rr.approved
FROM review_reports rr
WHERE rr.architect_reviewed_at IS NULL
ORDER BY rr.quality_score ASC;  -- Worst quality first

-- Or find unapproved reviews
SELECT
    rr.id,
    rr.commit_sha,
    rr.spec_id,
    rr.quality_score,
    rr.overall_assessment
FROM review_reports rr
WHERE rr.approved = 0
  AND rr.architect_reviewed_at IS NULL
ORDER BY rr.created_at DESC;
```

---

## Database Locations (CFR-015)

All database files MUST be in `data/` directory:

- **Primary**: `data/unified_roadmap_specs.db` (all agents use this)
- **Legacy**: `data/roadmap.db` (standalone, for backward compatibility)
- **Legacy**: `data/specs.db` (standalone, for backward compatibility)

Direct file access to markdown files (ROADMAP.md, SPEC-*.md) is **FORBIDDEN** per CFR-015.
All data access MUST go through database skills.

---

## Version History

- **2025-10-23**: Added stale work detection fields, moved phase to technical_specs
- **2025-10-21**: Added hierarchical spec support, review_reports table
- **2025-10-19**: Initial unified database structure
