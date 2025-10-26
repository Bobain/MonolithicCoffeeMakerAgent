
# Database Schema Organization

## Overview
The database is logically organized into agent-specific schemas, where each agent
has ownership and write access to their domain tables.

## Schema Ownership

### roadmap schema (project_manager)
**Purpose**: Roadmap management and priority tracking
**Write Access**: project_manager ONLY
**Read Access**: All agents

Tables:
- `priority` (was roadmap_priority): Roadmap items and priorities
- `audit` (was roadmap_audit): Audit trail for roadmap changes
- `metadata` (was roadmap_metadata): Roadmap metadata and settings
- `notification` (was roadmap_notification): Notifications for roadmap updates

### specs schema (architect)
**Purpose**: Technical specifications and implementation tasks
**Write Access**: architect ONLY
**Read Access**: All agents

Tables:
- `specification` (was specs_specification): Technical specifications
- `task` (was specs_task): Implementation tasks from specs
- `task_dependency` (was specs_task_dependency): Task dependencies

### orchestrator schema (orchestrator)
**Purpose**: Multi-agent orchestration and task management
**Write Access**: orchestrator ONLY
**Read Access**: All agents

Tables:
- `task` (was orchestrator_task): Orchestration tasks
- `state` (was orchestrator_state): Orchestrator state tracking
- `bug` (was orchestrator_bug): Bug tracking
- `agent_lifecycle` (was agent_lifecycle): Agent lifecycle events
- `agent_message` (was agent_message): Inter-agent messages

### review schema (code_reviewer)
**Purpose**: Code review tracking and commit analysis
**Write Access**: code_reviewer ONLY
**Read Access**: All agents

Tables:
- `code_review` (was review_code_review): Code review records
- `commit` (was review_commit): Commit tracking

### system schema (shared)
**Purpose**: System-wide shared tables
**Write Access**: All agents (with restrictions)
**Read Access**: All agents

Tables:
- `notifications`: General notification system
- `notification_user`: User notification preferences
- `notification_state`: Notification system state
- `metrics_subtask`: Performance metrics
- `audit`: System-wide audit log
- `schema_metadata`: Database schema metadata

## Access Control Rules

1. **Write Access**: Each agent can only write to tables in their schema
2. **Read Access**: All agents can read from any schema
3. **Notifications**: All agents can create notifications for their changes
4. **Audit Trail**: All changes are logged in respective audit tables

## Migration Notes

- SQLite doesn't support true schemas, so we use prefixing: `schema_table`
- But with cleaner names: `roadmap_priority` → `roadmap.priority` (conceptually)
- Foreign keys and references updated to match new naming
- Views recreated with new table references
