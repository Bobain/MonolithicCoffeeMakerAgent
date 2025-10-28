# SPEC-115: Database Table Renaming for Agent Ownership Clarity

**Status**: Draft
**Created**: 2025-10-28
**Owner**: architect
**Complexity**: Medium (6/10)
**Estimated Hours**: 8-12 hours

---

## Overview

### Purpose

Rename 20 database tables to use consistent agent-based prefixes, improving code clarity and preventing ownership confusion. This conservative approach keeps good existing prefixes (like `roadmap_*`, `specs_*`, `orchestrator_*`) and only fixes broken, missing, or misleading prefixes.

### Goals

1. **Clear ownership**: Table names immediately indicate which agent owns them
2. **Prevent confusion**: Fix misleading prefixes (e.g., `review_commit` owned by `code_developer`, not `code_reviewer`)
3. **Consistency**: Apply consistent prefix patterns across all agents
4. **Zero downtime**: Migration with backward compatibility during transition

### Success Criteria

- [ ] All 20 tables renamed with proper agent-based prefixes
- [ ] All Python code updated to use new table names
- [ ] Migration script tested on test database
- [ ] All tests passing after migration
- [ ] Documentation updated
- [ ] No breaking changes for existing deployments

---

## Current State Analysis

### Tables with Good Prefixes (KEEP AS-IS)

**12 tables** already have clear, consistent prefixes:

| Table | Prefix | Owner | Status |
|-------|--------|-------|--------|
| `roadmap_priority` | `roadmap_` | project_manager | ✅ Keep |
| `roadmap_metadata` | `roadmap_` | project_manager | ✅ Keep |
| `roadmap_audit` | `roadmap_` | project_manager | ✅ Keep |
| `roadmap_notification` | `roadmap_` | project_manager | ✅ Keep |
| `specs_specification` | `specs_` | architect | ✅ Keep |
| `specs_task` | `specs_` | architect | ✅ Keep |
| `specs_task_dependency` | `specs_` | architect | ✅ Keep |
| `orchestrator_state` | `orchestrator_` | orchestrator | ✅ Keep |
| `orchestrator_task` | `orchestrator_` | orchestrator | ✅ Keep |
| `orchestrator_bug` | `orchestrator_` | orchestrator | ✅ Keep |
| `review_code_review` | `review_` | code_reviewer | ✅ Keep |
| `migrations` | (none) | shared | ✅ Keep (system table) |

### Tables to Rename (20 tables)

#### Category 1: Misleading Prefix (1 table)

| Old Name | New Name | Owner | Issue |
|----------|----------|-------|-------|
| `review_commit` | `developer_commit` | code_developer | ❌ `review_` implies code_reviewer ownership |

#### Category 2: Missing Prefix (3 tables)

| Old Name | New Name | Owner | Issue |
|----------|----------|-------|-------|
| `command_token_usage` | `developer_token_usage` | code_developer | ❌ No prefix |
| `agent_lifecycle` | `orchestrator_agent_lifecycle` | orchestrator | ❌ Should match `orchestrator_*` |
| `notifications` | `shared_notifications` | shared | ❌ No prefix for inter-agent messaging |

#### Category 3: Generic/Vague Prefix (3 tables)

| Old Name | New Name | Owner | Issue |
|----------|----------|-------|-------|
| `system_schema_metadata` | `architect_schema_metadata` | architect | ❌ `system_` too vague |
| `notification_user` | `shared_notification_user` | shared | ❌ Should be explicitly shared |
| `notification_system_state` | `shared_notification_state` | shared | ❌ Should be explicitly shared |
| `system_audit` | `shared_audit` | shared | ❌ `system_` too generic |

#### Category 4: Wrong Prefix - Unmapped Tables (13 tables)

All `ui_*` tables were created before agent roles were finalized. They need proper agent-based prefixes:

**Assistant Tables** (3):
- `ui_bug_reports` → `assistant_bug_reports`
- `ui_demo_sessions` → `assistant_demo_sessions`
- `ui_delegation_log` → `assistant_delegation_log`

**UX Design Expert Tables** (4):
- `ui_component_library` → `ux_component_library`
- `ui_design_debt` → `ux_design_debt`
- `ui_design_specs` → `ux_design_specs`
- `ui_design_tokens` → `ux_design_tokens`

**User Listener Tables** (3):
- `ui_conversation_context` → `listener_conversation_context`
- `ui_intent_classification` → `listener_intent_classification`
- `ui_routing_log` → `listener_routing_log`

**Other Unmapped** (2):
- `agent_message` → `shared_agent_message` (shared)
- `metrics_subtask` → `manager_metrics_subtask` (project_manager)

---

## Architecture

### Prefix Convention

