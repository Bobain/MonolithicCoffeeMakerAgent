# Agent Command Extraction & Database Domain Isolation Architecture

## Executive Summary

This document outlines the comprehensive architecture for extracting all agent responsibilities into discrete commands with clear data domain boundaries and enforced database access permissions. Each agent will have specific commands mapped to their responsibilities, with write access limited to their domain tables and controlled read access to others.

---

## Phase 1: Agent Responsibilities Matrix

### ARCHITECT Agent

**Core Responsibilities:**
- Technical specification creation and management
- Architectural Decision Records (ADRs)
- Dependency management and approval
- Implementation task breakdown
- Worktree branch merging
- Code quality guidelines
- Architecture compliance enforcement

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Create technical specs | specs_* tables | WRITE |
| Manage ADRs | arch_adrs | WRITE |
| Approve dependencies | arch_dependencies | WRITE |
| Review implementations | dev_implementations | READ |
| Update guidelines | arch_guidelines | WRITE |
| Track compliance | arch_compliance | WRITE |

### CODE_DEVELOPER Agent

**Core Responsibilities:**
- Priority implementation from ROADMAP
- Test-driven development
- Code commit and PR creation
- DoD verification before submission
- Bug fixes with regression tests
- Implementation task execution

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Track implementations | dev_implementations | WRITE |
| Manage worktrees | dev_worktrees | WRITE |
| Record commits | dev_commits | WRITE |
| Store test results | dev_test_results | WRITE |
| Read specs | specs_* tables | READ |
| Update task status | dev_task_status | WRITE |

### PROJECT_MANAGER Agent

**Core Responsibilities:**
- ROADMAP management and updates
- Project health monitoring
- GitHub PR/Issue tracking
- Strategic planning and recommendations
- DoD verification (post-completion)
- Notification dispatch to agents
- Bug tracking oversight

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Manage roadmap | pm_roadmap | WRITE |
| Track priorities | pm_priorities | WRITE |
| Monitor GitHub | pm_github_status | WRITE |
| Send notifications | pm_notifications | WRITE |
| Verify DoD | pm_dod_verification | WRITE |
| Track project health | pm_health_metrics | WRITE |

### CODE_REVIEWER Agent

**Core Responsibilities:**
- Automated code review of implementations
- Quality score calculation
- Style guide compliance checking
- Security vulnerability scanning
- Test coverage verification
- Architect notification for issues

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Store review reports | review_reports | WRITE |
| Track quality scores | review_scores | WRITE |
| Log compliance issues | review_compliance | WRITE |
| Read commits | dev_commits | READ |
| Read specs | specs_* tables | READ |
| Create findings | review_findings | WRITE |

### ORCHESTRATOR Agent

**Core Responsibilities:**
- Agent lifecycle management
- Health monitoring and auto-restart
- Task routing and coordination
- Inter-agent message queue management
- Resource usage tracking
- Deadlock detection

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Track agent status | orch_agent_status | WRITE |
| Manage message queue | orch_messages | WRITE |
| Monitor health | orch_health_metrics | WRITE |
| Track restarts | orch_restart_history | WRITE |
| Coordinate tasks | orch_task_queue | WRITE |
| All agent tables | *_* tables | READ |

### ASSISTANT Agent

**Core Responsibilities:**
- Documentation expertise
- Demo creation with Puppeteer
- Bug detection and reporting
- Intelligent delegation to specialized agents
- Quick question answering
- Feature testing and validation

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Store demos | assist_demos | WRITE |
| Report bugs | assist_bug_reports | WRITE |
| Track delegations | assist_delegations | WRITE |
| Read documentation | All docs | READ |
| Read code | All code | READ |

### USER_LISTENER Agent

**Core Responsibilities:**
- Primary user interface
- Intent classification
- Agent delegation routing
- Conversation management
- Sound notifications (only agent allowed)
- Multi-turn interaction handling

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Track conversations | user_conversations | WRITE |
| Log intents | user_intents | WRITE |
| Store session data | user_sessions | WRITE |
| Route requests | user_routing | WRITE |
| Play notifications | user_notifications | WRITE |

### UX_DESIGN_EXPERT Agent

**Core Responsibilities:**
- UI/UX design specifications
- Tailwind CSS implementation guidance
- Design system creation
- Data visualization with Highcharts
- Component library design
- Accessibility compliance

