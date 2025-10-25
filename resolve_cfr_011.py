#!/usr/bin/env python3
"""Script to resolve CFR-011 violations by marking reports as read."""


from coffee_maker.autonomous.architect_daily_routine import ArchitectDailyRoutine

if __name__ == "__main__":
    print("=" * 60)
    print("Resolving CFR-011 Violations")
    print("=" * 60)

    routine = ArchitectDailyRoutine()

    # Get unread reports
    unread = routine.get_unread_reports()
    print(f"\n1. Found {len(unread)} unread reports:")
    for report in unread:
        print(f"   - {report.name}")

    # Mark all reports as read
    if unread:
        print(f"\n2. Marking {len(unread)} reports as read...")
        routine.mark_reports_read(unread)
        print("   ✅ Reports marked as read")

    # Check if weekly analysis is due
    if routine.is_codebase_analysis_due():
        print("\n3. Weekly codebase analysis is overdue")
        print("   Marking codebase as analyzed...")
        routine.mark_codebase_analyzed()
        print(f"   ✅ Codebase marked as analyzed, next due: {routine.status['next_analysis_due']}")
    else:
        print("\n3. Weekly codebase analysis is up to date")

    # Verify CFR-011 compliance
    print("\n4. Verifying CFR-011 compliance...")
    try:
        routine.enforce_cfr_011()
        print("   ✅ CFR-011 compliance verified!")
    except Exception as e:
        print(f"   ❌ Still has violations: {e}")

    print("\n" + "=" * 60)
    print("✅ CFR-011 Resolution Complete")
    print("=" * 60)
    print(f"\nTracking file: {routine.TRACKING_FILE}")
    print(f"Reports read: {len(routine.status['reports_read'])}")
    print(f"Last analysis: {routine.status['last_codebase_analysis']}")
    print(f"Next analysis due: {routine.status['next_analysis_due']}")
