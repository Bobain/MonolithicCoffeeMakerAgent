# PRIORITY 1.5: Database Synchronization Architecture

**Status**: ✅ **COMPLETE** - Decision made and implemented in PRIORITY 2 & 3
**Completion Date**: 2025-10-09
**Estimated Duration**: 2-3 days (design phase only) → Actual: 1 day
**Impact**: ⭐⭐⭐⭐⭐ (Critical infrastructure)
**Type**: Design-first priority (no implementation, integrated into other priorities)

**Decision**: Hybrid Shared SQLite (Option D) - See [ADR_001_DATABASE_SYNC_STRATEGY.md](./ADR_001_DATABASE_SYNC_STRATEGY.md)

---

## The Problem 🚨

We will have **two separate database instances**:

```
User's Project Environment          Daemon's Isolated Docker Environment
─────────────────────────           ─────────────────────────────────────
/project/data/                      /daemon-env/data/
  ├── langfuse_traces.db     ≠≠≠      ├── langfuse_traces.db
  ├── notifications.db       ≠≠≠      ├── notifications.db
  └── analytics.db           ≠≠≠      └── analytics.db

CONFLICT: Two separate databases with potentially overlapping/conflicting data!
```

**Specific Issues**:

1. **Notifications Table**:
   - Daemon writes: "User input required for PRIORITY 3"
   - Slack bot reads from: User's DB (doesn't see daemon's notification!)
   - User's `coffee-roadmap` CLI reads from: User's DB (doesn't see daemon's questions!)

2. **Analytics/Langfuse Traces**:
   - Daemon executes code → generates Langfuse traces → writes to daemon's DB
   - User runs analytics dashboard → reads from user's DB (doesn't see daemon's traces!)

3. **Roadmap State**:
   - User updates roadmap via `coffee-roadmap` CLI → writes to user's DB
   - Daemon needs to read latest roadmap state → reads from daemon's DB (stale data!)

---

## Critical Questions (Must Answer Before Implementation)

### 1. Database Architecture Strategy

**Options**:
- [ ] **A. Single Shared Database** (via Docker volume mount)
- [ ] **B. Separate DBs + Unidirectional Sync** (daemon → user)
- [ ] **C. Network Database** (PostgreSQL accessible to both)
- [ ] **D. Hybrid** (shared for some tables, isolated for others)

**Decision Criteria**:
- Isolation requirements (security, reproducibility)
- Concurrent access needs (can SQLite handle it?)
- Complexity budget (simple vs robust)
- Future scalability (single dev vs team vs production)

---

### 2. Data Ownership Matrix

For EACH table, decide the strategy:

| Table | Source | Consumers | Strategy | Rationale |
|-------|--------|-----------|----------|-----------|
| `traces` (Langfuse) | Daemon | User analytics dashboard | ? | Daemon generates, user views |
| `generations` (Langfuse) | Daemon | User analytics dashboard | ? | Daemon generates, user views |
| `events` (Langfuse) | Daemon | User analytics dashboard | ? | Daemon generates, user views |
| `notifications` | Daemon + PM CLI | Slack bot, User CLI | ? | Both write, both read |
| `slack_interactions` | Slack bot | Daemon, PM CLI | ? | Slack writes, both read |
| `roadmap_history` | PM CLI | Daemon | ? | PM writes, daemon reads |
| `daemon_execution_log` | Daemon only | Daemon only | ISOLATED | Internal daemon state |
| `daemon_task_queue` | Daemon only | Daemon only | ISOLATED | Internal daemon state |

**Strategies**:
- `SHARED`: Single database, both access directly
- `SYNC_D2U`: Daemon writes to isolated, syncs to user DB
- `SYNC_U2D`: User writes to project DB, syncs to daemon
- `SYNC_BI`: Bidirectional sync (complex!)
- `ISOLATED`: Only one environment accesses

---

### 3. Synchronization Mechanism (if needed)

**If we choose separate DBs with sync**:

