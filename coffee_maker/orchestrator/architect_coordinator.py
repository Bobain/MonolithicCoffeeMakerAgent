"""Architect Coordinator for proactive spec creation.

This module coordinates the architect agent to maintain a backlog of 2-3 specs
ahead of code_developer, ensuring zero blocking waits for technical specifications.

Architecture:
    - Identifies priorities that need specs
    - Maintains spec backlog target (default: 3 specs ahead)
    - Tracks spec creation progress
    - Ensures CFR-011 compliance (architect reads code-searcher reports)

Related:
    SPEC-104: Technical specification
    US-104: Strategic requirement (PRIORITY 20)
"""

import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ArchitectCoordinator:
    """
    Coordinates architect agent for proactive spec creation.

    Responsibilities:
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Prioritize spec creation by ROADMAP order
    - Track spec creation progress
    - Ensure CFR-011 compliance (architect reads code-searcher reports)
    """

    def __init__(self, spec_backlog_target: int = 3):
        """
        Initialize ArchitectCoordinator.

        Args:
            spec_backlog_target: Number of specs to keep ahead of code_developer
        """
        self.spec_backlog_target = spec_backlog_target

    def get_missing_specs(self, priorities: List[Dict]) -> List[Dict]:
        """
        Identify priorities that need specs.

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of priorities missing specs, sorted by priority number
        """
        missing = []

        for priority in priorities:
            if not self._has_spec(priority):
                missing.append(priority)

        return sorted(missing, key=lambda p: p["number"])

    def _has_spec(self, priority: Dict) -> bool:
        """
        Check if technical spec exists for priority.

        Args:
            priority: Priority dict

        Returns:
            True if spec exists, False otherwise
        """
        # Extract US number (e.g., "US-104 - Title" → "104")
        us_number = priority["us_number"].split("-")[1]

        spec_pattern = f"SPEC-{us_number}-*.md"
        spec_path = Path("docs/architecture/specs")

        return len(list(spec_path.glob(spec_pattern))) > 0

    def create_spec_backlog(self, priorities: List[Dict]) -> List[str]:
        """
        Create spec backlog (identify first N missing specs).

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of task IDs for specs that should be created
        """
        missing_specs = self.get_missing_specs(priorities)[: self.spec_backlog_target]

        task_ids = []

        for priority in missing_specs:
            task_id = f"spec-{priority['number']}"
            task_ids.append(task_id)

            logger.info(f"📋 Queued spec creation: PRIORITY {priority['number']} (task: {task_id})")

        return task_ids
