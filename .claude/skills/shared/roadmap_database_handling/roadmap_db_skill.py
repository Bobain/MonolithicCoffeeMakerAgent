"""Roadmap Database Skill for All Agents.

This skill provides a unified interface for all agents to interact with the roadmap database.
It enforces access control (write for project_manager only, read for all).

Access Control:
    - Write access: project_manager ONLY
    - Read access: All agents
    - Notifications: All agents can request updates via notifications

Usage Example:
    >>> from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
    >>>
    >>> # Initialize with agent name for access control
    >>> roadmap_db = RoadmapDatabase(agent_name="code_developer")
    >>>
    >>> # Read operations (allowed for all agents)
    >>> items = roadmap_db.get_all_items()
    >>> next_item = roadmap_db.get_next_planned()
    >>> stats = roadmap_db.get_stats()
    >>>
    >>> # Request updates (all agents can notify project_manager)
    >>> roadmap_db.create_update_notification(
    ...     item_id="US-062",
    ...     requested_by="code_developer",
    ...     notification_type="status_update",
    ...     requested_status="✅ Complete",
    ...     message="Implementation completed and tested"
    ... )
    >>>
    >>> # Write operations (project_manager ONLY)
    >>> if agent_name == "project_manager":
    ...     roadmap_db.update_status("US-062", "✅ Complete", "project_manager")
    ...     roadmap_db.approve_notification(notification_id, "project_manager")

Key Features:
    - Database-only access (ROADMAP.md file access is FORBIDDEN)
    - Foreign key links to technical_specs database
    - Audit trail for all changes
    - Notification system for inter-agent communication
    - Automatic project_manager notification for needed updates

Integration with Technical Specs:
    Each roadmap item has a spec_id field linking to technical_specs.id.
    This allows code_developer to find the spec for implementation:

    >>> item = roadmap_db.get_item("US-062")
    >>> spec_id = item.get("spec_id")  # e.g., "SPEC-062"
    >>> # code_developer can then read the spec from spec database

IMPORTANT Rules:
    1. NEVER read/write ROADMAP.md file directly
    2. Always use RoadmapDatabase for roadmap operations
    3. Non-PM agents must use notifications for status updates
    4. project_manager reviews and approves all notifications
    5. Database is the single source of truth for roadmap
"""

import logging
from typing import Dict, List, Optional

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

logger = logging.getLogger(__name__)


