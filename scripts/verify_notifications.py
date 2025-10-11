#!/usr/bin/env python3
"""Verify notifications database for expected entries.

This script checks the notifications database to ensure expected
notifications were created by the daemon.

Exit Codes:
    0: All expected notifications found
    1: Missing expected notifications
    2: Error accessing database

Usage:
    python scripts/verify_notifications.py [--db PATH]

Example:
    python scripts/verify_notifications.py
    python scripts/verify_notifications.py --db data/notifications.db
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Optional


def get_database_path() -> Optional[Path]:
    """Find notifications database in common locations.

    Returns:
        Path to database or None if not found
    """
    locations = [
        Path("data/notifications.db"),
        Path("notifications.db"),
        Path("/var/data/notifications.db"),
    ]

    for location in locations:
        if location.exists():
            print(f"Found database: {location}")
            return location

    return None


def get_notifications(db_path: Path) -> List[Dict]:
    """Get all notifications from database.

    Args:
        db_path: Path to notifications database

    Returns:
        List of notification dictionaries
    """
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM notifications ORDER BY created_at DESC")
        notifications = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notifications
    except sqlite3.Error as e:
        print(f"❌ ERROR: Database error: {e}", file=sys.stderr)
        sys.exit(2)


def verify_notification_structure(notif: Dict) -> bool:
    """Verify notification has required fields.

    Args:
        notif: Notification dictionary

    Returns:
        True if valid structure
    """
    required_fields = ["id", "type", "title", "message", "status", "created_at"]
    return all(field in notif for field in required_fields)


def check_for_blocked_priorities(notifications: List[Dict]) -> List[Dict]:
    """Find notifications about blocked/skipped priorities.

    Args:
        notifications: List of all notifications

    Returns:
        List of blocked priority notifications
    """
    blocked = []
    for notif in notifications:
        title = notif.get("title", "").lower()
        message = notif.get("message", "").lower()

        # Check for max retries or manual review notifications
        if any(
            keyword in title or keyword in message
            for keyword in ["max retries", "manual review", "skipped", "needs manual", "no changes"]
        ):
            blocked.append(notif)

    return blocked


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify notifications database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Verify notifications in default location:
    python scripts/verify_notifications.py

  Verify specific database:
    python scripts/verify_notifications.py --db data/notifications.db
        """,
    )

    parser.add_argument(
        "--db",
        type=Path,
        help="Path to notifications database (auto-detected if not specified)",
    )

    args = parser.parse_args()

    # Find database
    db_path = args.db
    if not db_path:
        db_path = get_database_path()

    if not db_path:
        print("❌ ERROR: No notifications database found", file=sys.stderr)
        print("   Specify database with --db or ensure data/notifications.db exists", file=sys.stderr)
        sys.exit(2)

    if not db_path.exists():
        print(f"❌ ERROR: Database not found: {db_path}", file=sys.stderr)
        sys.exit(2)

    # Get notifications
    print(f"Verifying notifications: {db_path}")
    print()

    notifications = get_notifications(db_path)

    if not notifications:
        print("⚠️  WARNING: No notifications found in database")
        print("   This might indicate:")
        print("   - Daemon hasn't run yet")
        print("   - Database was recently cleared")
        print("   - No issues encountered")
        sys.exit(0)

    print(f"Total notifications: {len(notifications)}")
    print()

    # Verify structure
    invalid = [n for n in notifications if not verify_notification_structure(n)]
    if invalid:
        print(f"❌ ERROR: {len(invalid)} notification(s) with invalid structure")
        for notif in invalid:
            print(f"   - Notification {notif.get('id', 'unknown')}")
        sys.exit(1)

    print("✅ All notifications have valid structure")

    # Check for blocked priorities
    blocked = check_for_blocked_priorities(notifications)
    if blocked:
        print()
        print(f"⚠️  Found {len(blocked)} notification(s) about blocked priorities:")
        print()
        for notif in blocked:
            print(f"   📋 Notification #{notif['id']}: {notif['title']}")
            print(f"      Type: {notif['type']}")
            print(f"      Status: {notif['status']}")
            print(f"      Message: {notif['message'][:100]}...")
            print()

        print("   These priorities may require manual intervention.")

    # Summary by status
    status_counts = {}
    for notif in notifications:
        status = notif["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    print()
    print("Notification Summary by Status:")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")

    # Summary by type
    type_counts = {}
    for notif in notifications:
        notif_type = notif["type"]
        type_counts[notif_type] = type_counts.get(notif_type, 0) + 1

    print()
    print("Notification Summary by Type:")
    for notif_type, count in sorted(type_counts.items()):
        print(f"   {notif_type}: {count}")

    print()
    print("✅ Notification verification complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
