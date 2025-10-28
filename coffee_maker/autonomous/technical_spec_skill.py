"""Technical Specification Skill - Database-only spec storage.

This module provides a unified interface for architect to create and manage
technical specifications stored entirely in the database (NO FILES).

The architect uses this class to:
1. Create hierarchical or monolithic specs in database
2. Store content as JSON (hierarchical) or markdown (monolithic)
3. Create implementation_tasks for parallel execution

Usage:
    from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill

    skill = TechnicalSpecSkill(agent_name="architect")

    # Create hierarchical spec (stored as JSON in database)
    spec_id = skill.create_hierarchical_spec(
        us_number=104,
        title="User Authentication System",
        roadmap_item_id="US-104",
        phases=[
            {
                "name": "database-schema",
                "hours": 2.0,
                "description": "Create User and Session models",
                "content": "## Phase 1: Database Schema\\n\\n### Models\\n..."
            },
            {
                "name": "authentication-logic",
                "hours": 1.5,
                "description": "Implement login/logout logic",
                "content": "## Phase 2: Auth Logic\\n\\n### Login\\n..."
            }
        ],
        problem_statement="Need secure user authentication",
        architecture="JWT-based authentication with refresh tokens"
    )

Author: architect
Date: 2025-10-24 (Refactored to database-only)
Related: PRIORITY 25 Phase 4, Database Schema Guide
"""

import json
import logging
from typing import Dict, List, Optional

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase

logger = logging.getLogger(__name__)


