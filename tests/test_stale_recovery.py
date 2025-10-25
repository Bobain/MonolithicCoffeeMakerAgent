#!/usr/bin/env python3
"""Test script for stale recovery mechanisms for both reviews and specs.

This script tests that:
1. Stale code reviews (in_progress >24h) are reset to pending
2. Stale technical specs (in_progress >24h) are reset to draft
3. The recovery functions work correctly

Usage:
    python tests/test_stale_recovery.py
"""

import logging
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add skill paths
sys.path.insert(0, ".claude/skills/shared/code_review_tracking")
sys.path.insert(0, ".claude/skills/shared/technical_spec_database")

from review_tracking_skill import CodeReviewTrackingSkill
from unified_spec_skill import TechnicalSpecSkill

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_stale_review_recovery():
    """Test stale code review recovery mechanism."""
    logger.info("=" * 60)
    logger.info("Testing Stale Code Review Recovery")
    logger.info("=" * 60)

    # Initialize skill
    review_skill = CodeReviewTrackingSkill(agent_name="test_agent")

    # Create a test review that appears stale
    db_path = Path("data/unified_roadmap_specs.db")
    if not db_path.exists():
        logger.warning("Unified database does not exist yet")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert a test review that's been in_progress for >24 hours
        stale_time = (datetime.now() - timedelta(hours=48)).isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO commit_reviews (
                commit_sha, spec_id, description, review_status,
                requested_by, requested_at, reviewer, claimed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "test_stale_commit",
                "SPEC-999",
                "Test stale review",
                "in_progress",
                "test_developer",
                stale_time,
                "test_reviewer",
                stale_time,  # Claimed 48 hours ago
            ),
        )

        # Also insert a normal in_progress review (recent)
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO commit_reviews (
                commit_sha, spec_id, description, review_status,
                requested_by, requested_at, reviewer, claimed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "test_recent_commit",
                "SPEC-998",
                "Test recent review",
                "in_progress",
                "test_developer",
                recent_time,
                "test_reviewer",
                recent_time,  # Claimed 1 hour ago
            ),
        )

        conn.commit()

        # Check initial state
        cursor.execute("SELECT commit_sha, review_status FROM commit_reviews WHERE commit_sha LIKE 'test_%'")
        before = cursor.fetchall()
        logger.info(f"Before reset: {before}")

        conn.close()

        # Run the stale recovery
        count = review_skill.reset_stale_reviews()
        logger.info(f"Reset {count} stale reviews")

        # Verify the results
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT commit_sha, review_status FROM commit_reviews WHERE commit_sha = 'test_stale_commit'")
        stale_result = cursor.fetchone()

        cursor.execute("SELECT commit_sha, review_status FROM commit_reviews WHERE commit_sha = 'test_recent_commit'")
        recent_result = cursor.fetchone()

        # Clean up test data
        cursor.execute("DELETE FROM commit_reviews WHERE commit_sha LIKE 'test_%'")
        conn.commit()
        conn.close()

        # Verify expectations
        if stale_result and stale_result[1] == "pending":
            logger.info("✅ Stale review correctly reset to pending")
        else:
            logger.error(f"❌ Stale review not reset properly: {stale_result}")

        if recent_result and recent_result[1] == "in_progress":
            logger.info("✅ Recent review correctly kept as in_progress")
        else:
            logger.error(f"❌ Recent review incorrectly modified: {recent_result}")

        return True

    except Exception as e:
        logger.error(f"Error testing review recovery: {e}")
        return False


def test_stale_spec_recovery():
    """Test stale technical specification recovery mechanism."""
    logger.info("=" * 60)
    logger.info("Testing Stale Technical Spec Recovery")
    logger.info("=" * 60)

    # Initialize skill
    spec_skill = TechnicalSpecSkill(agent_name="architect")

    # The unified database path
    db_path = Path("data/unified_roadmap_specs.db")
    if not db_path.exists():
        logger.warning("Unified database does not exist yet")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert a test spec that's been in_progress for >24 hours
        stale_time = (datetime.now() - timedelta(hours=48)).isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO specs_specification (
                id, spec_number, title, roadmap_item_id,
                status, spec_type, content, started_at,
                updated_at, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "SPEC-9999",
                9999,
                "Test stale spec",
                "TEST-001",
                "in_progress",
                "monolithic",
                "Test content for stale spec",
                stale_time,  # Started 48 hours ago
                datetime.now().isoformat(),
                "test_architect",
            ),
        )

        # Also insert a normal in_progress spec (recent)
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO specs_specification (
                id, spec_number, title, roadmap_item_id,
                status, spec_type, content, started_at,
                updated_at, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "SPEC-9998",
                9998,
                "Test recent spec",
                "TEST-002",
                "in_progress",
                "monolithic",
                "Test content for recent spec",
                recent_time,  # Started 1 hour ago
                datetime.now().isoformat(),
                "test_architect",
            ),
        )

        conn.commit()

        # Check initial state
        cursor.execute(
            "SELECT id, status, started_at FROM specs_specification WHERE spec_number IN (9999, 9998) ORDER BY spec_number"
        )
        before = cursor.fetchall()
        logger.info(f"Before reset: {before}")

        conn.close()

        # Run the stale recovery
        count = spec_skill.reset_stale_specs()
        logger.info(f"Reset {count} stale specs")

        # Verify the results
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, status, started_at FROM specs_specification WHERE id = 'SPEC-9999'")
        stale_result = cursor.fetchone()

        cursor.execute("SELECT id, status, started_at FROM specs_specification WHERE id = 'SPEC-9998'")
        recent_result = cursor.fetchone()

        # Clean up test data
        cursor.execute("DELETE FROM specs_specification WHERE spec_number IN (9999, 9998)")
        conn.commit()
        conn.close()

        # Verify expectations
        if stale_result and stale_result[1] == "draft" and stale_result[2] is None:
            logger.info("✅ Stale spec correctly reset to draft with cleared started_at")
        else:
            logger.error(f"❌ Stale spec not reset properly: {stale_result}")

        if recent_result and recent_result[1] == "in_progress" and recent_result[2] is not None:
            logger.info("✅ Recent spec correctly kept as in_progress with started_at")
        else:
            logger.error(f"❌ Recent spec incorrectly modified: {recent_result}")

        return True

    except Exception as e:
        logger.error(f"Error testing spec recovery: {e}")
        return False


def main():
    """Run all stale recovery tests."""
    logger.info("Starting Stale Recovery Tests")
    logger.info("=" * 60)

    all_passed = True

    # Test review recovery
    if not test_stale_review_recovery():
        all_passed = False

    logger.info("")

    # Test spec recovery
    if not test_stale_spec_recovery():
        all_passed = False

    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ All stale recovery tests passed!")
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