**Data Operations:**
| Action | Data Type | Access Level |
|--------|-----------|--------------|
| Store design specs | ux_design_specs | WRITE |
| Manage components | ux_components | WRITE |
| Track design tokens | ux_design_tokens | WRITE |
| Store visualizations | ux_visualizations | WRITE |
| Read implementations | dev_implementations | READ |

---

## Phase 2: Database Domain Architecture

### Table Prefix Convention

```sql
-- Architect domain
arch_specs              -- Technical specifications
arch_adrs               -- Architectural Decision Records
arch_dependencies       -- Dependency approvals
arch_guidelines         -- Implementation guidelines
arch_compliance         -- Architecture compliance tracking

-- Developer domain
dev_implementations     -- Implementation tracking
dev_worktrees          -- Git worktree management
dev_commits            -- Commit history
dev_test_results       -- Test execution results
dev_task_status        -- Task progress tracking

-- Project Manager domain
pm_roadmap             -- Roadmap items
pm_priorities          -- Priority tracking
pm_github_status       -- GitHub PR/Issue status
pm_notifications       -- Agent notifications
pm_dod_verification    -- Definition of Done checks
pm_health_metrics      -- Project health metrics

-- Code Reviewer domain
review_reports         -- Code review reports
review_scores          -- Quality scores
review_compliance      -- Style guide compliance
review_findings        -- Specific issues found

-- Orchestrator domain
orch_agent_status      -- Agent process status
orch_messages          -- Inter-agent messages
orch_health_metrics    -- System health metrics
orch_restart_history   -- Agent restart tracking
orch_task_queue        -- Task coordination

-- Assistant domain
assist_demos           -- Created demonstrations
assist_bug_reports     -- Bug findings
assist_delegations     -- Delegation tracking

-- User Listener domain
user_conversations     -- Conversation history
user_intents           -- Intent classifications
user_sessions          -- User session data
user_routing           -- Request routing

-- UX Design Expert domain
ux_design_specs        -- Design specifications
ux_components          -- Component library
ux_design_tokens       -- Design system tokens
ux_visualizations      -- Chart configurations

-- Shared read-only domain
shared_config          -- System configuration
shared_metrics         -- Aggregated metrics
shared_audit           -- Audit trail
```

---

## Phase 3: Command Structure Templates

### Command Directory Organization

```
.claude/commands/agents/
├── architect/
│   ├── create_spec.md
│   ├── approve_dependency.md
│   ├── generate_adr.md
│   ├── merge_worktree.md
│   └── update_guidelines.md
├── code_developer/
│   ├── implement_priority.md
│   ├── create_worktree.md
│   ├── run_tests.md
│   ├── commit_changes.md
│   └── fix_bug.md
├── project_manager/
│   ├── update_roadmap.md
│   ├── monitor_github.md
│   ├── verify_dod.md
│   ├── send_notification.md
│   └── analyze_health.md
├── code_reviewer/
│   ├── review_implementation.md
│   ├── check_compliance.md
│   ├── scan_security.md
│   └── generate_report.md
├── orchestrator/
│   ├── launch_agents.md
│   ├── monitor_health.md
│   ├── restart_agent.md
│   └── route_task.md
├── assistant/
│   ├── create_demo.md
│   ├── report_bug.md
│   ├── answer_question.md
│   └── delegate_task.md
├── user_listener/
│   ├── classify_intent.md
│   ├── route_request.md
│   └── manage_conversation.md
└── ux_design_expert/
    ├── design_interface.md
    ├── create_component.md
    ├── define_tokens.md
    └── configure_charts.md
```

### Command Template Structure

```markdown
---
command: agent.action
agent: architect
action: create_spec
data_domain: arch_specs
write_tables: [arch_specs]
read_tables: [pm_roadmap, dev_implementations]
required_skills: [technical_specification_handling, database_schema_guide]
---

# Command: architect.create_spec

## Purpose
Create a technical specification for a priority from the roadmap.

## Input Parameters
- priority_id: string (required) - Roadmap priority ID
- priority_name: string (required) - Human-readable priority name
- requirements: object (required) - Detailed requirements

## Database Operations

### READ Operations
```sql
-- Read priority details
SELECT * FROM pm_roadmap WHERE id = ?;