class TechnicalSpecSkill:
    """Database-only technical specification manager.

    This class provides a unified interface for architect to create and manage
    technical specifications stored entirely in the database.

    Key Features:
    - Stores hierarchical specs as JSON in database
    - Stores monolithic specs as markdown in database
    - No file system operations (database-first architecture)
    - Supports progressive disclosure via phase-based content
    """

    def __init__(self, agent_name: str = "architect"):
        """Initialize the skill wrapper.

        Args:
            agent_name: Name of agent using skill (must be "architect")
        """
        self.agent_name = agent_name
        self.db = RoadmapDatabase(agent_name=agent_name)

    def create_hierarchical_spec(
        self,
        us_number: int,
        title: str,
        roadmap_item_id: str,
        phases: List[Dict[str, any]],
        problem_statement: Optional[str] = None,
        architecture: Optional[str] = None,
    ) -> str:
        """Create a hierarchical technical specification.

        This method:
        1. Creates directory structure via skill (file system)
        2. Writes spec entry to database
        3. Links spec to roadmap item

        Args:
            us_number: User story number (e.g., 104)
            title: Spec title
            roadmap_item_id: Roadmap item ID (e.g., "US-104")
            phases: List of phase dicts with keys:
                - name: Phase name (e.g., "database-schema")
                - hours: Estimated hours for phase
                - description: Optional phase description
            problem_statement: What problem does this solve?
            architecture: High-level architecture description

        Returns:
            spec_id: Created spec ID (e.g., "SPEC-104")

        Example:
            >>> skill = TechnicalSpecSkill()
            >>> spec_id = skill.create_hierarchical_spec(
            ...     us_number=104,
            ...     title="Authentication System",
            ...     roadmap_item_id="US-104",
            ...     phases=[
            ...         {"name": "database", "hours": 1},
            ...         {"name": "auth-logic", "hours": 2}
            ...     ]
            ... )
            >>> print(spec_id)
            SPEC-104
        """
        logger.info(f"Creating hierarchical spec (database-only) for US-{us_number}: {title}")

        # Step 1: Build JSON content structure
        total_hours = sum(phase.get("hours", 0) for phase in phases)

        # Add phase numbers
        for i, phase in enumerate(phases, start=1):
            phase["number"] = i

        content_json = {
            "overview": problem_statement or f"Technical specification for {title}",
            "architecture": architecture or "To be determined",
            "phases": phases,
            "total_hours": total_hours,
        }

        content = json.dumps(content_json, indent=2)

        # Step 2: Extract phase names for metadata
        phase_names = [phase["name"] for phase in phases]

        # Step 3: Write to database (NO FILES)
        spec_id = self.db.create_technical_spec(
            spec_number=us_number,
            title=title,
            roadmap_item_id=roadmap_item_id,
            spec_type="hierarchical",
            content=content,  # ✅ JSON stored in database
            file_path=None,  # ❌ No files
            estimated_hours=total_hours,
            total_phases=len(phases),
            phase_files=json.dumps(phase_names),  # Metadata only
        )

        logger.info(f"✅ Created hierarchical spec in database: {spec_id}")
        logger.info(f"   Type: hierarchical (JSON in database)")
        logger.info(f"   Phases: {len(phases)}")
        logger.info(f"   Est. Hours: {total_hours}")
        logger.info(f"   Content Size: {len(content)} chars")

        return spec_id

    def create_monolithic_spec(
        self,
        us_number: int,
        title: str,
        roadmap_item_id: str,
        content: str,
        estimated_hours: Optional[float] = None,
    ) -> str:
        """Create a monolithic (single-file) technical specification.

        Args:
            us_number: User story number
            title: Spec title
            roadmap_item_id: Roadmap item ID
            content: Full spec content
            estimated_hours: Estimated implementation time

        Returns:
            spec_id: Created spec ID

        Example:
            >>> skill = TechnicalSpecSkill()
            >>> spec_id = skill.create_monolithic_spec(
            ...     us_number=105,
            ...     title="Simple Feature",
            ...     roadmap_item_id="US-105",
            ...     content="# SPEC-105\\n\\n...",
            ...     estimated_hours=4.0
            ... )
        """
        logger.info(f"Creating monolithic spec (database-only) for US-{us_number}: {title}")

        # Write to database (NO FILES)
        spec_id = self.db.create_technical_spec(
            spec_number=us_number,
            title=title,
            roadmap_item_id=roadmap_item_id,
            spec_type="monolithic",
            content=content,  # ✅ Markdown stored in database
            file_path=None,  # ❌ No files
            estimated_hours=estimated_hours,
        )

        logger.info(f"✅ Created database entry: {spec_id}")

        return spec_id

    def get_spec(self, roadmap_item_id: str) -> Optional[Dict]:
        """Get spec information from database.

        Args:
            roadmap_item_id: Roadmap item ID (e.g., "US-104")

        Returns:
            Dict with spec information, or None if not found
        """
        return self.db.get_technical_spec(roadmap_item_id=roadmap_item_id)

    def get_phase_content(self, roadmap_item_id: str, phase_number: Optional[int] = None) -> Optional[Dict]:
        """Get content for a specific phase (progressive disclosure).

        Args:
            roadmap_item_id: Roadmap item ID (e.g., "US-104")
            phase_number: Phase to load (None = current phase)

        Returns:
            Dict with:
                - phase: Phase dict with content
                - overview: Spec overview
                - total_phases: Total number of phases
                Or None if not found
        """
        spec = self.db.get_technical_spec(roadmap_item_id=roadmap_item_id)

        if not spec or spec.get("spec_type") != "hierarchical":
            return None

        content_data = json.loads(spec["content"])

        # Determine which phase to load
        if phase_number is None:
            phase_number = int(spec.get("phase", 1))

        # Get the requested phase
        phases = content_data.get("phases", [])
        if phase_number < 1 or phase_number > len(phases):
            return None

        phase = phases[phase_number - 1]

        return {
            "phase": phase,
            "overview": content_data.get("overview"),
            "architecture": content_data.get("architecture"),
            "total_phases": len(phases),
            "current_phase": phase_number,
        }

    def update_spec_phase(self, spec_id: str, current_phase: int, phase_status: str = "in_progress") -> bool:
        """Update current phase for a hierarchical spec.

        Args:
            spec_id: Spec ID (e.g., "SPEC-104")
            current_phase: Phase number (1-indexed)
            phase_status: "in_progress" or "completed"

        Returns:
            bool: True if updated successfully
        """
        return self.db.update_technical_spec(spec_id=spec_id, current_phase=current_phase, phase_status=phase_status)
