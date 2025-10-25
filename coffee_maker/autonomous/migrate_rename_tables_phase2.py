"""Database Consolidation - Phase 2: Table Renames.

This migration renames all tables to the new domain-based naming convention:
- roadmap_items → roadmap_priority
- technical_specs → specs_specification
- implementation_tasks → specs_task
- task_group_dependencies → specs_task_dependency
- code_reviews → review_code_review
- implementation_commits → review_commit
- audit_trail → system_audit
- schema_metadata → system_schema_metadata
- roadmap_update_notifications → roadmap_notification

Creates backward-compatible views for all old table names.

Author: architect
Date: 2025-10-25
Related: DATABASE_CONSOLIDATION_PLAN.md
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def rename_table(conn, old_name: str, new_name: str) -> tuple[bool, str]:
    """Rename a table and create a backward-compatible view.

    Args:
        conn: Database connection
        old_name: Current table name
        new_name: New table name

    Returns:
        tuple: (success: bool, message: str)
    """
    cursor = conn.cursor()

    try:
        # Check if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (old_name,))
        if not cursor.fetchone():
            return False, f"Table {old_name} not found"

        # Check if new table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (new_name,))
        if cursor.fetchone():
            return False, f"Table {new_name} already exists"

        # Rename table
        cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

        # Create backward-compatible view
        cursor.execute(f"CREATE VIEW {old_name} AS SELECT * FROM {new_name}")

        conn.commit()
        return True, f"Renamed {old_name} → {new_name} (with view)"

    except Exception as e:
        return False, f"Error: {e}"


def update_schema_metadata_references(conn):
    """Update schema_metadata table references to new table names.

    Args:
        conn: Database connection

    Returns:
        int: Number of records updated
    """
    cursor = conn.cursor()

    # Use system_schema_metadata (the actual table, not the view)
    metadata_table = "system_schema_metadata"

    # Mapping of old to new table names
    table_mapping = {
        "roadmap_items": "roadmap_priority",
        "technical_specs": "specs_specification",
        "implementation_tasks": "specs_task",
        "task_group_dependencies": "specs_task_dependency",
        "code_reviews": "review_code_review",
        "implementation_commits": "review_commit",
        "audit_trail": "system_audit",
        "schema_metadata": "system_schema_metadata",
        "roadmap_update_notifications": "roadmap_notification",
    }

    updated_count = 0

    for old_name, new_name in table_mapping.items():
        # Update entity_name for table records
        cursor.execute(
            f"""
            UPDATE {metadata_table}
            SET entity_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE entity_type = 'table' AND entity_name = ?
        """,
            (new_name, old_name),
        )
        updated_count += cursor.rowcount

        # Update parent_name for column records
        cursor.execute(
            f"""
            UPDATE {metadata_table}
            SET parent_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE entity_type = 'column' AND parent_name = ?
        """,
            (new_name, old_name),
        )
        updated_count += cursor.rowcount

        # Update related_tables JSON references (if any)
        cursor.execute(
            f"""
            UPDATE {metadata_table}
            SET related_tables = REPLACE(related_tables, ?, ?), updated_at = CURRENT_TIMESTAMP
            WHERE related_tables LIKE ?
        """,
            (f'"{old_name}"', f'"{new_name}"', f'%"{old_name}"%'),
        )
        updated_count += cursor.rowcount

    conn.commit()
    return updated_count


def migrate():
    """Run Phase 2: Table Renames."""

    print("=" * 80)
    print(" DATABASE CONSOLIDATION - Phase 2: Table Renames")
    print("=" * 80)
    print()
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    target_db = Path("data/roadmap.db")

    if not target_db.exists():
        print(f"❌ Target database not found: {target_db}")
        return False

    conn = sqlite3.connect(target_db)

    # Table rename mappings (in order to avoid FK conflicts)
    renames = [
        # DOMAIN: roadmap
        ("roadmap_items", "roadmap_priority"),
        ("roadmap_update_notifications", "roadmap_notification"),
        # DOMAIN: specs
        ("technical_specs", "specs_specification"),
        ("implementation_tasks", "specs_task"),
        ("task_group_dependencies", "specs_task_dependency"),
        # DOMAIN: review
        ("code_reviews", "review_code_review"),
        ("implementation_commits", "review_commit"),
        # DOMAIN: orchestrator
        ("orchestrator_state", "orchestrator_state"),  # Keep as-is
        ("orchestrator_tasks", "orchestrator_task"),  # Remove 's'
        ("bugs", "orchestrator_bug"),
        # DOMAIN: notification
        ("notification_user", "notification_user"),  # Keep as-is
        ("notification_system_state", "notification_system_state"),  # Keep as-is
        # DOMAIN: agent
        ("agent_lifecycle", "agent_lifecycle"),  # Keep as-is
        ("agent_messages", "agent_message"),  # Remove 's'
        # DOMAIN: metrics
        ("subtask_metrics", "metrics_subtask"),
        # DOMAIN: system
        ("audit_trail", "system_audit"),
        ("schema_metadata", "system_schema_metadata"),
        # DOMAIN: roadmap (keep as-is)
        ("roadmap_audit", "roadmap_audit"),
        ("roadmap_metadata", "roadmap_metadata"),
    ]

    # Track statistics
    success_count = 0
    skip_count = 0
    error_count = 0
    errors = []

    print("📋 Renaming Tables")
    print("-" * 80)

    for old_name, new_name in renames:
        # Skip if same name
        if old_name == new_name:
            print(f"  ⏭️  {old_name} (no change needed)")
            skip_count += 1
            continue

        print(f"  🔄 {old_name} → {new_name}...", end=" ", flush=True)

        success, message = rename_table(conn, old_name, new_name)

        if success:
            print(f"✅ {message}")
            success_count += 1
        else:
            print(f"❌ {message}")
            errors.append(f"{old_name} → {new_name}: {message}")
            error_count += 1

    print()

    # Update schema_metadata references
    print("📋 Updating schema_metadata References")
    print("-" * 80)

    updated_count = update_schema_metadata_references(conn)
    print(f"  ✅ Updated {updated_count} metadata records")
    print()

    conn.close()

    # Summary
    print("=" * 80)
    print(" MIGRATION SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Tables renamed: {success_count}")
    print(f"⏭️  Tables skipped (no change): {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📝 Metadata records updated: {updated_count}")

    if errors:
        print()
        print("⚠️  Errors encountered:")
        for error in errors:
            print(f"   - {error}")

    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verification
    print("=" * 80)
    print(" VERIFICATION - New Table Structure")
    print("=" * 80)
    print()

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    # List tables by domain
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """
    )
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Total tables: {len(tables)}")
    print()

    # Group by domain
    domains = {}
    for table in tables:
        if "_" in table:
            domain = table.split("_")[0]
        else:
            domain = "other"

        if domain not in domains:
            domains[domain] = []
        domains[domain].append(table)

    for domain, domain_tables in sorted(domains.items()):
        print(f"📦 {domain.upper()} domain:")
        for table in sorted(domain_tables):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} rows")
        print()

    # List views
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    """
    )
    views = [row[0] for row in cursor.fetchall()]

    if views:
        print(f"📋 Backward-compatible views: {len(views)}")
        for view in views:
            print(f"   • {view}")
        print()

    conn.close()

    print("=" * 80)
    print(" NEXT STEPS")
    print("=" * 80)
    print()
    print("1. ✅ Phase 2 complete - tables renamed with views for backward compatibility")
    print("2. ⏭️  Phase 3: Update code references to use new table names")
    print("3. ⏭️  Phase 4: Document all tables in system_schema_metadata")
    print()
    print("ℹ️  Note: Existing code will continue to work via views")
    print("   Gradually update code to use new table names for better clarity")
    print()

    return error_count == 0


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
