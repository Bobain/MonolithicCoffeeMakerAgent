# Database Consolidation Plan

**Date**: 2025-10-25
**Status**: Draft
**Goal**: Consolidate all databases into `data/roadmap.db` with logical organization

---

## Current State

### Active Databases (9 total)

| Database | Size | Tables | Purpose | Action |
|----------|------|--------|---------|--------|
| `data/roadmap.db` | 1.6 MB | 11 | **PRIMARY** - Roadmap, specs, reviews | Keep & consolidate into |
| `data/orchestrator.db` | 96 KB | 4 | Parallel execution tracking | **MERGE** |
| `data/notifications.db` | 3.6 MB | 2 | User notifications | **MERGE** |
| `data/agent_messages.db` | 24 KB | 1 | Agent communication | **MERGE** |
| `data/metrics.db` | 232 KB | 5 | Langfuse observability | **KEEP SEPARATE** (external) |
| `coffee_maker.db` | 112 KB | 4 | Legacy root database | **MERGE** |
| `data/task_metrics.db` | 24 KB | 1 | Task performance | **MERGE** |
| `data/test_unified.db` | 96 KB | 5 | Test database | **DELETE** |
| `data/unified_roadmap_specs.db` | 0 KB | 0 | Empty | **DELETE** |

---

## Proposed Organization

### SQLite Schema Limitation

**IMPORTANT**: SQLite doesn't support PostgreSQL-style schemas (`schema.table`).

**Solution**: Use **logical grouping via table name prefixes** + **views** for clean access.

### Table Naming Convention

```
<domain>_<entity>

Examples:
  roadmap_priority (instead of roadmap_items)
  specs_specification (instead of technical_specs)
  review_code_review (instead of code_reviews)
```

### Consolidated Table Structure

#### **DOMAIN: roadmap** (Strategic Planning)

| Current Name | New Name | Description |
|--------------|----------|-------------|
| `roadmap_items` | `roadmap_priority` | Strategic priorities from ROADMAP.md |
| `roadmap_audit` | `roadmap_audit` | Change tracking for priorities |
| `roadmap_metadata` | `roadmap_metadata` | Configuration (last sync time, etc.) |
| `roadmap_update_notifications` | `roadmap_notification` | Status update requests |

#### **DOMAIN: specs** (Technical Specifications)

| Current Name | New Name | Description |
|--------------|----------|-------------|
| `technical_specs` | `specs_specification` | Technical spec content (database-only) |
| `implementation_tasks` | `specs_task` | Atomic tasks for parallel execution |
| `task_group_dependencies` | `specs_task_dependency` | Task ordering constraints |

#### **DOMAIN: review** (Code Review)

| Current Name | New Name | Description |
|--------------|----------|-------------|
| `code_reviews` | `review_code_review` | Automated code review results |
| `implementation_commits` | `review_commit` | Commit tracking per priority |

#### **DOMAIN: orchestrator** (Parallel Execution)

| Current Name | New Name | Source | Description |
|--------------|----------|--------|-------------|
| `agent_lifecycle` | `orchestrator_agent_lifecycle` | orchestrator.db | Agent process tracking |
| `orchestrator_state` | `orchestrator_state` | orchestrator.db | Orchestrator configuration |
| `orchestrator_tasks` | `orchestrator_task` | orchestrator.db | Task queue |
| `bugs` | `orchestrator_bug` | orchestrator.db | Bug tracking |

#### **DOMAIN: notification** (User Notifications)

| Current Name | New Name | Source | Description |
|--------------|----------|--------|-------------|
| `notifications` (in roadmap.db) | `notification_roadmap` | roadmap.db | Roadmap-related notifications |
| `notifications` (in notifications.db) | `notification_user` | notifications.db | User-facing notifications |
| `system_state` | `notification_system_state` | notifications.db | Notification system state |

#### **DOMAIN: messaging** (Agent Communication)

| Current Name | New Name | Source | Description |
|--------------|----------|--------|-------------|
| `agent_messages` | `messaging_agent_message` | agent_messages.db | Inter-agent messages |

