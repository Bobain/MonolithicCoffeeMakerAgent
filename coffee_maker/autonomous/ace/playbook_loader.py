"""Playbook loading and saving utilities for ACE framework.

This module provides utilities for loading and saving agent playbooks to/from disk.
Supports JSON serialization with thread-safe file operations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from coffee_maker.autonomous.ace.config import ACEConfig, get_default_config
from coffee_maker.autonomous.ace.models import HealthMetrics, Playbook
from coffee_maker.utils.file_io import write_json_file

logger = logging.getLogger(__name__)


class PlaybookLoader:
    """Load and save agent playbooks."""

    def __init__(self, agent_name: str, config: Optional[ACEConfig] = None):
        """Initialize playbook loader.

        Args:
            agent_name: Name of the agent (e.g., "code_developer")
            config: ACE configuration (optional)
        """
        self.agent_name = agent_name
        self.config = config or get_default_config()
        self.playbook_path = self.config.playbook_dir / f"{agent_name}_playbook.json"

    def load(self) -> Playbook:
        """Load playbook from disk or create default.

        Returns:
            Playbook instance (loaded or default)
        """
        if self.playbook_path.exists():
            try:
                logger.info(f"Loading playbook from {self.playbook_path}")
                with open(self.playbook_path, "r") as f:
                    data = json.load(f)
                return Playbook.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load playbook: {e}, creating default")
                return self._create_default_playbook()
        else:
            logger.info(f"No playbook found at {self.playbook_path}, creating default")
            return self._create_default_playbook()

    def save(self, playbook: Playbook) -> Path:
        """Save playbook to disk.

        Uses atomic write (temp file + rename) for thread safety.

        Args:
            playbook: Playbook to save

        Returns:
            Path where playbook was saved
        """
        # Ensure directory exists
        self.config.playbook_dir.mkdir(parents=True, exist_ok=True)

        # Update playbook metadata
        playbook.last_updated = datetime.now()

        # Use utility function for atomic write
        write_json_file(self.playbook_path, playbook.to_dict())

        logger.info(f"Saved playbook to {self.playbook_path}")
        return self.playbook_path

    def to_markdown(self, playbook: Playbook) -> str:
        """Convert playbook to markdown format.

        Args:
            playbook: Playbook to convert

        Returns:
            Markdown string
        """
        lines = [
            f"# Playbook: {playbook.agent_name}",
            "",
            f"**Version**: {playbook.playbook_version}",
            f"**Last Updated**: {playbook.last_updated.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Bullets**: {playbook.total_bullets}",
            f"**Effectiveness Score**: {playbook.effectiveness_score:.2f}",
            "",
            "## Agent Identity",
            "",
            f"**Objective**: {playbook.agent_objective}",
            "",
            f"**Success Criteria**: {playbook.success_criteria}",
            "",
        ]

        # Add health metrics if available
        if playbook.health_metrics:
            metrics = playbook.health_metrics
            lines.extend(
                [
                    "## Health Metrics",
                    "",
                    f"- **Total Bullets**: {metrics.total_bullets}",
                    f"- **Average Helpful Count**: {metrics.avg_helpful_count:.2f}",
                    f"- **Effectiveness Ratio**: {metrics.effectiveness_ratio:.2f}",
                    f"- **Coverage Score**: {metrics.coverage_score:.2f}",
                    "",
                    "**This Session**:",
                    f"- Added: {metrics.bullets_added_this_session}",
                    f"- Updated: {metrics.bullets_updated_this_session}",
                    f"- Pruned: {metrics.bullets_pruned_this_session}",
                    "",
                ]
            )

        # Add bullets by category
        lines.append("## Bullets by Category")
        lines.append("")

        for category, bullets in sorted(playbook.categories.items()):
            lines.append(f"### {category}")
            lines.append("")

            # Sort bullets by priority (higher first), then confidence
            sorted_bullets = sorted(bullets, key=lambda b: (-b.priority, -b.confidence, -b.helpful_count))

            for bullet in sorted_bullets:
                if bullet.deprecated:
                    continue

                # Format: - [Priority] Content (confidence: X%, helpful: Y)
                confidence_pct = int(bullet.confidence * 100)
                lines.append(
                    f"- **[P{bullet.priority}]** {bullet.content} "
                    f"(confidence: {confidence_pct}%, helpful: {bullet.helpful_count})"
                )

            lines.append("")

        # Add statistics
        if playbook.statistics:
            lines.extend(["## Statistics", ""])
            for key, value in sorted(playbook.statistics.items()):
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def from_markdown(self, markdown: str) -> Playbook:
        """Parse playbook from markdown (optional, not implemented).

        Args:
            markdown: Markdown string to parse

        Returns:
            Playbook instance

        Raises:
            NotImplementedError: Markdown parsing not yet implemented
        """
        raise NotImplementedError("Markdown parsing not yet implemented. Use JSON format.")

    def _create_default_playbook(self) -> Playbook:
        """Create a new empty playbook.

        Returns:
            Default Playbook instance
        """
        return Playbook(
            playbook_version="1.0",
            agent_name=self.agent_name,
            agent_objective=f"Objectives for {self.agent_name}",
            success_criteria=f"Success criteria for {self.agent_name}",
            last_updated=datetime.now(),
            total_bullets=0,
            effectiveness_score=0.0,
            categories={},
            statistics={},
            health_metrics=HealthMetrics(),
            history=[],
        )
