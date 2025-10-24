"""Database Schema Awareness Skill.

This skill provides instant access to database schema information and usage patterns.

Usage:
    from coffee_maker.autonomous.skill_loader import load_skill

    skill = load_skill("database-schema-guide")

    # Get table purpose
    info = skill.execute(action="get_table_info", table="technical_specs")

    # Get usage example
    example = skill.execute(action="get_example", table="technical_specs", spec_type="hierarchical")

    # Check if should use files
    should_use_files = skill.execute(action="should_use_files", table="technical_specs")
    # Returns: {"result": False, "reason": "Store content in database, not files"}
"""

from pathlib import Path
from typing import Dict, Any


class DatabaseSchemaSkill:
    """Provides database schema information and best practices."""

    def __init__(self):
        """Initialize the skill."""
        self.guide_path = Path(__file__).parent / "DATABASE_SCHEMA_GUIDE.md"

        # Table metadata
        self.tables = {
            "technical_specs": {
                "purpose": "Store complete technical specification content in database (NO FILES!)",
                "content_column": "content",
                "content_type": "Plain markdown (monolithic) or JSON (hierarchical)",
                "use_files": False,
                "foreign_keys": [],
                "related_tables": ["implementation_tasks"],
            },
            "implementation_tasks": {
                "purpose": "Break specs into atomic, scoped tasks for parallel execution",
                "content_column": "scope_description",
                "content_type": "Plain text description",
                "use_files": False,
                "foreign_keys": [("spec_id", "technical_specs.id")],
                "related_tables": ["technical_specs"],
            },
        }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a database schema query.

        Args:
            action: Action to perform
            **kwargs: Action-specific parameters

        Returns:
            dict: {"result": <data>, "error": <error_message>}
        """
        try:
            if action == "get_table_info":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                info = self.tables.get(table)
                if not info:
                    return {"result": None, "error": f"Table '{table}' not found in guide"}

                return {"result": info, "error": None}

            elif action == "should_use_files":
                table = kwargs.get("table")
                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                info = self.tables.get(table)
                if not info:
                    return {"result": None, "error": f"Table '{table}' not found"}

                use_files = info.get("use_files", False)
                reason = "Store content in database, not files" if not use_files else "Files required for this table"

                return {
                    "result": use_files,
                    "reason": reason,
                    "content_column": info.get("content_column"),
                    "error": None,
                }

            elif action == "get_example":
                table = kwargs.get("table")
                spec_type = kwargs.get("spec_type", "monolithic")

                if not table:
                    return {"result": None, "error": "Missing 'table' parameter"}

                if table == "technical_specs":
                    if spec_type == "hierarchical":
                        example = {
                            "code": """
content = json.dumps({
    "overview": "High-level system description...",
    "phases": [
        {
            "number": 1,
            "name": "database-layer",
            "description": "Create database models",
            "hours": 2.0,
            "content": "## Phase 1\\n\\n### Models\\n..."
        },
        {
            "number": 2,
            "name": "api-layer",
            "description": "Implement REST API",
            "hours": 3.0,
            "content": "## Phase 2\\n\\n### Endpoints\\n..."
        }
    ]
})

db.create_technical_spec(
    spec_type="hierarchical",
    content=content,  # ✅ Store JSON here
    total_phases=2
)
""",
                            "description": "Hierarchical spec stored as JSON in content column",
                        }
                    else:
                        example = {
                            "code": """
content = \"\"\"# SPEC-116: User Authentication

## Overview
Complete authentication system...

## Requirements
- Login/logout
...
\"\"\"

db.create_technical_spec(
    spec_type="monolithic",
    content=content  # ✅ Store markdown here
)
""",
                            "description": "Monolithic spec stored as plain markdown",
                        }

                    return {"result": example, "error": None}

                elif table == "implementation_tasks":
                    example = {
                        "code": """
db.create_implementation_task(
    task_id="TASK-116-1",
    spec_id="SPEC-116",
    scope="database-layer",
    scope_description="Create User and Session models",
    assigned_files=json.dumps([
        "coffee_maker/models/user.py",
        "migrations/001_create_users.py"
    ]),
    branch_name="roadmap-implementation_task-TASK-116-1"
)
""",
                        "description": "Task breaks spec into atomic implementation unit",
                    }
                    return {"result": example, "error": None}

                return {"result": None, "error": f"No example for table '{table}'"}

            elif action == "get_guide_path":
                return {"result": str(self.guide_path), "error": None}

            elif action == "list_tables":
                return {"result": list(self.tables.keys()), "error": None}

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
        dict: {"result": <data>, "error": <error_message>}
    """
    skill = DatabaseSchemaSkill()
    return skill.execute(action, **kwargs)
