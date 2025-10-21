# SPEC-NEXT: Technical Prerequisite Identification and Tracking

**Status**: Draft
**Created**: 2025-10-21
**Author**: user_listener (from user requirement)
**Priority**: HIGH
**Related CFRs**: CFR-XXX (to be assigned)

## Problem Statement

Currently, architect has no formal responsibility or tooling to:
1. Identify common technical prerequisites needed by multiple user stories
2. Group user stories that share technical dependencies
3. Recommend prerequisite prioritization to project_manager

This leads to:
- **Duplicate technical work** across multiple user story implementations
- **Mid-implementation blockers** when prerequisites are discovered late
- **Inefficient prioritization** (implementing dependent USs before foundations)
- **Technical debt** from inconsistent implementations of same foundation

## Example Scenario

**Current Problem**:
```
US-050: User authentication for dashboard
US-060: Admin authentication for settings
US-070: API authentication for integrations

code_developer implements US-050 → Creates basic auth (JWT, 40 hours)
code_developer implements US-060 → Creates admin auth (duplicate work, 30 hours)
code_developer implements US-070 → Creates API auth (duplicate work, 25 hours)

Total time: 95 hours
Result: 3 different auth implementations, inconsistent patterns, tech debt
```

**With Prerequisite Tracking**:
```
architect analyzes ROADMAP → Identifies pattern
architect creates TECH-001: "Unified Authentication System"
architect links US-050, US-060, US-070 → TECH-001
architect notifies project_manager: "Prioritize TECH-001 first"

project_manager prioritizes TECH-001 before US-050/60/70
code_developer implements TECH-001 (30 hours) → Complete auth foundation
code_developer implements US-050 (10 hours) → Use existing auth
code_developer implements US-060 (8 hours) → Use existing auth
code_developer implements US-070 (7 hours) → Use existing auth

Total time: 55 hours (42% savings!)
Result: 1 consistent auth implementation, zero tech debt
```

## Proposed Solution

### 1. New Architect Responsibility

**CFR-XXX: Technical Prerequisite Identification**

architect MUST:
- Review upcoming planned user stories in ROADMAP
- Identify common technical foundations needed by 2+ user stories
- Create technical prerequisite specifications (TECH-XXX)
- Link user stories to prerequisites in database
- Notify project_manager with prioritization recommendations
- Perform this analysis weekly or when new user stories are added

### 2. Database Schema

Add to `roadmap_database.py`:

```sql
CREATE TABLE technical_prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prereq_id TEXT UNIQUE NOT NULL,              -- TECH-001, TECH-002, etc.
    title TEXT NOT NULL,                          -- "Unified Authentication System"
    description TEXT NOT NULL,                    -- Detailed technical description
    category TEXT,                                -- auth, database, api, ui, infrastructure
    status TEXT NOT NULL DEFAULT 'identified',   -- identified, planned, in_progress, complete
    priority TEXT NOT NULL DEFAULT 'high',       -- critical, high, medium, low
    estimated_hours TEXT,                         -- Implementation time estimate
    identified_by TEXT NOT NULL,                  -- Usually "architect"
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    implemented_at TEXT,                          -- When code_developer completed it
    notes TEXT
);

CREATE TABLE prerequisite_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_story_id TEXT NOT NULL,                 -- US-050, US-060, etc.
    prereq_id TEXT NOT NULL,                     -- TECH-001
    dependency_type TEXT NOT NULL,               -- requires, blocks, enhances, optional
    identified_by TEXT NOT NULL,                 -- Usually "architect"
    created_at TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (prereq_id) REFERENCES technical_prerequisites(prereq_id)
);
```

### 3. Architect Workflow

**Step 1: Identify Prerequisites**
```python
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

db = RoadmapDatabase()

# architect reviews planned user stories
planned = db.get_all_items(status_filter="📝 Planned")

# Identifies: US-050, US-060, US-070 all need authentication
# Creates technical prerequisite
db.create_technical_prerequisite(
    prereq_id="TECH-001",
    title="Unified Authentication System",
    description="""
    JWT-based authentication with role-based access control (RBAC).

    Features:
    - User registration and login
    - JWT token generation and validation
    - Role-based permissions (user, admin, api)
    - Password hashing with bcrypt
    - Token refresh mechanism
    - Session management

    Stack:
    - FastAPI security dependencies
    - python-jose for JWT
    - passlib for password hashing
    - SQLite for user/session storage
    """,
    category="auth",
    priority="critical",
    estimated_hours="30-35",
    identified_by="architect"
)
```

**Step 2: Link User Stories**
```python
# Link each user story to prerequisite
db.link_user_story_to_prerequisite("US-050", "TECH-001", dependency_type="requires")
db.link_user_story_to_prerequisite("US-060", "TECH-001", dependency_type="requires")
db.link_user_story_to_prerequisite("US-070", "TECH-001", dependency_type="requires")
```

**Step 3: Notify project_manager**
```python
# Create prioritization recommendation
notif_id = db.create_prerequisite_recommendation(
    prereq_id="TECH-001",
    user_story_ids=["US-050", "US-060", "US-070"],
    recommended_by="architect"
)
```

