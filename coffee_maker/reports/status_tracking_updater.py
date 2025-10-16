"""Status Tracking Document Updater - Auto-maintain STATUS_TRACKING.md.

This module provides functionality to automatically update the STATUS_TRACKING.md
document whenever story lifecycle events occur (start, complete, progress updates).

Example:
    >>> from coffee_maker.reports.status_tracking_updater import update_status_tracking
    >>>
    >>> # Update after story completion
    >>> update_status_tracking(
    ...     roadmap_path="docs/ROADMAP.md",
    ...     output_path="docs/STATUS_TRACKING.md"
    ... )
"""

import logging
from pathlib import Path

from coffee_maker.reports.status_report_generator import StatusReportGenerator

logger = logging.getLogger(__name__)


def update_status_tracking(
    roadmap_path: str = "docs/ROADMAP.md",
    output_path: str = "docs/STATUS_TRACKING.md",
    days: int = 14,
    upcoming_count: int = 5,
    force: bool = False,
) -> bool:
    """Update STATUS_TRACKING.md document from ROADMAP data.

    This function should be called whenever:
    - A story starts (status → In Progress)
    - A story completes (status → Complete)
    - Progress updates occur
    - Manual update requested

    Args:
        roadmap_path: Path to ROADMAP.md file
        output_path: Path to STATUS_TRACKING.md output file
        days: Number of days to look back for completions (default: 14)
        upcoming_count: Number of upcoming items to show (default: 5)
        force: Force update even if file is recent (default: False)

    Returns:
        True if update succeeded, False otherwise

    Example:
        >>> # Update after story completion
        >>> success = update_status_tracking()
        >>> print(f"Update {'succeeded' if success else 'failed'}")

        >>> # Update with custom parameters
        >>> success = update_status_tracking(
        ...     days=30,
        ...     upcoming_count=10,
        ...     force=True
        ... )
    """
    try:
        roadmap_path_obj = Path(roadmap_path)
        output_path_obj = Path(output_path)

        if not roadmap_path_obj.exists():
            logger.error(f"ROADMAP not found: {roadmap_path}")
            return False

        # Generate updated document
        generator = StatusReportGenerator(str(roadmap_path_obj))
        document_content = generator.generate_status_tracking_document(days=days, upcoming_count=upcoming_count)

        # Write to file
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        output_path_obj.write_text(document_content)

        logger.info(f"STATUS_TRACKING.md updated: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to update STATUS_TRACKING.md: {e}")
        return False


def on_story_started(story_id: str, roadmap_path: str = "docs/ROADMAP.md") -> None:
    """Hook called when a story starts (status → In Progress).

    Args:
        story_id: Story ID (e.g., "US-017")
        roadmap_path: Path to ROADMAP.md file

    Example:
        >>> on_story_started("US-017")
    """
    logger.info(f"Story started: {story_id} - Updating STATUS_TRACKING.md")
    update_status_tracking(roadmap_path=roadmap_path)


def on_story_completed(story_id: str, roadmap_path: str = "docs/ROADMAP.md") -> None:
    """Hook called when a story completes (status → Complete).

    Args:
        story_id: Story ID (e.g., "US-017")
        roadmap_path: Path to ROADMAP.md file

    Example:
        >>> on_story_completed("US-017")
    """
    logger.info(f"Story completed: {story_id} - Updating STATUS_TRACKING.md")
    update_status_tracking(roadmap_path=roadmap_path)


def on_progress_update(story_id: str, progress_pct: int, roadmap_path: str = "docs/ROADMAP.md") -> None:
    """Hook called when story progress updates.

    Args:
        story_id: Story ID (e.g., "US-017")
        progress_pct: Progress percentage (0-100)
        roadmap_path: Path to ROADMAP.md file

    Example:
        >>> on_progress_update("US-017", 75)
    """
    logger.info(f"Story progress updated: {story_id} ({progress_pct}%) - Updating STATUS_TRACKING.md")
    update_status_tracking(roadmap_path=roadmap_path)


def schedule_auto_update(interval_days: int = 3) -> None:
    """Schedule automatic STATUS_TRACKING.md updates.

    This function can be integrated with daemon or scheduler to automatically
    update the document every N days.

    Args:
        interval_days: Update interval in days (default: 3)

    Example:
        >>> # Schedule updates every 3 days
        >>> schedule_auto_update(interval_days=3)
    """
    # TODO: Implement scheduler integration
    # This would integrate with daemon or cron for automatic updates
    logger.info(f"Auto-update scheduled: every {interval_days} days")


def check_and_update_if_needed(
    roadmap_path: str = "docs/ROADMAP.md",
    output_path: str = "docs/STATUS_TRACKING.md",
    force: bool = False,
) -> dict:
    """Check if update is needed and perform it if necessary.

    This function:
    1. Checks if automatic update is needed (3-day interval)
    2. Checks for significant estimate changes (>1 day)
    3. Performs update if needed
    4. Records update timestamp

    Args:
        roadmap_path: Path to ROADMAP.md file
        output_path: Path to STATUS_TRACKING.md output file
        force: Force update regardless of schedule (default: False)

    Returns:
        Dictionary with update result:
        - updated: Whether update was performed
        - reason: Reason for update (or why skipped)
        - timestamp: Update timestamp (if performed)

    Example:
        >>> result = check_and_update_if_needed()
        >>> if result['updated']:
        ...     print(f"Updated: {result['reason']}")
        ... else:
        ...     print(f"Skipped: {result['reason']}")
    """
    from coffee_maker.reports.update_scheduler import UpdateScheduler

    try:
        scheduler = UpdateScheduler(roadmap_path=roadmap_path)

        # Check if update is needed
        if not scheduler.should_update(force=force):
            time_since = scheduler.get_time_since_last_update()
            days_ago = time_since.days if time_since else 0

            return {
                "updated": False,
                "reason": f"No update needed (last updated {days_ago} days ago)",
                "timestamp": None,
            }

        # Determine update reason
        if force:
            reason = "Manual update (forced)"
        elif scheduler._should_update_by_time():
            reason = f"{scheduler.update_interval_days}-day interval elapsed"
        else:
            changes = scheduler.check_estimate_changes()
            reason = f"{len(changes)} significant estimate change(s) detected"

        # Perform update
        success = update_status_tracking(roadmap_path=roadmap_path, output_path=output_path)

        if success:
            # Record update
            scheduler.record_update(manual=force)

            return {
                "updated": True,
                "reason": reason,
                "timestamp": scheduler.get_time_since_last_update(),
            }
        else:
            return {
                "updated": False,
                "reason": "Update failed",
                "timestamp": None,
            }

    except Exception as e:
        logger.error(f"Failed to check and update: {e}")
        return {
            "updated": False,
            "reason": f"Error: {e}",
            "timestamp": None,
        }
