"""Technical Specification Handling Skill - Unified spec operations.

This skill provides a single source of truth for all technical specification operations,
ensuring consistency across architect and code_developer agents.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("technical-specification-handling")
    result = skill.execute(action="find", priority=priority)
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.utils.spec_handler import SpecHandler


class TechnicalSpecificationHandlingSkill:
    """Technical specification handling skill."""

    def __init__(self):
        """Initialize the skill."""
        self.handler = SpecHandler()

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a specification operation.

        Args:
            action: Operation to perform ("find", "create", "update", "clean", "summarize")
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <result>, "error": <error_message>}
        """
        try:
            if action == "find":
                priority = kwargs.get("priority")
                if not priority:
                    return {"result": None, "error": "Missing 'priority' parameter"}

                spec_path = self.handler.find_spec(priority)
                return {"result": str(spec_path) if spec_path else None, "error": None}

            elif action == "find_by_us_id":
                us_id = kwargs.get("us_id")
                if not us_id:
                    return {"result": None, "error": "Missing 'us_id' parameter"}

                spec_path = self.handler.find_spec_by_us_id(us_id)
                return {"result": str(spec_path) if spec_path else None, "error": None}

            elif action == "spec_exists":
                priority = kwargs.get("priority")
                if not priority:
                    return {"result": None, "error": "Missing 'priority' parameter"}

                exists = self.handler.spec_exists(priority)
                return {"result": exists, "error": None}

            elif action == "create":
                # Extract required parameters
                us_number = kwargs.get("us_number")
                title = kwargs.get("title")
                priority_number = kwargs.get("priority_number")

                if not all([us_number, title, priority_number]):
                    return {"result": None, "error": "Missing required parameters: us_number, title, priority_number"}

                # Create spec content
                spec_content = self.handler.create_spec(
                    us_number=us_number,
                    title=title,
                    priority_number=priority_number,
                    problem_statement=kwargs.get("problem_statement", ""),
                    user_story=kwargs.get("user_story", ""),
                    architecture=kwargs.get("architecture", ""),
                    implementation_plan=kwargs.get("implementation_plan", ""),
                    testing_strategy=kwargs.get("testing_strategy", ""),
                    estimated_effort=kwargs.get("estimated_effort", "TBD"),
                    template_type=kwargs.get("template_type", "full"),
                )

                return {"result": spec_content, "error": None}

            elif action == "generate_filename":
                us_number = kwargs.get("us_number")
                title = kwargs.get("title")

                if not all([us_number, title]):
                    return {"result": None, "error": "Missing required parameters: us_number, title"}

                filename = self.handler.generate_spec_filename(us_number, title)
                return {"result": filename, "error": None}

            elif action == "create_hierarchical":
                # Create hierarchical spec structure
                us_number = kwargs.get("us_number")
                title = kwargs.get("title")
                phases = kwargs.get("phases")

                if not all([us_number, title, phases]):
                    return {"result": None, "error": "Missing required parameters: us_number, title, phases"}

                spec_dir = self.handler.create_hierarchical_spec(
                    us_number=us_number,
                    title=title,
                    phases=phases,
                    problem_statement=kwargs.get("problem_statement", ""),
                    architecture=kwargs.get("architecture", ""),
                    technology_stack=kwargs.get("technology_stack", ""),
                )

                return {"result": str(spec_dir), "error": None}

            elif action == "update":
                spec_path = kwargs.get("spec_path")
                changes = kwargs.get("changes")

                if not spec_path:
                    return {"result": None, "error": "Missing 'spec_path' parameter"}
                if not changes:
                    return {"result": None, "error": "Missing 'changes' parameter"}

                spec_path = Path(spec_path)
                updated_content = self.handler.update_spec(spec_path, changes)
                return {"result": updated_content, "error": None}

            elif action == "clean":
                spec_path = kwargs.get("spec_path")
                rules = kwargs.get("rules", {})

                if not spec_path:
                    return {"result": None, "error": "Missing 'spec_path' parameter"}

                spec_path = Path(spec_path)
                cleaned_content = self.handler.clean_spec(spec_path, rules)
                return {"result": cleaned_content, "error": None}

            elif action == "summarize":
                spec_path = kwargs.get("spec_path")
                summary_type = kwargs.get("summary_type", "executive")
                max_length = kwargs.get("max_length", 500)

                if not spec_path:
                    return {"result": None, "error": "Missing 'spec_path' parameter"}

                spec_path = Path(spec_path)
                summary = self.handler.summarize_spec(spec_path, summary_type, max_length)
                return {"result": summary, "error": None}

            elif action == "extract_version":
                content = kwargs.get("content")
                if not content:
                    return {"result": None, "error": "Missing 'content' parameter"}

                version = self.handler.extract_version(content)
                return {"result": version, "error": None}

            elif action == "bump_version":
                version = kwargs.get("version")
                bump_type = kwargs.get("bump_type", "minor")

                if not version:
                    return {"result": None, "error": "Missing 'version' parameter"}

                new_version = self.handler.bump_version(version, bump_type)
                return {"result": new_version, "error": None}

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
