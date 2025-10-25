"""Database Schema Awareness Skill (Enhanced with Introspection).

This skill provides instant access to database schema information using:
1. Database introspection (PRAGMA statements for SQLite)
2. system_schema_metadata table (descriptions, usage patterns)
3. Static documentation (examples, anti-patterns)

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

    skill = load_skill(SkillNames.DATABASE_SCHEMA_GUIDE)

    # Get table purpose and metadata
    info = skill.execute(action="get_table_info", table="technical_specs")

    # Check if should use files
    should_use_files = skill.execute(action="should_use_files", table="technical_specs")
    # Returns: {"result": False, "reason": "Store content in database, not files"}

    # List all tables (introspection)
    tables = skill.execute(action="list_tables")

    # Get column information (introspection + metadata)
    columns = skill.execute(action="get_columns", table="technical_specs")

    # Get relationships (FKs via introspection)
    relationships = skill.execute(action="get_relationships", table="technical_specs")

Author: architect
Date: 2025-10-25
Related: Database Schema Guide, HIERARCHICAL_SPEC_IMPLEMENTATION_STATUS.md
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional


class DatabaseSchemaSkill:
    """Provides database schema information via introspection and metadata."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the skill.

        Args:
            db_path: Path to database (default: data/roadmap.db)
        """
        self.guide_path = Path(__file__).parent / "DATABASE_SCHEMA_GUIDE.md"
        self.db_path = db_path or "data/roadmap.db"

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _introspect_tables(self) -> List[str]:
        """Get all table names via introspection."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        )

        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        return tables

    def _introspect_columns(self, table: str) -> List[Dict[str, Any]]:
        """Get column information for a table via PRAGMA."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table})")

        columns = []
        for row in cursor.fetchall():
            columns.append(
                {
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "default_value": row[4],
                    "is_primary_key": bool(row[5]),
                }
            )

        conn.close()

        return columns

    def _introspect_foreign_keys(self, table: str) -> List[Dict[str, str]]:
        """Get foreign key relationships via PRAGMA."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA foreign_key_list({table})")

        fks = []
        for row in cursor.fetchall():
            fks.append({"column": row[3], "references_table": row[2], "references_column": row[4]})

        conn.close()

        return fks

    def _get_metadata(
        self, entity_type: str, entity_name: str, parent_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get metadata from schema_metadata table."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if parent_name:
                cursor.execute(
                    """
                    SELECT description, purpose, usage_notes, content_type, use_files,
                           related_tables, foreign_keys
                    FROM system_schema_metadata
                    WHERE entity_type = ? AND entity_name = ? AND parent_name = ?
                """,
                    (entity_type, entity_name, parent_name),
                )
            else:
                cursor.execute(
                    """
                    SELECT description, purpose, usage_notes, content_type, use_files,
                           related_tables, foreign_keys
                    FROM system_schema_metadata
                    WHERE entity_type = ? AND entity_name = ? AND parent_name IS NULL
                """,
                    (entity_type, entity_name),
                )

            row = cursor.fetchone()

            if row:
                return {
                    "description": row[0],
                    "purpose": row[1],
                    "usage_notes": row[2],
                    "content_type": row[3],
                    "use_files": bool(row[4]),
                    "related_tables": json.loads(row[5]) if row[5] else [],
                    "foreign_keys": json.loads(row[6]) if row[6] else [],
                }

            return None

        except sqlite3.OperationalError:
            # schema_metadata table doesn't exist yet
            return None
        finally:
            conn.close()

    def _update_metadata(
        self, entity_type: str, entity_name: str, parent_name: Optional[str] = None, **metadata
    ) -> bool:
        """Update metadata for a table or column.

        Args:
            entity_type: 'table' or 'column'
            entity_name: Name of table or column
            parent_name: For columns, the table name
            **metadata: Fields to update (description, purpose, usage_notes, etc.)

        Returns:
            bool: True if updated successfully
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build UPDATE SET clause
            set_clauses = []
            values = []

            for key, value in metadata.items():
                if key in [
                    "description",
                    "purpose",
                    "usage_notes",
                    "content_type",
                    "use_files",
                    "related_tables",
                    "foreign_keys",
                ]:
                    set_clauses.append(f"{key} = ?")
                    # Convert lists/dicts to JSON
                    if isinstance(value, (list, dict)):
                        values.append(json.dumps(value))
                    else:
                        values.append(value)

            if not set_clauses:
                return False

            # Add updated_at
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")

            # Build WHERE clause
            where_clause = "entity_type = ? AND entity_name = ?"
            where_values = [entity_type, entity_name]

            if parent_name:
                where_clause += " AND parent_name = ?"
                where_values.append(parent_name)
            else:
                where_clause += " AND parent_name IS NULL"

            # Execute UPDATE
            query = f"UPDATE system_schema_metadata SET {', '.join(set_clauses)} WHERE {where_clause}"
            cursor.execute(query, values + where_values)

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a database schema query.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <data>, "error": <error_message>}
        """
        try:
            if action == "list_tables":
                # Introspect all tables
                tables = self._introspect_tables()
                return {"result": tables, "error": None}

            elif action == "get_table_info":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                # Get metadata + introspection
                metadata = self._get_metadata("table", table)
                columns = self._introspect_columns(table)
                fks = self._introspect_foreign_keys(table)

                result = {
                    "table_name": table,
                    "columns": [col["name"] for col in columns],
                    "column_count": len(columns),
                    "foreign_keys": fks,
                }

                if metadata:
                    result.update(
                        {
                            "description": metadata["description"],
                            "purpose": metadata["purpose"],
                            "usage_notes": metadata["usage_notes"],
                            "use_files": metadata["use_files"],
                            "related_tables": metadata["related_tables"],
                        }
                    )

                return {"result": result, "error": None}

            elif action == "get_columns":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                # Introspect columns
                columns = self._introspect_columns(table)

                # Enrich with metadata
                for col in columns:
                    metadata = self._get_metadata("column", col["name"], parent_name=table)
                    if metadata:
                        col.update(
                            {
                                "description": metadata["description"],
                                "purpose": metadata["purpose"],
                                "usage_notes": metadata["usage_notes"],
                                "content_type": metadata["content_type"],
                            }
                        )

                return {"result": columns, "error": None}

            elif action == "get_relationships":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                # Get FKs via introspection
                fks = self._introspect_foreign_keys(table)

                # Get related tables from metadata
                metadata = self._get_metadata("table", table)
                related = metadata["related_tables"] if metadata else []

                return {"result": {"foreign_keys": fks, "related_tables": related}, "error": None}

            elif action == "should_use_files":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                metadata = self._get_metadata("table", table)

                if not metadata:
                    return {"result": None, "error": f"No metadata found for table '{table}'"}

                use_files = metadata["use_files"]
                reason = "Store content in database, not files" if not use_files else "Files required for this table"

                # Find content column
                columns = self._introspect_columns(table)
                content_column = None
                for col in columns:
                    col_metadata = self._get_metadata("column", col["name"], parent_name=table)
                    if col_metadata and "content" in col["name"].lower():
                        content_column = col["name"]
                        break

                return {
                    "result": use_files,
                    "reason": reason,
                    "content_column": content_column,
                    "usage_notes": metadata.get("usage_notes"),
                    "error": None,
                }

            elif action == "get_example":
                # Static examples (from DATABASE_SCHEMA_GUIDE.md logic)
                table = kwargs.get("table")
                spec_type = kwargs.get("spec_type", "monolithic")

                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                if table == "technical_specs":
                    if spec_type == "hierarchical":
                        example = {
                            "code": """
content = json.dumps({
    "overview": "High-level system description...",
    "phases": [
        {
            "number": 1,
            "name": "database-layer",
            "description": "Create database models",
            "hours": 2.0,
            "content": "## Phase 1\\\\n\\\\n### Models\\\\n..."
        }
    ]
})

db.create_technical_spec(
    spec_type="hierarchical",
    content=content,  # ✅ Store JSON here
    total_phases=1
)
""",
                            "description": "Hierarchical spec stored as JSON in content column",
                        }
                    else:
                        example = {
                            "code": """
content = \\\"\\\"\\\"# SPEC-116: User Authentication

## Overview
Complete authentication system...
\\\"\\\"\\\"

db.create_technical_spec(
    spec_type="monolithic",
    content=content  # ✅ Store markdown here
)
""",
                            "description": "Monolithic spec stored as plain markdown",
                        }

                    return {"result": example, "error": None}

                return {"result": None, "error": f"No examples for table '{table}'"}

            elif action == "update_metadata":
                # Allow code_developer to update metadata
                entity_type = kwargs.get("entity_type")
                entity_name = kwargs.get("entity_name")
                parent_name = kwargs.get("parent_name")

                if not entity_type or not entity_name:
                    return {"result": None, "error": "Missing required parameters: entity_type, entity_name"}

                # Extract metadata fields
                metadata = {
                    k: v for k, v in kwargs.items() if k not in ["entity_type", "entity_name", "parent_name", "action"]
                }

                success = self._update_metadata(entity_type, entity_name, parent_name, **metadata)

                return {
                    "result": success,
                    "message": f"Updated metadata for {entity_type} '{entity_name}'" if success else "No changes made",
                    "error": None if success else "Update failed",
                }

            else:
                return {"result": None, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"result": None, "error": str(e)}


# Skill entry point
def run(action: str, **kwargs) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        action: Action to perform
        **kwargs: Action-specific parameters

    Returns:
        dict: {"result": <data>, "error": <error_message>}
    """
    skill = DatabaseSchemaSkill()
    return skill.execute(action, **kwargs)
