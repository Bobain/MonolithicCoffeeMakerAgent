#!/usr/bin/env python3
"""Test the Technical Specification Database functionality.

This script demonstrates:
1. Reading spec information (all agents can do this)
2. Creating and updating specs (architect only)
3. Querying and statistics
"""

import sys

sys.path.insert(0, ".claude/skills/shared/technical_specification_handling")

from coffee_maker.autonomous.spec_database import SpecDatabase
from spec_database_integration import SpecDatabaseIntegration


def test_read_operations():
    """Test read operations (available to all agents)."""
    print("\n" + "=" * 60)
    print("Testing READ Operations (All Agents)")
    print("=" * 60)

    db = SpecDatabase()

    # Get all specs
    all_specs = db.get_all_specs()
    print(f"\n1. Total specs in database: {len(all_specs)}")

    # Show first 5 specs
    print("\n2. First 5 specs:")
    for spec in all_specs[:5]:
        status_icon = {"draft": "📝", "in_progress": "🔄", "complete": "✅", "approved": "✓"}.get(spec["status"], "?")
        print(f"   {status_icon} {spec['id']}: {spec['title'][:40]}...")

    # Get stats
    stats = db.get_spec_stats()
    print("\n3. Statistics:")
    print(f"   Total specs: {stats['total_specs']}")
    if stats["status_counts"]:
        print("   By status:")
        for status, count in stats["status_counts"].items():
            print(f"     - {status}: {count}")

    # Find specific spec
    print("\n4. Finding specific spec (SPEC-1):")
    spec = db.get_spec("SPEC-1")
    if spec:
        print(f"   Found: {spec['title']}")
        print(f"   Status: {spec['status']}")
        print(f"   File: {spec['file_path']}")


def test_write_operations():
    """Test write operations (architect only)."""
    print("\n" + "=" * 60)
    print("Testing WRITE Operations (Architect Only)")
    print("=" * 60)

    # Test as architect
    integration = SpecDatabaseIntegration(agent_name="architect")

    print("\n1. Creating new spec as architect:")
    try:
        spec_id, file_path = integration.create_spec_with_tracking(
            spec_number=999,
            title="Test Spec for Database Demo",
            roadmap_item_id="TEST-001",
            content="# SPEC-999: Test Spec\n\nThis is a test spec for demonstration.",
            spec_type="monolithic",
            estimated_hours=2.0,
        )
        print(f"   ✅ Created: {spec_id}")
        print(f"   File: {file_path}")

        # Update status
        print("\n2. Updating spec status:")
        success = integration.update_spec_status(spec_id, "in_progress")
        if success:
            print(f"   ✅ Updated {spec_id} to 'in_progress'")

        # Complete with actual hours
        print("\n3. Completing spec with actual hours:")
        success = integration.update_spec_status(spec_id, "complete", actual_hours=1.5)
        if success:
            print(f"   ✅ Completed {spec_id} (1.5 hours actual)")

    except PermissionError as e:
        print(f"   ❌ Permission error: {e}")

    # Test as non-architect
    print("\n4. Testing write protection (as code_developer):")
    integration_dev = SpecDatabaseIntegration(agent_name="code_developer")
    try:
        integration_dev.create_spec_with_tracking(
            spec_number=998,
            title="Should Fail",
            roadmap_item_id="TEST-002",
            content="This should not work",
        )
        print("   ❌ ERROR: Should have been blocked!")
    except PermissionError as e:
        print(f"   ✅ Correctly blocked: {e}")


def test_integration_features():
    """Test integration features."""
    print("\n" + "=" * 60)
    print("Testing Integration Features")
    print("=" * 60)

    integration = SpecDatabaseIntegration(agent_name="code_developer")

    # Find spec for priority
    print("\n1. Finding spec for priority:")
    priority = {"number": "1", "title": "US-001 - Some feature", "name": "PRIORITY-1"}
    spec = integration.find_spec_for_priority(priority)
    if spec:
        print(f"   Found: {spec['id']} - {spec['title']}")
    else:
        print("   No spec found for this priority")

    # Get pending specs
    print("\n2. Pending specs (need work):")
    pending = integration.get_pending_specs()
    print(f"   Total pending: {len(pending)}")
    for spec in pending[:3]:
        print(f"     - {spec['id']}: {spec['status']}")

    # Check if spec exists
    print("\n3. Checking if specs exist:")
    for num in [1, 999, 1000]:
        exists = integration.check_spec_exists(num)
        print(f"   SPEC-{num}: {'✅ Exists' if exists else '❌ Not found'}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Technical Specification Database Test Suite")
    print("=" * 60)

    test_read_operations()
    test_write_operations()
    test_integration_features()

    print("\n" + "=" * 60)
    print("✅ Test Suite Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
