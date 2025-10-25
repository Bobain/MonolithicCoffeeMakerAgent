"""Migration: Add schema_metadata table for database documentation.

This migration creates a table to store descriptions and metadata about
database tables, columns, and relationships.

Author: architect
Date: 2025-10-25
Related: Database Schema Guide skill, HIERARCHICAL_SPEC_IMPLEMENTATION_STATUS.md
"""

import sqlite3
from pathlib import Path


def migrate():
    """Add schema_metadata table to store database documentation."""

    db_path = Path("data/roadmap.db")

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create schema_metadata table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,  -- 'table', 'column', 'relationship'
                entity_name TEXT NOT NULL,  -- Table name or column name
                parent_name TEXT,           -- For columns: table name; for relationships: from_table

                -- Documentation
                description TEXT NOT NULL,
                purpose TEXT,               -- What this entity is for
                usage_notes TEXT,           -- How to use it correctly

                -- Metadata
                content_type TEXT,          -- For columns: 'json', 'markdown', 'text', etc.
                use_files BOOLEAN DEFAULT 0, -- Should this entity use filesystem?

                -- Relationships
                related_tables TEXT,        -- JSON array of related table names
                foreign_keys TEXT,          -- JSON array of FK definitions

                -- Versioning
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                -- Constraints
                UNIQUE(entity_type, entity_name, parent_name)
            )
        """
        )

        # Create indexes for fast lookups
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_schema_metadata_entity
            ON schema_metadata(entity_type, entity_name)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_schema_metadata_parent
            ON schema_metadata(entity_type, parent_name)
        """
        )

        # Insert metadata for existing tables
        tables_metadata = [
            {
                "entity_type": "table",
                "entity_name": "technical_specs",
                "description": "Store complete technical specification content in database (NO FILES!)",
                "purpose": "Store hierarchical or monolithic specs entirely in database content column",
                "usage_notes": "NEVER create files for specs. Use TechnicalSpecSkill to create/read specs.",
                "use_files": 0,
                "related_tables": '["implementation_tasks", "roadmap_items"]',
            },
            {
                "entity_type": "table",
                "entity_name": "implementation_tasks",
                "description": "Break specs into atomic, scoped tasks for parallel execution",
                "purpose": "Enable parallel development by splitting specs into independent implementation tasks",
                "usage_notes": "Each task is scoped to specific files and spec sections. Use ImplementationTaskManager.",
                "use_files": 0,
                "related_tables": '["technical_specs"]',
                "foreign_keys": '[{"column": "spec_id", "references": "technical_specs.id"}]',
            },
            {
                "entity_type": "table",
                "entity_name": "roadmap_items",
                "description": "Master list of priorities from ROADMAP.md",
                "purpose": "Track strategic priorities and their implementation status",
                "usage_notes": "Synced from docs/roadmap/ROADMAP.md. Use RoadmapDatabase for access.",
                "use_files": 0,
                "related_tables": '["technical_specs", "implementation_tasks"]',
            },
        ]

        # Insert column metadata for technical_specs
        columns_metadata = [
            {
                "entity_type": "column",
                "entity_name": "content",
                "parent_name": "technical_specs",
                "description": "Full spec content: markdown (monolithic) or JSON (hierarchical)",
                "purpose": "Store complete spec content in database (NOT on filesystem)",
                "content_type": "markdown or JSON",
                "usage_notes": "For hierarchical: JSON with {overview, architecture, phases}. For monolithic: plain markdown.",
            },
            {
                "entity_type": "column",
                "entity_name": "spec_type",
                "parent_name": "technical_specs",
                "description": "Type of spec: 'monolithic' or 'hierarchical'",
                "purpose": "Determines how to parse content column",
                "content_type": "text",
                "usage_notes": "hierarchical = JSON with phases, monolithic = plain markdown",
            },
            {
                "entity_type": "column",
                "entity_name": "total_phases",
                "parent_name": "technical_specs",
                "description": "Number of phases in hierarchical spec (NULL for monolithic)",
                "purpose": "Track progressive disclosure phases",
                "content_type": "integer",
            },
            {
                "entity_type": "column",
                "entity_name": "phase_files",
                "parent_name": "technical_specs",
                "description": "JSON array of phase names (metadata only, NOT filesystem paths)",
                "purpose": "Track phase structure for hierarchical specs",
                "content_type": "json",
                "usage_notes": "Array of phase names like ['database-layer', 'api-layer']. NOT file paths!",
            },
            {
                "entity_type": "column",
                "entity_name": "scope_description",
                "parent_name": "implementation_tasks",
                "description": "Plain text description of what this task implements",
                "purpose": "Describes task scope without duplicating spec content",
                "content_type": "text",
                "usage_notes": "Brief description, not full spec. Full spec in technical_specs.content.",
            },
        ]

        # Insert all metadata
        for metadata in tables_metadata + columns_metadata:
            cursor.execute(
                """
                INSERT OR REPLACE INTO schema_metadata (
                    entity_type, entity_name, parent_name, description, purpose,
                    usage_notes, content_type, use_files, related_tables, foreign_keys
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metadata["entity_type"],
                    metadata["entity_name"],
                    metadata.get("parent_name"),
                    metadata["description"],
                    metadata.get("purpose"),
                    metadata.get("usage_notes"),
                    metadata.get("content_type"),
                    metadata.get("use_files", 0),
                    metadata.get("related_tables"),
                    metadata.get("foreign_keys"),
                ),
            )

        conn.commit()
        print("✅ Migration completed successfully")
        print(f"   Created schema_metadata table")
        print(f"   Inserted metadata for {len(tables_metadata)} tables")
        print(f"   Inserted metadata for {len(columns_metadata)} columns")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM schema_metadata")
        count = cursor.fetchone()[0]
        print(f"   Total metadata records: {count}")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        import traceback

        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
