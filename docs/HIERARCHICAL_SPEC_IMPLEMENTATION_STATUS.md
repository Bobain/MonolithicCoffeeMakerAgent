# Hierarchical Spec Database Integration - Implementation Status

**Date**: 2025-10-24
**Commit**: 478486b
**Status**: ✅ PHASE 1 COMPLETE (Database Infrastructure)

---

## Summary

**PRIORITY 25 Phase 4 (Spec Migration)** - Database integration for hierarchical specs.

**Phase 1 COMPLETE**: Database methods, schema, and skill wrapper implemented.
**Phase 2 REMAINING**: Architect agent integration, code_developer updates, testing.

---

## ✅ What's Implemented (Phase 1)

### 1. Database Write Methods (`RoadmapDatabase`)

**Location**: `coffee_maker/autonomous/roadmap_database.py` (+304 lines)

**New Methods**:

```python
# Create hierarchical or monolithic spec
create_technical_spec(
    spec_number: int,
    title: str,
    roadmap_item_id: str,
    spec_type: str = "monolithic",  # or "hierarchical"
    file_path: Optional[str] = None,
    total_phases: Optional[int] = None,
    phase_files: Optional[List[str]] = None,
    **kwargs
) -> str

# Update spec (status, phase, content)
update_technical_spec(
    spec_id: str,
    status: Optional[str] = None,
    current_phase: Optional[int] = None,
    phase_status: Optional[str] = None,
    **kwargs
) -> bool

# Retrieve spec by ID or roadmap item
get_technical_spec(
    spec_id: Optional[str] = None,
    roadmap_item_id: Optional[str] = None
) -> Optional[Dict]

# Query all specs with filtering
get_all_technical_specs(
    status: Optional[str] = None,
    spec_type: Optional[str] = None
) -> List[Dict]
```

**Features**:
- ✅ Permission checks (architect-only)
- ✅ Auto-links specs to roadmap items
- ✅ JSON support for phase_files
- ✅ Atomic database operations
- ✅ Comprehensive error handling

---

### 2. Schema Enhancements

**Migration**: `migrate_add_hierarchical_spec_columns.py`

**New Columns** (added to `technical_specs` table):
```sql
total_phases INTEGER           -- Number of phases in hierarchical spec
phase_files TEXT               -- JSON array of phase file names
current_phase_status TEXT      -- Status of current phase
```

**Existing Columns** (already present):
```sql
spec_type TEXT DEFAULT 'monolithic'  -- 'monolithic' or 'hierarchical'
phase TEXT                           -- Current phase number
```

**Migration Status**: ✅ Complete (ran successfully)

---

### 3. TechnicalSpecSkill Wrapper

**Location**: `coffee_maker/autonomous/technical_spec_skill.py` (267 lines)

**Purpose**: Unified interface for architect to create specs with full database persistence.

**Key Methods**:

```python
class TechnicalSpecSkill:
    def create_hierarchical_spec(
        us_number: int,
        title: str,
        roadmap_item_id: str,
        phases: List[Dict[str, any]]
    ) -> str:
        """
        1. Creates directory structure via skill
        2. Writes spec entry to database
        3. Links spec to roadmap item

        Returns: spec_id (e.g., "SPEC-104")
        """

    def create_monolithic_spec(
        us_number: int,
        title: str,
        roadmap_item_id: str,
        content: str
    ) -> str:
        """
        1. Creates spec file
        2. Writes spec entry to database
        3. Links spec to roadmap item

        Returns: spec_id
        """

    def get_spec(roadmap_item_id: str) -> Optional[Dict]:
        """Get spec from database"""

    def update_spec_phase(
        spec_id: str,
        current_phase: int,
        phase_status: str
    ) -> bool:
        """Update current phase"""
```

**Features**:
- ✅ Wraps technical-specification-handling skill
- ✅ Integrates file system + database operations
- ✅ Maintains sync between DB and files
- ✅ Supports both hierarchical and monolithic

---

## ⚠️ What's Remaining (Phase 2)

