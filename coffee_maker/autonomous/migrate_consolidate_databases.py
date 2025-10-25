"""Database Consolidation Migration - Phase 1.

This migration consolidates all databases into data/roadmap.db:
- Merges data/orchestrator.db
- Merges data/notifications.db
- Merges data/agent_messages.db
- Merges coffee_maker.db
- Merges data/task_metrics.db

Author: architect
Date: 2025-10-25
Related: DATABASE_CONSOLIDATION_PLAN.md
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def attach_and_copy_table(target_conn, source_db_path, table_name, new_name=None):
    """Attach source database and copy table to target.

    Args:
        target_conn: Connection to target database
        source_db_path: Path to source database
        table_name: Table to copy
        new_name: Optional new name for table (default: same name)

    Returns:
        tuple: (success: bool, rows_copied: int, error: str)
    """
    cursor = target_conn.cursor()
    target_table = new_name or table_name

    try:
        # Ensure no existing attachment
        try:
            cursor.execute("DETACH DATABASE source_db")
        except:
            pass

        # Attach source database
        cursor.execute(f"ATTACH DATABASE '{source_db_path}' AS source_db")

        # Check if table exists in source
        cursor.execute("SELECT name FROM source_db.sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            cursor.execute("DETACH DATABASE source_db")
            return False, 0, f"Table {table_name} not found in {source_db_path}"

        # Get table schema from source
        cursor.execute(f"SELECT sql FROM source_db.sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_sql = cursor.fetchone()[0]

        # Modify CREATE TABLE statement if renaming
        if new_name:
            create_sql = create_sql.replace(
                f"CREATE TABLE {table_name}", f"CREATE TABLE IF NOT EXISTS {target_table}", 1
            )
            create_sql = create_sql.replace(
                f"CREATE TABLE IF NOT EXISTS {table_name}", f"CREATE TABLE IF NOT EXISTS {target_table}", 1
            )
        else:
            create_sql = create_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1)

        # Create table in target (if doesn't exist)
        cursor.execute(create_sql)

        # Copy data
        cursor.execute(f"INSERT OR IGNORE INTO {target_table} SELECT * FROM source_db.{table_name}")
        rows_copied = cursor.rowcount

        # Detach source database
        cursor.execute("DETACH DATABASE source_db")

        target_conn.commit()
        return True, rows_copied, None

    except Exception as e:
        try:
            cursor.execute("DETACH DATABASE source_db")
        except:
            pass
        return False, 0, str(e)


def merge_schema_metadata(target_conn, source_db_path):
    """Merge schema_metadata tables, avoiding duplicates.

    Args:
        target_conn: Connection to target database
        source_db_path: Path to source database

    Returns:
        int: Number of new records added
    """
    cursor = target_conn.cursor()

    try:
        # Ensure no existing attachment
        try:
            cursor.execute("DETACH DATABASE source_db")
        except:
            pass

        cursor.execute(f"ATTACH DATABASE '{source_db_path}' AS source_db")

        # Check if table exists in both
        cursor.execute("SELECT name FROM source_db.sqlite_master WHERE type='table' AND name='schema_metadata'")
        if not cursor.fetchone():
            cursor.execute("DETACH DATABASE source_db")
            return 0

        # Merge records (avoid duplicates)
        cursor.execute(
            """
            INSERT OR IGNORE INTO schema_metadata (
                entity_type, entity_name, parent_name, description, purpose,
                usage_notes, content_type, use_files, related_tables, foreign_keys,
                created_at, updated_at
            )
            SELECT
                entity_type, entity_name, parent_name, description, purpose,
                usage_notes, content_type, use_files, related_tables, foreign_keys,
                created_at, updated_at
            FROM source_db.schema_metadata
        """
        )

        rows_added = cursor.rowcount

        cursor.execute("DETACH DATABASE source_db")
        target_conn.commit()

        return rows_added

    except Exception as e:
        try:
            cursor.execute("DETACH DATABASE source_db")
        except:
            pass
        print(f"  ⚠️  Error merging schema_metadata: {e}")
        return 0


def migrate():
    """Run Phase 1 database consolidation."""

    print("=" * 80)
    print(" DATABASE CONSOLIDATION - Phase 1")
    print("=" * 80)
    print()
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    target_db = Path("data/roadmap.db")

    if not target_db.exists():
        print(f"❌ Target database not found: {target_db}")
        return False

    # Connect to target
    conn = sqlite3.connect(target_db)

    # Track statistics
    total_tables = 0
    total_rows = 0
    errors = []

    # Migration tasks
    migrations = [
        {
            "source": "data/orchestrator.db",
            "tables": [
                {"name": "agent_lifecycle", "rename": None},
                {"name": "orchestrator_state", "rename": None},
                {"name": "orchestrator_tasks", "rename": None},
                {"name": "bugs", "rename": None},
            ],
        },
        {
            "source": "data/notifications.db",
            "tables": [
                {"name": "notifications", "rename": "notification_user"},  # Conflict with existing
                {"name": "system_state", "rename": "notification_system_state"},
            ],
        },
        {
            "source": "data/agent_messages.db",
            "tables": [
                {"name": "agent_messages", "rename": None},
            ],
        },
        {
            "source": "coffee_maker.db",
            "tables": [
                {"name": "task_group_dependencies", "rename": None},
                # Skip schema_metadata - will merge separately
                # Skip commits, implementation_tasks (empty)
            ],
        },
        {
            "source": "data/task_metrics.db",
            "tables": [
                {"name": "subtask_metrics", "rename": None},
            ],
        },
    ]

    # Execute migrations
    for migration in migrations:
        source_path = Path(migration["source"])

        if not source_path.exists():
            print(f"⚠️  Source not found: {source_path} (skipping)")
            print()
            continue

        print(f"📁 Merging: {source_path}")
        print("-" * 80)

        for table_info in migration["tables"]:
            table_name = table_info["name"]
            new_name = table_info.get("rename")
            display_name = f"{table_name} → {new_name}" if new_name else table_name

            print(f"  📋 {display_name}...", end=" ", flush=True)

            success, rows, error = attach_and_copy_table(conn, source_path, table_name, new_name)

            if success:
                print(f"✅ {rows} rows")
                total_tables += 1
                total_rows += rows
            else:
                print(f"❌ {error}")
                errors.append(f"{source_path}/{table_name}: {error}")

        # Merge schema_metadata if exists
        if source_path.name == "coffee_maker.db":
            print(f"  📋 schema_metadata (merge)...", end=" ", flush=True)
            rows_added = merge_schema_metadata(conn, source_path)
            print(f"✅ {rows_added} new records")
            if rows_added > 0:
                total_rows += rows_added

        print()

    conn.close()

    # Summary
    print("=" * 80)
    print(" MIGRATION SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Tables merged: {total_tables}")
    print(f"✅ Total rows copied: {total_rows}")

    if errors:
        print(f"⚠️  Errors encountered: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"✅ No errors")

    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verify consolidated database
    print("=" * 80)
    print(" VERIFICATION")
    print("=" * 80)
    print()

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Total tables in {target_db}: {len(tables)}")
    print()

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  • {table}: {count} rows")

    conn.close()

    print()
    print("=" * 80)
    print(" NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Test that all functionality still works")
    print("2. Review merged data for correctness")
    print("3. Proceed with Phase 2 (table renames)")
    print()
    print(f"📦 Backup available at: data/backup-*/")
    print()

    return len(errors) == 0


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
