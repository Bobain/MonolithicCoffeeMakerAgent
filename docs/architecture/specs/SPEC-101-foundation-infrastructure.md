# SPEC-101: Foundation Infrastructure for Unified Agent Commands

**Status**: Draft
**Created**: 2025-10-26
**Author**: architect
**Parent Spec**: SPEC-100
**Related CFRs**: CFR-007 (Context Budget), CFR-014 (Database Tracing), CFR-015 (Centralized Database)
**Dependencies**: None (foundational)

## Executive Summary

Implement the core infrastructure for the unified agent commands architecture: `DomainWrapper`, `CommandLoader`, and `Command` classes. This foundation enables **permission-enforced**, **audit-tracked**, **skill-integrated** command execution while **wrapping existing database classes** without modification.

### Key Design Principles

1. **Wrap, don't replace** - Use existing `RoadmapDatabase`, `NotificationDatabase`, etc.
2. **Permission enforcement** - Table-level ownership controls
3. **Full audit trails** - Every operation logged to `system_audit`
4. **Skill integration** - Commands can declare and use skills
5. **Markdown-driven** - Commands defined in `.md` files with frontmatter

---

## Architecture Overview

### Component Relationship

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Classes                             │
│  (ArchitectAgent, CodeDeveloperAgent, ProjectManagerAgent)  │
└──────────────────┬───────────────────────────────────────────┘
                   │ creates
┌──────────────────▼───────────────────────────────────────────┐
│              CommandLoader                                   │
│  - Loads .md command files for agent                        │
│  - Parses frontmatter metadata                              │
│  - Validates permissions                                     │
│  - Loads required skills                                     │
│  - Executes commands with parameters                         │
└──────────────────┬───────────────────────────────────────────┘
                   │ manages
┌──────────────────▼───────────────────────────────────────────┐
│                 Command                                      │
│  - Encapsulates single responsibility                       │
│  - Declares tables (read/write), files, skills              │
│  - Implements execute() method                              │
│  - Returns structured results                               │
└──────────────────┬───────────────────────────────────────────┘
                   │ uses
┌──────────────────▼───────────────────────────────────────────┐
│              DomainWrapper                                   │
│  - Enforces table ownership permissions                     │
│  - Wraps RoadmapDatabase and other DBs                      │
│  - Adds audit trail to all operations                       │
│  - Provides read/write/notify methods                       │
└──────────────────┬───────────────────────────────────────────┘
                   │ wraps
┌──────────────────▼───────────────────────────────────────────┐
│         Existing Database Classes (UNCHANGED)               │
│  RoadmapDatabase, NotificationDatabase, SkillRegistry       │
└──────────────────────────────────────────────────────────────┘
```

---

## Component 1: DomainWrapper

### Purpose

Enforce database domain boundaries by wrapping existing database classes with permission checks and audit logging.

### Design

```python
# coffee_maker/database/domain_wrapper.py

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import logging

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

logger = logging.getLogger(__name__)


class PermissionError(Exception):
    """Raised when agent attempts unauthorized database operation."""
    pass


