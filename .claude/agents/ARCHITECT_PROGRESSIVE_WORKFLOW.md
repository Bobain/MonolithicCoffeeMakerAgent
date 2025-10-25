# Architect Progressive Workflow Guide

**Status**: Production ✅
**Last Updated**: 2025-10-24
**Related**: `plan_and_summary` field in `roadmap_items` table

---

## Overview

The architect uses a **progressive workflow** to work on large roadmap items across multiple sessions. The workflow is enforced at the **roadmap_items** granularity level.

### Why Roadmap-Level Tracking?

**Hierarchy**:
```
roadmap_items (1)  →  technical_specs (1-many)  →  implementation_tasks (many)
```

- **roadmap_items**: ONE plan for the entire user story/feature
- **technical_specs**: Multiple specs can be created for one roadmap item
- **implementation_tasks**: Multiple parallel tasks per spec

**Problem if tracked at spec-level**: Duplication across multiple specs for the same roadmap item.

**Solution**: Track plan_and_summary at the **roadmap_items** level.

---

## Concurrent Architect Prevention

**Problem**: Multiple architects (or multiple invocations of the same architect) working on the same roadmap item simultaneously would cause:
- Conflicting spec writes
- Race conditions in plan_and_summary updates
- Duplicate work
- Data corruption

**Solution**: Roadmap-item-level locking with `claim_spec_work()` / `release_spec_work()`

### How It Works

```
Two Levels of Protection:

1. Agent-Level Singleton (AgentRegistry):
   - Only ONE architect process can run at a time
   - Prevents duplicate agent launches

2. Roadmap-Item-Level Locking (Database):
   - Only ONE architect can claim a specific roadmap item
   - Prevents concurrent work on the same item
   - Even if the same architect is invoked twice

Combined Protection = No concurrent spec work on same item!
```

### Claiming Mechanism

```
roadmap_items table:
├── spec_work_started_at (TEXT)  # ISO timestamp when architect claimed
│
Methods:
├── claim_spec_work(item_id)     # Claim item for spec writing
├── release_spec_work(item_id)   # Release claim when done
└── reset_stale_spec_work()      # Reset claims >24 hours old
```

---

## Mandatory Workflow Steps

### Step 1: ALWAYS Claim Item and Check for Existing Plan

```python
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

roadmap_db = RoadmapDatabase(agent_name="architect")

# MANDATORY: Claim the item BEFORE starting work
if not roadmap_db.claim_spec_work("PRIORITY-26"):
    print("❌ Another architect is already working on PRIORITY-26")
    print("   Cannot proceed - item is locked")
    exit(1)

print("✅ Claimed PRIORITY-26 for spec work")

# Get roadmap item
item = roadmap_db.get_item("PRIORITY-26")

# Check if plan exists
existing_plan = roadmap_db.get_plan_and_summary("PRIORITY-26")

if not existing_plan:
    # CREATE NEW PLAN (first session)
    # See "Creating a Plan" section below
else:
    # RESUME EXISTING WORK (subsequent sessions)
    # See "Resuming Work" section below
```

### Step 2: Creating a Plan (First Session)

```python
plan = {
    "overview": "High-level description of what needs to be done",
    "sections_planned": [
        "user_model_spec",      # SPEC-131
        "login_api_spec",       # SPEC-132
        "password_reset_spec",  # SPEC-133
        "test_spec"             # SPEC-134
    ],
    "sections_completed": [],
    "next_steps": "Start with user_model_spec - design database schema",
    "blockers": [],
    "work_sessions": 1,
    "specs_written": [],           # Track spec IDs created
    "tech_specs_complete": False,
    "architecture_summary": None,
    "reusable_components": []      # Components for future reuse
}

roadmap_db.update_plan_and_summary("PRIORITY-26", plan)
```

### Step 3: Working on Specs (Each Session)

```python
from coffee_maker.autonomous.unified_spec_skill import TechnicalSpecSkill

spec_skill = TechnicalSpecSkill(agent_name="architect")

# Get current plan
plan = roadmap_db.get_plan_and_summary("PRIORITY-26")

# Work on next section
if "user_model_spec" not in plan["sections_completed"]:
    spec_id = spec_skill.create_spec(
        spec_number=131,
        title="Authentication System - User Model",
        roadmap_item_id="PRIORITY-26",
        content={
            "overview": "User model design...",
            "data_model": "Schema with email, password_hash...",
            "implementation": "User class with validation..."
        },
        spec_type="hierarchical",
        estimated_hours=4.0
    )

    # Update plan
    plan["sections_completed"].append("user_model_spec")
    plan["specs_written"].append(spec_id)
    plan["next_steps"] = "Create login_api_spec - JWT token generation"
    plan["work_sessions"] += 1

    roadmap_db.update_plan_and_summary("PRIORITY-26", plan)
```

### Step 4: Mark Complete with Architecture Summary

