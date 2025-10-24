"""Technical Specification Skill - Unified interface for architect.

This module provides a Python interface to the technical-specification-handling
skill, integrating both file system operations and database persistence.

The architect uses this class to:
1. Create hierarchical or monolithic specs
2. Write specs to both database AND file system
3. Maintain synchronization between database and files

Usage:
    from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill

    skill = TechnicalSpecSkill(agent_name="architect")

    # Create hierarchical spec
    spec_id = skill.create_hierarchical_spec(
        us_number=104,
        title="User Authentication System",
        roadmap_item_id="US-104",
        phases=[
            {"name": "database-schema", "hours": 1},
            {"name": "authentication-logic", "hours": 1.5}
        ]
    )

Author: architect
Date: 2025-10-24
Related: PRIORITY 25 Phase 4
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.autonomous.roadmap_database import RoadmapDatabase
from coffee_maker.utils.spec_handler import SpecHandler

logger = logging.getLogger(__name__)


class TechnicalSpecSkill:
    """Unified interface for creating and managing technical specifications.

    This class wraps the technical-specification-handling skill and integrates
    it with RoadmapDatabase for full database persistence.

    Key Features:
    - Creates hierarchical spec directories via skill
    - Persists spec metadata to database
    - Maintains sync between file system and database
    - Supports both hierarchical and monolithic specs
    """

    def __init__(self, agent_name: str = "architect"):
        """Initialize the skill wrapper.

        Args:
            agent_name: Name of agent using skill (must be "architect")
        """
        self.agent_name = agent_name
        self.db = RoadmapDatabase(agent_name=agent_name)
        self.handler = SpecHandler()

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
        logger.info(f"Creating hierarchical spec for US-{us_number}: {title}")

        # Step 1: Create directory structure via SpecHandler
        spec_dir = self.handler.create_hierarchical_spec(
            us_number=str(us_number),
            title=title,
            phases=phases,
            problem_statement=problem_statement or "",
            architecture=architecture or "",
        )

        if not spec_dir or not spec_dir.exists():
            raise RuntimeError(f"Failed to create spec directory: {spec_dir}")

        logger.info(f"✅ Created spec directory: {spec_dir}")

        # Step 2: Calculate metadata
        total_hours = sum(phase.get("hours", 0) for phase in phases)
        phase_files = [f"phase{i+1}-{phase['name']}.md" for i, phase in enumerate(phases)]

        # Step 3: Read README.md content for database
        readme_path = Path(spec_dir) / "README.md"
        readme_content = readme_path.read_text() if readme_path.exists() else None

        # Step 4: Write to database
        spec_id = self.db.create_technical_spec(
            spec_number=us_number,
            title=title,
            roadmap_item_id=roadmap_item_id,
            spec_type="hierarchical",
            file_path=str(spec_dir),
            content=readme_content,
            estimated_hours=total_hours,
            total_phases=len(phases),
            phase_files=phase_files,
        )

        logger.info(f"✅ Created database entry: {spec_id}")
        logger.info(f"   Type: hierarchical")
        logger.info(f"   Phases: {len(phases)}")
        logger.info(f"   Est. Hours: {total_hours}")

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
        logger.info(f"Creating monolithic spec for US-{us_number}: {title}")

        # Create file
        spec_file = Path(f"docs/architecture/specs/SPEC-{us_number:03d}-{self.handler._slugify(title)}.md")
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        spec_file.write_text(content)

        logger.info(f"✅ Created spec file: {spec_file}")

        # Write to database
        spec_id = self.db.create_technical_spec(
            spec_number=us_number,
            title=title,
            roadmap_item_id=roadmap_item_id,
            spec_type="monolithic",
            file_path=str(spec_file),
            content=content,
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
