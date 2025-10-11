#!/usr/bin/env python3
"""Verify notification system is working correctly.

This script checks:
- Notification database exists and is accessible
- Notifications can be created and retrieved
- Database schema is correct

Usage:
    python scripts/verify_notifications.py [--db-path PATH]

Exit Codes:
    0: All checks passed
    1: Verification failed
    2: Script error
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List


def check_db_exists(db_path: Path) -> bool:
    """Check if notification database exists.

    Args:
        db_path: Path to database file

    Returns:
        True if database exists
    """
    return db_path.exists()


def verify_db_schema(db_path: Path) -> Dict[str, bool]:
    """Verify database schema is correct.

    Args:
        db_path: Path to database file

    Returns:
        Dict with verification results
    """
    results = {
        "can_import": False,
        "can_connect": False,
        "has_notifications_table": False,
        "can_create": False,
        "can_retrieve": False,
    }

    try:
        # Import NotificationDB
        from coffee_maker.cli.notification_db import NotificationDB

        results["can_import"] = True

        # Connect to database
        db = NotificationDB(str(db_path))
        results["can_connect"] = True

        # Check table exists (by trying to query)
        try:
            db.get_pending_notifications()
            results["has_notifications_table"] = True
        except Exception:
            pass

        # Try to create a test notification
        try:
            test_id = db.create_notification(
                notification_type="test", priority_name="TEST_VERIFY", message="Verification test notification"
            )
            results["can_create"] = True

            # Try to retrieve it
            test_notif = db.get_notification(test_id)
            if test_notif and test_notif["id"] == test_id:
                results["can_retrieve"] = True

            # Clean up test notification
            try:
                db.mark_notification_handled(test_id, response="test_cleanup")
            except Exception:
                pass

        except Exception:
            pass

    except Exception as e:
        print(f"⚠️  Error during verification: {e}", file=sys.stderr)

    return results


def check_pending_notifications(db_path: Path) -> List[Dict]:
    """Get list of pending notifications.

    Args:
        db_path: Path to database file

    Returns:
        List of pending notification dicts
    """
    try:
        from coffee_maker.cli.notification_db import NotificationDB

        db = NotificationDB(str(db_path))
        return db.get_pending_notifications()
    except Exception as e:
        print(f"⚠️  Could not retrieve pending notifications: {e}", file=sys.stderr)
        return []


def print_results(db_path: Path, results: Dict[str, bool], pending: List[Dict]) -> None:
    """Print verification results.

    Args:
        db_path: Path to database file
        results: Verification results
        pending: List of pending notifications
    """
    print("\n" + "=" * 60)
    print("NOTIFICATION SYSTEM VERIFICATION")
    print("=" * 60 + "\n")

    print(f"Database: {db_path}")
    print(f"Exists: {'✅' if db_path.exists() else '❌'}\n")

    print("Verification Checks:")
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        check_name = check.replace("_", " ").title()
        print(f"  {status} {check_name}")

    print(f"\nPending Notifications: {len(pending)}")
    if pending:
        print("\nRecent pending notifications:")
        for notif in pending[:5]:  # Show first 5
            print(f"  - [{notif['id']}] {notif['priority_name']}: {notif['message'][:50]}...")

    # Overall status
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ VERIFICATION PASSED: Notification system is working")
    else:
        print("❌ VERIFICATION FAILED: Issues detected")
    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify notification system health", formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/notifications.db"),
        help="Path to notifications database (default: data/notifications.db)",
    )
    parser.add_argument("--quiet", action="store_true", help="Only output errors (exit code indicates status)")

    args = parser.parse_args()

    try:
        # Run verification
        db_exists = check_db_exists(args.db_path)

        if not db_exists:
            if not args.quiet:
                print(f"⚠️  Database not found: {args.db_path}")
                print("   This is normal if daemon hasn't run yet.")
            sys.exit(0)  # Not an error if DB doesn't exist yet

        results = verify_db_schema(args.db_path)
        pending = check_pending_notifications(args.db_path)

        if not args.quiet:
            print_results(args.db_path, results, pending)

        # Exit with appropriate code
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
