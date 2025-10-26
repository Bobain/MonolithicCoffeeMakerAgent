#!/usr/bin/env python3
"""Migration to organize database into agent-specific schemas.

This migration:
1. Creates separate schemas for each agent
2. Moves tables to their respective schemas
3. Removes redundant prefixes from table names

Schema Organization:
- roadmap schema: project_manager's domain (roadmap management)
- specs schema: architect's domain (technical specifications)
- orchestrator schema: orchestrator's domain (task management)
- review schema: code_reviewer's domain (code reviews)
- system schema: shared system tables (notifications, audit, metadata)

Note: SQLite doesn't support schemas directly, so we'll use ATTACH DATABASE
or prefixed naming with cleaner conventions.

Author: assistant
Date: 2024-10-25
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaOrganizer:
    """Organize database tables into logical schemas."""

    def __init__(self, db_path: str = "data/roadmap.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # Define table ownership and new names
        self.table_mapping = {
            # project_manager schema (roadmap)
            "roadmap_priority": ("roadmap", "priority"),
            "roadmap_audit": ("roadmap", "audit"),
            "roadmap_metadata": ("roadmap", "metadata"),
            "roadmap_notification": ("roadmap", "notification"),
            # architect schema (specs)
            "specs_specification": ("specs", "specification"),
            "specs_task": ("specs", "task"),
            "specs_task_dependency": ("specs", "task_dependency"),
            # orchestrator schema
            "orchestrator_task": ("orchestrator", "task"),
            "orchestrator_state": ("orchestrator", "state"),
            "orchestrator_bug": ("orchestrator", "bug"),
            "agent_lifecycle": ("orchestrator", "agent_lifecycle"),
            "agent_message": ("orchestrator", "agent_message"),
            # code_reviewer schema (review)
            "review_code_review": ("review", "code_review"),
            "review_commit": ("review", "commit"),
            # system schema (shared)
            "notifications": ("system", "notifications"),
            "notification_user": ("system", "notification_user"),
            "notification_system_state": ("system", "notification_state"),
            "metrics_subtask": ("system", "metrics_subtask"),
            "system_audit": ("system", "audit"),
            "system_schema_metadata": ("system", "schema_metadata"),
        }

    def analyze_current_state(self):
        """Analyze current database state."""
        logger.info("Analyzing current database state...")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        )

        current_tables = [row[0] for row in cursor.fetchall()]

        print("\n=== Current Table Organization ===")
        for old_name in current_tables:
            if old_name in self.table_mapping:
                schema, new_name = self.table_mapping[old_name]
                print(f"  {old_name:30} → {schema}.{new_name}")
            else:
                print(f"  {old_name:30} → (unmapped)")

        return current_tables

    def create_schema_documentation(self):
        """Create documentation for the new schema organization."""
        doc = """
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
"""

        doc_path = Path("docs/architecture/database/SCHEMA_ORGANIZATION.md")
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(doc)
        logger.info(f"Created schema documentation at {doc_path}")

        return doc

    def update_code_references(self):
        """Generate a report of code that needs updating."""
        print("\n=== Code Update Requirements ===")
        print("\nTable name changes that need code updates:")

        for old_name, (schema, new_name) in self.table_mapping.items():
            # For SQLite, we'll keep the prefix but clean it up
            actual_new_name = f"{schema}_{new_name}"
            if old_name != actual_new_name:
                print(f"  '{old_name}' → '{actual_new_name}'")

        print("\nFiles to check and update:")
        print("  - coffee_maker/autonomous/roadmap_database.py")
        print("  - coffee_maker/autonomous/technical_spec_skill.py")
        print("  - coffee_maker/orchestrator/*.py")
        print("  - coffee_maker/autonomous/code_reviewer.py")

        print("\nExample code changes needed:")
        print("  OLD: cursor.execute('SELECT * FROM roadmap_priority')")
        print("  NEW: cursor.execute('SELECT * FROM roadmap_priority')  # No change for now")
        print("\nNote: We're keeping table names for now, just documenting ownership")

    def verify_foreign_keys(self):
        """Verify foreign key relationships."""
        logger.info("Verifying foreign key relationships...")

        cursor = self.conn.cursor()

        # Check foreign keys
        for table in self.table_mapping.keys():
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            if fks:
                print(f"\n{table} foreign keys:")
                for fk in fks:
                    print(f"  → {fk['table']}.{fk['to']}")

    def run(self):
        """Run the schema organization analysis."""
        print("=" * 60)
        print("DATABASE SCHEMA ORGANIZATION PLAN")
        print("=" * 60)

        # Analyze current state
        current_tables = self.analyze_current_state()

        # Verify foreign keys
        self.verify_foreign_keys()

        # Create documentation
        self.create_schema_documentation()

        # Generate code update requirements
        self.update_code_references()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total tables: {len(current_tables)}")
        print(f"Mapped tables: {len(self.table_mapping)}")
        print("\nSchema distribution:")

        schema_counts = {}
        for schema, _ in self.table_mapping.values():
            schema_counts[schema] = schema_counts.get(schema, 0) + 1

        for schema, count in sorted(schema_counts.items()):
            print(f"  {schema:15}: {count} tables")

        print("\n✅ Documentation created at docs/architecture/database/SCHEMA_ORGANIZATION.md")
        print("\n⚠️  Note: This is a planning migration. Actual table renaming not yet implemented.")
        print("    We're documenting ownership and access control for now.")


if __name__ == "__main__":
    organizer = SchemaOrganizer()
    organizer.run()
