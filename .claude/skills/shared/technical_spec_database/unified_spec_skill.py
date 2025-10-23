"""Unified Technical Specification Database Skill.

This skill provides THE ONLY authorized way to access technical specifications.
Direct file manipulation of specs is FORBIDDEN.

Access Control:
    - Write access: architect ONLY
    - Read access: All agents
    - Hierarchical loading: code_developer can load specific sections

Database-Only Pattern:
    All technical specifications MUST be stored in the database.
    Files in docs/architecture/specs/ are for backup/reference only.
    The database is the single source of truth.

Hierarchical Specifications:
    Specs support 3-level hierarchy for selective loading:
    1. Overview (always loaded)
    2. Section (loaded as needed)
    3. Details (loaded for specific implementation)

    This allows code_developer to load only what's needed for context budget.

Integration with Roadmap:
    Each roadmap item can link to a technical spec via spec_id.
    code_developer uses JOIN queries to find next implementation task.

Example Usage:
    >>> from coffee_maker.autonomous.unified_spec_skill import TechnicalSpecSkill
    >>>
    >>> # Initialize with agent name
    >>> spec_skill = TechnicalSpecSkill(agent_name="code_developer")
    >>>
    >>> # Find next task to implement (JOIN roadmap + specs)
    >>> next_task = spec_skill.get_next_implementation_task()
    >>> if next_task:
    >>>     print(f"Implement: {next_task['title']}")
    >>>     print(f"Spec: {next_task['spec_id']}")
    >>>
    >>>     # Load only needed spec sections
    >>>     overview = spec_skill.get_spec_overview(next_task['spec_id'])
    >>>     api_section = spec_skill.get_spec_section(next_task['spec_id'], 'api_design')
    >>>
    >>> # Architect creates/updates specs
    >>> if agent_name == "architect":
    >>>     spec_skill.create_spec(...)  # Only architect can do this

FORBIDDEN Operations:
    ❌ Writing directly to docs/architecture/specs/*.md files
    ❌ Reading spec files without going through database
    ❌ Any agent except architect modifying specs
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TechnicalSpecSkill:
    """Unified skill for technical specification database access.

    Provides consistent interface for all agents with proper access control.
    Supports hierarchical specs and roadmap integration.
    """

    def __init__(self, agent_name: str = "unknown"):
        """Initialize technical spec skill.

        Args:
            agent_name: Name of agent using skill (for access control)
        """
        self.agent_name = agent_name
        self.can_write = agent_name == "architect"

        # Use unified database for efficient JOINs
        from coffee_maker.autonomous.unified_database import get_unified_database

        self.db = get_unified_database()

        if not self.can_write and agent_name != "unknown":
            logger.info(f"Agent {agent_name} has read-only access to technical specs")

    # ==================== READ OPERATIONS (All Agents) ====================

    def get_next_implementation_task(self) -> Optional[Dict]:
        """Get next roadmap item ready for implementation (has spec).

        This JOINs roadmap and technical_specs to find the next
        planned item that has a complete technical specification.

        Returns:
            Dict with roadmap item + spec info, or None if nothing ready
        """
        # Use unified database for efficient JOIN
        return self.db.get_next_implementation_task()

    def get_spec_by_id(self, spec_id: str) -> Optional[Dict]:
        """Get complete technical specification by ID.

        Args:
            spec_id: Spec ID (e.g., "SPEC-115")

        Returns:
            Complete spec dictionary or None
        """
        try:
            conn = sqlite3.connect(self.spec_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE id = ?
            """,
                (spec_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                spec = dict(row)
                # Parse JSON fields
                if spec.get("dependencies"):
                    spec["dependencies"] = json.loads(spec["dependencies"])
                return spec

            return None

        except sqlite3.Error as e:
            logger.error(f"Error getting spec: {e}")
            return None

    def get_spec_overview(self, spec_id: str) -> Optional[str]:
        """Get only the overview section of a hierarchical spec.

        This is the top level (1/3) of the hierarchy.
        Used when code_developer needs minimal context.

        Args:
            spec_id: Spec ID

        Returns:
            Overview section or None
        """
        spec = self.get_spec_by_id(spec_id)
        if not spec:
            return None

        content = spec.get("content", "")

        # For hierarchical specs, extract overview section
        if spec.get("spec_type") == "hierarchical":
            # Parse hierarchical content structure
            try:
                if isinstance(content, str):
                    # If stored as JSON string
                    hierarchy = json.loads(content) if content.startswith("{") else {"overview": content}
                else:
                    hierarchy = content

                return hierarchy.get("overview", content)
            except (json.JSONDecodeError, TypeError):
                # Fallback: return first section up to first ## heading
                lines = content.split("\n")
                overview = []
                for line in lines:
                    if line.startswith("## ") and overview:
                        break
                    overview.append(line)
                return "\n".join(overview)
        else:
            # For monolithic specs, return executive summary or first section
            lines = content.split("\n")
            overview = []
            in_overview = False

            for line in lines:
                if "executive summary" in line.lower() or "overview" in line.lower():
                    in_overview = True
                elif line.startswith("## ") and in_overview:
                    break
                if in_overview:
                    overview.append(line)

            return "\n".join(overview) if overview else content[:1000]  # First 1000 chars

    def get_spec_section(self, spec_id: str, section_name: str) -> Optional[str]:
        """Get specific section from a hierarchical spec.

        This is level 2/3 of the hierarchy.
        Used when code_developer needs specific implementation details.

        Args:
            spec_id: Spec ID
            section_name: Section name (e.g., "api_design", "data_model")

        Returns:
            Section content or None
        """
        spec = self.get_spec_by_id(spec_id)
        if not spec:
            return None

        content = spec.get("content", "")

        if spec.get("spec_type") == "hierarchical":
            try:
                if isinstance(content, str):
                    hierarchy = json.loads(content) if content.startswith("{") else {}
                else:
                    hierarchy = content

                # Look for section in hierarchy
                return hierarchy.get(section_name)
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback: Extract section by markdown headers
        lines = content.split("\n")
        section_content = []
        in_section = False

        for line in lines:
            # Check if we found the section
            if section_name.replace("_", " ").lower() in line.lower() and line.startswith("#"):
                in_section = True
                section_content.append(line)
            elif in_section:
                # Stop at next section of same or higher level
                if line.startswith("#") and not line.startswith("###"):
                    break
                section_content.append(line)

        return "\n".join(section_content) if section_content else None

    def get_spec_implementation_details(self, spec_id: str) -> Optional[str]:
        """Get detailed implementation section (level 3/3).

        This includes code examples, algorithms, test cases.
        Used when code_developer is actively implementing.

        Args:
            spec_id: Spec ID

        Returns:
            Implementation details or None
        """
        spec = self.get_spec_by_id(spec_id)
        if not spec:
            return None

        content = spec.get("content", "")

        if spec.get("spec_type") == "hierarchical":
            try:
                hierarchy = json.loads(content) if isinstance(content, str) and content.startswith("{") else {}

                # Collect all implementation-related sections
                details = []
                for key in ["implementation", "code_examples", "algorithms", "test_strategy", "details"]:
                    if key in hierarchy:
                        details.append(f"## {key.replace('_', ' ').title()}\n{hierarchy[key]}")

                return "\n\n".join(details) if details else None
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback: Extract implementation sections
        impl_keywords = ["implementation", "algorithm", "code example", "test", "api"]
        lines = content.split("\n")
        impl_content = []
        in_impl = False

        for line in lines:
            if any(keyword in line.lower() for keyword in impl_keywords) and line.startswith("#"):
                in_impl = True
            if in_impl:
                impl_content.append(line)

        return "\n".join(impl_content) if impl_content else None

    def find_specs_for_priority(self, priority_number: str) -> List[Dict]:
        """Find all specs related to a priority/user story.

        Args:
            priority_number: Priority number (e.g., "26", "US-062")

        Returns:
            List of spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.spec_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Handle both PRIORITY-X and US-X formats
            roadmap_patterns = [f"PRIORITY-{priority_number}", f"US-{priority_number}", priority_number]

            placeholders = ",".join(["?" for _ in roadmap_patterns])
            cursor.execute(
                f"""
                SELECT * FROM technical_specs
                WHERE roadmap_item_id IN ({placeholders})
                ORDER BY spec_number DESC
            """,
                roadmap_patterns,
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error finding specs: {e}")
            return []

    def get_pending_specs(self) -> List[Dict]:
        """Get specs that need work (draft or in_progress).

        Useful for architect to track incomplete specs.

        Returns:
            List of pending spec dictionaries
        """
        try:
            conn = sqlite3.connect(self.spec_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM technical_specs
                WHERE status IN ('draft', 'in_progress')
                ORDER BY spec_number DESC
            """
            )

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting pending specs: {e}")
            return []

    # ==================== WRITE OPERATIONS (Architect Only) ====================

    def create_spec(
        self,
        spec_number: int,
        title: str,
        roadmap_item_id: str,
        content: Dict[str, str] | str,
        spec_type: str = "monolithic",
        dependencies: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
    ) -> str:
        """Create new technical specification (architect only).

        Args:
            spec_number: Spec number (e.g., 115)
            title: Spec title
            roadmap_item_id: Related roadmap item (e.g., "PRIORITY-26")
            content: Spec content (Dict for hierarchical, str for monolithic)
            spec_type: "monolithic" or "hierarchical"
            dependencies: List of other spec IDs this depends on
            estimated_hours: Estimated implementation hours

        Returns:
            Spec ID (e.g., "SPEC-115")

        Raises:
            PermissionError: If not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can create specs, not {self.agent_name}")

        spec_id = f"SPEC-{spec_number}"

        # Convert hierarchical content to JSON if needed
        if spec_type == "hierarchical" and isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = content

        try:
            conn = sqlite3.connect(self.spec_db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO technical_specs (
                    id, spec_number, title, roadmap_item_id, status,
                    spec_type, content, dependencies, estimated_hours,
                    updated_at, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    spec_id,
                    spec_number,
                    title,
                    roadmap_item_id,
                    "draft",
                    spec_type,
                    content_str,
                    json.dumps(dependencies) if dependencies else None,
                    estimated_hours,
                    datetime.now().isoformat(),
                    self.agent_name,
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Created technical spec {spec_id} in database")

            # Notify project_manager to update roadmap with spec link
            self._notify_roadmap_update(spec_id, roadmap_item_id)

            return spec_id

        except sqlite3.Error as e:
            logger.error(f"Error creating spec: {e}")
            raise

    def update_spec_status(self, spec_id: str, new_status: str, actual_hours: Optional[float] = None) -> bool:
        """Update spec status (architect only).

        Args:
            spec_id: Spec ID
            new_status: New status ('draft', 'in_progress', 'complete', 'approved')
            actual_hours: Actual implementation hours (when marking complete)

        Returns:
            True if successful

        Raises:
            PermissionError: If not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can update specs, not {self.agent_name}")

        try:
            conn = sqlite3.connect(self.spec_db_path)
            cursor = conn.cursor()

            update_fields = ["status = ?", "updated_at = ?", "updated_by = ?"]
            params = [new_status, datetime.now().isoformat(), self.agent_name]

            if actual_hours is not None:
                update_fields.append("actual_hours = ?")
                params.append(actual_hours)

            params.append(spec_id)  # WHERE clause

            cursor.execute(
                f"""
                UPDATE technical_specs
                SET {', '.join(update_fields)}
                WHERE id = ?
            """,
                params,
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            if success:
                if new_status == "complete":
                    # Notify project_manager that spec is ready
                    self._notify_spec_complete(spec_id)
                elif new_status == "approved":
                    # Notify project_manager that spec is approved and ready for implementation
                    self._notify_spec_approved(spec_id)

            return success

        except sqlite3.Error as e:
            logger.error(f"Error updating spec status: {e}")
            return False

    def update_spec_content(
        self, spec_id: str, content: Dict[str, str] | str, section_only: Optional[str] = None
    ) -> bool:
        """Update spec content or specific section (architect only).

        Args:
            spec_id: Spec ID
            content: New content (full or section)
            section_only: If provided, only update this section (hierarchical specs)

        Returns:
            True if successful

        Raises:
            PermissionError: If not architect
        """
        if not self.can_write:
            raise PermissionError(f"Only architect can update specs, not {self.agent_name}")

        try:
            # Get current spec
            current = self.get_spec_by_id(spec_id)
            if not current:
                logger.error(f"Spec {spec_id} not found")
                return False

            # Handle hierarchical update
            if section_only and current.get("spec_type") == "hierarchical":
                try:
                    current_content = (
                        json.loads(current["content"]) if isinstance(current["content"], str) else current["content"]
                    )
                except (json.JSONDecodeError, TypeError):
                    current_content = {}

                # Update only the specified section
                current_content[section_only] = content
                final_content = json.dumps(current_content, indent=2)
            else:
                # Full content replacement
                if isinstance(content, dict):
                    final_content = json.dumps(content, indent=2)
                else:
                    final_content = content

            conn = sqlite3.connect(self.spec_db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE technical_specs
                SET content = ?, updated_at = ?, updated_by = ?
                WHERE id = ?
            """,
                (final_content, datetime.now().isoformat(), self.agent_name, spec_id),
            )

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            return success

        except sqlite3.Error as e:
            logger.error(f"Error updating spec content: {e}")
            return False

    # ==================== PRIVATE HELPER METHODS ====================

    def _notify_roadmap_update(self, spec_id: str, roadmap_item_id: str) -> None:
        """Notify project_manager to link spec to roadmap item."""
        try:
            from coffee_maker.autonomous.roadmap_database_v2 import RoadmapDatabaseV2

            roadmap_db = RoadmapDatabaseV2(agent_name=self.agent_name)

            # Create detailed notification for project_manager
            message = (
                f"ACTION REQUIRED: Link technical spec to roadmap\n"
                f"- Spec ID: {spec_id}\n"
                f"- Roadmap Item: {roadmap_item_id}\n"
                f"- Action: Use unified_db.link_spec_to_roadmap('{roadmap_item_id}', '{spec_id}')\n"
                f"- This will enable code_developer to find this task via JOIN queries"
            )

            roadmap_db.create_update_notification(
                item_id=roadmap_item_id,
                requested_by="architect",
                notification_type="link_spec",
                requested_status=None,
                message=message,
            )

            logger.info(f"📬 Notified project_manager to link {spec_id} to {roadmap_item_id}")

        except Exception as e:
            logger.warning(f"Could not notify project_manager: {e}")

    def _notify_spec_complete(self, spec_id: str) -> None:
        """Notify project_manager that spec is complete and ready."""
        try:
            spec = self.get_spec_by_id(spec_id)
            if not spec:
                return

            from coffee_maker.autonomous.roadmap_database_v2 import RoadmapDatabaseV2

            roadmap_db = RoadmapDatabaseV2(agent_name=self.agent_name)

            # Create detailed notification
            message = (
                f"SPEC COMPLETE: Technical specification ready for implementation\n"
                f"- Spec ID: {spec_id}\n"
                f"- Title: {spec.get('title', 'Unknown')}\n"
                f"- Roadmap Item: {spec.get('roadmap_item_id', 'Not linked')}\n"
                f"- Status: Complete\n"
                f"- Estimated Hours: {spec.get('estimated_hours', 'Not specified')}\n"
                f"\nACTIONS REQUIRED:\n"
                f"1. Verify spec is linked to roadmap item\n"
                f"2. Update roadmap item status to '🔄 In Progress' or '📋 Ready for Implementation'\n"
                f"3. code_developer can now implement this feature"
            )

            roadmap_db.create_update_notification(
                item_id=spec.get("roadmap_item_id", "UNKNOWN"),
                requested_by="architect",
                notification_type="spec_complete",
                requested_status="🔄 In Progress",
                message=message,
            )

            logger.info(f"✅ Notified project_manager that {spec_id} is complete")

        except Exception as e:
            logger.warning(f"Could not notify about spec completion: {e}")

    def _notify_spec_approved(self, spec_id: str) -> None:
        """Notify project_manager that spec is approved for implementation."""
        try:
            spec = self.get_spec_by_id(spec_id)
            if not spec:
                return

            from coffee_maker.autonomous.roadmap_database_v2 import RoadmapDatabaseV2

            roadmap_db = RoadmapDatabaseV2(agent_name=self.agent_name)

            message = (
                f"SPEC APPROVED: Ready for immediate implementation\n"
                f"- Spec ID: {spec_id}\n"
                f"- Title: {spec.get('title', 'Unknown')}\n"
                f"- Roadmap Item: {spec.get('roadmap_item_id', 'Not linked')}\n"
                f"- Status: Approved\n"
                f"\ncode_developer can now find this via get_next_implementation_task()"
            )

            roadmap_db.create_update_notification(
                item_id=spec.get("roadmap_item_id", "UNKNOWN"),
                requested_by="architect",
                notification_type="spec_approved",
                requested_status="🔄 In Progress",
                message=message,
            )

            logger.info(f"✅ Notified project_manager that {spec_id} is approved")

        except Exception as e:
            logger.warning(f"Could not notify about spec approval: {e}")


# ==================== SKILL FACTORY ====================


def get_technical_spec_skill(agent_name: str) -> TechnicalSpecSkill:
    """Factory function to get technical spec skill for an agent.

    Args:
        agent_name: Name of agent requesting skill

    Returns:
        TechnicalSpecSkill instance with appropriate permissions
    """
    return TechnicalSpecSkill(agent_name)


# ==================== USAGE DOCUMENTATION ====================

SPEC_SKILL_USAGE = """
## Technical Specification Database Skill Usage

### For code_developer (Finding Next Task):
```python
from coffee_maker.autonomous.unified_spec_skill import TechnicalSpecSkill

# Initialize skill
spec_skill = TechnicalSpecSkill(agent_name="code_developer")

# Find next implementation task (JOIN roadmap + specs)
next_task = spec_skill.get_next_implementation_task()
if next_task:
    print(f"Task: {next_task['item_title']}")
    print(f"Spec: {next_task['spec_id']}")

    # Load spec hierarchically (for context budget)
    overview = spec_skill.get_spec_overview(next_task['spec_id'])
    # Load only when implementing specific part
    api_details = spec_skill.get_spec_section(next_task['spec_id'], 'api_design')
    # Load when deep in implementation
    impl_details = spec_skill.get_spec_implementation_details(next_task['spec_id'])
```

### For architect (Creating/Updating Specs):
```python
# Create hierarchical spec
spec_id = spec_skill.create_spec(
    spec_number=116,
    title="New Feature Implementation",
    roadmap_item_id="PRIORITY-28",
    content={
        "overview": "High-level feature description...",
        "api_design": "Detailed API endpoints...",
        "data_model": "Database schema...",
        "implementation": "Step-by-step implementation guide...",
        "test_strategy": "Testing approach..."
    },
    spec_type="hierarchical",
    estimated_hours=8.0
)

# Update status when complete
spec_skill.update_spec_status(spec_id, "complete")
```

### FORBIDDEN Operations:
```python
# ❌ NEVER write specs to files directly
with open("docs/architecture/specs/SPEC-116.md", "w") as f:
    f.write(content)  # WRONG!

# ✅ ALWAYS use the database
spec_skill.create_spec(...)  # CORRECT

# ❌ NEVER read spec files directly
content = Path("docs/architecture/specs/SPEC-116.md").read_text()  # WRONG!

# ✅ ALWAYS use the database
spec = spec_skill.get_spec_by_id("SPEC-116")  # CORRECT
```

### Hierarchical Loading Pattern:
1. **Context Budget Management**: Load only what you need
   - Overview: ~500 tokens (always load)
   - Section: ~1000 tokens (load when working on that part)
   - Details: ~2000 tokens (load when implementing)

2. **Progressive Loading**:
   ```python
   # Start with overview
   context = spec_skill.get_spec_overview(spec_id)

   # Add section when needed
   if working_on_api:
       context += spec_skill.get_spec_section(spec_id, "api_design")

   # Add details when implementing
   if implementing_now:
       context += spec_skill.get_spec_implementation_details(spec_id)
   ```
"""