-- Check existing implementations
SELECT * FROM dev_implementations WHERE priority_id = ?;
```

### WRITE Operations
```sql
-- Create new spec
INSERT INTO arch_specs (
    id, priority_id, title, content,
    created_at, created_by, status
) VALUES (?, ?, ?, ?, ?, 'architect', 'draft');
```

## Required Skills
1. **technical_specification_handling** - For spec creation
2. **database_schema_guide** - For understanding data structures

## Execution Steps
1. Validate agent permissions (must be architect)
2. Load required skills
3. Read priority from pm_roadmap
4. Analyze requirements and existing code
5. Generate technical specification
6. Store in arch_specs table
7. Link to priority in roadmap
8. Notify project_manager of completion

## Error Handling
- PermissionError: If not architect agent
- NotFoundError: If priority doesn't exist
- DuplicateError: If spec already exists for priority
- ValidationError: If requirements incomplete

## Success Criteria
- Spec created and stored in database
- Spec linked to priority
- Notification sent to project_manager
- Audit trail created

## Example Usage
```python
from coffee_maker.database.domain_access import DomainDatabase

db = DomainDatabase(agent_type=AgentType.ARCHITECT)

# Create spec
spec_id = db.write('arch_specs', {
    'id': 'SPEC-100',
    'priority_id': 'PRIORITY-25',
    'title': 'Authentication System',
    'content': spec_content,
    'created_at': datetime.now(),
    'status': 'draft'
})

# Notify PM
db.cross_domain_notify('project_manager', {
    'type': 'spec_created',
    'spec_id': spec_id,
    'priority_id': 'PRIORITY-25'
})
```
```

---

## Phase 4: Database Access Layer Implementation

### DomainDatabase Class

```python
# coffee_maker/database/domain_access.py

from enum import Enum
from typing import Dict, List, Any, Optional
import sqlite3
from dataclasses import dataclass
from datetime import datetime

class AgentType(Enum):
    ARCHITECT = "architect"
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    CODE_REVIEWER = "code_reviewer"
    ORCHESTRATOR = "orchestrator"
    ASSISTANT = "assistant"
    USER_LISTENER = "user_listener"
    UX_DESIGN_EXPERT = "ux_design_expert"

# Domain prefix mapping
AGENT_PREFIXES = {
    AgentType.ARCHITECT: "arch_",
    AgentType.CODE_DEVELOPER: "dev_",
    AgentType.PROJECT_MANAGER: "pm_",
    AgentType.CODE_REVIEWER: "review_",
    AgentType.ORCHESTRATOR: "orch_",
    AgentType.ASSISTANT: "assist_",
    AgentType.USER_LISTENER: "user_",
    AgentType.UX_DESIGN_EXPERT: "ux_",
}

# Read permissions matrix
READ_PERMISSIONS = {
    AgentType.ARCHITECT: ["arch_", "dev_", "pm_", "review_", "shared_"],
    AgentType.CODE_DEVELOPER: ["dev_", "arch_", "pm_", "shared_"],
    AgentType.PROJECT_MANAGER: ["pm_", "arch_", "dev_", "review_", "shared_"],
    AgentType.CODE_REVIEWER: ["review_", "dev_", "arch_", "shared_"],
    AgentType.ORCHESTRATOR: ["*"],  # Can read all
    AgentType.ASSISTANT: ["assist_", "shared_", "*"],  # Can read all for demos
    AgentType.USER_LISTENER: ["user_", "shared_"],
    AgentType.UX_DESIGN_EXPERT: ["ux_", "dev_", "shared_"],
}

class DomainDatabase:
    """Database access with domain isolation."""

    def __init__(self, agent_type: AgentType, db_path: str = "data/unified.db"):
        self.agent_type = agent_type
        self.write_prefix = AGENT_PREFIXES[agent_type]
        self.read_prefixes = READ_PERMISSIONS[agent_type]
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def can_write(self, table: str) -> bool:
        """Check if agent can write to table."""
        return table.startswith(self.write_prefix)

    def can_read(self, table: str) -> bool:
        """Check if agent can read from table."""
        if "*" in self.read_prefixes:
            return True
        return any(table.startswith(p) for p in self.read_prefixes)

    def write(self, table: str, data: Dict[str, Any]) -> int:
        """Write data to table with permission check."""
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_type.value} cannot write to {table}. "
                f"Only tables with prefix '{self.write_prefix}' allowed."
            )

        # Add audit fields
        data['created_by'] = self.agent_type.value
        data['created_at'] = datetime.now().isoformat()

        # Build INSERT query
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor = self.conn.cursor()
        cursor.execute(query, list(data.values()))
        self.conn.commit()

        # Log to audit trail
        self._audit_log('WRITE', table, cursor.lastrowid)

        return cursor.lastrowid

    def read(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Read data from table with permission check."""
        if not self.can_read(table):
            raise PermissionError(
                f"{self.agent_type.value} cannot read from {table}. "
                f"Allowed prefixes: {self.read_prefixes}"
            )

        # Build SELECT query
        query = f"SELECT * FROM {table}"
        params = []

        if conditions:
            where_clauses = [f"{k} = ?" for k in conditions.keys()]
            query += f" WHERE {' AND '.join(where_clauses)}"
            params = list(conditions.values())

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        # Log to audit trail
        self._audit_log('READ', table, None)

        # Convert to dict
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update(self, table: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        """Update data in table with permission check."""
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_type.value} cannot update {table}. "
                f"Only tables with prefix '{self.write_prefix}' allowed."
            )

        # Add audit fields
        data['updated_by'] = self.agent_type.value
        data['updated_at'] = datetime.now().isoformat()

        # Build UPDATE query
        set_clauses = [f"{k} = ?" for k in data.keys()]
        where_clauses = [f"{k} = ?" for k in conditions.keys()]

        query = f"""
            UPDATE {table}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
        """

        params = list(data.values()) + list(conditions.values())

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()

        # Log to audit trail
        self._audit_log('UPDATE', table, cursor.rowcount)

        return cursor.rowcount

    def delete(self, table: str, conditions: Dict[str, Any]) -> int:
        """Delete data from table with permission check."""
        if not self.can_write(table):
            raise PermissionError(
                f"{self.agent_type.value} cannot delete from {table}. "
                f"Only tables with prefix '{self.write_prefix}' allowed."
            )

        # Build DELETE query
        where_clauses = [f"{k} = ?" for k in conditions.keys()]
        query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        params = list(conditions.values())

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()

        # Log to audit trail
        self._audit_log('DELETE', table, cursor.rowcount)

        return cursor.rowcount

    def cross_domain_notify(self, target_agent: str, message: Dict[str, Any]):
        """Send notification to another agent via orchestrator."""
        # Orchestrator has special permission to write to any notification table
        notification = {
            'from_agent': self.agent_type.value,
            'to_agent': target_agent,
            'message_type': message.get('type', 'notification'),
            'payload': json.dumps(message),
            'status': 'pending'
        }

        # Write to orchestrator message queue (special case)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO orch_messages
            (from_agent, to_agent, message_type, payload, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            notification['from_agent'],
            notification['to_agent'],
            notification['message_type'],
            notification['payload'],
            notification['status'],
            datetime.now().isoformat()
        ))
        self.conn.commit()

    def _audit_log(self, operation: str, table: str, affected_rows: Optional[int]):
        """Log all database operations for audit trail."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO shared_audit
            (agent, operation, table_name, affected_rows, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.agent_type.value,
            operation,
            table,
            affected_rows,
            datetime.now().isoformat()
        ))
        self.conn.commit()
```