| Prefix | Agent | Purpose |
|--------|-------|---------|
| `manager_` | project_manager | Strategic planning, ROADMAP management |
| `architect_` | architect | Technical design, specifications |
| `developer_` | code_developer | Implementation, commits, tokens |
| `reviewer_` | code_reviewer | Quality assurance, code reviews |
| `orchestrator_` | orchestrator | Multi-agent coordination |
| `listener_` | user_listener | User interaction, routing |
| `assistant_` | assistant | Documentation, demos, delegation |
| `ux_` | ux_design_expert | Design system, tokens, specs |
| `shared_` | (multiple) | Cross-agent infrastructure |

**Note**: Existing good prefixes kept as-is:
- `roadmap_` for project_manager (descriptive, well-known)
- `specs_` for architect (clear, established)
- `orchestrator_` for orchestrator (already perfect)

### Migration Strategy

**Phase 1: Create Views (Backward Compatibility)**
```sql
-- Example: Create view with old name pointing to new table
CREATE VIEW review_commit AS SELECT * FROM developer_commit;
```

**Phase 2: Rename Tables**
```sql
ALTER TABLE review_commit RENAME TO developer_commit;
```

**Phase 3: Update Code**
- Update all Python code to use new table names
- Keep views for 1 release cycle (backward compatibility)

**Phase 4: Remove Views**
- After all code updated, drop compatibility views

---

## Implementation Tasks

### TASK-115-1: Create Migration Script (2 hours)

**Files**: `data/migrations/004_rename_tables_agent_ownership.sql`

**Implementation**:
```sql
-- Migration: Rename tables for agent ownership clarity
-- Date: 2025-10-28
-- SPEC: SPEC-115

BEGIN TRANSACTION;

-- 1. Misleading prefix
ALTER TABLE review_commit RENAME TO developer_commit;

-- 2. Missing prefix
ALTER TABLE command_token_usage RENAME TO developer_token_usage;
ALTER TABLE agent_lifecycle RENAME TO orchestrator_agent_lifecycle;
ALTER TABLE notifications RENAME TO shared_notifications;

-- 3. Generic/vague prefix
ALTER TABLE system_schema_metadata RENAME TO architect_schema_metadata;
ALTER TABLE notification_user RENAME TO shared_notification_user;
ALTER TABLE notification_system_state RENAME TO shared_notification_state;
ALTER TABLE system_audit RENAME TO shared_audit;

-- 4. Unmapped tables - Assistant
ALTER TABLE ui_bug_reports RENAME TO assistant_bug_reports;
ALTER TABLE ui_demo_sessions RENAME TO assistant_demo_sessions;
ALTER TABLE ui_delegation_log RENAME TO assistant_delegation_log;

-- 5. Unmapped tables - UX Design Expert
ALTER TABLE ui_component_library RENAME TO ux_component_library;
ALTER TABLE ui_design_debt RENAME TO ux_design_debt;
ALTER TABLE ui_design_specs RENAME TO ux_design_specs;
ALTER TABLE ui_design_tokens RENAME TO ux_design_tokens;

-- 6. Unmapped tables - User Listener
ALTER TABLE ui_conversation_context RENAME TO listener_conversation_context;
ALTER TABLE ui_intent_classification RENAME TO listener_intent_classification;
ALTER TABLE ui_routing_log RENAME TO listener_routing_log;

-- 7. Other unmapped
ALTER TABLE agent_message RENAME TO shared_agent_message;
ALTER TABLE metrics_subtask RENAME TO manager_metrics_subtask;

-- Record migration
INSERT INTO migrations (name) VALUES ('004_rename_tables_agent_ownership');

COMMIT;
```

**Tests**: Run on test database, verify all tables renamed

**Dependencies**: None

**Success Criteria**: Migration runs without errors, all 20 tables renamed

---

### TASK-115-2: Create Backward Compatibility Views (1 hour)

**Files**: `data/migrations/004b_compatibility_views.sql`

