#!/usr/bin/env python3
"""Migration: Rename section_order to priority_order in roadmap_items table.

This migration renames the section_order column to priority_order for better clarity.
The field represents the priority ordering from ROADMAP.md, not section divisions.

Rationale:
- section_order is misleading (it's about priority, not sections)
- priority_order clearly indicates it tracks roadmap priority position
- More intuitive for all agents using roadmap ordering

This migration runs on:
- data/roadmap.db (RoadmapDatabase)
- data/unified_roadmap_specs.db (UnifiedDatabase)

Author: architect
Date: 2025-10-24
Related: User feedback on field naming
"""

import sqlite3
from pathlib import Path


def migrate_rename_section_order(db_path: str, table_name: str = "roadmap_items") -> None:
    """Rename section_order to priority_order in roadmap_items table.

    Args:
        db_path: Path to database file
        table_name: Table to migrate (default: roadmap_items)
    """
    print(f"\n🔧 Migration: Rename section_order → priority_order")
    print(f"Database: {db_path}")
    print(f"Table: {table_name}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"⚠️  {table_name} table does not exist, skipping migration")
            conn.close()
            return

        print(f"\n1. Reading current schema and data...")
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"   Found {len(rows)} existing items")

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current columns: {', '.join(columns)}")

        # Check if already migrated
        if "priority_order" in columns:
            print("✅ Column already renamed to priority_order, skipping migration")
            conn.close()
            return

        if "section_order" not in columns:
            print("⚠️  section_order column not found, skipping migration")
            conn.close()
            return

        print(f"\n2. Creating new table with priority_order...")
        cursor.execute(
            f"""
            CREATE TABLE {table_name}_new (
                id TEXT PRIMARY KEY,
                item_type TEXT NOT NULL,
                number TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                spec_id TEXT,
                content TEXT,
                estimated_hours TEXT,
                dependencies TEXT,
                priority_order INTEGER NOT NULL UNIQUE,  -- RENAMED from section_order, UNIQUE constraint added
                implementation_started_at TEXT,
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                FOREIGN KEY (spec_id) REFERENCES technical_specs(id) ON DELETE SET NULL
            )
        """
        )
        print("✅ New table created")

        print(f"\n3. Migrating data to new table...")
        if rows:
            for row in rows:
                old_data = dict(zip(columns, row))

                cursor.execute(
                    f"""
                    INSERT INTO {table_name}_new (
                        id, item_type, number, title, status, spec_id,
                        content, estimated_hours, dependencies, priority_order,
                        implementation_started_at, updated_at, updated_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        old_data["id"],
                        old_data["item_type"],
                        old_data["number"],
                        old_data["title"],
                        old_data["status"],
                        old_data.get("spec_id"),
                        old_data.get("content"),
                        old_data.get("estimated_hours"),
                        old_data.get("dependencies"),
                        old_data["section_order"],  # Copy value to priority_order
                        old_data.get("implementation_started_at"),
                        old_data["updated_at"],
                        old_data["updated_by"],
                    ),
                )

            print(f"✅ Migrated {len(rows)} items")
        else:
            print("   No data to migrate")

        print(f"\n4. Recreating indexes...")
        # Drop old indexes
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_type")
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_status")
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_order")
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_number")
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_spec")
        cursor.execute(f"DROP INDEX IF EXISTS idx_items_id")

        # Create new indexes with updated name
        cursor.execute(f"CREATE INDEX idx_items_type ON {table_name}_new(item_type)")
        cursor.execute(f"CREATE INDEX idx_items_status ON {table_name}_new(status)")
        cursor.execute(f"CREATE INDEX idx_items_priority_order ON {table_name}_new(priority_order)")  # RENAMED
        cursor.execute(f"CREATE INDEX idx_items_number ON {table_name}_new(number)")
        cursor.execute(f"CREATE INDEX idx_items_spec ON {table_name}_new(spec_id)")
        cursor.execute(f"CREATE UNIQUE INDEX idx_items_id ON {table_name}_new(id)")
        print("✅ Indexes recreated (idx_items_order → idx_items_priority_order)")

        print(f"\n5. Swapping tables...")
        cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        print("✅ Tables swapped")

        conn.commit()
        print(f"\n✅ Migration complete!")
        print(f"   - Renamed: section_order → priority_order")
        print(f"   - Added: UNIQUE constraint on priority_order")
        print(f"   - Updated: Index name (idx_items_order → idx_items_priority_order)")
        print(f"   - Preserved: All {len(rows)} items with ordering intact")

    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration(db_path: str, table_name: str = "roadmap_items") -> None:
    """Verify migration was successful.

    Args:
        db_path: Path to database file
        table_name: Table to verify
    """
    print(f"\n🔍 Verifying migration...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        print(f"❌ {table_name} table not found!")
        conn.close()
        return

    print(f"✅ {table_name} table exists")

    # Check schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    # Check old column is gone
    if "section_order" in columns:
        print("❌ Old 'section_order' column still exists!")
    else:
        print("✅ Old 'section_order' column removed")

    # Check new column exists
    if "priority_order" in columns:
        print(f"✅ New 'priority_order' column exists ({columns['priority_order']})")
    else:
        print("❌ New 'priority_order' column missing!")

    # Check indexes
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'")
    indexes = [row[0] for row in cursor.fetchall()]

    if "idx_items_order" in indexes:
        print("❌ Old index 'idx_items_order' still exists!")
    else:
        print("✅ Old index 'idx_items_order' removed")

    if "idx_items_priority_order" in indexes:
        print("✅ New index 'idx_items_priority_order' exists")
    else:
        print("❌ New index 'idx_items_priority_order' missing!")

    # Check data
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total items: {count}")

    # Show sample ordering
    cursor.execute(f"SELECT id, title, priority_order FROM {table_name} ORDER BY priority_order LIMIT 5")
    print(f"\n📋 Sample items (ordered by priority_order):")
    for row in cursor.fetchall():
        print(f"   {row[2]:3d}. {row[0]}: {row[1][:50]}")

    conn.close()


if __name__ == "__main__":
    # Migrate both databases
    databases = [
        ("data/roadmap.db", "RoadmapDatabase"),
        ("data/unified_roadmap_specs.db", "UnifiedDatabase"),
    ]

    for db_path, db_name in databases:
        db_file = Path(db_path)
        if not db_file.exists():
            print(f"\n⚠️  {db_name} not found at {db_path}, skipping")
            continue

        print(f"\n{'=' * 70}")
        print(f"Migrating {db_name}")
        print(f"{'=' * 70}")

        migrate_rename_section_order(str(db_file))
        verify_migration(str(db_file))

    print(f"\n{'=' * 70}")
    print("✅ All migrations complete!")
    print(f"{'=' * 70}")