---

## Phase 5: Migration Strategy

### Step 1: Create New Database Schema

```sql
-- Create all domain tables with proper prefixes
-- Run migration script to create unified database

CREATE TABLE arch_specs (
    id TEXT PRIMARY KEY,
    priority_id TEXT,
    title TEXT NOT NULL,
    content TEXT,
    status TEXT,
    created_at TIMESTAMP,
    created_by TEXT,
    updated_at TIMESTAMP,
    updated_by TEXT
);

CREATE TABLE dev_implementations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id TEXT,
    file_path TEXT,
    content TEXT,
    status TEXT,
    created_at TIMESTAMP,
    created_by TEXT
);

-- Continue for all domain tables...
```

### Step 2: Update Agent Classes

```python
# Example: Update architect agent
class ArchitectAgent:
    def __init__(self):
        self.db = DomainDatabase(AgentType.ARCHITECT)

    def create_spec(self, priority_id: str, requirements: dict):
        # Load command from .claude/commands/agents/architect/create_spec.md
        command = load_command("architect.create_spec")

        # Validate permissions
        if not self.db.can_write("arch_specs"):
            raise PermissionError("Cannot write to specs table")

        # Execute command logic
        spec = self._generate_spec(requirements)

        # Store in database
        spec_id = self.db.write("arch_specs", {
            "id": f"SPEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "priority_id": priority_id,
            "title": spec["title"],
            "content": spec["content"],
            "status": "draft"
        })

        # Notify project manager
        self.db.cross_domain_notify("project_manager", {
            "type": "spec_created",
            "spec_id": spec_id,
            "priority_id": priority_id
        })

        return spec_id
```