**Notification to project_manager**:
```markdown
🏗️ Technical Prerequisite Recommendation from architect

**Prerequisite**: TECH-001 - Unified Authentication System
**Category**: auth
**Priority**: critical
**Estimated Effort**: 30-35 hours

**Description**:
JWT-based authentication with role-based access control...

**Dependent User Stories** (3):
- US-050: User authentication for dashboard (📝 Planned)
- US-060: Admin authentication for settings (📝 Planned)
- US-070: API authentication for integrations (📝 Planned)

**Recommendation**:
Prioritize TECH-001 BEFORE the 3 user stories listed above to:
1. Avoid duplicate technical work across multiple implementations
2. Ensure consistent technical foundation
3. Enable parallel implementation of dependent stories
4. Reduce overall implementation time by ~42% (95h → 55h)

**Next Steps**:
1. Review prerequisite specification in docs/architecture/specs/SPEC-001-unified-auth.md
2. Add TECH-001 to ROADMAP.md as high-priority technical task
3. Schedule TECH-001 before US-050/060/070
4. Notify code_developer when TECH-001 is ready for implementation

**Impact if NOT prioritized**:
- Each user story will re-implement authentication (95 total hours)
- Higher risk of inconsistent implementations (security vulnerabilities)
- Longer overall delivery time
- Increased technical debt and maintenance burden
```

### 4. project_manager Actions

**Review Recommendations**:
```python
# Get all prerequisite recommendations
notifications = db.get_pending_notifications()
prereq_notifs = [n for n in notifications if n['notification_type'] == 'prerequisite_recommendation']

# Review and approve
for notif in prereq_notifs:
    # Add TECH-001 to ROADMAP
    # Update priorities to schedule TECH-001 first
    # Approve notification
    db.approve_notification(notif['id'], processed_by="project_manager")
```

### 5. Querying and Reporting

**Get all prerequisites with dependent stories**:
```python
grouped = db.get_grouped_dependencies()
for group in grouped:
    print(f"{group['prereq_id']}: {group['title']}")
    print(f"  Status: {group['status']}")
    print(f"  Priority: {group['priority']}")
    print(f"  Dependent stories: {len(group['user_stories'])}")
    for story in group['user_stories']:
        print(f"    - {story['user_story_id']}: {story['user_story_title']}")
```

**Get stories waiting for a prerequisite**:
```python
stories = db.get_user_stories_by_prerequisite("TECH-001")
# Returns list of US-050, US-060, US-070 with dependency details
```

## Implementation Plan

### Phase 1: Database Schema (1-2 hours)
- [ ] Add `technical_prerequisites` table to roadmap_database.py
- [ ] Add `prerequisite_dependencies` table
- [ ] Add indexes for fast queries
- [ ] Create migration if needed
- [ ] Test import/export still works

### Phase 2: Database Methods (2-3 hours)
- [ ] `create_technical_prerequisite()`
- [ ] `link_user_story_to_prerequisite()`
- [ ] `get_user_stories_by_prerequisite()`
- [ ] `get_grouped_dependencies()`
- [ ] `create_prerequisite_recommendation()`
- [ ] Unit tests for all methods

### Phase 3: Architect Skill (2-3 hours)
- [ ] Create `.claude/skills/identify-technical-prerequisites.md`
- [ ] Add prompts for pattern analysis
- [ ] Add workflow for creating prerequisites
- [ ] Add workflow for linking dependencies
- [ ] Integration tests

### Phase 4: project_manager Integration (1-2 hours)
- [ ] Add prerequisite review command
- [ ] Display prerequisite recommendations in dashboard
- [ ] Add approval workflow
- [ ] Update ROADMAP management to respect prerequisites

### Phase 5: Documentation (1 hour)
- [ ] Update docs/AGENT_OWNERSHIP.md
- [ ] Update docs/WORKFLOWS.md
- [ ] Add examples to README
- [ ] Create tutorial in docs/

## Benefits

✅ **40-60% reduction in duplicate technical work**
✅ **Consistent technical foundations** across features
✅ **Earlier identification** of technical dependencies
✅ **Better prioritization** by project_manager
✅ **Lower technical debt** from inconsistent implementations
✅ **Parallel development** after prerequisite is complete
✅ **Clear architectural guidance** for code_developer

## Categories of Technical Prerequisites

**Common categories** architect should look for:

1. **Authentication/Authorization** - User auth, API keys, OAuth, RBAC
2. **Database Infrastructure** - Schema migrations, ORMs, connection pooling
3. **API Foundations** - REST framework, validation, error handling, rate limiting
4. **UI Components** - Design system, component library, theming, layouts
5. **Infrastructure** - Logging, monitoring, deployment, CI/CD
6. **Data Processing** - ETL pipelines, data validation, transformation
7. **Integration** - Third-party APIs, webhooks, message queues
8. **Testing** - Test framework setup, fixtures, mocks, test data

## Success Metrics

Track impact over time:
- Number of technical prerequisites identified
- User stories grouped per prerequisite (higher = more savings)
- Implementation time savings (estimated vs. actual)
- Technical debt reduction (fewer inconsistent patterns)
- code_developer feedback on prerequisite quality

## Example Prerequisites

**TECH-001: Unified Authentication System**
- Dependencies: US-050, US-060, US-070
- Time savings: 40 hours (95h → 55h)

**TECH-002: Streamlit Component Library**
- Dependencies: US-010, US-020, US-030, US-040
- Time savings: 60 hours (120h → 60h)

**TECH-003: Database Migration Framework**
- Dependencies: PRIORITY-5, PRIORITY-8, US-025
- Time savings: 25 hours (50h → 25h)

## Next Steps

1. Review and approve this specification
2. Create database schema changes
3. Implement database methods
4. Create architect skill
5. Update project_manager tooling
6. Document in AGENT_OWNERSHIP.md
7. Test with real ROADMAP analysis

---

**Total Estimated Effort**: 7-11 hours
**Expected ROI**: 40-60% reduction in duplicate work
**Priority**: HIGH (prevents wasted implementation time)
