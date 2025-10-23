"""Technical Specification Database Integration for architect.

This module extends the technical_specification_handling skill to integrate
with the spec database for tracking and managing specifications.

Access Control:
    - Write access: architect only
    - Read access: All agents

Example usage in architect:
    >>> from coffee_maker.autonomous.spec_database import SpecDatabase
    >>>
    >>> # Initialize database
    >>> db = SpecDatabase()
    >>>
    >>> # When creating a new spec
    >>> spec_id = db.create_spec(
    ...     spec_number=115,
    ...     title="New Feature Implementation",
    ...     roadmap_item_id="PRIORITY-28",
    ...     spec_type="hierarchical",
    ...     file_path="docs/architecture/specs/SPEC-115-new-feature/",
    ...     estimated_hours=6.0,
    ...     created_by="architect"
    ... )
    >>>
    >>> # Update status when working on spec
    >>> db.update_status(spec_id, "in_progress", "architect")
    >>>
    >>> # Mark complete when done
    >>> db.update_status(spec_id, "complete", "architect", actual_hours=5.5)

Example usage in other agents (read-only):
    >>> from coffee_maker.autonomous.spec_database import SpecDatabase
    >>>
    >>> # Initialize database
    >>> db = SpecDatabase()
    >>>
    >>> # Find specs for a roadmap item
    >>> specs = db.get_specs_for_roadmap_item("PRIORITY-28")
    >>> for spec in specs:
    ...     print(f"{spec['id']}: {spec['title']} - {spec['status']}")
    >>>
    >>> # Check if spec exists for a priority
    >>> spec = db.find_spec_by_number(115)
    >>> if spec and spec['status'] == 'complete':
    ...     print(f"Spec ready: {spec['file_path']}")
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from coffee_maker.autonomous.spec_database import SpecDatabase

logger = logging.getLogger(__name__)


class SpecDatabaseIntegration:
    """Integration layer between technical specs and the database.

    This class provides high-level operations for managing specs in both
    the filesystem and database, maintaining consistency between both.
    """

    def __init__(self, agent_name: str = "unknown"):
        """Initialize spec database integration.

        Args:
            agent_name: Name of the agent using this integration
        """
        self.agent_name = agent_name
        self.db = SpecDatabase()
        self.specs_dir = Path("docs/architecture/specs")

        # Check write permission
        self.can_write = agent_name == "architect"

        if not self.can_write and agent_name != "unknown":
            logger.info(f"Agent {agent_name} has read-only access to spec database")

    def create_spec_with_tracking(
        self,
        spec_number: int,
        title: str,
        roadmap_item_id: str,
        content: str,
        spec_type: str = "monolithic",
        dependencies: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
    ) -> Tuple[str, Path]:
        """Create a new spec file and track it in the database.

        Args:
            spec_number: Spec number (e.g., 115)
            title: Spec title
            roadmap_item_id: Related roadmap item
            content: Full markdown content
            spec_type: "monolithic" or "hierarchical"
            dependencies: List of spec IDs this depends on
            estimated_hours: Total effort estimate

        Returns:
            Tuple of (spec_id, file_path)

        Raises:
            PermissionError: If agent is not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can create specs, not {self.agent_name}")

        # Generate filename
        slug = title.lower().replace(" ", "-")[:50]  # Limit length

        if spec_type == "hierarchical":
            # Create directory for hierarchical spec
            spec_path = self.specs_dir / f"SPEC-{spec_number}-{slug}"
            spec_path.mkdir(parents=True, exist_ok=True)

            # Write README.md
            readme_path = spec_path / "README.md"
            readme_path.write_text(content)

            file_path = spec_path
        else:
            # Create single file for monolithic spec
            spec_path = self.specs_dir / f"SPEC-{spec_number}-{slug}.md"
            spec_path.parent.mkdir(parents=True, exist_ok=True)
            spec_path.write_text(content)

            file_path = spec_path

        # Track in database
        spec_id = self.db.create_spec(
            spec_number=spec_number,
            title=title,
            roadmap_item_id=roadmap_item_id,
            spec_type=spec_type,
            file_path=str(file_path),
            dependencies=dependencies,
            estimated_hours=estimated_hours,
            created_by=self.agent_name,
        )

        logger.info(f"✅ Created and tracked {spec_id} at {file_path}")
        return spec_id, file_path

    def find_spec_for_priority(self, priority: Dict) -> Optional[Dict]:
        """Find spec for a priority/user story.

        Args:
            priority: Dict with keys:
                - "number": Priority number
                - "title": Title (may contain US-XXX)
                - "name": Name (e.g., "US-104" or "PRIORITY 20")

        Returns:
            Spec dictionary with database info, or None if not found
        """
        # Extract US number if present
        import re

        us_match = re.search(r"US-(\d+)", priority.get("title", ""))

        if us_match:
            us_number = int(us_match.group(1))
            spec = self.db.find_spec_by_number(us_number)
            if spec:
                return spec

        # Try priority-based lookup
        priority_num = priority.get("number", "").replace(".", "")
        try:
            spec_number = int(priority_num)
            spec = self.db.find_spec_by_number(spec_number)
            if spec:
                return spec
        except (ValueError, TypeError):
            pass

        # Search by roadmap item ID
        roadmap_id = priority.get("name", "")
        if roadmap_id:
            specs = self.db.get_specs_for_roadmap_item(roadmap_id)
            if specs:
                return specs[0]  # Return first match

        return None

    def update_spec_status(self, spec_id: str, new_status: str, actual_hours: Optional[float] = None) -> bool:
        """Update spec status in database.

        Args:
            spec_id: Spec ID (e.g., "SPEC-115")
            new_status: New status ('draft', 'in_progress', 'complete', 'approved')
            actual_hours: Actual effort (when marking complete)

        Returns:
            True if successful

        Raises:
            PermissionError: If agent is not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can update specs, not {self.agent_name}")

        success = self.db.update_status(
            spec_id=spec_id, new_status=new_status, updated_by=self.agent_name, actual_hours=actual_hours
        )

        # Notify project_manager if spec is complete and needs roadmap update
        if success and new_status == "complete":
            self._notify_project_manager_roadmap_update(spec_id, "spec_complete")

        return success

    def get_spec_summary(self) -> Dict:
        """Get summary statistics about specs.

        Returns:
            Dictionary with statistics
        """
        stats = self.db.get_spec_stats()

        # Add completion percentage
        total = stats.get("total_specs", 0)
        complete = stats.get("status_counts", {}).get("complete", 0)

        if total > 0:
            stats["completion_percentage"] = (complete / total) * 100
        else:
            stats["completion_percentage"] = 0

        return stats

    def check_spec_exists(self, spec_number: int) -> bool:
        """Check if a spec exists in the database.

        Args:
            spec_number: Spec number to check

        Returns:
            True if spec exists
        """
        spec = self.db.find_spec_by_number(spec_number)
        return spec is not None

    def get_pending_specs(self) -> List[Dict]:
        """Get all specs that need work (draft or in_progress).

        Returns:
            List of spec dictionaries
        """
        drafts = self.db.get_specs_by_status("draft")
        in_progress = self.db.get_specs_by_status("in_progress")

        return drafts + in_progress

    def sync_filesystem_to_database(self) -> Tuple[int, int]:
        """Sync existing filesystem specs to database.

        This is useful for importing specs created before the database existed.

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        if not self.can_write:
            raise PermissionError("Only architect can sync specs to database")

        return self.db.import_existing_specs()

    def _notify_project_manager_roadmap_update(self, spec_id: str, notification_type: str) -> None:
        """Send notification to project_manager about roadmap update needed.

        This creates a notification that project_manager will see and act upon.

        Args:
            spec_id: Spec ID that triggered the notification
            notification_type: Type of notification (e.g., "spec_complete", "spec_ready")
        """
        try:
            # Import roadmap database to create notification
            from coffee_maker.autonomous.roadmap_database_v2 import RoadmapDatabaseV2

            roadmap_db = RoadmapDatabaseV2(agent_name=self.agent_name)

            # Find the spec details
            spec = self.db.find_spec_by_id(spec_id)
            if not spec:
                logger.warning(f"Could not find spec {spec_id} to notify about")
                return

            # Create notification for project_manager
            notification_id = roadmap_db.create_update_notification(
                item_id=spec.get("roadmap_item_id", "UNKNOWN"),
                requested_by="architect",
                notification_type="status_update",
                requested_status="🔄 In Progress" if notification_type == "spec_complete" else None,
                message=f"Technical specification {spec_id} is complete and ready for implementation. "
                f"Please update the roadmap item {spec.get('roadmap_item_id', '')} status accordingly.",
            )

            logger.info(f"✅ Notified project_manager about {spec_id} completion (notification #{notification_id})")

        except ImportError:
            logger.warning("RoadmapDatabaseV2 not available yet, skipping notification")
        except Exception as e:
            logger.error(f"Failed to notify project_manager: {e}")


