# Migration 004: Database Table Renaming for Agent Ownership Clarity

**SPEC**: SPEC-115
**Created**: 2025-10-28
**Status**: Ready for execution
**Approach**: Simplified (no backward compatibility views)

---

## Overview

This migration renames **20 database tables** with proper agent-based prefixes to improve code clarity and prevent ownership confusion.

### What This Migration Does

Renames tables in **three databases**:
- **roadmap.db**: 19 tables
- **development.db**: 1 table
- **notifications.db**: 1 table (counted in roadmap.db list, but in separate database)

### Tables Being Renamed

| Old Name | New Name | Owner | Database |
|----------|----------|-------|----------|
| `review_commit` | `developer_commit` | code_developer | roadmap.db |
| `command_token_usage` | `developer_token_usage` | code_developer | development.db |
| `agent_lifecycle` | `orchestrator_agent_lifecycle` | orchestrator | roadmap.db |
| `notifications` | `shared_notifications` | shared | roadmap.db + notifications.db |
| `system_schema_metadata` | `architect_schema_metadata` | architect | roadmap.db |
| `notification_user` | `shared_notification_user` | shared | roadmap.db |
| `notification_system_state` | `shared_notification_state` | shared | roadmap.db |
| `system_audit` | `shared_audit` | shared | roadmap.db |
| `ui_bug_reports` | `assistant_bug_reports` | assistant | roadmap.db |
| `ui_demo_sessions` | `assistant_demo_sessions` | assistant | roadmap.db |
| `ui_delegation_log` | `assistant_delegation_log` | assistant | roadmap.db |
| `ui_component_library` | `ux_component_library` | ux_design_expert | roadmap.db |
| `ui_design_debt` | `ux_design_debt` | ux_design_expert | roadmap.db |
| `ui_design_specs` | `ux_design_specs` | ux_design_expert | roadmap.db |
| `ui_design_tokens` | `ux_design_tokens` | ux_design_expert | roadmap.db |
| `ui_conversation_context` | `listener_conversation_context` | user_listener | roadmap.db |
| `ui_intent_classification` | `listener_intent_classification` | user_listener | roadmap.db |
| `ui_routing_log` | `listener_routing_log` | user_listener | roadmap.db |
| `agent_message` | `shared_agent_message` | shared | roadmap.db |
| `metrics_subtask` | `manager_metrics_subtask` | project_manager | roadmap.db |

---

## Migration Files

Three migration scripts (run in order):

1. **`004_rename_tables_agent_ownership.sql`** - Main migration for roadmap.db (19 tables)
2. **`004b_rename_development_tables.sql`** - Development.db migration (1 table + views)
3. **`004c_rename_notifications_tables.sql`** - Notifications.db migration (1 table)

---

## Pre-Migration Checklist

**BEFORE running migration:**

