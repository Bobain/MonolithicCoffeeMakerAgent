# GUIDELINE-006: Technical Specification Database Access

**Status**: Active
**Created**: 2025-10-24
**Last Updated**: 2025-10-24
**Related**: CFR-007 (Context Budget), CFR-015 (Centralized Database Storage)

## Summary

TechnicalSpecSkill (`.claude/skills/shared/technical_spec_database/unified_spec_skill.py`) is the **ONLY** authorized way to access technical specifications in the database. Direct SQL access to the `technical_specs` table is **FORBIDDEN** in agent code.

## Rationale

1. **Access Control**: Only architect can write specs; all agents can read
2. **Hierarchical Loading**: Supports CFR-007 context budget management
3. **Database-Only Pattern**: Eliminates filesystem/database sync issues
4. **Consistent Interface**: Single API for all spec operations
5. **Testing Support**: Hybrid mode allows test isolation

## The ONLY Way: TechnicalSpecSkill

### For architect (Writing Specs)

```python
from technical_spec_database.unified_spec_skill import TechnicalSpecSkill

spec_skill = TechnicalSpecSkill(agent_name="architect")

# Create hierarchical spec
spec_id = spec_skill.create_spec(
    spec_number=132,
    title="Work Creation & Task Decomposition",
    roadmap_item_id="PRIORITY-32",
    content={
        "overview": "High-level feature description...",
        "implementation": "Phase 1: ...\nPhase 2: ...",
        "api_design": "API endpoints...",
        "testing": "Test strategy..."
    },
    spec_type="hierarchical",
    estimated_hours=8.0
)

# Update status when complete
spec_skill.update_spec_status(spec_id, "complete", actual_hours=7.5)
```

### For code_developer (Reading Specs Hierarchically)

**CFR-007 Compliant** - Load only what you need:

```python
spec_skill = TechnicalSpecSkill(agent_name="code_developer")

# Level 1: Overview only (~500 tokens)
overview = spec_skill.get_spec_overview("SPEC-132")

# Level 2: Specific section (~1000 tokens)
impl_section = spec_skill.get_spec_section("SPEC-132", "implementation")

# Level 3: Full details (~2000 tokens)
details = spec_skill.get_spec_implementation_details("SPEC-132")

# Full spec (use sparingly)
full_spec = spec_skill.get_spec_by_id("SPEC-132")
```

## Hybrid Mode for Testing

Production code using TechnicalSpecSkill can still be tested with temporary databases:

```python
# In production module
class ImplementationTaskCreator:
    def __init__(self, db_path: str, agent_name: str = "architect"):
        self.db_path = db_path
        # Hybrid mode: skill for production, direct for tests
        self.use_skill = not db_path.endswith(".db")
        if self.use_skill:
            self.spec_skill = TechnicalSpecSkill(agent_name=agent_name)
        else:
            self.spec_skill = None

    def _read_spec(self, spec_id: str):
        if self.use_skill and self.spec_skill:
            # Production: use shared skill
            return self.spec_skill.get_spec_by_id(spec_id)
        else:
            # Testing: direct database access
            conn = sqlite3.connect(self.db_path)
            # ... test code ...
```

## FORBIDDEN Operations

### ❌ Direct SQL Access in Agent Code

```python
# FORBIDDEN in agent code (architect, code_developer, etc.)
conn = sqlite3.connect("coffee_maker.db")
cursor.execute("SELECT content FROM technical_specs WHERE id = ?", (spec_id,))
# This violates GUIDELINE-006!
```

### ❌ Reading Spec Files Directly

```python
# FORBIDDEN
content = Path("docs/architecture/specs/SPEC-132.md").read_text()
# Files are backup/reference only, not source of truth
```

### ❌ Writing Specs Without TechnicalSpecSkill

```python
# FORBIDDEN
cursor.execute("INSERT INTO technical_specs ...")
# Only TechnicalSpecSkill can write specs (enforces access control)
```

## Allowed Direct Access

### ✅ Utility/Admin Scripts

```python
# dump_technical_spec.py - Export utility
# Migration scripts - Schema changes
# These are infrastructure, not agent code
```

### ✅ Test Code

```python
# test_implementation_task_creator.py
@pytest.fixture
def hierarchical_spec(temp_db):
    """Insert test spec directly into temp database"""
    conn = sqlite3.connect(temp_db)
    cursor.execute("INSERT INTO technical_specs ...")
    # Tests can use direct access for setup
```

## Implementation Checklist

When adding spec reading to a new module:

- [ ] Import TechnicalSpecSkill from `.claude/skills/shared/technical_spec_database/`
- [ ] Initialize with appropriate agent_name
- [ ] Use hierarchical loading (get_spec_overview, get_spec_section, etc.)
- [ ] Implement hybrid mode if module needs testing
- [ ] Never use direct SQL in production code paths
- [ ] Document which agent uses this module (for access control)

## Enforcement

**Pre-commit Hook** (Future):
- Detect `SELECT.*FROM technical_specs` in agent code
- Warn about direct database access
- Require explicit @allow_direct_sql decorator for utilities

## Files Using TechnicalSpecSkill

### Production Code

- `coffee_maker/autonomous/implementation_task_creator.py` - architect task decomposition
- `coffee_maker/autonomous/implementation_task_manager.py` - code_developer spec reading
- `.claude/skills/shared/technical_spec_database/unified_spec_skill.py` - The skill itself

### Deleted (Old Pattern)

- ~~`coffee_maker/autonomous/spec_database.py`~~ - Deprecated dual filesystem+database pattern
- ~~`.claude/skills/shared/technical_specification_handling/spec_database_integration.py`~~ - Old skill
- ~~`coffee_maker/autonomous/create_spec_priority_31.py`~~ - One-off script
- ~~`coffee_maker/autonomous/create_spec_priority_32.py`~~ - One-off script

### Renamed (Clarity Improvement)

- ~~`coffee_maker/autonomous/work_creator.py`~~ → `implementation_task_creator.py`
- ~~`coffee_maker/autonomous/work_manager.py`~~ → `implementation_task_manager.py`

## Related Guidelines

- **CFR-007**: Context Budget Management → Use hierarchical loading
- **CFR-015**: Centralized Database Storage → All .db files in `data/`
- **GUIDELINE-004**: Git Tagging Workflow → Spec versioning strategy

## References

- TechnicalSpecSkill: `.claude/skills/shared/technical_spec_database/unified_spec_skill.py`
- Database Schema: `coffee_maker/autonomous/unified_database.py`
- Example Usage: `coffee_maker/autonomous/implementation_task_creator.py:_read_spec()`

---

**Remember**: TechnicalSpecSkill is not just a convenience—it's the **enforced interface** for all spec access. Direct SQL in agent code is a violation.
