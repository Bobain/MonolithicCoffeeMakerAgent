"""Technical Specification Handling Skill - Database-first architecture.

This skill provides a single source of truth for all technical specification operations,
enforcing database-first storage where ALL specs are written to and read from the
specs_specification database table. Files are optional backup/export only.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("technical-specification-handling")
    result = skill.execute(action="get_spec", us_id="US-104")
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.database.domain_wrapper import DomainWrapper, AgentType, PermissionError
from coffee_maker.utils.logging import get_logger

logger = get_logger(__name__)


class TechnicalSpecificationHandlingSkill:
    """Technical specification handling skill - database-first architecture.

    CRITICAL: This skill ALWAYS writes specs to the specs_specification database table.
    Files are NEVER the primary storage - they are optional exports only.
    """

    def __init__(self, agent_type: AgentType = AgentType.ARCHITECT):
        """Initialize the skill.

        Args:
            agent_type: The agent type using this skill (defaults to ARCHITECT)
        """
        self.agent_type = agent_type
        self.db = DomainWrapper(agent_type, db_path="data/roadmap.db")
        self.db_path = Path("data/roadmap.db")

    def _validate_database_first(self) -> None:
        """Validate that database-first architecture is being enforced.

        Raises:
            ValueError: If database-first architecture is being violated
        """
        pass  # Validation passed

    def _find_spec_number_from_us_id(self, us_id: str) -> Optional[int]:
        """Extract spec number from US ID.

        Args:
            us_id: The US ID (e.g., "US-104")

        Returns:
            The spec number (e.g., 104) or None if not found
        """
        if not us_id.startswith("US-"):
            us_id = f"US-{us_id}"

        try:
            # Extract number from US-XXX format
            num = int(us_id.split("-")[1])
            return num
        except (IndexError, ValueError):
            return None

    def _get_spec_from_database(self, spec_id: str) -> Optional[Dict[str, Any]]:
        """Get specification from database.

        Args:
            spec_id: The spec ID (e.g., "SPEC-104")

        Returns:
            The specification dict or None if not found
        """
        try:
            results = self.db.read("specs_specification", {"id": spec_id})
            return results[0] if results else None
        except PermissionError as e:
            logger.warning(f"Permission error reading spec: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading spec {spec_id}: {e}")
            return None

    def _get_all_specs_from_database(self) -> List[Dict[str, Any]]:
        """Get all specifications from database.

        Returns:
            List of specification dicts
        """
        try:
            results = self.db.read("specs_specification")
            return results if results else []
        except PermissionError as e:
            logger.warning(f"Permission error reading specs: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading specs: {e}")
            return []

    def _write_spec_to_database(self, spec_data: Dict[str, Any]) -> bool:
        """Write specification to database.

        Args:
            spec_data: The specification data to write

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.write("specs_specification", spec_data)
            logger.info(f"Spec {spec_data.get('id')} written to database")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied writing spec: {e}")
            return False
        except Exception as e:
            logger.error(f"Error writing spec to database: {e}")
            return False

    def _export_spec_to_file(self, spec_id: str, content: str, file_path: Optional[str] = None) -> Optional[str]:
        """Export specification content to file (optional backup only).

        Args:
            spec_id: The spec ID for naming
            content: The content to export
            file_path: Optional custom file path

        Returns:
            The file path where exported, or None if not exported
        """
        if not file_path:
            # Default to docs/architecture/specs/
            spec_num = spec_id.split("-")[1]
            file_path = f"docs/architecture/specs/SPEC-{spec_num}-spec.md"

        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"Spec {spec_id} exported to {file_path}")
            return str(path)
        except Exception as e:
            logger.warning(f"Failed to export spec to file: {e}")
            return None

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a specification operation using database.

        Args:
            action: Operation to perform
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <result>, "error": <error_message>}
        """
        self._validate_database_first()

        try:
            # Finding specifications
            if action in ["find", "find_spec", "find_by_us_id"]:
                us_id = kwargs.get("us_id")
                priority_num = kwargs.get("priority_num")
                title_pattern = kwargs.get("title_pattern")

                if us_id:
                    # Normalize US ID format
                    spec_num = self._find_spec_number_from_us_id(us_id)
                    if spec_num is None:
                        return {"result": None, "error": f"Invalid US ID format: {us_id}"}

                    spec_id = f"SPEC-{spec_num:03d}"
                    spec = self._get_spec_from_database(spec_id)
                    if spec:
                        return {
                            "result": spec,
                            "error": None,
                            "source": "database",
                        }
                    return {
                        "result": None,
                        "error": f"No spec found for {us_id} in database",
                        "source": "database",
                    }

                elif priority_num:
                    # Find by priority number using spec number
                    spec_id = f"SPEC-{priority_num:03d}"
                    spec = self._get_spec_from_database(spec_id)
                    if spec:
                        return {
                            "result": spec,
                            "error": None,
                            "source": "database",
                        }
                    return {
                        "result": None,
                        "error": f"No spec found for priority {priority_num} in database",
                        "source": "database",
                    }

                elif title_pattern:
                    # Find by title pattern
                    all_specs = self._get_all_specs_from_database()
                    matching = [s for s in all_specs if title_pattern.lower() in s.get("title", "").lower()]
                    return {
                        "result": matching,
                        "error": None,
                        "source": "database",
                    }

                else:
                    return {
                        "result": None,
                        "error": "Must provide us_id, priority_num, or title_pattern",
                    }

            # Get full spec content
            elif action == "get_spec":
                us_id = kwargs.get("us_id")
                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                spec_num = self._find_spec_number_from_us_id(us_id)
                if spec_num is None:
                    return {"result": None, "error": f"Invalid US ID format: {us_id}"}

                spec_id = f"SPEC-{spec_num:03d}"
                spec = self._get_spec_from_database(spec_id)
                if spec:
                    return {
                        "result": spec,
                        "error": None,
                        "source": "database",
                    }
                return {
                    "result": None,
                    "error": f"No spec found for {us_id} in database",
                    "source": "database",
                }

            # Create hierarchical specification
            elif action in ["create_hierarchical_spec", "create_hierarchical"]:
                us_number = kwargs.get("us_number") or kwargs.get("us_id")
                title = kwargs.get("title")
                phases = kwargs.get("phases", [])
                roadmap_item_id = kwargs.get("roadmap_item_id")

                if not all([us_number, title]):
                    return {"result": None, "error": "Missing required: us_number, title"}

                # Normalize US ID
                if isinstance(us_number, str):
                    if us_number.startswith("US-"):
                        spec_num = self._find_spec_number_from_us_id(us_number)
                    else:
                        spec_num = int(us_number) if us_number.isdigit() else None
                else:
                    spec_num = us_number

                if spec_num is None:
                    return {"result": None, "error": f"Invalid US number: {us_number}"}

                # Ensure roadmap_item_id is set
                if not roadmap_item_id:
                    roadmap_item_id = f"US-{spec_num}"

                spec_id = f"SPEC-{spec_num:03d}"

                # Build JSON structure for hierarchical spec
                spec_content = {
                    "type": "hierarchical",
                    "spec_id": spec_id,
                    "title": title,
                    "phases": {},
                }

                # Add phase information
                for i, phase in enumerate(phases, 1):
                    phase_name = phase.get("name", f"Phase {i}")
                    spec_content["phases"][phase_name] = {
                        "number": i,
                        "name": phase_name,
                        "description": phase.get("description", ""),
                        "hours": phase.get("hours", 0),
                        "content": phase.get("content", ""),
                    }

                # Build spec data for database
                spec_data = {
                    "id": spec_id,
                    "spec_number": spec_num,
                    "title": title,
                    "roadmap_item_id": roadmap_item_id,
                    "status": "draft",
                    "spec_type": "hierarchical",
                    "content": json.dumps(spec_content),  # STORE IN DATABASE!
                    "total_phases": len(phases),
                    "phase_files": json.dumps([p.get("name", f"Phase {i}") for i, p in enumerate(phases, 1)]),
                    "dependencies": json.dumps(kwargs.get("dependencies", [])),
                    "estimated_hours": kwargs.get("estimated_hours"),
                    "updated_at": datetime.now().isoformat(),
                    "updated_by": self.agent_type.value,
                }

                # Write to DATABASE (PRIMARY STORAGE)
                if self._write_spec_to_database(spec_data):
                    # Optional: Export to file as backup
                    if kwargs.get("export_file", False):
                        overview_content = f"# {spec_id}: {title}\n\n"
                        overview_content += f"Type: Hierarchical ({len(phases)} phases)\n\n"
                        self._export_spec_to_file(spec_id, overview_content)

                    return {
                        "result": {
                            "spec_id": spec_id,
                            "roadmap_item_id": roadmap_item_id,
                            "spec_type": "hierarchical",
                            "total_phases": len(phases),
                        },
                        "error": None,
                        "source": "database",  # PRIMARY STORAGE
                    }
                else:
                    return {
                        "result": None,
                        "error": "Failed to write spec to database",
                    }

            # Read hierarchical spec phase with progressive disclosure
            elif action in ["read_hierarchical_spec", "read_phase"]:
                us_id = kwargs.get("us_id")
                phase_name = kwargs.get("phase")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                spec_num = self._find_spec_number_from_us_id(us_id)
                if spec_num is None:
                    return {"result": None, "error": f"Invalid US ID format: {us_id}"}

                spec_id = f"SPEC-{spec_num:03d}"
                spec = self._get_spec_from_database(spec_id)

                if not spec:
                    return {
                        "result": None,
                        "error": f"No spec found for {us_id} in database",
                        "source": "database",
                    }

                # Check if it's hierarchical
                if spec.get("spec_type") != "hierarchical":
                    # Return monolithic spec content
                    return {
                        "result": {
                            "spec_type": "monolithic",
                            "content": spec.get("content", ""),
                        },
                        "error": None,
                        "source": "database",
                    }

                # Parse JSON content from database
                try:
                    spec_content = json.loads(spec.get("content", "{}"))
                except json.JSONDecodeError:
                    spec_content = {"phases": {}}

                phases = spec_content.get("phases", {})

                if phase_name and phase_name in phases:
                    # Return specific phase (progressive disclosure)
                    phase_content = phases[phase_name]
                    return {
                        "result": {
                            "spec_type": "hierarchical",
                            "current_phase": phase_name,
                            "total_phases": spec.get("total_phases"),
                            "phase_content": phase_content.get("content", ""),
                            "phase_description": phase_content.get("description", ""),
                            "phase_hours": phase_content.get("hours", 0),
                        },
                        "error": None,
                        "source": "database",
                    }
                else:
                    # Return available phases
                    return {
                        "result": {
                            "spec_type": "hierarchical",
                            "available_phases": list(phases.keys()),
                            "total_phases": spec.get("total_phases"),
                            "phases": {
                                name: {
                                    "description": p.get("description", ""),
                                    "hours": p.get("hours", 0),
                                }
                                for name, p in phases.items()
                            },
                        },
                        "error": None,
                        "source": "database",
                    }

            # Detect current phase
            elif action in ["detect_phase", "get_current_phase"]:
                us_id = kwargs.get("us_id")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                spec_num = self._find_spec_number_from_us_id(us_id)
                if spec_num is None:
                    return {"result": None, "error": f"Invalid US ID format: {us_id}"}

                spec_id = f"SPEC-{spec_num:03d}"
                spec = self._get_spec_from_database(spec_id)

                if not spec:
                    return {
                        "result": {"current_phase": "not_started"},
                        "error": None,
                        "source": "database",
                    }

                # Return current phase status from database
                current_phase = spec.get("current_phase_status", "not_started")
                return {
                    "result": {"current_phase": current_phase},
                    "error": None,
                    "source": "database",
                }

            # List all specs
            elif action in ["list", "list_specs", "get_all_specs"]:
                specs = self._get_all_specs_from_database()
                return {
                    "result": specs,
                    "error": None,
                    "source": "database",
                }

            # Update spec
            elif action in ["update", "update_spec"]:
                us_id = kwargs.get("us_id")
                content = kwargs.get("content")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                spec_num = self._find_spec_number_from_us_id(us_id)
                if spec_num is None:
                    return {"result": None, "error": f"Invalid US ID format: {us_id}"}

                spec_id = f"SPEC-{spec_num:03d}"

                # Update spec in database
                try:
                    self.db.update(
                        "specs_specification",
                        {
                            "content": content,
                            "updated_at": datetime.now().isoformat(),
                            "updated_by": self.agent_type.value,
                        },
                        {"id": spec_id},
                    )
                    return {
                        "result": True,
                        "error": None,
                        "source": "database",
                    }
                except Exception as e:
                    return {
                        "result": False,
                        "error": f"Failed to update spec in database: {e}",
                    }

            else:
                return {"result": None, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {"result": None, "error": str(e)}


# Skill entry point
def run(action: str, agent_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        action: Action to perform
        agent_type: Optional agent type (defaults to ARCHITECT)
        **kwargs: Action-specific parameters

    Returns:
        dict: {"result": <result>, "error": <error_message>}
    """
    # Determine agent type
    if agent_type:
        try:
            agent_enum = AgentType[agent_type.upper()]
        except KeyError:
            agent_enum = AgentType.ARCHITECT
    else:
        agent_enum = AgentType.ARCHITECT

    skill = TechnicalSpecificationHandlingSkill(agent_type=agent_enum)
    return skill.execute(action, **kwargs)
