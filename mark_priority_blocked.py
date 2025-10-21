#!/usr/bin/env python3
"""Mark PRIORITY 25 as blocked so daemon will skip it and move to next priority."""

from pathlib import Path

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

if __name__ == "__main__":
    print("=" * 60)
    print("Marking PRIORITY 25 as Blocked")
    print("=" * 60)

    db = RoadmapDatabase()

    # Import current ROADMAP
    roadmap_path = Path("docs/roadmap/ROADMAP.md")
    print(f"\n1. Importing ROADMAP from {roadmap_path}...")
    items_imported = db.import_from_file(roadmap_path)
    print(f"   ✅ Imported {items_imported} items")

    # Find PRIORITY 25
    items = db.get_all_items()
    priority_25 = next((item for item in items if item["id"] == "PRIORITY-25"), None)

    if not priority_25:
        print("\n   ❌ PRIORITY 25 not found in database")
        exit(1)

    print(f"\n2. Found PRIORITY-25:")
    print(f"   Title: {priority_25['title']}")
    print(f"   Current status: {priority_25['status']}")

    # Update status to Blocked
    print(f"\n3. Updating status to '⏸️ Blocked - Waiting for spec'...")
    success = db.update_status(
        item_id="PRIORITY-25", new_status="⏸️ Blocked - Waiting for spec", updated_by="manual_fix"
    )

    if not success:
        print("   ❌ Failed to update status")
        exit(1)

    print("   ✅ Status updated in database")

    # Export back to ROADMAP.md
    print(f"\n4. Exporting to {roadmap_path}...")
    db.export_to_file(roadmap_path)
    print("   ✅ Exported to ROADMAP.md")

    # Verify
    items = db.get_all_items()
    priority_25 = next((item for item in items if item["id"] == "PRIORITY-25"), None)
    print(f"\n5. Verification:")
    print(f"   New status: {priority_25['status']}")

    # Get next planned (should now be PRIORITY 26 or later)
    print(f"\n6. Finding next planned priority...")
    next_item = db.get_next_planned()
    if next_item:
        print(f"   ✅ Next planned: {next_item['id']} - {next_item['title']}")
    else:
        print("   ℹ️  No more planned priorities")

    print("\n" + "=" * 60)
    print("✅ PRIORITY 25 marked as blocked")
    print("=" * 60)
    print("\nThe daemon will now skip PRIORITY 25 and work on the next priority.")
    print("Once architect creates the spec, you can unblock it with:")
    print("  poetry run python unblock_priority.py 25")