**Implementation**:
```sql
-- Backward compatibility views for renamed tables
-- These allow old code to continue working during transition

BEGIN TRANSACTION;

-- Create views with old names
CREATE VIEW review_commit AS SELECT * FROM developer_commit;
CREATE VIEW command_token_usage AS SELECT * FROM developer_token_usage;
CREATE VIEW agent_lifecycle AS SELECT * FROM orchestrator_agent_lifecycle;
CREATE VIEW notifications AS SELECT * FROM shared_notifications;
CREATE VIEW system_schema_metadata AS SELECT * FROM architect_schema_metadata;
CREATE VIEW notification_user AS SELECT * FROM shared_notification_user;
CREATE VIEW notification_system_state AS SELECT * FROM shared_notification_state;
CREATE VIEW system_audit AS SELECT * FROM shared_audit;
CREATE VIEW ui_bug_reports AS SELECT * FROM assistant_bug_reports;
CREATE VIEW ui_demo_sessions AS SELECT * FROM assistant_demo_sessions;
CREATE VIEW ui_delegation_log AS SELECT * FROM assistant_delegation_log;
CREATE VIEW ui_component_library AS SELECT * FROM ux_component_library;
CREATE VIEW ui_design_debt AS SELECT * FROM ux_design_debt;
CREATE VIEW ui_design_specs AS SELECT * FROM ux_design_specs;
CREATE VIEW ui_design_tokens AS SELECT * FROM ux_design_tokens;
CREATE VIEW ui_conversation_context AS SELECT * FROM listener_conversation_context;
CREATE VIEW ui_intent_classification AS SELECT * FROM listener_intent_classification;
CREATE VIEW ui_routing_log AS SELECT * FROM listener_routing_log;
CREATE VIEW agent_message AS SELECT * FROM shared_agent_message;
CREATE VIEW metrics_subtask AS SELECT * FROM manager_metrics_subtask;

COMMIT;
```

**Tests**: Verify old code still works with views

**Dependencies**: TASK-115-1

**Success Criteria**: All 20 views created, old table names still accessible

---

### TASK-115-3: Find and Update Code References (3 hours)

**Files**: All Python files referencing renamed tables

**Implementation**:
```bash
# Find all references to old table names
for table in review_commit command_token_usage agent_lifecycle notifications \
    system_schema_metadata notification_user notification_system_state \
    system_audit ui_bug_reports ui_demo_sessions ui_delegation_log \
    ui_component_library ui_design_debt ui_design_specs ui_design_tokens \
    ui_conversation_context ui_intent_classification ui_routing_log \
    agent_message metrics_subtask; do

    echo "=== Finding references to: $table ==="
    grep -r "$table" coffee_maker/ tests/ --include="*.py"
done
```

**Update patterns**:
- SQL queries: `FROM review_commit` → `FROM developer_commit`
- Table constants: `TABLE_REVIEW_COMMIT = "review_commit"` → `TABLE_DEVELOPER_COMMIT = "developer_commit"`
- Comments: Update table references in docstrings

**Tests**: Run full test suite after each batch of changes

**Dependencies**: TASK-115-2

**Success Criteria**: All code references updated, tests passing

---

### TASK-115-4: Update Documentation (1 hour)

**Files**:
- `docs/DATABASE_SCHEMA.md` (if exists)
- Agent READMEs (`.claude/commands/agents/*/README.md`)
- Any database-related guides

**Implementation**:
- Update table ownership documentation
- Update query examples
- Add migration notes

**Tests**: Manual review of documentation

**Dependencies**: TASK-115-3

**Success Criteria**: All documentation reflects new table names

---

### TASK-115-5: Create Removal Script for Compatibility Views (1 hour)

**Files**: `data/migrations/005_remove_compatibility_views.sql`

**Implementation**:
```sql
-- Remove backward compatibility views after code updated
-- Run this AFTER all code has been updated to use new names

BEGIN TRANSACTION;

-- Drop all compatibility views
DROP VIEW IF EXISTS review_commit;
DROP VIEW IF EXISTS command_token_usage;
DROP VIEW IF EXISTS agent_lifecycle;
DROP VIEW IF EXISTS notifications;
DROP VIEW IF EXISTS system_schema_metadata;
DROP VIEW IF EXISTS notification_user;
DROP VIEW IF EXISTS notification_system_state;
DROP VIEW IF EXISTS system_audit;
DROP VIEW IF EXISTS ui_bug_reports;
DROP VIEW IF EXISTS ui_demo_sessions;
DROP VIEW IF EXISTS ui_delegation_log;
DROP VIEW IF EXISTS ui_component_library;
DROP VIEW IF EXISTS ui_design_debt;
DROP VIEW IF EXISTS ui_design_specs;
DROP VIEW IF EXISTS ui_design_tokens;
DROP VIEW IF EXISTS ui_conversation_context;
DROP VIEW IF EXISTS ui_intent_classification;
DROP VIEW IF EXISTS ui_routing_log;
DROP VIEW IF EXISTS agent_message;
DROP VIEW IF EXISTS metrics_subtask;

-- Record cleanup
INSERT INTO migrations (name) VALUES ('005_remove_compatibility_views');

COMMIT;
```

**Tests**: Verify views removed, code still works with new table names

**Dependencies**: TASK-115-4

**Success Criteria**: Views removed cleanly, no code breakage

---

### TASK-115-6: Testing and Validation (2 hours)

**Tests**:

1. **Unit Tests**: All existing unit tests pass
2. **Integration Tests**: Database operations work correctly
3. **Agent Tests**: Each agent can read/write to its tables
4. **Migration Test**: Run migration on copy of production database

