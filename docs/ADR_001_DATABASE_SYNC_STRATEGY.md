# ADR 001: Database Synchronization Strategy

**Status**: ✅ ACCEPTED and IMPLEMENTED
**Date**: 2025-10-09
**Decision Makers**: Development Team
**Related**: PRIORITY 1.5 Database Sync Design

---

## Context

The Coffee Maker Agent has two execution environments:
1. **User's Project Environment**: Where the user runs `project-manager` CLI and analytics
2. **Daemon Environment**: Where the autonomous daemon executes tasks

Both environments need access to shared state:
- **Notifications**: Daemon asks questions → User responds via CLI
- **Analytics**: Daemon generates traces → User views in dashboard
- **Roadmap State**: Both read/write roadmap updates

**Problem**: How do we synchronize database access between these two environments?

---

## Decision

We have **ACCEPTED and IMPLEMENTED Option D (Hybrid Shared SQLite)**:

### Core Strategy

**Shared SQLite databases in common DATA_DIR**:
```python
# coffee_maker/config.py
DATA_DIR = PROJECT_ROOT / "data"  # Shared between user and daemon

DATABASE_PATHS = {
    "analytics": DATA_DIR / "analytics.db",
    "notifications": DATA_DIR / "notifications.db",
    "langfuse_export": DATA_DIR / "langfuse_export.db",
}
```

**Concurrent Access Protection**:
- ✅ SQLite WAL (Write-Ahead Logging) mode enabled
- ✅ 30-second busy_timeout for lock handling
- ✅ @with_retry decorator for transient failures
- ✅ File lock (ROADMAP_LOCK_PATH) for critical file operations

**Validation**:
- ✅ `validate_database_paths()` ensures all DBs are in shared DATA_DIR
- ✅ Runtime checks prevent accidental isolation

---

## Rationale

### Why Shared SQLite (Not Separate DBs)?

1. **Simplicity**: No sync logic needed → fewer bugs, easier to reason about
2. **Real-time**: User sees daemon's notifications immediately
3. **Single source of truth**: No conflict resolution needed
4. **Development velocity**: PRIORITY 2 & 3 implemented faster
5. **Sufficient for single-developer use**: Current target audience

### Why WAL Mode?

```python
# coffee_maker/cli/notifications.py
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=30000")
```

- **Concurrent reads**: Multiple readers don't block each other
- **Write isolation**: Writers don't block readers (most of the time)
- **Automatic checkpointing**: SQLite handles WAL cleanup
- **Battle-tested**: Used by major production systems

### Why NOT PostgreSQL?

While PostgreSQL would provide better concurrent access:
- ❌ **Overkill**: Single developer doesn't need heavyweight DB
- ❌ **Setup complexity**: Requires PostgreSQL installation/running
- ❌ **Deployment**: Adds dependency to user environment
- ✅ **Migration path available**: Can upgrade later if needed (see Phase 2 below)

### Why NOT Sync Mechanisms?

Separate DBs with sync would provide better isolation but:
- ❌ **Complexity**: Need sync daemon/process
- ❌ **Data lag**: User doesn't see daemon updates immediately
- ❌ **Conflict resolution**: Requires complex logic
- ❌ **Testing burden**: More failure modes to test
- ❌ **Premature optimization**: YAGNI for current scope

---

## Data Ownership Matrix

| Table | Source | Consumers | Strategy | Database | Rationale |
|-------|--------|-----------|----------|----------|-----------|
| `notifications` | Daemon + PM CLI | PM CLI, Slack bot | **SHARED** | notifications.db | Both read/write, need real-time |
| `traces` | Langfuse + Daemon | Analytics dashboard | **SHARED** | langfuse_export.db | Daemon generates, user views |
| `generations` | Langfuse + Daemon | Analytics dashboard | **SHARED** | langfuse_export.db | Daemon generates, user views |
| `events` | Langfuse + Daemon | Analytics dashboard | **SHARED** | langfuse_export.db | Daemon generates, user views |
| `analytics_*` | Analyzer scripts | Dashboard | **SHARED** | analytics.db | Daemon may trigger analysis |
| `roadmap_history`* | PM CLI | PM CLI, Daemon | **FILE** | ROADMAP.md | Version controlled, file-locked |
| `daemon_execution_log`* | Daemon only | Daemon only | **FUTURE_ISOLATED** | (not yet implemented) | Internal daemon state |
| `daemon_task_queue`* | Daemon only | Daemon only | **FUTURE_ISOLATED** | (not yet implemented) | Internal daemon state |