### Step 3: Migrate Existing Data

```python
# Migration script to move data to new schema
def migrate_to_domain_schema():
    """Migrate existing databases to unified domain schema."""

    # Connect to old databases
    old_roadmap = sqlite3.connect("data/roadmap.db")
    old_code_dev = sqlite3.connect("data/code_developer.db")
    old_notifs = sqlite3.connect("data/notifications.db")

    # Connect to new unified database
    new_db = sqlite3.connect("data/unified.db")

    # Migrate roadmap → pm_roadmap
    migrate_table(old_roadmap, new_db, "roadmap", "pm_roadmap")

    # Migrate implementations → dev_implementations
    migrate_table(old_code_dev, new_db, "implementations", "dev_implementations")

    # Continue for all tables...
```

### Step 4: Update Skills

```python
# Update skills to use DomainDatabase
class TechnicalSpecSkill:
    def __init__(self, agent_name: str):
        agent_type = AgentType[agent_name.upper()]
        self.db = DomainDatabase(agent_type)

    def get_spec(self, spec_id: str):
        # Use domain database for access
        specs = self.db.read("arch_specs", {"id": spec_id})
        if not specs:
            raise NotFoundError(f"Spec {spec_id} not found")
        return specs[0]
```

### Step 5: Testing & Validation

```python
# Test permission enforcement
def test_domain_isolation():
    # Developer should NOT write to architect tables
    dev_db = DomainDatabase(AgentType.CODE_DEVELOPER)

    with pytest.raises(PermissionError):
        dev_db.write("arch_specs", {"title": "Unauthorized"})

    # Developer CAN write to dev tables
    result = dev_db.write("dev_implementations", {
        "file_path": "test.py",
        "content": "test"
    })
    assert result is not None

    # Orchestrator CAN read all tables
    orch_db = DomainDatabase(AgentType.ORCHESTRATOR)
    specs = orch_db.read("arch_specs")
    impls = orch_db.read("dev_implementations")
    assert specs is not None
    assert impls is not None
```

---

## Phase 6: Benefits & Outcomes

### Security & Isolation
- **No cross-contamination**: Each agent can only write to its own domain
- **Clear audit trail**: Every operation logged with agent identity
- **Permission enforcement**: Database layer prevents unauthorized access
- **Data integrity**: No agent can corrupt another's data

### Maintainability
- **Single source of truth**: All agent capabilities in command files
- **Easy updates**: Modify command without changing code
- **Clear documentation**: Each command self-documents its purpose
- **Testable**: Commands can be tested in isolation

### Observability
- **Full traceability**: Every database operation traced to command and agent
- **Performance metrics**: Track slow operations per domain
- **Audit compliance**: Complete audit trail for all changes
- **Debugging**: Easy to trace data flow through system

### Scalability
- **Horizontal scaling**: Agents can run on different machines
- **Domain sharding**: Each domain can be in separate database
- **Cache optimization**: Domain-specific caching strategies
- **Query optimization**: Indexes per domain usage patterns

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Create DomainDatabase class
- [ ] Set up unified database schema
- [ ] Implement permission matrix
- [ ] Create audit logging

### Week 2: Command Extraction
- [ ] Extract architect commands
- [ ] Extract code_developer commands
- [ ] Extract project_manager commands
- [ ] Create command templates

### Week 3: Agent Updates
- [ ] Update architect to use commands
- [ ] Update code_developer to use commands
- [ ] Update project_manager to use commands
- [ ] Update remaining agents

### Week 4: Migration
- [ ] Create migration scripts
- [ ] Migrate existing data
- [ ] Update all skills
- [ ] Test permission enforcement

### Week 5: Testing & Documentation
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Deployment guide

---

## Success Criteria

1. **All agents using domain commands** - No inline prompts or direct database access
2. **Permission enforcement working** - No unauthorized writes possible
3. **Audit trail complete** - Every operation logged
4. **Performance maintained** - No degradation from current system
5. **Migration successful** - All existing data preserved
6. **Tests passing** - 100% of domain isolation tests pass

---

## Next Steps

1. Review and approve this architecture
2. Create DomainDatabase implementation
3. Begin command extraction for architect agent
4. Set up test environment with new schema
5. Create migration plan for production

---

**Document Version**: 1.0
**Created**: 2025-10-26
**Status**: DRAFT - Awaiting Review
