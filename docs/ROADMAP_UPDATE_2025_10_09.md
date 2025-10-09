# Roadmap Update - Database Guardrails & MVP Design

**Date**: 2025-10-09
**Status**: ✅ Design Complete
**Impact**: Critical infrastructure decisions for PRIORITY 1.5, 2, and 3

---

## Summary

This update establishes the **database synchronization strategy** and **Project Manager CLI MVP design** to ensure the autonomous daemon and user's environment can safely share data without conflicts.

---

## Key Decisions Made

### 1. Database Architecture: Shared SQLite (Option A)

**Decision**: Use shared SQLite databases via Docker volume mounts for MVP.

**Rationale**:
- ✅ Simple to implement (no sync logic)
- ✅ Real-time updates (single source of truth)
- ✅ Perfect for single-developer local use
- ⚠️ SQLite locking mitigated with WAL mode + retry logic

**Reference**: `PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`

---

### 2. ROADMAP.md: Single Shared File

**Critical Decision**: There is **ONLY ONE** `ROADMAP.md` file shared via Docker volume.

**Implementation**:
```yaml
# docker-compose.yml
volumes:
  - ./docs/ROADMAP.md:/project/docs/ROADMAP.md:rw  # Same file!
```

**Conflict Resolution**:
- **MVP**: File lock (`filelock` library) - only one edit at a time
- **Future**: Git-based merge (automatic conflict resolution)

**User's Concern Addressed**: "We should never have differences between the roadmap.md that will be edited by the project_manager and the roadmap.md that the claude-cli daemon agent is reading and editing. Or git should be able to merge and solve conflicts."

✅ **Solution**: Share single file + file lock ensures no conflicts

---

### 3. Project Manager CLI: Two-Phase Approach

**Phase 1: MVP - Database Guardrails First** (2-3 days)
- Basic CLI commands (no AI)
- Notification database with retry logic
- WAL mode + timeout configuration
- Establishes patterns for daemon

**Phase 2: Full AI Integration** (2-3 days)
- Claude AI for natural language
- Rich terminal UI
- Roadmap editing
- Slack integration

**Rationale**: Validate database patterns before adding complexity

**Reference**: `PROJECT_MANAGER_MVP_DESIGN.md`

---

## Documents Created

1. **`PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`** (450+ lines)
   - Problem analysis with examples
   - 4 architectural options with pros/cons
   - Data ownership matrix
   - Phased approach (SQLite → PostgreSQL)
   - Comprehensive design questions

2. **`PROJECT_MANAGER_MVP_DESIGN.md`** (696 lines)
   - Docker volume configuration
   - Database guardrails (WAL mode, retry logic)
   - Notification schema (3 tables)
   - CLI commands specification
   - 3-phase implementation plan
   - Database access patterns
   - Testing strategy

3. **Added to `ROADMAP.md`**:
   - **PRIORITY 1.5**: Database Synchronization Architecture (inserted between PRIORITY 1 and 2)
   - **Recurring Best Practices**: 10 practices to apply continuously
   - **MVP Approach**: Two-phase implementation strategy for PRIORITY 2

---

## Recurring Best Practices Added to Roadmap

Established **10 recurring practices** to apply throughout development:

1. 🗃️ **Database Synchronization Review** - Check every database operation
2. 🧹 **Code Refactoring & Simplification** - Clean as you build
3. 📝 **Documentation Updating** - Keep docs in sync
4. 🧪 **Test Coverage Maintenance** - Tests for every feature
5. 🎨 **Code Formatting & Linting** - Automated via pre-commit
6. 🔍 **Performance Profiling** - Optimize LLM costs
7. 🔐 **Security Review** - Protect sensitive data
8. 📊 **Analytics & Observability** - Measure everything
9. 🗂️ **Dependency Management** - Monthly security audits
10. 🎯 **Roadmap Synchronization** - Keep roadmap updated

**Philosophy**: "Every new feature implementation is an opportunity to improve the entire codebase."

---

## Critical Guidelines Established

### Database Access Pattern

**All database operations MUST follow this pattern**:

```python
from coffee_maker.utils.database import get_db_connection
from coffee_maker.utils.retry_utils import with_retry
from langfuse.decorators import observe
from sqlite3 import OperationalError

@observe
@with_retry(
    max_attempts=3,
    backoff_base=1.5,
    retriable_exceptions=(OperationalError,),
)
def database_operation():
    with get_db_connection("notifications") as conn:
        # Your query here
        conn.execute("INSERT INTO ...")
        # Auto-commits on success
```

**Enforces**:
- ✅ WAL mode enabled
- ✅ 5-second busy timeout
- ✅ Automatic retry on lock errors
- ✅ Langfuse observability
- ✅ Proper error handling

---

### ROADMAP.md Editing Pattern

**All ROADMAP.md edits MUST use file lock**:

```python
from filelock import FileLock

ROADMAP_LOCK = "/tmp/roadmap.lock"

def edit_roadmap_safely(edit_function):
    with FileLock(ROADMAP_LOCK, timeout=10):
        current = Path("./docs/ROADMAP.md").read_text()
        new_content = edit_function(current)
        Path("./docs/ROADMAP.md").write_text(new_content)

        # Optional: Git commit
        subprocess.run(["git", "add", "docs/ROADMAP.md"])
        subprocess.run(["git", "commit", "-m", "Update ROADMAP"])
```

**Prevents**:
- ❌ Concurrent edits from user and daemon
- ❌ Lost updates
- ❌ File corruption

---

## Implementation Checklist

### PRIORITY 1.5: Database Sync Design (2-3 days)

**Day 1: Problem Analysis** (4-6h)
- [x] Problem analysis document ✅ (already complete)
- [ ] Data ownership matrix (complete table for each database table)
- [ ] Use case documentation (local dev, team, production)

**Day 2: Architecture Evaluation** (6-8h)
- [ ] Prototype shared SQLite approach
- [ ] Test concurrent access (10+ parallel writes)
- [ ] Benchmark performance
- [ ] Document pros/cons

**Day 3: Decision + Documentation** (4-6h)
- [ ] Architecture Decision Record (ADR)
- [ ] Implementation guidelines for PRIORITY 2 & 3
- [ ] Migration plan (SQLite → PostgreSQL)
- [ ] User approval

---

### PRIORITY 2: Project Manager CLI MVP (2-3 days)

**Phase 1: Database Foundation** (Day 1, 4-6h)
- [ ] `coffee_maker/utils/database.py` - Connection manager
- [ ] `coffee_maker/cli/notification_schema.sql` - Schema
- [ ] `coffee_maker/cli/init_database.py` - Initialization
- [ ] `coffee_maker/cli/database_operations.py` - CRUD with retry
- [ ] Unit tests (database operations)
- [ ] Integration test (concurrent writes)

**Phase 2: Basic CLI** (Day 2, 4-6h)
- [ ] `coffee_maker/cli/roadmap_cli.py` - Main CLI
- [ ] `coffee_maker/cli/commands/view.py` - View commands
- [ ] `coffee_maker/cli/commands/status.py` - Status updates
- [ ] `coffee_maker/cli/commands/notify.py` - Notifications
- [ ] `coffee_maker/cli/commands/sync.py` - Sync command
- [ ] Setup.py entry point: `coffee-roadmap`

**Phase 3: Testing & Docs** (Day 3, 2-3h)
- [ ] Integration tests (CLI)
- [ ] README for PM CLI
- [ ] Database pattern docs
- [ ] Ready for daemon integration

---

## Success Criteria

**PRIORITY 1.5** is successful if:
- ✅ All critical questions answered
- ✅ ADR complete and approved
- ✅ Data ownership matrix complete
- ✅ Implementation guidelines clear
- ✅ PRIORITY 2 & 3 developers know exactly what to do

**PRIORITY 2 MVP** is successful if:
- ✅ Database operations work with 10+ concurrent writes
- ✅ No "database is locked" errors
- ✅ Daemon can read PM CLI notifications
- ✅ PM CLI can read daemon notifications
- ✅ All tests passing
- ✅ Ready for PRIORITY 3 (Autonomous Daemon)

---

## Migration Path

### Current (MVP)
```
User Environment            Daemon Environment
───────────────             ──────────────────
./data/                ═══  /project/data/     (shared volume)
./docs/ROADMAP.md      ═══  /project/docs/ROADMAP.md (shared volume)
```

### Future (Team/Production)
```
PostgreSQL Server
─────────────────
All clients connect to:
postgresql://localhost:5432/coffee_maker

- Row-level security
- Proper concurrent access
- Better tooling
```

**When to migrate**: When scaling beyond single developer

---

## References

1. **PRIORITY 1.5 Design**: `docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`
2. **Project Manager MVP**: `docs/PROJECT_MANAGER_MVP_DESIGN.md`
3. **Roadmap**: `docs/ROADMAP.md` (updated with PRIORITY 1.5 and recurring practices)
4. **Sprint 1 Summary**: `docs/sprint1_improvements_summary.md` (refactoring examples)

---

## Next Steps

1. **User Review**: Review all documents and approve approach
2. **Start PRIORITY 1.5**: Begin Day 1 (problem analysis + data ownership matrix)
3. **Validate Approach**: Prototype concurrent access with shared SQLite
4. **Build MVP**: Implement PRIORITY 2 Phase 1 (database foundation)

---

## Questions for User

1. **Database Strategy**: Do you approve shared SQLite (Option A) for MVP?
2. **File Locking**: Is `filelock` library acceptable for ROADMAP.md conflicts?
3. **Git Integration**: Should we commit ROADMAP.md changes automatically?
4. **Scope**: Does the two-phase approach (basic CLI first, AI later) make sense?

---

**Status**: Ready for user review and approval ✅
**Next Action**: User approval to begin PRIORITY 1.5 Day 1