- [ ] **Backup all databases**:
  ```bash
  cp data/roadmap.db data/roadmap.db.backup_$(date +%Y%m%d_%H%M%S)
  cp data/development.db data/development.db.backup_$(date +%Y%m%d_%H%M%S)
  cp data/notifications.db data/notifications.db.backup_$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **Stop all running agents** (prevent conflicts during migration):
  ```bash
  # Check for running agents
  ps aux | grep "poetry run" | grep -v grep

  # Kill if found
  pkill -f "poetry run code-developer"
  pkill -f "poetry run project-manager"
  ```

- [ ] **Verify database locations**:
  ```bash
  ls -lh data/*.db
  ```

- [ ] **Review migration scripts**:
  ```bash
  cat data/migrations/004*.sql
  ```

---

## Running the Migration

### Automated (Recommended)

Run all three migrations in sequence:

```bash
# Navigate to project root
cd /Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent

# Run migrations
sqlite3 data/roadmap.db < data/migrations/004_rename_tables_agent_ownership.sql
sqlite3 data/development.db < data/migrations/004b_rename_development_tables.sql
sqlite3 data/notifications.db < data/migrations/004c_rename_notifications_tables.sql
```

### Manual (One-by-One)

Run each migration individually with verification:

```bash
# 1. Roadmap database
echo "Migrating roadmap.db..."
sqlite3 data/roadmap.db < data/migrations/004_rename_tables_agent_ownership.sql

# Verify
sqlite3 data/roadmap.db "SELECT name FROM migrations WHERE name='004_rename_tables_agent_ownership';"

# 2. Development database
echo "Migrating development.db..."
sqlite3 data/development.db < data/migrations/004b_rename_development_tables.sql

# Verify
sqlite3 data/development.db "SELECT name FROM migrations WHERE name='004b_rename_development_tables';"

# 3. Notifications database
echo "Migrating notifications.db..."
sqlite3 data/notifications.db < data/migrations/004c_rename_notifications_tables.sql

# Verify
sqlite3 data/notifications.db "SELECT name FROM migrations WHERE name='004c_rename_notifications_tables';"
```

---

## Post-Migration Verification

### 1. Check Tables Were Renamed

```bash
# Roadmap database (should show new table names)
sqlite3 data/roadmap.db ".tables" | tr ' ' '\n' | sort | grep -E "developer_commit|orchestrator_agent_lifecycle|shared_notifications|architect_schema_metadata|shared_notification_user|shared_notification_state|shared_audit|assistant_|ux_|listener_|shared_agent_message|manager_metrics_subtask"

# Development database
sqlite3 data/development.db ".tables" | grep developer_token_usage

# Notifications database
sqlite3 data/notifications.db ".tables" | grep shared_notifications
```

### 2. Verify Data Integrity

```bash
# Count records in renamed tables (sanity check)
sqlite3 data/roadmap.db << EOF
SELECT 'developer_commit' as table_name, COUNT(*) as record_count FROM developer_commit
UNION ALL
SELECT 'orchestrator_agent_lifecycle', COUNT(*) FROM orchestrator_agent_lifecycle
UNION ALL
SELECT 'shared_notifications', COUNT(*) FROM shared_notifications;
EOF
```

### 3. Check Foreign Keys

```bash
# Verify foreign key constraints still work
sqlite3 data/roadmap.db "PRAGMA foreign_key_check;"
```

### 4. Check Migration Records

```bash
# Verify all migrations recorded
sqlite3 data/roadmap.db "SELECT * FROM migrations ORDER BY id;"
sqlite3 data/development.db "SELECT * FROM migrations ORDER BY id;"
sqlite3 data/notifications.db "SELECT * FROM migrations ORDER BY id;"
```

---

## Expected Output

After successful migration:

### roadmap.db
- 19 tables renamed
- `migrations` table has entry: `004_rename_tables_agent_ownership`
- All foreign keys intact
- All indexes renamed automatically

### development.db
- 1 table renamed: `command_token_usage` → `developer_token_usage`
- 3 views recreated with new table name
- `migrations` table has entry: `004b_rename_development_tables`

### notifications.db
- 1 table renamed: `notifications` → `shared_notifications`
- `migrations` table has entry: `004c_rename_notifications_tables`

---

## Rollback Instructions

If migration causes issues, restore from backups:

```bash
# Stop all agents first
pkill -f "poetry run"

# Restore from backups
cp data/roadmap.db.backup_YYYYMMDD_HHMMSS data/roadmap.db
cp data/development.db.backup_YYYYMMDD_HHMMSS data/development.db
cp data/notifications.db.backup_YYYYMMDD_HHMMSS data/notifications.db

# Verify restoration
sqlite3 data/roadmap.db ".tables" | grep review_commit
```

Alternatively, run rollback SQL from each migration file (see comments at end of each .sql file).

---

## Next Steps (After Migration)

After running migration successfully:

1. **Update Python Code** (TASK-115-3):
   - Find all references to old table names
   - Update to use new table names
   - Run tests after each batch of changes

2. **Update Documentation** (TASK-115-4):
   - Update database schema documentation
   - Update agent READMEs
   - Add migration notes

3. **Testing** (TASK-115-6):
   - Run full test suite: `pytest`
   - Test each agent's database operations
   - Verify query performance unchanged

---

## Troubleshooting

### Error: "no such table: X"

**Cause**: Table doesn't exist in this database (already renamed or in different database)

**Solution**: Check which database contains the table:
```bash
sqlite3 data/roadmap.db "SELECT name FROM sqlite_master WHERE name='X';"
sqlite3 data/development.db "SELECT name FROM sqlite_master WHERE name='X';"
sqlite3 data/notifications.db "SELECT name FROM sqlite_master WHERE name='X';"
```

### Error: "table X already exists"

**Cause**: Migration already run (idempotent protection failed)

**Solution**: Check migrations table:
```bash
sqlite3 data/roadmap.db "SELECT * FROM migrations WHERE name LIKE '004%';"
```

If migration recorded but table not renamed, manually rename:
```bash
sqlite3 data/roadmap.db "ALTER TABLE old_name RENAME TO new_name;"
```

### Error: Foreign key violations

**Cause**: Foreign key constraints broken by rename

**Solution**: Run foreign key check:
```bash
sqlite3 data/roadmap.db "PRAGMA foreign_key_check;"
```

Foreign keys should automatically update with table renames in SQLite.

---

## Testing Summary

All three migration scripts have been tested on copies of the databases:

✅ **roadmap.db.test_migration**: 19 tables renamed successfully
✅ **development.db.test_migration**: 1 table + 3 views updated successfully
✅ **notifications.db.test_migration**: 1 table renamed successfully

No errors encountered during test runs.

---

## Related Documentation

- **SPEC-115**: `docs/architecture/specs/SPEC-115-database-table-renaming-for-agent-ownership.md`
- **CFR-015**: Centralized Database Storage
- **Agent Ownership**: `docs/AGENT_OWNERSHIP.md`

---

**Migration Status**: ✅ Ready for production execution
**Estimated Time**: < 5 seconds (all three databases)
**Risk Level**: Low (tested, reversible, backed up)