```python
# When ALL specs are written
if len(plan["sections_completed"]) == len(plan["sections_planned"]):
    plan["tech_specs_complete"] = True

    # Write architecture summary
    plan["architecture_summary"] = {
        "overview": "Complete authentication system with JWT tokens",
        "components_created": [
            "User model (database schema and validation)",
            "JWT token generator and validator",
            "Login/logout API endpoints",
            "Password reset flow with email",
            "Integration test suite"
        ],
        "dependencies": {
            "internal": [],  # Other specs this depends on
            "external": ["bcrypt", "PyJWT", "email-validator"]
        },
        "database_changes": [
            "users table: id, email, password_hash, created_at, updated_at",
            "password_reset_tokens table: token, user_id, expires_at"
        ]
    }

    # CRITICAL: Identify reusable components
    plan["reusable_components"] = [
        {
            "name": "JWT token generator",
            "location": "SPEC-132 /implementation section",
            "use_cases": [
                "API authentication for other services",
                "Session management for admin panel",
                "Third-party API integrations"
            ]
        },
        {
            "name": "Email notification system",
            "location": "SPEC-133 /implementation section",
            "use_cases": [
                "User registration confirmation",
                "Password change notifications",
                "Account activity alerts"
            ]
        }
    ]

    plan["next_steps"] = "All specs complete. Ready for implementation task creation."

    roadmap_db.update_plan_and_summary("PRIORITY-26", plan)

    # MANDATORY: Release claim when work is complete
    roadmap_db.release_spec_work("PRIORITY-26")

    print("✅ Technical specs complete!")
    print(f"   Specs written: {len(plan['specs_written'])}")
    print(f"   Reusable components: {len(plan['reusable_components'])}")
    print("   Released claim on PRIORITY-26")
```

---

## Finding and Reusing Components (MANDATORY)

**BEFORE** writing any new spec, **ALWAYS** search for reusable components:

```python
# Search for reusable components
reusable_found = roadmap_db.find_reusable_components(
    search_terms=["JWT", "token", "auth", "authentication"]
)

if reusable_found:
    print(f"✅ Found {len(reusable_found)} reusable components:")
    for comp in reusable_found:
        print(f"\n  Component: {comp['component_name']}")
        print(f"  Source: {comp['source_item_id']} - {comp['source_item_title']}")
        print(f"  Location: {comp['location']}")
        print(f"  Use cases: {', '.join(comp['use_cases'])}")

# Reference in new spec
spec_id = spec_skill.create_spec(
    spec_number=140,
    title="Admin Panel - Authentication",
    roadmap_item_id="PRIORITY-30",
    content={
        "overview": "Admin auth using existing JWT infrastructure...",
        "dependencies": "Reuses JWT token generator from SPEC-132",
        "implementation": """
        REUSE EXISTING:
        - JWT token generation from SPEC-132 /implementation
        - Token validation logic from SPEC-132 /implementation

        NEW IMPLEMENTATION:
        - Admin-specific claims in JWT payload
        - Role-based access control
        """
    },
    spec_type="hierarchical",
    estimated_hours=2.0  # Reduced due to reuse
)
```

---

## Handling Blockers

```python
# Add blocker
plan = roadmap_db.get_plan_and_summary("PRIORITY-26")
plan["blockers"].append({
    "description": "Need user decision on email provider (SendGrid vs AWS SES)",
    "blocking_section": "password_reset_spec",
    "added_at": datetime.now().isoformat()
})
plan["next_steps"] = "BLOCKED: Waiting for email provider decision"
roadmap_db.update_plan_and_summary("PRIORITY-26", plan)

# MANDATORY: Release claim when blocked
roadmap_db.release_spec_work("PRIORITY-26")
print("Released claim due to blocker - can be resumed later")

# When blocker resolved (need to reclaim)
if roadmap_db.claim_spec_work("PRIORITY-26"):
    plan = roadmap_db.get_plan_and_summary("PRIORITY-26")
    plan["blockers"] = [b for b in plan["blockers"] if "email provider" not in b["description"]]
    plan["next_steps"] = "Resume password_reset_spec with SendGrid"
    roadmap_db.update_plan_and_summary("PRIORITY-26", plan)
```

---

## plan_and_summary Schema

```python
{
    # Planning
    "overview": str,                    # High-level description
    "sections_planned": List[str],      # What specs are needed
    "sections_completed": List[str],    # What specs are done
    "next_steps": str,                  # What to do next session

    # Tracking
    "blockers": List[Dict],             # Current blockers
    "work_sessions": int,               # Number of sessions
    "specs_written": List[str],         # Spec IDs created

    # Completion
    "tech_specs_complete": bool,        # All specs done?
    "architecture_summary": Dict,       # Architecture overview
    "reusable_components": List[Dict]   # Components for reuse
}
```

---

## Database Methods

### RoadmapDatabase Methods

```python
# Locking (architect only)
roadmap_db.claim_spec_work(item_id: str) -> bool
roadmap_db.release_spec_work(item_id: str) -> bool
roadmap_db.reset_stale_spec_work(stale_hours: int = 24) -> int

# Plan management (architect only for update, all agents for read)
roadmap_db.update_plan_and_summary(item_id: str, plan_and_summary: Dict) -> bool
roadmap_db.get_plan_and_summary(item_id: str) -> Optional[Dict]

# Reusability (all agents)
roadmap_db.find_reusable_components(search_terms: List[str]) -> List[Dict]
```

---

## Benefits

1. **Correct Granularity**: One plan per roadmap item, not per spec
2. **No Duplication**: Single source of truth
3. **Progressive Work**: Clear resumption points across sessions
4. **Reusability**: Track and find components for future work
5. **Architecture Knowledge**: Comprehensive summaries for each completed item

---

## Related Files

- **Database**: `coffee_maker/autonomous/roadmap_database.py`
- **Migration**: `coffee_maker/autonomous/migrate_move_plan_to_roadmap_and_cleanup.py`
- **Agent Prompt**: `.claude/agents/architect.md` (Workflow 1)
- **Spec Skill**: `.claude/skills/shared/technical_spec_database/unified_spec_skill.py`

---

**Remember**: ALWAYS check for existing plan, search for reusable components, and update plan_and_summary after each session!