class RoadmapDBSkill:
    """Skill for interacting with roadmap database.

    This provides a clean interface for all agents to work with the roadmap
    while enforcing access control and database-only patterns.
    """

    def __init__(self, agent_name: str):
        """Initialize roadmap database skill.

        Args:
            agent_name: Name of agent using this skill (for access control)
        """
        self.agent_name = agent_name
        self.db = RoadmapDatabase(agent_name=agent_name)
        self.can_write = agent_name == "project_manager"

        if not self.can_write:
            logger.info(f"Agent {agent_name} has read-only access to roadmap")

    def get_next_priority(self) -> Optional[Dict]:
        """Get next planned priority from roadmap.

        Returns:
            Next planned item dict or None if no planned items
        """
        return self.db.get_next_planned()

    def get_item_spec(self, item_id: str) -> Optional[str]:
        """Get technical spec ID for a roadmap item.

        Args:
            item_id: Roadmap item ID (e.g., "US-062")

        Returns:
            Spec ID (e.g., "SPEC-062") or None if no spec linked
        """
        item = self.db.get_item(item_id)
        return item.get("spec_id") if item else None

    def request_status_update(self, item_id: str, new_status: str, reason: str) -> int:
        """Request project_manager to update item status.

        This creates a notification that project_manager will review.

        Args:
            item_id: Item to update (e.g., "US-062")
            new_status: Requested status (e.g., "✅ Complete")
            reason: Explanation for the update

        Returns:
            Notification ID
        """
        return self.db.create_update_notification(
            item_id=item_id,
            requested_by=self.agent_name,
            notification_type="status_update",
            requested_status=new_status,
            message=reason,
        )

    def get_roadmap_stats(self) -> Dict:
        """Get roadmap statistics.

        Returns:
            Dict with total, planned, in_progress, complete counts
        """
        return self.db.get_stats()

    def find_items_needing_specs(self) -> List[Dict]:
        """Find roadmap items without technical specs.

        Useful for architect to identify what needs design work.

        Returns:
            List of items missing spec_id
        """
        all_items = self.db.get_all_items()
        return [item for item in all_items if not item.get("spec_id") and item.get("status") != "✅ Complete"]

    def find_items_ready_for_implementation(self) -> List[Dict]:
        """Find items with specs ready for code_developer.

        Returns:
            List of planned items that have technical specs
        """
        all_items = self.db.get_all_items(status_filter="Planned")
        return [item for item in all_items if item.get("spec_id")]  # Has a spec

    # Project Manager only methods
    def update_item_status(self, item_id: str, new_status: str) -> bool:
        """Update roadmap item status (PM only).

        Args:
            item_id: Item to update
            new_status: New status

        Returns:
            True if successful

        Raises:
            PermissionError: If not project_manager
        """
        if not self.can_write:
            raise PermissionError(f"Only project_manager can update status, not {self.agent_name}")

        return self.db.update_status(item_id, new_status, self.agent_name)

    def process_pending_notifications(self) -> int:
        """Process pending update notifications (PM only).

        Reviews and approves valid notifications.

        Returns:
            Number of notifications processed

        Raises:
            PermissionError: If not project_manager
        """
        if not self.can_write:
            raise PermissionError(f"Only project_manager can process notifications, not {self.agent_name}")

        notifications = self.db.get_pending_notifications()
        processed = 0

        for notif in notifications:
            # Auto-approve notifications from trusted agents
            if notif["requested_by"] in ["architect", "code_developer", "code_reviewer"]:
                if self.db.approve_notification(notif["id"], self.agent_name):
                    processed += 1
                    logger.info(f"Approved notification #{notif['id']} from {notif['requested_by']}")

        return processed

    # Implementation tracking methods (for code_developer)
    def claim_work(self, item_id: str) -> bool:
        """Claim a roadmap item for implementation.

        Used by code_developer to mark an item as being actively worked on.
        Tracks start time for stale work detection.

        Args:
            item_id: Item to claim (e.g., "PRIORITY-27")

        Returns:
            True if successfully claimed, False if already claimed
        """
        return self.db.claim_implementation(item_id, self.agent_name)

    def release_work(self, item_id: str) -> bool:
        """Release claim on a roadmap item.

        Called when work completes or is abandoned.

        Args:
            item_id: Item to release

        Returns:
            True if successfully released
        """
        return self.db.release_implementation(item_id, self.agent_name)

    def reset_stale_work(self, stale_hours: int = 24) -> int:
        """Find and reset stale implementations (>24h with no progress).

        This should be called periodically by orchestrator or maintenance task.

        Args:
            stale_hours: Number of hours before considering work stale (default: 24)

        Returns:
            Number of stale implementations reset
        """
        return self.db.reset_stale_implementations(stale_hours)


def get_roadmap_skill(agent_name: str) -> RoadmapDBSkill:
    """Factory function to get roadmap skill for an agent.

    Args:
        agent_name: Name of agent requesting skill

    Returns:
        RoadmapDBSkill instance with appropriate permissions
    """
    return RoadmapDBSkill(agent_name)


# Example usage in agent prompts
ROADMAP_SKILL_USAGE = """
## Using the Roadmap Database Skill

### For All Agents (Read Access):
```python
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

# Initialize with your agent name
roadmap_db = RoadmapDatabase(agent_name="code_developer")

# Get next planned item
next_item = roadmap_db.get_next_planned()
if next_item:
    print(f"Next: {next_item['id']}: {next_item['title']}")

    # Check if it has a spec
    if next_item.get('spec_id'):
        print(f"Spec available: {next_item['spec_id']}")

# Request status update (creates notification for PM)
roadmap_db.create_update_notification(
    item_id="US-062",
    requested_by="code_developer",
    notification_type="status_update",
    requested_status="✅ Complete",
    message="Implementation complete, all tests passing"
)
```

### For project_manager (Write Access):
```python
# Update status directly
roadmap_db.update_status("US-062", "✅ Complete", "project_manager")

# Process notifications from other agents
notifications = roadmap_db.get_pending_notifications()
for notif in notifications:
    if valid:  # Your validation logic
        roadmap_db.approve_notification(notif['id'], "project_manager")
```

### FORBIDDEN Operations:
```python
# NEVER do this - direct file access is FORBIDDEN
with open("docs/roadmap/ROADMAP.md") as f:  # ❌ WRONG
    content = f.read()

# ALWAYS use the database instead
items = roadmap_db.get_all_items()  # ✅ CORRECT
```
"""
