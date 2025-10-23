#!/usr/bin/env python3
"""Initialize the Technical Specification Database.

This script:
1. Creates the specs database at data/specs.db
2. Imports existing spec files from docs/architecture/specs/
3. Shows statistics about imported specs

Usage:
    python init_spec_database.py
"""

from coffee_maker.autonomous.spec_database import SpecDatabase


def main():
    """Initialize spec database and import existing specs."""
    print("=" * 60)
    print("Technical Specification Database Initialization")
    print("=" * 60)

    # Create database
    print("\n1. Creating database at data/specs.db...")
    db = SpecDatabase()
    print("   ✅ Database created")

    # Import existing specs
    print("\n2. Importing existing specs from filesystem...")
    imported, skipped = db.import_existing_specs()
    print(f"   ✅ Imported: {imported} specs")
    print(f"   ⏭️  Skipped: {skipped} (already in database or invalid)")

    # Show statistics
    print("\n3. Database Statistics:")
    stats = db.get_spec_stats()

    print(f"   Total specs: {stats['total_specs']}")

    if stats.get("status_counts"):
        print("\n   Status breakdown:")
        for status, count in stats["status_counts"].items():
            print(f"     - {status}: {count}")

    if stats.get("total_estimated_hours"):
        print(f"\n   Effort estimates:")
        print(f"     - Total estimated: {stats['total_estimated_hours']:.1f} hours")
        print(f"     - Average per spec: {stats['avg_estimated_hours']:.1f} hours")

    # Show some example queries
    print("\n4. Example Queries:")

    # Get draft specs
    draft_specs = db.get_specs_by_status("draft")
    print(f"\n   Draft specs: {len(draft_specs)}")
    if draft_specs:
        for spec in draft_specs[:3]:  # Show first 3
            print(f"     - {spec['id']}: {spec['title']}")

    # Show audit trail
    print("\n5. Recent Activity (Audit Trail):")
    audit = db.get_audit_trail(limit=5)
    if audit:
        for entry in audit:
            print(f"   - {entry['changed_at']}: {entry['changed_by']} {entry['action']} {entry['spec_id']}")
    else:
        print("   No audit entries yet")

    print("\n" + "=" * 60)
    print("✅ Spec database initialization complete!")
    print(f"   Database location: data/specs.db")
    print(f"   Total specs tracked: {stats['total_specs']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