- [ ] **Frequency**: Real-time? Periodic (every N seconds)? Event-driven (on daemon pause)?
- [ ] **Direction**: One-way (daemon → user)? Bidirectional?
- [ ] **Conflict Resolution**: Last-write-wins? Versioning? CRDTs? User-wins?
- [ ] **Failure Handling**: Retry? Queue? Alert user? Block daemon?
- [ ] **Implementation**: Separate sync process? Built into daemon? Part of PM CLI?

---

### 4. Isolation vs Integration Trade-offs

**Why do we want isolated environment?**
- Security: Daemon can't corrupt user's codebase
- Reproducibility: Clean environment for each run
- Cleanup: Easy to reset daemon environment
- Safety: Errors don't affect user's work

**Why do we want integration?**
- Real-time data access (no sync lag)
- Simpler architecture (no sync logic)
- Single source of truth (no conflicts)
- Better user experience (immediate updates)

**Can we have both?**
- Docker volume mounts (shared filesystem)
- Network-accessible database (PostgreSQL)
- Hybrid approach (some shared, some isolated)

---

## Architecture Options

### Option A: Shared SQLite via Docker Volume

```yaml
# docker-compose.yml
services:
  daemon:
    volumes:
      - ./data:/project/data:rw  # Share entire data directory
    environment:
      - ANALYTICS_DB=/project/data/analytics.db
      - NOTIFICATIONS_DB=/project/data/notifications.db
```

**Implementation**:
```python
# Both daemon and user use SAME database files
class SharedDatabaseAccess:
    def __init__(self):
        self.analytics_db = "/project/data/analytics.db"
        self.notifications_db = "/project/data/notifications.db"

    # No sync needed - direct access
    def write_notification(self, notification):
        conn = sqlite3.connect(self.notifications_db)
        # ... direct write
```

**Pros**:
✅ No sync logic needed (single source of truth)
✅ Real-time updates (daemon writes → user sees immediately)
✅ Simple architecture (minimal code)
✅ Works for local development (single developer)

**Cons**:
❌ SQLite locking issues (concurrent writes may fail)
❌ Less isolated (daemon can corrupt user DB)
❌ Cleanup complexity (daemon data mixed with user data)
❌ Testing complexity (shared state between tests)

---

### Option B: Separate DBs + Unidirectional Sync (Daemon → User)

```python
class UnidirectionalSync:
    """Daemon writes to isolated DB, periodically syncs to user DB"""

    def __init__(self):
        self.daemon_db = "/daemon-env/data/analytics.db"
        self.user_db = "/project/data/analytics.db"
        self.last_sync_timestamp = 0

    def sync_new_records(self):
        """Copy records created since last sync"""
        daemon_conn = sqlite3.connect(self.daemon_db)
        user_conn = sqlite3.connect(self.user_db)

        # Get new records
        new_records = daemon_conn.execute("""
            SELECT * FROM traces
            WHERE created_at > ?
        """, (self.last_sync_timestamp,)).fetchall()

        # Insert into user DB (with conflict handling)
        for record in new_records:
            try:
                user_conn.execute("INSERT INTO traces VALUES (...)", record)
            except sqlite3.IntegrityError:
                # Conflict - decide strategy (skip, update, error)
                pass

        user_conn.commit()
        self.last_sync_timestamp = time.time()
```