*Notes:*
- `roadmap_history`: Currently stored in ROADMAP.md file (not a DB table), protected by file lock
- `daemon_execution_log` & `daemon_task_queue`: Not yet implemented; when added, can be isolated if needed

---

## Concurrency Strategy

### Read Operations
- **Multiple concurrent readers**: ✅ Supported (WAL mode)
- **Timeout**: 30 seconds
- **Retry**: 3 attempts with exponential backoff (@with_retry)

### Write Operations
- **Write while reading**: ✅ Supported (WAL mode, readers not blocked)
- **Concurrent writes**: ⚠️ Serialized (SQLite limitation)
- **Lock wait**: 30-second busy_timeout
- **Retry**: 3 attempts with exponential backoff (@with_retry)

### Lock Contention Scenarios

**Scenario 1: User reads notifications while daemon writes**
```
Timeline:
├── User: SELECT * FROM notifications  [0ms]
├── Daemon: INSERT INTO notifications  [5ms]  ← doesn't block user
└── User: Fetch complete                [10ms]
Result: ✅ Both succeed
```

**Scenario 2: Daemon writes while user writes**
```
Timeline:
├── Daemon: INSERT INTO notifications  [0ms - acquires lock]
├── User: UPDATE notification SET...    [5ms - waits for lock]
│                                       [30s timeout, 3 retries]
└── User: Write succeeds after lock release
Result: ✅ Both succeed (user waits)
```

**Scenario 3: Database locked for >30s**
```
Timeline:
├── Long-running query                  [0ms - holds lock]
├── User: INSERT notification           [5ms - waits]
│   ├── Attempt 1: timeout after 30s   [35s]
│   ├── Attempt 2: timeout after 30s   [65s]
│   └── Attempt 3: timeout after 30s   [95s]
└── Result: ❌ OperationalError raised
Action: User sees error, daemon logs it
```

### File Lock Strategy

For critical file operations (ROADMAP.md updates):
```python
ROADMAP_LOCK_PATH = "/tmp/roadmap.lock"

# Both daemon and PM CLI use this lock
with FileLock(ROADMAP_LOCK_PATH, timeout=60):
    # Read/modify/write ROADMAP.md
    pass
```

---

## Implementation Details

### Database Connection Pattern

```python
# coffee_maker/cli/notifications.py
class NotificationDB:
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def create_notification(self, ...):
        with self._get_connection() as conn:
            # Database operations
            pass
```

**Key Features**:
1. **Connection per operation**: Fresh connection for each DB operation (avoids stale connections)
2. **Row factory**: Dict-like row access (`row['column']`)
3. **Busy timeout**: 30 seconds before giving up on locks
4. **Context manager**: Automatic connection cleanup
5. **Retry decorator**: Automatic retry on transient failures

### WAL Mode Configuration

```python
def _init_database(self):
    conn = sqlite3.connect(self.db_path, timeout=30.0)

    # Enable WAL mode for multi-process safety
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")

    # Create schema
    conn.executescript(CREATE_SCHEMA)
    conn.commit()
    conn.close()
```

**WAL Benefits**:
- Readers don't block writers
- Writers don't block readers (usually)
- Better performance for concurrent access
- Crash recovery built-in

### Validation on Startup

```python
# coffee_maker/config.py (runs on import)
def validate_database_paths():
    for db_name, db_path in DATABASE_PATHS.items():
        if not str(db_path).startswith(str(DATA_DIR)):
            raise RuntimeError(
                f"Database '{db_name}' is not in shared DATA_DIR!"
            )

validate_database_paths()  # Called on import
```

---

## Consequences

### Positive

✅ **Implemented and working**: PRIORITY 2 & 3 are 80-90% complete
✅ **Simple architecture**: No sync logic to maintain
✅ **Real-time updates**: User sees daemon's work immediately
✅ **Battle-tested**: WAL mode is production-proven
✅ **Easy testing**: Single DB, no sync edge cases
✅ **Fast development**: Minimal infrastructure overhead

### Negative

⚠️ **SQLite limitations**:
- Concurrent writes are serialized (one at a time)
- Not suitable for high-write workloads
- Network access not possible (local filesystem only)

⚠️ **Cleanup complexity**:
- Daemon data mixed with user data
- Cannot easily "reset daemon state" without affecting user data
- Mitigation: Use soft deletes or status flags

⚠️ **Isolation limitations**:
- Daemon can theoretically corrupt user DB
- Mitigation: Daemon runs with same permissions as user (no privilege escalation)

### Accepted Trade-offs

1. **Single-developer focus**: Acceptable for current target audience
2. **Write serialization**: Acceptable given low write frequency
3. **Local-only**: Acceptable for desktop development tool
4. **Shared state**: Acceptable given current trust model

