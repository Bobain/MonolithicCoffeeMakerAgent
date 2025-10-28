# Technical Specification Handling - Database-First Architecture

**CRITICAL ENFORCEMENT**: The technical_specification_handling skill now enforces database-first architecture where ALL specifications are stored in the `specs_specification` table. Files are OPTIONAL backup/export only.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  TechnicalSpecificationHandlingSkill          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ✅ PRIMARY STORAGE: specs_specification (Database)           │
│     - All specs written here by architect                    │
│     - All specs read FROM here by code_developer             │
│     - Persistent, queryable, audited                         │
│                                                               │
│  ⚠️  SECONDARY (BACKUP): File system (Optional only)          │
│     - export_file=True only creates backup                   │
│     - NOT used for primary retrieval                         │
│     - Not required for operation                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Changes from File-Based to Database-First

### Before (File-Based - WRONG)
```python
# WRONG: Specs stored in files
spec_file = Path("docs/architecture/specs/SPEC-104-spec.md")
spec_file.write_text(content)  # PRIMARY STORAGE
spec = spec_file.read_text()   # Read from file
```

### After (Database-First - CORRECT)
```python
# CORRECT: Specs stored in database
db = DomainWrapper(AgentType.ARCHITECT)

# Write to database
spec_data = {
    "id": "SPEC-104",
    "spec_number": 104,
    "title": "Example Spec",
    "content": json.dumps(spec_content),  # Store JSON in database!
    "updated_at": datetime.now().isoformat(),
    "updated_by": "architect",
}

db.write("specs_specification", spec_data)  # PRIMARY STORAGE

# Read from database
results = db.read("specs_specification", {"id": "SPEC-104"})  # From database!

# Optional: Export to file as backup
if export_file:
    spec_file = Path("docs/architecture/specs/SPEC-104-spec.md")
    spec_file.write_text(spec_content)  # BACKUP ONLY
```

## Implementation Details

### 1. Database Schema (`specs_specification` table)

```sql
CREATE TABLE "specs_specification" (
    id TEXT PRIMARY KEY,              -- "SPEC-104"
    spec_number INTEGER NOT NULL,     -- 104 (unique)
    title TEXT NOT NULL,              -- "Spec title"
    roadmap_item_id TEXT,             -- "US-104"
    status TEXT DEFAULT 'draft',      -- 'draft', 'ready', 'approved'
    spec_type TEXT DEFAULT 'monolithic',  -- 'monolithic' or 'hierarchical'
    file_path TEXT,                   -- OPTIONAL: path if exported to file
    content TEXT,                     -- CRITICAL: Full spec content (JSON or markdown)
    dependencies TEXT,                -- JSON array of dependencies
    estimated_hours REAL,             -- Estimated implementation hours
    updated_at TEXT NOT NULL,         -- ISO timestamp
    updated_by TEXT NOT NULL,         -- Agent that updated (e.g., "architect")
    total_phases INTEGER,             -- For hierarchical specs
    phase_files TEXT,                 -- JSON array of phase names
    current_phase_status TEXT,        -- Current phase progress
);
```

### 2. Content Storage Format

#### Monolithic Specs
```python
# Content is plain markdown
content = """# SPEC-104: Example Spec

## Overview
This is an example specification.

## Implementation
Details here...
"""

# Stored in database as-is
db.write("specs_specification", {
    "id": "SPEC-104",
    "spec_number": 104,
    "title": "Example Spec",
    "spec_type": "monolithic",
    "content": content,  # Plain text, not JSON
    ...
})
```

#### Hierarchical Specs
```python
# Content is JSON with phase structure
spec_content = {
    "type": "hierarchical",
    "spec_id": "SPEC-105",
    "title": "Multi-phase Spec",
    "phases": {
        "Phase 1": {
            "number": 1,
            "name": "Phase 1",
            "description": "First phase",
            "hours": 8,
            "content": "Phase 1 detailed content..."
        },
        "Phase 2": {
            "number": 2,
            "name": "Phase 2",
            "description": "Second phase",
            "hours": 12,
            "content": "Phase 2 detailed content..."
        }
    }
}

# Stored in database as JSON string
import json
db.write("specs_specification", {
    "id": "SPEC-105",
    "spec_number": 105,
    "title": "Multi-phase Spec",
    "spec_type": "hierarchical",
    "content": json.dumps(spec_content),  # JSON string in database!
    "total_phases": 2,
    "phase_files": json.dumps(["Phase 1", "Phase 2"]),
    ...
})
```

