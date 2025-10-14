# Project Manager CLI - MVP Design with Database Guardrails

**Document**: MVP implementation design for `coffee-roadmap` CLI
**Created**: 2025-10-09
**Status**: 📝 Design Phase
**Priority**: PRIORITY 2 implementation guide

---

## Executive Summary

This document defines the **Minimal Viable Product (MVP)** for the Project Manager CLI (`coffee-roadmap`) with a focus on **database guardrails** to prevent synchronization issues between the user's project environment and the daemon's isolated Docker environment.

**Core Philosophy**: Start with the simplest architecture that establishes proper patterns. The MVP will:
1. ✅ Use **shared SQLite** via Docker volume mounts (Option A from PRIORITY 1.5)
2. ✅ Establish **database access patterns** that prevent future sync issues
3. ✅ Provide **basic CLI** for roadmap management (no AI yet)
4. ✅ Set up **notification database** with proper guardrails
5. ✅ Create **foundation** for future autonomous daemon integration

---

## Architecture Decision: Shared SQLite (Option A)

Based on PRIORITY 1.5 analysis, the MVP will use **Option A: Shared SQLite via Docker Volume**.

### Why This Choice?

✅ **Pros**:
- Simple to implement (no sync logic needed)
- Real-time updates (daemon writes → user sees immediately)
- Single source of truth (no conflicts)
- Perfect for single-developer local use

