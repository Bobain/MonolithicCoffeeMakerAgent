#!/usr/bin/env python3
"""Create hierarchical technical specification for PRIORITY 31.

This spec defines how code_developer integrates with work_sessions table
for parallel development support.
"""

import json
import sqlite3
from datetime import datetime

from coffee_maker.autonomous.unified_database import get_unified_database

# Hierarchical spec content
spec_content = {
    "/overview": """
## Overview

Integrate code_developer with work_sessions table to enable parallel development through:
1. Technical spec reading from database (hierarchical specs)
2. Work session claiming with race-safe atomic operations
3. File access validation against assigned_files
4. Work session lifecycle management

**Problem**: code_developer currently:
- Reads ROADMAP directly without work_session tracking
- No assigned_files validation (can touch any file)
- No hierarchical spec reading from database
- Cannot be spawned in parallel safely

**Solution**: Implement work_session integration so multiple code_developers can:
- Claim independent work_sessions atomically
- Read only their assigned spec sections
- Touch only their assigned_files
- Update work_session status throughout execution

**Impact**: Foundation for 2-3x velocity increase through parallel development.
""",
    "/architecture": """
## Architecture

### Current Flow (Without work_sessions)

```
code_developer starts
    ↓
Reads ROADMAP.md directly
    ↓
Finds first "Planned" priority
    ↓
Implements entire priority
    ↓
Can touch ANY file (no validation)
    ↓
Cannot run in parallel (file conflicts)
```

### New Flow (With work_sessions)

```
code_developer --work-session WORK-42 starts
    ↓
Claims work_session atomically (race-safe)
    ↓
Reads technical spec from database using unified-spec-skill
    ↓
Reads ONLY assigned section (e.g., /implementation)
    ↓
Validates file access against assigned_files
    ↓
Implements work
    ↓
Updates work_session status (started_at, commit_sha, completed_at)
    ↓
Multiple instances run in parallel safely
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     code_developer                          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  New: WorkSessionManager                            │   │
│  │  - _query_available_work_sessions()                 │   │
│  │  - _claim_work_session(work_id) [ATOMIC]           │   │
│  │  - _validate_file_access(file_path)                │   │
│  │  - _update_work_session_status(status)             │   │
│  │  - _read_technical_spec_for_work()                 │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Modified: daemon.py                                │   │
│  │  - run() accepts work_session_id argument           │   │
│  │  - Validates all file operations                    │   │
│  │  - Uses unified-spec-skill for spec reading        │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              unified_database.work_sessions                  │
│  - work_id (PK)                                             │
│  - spec_id → technical_specs.id                            │
│  - scope (phase/section/module)                             │
│  - assigned_files (JSON array)                              │
│  - status (pending/in_progress/completed/failed)           │
│  - claimed_by, claimed_at, started_at, completed_at        │
└─────────────────────────────────────────────────────────────┘
```

### Race Condition Handling

Multiple code_developers trying to claim same work_session:

```python
# ATOMIC claim operation
UPDATE work_sessions
SET status = 'in_progress',
    claimed_by = 'code_developer',
    claimed_at = ?
WHERE work_id = ?
  AND status = 'pending'     # ← CRITICAL: only if still pending
  AND claimed_by IS NULL      # ← CRITICAL: not already claimed

# Returns rows_affected
# Only ONE code_developer gets rows_affected=1
# Others get rows_affected=0 (claim failed)
```
""",
    "/api_design": """
## API Design

### New CLI Arguments

```bash
# Spawn code_developer for specific work_session
code-developer --work-session WORK-42

# Spawn code_developer that auto-claims available work
code-developer --claim-available

# Legacy mode (for backward compatibility)
code-developer --priority 25
```

### WorkSessionManager Class

```python
class WorkSessionManager:
    \"\"\"Manages work_session integration for code_developer.\"\"\"

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.current_work_session: Optional[Dict[str, Any]] = None
        self.assigned_files: List[str] = []

    def query_available_work_sessions(
        self,
        scope: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        \"\"\"Query available work_sessions.

        Args:
            scope: Filter by scope (phase/section/module) or None for all

        Returns:
            List of available work_sessions (status='pending')
        \"\"\"

    def claim_work_session(self, work_id: str) -> bool:
        \"\"\"Atomically claim a work_session.

        Args:
            work_id: Work session ID to claim

        Returns:
            True if claimed successfully, False if already claimed

        Raises:
            WorkSessionNotFoundError: If work_id doesn't exist
            WorkSessionAlreadyClaimedError: If already claimed by this instance
        \"\"\"

    def validate_file_access(self, file_path: str) -> bool:
        \"\"\"Validate file access against assigned_files.

        Args:
            file_path: Path to file being accessed

        Returns:
            True if file in assigned_files, False otherwise

        Raises:
            FileAccessViolationError: If file not in assigned_files
        \"\"\"

    def update_work_session_status(
        self,
        status: str,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        \"\"\"Update work_session status.

        Args:
            status: New status (in_progress/completed/failed)
            commit_sha: Git commit SHA (when status='completed')
            error_message: Error message (when status='failed')
        \"\"\"

    def read_technical_spec_for_work(self) -> str:
        \"\"\"Read technical spec section for current work_session.

        Uses unified-spec-skill to read from database.
        Reads only the section specified in work_session.scope_description.

        Returns:
            Markdown content of spec section

        Example:
            work_session.scope_description = "Phase 2: /implementation"
            → Returns content of /implementation section only
        \"\"\"
```

### Modified daemon.py Methods

```python
class DevDaemon:
    def __init__(self, ..., work_session_id: Optional[str] = None):
        \"\"\"Initialize daemon with optional work_session_id.\"\"\"
        self.work_session_manager = WorkSessionManager(db_path)
        self.work_session_id = work_session_id

    def run(self) -> None:
        \"\"\"Main daemon loop.\"\"\"
        if self.work_session_id:
            # New path: work_session-based execution
            success = self.work_session_manager.claim_work_session(
                self.work_session_id
            )
            if not success:
                logger.error(f"Failed to claim work_session {self.work_session_id}")
                return

            # Read technical spec section
            spec_content = self.work_session_manager.read_technical_spec_for_work()

            # Update status to in_progress
            self.work_session_manager.update_work_session_status('in_progress')

            try:
                # Implement work using spec_content
                self._implement_from_spec(spec_content)

                # Commit changes
                commit_sha = self._git_commit()

                # Update status to completed
                self.work_session_manager.update_work_session_status(
                    'completed',
                    commit_sha=commit_sha
                )
            except Exception as e:
                # Update status to failed
                self.work_session_manager.update_work_session_status(
                    'failed',
                    error_message=str(e)
                )
                raise
        else:
            # Legacy path: ROADMAP-based execution
            self._run_legacy_mode()

    def _validate_file_operation(self, file_path: str) -> None:
        \"\"\"Validate file operation against assigned_files.\"\"\"
        if self.work_session_id:
            if not self.work_session_manager.validate_file_access(file_path):
                raise FileAccessViolationError(
                    f"File {file_path} not in assigned_files for "
                    f"work_session {self.work_session_id}"
                )
```
""",
    "/data_model": """
## Data Model

### work_sessions Table (Already Exists)

```sql
CREATE TABLE work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id TEXT NOT NULL UNIQUE,           -- "WORK-42"
    spec_id TEXT NOT NULL,                  -- Links to technical_specs.id
    roadmap_item_id TEXT,                   -- Links to roadmap_items.id
    scope TEXT NOT NULL,                    -- "phase", "section", "module"
    scope_description TEXT,                 -- "Phase 2: /implementation"
    assigned_files TEXT,                    -- JSON: ["file1.py", "file2.py"]
    branch_name TEXT NOT NULL UNIQUE,       -- "roadmap-work-42"
    worktree_path TEXT,                     -- Path to git worktree
    status TEXT NOT NULL DEFAULT 'pending', -- pending/in_progress/completed/failed
    claimed_by TEXT,                        -- "code_developer"
    claimed_at TEXT,                        -- ISO timestamp
    started_at TEXT,                        -- When work started
    completed_at TEXT,                      -- When work finished
    commit_sha TEXT,                        -- Final commit SHA
    merged_at TEXT,                         -- When merged to roadmap
    created_by TEXT NOT NULL DEFAULT 'architect',
    created_at TEXT NOT NULL,

    FOREIGN KEY (spec_id) REFERENCES technical_specs(id),
    FOREIGN KEY (roadmap_item_id) REFERENCES roadmap_items(id)
);
```

### work_session Lifecycle States

```
┌──────────┐
│ pending  │  ← Created by architect
└─────┬────┘
      │ code_developer claims
      ↓
┌──────────────┐
│ in_progress  │  ← Code development happening
└──────┬───────┘
       │
       ├─→ Success ──→ ┌───────────┐
       │                │ completed │
       │                └───────────┘
       │
       └─→ Error ────→ ┌─────────┐
                        │ failed  │
                        └─────────┘
```

### assigned_files JSON Schema

```json
{
  "type": "array",
  "items": {
    "type": "string",
    "description": "Relative file path from repo root"
  },
  "example": [
    "coffee_maker/autonomous/daemon.py",
    "coffee_maker/autonomous/daemon_implementation.py",
    "tests/unit/test_daemon_work_sessions.py"
  ]
}
```

### scope_description Format

Format: `"{Phase/Section Name}: {Hierarchical Path}"`

Examples:
- `"Phase 1: Database schema (/database_design)"`
- `"Phase 2: API implementation (/api_design, /implementation)"`
- `"Section: Testing (/test_strategy)"`
- `"Module: WorkSessionManager class"`
""",
    "/implementation": """
## Implementation

### Phase 1: WorkSessionManager Foundation (2-3 hours)

**File**: `coffee_maker/autonomous/work_session_manager.py` (NEW)

```python
\"\"\"Work session management for code_developer parallel execution.\"\"\"

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FileAccessViolationError(Exception):
    \"\"\"Raised when code_developer tries to access file not in assigned_files.\"\"\"


class WorkSessionNotFoundError(Exception):
    \"\"\"Raised when work_session_id doesn't exist in database.\"\"\"


class WorkSessionAlreadyClaimedError(Exception):
    \"\"\"Raised when trying to claim already-claimed work_session.\"\"\"


class WorkSessionManager:
    \"\"\"Manages work_session integration for code_developer.\"\"\"

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.current_work_session: Optional[Dict[str, Any]] = None
        self.assigned_files: List[str] = []

    def query_available_work_sessions(
        self, scope: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        \"\"\"Query available work_sessions from database.\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if scope:
            cursor.execute(
                \"\"\"
                SELECT * FROM work_sessions
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                  AND scope = ?
                ORDER BY created_at ASC
            \"\"\",
                (scope,),
            )
        else:
            cursor.execute(
                \"\"\"
                SELECT * FROM work_sessions
                WHERE status = 'pending'
                  AND claimed_by IS NULL
                ORDER BY created_at ASC
            \"\"\"
            )

        work_sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return work_sessions

    def claim_work_session(self, work_id: str) -> bool:
        \"\"\"Atomically claim a work_session (race-safe).\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if work_session exists
            cursor.execute(
                \"SELECT status, claimed_by FROM work_sessions WHERE work_id = ?\",
                (work_id,),
            )
            result = cursor.fetchone()

            if not result:
                raise WorkSessionNotFoundError(f"work_session {work_id} not found")

            status, claimed_by = result

            if claimed_by == "code_developer" and self.current_work_session:
                raise WorkSessionAlreadyClaimedError(
                    f"work_session {work_id} already claimed by this instance"
                )

            # ATOMIC claim operation
            now = datetime.now().isoformat()
            cursor.execute(
                \"\"\"
                UPDATE work_sessions
                SET status = 'in_progress',
                    claimed_by = 'code_developer',
                    claimed_at = ?
                WHERE work_id = ?
                  AND status = 'pending'
                  AND claimed_by IS NULL
            \"\"\",
                (now, work_id),
            )

            rows_affected = cursor.rowcount

            if rows_affected == 0:
                # Claim failed (another instance claimed it)
                logger.warning(f"Failed to claim work_session {work_id} - already claimed")
                conn.close()
                return False

            # Load full work_session data
            cursor.execute(
                \"SELECT * FROM work_sessions WHERE work_id = ?\", (work_id,)
            )
            conn.row_factory = sqlite3.Row
            self.current_work_session = dict(cursor.fetchone())

            # Parse assigned_files
            self.assigned_files = json.loads(
                self.current_work_session["assigned_files"]
            )

            conn.commit()
            logger.info(
                f"✅ Successfully claimed work_session {work_id} with "
                f"{len(self.assigned_files)} assigned files"
            )
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error claiming work_session {work_id}: {e}")
            raise
        finally:
            conn.close()

    def validate_file_access(self, file_path: str) -> bool:
        \"\"\"Validate file access against assigned_files.\"\"\"
        if not self.current_work_session:
            # No work_session active, allow all files (legacy mode)
            return True

        # Normalize file path
        file_path = str(Path(file_path))

        # Check if file in assigned_files
        for assigned_file in self.assigned_files:
            assigned_path = str(Path(assigned_file))
            if file_path == assigned_path or file_path.endswith(assigned_path):
                return True

        # File not in assigned_files
        raise FileAccessViolationError(
            f"File access violation: {file_path} not in assigned_files for "
            f"work_session {self.current_work_session['work_id']}.\\n"
            f"Assigned files: {self.assigned_files}"
        )

    def update_work_session_status(
        self,
        status: str,
        commit_sha: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        \"\"\"Update work_session status in database.\"\"\"
        if not self.current_work_session:
            raise ValueError("No active work_session to update")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if status == "in_progress":
            cursor.execute(
                \"\"\"
                UPDATE work_sessions
                SET status = ?,
                    started_at = ?
                WHERE work_id = ?
            \"\"\",
                (status, now, self.current_work_session["work_id"]),
            )
        elif status == "completed":
            cursor.execute(
                \"\"\"
                UPDATE work_sessions
                SET status = ?,
                    completed_at = ?,
                    commit_sha = ?
                WHERE work_id = ?
            \"\"\",
                (status, now, commit_sha, self.current_work_session["work_id"]),
            )
        elif status == "failed":
            # Store error in scope_description (or add error_message column)
            cursor.execute(
                \"\"\"
                UPDATE work_sessions
                SET status = ?,
                    completed_at = ?
                WHERE work_id = ?
            \"\"\",
                (status, now, self.current_work_session["work_id"]),
            )
            logger.error(f"work_session {self.current_work_session['work_id']} failed: {error_message}")

        conn.commit()
        conn.close()

        logger.info(
            f"Updated work_session {self.current_work_session['work_id']} "
            f"status to {status}"
        )

    def read_technical_spec_for_work(self) -> str:
        \"\"\"Read technical spec section for current work_session.\"\"\"
        if not self.current_work_session:
            raise ValueError("No active work_session")

        spec_id = self.current_work_session["spec_id"]
        scope_description = self.current_work_session["scope_description"]

        # Parse section path from scope_description
        # Format: "Phase 2: /implementation" or "Section: /api_design, /implementation"
        import re

        section_paths = re.findall(r"/\w+", scope_description)

        if not section_paths:
            # No section specified, read entire spec
            return self._read_full_spec(spec_id)

        # Read specific sections using unified-spec-skill
        # For now, read from database directly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            \"SELECT content, spec_type FROM technical_specs WHERE id = ?\",
            (spec_id,),
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Technical spec {spec_id} not found")

        content, spec_type = result

        if spec_type != "hierarchical":
            # Non-hierarchical spec, return full content
            return content

        # Parse hierarchical spec JSON
        spec_json = json.loads(content)

        # Extract requested sections
        section_content = []
        for section_path in section_paths:
            section_key = section_path.lstrip("/")
            if section_key in spec_json:
                section_content.append(f"## {section_path}")
                section_content.append(spec_json[section_key])
            else:
                logger.warning(
                    f"Section {section_path} not found in spec {spec_id}"
                )

        return "\\n\\n".join(section_content)

    def _read_full_spec(self, spec_id: str) -> str:
        \"\"\"Read full technical spec (all sections).\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            \"SELECT content, spec_type FROM technical_specs WHERE id = ?\",
            (spec_id,),
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Technical spec {spec_id} not found")

        content, spec_type = result

        if spec_type != "hierarchical":
            return content

        # Hierarchical spec - combine all sections
        spec_json = json.loads(content)
        sections = []
        for section_key, section_content in spec_json.items():
            sections.append(f"## /{section_key}")
            sections.append(section_content)

        return "\\n\\n".join(sections)
```

### Phase 2: daemon.py Integration (2-3 hours)

**File**: `coffee_maker/autonomous/daemon.py` (MODIFY)

```python
# Add imports
from coffee_maker.autonomous.work_session_manager import (
    WorkSessionManager,
    FileAccessViolationError,
    WorkSessionNotFoundError,
)

class DevDaemon:
    def __init__(
        self,
        ...
        work_session_id: Optional[str] = None,
    ):
        ...
        # Add work_session support
        self.work_session_id = work_session_id
        self.work_session_manager: Optional[WorkSessionManager] = None

        if work_session_id:
            db = get_unified_database()
            self.work_session_manager = WorkSessionManager(db.db_path)

    def run(self) -> None:
        \"\"\"Main daemon loop.\"\"\"
        if self.work_session_id:
            return self._run_work_session_mode()
        else:
            return self._run_legacy_mode()

    def _run_work_session_mode(self) -> None:
        \"\"\"Execute work_session-based development.\"\"\"
        try:
            # Claim work_session
            success = self.work_session_manager.claim_work_session(
                self.work_session_id
            )
            if not success:
                logger.error(
                    f"Failed to claim work_session {self.work_session_id}"
                )
                return

            # Read technical spec section
            spec_content = self.work_session_manager.read_technical_spec_for_work()
            logger.info(
                f"Read {len(spec_content)} chars from technical spec "
                f"for work_session {self.work_session_id}"
            )

            # Update status to in_progress
            self.work_session_manager.update_work_session_status("in_progress")

            # Implement work using spec_content
            self._implement_from_spec(spec_content)

            # Commit changes
            commit_sha = self._git_commit_work_session()

            # Update status to completed
            self.work_session_manager.update_work_session_status(
                "completed", commit_sha=commit_sha
            )

            logger.info(
                f"✅ work_session {self.work_session_id} completed successfully"
            )

        except FileAccessViolationError as e:
            logger.error(f"File access violation: {e}")
            self.work_session_manager.update_work_session_status(
                "failed", error_message=str(e)
            )
            raise

        except Exception as e:
            logger.error(f"work_session {self.work_session_id} failed: {e}")
            self.work_session_manager.update_work_session_status(
                "failed", error_message=str(e)
            )
            raise

    def _validate_file_operation(self, file_path: str) -> None:
        \"\"\"Validate file operation against assigned_files.\"\"\"
        if self.work_session_manager:
            self.work_session_manager.validate_file_access(file_path)
```

### Phase 3: CLI Integration (1 hour)

**File**: `coffee_maker/autonomous/daemon_cli.py` (MODIFY)

```python
def main() -> None:
    parser = argparse.ArgumentParser(...)

    # Add work_session argument
    parser.add_argument(
        "--work-session",
        type=str,
        help="Work session ID to claim and execute (e.g., WORK-42)"
    )

    args = parser.parse_args()

    # Create daemon with work_session support
    daemon = DevDaemon(
        ...
        work_session_id=args.work_session,
    )

    daemon.run()
```
""",
    "/test_strategy": """
## Test Strategy

### Unit Tests

**File**: `tests/unit/test_work_session_manager.py` (NEW)

```python
def test_query_available_work_sessions():
    \"\"\"Test querying available work_sessions.\"\"\"
    # Setup: Create 3 work_sessions (2 pending, 1 in_progress)
    # Execute: Query available work_sessions
    # Assert: Returns only 2 pending work_sessions

def test_claim_work_session_success():
    \"\"\"Test successful work_session claiming.\"\"\"
    # Setup: Create pending work_session
    # Execute: Claim work_session
    # Assert: status='in_progress', claimed_by='code_developer'

def test_claim_work_session_race_condition():
    \"\"\"Test race condition handling.\"\"\"
    # Setup: Create pending work_session
    # Execute: 2 instances try to claim simultaneously
    # Assert: Only 1 succeeds, 1 fails

def test_validate_file_access_allowed():
    \"\"\"Test file access validation (allowed).\"\"\"
    # Setup: Claim work_session with assigned_files=["foo.py"]
    # Execute: Validate access to "foo.py"
    # Assert: Returns True

def test_validate_file_access_denied():
    \"\"\"Test file access validation (denied).\"\"\"
    # Setup: Claim work_session with assigned_files=["foo.py"]
    # Execute: Validate access to "bar.py"
    # Assert: Raises FileAccessViolationError

def test_update_work_session_status():
    \"\"\"Test status updates.\"\"\"
    # Test: pending → in_progress
    # Test: in_progress → completed (with commit_sha)
    # Test: in_progress → failed (with error_message)

def test_read_technical_spec_hierarchical():
    \"\"\"Test reading hierarchical spec sections.\"\"\"
    # Setup: Create hierarchical spec with /overview, /implementation
    # Setup: Create work_session with scope_description="Phase 1: /implementation"
    # Execute: read_technical_spec_for_work()
    # Assert: Returns only /implementation section
```

### Integration Tests

**File**: `tests/integration/test_daemon_work_sessions.py` (NEW)

```python
def test_daemon_work_session_end_to_end():
    \"\"\"Test full work_session execution.\"\"\"
    # Setup: Create technical spec in database
    # Setup: Create work_session with assigned_files
    # Execute: Spawn code_developer --work-session WORK-TEST
    # Assert: work_session claimed
    # Assert: Code implemented
    # Assert: Files touched match assigned_files
    # Assert: work_session status='completed'
    # Assert: commit_sha recorded

def test_parallel_code_developers():
    \"\"\"Test 2 code_developers claiming different work_sessions.\"\"\"
    # Setup: Create 2 work_sessions (WORK-1, WORK-2)
    # Execute: Spawn 2 code_developers simultaneously
    # Assert: Both claim different work_sessions
    # Assert: No file conflicts
    # Assert: Both complete successfully

def test_file_access_violation_enforcement():
    \"\"\"Test file access violation is enforced.\"\"\"
    # Setup: Create work_session with assigned_files=["foo.py"]
    # Execute: code_developer tries to modify "bar.py"
    # Assert: FileAccessViolationError raised
    # Assert: work_session status='failed'
```

### Manual Testing

```bash
# Test 1: Query available work_sessions
python3 -c "
from coffee_maker.autonomous.work_session_manager import WorkSessionManager
mgr = WorkSessionManager('data/unified_roadmap_specs.db')
sessions = mgr.query_available_work_sessions()
print(f'Available: {len(sessions)} work_sessions')
"

# Test 2: Claim work_session
code-developer --work-session WORK-42 --auto-approve

# Test 3: Parallel execution
code-developer --work-session WORK-42 &
code-developer --work-session WORK-43 &
wait
```
""",
    "/dependencies": """
## Dependencies

### Required (Already Available)

✅ **work_sessions table** (commit 64e78e7)
- Table structure complete
- Indexes created
- Ready for use

✅ **technical_specs table with hierarchical specs**
- Stores specs as JSON with section keys
- /overview, /architecture, /api_design, etc.

✅ **unified-spec-skill**
- Can read hierarchical specs from database
- Supports section-based reading

✅ **unified_database.py**
- Database access layer
- Connection management

### New Dependencies

**None** - All required infrastructure already exists!

### Version Compatibility

- Python 3.8+
- SQLite 3.24+
- All existing dependencies remain unchanged
""",
    "/success_criteria": """
## Success Criteria

### Functional Requirements

- [ ] **CLI Argument**: code_developer accepts `--work-session WORK-42` argument
- [ ] **work_session Query**: code_developer can query available work_sessions from database
- [ ] **Atomic Claiming**: code_developer claims work_session atomically (race-safe)
- [ ] **Race Condition Handling**: Multiple code_developers can't claim same work_session
- [ ] **Spec Reading**: code_developer reads technical spec from database using unified-spec-skill
- [ ] **Section Reading**: code_developer reads only assigned spec sections (e.g., /implementation)
- [ ] **File Validation**: code_developer validates ALL file operations against assigned_files
- [ ] **File Access Denial**: code_developer raises FileAccessViolationError for non-assigned files
- [ ] **Status Updates**: code_developer updates work_session.started_at on start
- [ ] **Commit Recording**: code_developer updates work_session.commit_sha on completion
- [ ] **Completion Recording**: code_developer updates work_session.completed_at on success
- [ ] **Status Completed**: code_developer updates work_session.status='completed' on success
- [ ] **Status Failed**: code_developer updates work_session.status='failed' on error

### Integration Requirements

- [ ] **Integration Test**: Spawn 2 code_developers, both claim different work_sessions
- [ ] **File Violation Test**: code_developer fails when trying to touch file NOT in assigned_files
- [ ] **Race Condition Test**: 3 code_developers try to claim same work_session, only 1 succeeds
- [ ] **End-to-End Test**: Full work_session execution from claim to completion

### Performance Requirements

- [ ] **Claiming Latency**: work_session claiming completes in <100ms
- [ ] **File Validation Latency**: File access validation completes in <10ms
- [ ] **Database Query**: Query available work_sessions completes in <50ms

### Quality Requirements

- [ ] **Test Coverage**: ≥90% code coverage for WorkSessionManager
- [ ] **Error Handling**: All database errors handled gracefully
- [ ] **Logging**: All work_session operations logged at INFO level
- [ ] **Type Hints**: All new methods have type hints
- [ ] **Documentation**: Docstrings for all public methods

### Backward Compatibility

- [ ] **Legacy Mode**: code_developer still works without --work-session argument
- [ ] **ROADMAP Mode**: code_developer can still read ROADMAP.md directly
- [ ] **No Breaking Changes**: Existing code_developer usage remains functional
""",
}