### 3. Skill Methods and Database Operations

#### `create_hierarchical()`
```python
# Input
result = skill.execute(
    action="create_hierarchical",
    us_number="104",
    title="Test Spec",
    phases=[
        {"name": "Phase 1", "description": "First phase", "hours": 8}
    ],
    roadmap_item_id="US-104",
    export_file=False  # NO file export by default
)

# Output
result = {
    "result": {
        "spec_id": "SPEC-104",
        "roadmap_item_id": "US-104",
        "spec_type": "hierarchical",
        "total_phases": 1,
    },
    "error": None,
    "source": "database"  # ✅ Always database!
}

# Behind the scenes
1. Build JSON spec content
2. Write to specs_specification table (DomainWrapper.write)
3. Optional: Export to file if export_file=True
4. Return success
```

#### `find()` / `get_spec()`
```python
# Input
result = skill.execute(action="find", us_id="US-104")

# Output
result = {
    "result": {
        "id": "SPEC-104",
        "title": "Test Spec",
        "spec_type": "hierarchical",
        "content": '{"type": "hierarchical", ...}',  # From database!
        "total_phases": 1,
        # ... all database fields
    },
    "error": None,
    "source": "database"  # ✅ Always from database!
}

# Behind the scenes
1. Extract spec number from US ID
2. Query specs_specification table (DomainWrapper.read)
3. Return spec record from database
```

#### `read_hierarchical_spec()`
```python
# Input - Progressive Disclosure
result = skill.execute(
    action="read_hierarchical_spec",
    us_id="US-104",
    phase="Phase 1"  # Request specific phase
)

# Output
result = {
    "result": {
        "spec_type": "hierarchical",
        "current_phase": "Phase 1",
        "total_phases": 1,
        "phase_content": "Phase 1 detailed content...",
        "phase_description": "First phase",
        "phase_hours": 8,
    },
    "error": None,
    "source": "database"  # ✅ From database JSON!
}

# Behind the scenes
1. Query specs_specification table (DomainWrapper.read)
2. Parse JSON content
3. Extract specific phase (progressive disclosure = context savings!)
4. Return only requested phase content
```

#### `update_spec()`
```python
# Input
result = skill.execute(
    action="update_spec",
    us_id="US-104",
    content="Updated content..."
)

# Output
result = {
    "result": True,
    "error": None,
    "source": "database"  # ✅ Updated in database!
}

# Behind the scenes
1. Extract spec number from US ID
2. Update specs_specification table (DomainWrapper.update)
3. Add audit trail
4. Return success
```

#### `list_specs()`
```python
# Input
result = skill.execute(action="list_specs")

# Output
result = {
    "result": [
        {"id": "SPEC-001", "title": "...", "content": "...", ...},
        {"id": "SPEC-002", "title": "...", "content": "...", ...},
        # All specs from database
    ],
    "error": None,
    "source": "database"  # ✅ All from database!
}
```

## Permission Enforcement

The skill uses `DomainWrapper` to enforce proper permissions:

```python
# Only architect can write to specs_specification
db = DomainWrapper(AgentType.ARCHITECT)
db.write("specs_specification", spec_data)  # ✅ Allowed

# code_developer can read from specs_specification
db = DomainWrapper(AgentType.CODE_DEVELOPER)
specs = db.read("specs_specification", {"id": "SPEC-104"})  # ✅ Allowed

# project_manager can read everything (monitoring)
db = DomainWrapper(AgentType.PROJECT_MANAGER)
all_specs = db.read("specs_specification")  # ✅ Allowed
```

## Audit Logging

All database writes are automatically logged to `system_audit` table:

```sql
-- Automatic audit trail
INSERT INTO system_audit (table_name, item_id, action, changed_by, changed_at)
VALUES ('specs_specification', 'SPEC-104', 'create', 'architect', '2025-10-26T...')
```

## Usage Examples