⚠️ **Cons** (acceptable for MVP):
- SQLite locking issues (mitigated with WAL mode + retries)
- Less isolated (acceptable - daemon can't corrupt if designed correctly)
- Cleanup complexity (acceptable - we'll document clear procedures)

### Docker Volume Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  daemon:
    build: .
    volumes:
      # CRITICAL: Share entire data directory (read-write)
      - ./data:/project/data:rw

      # CRITICAL: Share ROADMAP.md file (read-write for both)
      # There is ONLY ONE ROADMAP.md - no separate copies!
      - ./docs/roadmap/ROADMAP.md:/project/docs/roadmap/ROADMAP.md:rw

      # CRITICAL: Share entire project directory (for git operations)
      - .:/project/code:rw

    environment:
      # All databases point to SHARED location
      - ANALYTICS_DB=/project/data/analytics.db
      - NOTIFICATIONS_DB=/project/data/notifications.db
      - LANGFUSE_EXPORT_DB=/project/data/langfuse_export.db

      # Roadmap path (SAME FILE for user and daemon)
      - ROADMAP_PATH=/project/docs/roadmap/ROADMAP.md

    # Prevent daemon from corrupting files
    read_only: false  # Need write access to databases and ROADMAP.md
    security_opt:
      - no-new-privileges:true
```

**Key Design Decisions**:
1. **Data directory** (`./data/`) is shared read-write between user and daemon
2. **ROADMAP.md** is shared read-write - **THERE IS ONLY ONE FILE** ⚡
3. **Project directory** (`.`) is shared read-write for git operations
4. All database paths use `/project/data/` (shared location)
5. Environment variables enforce correct paths

**Critical: Single Source of Truth for ROADMAP.md**

❌ **WRONG**: Create separate copies
```
User's Environment:                Daemon's Environment:
./docs/roadmap/ROADMAP.md           ≠≠≠    /daemon/docs/roadmap/ROADMAP.md
                            ^
                      CONFLICT! Two files!
```

✅ **CORRECT**: Share single file via Docker volume
```
User's Environment:                Daemon's Environment:
./docs/roadmap/ROADMAP.md           ===    /project/docs/roadmap/ROADMAP.md
                            ^
                      SAME FILE via volume mount!
```

**Conflict Resolution Strategy**: Use Git

Since both user and daemon can write to ROADMAP.md, conflicts are possible:

**Option 1: Lock-Based (MVP Approach)** ✅ **START HERE**
```python
# coffee_maker/cli/roadmap_lock.py
from filelock import FileLock
import time

ROADMAP_LOCK = "/tmp/roadmap.lock"

def edit_roadmap_safely(edit_function):
    """Edit ROADMAP.md with file lock to prevent conflicts."""
    with FileLock(ROADMAP_LOCK, timeout=10):
        # Read current state
        current = Path("./docs/roadmap/ROADMAP.md").read_text()

        # Apply edit
        new_content = edit_function(current)

        # Write back
        Path("./docs/roadmap/ROADMAP.md").write_text(new_content)

        # Git commit (optional but recommended)
        subprocess.run(["git", "add", "docs/roadmap/ROADMAP.md"])
        subprocess.run(["git", "commit", "-m", f"Update ROADMAP.md: {edit_function.__name__}"])
```

**Option 2: Git-Based Conflict Resolution** (Future Enhancement)
```python
# If lock times out, fall back to git merge
try:
    with FileLock(ROADMAP_LOCK, timeout=5):
        edit_roadmap()
except Timeout:
    # Create branch, edit, merge
    subprocess.run(["git", "checkout", "-b", "daemon-update"])
    edit_roadmap()
    subprocess.run(["git", "add", "docs/roadmap/ROADMAP.md"])
    subprocess.run(["git", "commit", "-m", "Daemon update"])
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["git", "merge", "daemon-update"])
    # Git will handle conflicts
```

**Best Practice**: Minimize concurrent edits
- User edits roadmap during planning/thinking
- Daemon edits roadmap during status updates
- These rarely overlap in practice

---

## Database Guardrails

### 1. SQLite Configuration (WAL Mode + Timeout)

**Problem**: SQLite doesn't handle concurrent writes well by default.

**Solution**: Enable Write-Ahead Logging (WAL) and set busy timeout.

```python
# coffee_maker/utils/database.py

import sqlite3
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# CRITICAL: All database paths MUST use shared location
SHARED_DATA_DIR = "/project/data"  # In Docker
# SHARED_DATA_DIR = "./data"  # In local dev

DATABASE_PATHS = {
    "analytics": f"{SHARED_DATA_DIR}/analytics.db",
    "notifications": f"{SHARED_DATA_DIR}/notifications.db",
    "langfuse_export": f"{SHARED_DATA_DIR}/langfuse_export.db",
}


def configure_sqlite_connection(conn: sqlite3.Connection) -> None:
    """Configure SQLite connection with proper guardrails.

    CRITICAL: This must be called for EVERY database connection.
    """
    # Enable WAL mode for concurrent access
    conn.execute("PRAGMA journal_mode=WAL")

    # Set busy timeout to 5 seconds (prevents immediate failures)
    conn.execute("PRAGMA busy_timeout=5000")

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys=ON")

    # Synchronous mode: NORMAL (balance safety/performance)
    conn.execute("PRAGMA synchronous=NORMAL")

    logger.debug("SQLite connection configured with WAL mode and 5s timeout")


@contextmanager
def get_db_connection(db_name: str) -> Generator[sqlite3.Connection, None, None]:
    """Get database connection with proper configuration.

    Args:
        db_name: One of 'analytics', 'notifications', 'langfuse_export'

    Yields:
        Configured SQLite connection

    Example:
        >>> with get_db_connection("notifications") as conn:
        ...     conn.execute("INSERT INTO notifications ...")
    """
    if db_name not in DATABASE_PATHS:
        raise ValueError(f"Unknown database: {db_name}. Valid: {list(DATABASE_PATHS.keys())}")

    db_path = DATABASE_PATHS[db_name]
    conn = sqlite3.connect(db_path)

    try:
        configure_sqlite_connection(conn)
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error in {db_name}: {e}")
        raise
    finally:
        conn.close()
```

**Usage**:
```python
# CORRECT: Always use the context manager
with get_db_connection("notifications") as conn:
    conn.execute("INSERT INTO notifications (message) VALUES (?)", ("Test",))

# WRONG: Direct connection without configuration
conn = sqlite3.connect("notifications.db")  # ❌ No WAL mode, no timeout!
```

---

### 2. Retry Logic for Database Operations

**Problem**: Even with WAL mode, concurrent writes can occasionally fail with `OperationalError: database is locked`.

**Solution**: Wrap all database writes with `@with_retry` decorator.

```python
# coffee_maker/cli/database_operations.py

from coffee_maker.utils.retry_utils import with_retry
from coffee_maker.utils.database import get_db_connection
from sqlite3 import OperationalError
from langfuse.decorators import observe
import logging

logger = logging.getLogger(__name__)


@observe
@with_retry(
    max_attempts=3,
    backoff_base=1.5,
    retriable_exceptions=(OperationalError,),
)
def insert_notification(
    source: str,
    notification_type: str,
    message: str,
    channels: list[str],
) -> int:
    """Insert notification into database with retry protection.

    Args:
        source: 'daemon' or 'project_manager'
        notification_type: 'question', 'status', 'alert'
        message: Notification message
        channels: List of channels (e.g., ['terminal', 'slack'])

    Returns:
        Notification ID

    Raises:
        RetryExhausted: If all retry attempts fail
    """
    with get_db_connection("notifications") as conn:
        cursor = conn.execute(
            """
            INSERT INTO notifications (source, type, message, channels, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', datetime('now'))
            """,
            (source, notification_type, message, ",".join(channels)),
        )
        notification_id = cursor.lastrowid
        logger.info(f"Inserted notification {notification_id} from {source}")
        return notification_id


@observe
@with_retry(
    max_attempts=3,
    backoff_base=1.5,
    retriable_exceptions=(OperationalError,),
)
def update_notification_status(notification_id: int, status: str, response: str = None) -> None:
    """Update notification status with retry protection.

    Args:
        notification_id: Notification ID
        status: New status ('pending', 'sent', 'responded', 'failed')
        response: Optional user response
    """
    with get_db_connection("notifications") as conn:
        conn.execute(
            """
            UPDATE notifications
            SET status = ?, user_response = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (status, response, notification_id),
        )
        logger.info(f"Updated notification {notification_id} status to {status}")
```

**Key Points**:
1. ✅ `@observe` decorator for Langfuse tracking
2. ✅ `@with_retry` decorator for automatic retry on lock errors
3. ✅ Uses `get_db_connection()` context manager
4. ✅ Proper logging for debugging

---

### 3. Notification Database Schema

**File**: `coffee_maker/cli/notification_schema.sql`

```sql
-- Notifications table
-- Stores all notifications sent by daemon or project manager
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL CHECK(source IN ('daemon', 'project_manager')),
    type TEXT NOT NULL CHECK(type IN ('question', 'status', 'alert', 'info')),
    message TEXT NOT NULL,
    channels TEXT NOT NULL,  -- Comma-separated: 'terminal,slack,email'
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'responded', 'failed')),
    user_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_source ON notifications(source);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- Slack interactions table
-- Stores Slack button clicks and responses
CREATE TABLE IF NOT EXISTS slack_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,  -- Slack user ID
    user_name TEXT,  -- Slack username for display
    action TEXT NOT NULL,  -- Button value (e.g., 'daemon:yes', 'pm:/view')
    routed_to TEXT NOT NULL CHECK(routed_to IN ('daemon', 'project_manager')),
    response_data TEXT,  -- JSON blob for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_slack_interactions_notification ON slack_interactions(notification_id);
CREATE INDEX IF NOT EXISTS idx_slack_interactions_user ON slack_interactions(user_id);

-- Roadmap history table
-- Tracks all changes to ROADMAP.md
CREATE TABLE IF NOT EXISTS roadmap_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    changed_by TEXT NOT NULL CHECK(changed_by IN ('user', 'daemon')),
    change_type TEXT NOT NULL CHECK(change_type IN ('add', 'update', 'delete', 'status_change')),
    priority_name TEXT,  -- Which priority was changed
    before_text TEXT,  -- State before change
    after_text TEXT,  -- State after change
    diff TEXT,  -- Git-style diff
    reason TEXT,  -- Why the change was made
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_roadmap_history_priority ON roadmap_history(priority_name);
CREATE INDEX IF NOT EXISTS idx_roadmap_history_changed_by ON roadmap_history(changed_by);
CREATE INDEX IF NOT EXISTS idx_roadmap_history_created_at ON roadmap_history(created_at DESC);
```

**Initialization Script**:

```python
# coffee_maker/cli/init_database.py

from coffee_maker.utils.database import get_db_connection
import logging

logger = logging.getLogger(__name__)


def initialize_notifications_database() -> None:
    """Initialize notifications database with schema.

    CRITICAL: Run this before any database operations.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    with get_db_connection("notifications") as conn:
        # Read schema from file
        schema_path = Path(__file__).parent / "notification_schema.sql"
        schema = schema_path.read_text()

        # Execute schema (creates tables if they don't exist)
        conn.executescript(schema)

        logger.info("Initialized notifications database schema")
```

---

## MVP Feature Set

### Core Features (Must Have)

1. **Roadmap Viewer** (`/view`)
   - Display entire ROADMAP.md
   - Display specific priority
   - Search functionality

2. **Status Updater** (`/update`)
   - Update priority status
   - Update completion percentage
   - Update timeline

3. **Notification System**
   - Send notifications to terminal
   - Store notifications in database
   - Query notification history

4. **Sync to Daemon**
   - Copy ROADMAP.md to daemon's environment
   - Verify sync succeeded

### Deferred Features (Future)

❌ Claude AI integration (too complex for MVP)
❌ Slack integration (separate priority)
❌ Rich terminal UI (basic text is fine)
❌ Roadmap editing (read-only for MVP)
❌ History/undo functionality

---

## CLI Commands (MVP)

```bash
# View roadmap
coffee-roadmap view              # Show entire roadmap
coffee-roadmap view PRIORITY-2   # Show specific priority

# Update status
coffee-roadmap status PRIORITY-2 "in_progress"
coffee-roadmap status PRIORITY-2 "completed"

# Notifications
coffee-roadmap notify "Message from daemon" --source daemon --type status
coffee-roadmap notify "User alert" --source project_manager --type alert
coffee-roadmap notifications list              # Show recent notifications
coffee-roadmap notifications show 123          # Show notification by ID

# Sync
coffee-roadmap sync              # Sync ROADMAP.md to daemon environment

# Database management
coffee-roadmap db init           # Initialize database schema
coffee-roadmap db status         # Show database status
coffee-roadmap db vacuum         # Optimize database
```

---

## Implementation Plan

### Phase 1: Database Foundation (Day 1, 4-6h)

**Deliverables**:
- [ ] `coffee_maker/utils/database.py` - Connection manager with WAL mode
- [ ] `coffee_maker/cli/notification_schema.sql` - Database schema
- [ ] `coffee_maker/cli/init_database.py` - Initialization script
- [ ] `coffee_maker/cli/database_operations.py` - CRUD operations with retry
- [ ] Unit tests for database operations
- [ ] Integration test: concurrent writes

**Acceptance Criteria**:
- ✅ All database connections use WAL mode + timeout
- ✅ All write operations have `@with_retry` decorator
- ✅ Schema creates successfully
- ✅ Concurrent write test passes (10 parallel writes)

---

### Phase 2: Basic CLI (Day 2, 4-6h)

**Deliverables**:
- [ ] `coffee_maker/cli/roadmap_cli.py` - Main CLI entry point
- [ ] `coffee_maker/cli/commands/view.py` - View commands
- [ ] `coffee_maker/cli/commands/status.py` - Status update commands
- [ ] `coffee_maker/cli/commands/notify.py` - Notification commands
- [ ] `coffee_maker/cli/commands/sync.py` - Sync command
- [ ] Setup.py entry point: `coffee-roadmap`

**Acceptance Criteria**:
- ✅ `coffee-roadmap view` displays ROADMAP.md
- ✅ `coffee-roadmap status PRIORITY-2 completed` updates roadmap
- ✅ `coffee-roadmap notify` inserts into database
- ✅ `coffee-roadmap sync` copies to daemon path

---

### Phase 3: Testing & Documentation (Day 3, 2-3h)

**Deliverables**:
- [ ] Integration tests (CLI commands)
- [ ] README.md for Project Manager CLI
- [ ] Database access pattern documentation
- [ ] Video demo (optional)

**Acceptance Criteria**:
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Ready for daemon integration

---

## Database Access Patterns (Critical Guidelines)

### Pattern 1: Read-Heavy Operations

**When**: Querying analytics, viewing notifications, reading roadmap state

```python
# Good: Simple read with retry (in case of write lock)
@with_retry(max_attempts=2, retriable_exceptions=(OperationalError,))
def get_recent_notifications(limit: int = 10) -> list[dict]:
    with get_db_connection("notifications") as conn:
        cursor = conn.execute(
            "SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
```

---

### Pattern 2: Write Operations

**When**: Inserting notifications, updating status, recording history

```python
# Good: Write with retry + transaction
@observe
@with_retry(max_attempts=3, retriable_exceptions=(OperationalError,))
def record_roadmap_change(priority: str, before: str, after: str) -> None:
    with get_db_connection("notifications") as conn:
        conn.execute(
            """
            INSERT INTO roadmap_history (changed_by, change_type, priority_name, before_text, after_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("user", "update", priority, before, after),
        )
        # Context manager automatically commits on success
```

---

### Pattern 3: Batch Operations

**When**: Exporting Langfuse traces, syncing multiple records

```python
# Good: Use transaction for multiple related writes
@observe
@with_retry(max_attempts=3, retriable_exceptions=(OperationalError,))
def export_traces_batch(traces: list[dict]) -> int:
    with get_db_connection("analytics") as conn:
        # Single transaction for all inserts
        conn.executemany(
            "INSERT INTO traces (id, name, input, output) VALUES (?, ?, ?, ?)",
            [(t["id"], t["name"], t["input"], t["output"]) for t in traces],
        )
        return len(traces)
```

---

### Pattern 4: Daemon-Specific Reads

**When**: Daemon needs to read roadmap state, check for notifications

```python
# Daemon reads notification targeted to it
@with_retry(max_attempts=2, retriable_exceptions=(OperationalError,))
def get_pending_notifications_for_daemon() -> list[dict]:
    with get_db_connection("notifications") as conn:
        cursor = conn.execute(
            """
            SELECT * FROM notifications
            WHERE source = 'project_manager' AND status = 'pending'
            ORDER BY created_at ASC
            """,
        )
        return [dict(row) for row in cursor.fetchall()]
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_database_operations.py

import pytest
from coffee_maker.cli.database_operations import insert_notification
from coffee_maker.utils.database import get_db_connection


def test_insert_notification_success():
    """Test inserting notification with proper retry logic."""
    notification_id = insert_notification(
        source="daemon",
        notification_type="status",
        message="Test notification",
        channels=["terminal"],
    )

    assert notification_id > 0

    # Verify it's in database
    with get_db_connection("notifications") as conn:
        cursor = conn.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "daemon"  # source


def test_concurrent_writes():
    """Test that concurrent writes don't cause lock errors."""
    import concurrent.futures

    def write_notification(i: int) -> int:
        return insert_notification(
            source="daemon",
            notification_type="status",
            message=f"Concurrent write {i}",
            channels=["terminal"],
        )

    # Write 10 notifications concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(write_notification, i) for i in range(10)]
        results = [f.result() for f in futures]

    # All should succeed
    assert len(results) == 10
    assert all(r > 0 for r in results)
```

---

### Integration Tests

```bash
# tests/integration/test_cli.sh

#!/bin/bash
set -e

echo "Testing coffee-roadmap CLI..."

# Initialize database
coffee-roadmap db init

# View roadmap
coffee-roadmap view | grep "PRIORITY 1"

# Send notification
coffee-roadmap notify "Test message" --source daemon --type status

# List notifications
coffee-roadmap notifications list | grep "Test message"

# Update status
coffee-roadmap status PRIORITY-1 "in_progress"

# Verify update
coffee-roadmap view PRIORITY-1 | grep "in_progress"

echo "✅ All CLI tests passed!"
```

---

## Rollback Plan

If MVP has critical issues:

1. **Database corruption**: Restore from backup
   ```bash
   cp data/notifications.db.backup data/notifications.db
   ```

2. **Lock errors persist**: Increase timeout
   ```python
   conn.execute("PRAGMA busy_timeout=10000")  # 10 seconds
   ```

3. **Performance issues**: Switch to PostgreSQL (Phase 2)

---

## Success Criteria

MVP is successful if:

1. ✅ Database operations succeed with concurrent access (10+ parallel writes)
2. ✅ No `database is locked` errors in normal operation
3. ✅ Daemon can read notifications written by PM CLI
4. ✅ PM CLI can read notifications written by daemon
5. ✅ All unit tests pass (database + CLI)
6. ✅ Integration test passes (concurrent writes)
7. ✅ Documentation complete and clear
8. ✅ Ready for PRIORITY 3 (Autonomous Daemon) implementation

---

## Next Steps After MVP

1. **Phase 2**: Add Claude AI integration (natural language commands)
2. **Phase 3**: Add Slack integration (notification routing)
3. **Phase 4**: Add rich terminal UI (progress bars, colors)
4. **Phase 5**: Consider PostgreSQL migration (if team grows)

---

## References

- **PRIORITY 1.5 Design**: `docs/PRIORITY_1.5_DATABASE_SYNC_DESIGN.md`
- **Retry Patterns**: `docs/retry_patterns.md` (if exists)
- **Sprint 1 Summary**: `docs/sprint1_improvements_summary.md`
- **ROADMAP**: `docs/roadmap/ROADMAP.md` (Recurring Best Practices section)

---

## Approval

- [ ] User review
- [ ] Database strategy approved (Shared SQLite via Docker volume)
- [ ] MVP scope approved (basic CLI, no AI yet)
- [ ] Ready to implement

---

**Last Updated**: 2025-10-09
**Status**: Ready for implementation
