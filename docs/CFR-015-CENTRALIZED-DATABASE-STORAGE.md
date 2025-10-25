# CFR-015: Centralized Database Storage

**Critical Functional Requirement**
**Status**: Active
**Priority**: CRITICAL
**Created**: 2025-10-23
**Author**: Claude Code

## Summary

ALL database files (.db, .sqlite, .sqlite3) MUST be stored exclusively in the `data/` directory. No database files are allowed in any other location including root directory, `.claude/`, or any subdirectories outside of `data/`.

## Requirements

### 1. Storage Location

All database files MUST be stored in `data/` with the following structure:

```
data/
├── notifications.db     # User notifications
├── metrics.db           # LLM metrics and analytics
├── orchestrator.db      # Orchestrator state and traces
├── bugs.db              # Bug tracking
├── roadmap.db           # Roadmap database (if used)
├── agent_messages.db    # Agent communication (if used)
└── [agent_name].db      # Per-agent databases (if needed)
```

### 2. Prohibited Locations

Database files MUST NOT be stored in:
- Root directory (`/`)
- `.claude/` or any subdirectories
- `coffee_maker/` source directories
- `tests/` directories
- Any location outside `data/`

### 3. Code Requirements

All code creating or accessing databases MUST:

```python
from pathlib import Path

# CORRECT - Using data directory
db_path = Path("data/metrics.db")

# WRONG - Root directory
db_path = Path("metrics.db")  # ❌ VIOLATION

# WRONG - Other directories
db_path = Path(".claude/agents/data/orchestrator.db")  # ❌ VIOLATION
```

### 4. Configuration

Database paths should be configurable but default to `data/`:

```python
class DatabaseConfig:
    BASE_DIR = Path("data")
    METRICS_DB = BASE_DIR / "metrics.db"
    ORCHESTRATOR_DB = BASE_DIR / "orchestrator.db"
    NOTIFICATIONS_DB = BASE_DIR / "notifications.db"
```

### 5. Git Ignore

The `.gitignore` file MUST include:

```gitignore
# SQLite database files (NEVER commit these to git!)
*.db
*.sqlite
*.sqlite3
*.db-wal
*.db-shm
*.db-journal

# All database files in data directory
data/*.db
data/*.sqlite
data/*.sqlite3
```

## Rationale

1. **Organization**: Single location for all persistent data
2. **Backup**: Easy to backup/restore all databases
3. **Security**: Can apply permissions to single directory
4. **Clarity**: Developers know exactly where databases are
5. **Gitignore**: Simple pattern to exclude from version control
6. **Deployment**: Easy to mount data volume in containers

## Migration

For existing databases in wrong locations:

1. Move file to `data/` directory
2. Update all code references
3. Test functionality
4. Remove old file

Example:
```bash
# Move database
mv llm_metrics.db data/metrics.db

# Update code
# FROM: db_path = "llm_metrics.db"
# TO:   db_path = "data/metrics.db"
```

## Enforcement

1. Pre-commit hooks should check for database files outside `data/`
2. Code reviews must verify CFR-015 compliance
3. Tests should use temporary databases in `data/test/` or temp directories
4. CI/CD should fail if databases detected outside `data/`

## Exceptions

ONLY the following exceptions are allowed:

1. **Tests**: May use temporary databases in system temp directory
2. **Migrations**: May temporarily create databases during migration scripts
3. **Backups**: May be stored in `data/backups/` subdirectory

All exceptions MUST be documented in code comments.

## Related

- CFR-014: Database Tracing (orchestrator database)
- GUIDELINE-015: Database Migration Strategy
- .gitignore: Database exclusion patterns

## Compliance Checklist

- [ ] All production databases in `data/` directory
- [ ] No databases in root directory
- [ ] No databases in `.claude/` directory
- [ ] All code uses `data/` paths
- [ ] .gitignore excludes all database patterns
- [ ] Documentation updated to reflect paths
- [ ] Migration completed for existing databases

---

**VIOLATION PENALTY**: Any code creating databases outside `data/` will be rejected in code review and must be fixed before merge.