def main():
    """Insert SPEC-131 into database."""
    db = get_unified_database()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    spec_id = "SPEC-131"
    spec_number = 131
    title = "code_developer work_sessions Integration for Parallel Development"
    roadmap_item_id = "PRIORITY-31"

    # Check if spec already exists
    cursor.execute("SELECT id FROM technical_specs WHERE id = ?", (spec_id,))
    exists = cursor.fetchone()

    if exists:
        print(f"⚠️  Spec {spec_id} already exists, updating...")
        cursor.execute(
            """
            UPDATE technical_specs
            SET content = ?,
                updated_at = ?,
                updated_by = 'architect',
                title = ?,
                roadmap_item_id = ?,
                status = 'approved',
                spec_type = 'hierarchical',
                estimated_hours = 7
            WHERE id = ?
        """,
            (
                json.dumps(spec_content),
                datetime.now().isoformat(),
                title,
                roadmap_item_id,
                spec_id,
            ),
        )
        print(f"✅ Updated {spec_id}")
    else:
        # Insert new spec
        cursor.execute(
            """
            INSERT INTO technical_specs (
                id, spec_number, title, roadmap_item_id,
                status, spec_type, content,
                estimated_hours, updated_at, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                spec_id,
                spec_number,
                title,
                roadmap_item_id,
                "approved",
                "hierarchical",
                json.dumps(spec_content),
                7,  # estimated_hours
                datetime.now().isoformat(),
                "architect",
            ),
        )
        print(f"✅ Created {spec_id}: {title}")

    conn.commit()
    conn.close()

    print(f"\n📋 Spec sections:")
    for section_key in spec_content.keys():
        section_length = len(spec_content[section_key])
        print(f"  {section_key}: {section_length} chars")

    print(f"\n🎯 Total spec size: {len(json.dumps(spec_content))} chars")


if __name__ == "__main__":
    main()
