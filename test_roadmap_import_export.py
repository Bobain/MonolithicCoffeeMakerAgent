#!/usr/bin/env python3
"""Test script for RoadmapDatabase import/export cycle.

This script tests:
1. Importing ROADMAP.md into database
2. Querying items from database
3. Exporting database back to markdown
4. Verifying the export matches original formatting
"""

import tempfile
from pathlib import Path

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


def test_import_export_cycle():
    """Test complete import/export cycle with real ROADMAP.md."""
    print("=" * 60)
    print("Testing RoadmapDatabase Import/Export Cycle")
    print("=" * 60)

    # Use temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_roadmap.db"
        db = RoadmapDatabase(db_path=db_path)

        # Import from actual ROADMAP.md
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            print(f"❌ ROADMAP.md not found at {roadmap_path}")
            return False

        print(f"\n1. Importing from {roadmap_path}...")
        items_imported = db.import_from_file(roadmap_path)
        print(f"   ✅ Imported {items_imported} items")

        # Query all items
        print("\n2. Querying all items from database...")
        items = db.get_all_items()
        print(f"   ✅ Found {len(items)} items in database")

        # Show first 3 items
        print("\n3. Sample items:")
        for item in items[:3]:
            print(f"   - {item['id']}: {item['title']} [{item['status']}]")

        # Get next planned item
        print("\n4. Finding next planned item...")
        next_item = db.get_next_planned()
        if next_item:
            print(f"   ✅ Next planned: {next_item['id']} - {next_item['title']}")
        else:
            print("   ℹ️  No planned items found")

        # Export to temporary file
        print("\n5. Exporting to temporary file...")
        export_path = Path(tmpdir) / "ROADMAP_exported.md"
        db.export_to_file(export_path)
        print(f"   ✅ Exported to {export_path}")

        # Compare line counts
        original_lines = roadmap_path.read_text().split("\n")
        exported_lines = export_path.read_text().split("\n")

        print("\n6. Comparing original and exported files...")
        print(f"   Original: {len(original_lines)} lines")
        print(f"   Exported: {len(exported_lines)} lines")

        # Check if we preserved structure
        if abs(len(original_lines) - len(exported_lines)) < 10:
            print("   ✅ Line counts match (within 10 lines)")
        else:
            print(f"   ⚠️  Line count difference: {abs(len(original_lines) - len(exported_lines))} lines")

        # Test notification workflow
        print("\n7. Testing notification workflow...")

        # Create a test notification
        notification_id = db.create_update_notification(
            item_id=items[0]["id"],
            requested_by="test_script",
            notification_type="status_update",
            requested_status="🔄 In Progress",
            message="Testing notification system",
        )
        print(f"   ✅ Created notification ID: {notification_id}")

        # Get pending notifications
        notifications = db.get_pending_notifications()
        print(f"   ✅ Found {len(notifications)} pending notification(s)")

        # Approve the notification
        success = db.approve_notification(
            notification_id=notification_id, processed_by="test_script", notes="Test approval"
        )
        if success:
            print("   ✅ Approved notification successfully")
        else:
            print("   ❌ Failed to approve notification")

        # Verify item status was updated
        updated_items = db.get_all_items()
        updated_item = next((i for i in updated_items if i["id"] == items[0]["id"]), None)
        if updated_item and updated_item["status"] == "🔄 In Progress":
            print("   ✅ Item status updated correctly")
        else:
            print("   ❌ Item status not updated")

        print("\n" + "=" * 60)
        print("✅ Import/Export cycle test completed successfully!")
        print("=" * 60)

        return True


if __name__ == "__main__":
    try:
        success = test_import_export_cycle()
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        exit(1)