**Validation Checklist**:
- [ ] All 20 tables renamed correctly
- [ ] Indexes and foreign keys intact
- [ ] All code references updated
- [ ] Documentation accurate
- [ ] No performance regression
- [ ] Backward compatibility views working
- [ ] Old code works with views
- [ ] New code works with new names

**Dependencies**: All previous tasks

**Success Criteria**: All tests passing, no regressions

---

## Database Schema Impact

### Tables Affected (20)

**By Agent**:
- code_developer: 2 tables
- orchestrator: 1 table
- architect: 1 table
- shared: 5 tables
- assistant: 3 tables
- ux_design_expert: 4 tables
- user_listener: 3 tables
- project_manager: 1 table

### Foreign Keys

**Tables with FK constraints**:
- `developer_commit` (FK to roadmap_priority)
- `architect_schema_metadata` (none)
- `manager_metrics_subtask` (likely FK to roadmap_priority)

**Action**: Verify FK constraints remain intact after rename

### Indexes

**Affected indexes** (will be automatically renamed by SQLite):
- All indexes on renamed tables get new names automatically
- Verify index performance after migration

---

## Testing Strategy

### Pre-Migration Testing

1. **Backup Databases**:
   ```bash
   cp data/roadmap.db data/roadmap.db.backup
   cp data/development.db data/development.db.backup
   ```

2. **Test Migration Script**:
   ```bash
   sqlite3 data/test_roadmap.db < data/migrations/004_rename_tables_agent_ownership.sql
   ```

3. **Verify Table Renames**:
   ```bash
   sqlite3 data/test_roadmap.db ".tables"
   ```

### Post-Migration Testing

1. **Run Test Suite**: `pytest`
2. **Agent Integration Tests**: Test each agent's database operations
3. **Performance Tests**: Verify query performance unchanged

### Rollback Plan

If migration fails:
```bash
# Restore from backup
cp data/roadmap.db.backup data/roadmap.db
cp data/development.db.backup data/development.db
```

---

## Acceptance Criteria

### Functional Requirements

- [ ] All 20 tables renamed with correct agent-based prefixes
- [ ] All Python code updated to use new table names
- [ ] Backward compatibility views created
- [ ] Migration script tested on test database
- [ ] All tests passing (unit, integration, agent tests)
- [ ] Zero downtime during migration
- [ ] Foreign keys and indexes intact

### Non-Functional Requirements

- [ ] Migration completes in < 5 seconds
- [ ] No performance degradation in queries
- [ ] Documentation updated and accurate
- [ ] Rollback plan documented and tested

### Code Quality

- [ ] Migration scripts follow SQL best practices
- [ ] Code changes follow Python style guide
- [ ] All table references use constants (not hardcoded strings)
- [ ] Comprehensive error handling

---

## Dependencies

### Internal Dependencies

- **Database**: `data/roadmap.db`, `data/development.db`
- **Migration System**: Existing migration tracking in `migrations` table

### External Dependencies

- None (SQLite built-in ALTER TABLE)

### Risks

1. **Code References Missed**: Some table references not updated
   - **Mitigation**: Comprehensive grep search, test coverage

2. **Foreign Key Issues**: FK constraints broken by rename
   - **Mitigation**: Test on copy first, verify constraints

3. **View Performance**: Views might be slower than tables
   - **Mitigation**: Views are temporary, removed after code updated

---

## Timeline

**Total Estimated Time**: 10 hours

| Task | Duration | Dependencies |
|------|----------|--------------|
| TASK-115-1: Migration Script | 2h | None |
| TASK-115-2: Compatibility Views | 1h | TASK-115-1 |
| TASK-115-3: Update Code | 3h | TASK-115-2 |
| TASK-115-4: Update Docs | 1h | TASK-115-3 |
| TASK-115-5: Removal Script | 1h | TASK-115-4 |
| TASK-115-6: Testing | 2h | All tasks |

**Recommended Approach**: Complete in 1-2 work sessions

---

## Related Documents

- **CFR-015**: Centralized Database Storage
- **Database Schema Introspection**: `.claude/skills/shared/introspection-database/SKILL.md`
- **Agent Ownership**: `docs/AGENT_OWNERSHIP.md`

---

## Notes

### Why Conservative Approach?

- **Low Risk**: Only fixing broken prefixes, not changing everything
- **Backward Compatible**: Views allow gradual code migration
- **Established Patterns**: Keeps good prefixes like `roadmap_`, `specs_`
- **Clear Benefits**: Fixes actual confusion (e.g., `review_commit` misleading)

### Future Considerations

After this migration, consider:
- Documenting table ownership in database metadata
- Adding ownership checks in database access layer
- Creating admin tool to visualize agent→table ownership

---

**Version**: 1.0.0
**Last Updated**: 2025-10-28
**Estimated Tokens**: ~3,500 tokens
