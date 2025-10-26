"""Technical Specification Handling Skill - Database-based spec operations.

This skill provides a single source of truth for all technical specification operations,
using the database-first architecture for storing and retrieving specifications.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("technical-specification-handling")
    result = skill.execute(action="get_spec", us_id="US-104")
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase


class TechnicalSpecificationHandlingSkill:
    """Technical specification handling skill - database-based."""

    def __init__(self):
        """Initialize the skill."""
        self.spec_skill = TechnicalSpecSkill(agent_name="shared")
        self.db = RoadmapDatabase(agent_name="shared")

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a specification operation using database.

        Args:
            action: Operation to perform
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <result>, "error": <error_message>}
        """
        try:
            # Finding specifications
            if action in ["find", "find_spec", "find_by_us_id"]:
                us_id = kwargs.get("us_id")
                priority_num = kwargs.get("priority_num")
                title_pattern = kwargs.get("title_pattern")

                if us_id:
                    # Normalize US ID format
                    if not us_id.startswith("US-"):
                        us_id = f"US-{us_id}"
                    spec = self.db.get_technical_spec(us_id)
                    if spec:
                        return {"result": spec, "error": None}
                    return {"result": None, "error": f"No spec found for {us_id}"}

                elif priority_num:
                    # Find by priority number
                    priorities = self.db.get_all_priorities()
                    for p in priorities:
                        if str(p.get("number")) == str(priority_num):
                            us_id = p.get("id", "")
                            if us_id:
                                spec = self.db.get_technical_spec(us_id)
                                if spec:
                                    return {"result": spec, "error": None}
                    return {"result": None, "error": f"No spec found for priority {priority_num}"}

                elif title_pattern:
                    # Find by title pattern
                    specs = self.db.get_all_technical_specs()
                    matching = [s for s in specs if title_pattern.lower() in s.get("title", "").lower()]
                    return {"result": matching, "error": None}

                else:
                    return {"result": None, "error": "Must provide us_id, priority_num, or title_pattern"}

            # Get full spec content
            elif action == "get_spec":
                us_id = kwargs.get("us_id")
                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                if not us_id.startswith("US-"):
                    us_id = f"US-{us_id}"

                spec = self.db.get_technical_spec(us_id)
                return {"result": spec, "error": None}

            # Create hierarchical specification
            elif action in ["create_hierarchical_spec", "create_hierarchical"]:
                us_number = kwargs.get("us_number") or kwargs.get("us_id")
                title = kwargs.get("title")
                phases = kwargs.get("phases", [])
                roadmap_item_id = kwargs.get("roadmap_item_id")

                if not all([us_number, title]):
                    return {"result": None, "error": "Missing required: us_number, title"}

                # Ensure roadmap_item_id is set
                if not roadmap_item_id:
                    roadmap_item_id = f"US-{us_number}" if not str(us_number).startswith("US-") else us_number

                spec_id = self.spec_skill.create_hierarchical_spec(
                    us_number=int(us_number) if isinstance(us_number, str) and us_number.isdigit() else us_number,
                    title=title,
                    roadmap_item_id=roadmap_item_id,
                    phases=phases,
                    problem_statement=kwargs.get("problem_statement"),
                    architecture=kwargs.get("architecture"),
                )

                return {"result": {"spec_id": spec_id, "roadmap_item_id": roadmap_item_id}, "error": None}

            # Read hierarchical spec phase
            elif action in ["read_hierarchical_spec", "read_phase"]:
                us_id = kwargs.get("us_id")
                phase = kwargs.get("phase")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                if not us_id.startswith("US-"):
                    us_id = f"US-{us_id}"

                spec = self.db.get_technical_spec(us_id)
                if not spec:
                    return {"result": None, "error": f"No spec found for {us_id}"}

                # Check if it's hierarchical
                if spec.get("is_hierarchical"):
                    content = spec.get("content", "{}")
                    if isinstance(content, str):
                        content = json.loads(content)

                    phases = content.get("phases", {})

                    if phase and phase in phases:
                        # Return specific phase
                        phase_content = phases[phase]
                        return {
                            "result": {
                                "phase": phase,
                                "content": phase_content.get("content", ""),
                                "description": phase_content.get("description", ""),
                                "hours": phase_content.get("hours", 0),
                            },
                            "error": None,
                        }
                    else:
                        # Return available phases
                        return {"result": {"available_phases": list(phases.keys()), "phases": phases}, "error": None}
                else:
                    # Return monolithic spec
                    return {"result": {"content": spec.get("content", "")}, "error": None}

            # Detect current phase
            elif action in ["detect_phase", "get_current_phase"]:
                us_id = kwargs.get("us_id")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                if not us_id.startswith("US-"):
                    us_id = f"US-{us_id}"

                # Get implementation tasks to determine phase
                tasks = self.db.get_implementation_tasks(us_id)
                if tasks:
                    # Find the first incomplete task
                    for task in tasks:
                        if task.get("status") != "completed":
                            return {"result": {"current_phase": task.get("phase", "unknown")}, "error": None}

                    # All tasks completed
                    return {"result": {"current_phase": "completed"}, "error": None}

                return {"result": {"current_phase": "not_started"}, "error": None}

            # List all specs
            elif action in ["list", "list_specs", "get_all_specs"]:
                specs = self.db.get_all_technical_specs()
                return {"result": specs, "error": None}

            # Update spec
            elif action in ["update", "update_spec"]:
                us_id = kwargs.get("us_id")
                content = kwargs.get("content")

                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                if not us_id.startswith("US-"):
                    us_id = f"US-{us_id}"

                # Update spec in database
                success = self.db.update_technical_spec(us_id, content=content)
                return {"result": success, "error": None if success else "Failed to update spec"}

            else:
                return {"result": None, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"result": None, "error": str(e)}


# Skill entry point
def run(action: str, **kwargs) -> Dict[str, Any]:
    """Skill entry point.

    Args:
        action: Action to perform
        **kwargs: Action-specific parameters

    Returns:
        dict: {"result": <result>, "error": <error_message>}
    """
    skill = TechnicalSpecificationHandlingSkill()
    return skill.execute(action, **kwargs)
