# Database Migration - Execute Once and Forget

## What This Does

1. **Consolidates** all databases into ONE: `roadmap.db`
   - Merges `notifications.db` data
   - Moves `command_token_usage` table from `development.db`
   - Deletes `development.db` and `notifications.db`

2. **Renames** 20 tables with agent-based prefixes (SPEC-115)
   - Fixes misleading prefixes (e.g., `review_commit` → `developer_commit`)
   - Adds missing prefixes (e.g., `notifications` → `shared_notifications`)
   - Reassigns UI tables to proper agents

3. **Cleans up** - Deletes ALL migration scripts including itself
   - No `migrations` table tracking
   - Scripts are one-time use only

## How to Run

```bash
# ONE command to rule them all
./data/migrations/execute_and_cleanup.sh
```

That's it! The script will:
- Backup existing databases
- Consolidate to single database
- Rename all tables
- Delete itself and all other migration files

## Result

- ✅ ONE database: `data/roadmap.db`
- ✅ 20 tables with clear agent-based prefixes
- ✅ No migration scripts left behind
- ✅ Backups in `data/backups/`

## Next Steps (Automated)

After this runs, code_developer will:
- Update all Python code references (TASK-115-3)
- Update documentation (TASK-115-4)
- Run full test suite (TASK-115-6)

---

**NOTE**: This file will delete itself after execution!