### Architect Creating a Spec
```python
from coffee_maker.autonomous.skill_loader import load_skill

skill = load_skill("technical-specification-handling")

result = skill.execute(
    action="create_hierarchical",
    agent_type="ARCHITECT",  # Pass agent type
    us_number="104",
    title="Orchestrator Continuous Work Loop",
    phases=[
        {
            "name": "Database Setup",
            "description": "Create required tables",
            "hours": 8,
            "content": "..."
        },
        {
            "name": "Implementation",
            "description": "Implement core logic",
            "hours": 32,
            "content": "..."
        }
    ],
    roadmap_item_id="US-104",
    estimated_hours=40,
    export_file=True  # Optional: Also save to file
)

# Returns: {"result": {...}, "error": None, "source": "database"}
```

### Code Developer Reading a Spec
```python
# Read full monolithic spec
spec = skill.execute(
    action="get_spec",
    agent_type="CODE_DEVELOPER",
    us_id="US-104"
)

# Read specific phase from hierarchical spec (progressive disclosure!)
phase = skill.execute(
    action="read_hierarchical_spec",
    agent_type="CODE_DEVELOPER",
    us_id="US-104",
    phase="Implementation"
)

# This returns ONLY the "Implementation" phase content
# NOT the entire 40KB spec (context budget optimization!)
```

## Key Guarantees

### ✅ ALWAYS Database
- All `create_*` operations write to `specs_specification` table
- All `read_*` operations query `specs_specification` table
- All `update_*` operations modify `specs_specification` table
- All responses include `"source": "database"`

### ✅ Files are Backup Only
- Files created ONLY if `export_file=True` (default: False)
- Files NOT used for primary retrieval
- Files NOT required for system operation
- Can be safely deleted without data loss

### ✅ Permission Enforcement
- `DomainWrapper` enforces agent-based permissions
- Only authorized agents can read/write
- Audit trail logged for all operations

### ✅ Progressive Disclosure
- Hierarchical specs load only requested phases
- Saves context budget (only ~10KB instead of 40KB)
- Full spec available if needed

## Migration from File-Based System

If you have specs in files that need to be migrated to the database:

```python
from pathlib import Path
from coffee_maker.database.domain_wrapper import DomainWrapper, AgentType

# Read spec from file
spec_file = Path("docs/architecture/specs/SPEC-104-spec.md")
content = spec_file.read_text()

# Write to database
db = DomainWrapper(AgentType.ARCHITECT)
db.write("specs_specification", {
    "id": "SPEC-104",
    "spec_number": 104,
    "title": "Spec Title",
    "roadmap_item_id": "US-104",
    "spec_type": "monolithic",
    "content": content,
    "updated_at": datetime.now().isoformat(),
    "updated_by": "architect",
})

# File can now be deleted (or kept as backup)
```

## Testing

The skill includes comprehensive validation:

1. **Database-first verification**: All create/read/update operations tested
2. **Permission enforcement**: DomainWrapper permission checks validated
3. **Audit logging**: Operations logged to system_audit table
4. **Progressive disclosure**: Hierarchical phase loading validated
5. **Format validation**: JSON content structure verified

## Troubleshooting

### Spec not found
```python
# If you get "No spec found in database"
# Check if spec was actually written to database:
sqlite3 data/roadmap.db "SELECT id, title FROM specs_specification WHERE id = 'SPEC-104'"
```

### Permission denied
```python
# If you get "PermissionError"
# Verify agent type has permission:
# - ARCHITECT: Can write to specs_specification
# - CODE_DEVELOPER: Can read from specs_specification
# - PROJECT_MANAGER: Can read all (monitoring)
```

### Content retrieval
```python
# Always query database, NOT files
db = DomainWrapper(AgentType.CODE_DEVELOPER)
spec = db.read("specs_specification", {"id": "SPEC-104"})
content = spec[0]["content"]  # Content from database!
```

## Summary

The technical_specification_handling skill enforces database-first architecture:

1. **All specs stored in `specs_specification` table** - Single source of truth
2. **Files are optional backup only** - NOT required for operation
3. **Permission enforced via DomainWrapper** - Agent-based access control
4. **Progressive disclosure for hierarchical specs** - Context budget optimization
5. **Full audit trail** - All operations logged to system_audit table

This ensures consistency, auditability, and optimal resource usage across the entire system.