# Skill integration function for use in prompts
def invoke_spec_database(action: str, **kwargs) -> Dict:
    """Main entry point for spec database operations.

    Args:
        action: Operation to perform:
            - "create": Create new spec with tracking
            - "find": Find spec for priority
            - "update_status": Update spec status
            - "get_stats": Get statistics
            - "get_pending": Get specs needing work
            - "check_exists": Check if spec exists
            - "sync": Import filesystem specs to database
        **kwargs: Arguments for the specific action

    Returns:
        Result dictionary based on action
    """
    agent_name = kwargs.get("agent_name", "unknown")
    integration = SpecDatabaseIntegration(agent_name)

    if action == "create":
        if not integration.can_write:
            return {"success": False, "error": "Only architect can create specs"}

        spec_id, file_path = integration.create_spec_with_tracking(
            spec_number=kwargs["spec_number"],
            title=kwargs["title"],
            roadmap_item_id=kwargs.get("roadmap_item_id", ""),
            content=kwargs["content"],
            spec_type=kwargs.get("spec_type", "monolithic"),
            dependencies=kwargs.get("dependencies"),
            estimated_hours=kwargs.get("estimated_hours"),
        )
        return {"success": True, "spec_id": spec_id, "file_path": str(file_path)}

    elif action == "find":
        spec = integration.find_spec_for_priority(kwargs["priority"])
        return {"success": spec is not None, "spec": spec}

    elif action == "update_status":
        if not integration.can_write:
            return {"success": False, "error": "Only architect can update specs"}

        success = integration.update_spec_status(
            spec_id=kwargs["spec_id"], new_status=kwargs["status"], actual_hours=kwargs.get("actual_hours")
        )
        return {"success": success}

    elif action == "get_stats":
        stats = integration.get_spec_summary()
        return {"success": True, "stats": stats}

    elif action == "get_pending":
        specs = integration.get_pending_specs()
        return {"success": True, "specs": specs}

    elif action == "check_exists":
        exists = integration.check_spec_exists(kwargs["spec_number"])
        return {"success": True, "exists": exists}

    elif action == "sync":
        if not integration.can_write:
            return {"success": False, "error": "Only architect can sync specs"}

        imported, skipped = integration.sync_filesystem_to_database()
        return {"success": True, "imported": imported, "skipped": skipped}

    else:
        return {"success": False, "error": f"Unknown action: {action}"}