#### **DOMAIN: metrics** (Performance Tracking)

| Current Name | New Name | Source | Description |
|--------------|----------|--------|-------------|
| `subtask_metrics` | `metrics_subtask` | task_metrics.db | Task performance metrics |

#### **DOMAIN: system** (Infrastructure)

| Current Name | New Name | Description |
|--------------|----------|-------------|
| `audit_trail` | `system_audit` | Universal audit trail |
| `schema_metadata` | `system_schema_metadata` | Database self-documentation |

---

## Migration Strategy

### Phase 1: Consolidate Data (No Renames Yet)

1. **Merge `data/orchestrator.db` → `data/roadmap.db`**
   - Copy tables: `agent_lifecycle`, `orchestrator_state`, `orchestrator_tasks`, `bugs`
   - Preserve all data

2. **Merge `data/notifications.db` → `data/roadmap.db`**
   - Rename table: `notifications` → `notification_user` (conflict with existing)
   - Copy table: `system_state` → `notification_system_state`

3. **Merge `data/agent_messages.db` → `data/roadmap.db`**
   - Copy table: `agent_messages`

4. **Merge `coffee_maker.db` → `data/roadmap.db`**
   - Copy table: `schema_metadata` (merge with existing)
   - Copy table: `task_group_dependencies`
   - Skip empty tables: `commits`, `implementation_tasks`

5. **Merge `data/task_metrics.db` → `data/roadmap.db`**
   - Copy table: `subtask_metrics`

### Phase 2: Rename Tables for Organization

**Create migration script** that:
1. Renames all tables to new convention
2. Updates all foreign key references
3. Creates views for backward compatibility

**Example**:
```sql
-- Rename table
ALTER TABLE roadmap_items RENAME TO roadmap_priority;

-- Create backward-compatible view
CREATE VIEW roadmap_items AS SELECT * FROM roadmap_priority;
```

### Phase 3: Update Code References

**Find and replace** in codebase:
- `roadmap_items` → `roadmap_priority`
- `technical_specs` → `specs_specification`
- `implementation_tasks` → `specs_task`
- etc.

**Affected files** (estimate ~50-100 files):
- `coffee_maker/autonomous/roadmap_database.py`
- `coffee_maker/autonomous/spec_handler.py`
- `coffee_maker/orchestrator/*.py`
- All CLI commands
- All agent code

### Phase 4: Document All Tables

Add metadata for ALL tables to `system_schema_metadata`:
- Currently: 3 tables documented (27%)
- Target: 25+ tables documented (100%)

---

## Benefits

✅ **Single Source of Truth**: One database file instead of 9
✅ **Logical Organization**: Clear domain separation
✅ **Self-Documenting**: All tables have metadata
✅ **Easier Backup**: One file to backup
✅ **Better Performance**: No cross-database queries
✅ **Cleaner Codebase**: Consistent naming convention

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Data loss during merge | Full backup before migration |
| Broken code references | Create views for backward compatibility |
| Foreign key violations | Check constraints before rename |
| Long migration time | Run incrementally, test after each phase |

---

## Estimated Effort

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Consolidate Data | 2-3 hours | HIGH |
| Phase 2: Rename Tables | 1-2 hours | MEDIUM |
| Phase 3: Update Code | 3-4 hours | HIGH |
| Phase 4: Document All | 2-3 hours | MEDIUM |
| **TOTAL** | **8-12 hours** | - |

---

## Next Steps

1. **Get user approval** for consolidation plan
2. **Backup all databases** to `data/backup-YYYY-MM-DD/`
3. **Run Phase 1** migration (consolidate data)
4. **Test** that all functionality still works
5. **Proceed** with Phase 2-4 incrementally

---

## Open Questions

1. Should we keep `data/metrics.db` separate (Langfuse external dependency)?
2. Should we create a `data/archive/` for old database files?
3. Do we want to version the consolidated database schema?

---

**Status**: Awaiting approval to proceed with Phase 1