### 1. Architect Agent Integration (4-6 hours)

**Status**: NOT STARTED

**Current**: Architect uses `spec_generator.py` (file-only, no database)

**Needed**:
1. Update architect agent to use `TechnicalSpecSkill`
2. Replace file-only spec creation with database persistence
3. Integrate hierarchical spec creation workflow

**Files to Modify**:
- `coffee_maker/autonomous/spec_generator.py`
- `.claude/agents/architect.md` (workflow updates)
- Any architect daemon/CLI code

**Estimated**: 4-6 hours

---

### 2. code_developer Daemon Updates (2 hours)

**Status**: NOT STARTED

**Current**: code_developer searches file system for specs

**Needed**:
1. Query database for spec: `db.get_technical_spec(roadmap_item_id=...)`
2. Use `technical-specification-handling` skill to load hierarchical specs
3. Implement progressive disclosure (load current phase only)

**Files to Modify**:
- `coffee_maker/autonomous/daemon.py` (spec loading logic)
- `coffee_maker/autonomous/implementation_task_manager.py`

**Estimated**: 2 hours

---

### 3. Testing (2 hours)

**Status**: NOT STARTED

**Needed**:
1. Unit tests for database methods
2. Integration tests for skill wrapper
3. End-to-end tests for architect → database → code_developer flow

**Files to Create**:
- `tests/unit/test_roadmap_database_specs.py`
- `tests/unit/test_technical_spec_skill.py`
- `tests/integration/test_hierarchical_spec_e2e.py`

**Estimated**: 2 hours

---

### 4. Documentation Updates (1 hour)

**Status**: NOT STARTED

**Needed**:
1. Update `.claude/agents/architect.md` with new workflow
2. Update `docs/ARCHITECT_IMPLEMENTATION_STATUS.md`
3. Add examples to skill documentation

**Estimated**: 1 hour

---

## Database Schema - Current State

```sql
CREATE TABLE technical_specs (
    -- Core fields
    id TEXT PRIMARY KEY,                     -- SPEC-104
    spec_number INTEGER NOT NULL UNIQUE,     -- 104
    title TEXT NOT NULL,                     -- "Auth System"
    roadmap_item_id TEXT,                    -- US-104 (FK to roadmap_items)

    -- Status
    status TEXT NOT NULL DEFAULT 'draft',    -- draft|approved|complete|deprecated

    -- Type (NEW)
    spec_type TEXT DEFAULT 'monolithic',     -- monolithic|hierarchical

    -- File system
    file_path TEXT,                          -- Path to spec file or directory
    content TEXT,                            -- Full content (monolithic) or README (hierarchical)

    -- Hierarchical support (NEW)
    total_phases INTEGER,                    -- Number of phases
    phase TEXT,                              -- Current phase number
    phase_files TEXT,                        -- JSON: ["phase1-db.md", "phase2-auth.md"]
    current_phase_status TEXT,               -- in_progress|completed

    -- Estimation
    estimated_hours REAL,                    -- Total estimated time
    actual_hours REAL,                       -- Actual implementation time
    dependencies TEXT,                       -- JSON: Other spec dependencies

    -- Metadata
    updated_at TEXT NOT NULL,                -- ISO timestamp
    updated_by TEXT NOT NULL,                -- Agent name
    started_at TEXT,                         -- When implementation started

    -- Legacy (to be cleaned up)
    plan_summary TEXT,
    plan_and_summary TEXT
);
```

---

## Example Usage (After Phase 2 Complete)

### Architect: Create Hierarchical Spec