class DomainWrapper:
    """Permission-enforced wrapper for database operations.

    Wraps existing database classes (RoadmapDatabase, etc.) with:
    - Table ownership permission checks
    - Audit trail logging
    - Inter-agent notifications

    Example:
        >>> db = DomainWrapper(AgentType.ARCHITECT)
        >>> db.write("specs_specification", {"id": "SPEC-101", "title": "..."})
        >>> items = db.read("roadmap_priority", {"status": "📝 Planned"})
    """

    # Table ownership mapping (who can write to each table)
    TABLE_OWNERSHIP = {
        # Project Manager domain
        "roadmap_priority": AgentType.PROJECT_MANAGER,
        "roadmap_metadata": AgentType.PROJECT_MANAGER,
        "roadmap_audit": AgentType.PROJECT_MANAGER,
        "roadmap_notification": AgentType.PROJECT_MANAGER,

        # Architect domain
        "specs_specification": AgentType.ARCHITECT,
        "specs_task": AgentType.ARCHITECT,

        # Developer domain
        "review_commit": AgentType.CODE_DEVELOPER,

        # Reviewer domain
        "review_code_review": AgentType.CODE_REVIEWER,

        # Orchestrator domain
        "agent_lifecycle": AgentType.ORCHESTRATOR,
        "orchestrator_task": AgentType.ORCHESTRATOR,
        "agent_message": AgentType.ORCHESTRATOR,

        # Shared (all agents can write)
        "notifications": "shared",
        "system_audit": "shared",
    }

    # Read permissions mapping (who can read from tables)
    READ_PERMISSIONS = {
        AgentType.ARCHITECT: [
            "roadmap_priority", "specs_*", "review_code_review",
            "notifications", "system_audit"
        ],
        AgentType.CODE_DEVELOPER: [
            "roadmap_priority", "specs_*", "review_commit",
            "notifications", "system_audit"
        ],
        AgentType.PROJECT_MANAGER: ["*"],  # Can read everything for monitoring
        AgentType.CODE_REVIEWER: [
            "specs_*", "review_*", "roadmap_priority",
            "notifications", "system_audit"
        ],
        AgentType.ORCHESTRATOR: ["*"],  # Can read everything for coordination
        AgentType.ASSISTANT: ["*"],  # Can read everything for demos
        AgentType.USER_LISTENER: ["roadmap_priority", "notifications"],
        AgentType.UX_DESIGN_EXPERT: ["roadmap_priority", "specs_specification"],
    }

    def __init__(self, agent_type: AgentType, db_path: Optional[Path] = None):
        """Initialize domain wrapper.

        Args:
            agent_type: Type of agent using this wrapper
            db_path: Path to SQLite database (default: data/roadmap.db)
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value

        if db_path is None:
            db_path = Path("data/roadmap.db")

        # Wrap existing RoadmapDatabase
        self.db = RoadmapDatabase(db_path, agent_name=self.agent_name)
        self.read_tables = self.READ_PERMISSIONS.get(agent_type, [])

        logger.info(
            f"DomainWrapper initialized for {self.agent_name} "
            f"(write: {self._get_writable_tables()}, read: {self.read_tables})"
        )

    def _get_writable_tables(self) -> List[str]:
        """Get list of tables this agent can write to."""
        writable = []
        for table, owner in self.TABLE_OWNERSHIP.items():
            if owner == "shared" or owner == self.agent_type:
                writable.append(table)
        return writable

    def can_write(self, table: str) -> bool:
        """Check if agent has write permission for table.

        Args:
            table: Table name to check

        Returns:
            True if agent can write to table
        """
        ownership = self.TABLE_OWNERSHIP.get(table)
        return ownership == "shared" or ownership == self.agent_type

    def can_read(self, table: str) -> bool:
        """Check if agent has read permission for table.

        Args:
            table: Table name to check

        Returns:
            True if agent can read from table
        """
        # Wildcard permission
        if "*" in self.read_tables:
            return True

        # Exact match
        if table in self.read_tables:
            return True

        # Pattern match (e.g., "specs_*" matches "specs_specification")
        for pattern in self.read_tables:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if table.startswith(prefix):
                    return True

        return False

    def _audit_log(self, action: str, table: str, item_id: str, details: Dict[str, Any]):
        """Log operation to audit trail.

        Args:
            action: Action performed ('create', 'update', 'delete', 'read')
            table: Table affected
            item_id: ID of item affected
            details: Additional details (field_changed, old_value, new_value)
        """
        import sqlite3

        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO system_audit (
                table_name, item_id, action, field_changed,
                old_value, new_value, changed_by, changed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                table,
                item_id,
                action,
                details.get("field_changed"),
                details.get("old_value"),
                details.get("new_value"),
                self.agent_name,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def write(self, table: str, data: Dict[str, Any], action: str = "create") -> Any:
        """Write data to table with permission check and audit.

        Args:
            table: Table to write to
            data: Data to write
            action: Action type ('create', 'update', 'delete')

        Returns:
            Result of write operation

        Raises:
            PermissionError: If agent lacks write permission
        """
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_name} cannot write to {table}. "
                f"Owner: {self.TABLE_OWNERSHIP.get(table, 'unknown')}"
            )

        # Add tracking metadata
        data["updated_by"] = self.agent_name
        data["updated_at"] = datetime.now().isoformat()

        # Delegate to appropriate method based on table
        result = self._write_to_table(table, data, action)

        # Audit log
        self._audit_log(
            action=action,
            table=table,
            item_id=data.get("id", "unknown"),
            details={"field_changed": "all", "new_value": json.dumps(data)[:200]}
        )

        logger.info(f"{self.agent_name} wrote to {table}: {action} {data.get('id', '')}")

        return result

    def _write_to_table(self, table: str, data: Dict[str, Any], action: str) -> Any:
        """Delegate write to appropriate database method.

        Args:
            table: Table name
            data: Data to write
            action: Action type

        Returns:
            Write operation result
        """
        # Use existing RoadmapDatabase methods where available
        if table == "roadmap_priority":
            if action == "create":
                return self.db.insert_item(data)
            elif action == "update":
                return self.db.update_item(data["id"], data)

        # Generic write for other tables
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        if action == "create":
            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            cursor.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                tuple(data.values())
            )
        elif action == "update":
            set_clause = ", ".join(f"{k} = ?" for k in data.keys() if k != "id")
            cursor.execute(
                f"UPDATE {table} SET {set_clause} WHERE id = ?",
                tuple(v for k, v in data.items() if k != "id") + (data["id"],)
            )

        conn.commit()
        result = cursor.lastrowid
        conn.close()

        return result

    def read(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Read data from table with permission check.

        Args:
            table: Table to read from
            conditions: Optional WHERE conditions

        Returns:
            List of matching records

        Raises:
            PermissionError: If agent lacks read permission
        """
        if not self.can_read(table):
            raise PermissionError(
                f"{self.agent_name} cannot read from {table}"
            )

        # Use existing RoadmapDatabase methods where available
        if table == "roadmap_priority":
            items = self.db.get_all_items()

            # Apply conditions if provided
            if conditions:
                items = [
                    item for item in items
                    if all(item.get(k) == v for k, v in conditions.items())
                ]

            return items

        # Generic read for other tables
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if conditions:
            where_clause = " AND ".join(f"{k} = ?" for k in conditions.keys())
            cursor.execute(
                f"SELECT * FROM {table} WHERE {where_clause}",
                tuple(conditions.values())
            )
        else:
            cursor.execute(f"SELECT * FROM {table}")

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def send_notification(
        self,
        target_agent: str,
        notification_type: str,
        item_id: Optional[str] = None,
        message: Optional[str] = None
    ) -> int:
        """Send notification to another agent.

        Args:
            target_agent: Agent to notify
            notification_type: Type of notification
            item_id: Optional related item ID
            message: Optional message content

        Returns:
            Notification ID
        """
        notification_data = {
            "target_agent": target_agent,
            "source_agent": self.agent_name,
            "notification_type": notification_type,
            "item_id": item_id,
            "message": message,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        return self.write("notifications", notification_data, action="create")
```

### Database Schema Requirements

**No changes required** - Uses existing tables:
- `system_audit` - Already exists
- `notifications` - Already exists
- All domain tables - Already exist

### Testing Requirements

```python
# tests/unit/test_domain_wrapper.py

def test_permission_enforcement():
    """Test that permission checks work correctly."""
    # Developer cannot write to architect tables
    dev_db = DomainWrapper(AgentType.CODE_DEVELOPER)

    with pytest.raises(PermissionError):
        dev_db.write("specs_specification", {"id": "SPEC-101"})

    # But can write to own tables
    dev_db.write("review_commit", {"id": "commit-1", "commit_hash": "abc123"})

def test_read_permissions():
    """Test that read permissions work correctly."""
    # User listener has limited read access
    listener_db = DomainWrapper(AgentType.USER_LISTENER)

    # Can read roadmap
    items = listener_db.read("roadmap_priority")
    assert isinstance(items, list)

    # Cannot read specs
    with pytest.raises(PermissionError):
        listener_db.read("specs_specification")

def test_audit_logging():
    """Test that all operations are logged."""
    db = DomainWrapper(AgentType.ARCHITECT)

    # Write operation
    db.write("specs_specification", {"id": "SPEC-101", "title": "Test"})

    # Check audit log
    audits = db.read("system_audit", {"table_name": "specs_specification"})
    assert len(audits) > 0
    assert audits[-1]["action"] == "create"
    assert audits[-1]["changed_by"] == "architect"
```

---

## Component 2: CommandLoader

### Purpose

Load command definitions from markdown files, validate permissions, manage skills, and execute commands.

### Design

```python
# coffee_maker/commands/command_loader.py

import frontmatter
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.database.domain_wrapper import DomainWrapper
from coffee_maker.commands.command import Command

logger = logging.getLogger(__name__)


class CommandLoader:
    """Loads and executes commands for an agent from markdown files.

    Commands are defined as markdown files with frontmatter metadata:

    ```markdown
    ---
    command: architect.create_spec
    agent: architect
    action: create_spec
    tables:
      write: [specs_specification]
      read: [roadmap_priority]
    required_skills: [technical_specification_handling]
    ---

    # Command: architect.create_spec

    ## Purpose
    Create a technical specification for a priority...
    ```

    Example:
        >>> loader = CommandLoader(AgentType.ARCHITECT)
        >>> result = loader.execute("create_spec", {"priority_id": "PRIORITY-25"})
    """

    def __init__(self, agent_type: AgentType, commands_dir: Optional[Path] = None):
        """Initialize command loader.

        Args:
            agent_type: Type of agent
            commands_dir: Directory containing command files (default: .claude/commands/agents/{agent})
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.db = DomainWrapper(agent_type)

        if commands_dir is None:
            commands_dir = Path(f".claude/commands/agents/{self.agent_name}")

        self.commands_dir = commands_dir
        self.commands: Dict[str, Command] = {}

        # Load all commands for this agent
        if self.commands_dir.exists():
            self._load_commands()
        else:
            logger.warning(f"Commands directory not found: {self.commands_dir}")

    def _load_commands(self):
        """Load all command markdown files for this agent."""
        command_files = list(self.commands_dir.glob("*.md"))

        for cmd_file in command_files:
            try:
                command = self._parse_command(cmd_file)
                self.commands[command.action] = command
                logger.debug(f"Loaded command: {command.name}")
            except Exception as e:
                logger.error(f"Failed to load command {cmd_file}: {e}")

        logger.info(f"Loaded {len(self.commands)} commands for {self.agent_name}")

    def _parse_command(self, path: Path) -> Command:
        """Parse command from markdown file.

        Args:
            path: Path to command markdown file

        Returns:
            Command object
        """
        with open(path) as f:
            post = frontmatter.load(f)

        metadata = post.metadata

        return Command(
            name=metadata.get("command", "unknown"),
            agent=metadata.get("agent", self.agent_name),
            action=metadata.get("action", path.stem),
            tables_write=metadata.get("tables", {}).get("write", []),
            tables_read=metadata.get("tables", {}).get("read", []),
            files_write=metadata.get("files", {}).get("write", []),
            files_read=metadata.get("files", {}).get("read", []),
            required_skills=metadata.get("required_skills", []),
            required_tools=metadata.get("required_tools", []),
            content=post.content,
            source_file=str(path)
        )

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute a command with parameters.

        Args:
            action: Action name (e.g., "create_spec")
            params: Parameters for command execution

        Returns:
            Command execution result

        Raises:
            ValueError: If command not found
            PermissionError: If permission validation fails
        """
        if action not in self.commands:
            raise ValueError(
                f"Command '{action}' not found for {self.agent_name}. "
                f"Available: {list(self.commands.keys())}"
            )

        command = self.commands[action]

        logger.info(f"Executing command: {command.name}")

        # Validate permissions BEFORE execution
        self._validate_permissions(command)

        # Load required skills
        skills = self._load_skills(command.required_skills)

        # Execute command
        result = command.execute(self.db, params, skills)

        logger.info(f"Command {command.name} completed: {result.get('success', False)}")

        return result

    def _validate_permissions(self, command: Command):
        """Validate agent has permissions for command.

        Args:
            command: Command to validate

        Raises:
            PermissionError: If agent lacks required permissions
        """
        # Check write permissions
        for table in command.tables_write:
            if not self.db.can_write(table):
                raise PermissionError(
                    f"Command '{command.name}' requires write access to '{table}' "
                    f"but {self.agent_name} cannot write to it"
                )

        # Check read permissions
        for table in command.tables_read:
            if not self.db.can_read(table):
                raise PermissionError(
                    f"Command '{command.name}' requires read access to '{table}' "
                    f"but {self.agent_name} cannot read from it"
                )

    def _load_skills(self, skill_names: List[str]) -> Dict[str, Any]:
        """Load required skills for command.

        Args:
            skill_names: List of skill names to load

        Returns:
            Dictionary of skill name to skill object
        """
        from coffee_maker.autonomous.skill_loader import load_skill

        skills = {}
        for skill_name in skill_names:
            try:
                skill = load_skill(skill_name)
                skills[skill_name] = skill
                logger.debug(f"Loaded skill: {skill_name}")
            except Exception as e:
                logger.warning(f"Failed to load skill {skill_name}: {e}")

        return skills

    def list_commands(self) -> List[str]:
        """List all available commands for this agent.

        Returns:
            List of command action names
        """
        return list(self.commands.keys())
```

### Testing Requirements

```python
# tests/unit/test_command_loader.py

def test_load_commands():
    """Test that commands are loaded correctly."""
    loader = CommandLoader(AgentType.ARCHITECT)

    # Should have some commands
    assert len(loader.commands) > 0

    # Check specific command loaded
    assert "create_spec" in loader.commands

def test_permission_validation():
    """Test that permission validation works."""
    loader = CommandLoader(AgentType.CODE_DEVELOPER)

    # Should fail if trying to execute architect command
    with pytest.raises((ValueError, PermissionError)):
        loader.execute("create_spec", {"priority_id": "PRIORITY-1"})
```

---

## Component 3: Command

### Purpose

Encapsulate a single command's logic, metadata, and execution.

### Design

```python
# coffee_maker/commands/command.py

from typing import Any, Dict, List, Optional
import logging

from coffee_maker.database.domain_wrapper import DomainWrapper

logger = logging.getLogger(__name__)


class Command:
    """Individual command implementation.

    Encapsulates:
    - Command metadata (name, agent, action)
    - Permission requirements (tables, files)
    - Skill dependencies
    - Execution logic

    Commands are typically loaded from markdown files by CommandLoader.
    """

    def __init__(
        self,
        name: str,
        agent: str,
        action: str,
        tables_write: List[str] = None,
        tables_read: List[str] = None,
        files_write: List[str] = None,
        files_read: List[str] = None,
        required_skills: List[str] = None,
        required_tools: List[str] = None,
        content: str = "",
        source_file: str = ""
    ):
        """Initialize command.

        Args:
            name: Full command name (e.g., "architect.create_spec")
            agent: Agent that owns this command
            action: Action name (e.g., "create_spec")
            tables_write: Tables this command writes to
            tables_read: Tables this command reads from
            files_write: Files this command writes
            files_read: Files this command reads
            required_skills: Skills required for execution
            required_tools: Tools required (git, gh, pytest, etc.)
            content: Markdown content from command file
            source_file: Path to source markdown file
        """
        self.name = name
        self.agent = agent
        self.action = action
        self.tables_write = tables_write or []
        self.tables_read = tables_read or []
        self.files_write = files_write or []
        self.files_read = files_read or []
        self.required_skills = required_skills or []
        self.required_tools = required_tools or []
        self.content = content
        self.source_file = source_file

    def execute(
        self,
        db: DomainWrapper,
        params: Dict[str, Any],
        skills: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the command.

        Args:
            db: Domain wrapper for database access
            params: Command parameters
            skills: Loaded skills dictionary

        Returns:
            Result dictionary with 'success' key and command-specific data
        """
        # This is a base implementation
        # Specific commands will override or be generated from markdown

        logger.info(f"Executing command: {self.name} with params: {params}")

        # Command-specific logic would go here
        # For now, this is a placeholder that will be enhanced
        # when individual commands are implemented

        return {
            "success": True,
            "command": self.name,
            "params": params
        }

    def __repr__(self) -> str:
        return f"Command({self.name}, agent={self.agent}, action={self.action})"
```

---

## Implementation Tasks

### Task Breakdown (CFR-007 Compliant: <30% context each)

#### TASK-101-1: Implement DomainWrapper (6 hours)

**Scope**:
- Create `coffee_maker/database/domain_wrapper.py`
- Implement permission checking (`can_write`, `can_read`)
- Implement audit logging (`_audit_log`)
- Implement read/write methods wrapping RoadmapDatabase
- Implement notification method

**Files**:
- Create: `coffee_maker/database/domain_wrapper.py`
- Create: `coffee_maker/database/__init__.py` (if not exists)

**Tests**:
- Create: `tests/unit/test_domain_wrapper.py`
- Test permission enforcement (write denied)
- Test permission enforcement (write allowed)
- Test read permissions
- Test audit logging
- Test notification sending

**Context Size**: ~12% (single class + tests)

**Success Criteria**:
- ✅ All permission tests pass
- ✅ Audit logs created for all operations
- ✅ Existing RoadmapDatabase methods work unchanged
- ✅ No schema changes required

---

#### TASK-101-2: Implement CommandLoader (6 hours)

**Scope**:
- Create `coffee_maker/commands/command_loader.py`
- Implement markdown parsing with frontmatter
- Implement command loading from directory
- Implement permission validation before execution
- Implement skill loading integration

**Files**:
- Create: `coffee_maker/commands/command_loader.py`
- Create: `coffee_maker/commands/__init__.py`

**Dependencies**:
- `frontmatter` package (Tier 1 approved)
- TASK-101-1 (DomainWrapper)

**Tests**:
- Create: `tests/unit/test_command_loader.py`
- Test command loading from markdown
- Test permission validation
- Test command execution
- Test skill integration

**Context Size**: ~15% (loader + parsing logic + tests)

**Success Criteria**:
- ✅ Commands loaded from markdown files
- ✅ Frontmatter parsed correctly
- ✅ Permission validation works
- ✅ Skills loaded when required

---

#### TASK-101-3: Implement Command Base Class (4 hours)

**Scope**:
- Create `coffee_maker/commands/command.py`
- Implement Command class with metadata
- Implement execute() method template
- Document command structure

**Files**:
- Create: `coffee_maker/commands/command.py`

**Dependencies**:
- TASK-101-1 (DomainWrapper)

**Tests**:
- Create: `tests/unit/test_command.py`
- Test command initialization
- Test metadata access
- Test execute() template

**Context Size**: ~8% (simple base class + tests)

**Success Criteria**:
- ✅ Command class properly structured
- ✅ Metadata accessible
- ✅ Execute method callable

---

#### TASK-101-4: Integration Testing & Documentation (4 hours)

**Scope**:
- Create end-to-end integration tests
- Test complete workflow: Load → Validate → Execute
- Document usage patterns
- Create example command files

**Files**:
- Create: `tests/integration/test_command_system.py`
- Create: `.claude/commands/agents/example/test_command.md`
- Update: `docs/architecture/specs/SPEC-101-foundation-infrastructure.md` (add examples)

**Dependencies**:
- TASK-101-1, TASK-101-2, TASK-101-3

**Tests**:
- Integration test: Load command → Execute → Verify audit
- Integration test: Permission denial flow
- Integration test: Skill integration

**Context Size**: ~10% (integration tests + examples)

**Success Criteria**:
- ✅ End-to-end workflow works
- ✅ All integration tests pass
- ✅ Documentation complete
- ✅ Example commands provided

---

## Total Effort Estimate

| Task | Hours | Complexity | Context % |
|------|-------|------------|-----------|
| TASK-101-1: DomainWrapper | 6 | Medium | 12% |
| TASK-101-2: CommandLoader | 6 | Medium | 15% |
| TASK-101-3: Command Base | 4 | Low | 8% |
| TASK-101-4: Integration | 4 | Low | 10% |
| **TOTAL** | **20** | **Medium** | **<30% each** |

---

## Success Criteria

### Functional

- ✅ DomainWrapper enforces all table permissions
- ✅ CommandLoader loads commands from markdown files
- ✅ Commands execute with full audit trails
- ✅ Skills integrate seamlessly with commands
- ✅ Existing database classes work unchanged

### Technical

- ✅ All unit tests pass (>90% coverage)
- ✅ All integration tests pass
- ✅ No schema changes required
- ✅ Performance overhead <5%
- ✅ Context budget <30% per task

### Documentation

- ✅ All classes documented with docstrings
- ✅ Usage examples provided
- ✅ Integration guide complete
- ✅ Example commands available

---

## Dependencies

### Python Packages

| Package | Version | Purpose | Approval Status |
|---------|---------|---------|-----------------|
| `frontmatter` | Latest | Parse markdown frontmatter | ✅ Tier 1 Approved |
| `pyyaml` | Latest | YAML parsing (frontmatter dependency) | ✅ Tier 1 Approved |

### Existing Infrastructure

| Component | Usage | Changes Required |
|-----------|-------|------------------|
| RoadmapDatabase | Wrapped by DomainWrapper | None |
| AgentRegistry | Used for agent type definitions | None |
| SkillLoader | Integrated with CommandLoader | None |
| NotificationDatabase | Used for inter-agent communication | None |

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_domain_wrapper.py
- test_permission_write_allowed()
- test_permission_write_denied()
- test_permission_read_allowed()
- test_permission_read_denied()
- test_audit_logging()
- test_notification_sending()

# tests/unit/test_command_loader.py
- test_load_commands_from_directory()
- test_parse_frontmatter()
- test_validate_permissions()
- test_load_skills()
- test_execute_command()

# tests/unit/test_command.py
- test_command_initialization()
- test_command_metadata()
- test_command_execute()
```

### Integration Tests

```python
# tests/integration/test_command_system.py
- test_end_to_end_command_execution()
- test_permission_enforcement_workflow()
- test_audit_trail_creation()
- test_skill_integration()
- test_cross_agent_notifications()
```

---

## Migration Path

### Phase 1: Foundation (This Spec)

1. Implement DomainWrapper
2. Implement CommandLoader
3. Implement Command base class
4. Test thoroughly

### Phase 2: Agent Integration

1. Create first command (architect.create_spec)
2. Integrate CommandLoader into ArchitectAgent
3. Validate workflow
4. Expand to other agents

### Phase 3: Parallel Operation

1. Agents use both legacy and command methods
2. Feature flags control which path is used
3. Gradual migration agent by agent

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance overhead from wrappers | Medium | Low | Benchmark each operation, optimize hot paths |
| Breaking existing database access | Low | High | Comprehensive integration tests, parallel operation |
| Skill integration complexity | Medium | Medium | Start with simple skills, add complex ones gradually |
| Context budget violations | Low | Medium | Careful task sizing, validation before implementation |

---

## Related Documents

- [SPEC-100: Unified Agent Commands Architecture (Master)](SPEC-100-unified-agent-commands-architecture.md)
- [docs/UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md](../../UNIFIED_AGENT_COMMANDS_COMPLETE_PLAN.md)
- [CFR-007: Context Budget](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-007)
- [CFR-014: Database Tracing](../../roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md#cfr-014)
- [CFR-015: Centralized Database Storage](../../CFR-015-CENTRALIZED-DATABASE-STORAGE.md)

---

**Specification Status**: Draft - Ready for Implementation
**Estimated Effort**: 20 hours
**Complexity**: Medium
**Context Budget**: All tasks <30% ✅
**Dependencies**: None (foundational)