---

## Migration Path (Phase 2)

When we need better concurrent access (team collaboration, production deployment):

### Option 1: PostgreSQL Migration

```python
# Step 1: Export SQLite data
def export_to_postgres():
    sqlite_conn = sqlite3.connect("data/notifications.db")
    pg_conn = psycopg2.connect("postgresql://localhost/coffee_maker")

    rows = sqlite_conn.execute("SELECT * FROM notifications").fetchall()
    pg_conn.executemany(
        "INSERT INTO notifications VALUES (...)", rows
    )
    pg_conn.commit()

# Step 2: Update DATABASE_PATHS
DATABASE_PATHS = {
    "notifications": "postgresql://localhost/coffee_maker",
    # ... other tables
}

# Step 3: Switch connection logic
if db_path.startswith("postgresql://"):
    conn = psycopg2.connect(db_path)
else:
    conn = sqlite3.connect(db_path)
```

### Option 2: Separate DBs + Sync

```python
# Only if we need true isolation (e.g., sandboxed daemon)
class SyncManager:
    def __init__(self):
        self.daemon_db = "/daemon-env/data/notifications.db"
        self.user_db = "/project/data/notifications.db"

    def sync_daemon_to_user(self):
        # Copy new records from daemon → user
        daemon_conn = sqlite3.connect(self.daemon_db)
        user_conn = sqlite3.connect(self.user_db)

        new_records = daemon_conn.execute("""
            SELECT * FROM notifications
            WHERE id > (SELECT MAX(id) FROM synced_ids)
        """).fetchall()

        for record in new_records:
            user_conn.execute("INSERT INTO notifications VALUES (?)", record)

        user_conn.commit()
```

---

## Testing Strategy

### Unit Tests

✅ **Already implemented** (`tests/ci_tests/cli/test_notifications.py`):
- Create notification
- Get pending notifications
- Respond to notification
- Mark as read/dismissed
- Concurrent read/write scenarios

### Integration Tests

✅ **Already implemented** (`tests/integration_tests/`):
- Daemon creates notification → User reads it
- User responds → Daemon receives response
- Multiple daemon tasks with concurrent notifications

### Performance Tests

⏳ **Future work**:
- Benchmark concurrent reads (expected: excellent)
- Benchmark concurrent writes (expected: serialized but acceptable)
- Measure lock contention under load

---

## Monitoring and Observability

### Database Metrics

```python
# Monitor lock contention
def check_wal_status():
    conn = sqlite3.connect("data/notifications.db")
    result = conn.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
    # result: (busy, log_size, checkpointed_frames)
    return result
```

### Logging

```python
# coffee_maker/cli/notifications.py
logger.info(f"NotificationDB initialized: {db_path}")
logger.info(f"Created notification {notif_id}: {title}")
logger.warning(f"Database locked, retrying... (attempt {attempt}/3)")
```

### Error Tracking

```python
@with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
def create_notification(...):
    # Automatic retry + logging
    # Final failure raises OperationalError → caught by daemon
```

---

## Alternatives Considered

### Option B: Separate DBs + Sync
**Rejected**: Too complex for single-developer use case

### Option C: PostgreSQL
**Rejected**: Overkill for current scope, can migrate later if needed

### Option A (pure): Shared SQLite without hybrid elements
**Accepted with modification**: Added validation and future isolation for daemon-only state

---

## References

- [SQLite WAL Mode Documentation](https://www.sqlite.org/wal.html)
- [SQLite Concurrent Access](https://www.sqlite.org/lockingv3.html)
- PRIORITY 1.5: Database Synchronization Architecture
- `coffee_maker/config.py`: Database path validation
- `coffee_maker/cli/notifications.py`: NotificationDB implementation

---

## Status Summary

| Deliverable | Status | Location |
|-------------|--------|----------|
| Problem Analysis | ✅ Complete | PRIORITY_1.5_DATABASE_SYNC_DESIGN.md |
| Architecture Decision | ✅ Complete | This document (ADR_001) |
| Data Ownership Matrix | ✅ Complete | This document (section above) |
| Concurrency Strategy | ✅ Complete | This document (section above) |
| Implementation | ✅ Complete | coffee_maker/cli/notifications.py, config.py |
| Testing Strategy | ✅ Complete | This document + tests/ directory |
| Migration Plan | ✅ Complete | This document (Phase 2 section) |
| Validation | ✅ Complete | coffee_maker/config.py validation functions |

**PRIORITY 1.5**: ✅ **COMPLETE** - Design finalized and implemented in PRIORITY 2 & 3