**Pros**:
✅ Clean isolation (daemon can't corrupt user DB directly)
✅ User DB always has complete history
✅ Easy cleanup (delete daemon DB without affecting user data)
✅ Daemon failures don't corrupt user DB

**Cons**:
❌ Sync complexity (need background sync process)
❌ Data lag (not real-time, depends on sync frequency)
❌ Storage duplication (same data in both DBs)
❌ Conflict resolution needed (what if user modifies synced data?)

---

### Option C: Network-Accessible PostgreSQL

```python
class PostgreSQLStrategy:
    """Both daemon and user connect to same PostgreSQL instance"""

    def __init__(self):
        # Shared PostgreSQL (can be in Docker too)
        self.db_url = "postgresql://localhost:5432/coffee_maker"

    # Daemon connects with restricted permissions
    daemon_user = "daemon_user"  # Can only INSERT/SELECT
    user_user = "admin_user"     # Full permissions

    # Row-level security (optional)
    """
    CREATE POLICY daemon_policy ON traces
    FOR INSERT TO daemon_user
    USING (source = 'daemon');
    """
```

**Pros**:
✅ True shared database (no sync needed)
✅ Proper concurrent access (PostgreSQL handles it)
✅ Row-level security (fine-grained permissions)
✅ Scales to team/production use
✅ Better tooling (pgAdmin, etc.)

**Cons**:
❌ More complex setup (requires PostgreSQL running)
❌ Heavier than SQLite (more resources)
❌ Network dependency (daemon needs DB connection)
❌ Overkill for single-developer local use

---

### Option D: Hybrid (Split by Data Type)

```python
class HybridStrategy:
    """
    Shared data: Analytics, notifications (via Docker volume or PostgreSQL)
    Isolated data: Daemon internal state (isolated SQLite)
    """

    def __init__(self):
        # Shared databases (via Docker volume mount)
        self.shared = {
            "analytics": "/project/data/analytics.db",
            "notifications": "/project/data/notifications.db"
        }

        # Isolated daemon-only database
        self.isolated = "/daemon-env/data/daemon_internal.db"

    def write_trace(self, trace):
        # Shared data - direct write to user's DB
        conn = sqlite3.connect(self.shared["analytics"])
        conn.execute("INSERT INTO traces VALUES (...)")

    def write_task_state(self, state):
        # Isolated data - daemon-only DB
        conn = sqlite3.connect(self.isolated)
        conn.execute("INSERT INTO task_queue VALUES (...)")
```

**Data Split**:
- **Shared** (Docker volume or PostgreSQL):
  - `langfuse_traces.db` (analytics, notifications)
  - User needs to see daemon's traces
  - Slack bot needs to see daemon's notifications

- **Isolated** (daemon-only SQLite):
  - `daemon_internal.db` (task queue, execution logs, temp state)
  - User doesn't need to see this
  - Can be deleted on daemon restart

**Pros**:
✅ Best of both worlds (shared + isolated)
✅ Clear data ownership (by database file)
✅ No sync for shared data
✅ Isolated data stays truly isolated

**Cons**:
❌ More complex architecture (two database strategies)
❌ Need to carefully decide which data goes where
❌ Still has SQLite concurrency limitations for shared data

---

## Recommended Phased Approach

### Phase 1: Shared SQLite (PRIORITY 1-3)
**For initial implementation**:
- Use **Option A or D** (shared SQLite via Docker volume)
- Accept SQLite locking limitations (daemon waits if locked)
- Document concurrency expectations
- Good enough for single-developer local use

**Implementation**:
```yaml
# docker-compose.yml
volumes:
  - ./data:/project/data:rw
```

### Phase 2: PostgreSQL Migration (PRIORITY 4+ or later)
**When needed** (team collaboration, production):
- Migrate to **Option C** (PostgreSQL)
- Proper concurrent access
- Row-level security
- Better scalability

**Migration Path**:
```python
# Migration script: SQLite → PostgreSQL
def migrate_sqlite_to_postgres():
    sqlite_conn = sqlite3.connect("data/analytics.db")
    pg_conn = psycopg2.connect("postgresql://...")

    # Copy all tables
    for table in ["traces", "generations", "events"]:
        rows = sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()
        pg_conn.executemany(f"INSERT INTO {table} VALUES (...)", rows)
```

---

## Decision Matrix

| Use Case | Recommended Strategy | Rationale |
|----------|---------------------|-----------|
| Single developer, local | Option A/D (Shared SQLite) | Simple, fast, good enough |
| Team collaboration | Option C (PostgreSQL) | Concurrent access needed |
| Production deployment | Option C (PostgreSQL) | Scalability, reliability |
| CI/CD testing | Option B (Separate + sync) | Isolation for tests |

---

## Implementation Guidelines (For PRIORITY 2 & 3)

**Once we decide on a strategy**, follow these guidelines:

### If we choose Option A (Shared SQLite):

```python
# PRIORITY 2: Roadmap CLI
class RoadmapEditor:
    def __init__(self):
        # Use shared database path
        self.db_path = os.environ.get("NOTIFICATIONS_DB", "data/notifications.db")

# PRIORITY 3: Daemon
class Daemon:
    def __init__(self):
        # Use same shared database path
        self.db_path = os.environ.get("NOTIFICATIONS_DB", "/project/data/notifications.db")
```

### If we choose Option B (Separate + Sync):

```python
# Add sync process to daemon
class Daemon:
    def __init__(self):
        self.sync_manager = SyncManager()
        self.sync_interval = 10  # seconds

    def run(self):
        while True:
            # Normal daemon work
            self.execute_task()

            # Periodic sync
            if time.time() - self.last_sync > self.sync_interval:
                self.sync_manager.sync_to_user_db()
```

### If we choose Option C (PostgreSQL):

```python
# Update database URLs
ANALYTICS_DB = "postgresql://localhost:5432/coffee_maker"

# Both daemon and PM use same connection string
# Differentiated by database users/roles
```

---

## Deliverables (Design Phase)

- [x] **Problem Analysis Document** (this file) ✅
- [x] **Architecture Decision Record** (ADR) with final choice and rationale ✅ [ADR_001](./ADR_001_DATABASE_SYNC_STRATEGY.md)
- [x] **Data Ownership Matrix** (complete table above) ✅ See ADR_001
- [x] **Concurrency Strategy** (how to handle concurrent writes) ✅ See ADR_001
- [x] **Sync Mechanism Spec** (N/A - using shared DB, no sync needed) ✅
- [x] **Migration Plan** (SQLite → PostgreSQL, if phased approach) ✅ See ADR_001 Phase 2
- [x] **Testing Strategy** (how to test database access patterns) ✅ See ADR_001
- [x] **Implementation Guidelines** (concrete code examples for PRIORITY 2 & 3) ✅ See ADR_001
- [x] **Rollback Plan** (N/A - shared DB, no sync failures possible) ✅

---

## Timeline

**Day 1: Problem Analysis + Requirements** (4-6h)
- Document all use cases (local dev, team, production)
- List all database tables and their sync requirements
- Identify critical questions that must be answered
- Create data ownership matrix (draft)

**Day 2: Architecture Evaluation** (6-8h)
- Prototype all 4 options with code examples
- Test concurrent access scenarios
- Benchmark performance (SQLite vs PostgreSQL)
- Document pros/cons for each option
- Make recommendation

**Day 3: Decision + Documentation** (4-6h)
- Finalize architecture decision (with team/user input)
- Write Architecture Decision Record (ADR)
- Create implementation guidelines for PRIORITY 2-3
- Document migration path (if phased)
- Review and approval

**Total**: 14-20h (2-3 days) - **Design only, implementation in other priorities**

---

## Success Criteria ✅ ALL COMPLETE

- ✅ All critical questions answered with clear rationale → See ADR_001
- ✅ ADR document complete and approved → ADR_001_DATABASE_SYNC_STRATEGY.md
- ✅ Data ownership matrix complete (every table has a strategy) → ADR_001, section "Data Ownership Matrix"
- ✅ PRIORITY 2 & 3 developers know exactly how to implement → Already implemented! Tests passing (159/159)
- ✅ Migration plan exists (if phased approach) → ADR_001, section "Migration Path (Phase 2)"
- ✅ Testing strategy defined → ADR_001, section "Testing Strategy"
- ✅ Rollback/recovery plan documented → N/A (shared DB, monitoring via logging)

---

## Integration with Other Priorities ✅ COMPLETE

This was a **design-only priority**. Implementation completed in:

- **PRIORITY 1** (Analytics): ✅ DB schema uses shared DATA_DIR with WAL mode
- **PRIORITY 2** (Roadmap CLI): ✅ NotificationDB follows shared SQLite pattern
- **PRIORITY 3** (Daemon): ✅ Daemon uses same DATABASE_PATHS configuration
- **All notification priorities**: ✅ Using shared notifications.db with retry logic

**RESULTS** ✅:
- ✅ **Design complete**: ADR_001 documents final decision
- ✅ **Implementation complete**: PRIORITY 2 & 3 implemented and tested
- ✅ **No blockers**: Shared SQLite approach enabled rapid development
- ✅ **Tests passing**: 159/159 tests (0 regressions)
- ✅ **Validation in place**: config.py validates DB paths on import