```python
from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill

skill = TechnicalSpecSkill(agent_name="architect")

spec_id = skill.create_hierarchical_spec(
    us_number=104,
    title="User Authentication System",
    roadmap_item_id="US-104",
    phases=[
        {"name": "database-schema", "hours": 1.0, "description": "Create user and session tables"},
        {"name": "authentication-logic", "hours": 1.5, "description": "Implement login/logout"},
        {"name": "api-endpoints", "hours": 2.0, "description": "REST API for auth"},
        {"name": "tests-docs", "hours": 1.0, "description": "Tests and documentation"}
    ]
)

print(f"Created: {spec_id}")
# Output: Created: SPEC-104

# File structure created:
# docs/architecture/specs/SPEC-104-user-authentication-system/
# ├── README.md (overview)
# ├── phase1-database-schema.md
# ├── phase2-authentication-logic.md
# ├── phase3-api-endpoints.md
# └── phase4-tests-docs.md

# Database entry created:
# {
#     "id": "SPEC-104",
#     "spec_type": "hierarchical",
#     "total_phases": 4,
#     "estimated_hours": 5.5,
#     "phase_files": ["phase1-database-schema.md", ...]
# }
```

### code_developer: Load Spec from Database

```python
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

db = RoadmapDatabase(agent_name="code_developer")

# Get spec from database
spec = db.get_technical_spec(roadmap_item_id="US-104")

if spec and spec["spec_type"] == "hierarchical":
    print(f"Hierarchical spec with {spec['total_phases']} phases")
    print(f"Current phase: {spec.get('phase', 1)}")

    # Load current phase only (via skill)
    # ... progressive disclosure logic ...
```

---

## Testing the Database Methods

### Quick Verification (Manual)

```python
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

# Test as architect
db = RoadmapDatabase(agent_name="architect")  # can_write = True

# Create test spec
spec_id = db.create_technical_spec(
    spec_number=999,
    title="Test Hierarchical Spec",
    roadmap_item_id="TEST-999",
    spec_type="hierarchical",
    file_path="docs/architecture/specs/SPEC-999-test/",
    total_phases=3,
    phase_files=["phase1-setup.md", "phase2-impl.md", "phase3-test.md"]
)

print(f"Created: {spec_id}")

# Retrieve spec
spec = db.get_technical_spec(spec_id="SPEC-999")
print(f"Retrieved: {spec}")

# Update phase
db.update_technical_spec(
    spec_id="SPEC-999",
    current_phase=2,
    phase_status="in_progress"
)

# Get all hierarchical specs
hierarchical = db.get_all_technical_specs(spec_type="hierarchical")
print(f"Found {len(hierarchical)} hierarchical specs")
```

---

## Commits (Phase 1)

1. **478486b** - feat: Add hierarchical spec database support (Phase 1)
   - Database methods (+304 lines)
   - Schema migration
   - TechnicalSpecSkill wrapper
   - Permission checks
   - JSON support

---

## Next Steps (Priority Order)

### Immediate (Week 1)

1. **Test Database Methods** (1 hour)
   - Verify create/update/get operations
   - Test permission enforcement
   - Test JSON serialization

2. **Update Architect Agent** (4-6 hours)
   - Integrate TechnicalSpecSkill
   - Replace spec_generator usage
   - Update workflows in .claude/agents/architect.md

3. **Update code_developer Daemon** (2 hours)
   - Query database instead of file system
   - Implement progressive loading

### Follow-up (Week 2)

4. **Create Tests** (2 hours)
   - Unit tests for database methods
   - Integration tests for e2e flow

5. **Documentation** (1 hour)
   - Update agent documentation
   - Add usage examples

6. **Migration** (Optional)
   - Migrate existing monolithic specs to database
   - Convert selected specs to hierarchical

---

## Success Criteria

- [ ] Database methods fully tested
- [ ] Architect creates specs in database
- [ ] code_developer loads specs from database
- [ ] Hierarchical specs reduce context by 71%
- [ ] File system and database stay in sync
- [ ] All tests passing
- [ ] Documentation updated

---

## Related

- **PRIORITY**: 25 Phase 4 (Spec Migration)
- **CFRs**: CFR-016 (Incremental Steps), CFR-007 (Context Budget)
- **Skills**: technical-specification-handling v2.0.0
- **Docs**: docs/ARCHITECT_IMPLEMENTATION_STATUS.md

---

**Summary**: Phase 1 infrastructure complete. Database methods, schema, and skill wrapper are ready. Next: integrate with architect agent and code_developer daemon.
