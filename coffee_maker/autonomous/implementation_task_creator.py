"""Implementation task creator for architect - decomposes specs into parallelizable specs_task.

This module enables architect to:
1. Analyze technical specifications
2. Identify parallelizable work units
3. Perform file dependency analysis
4. Create specs_task with non-overlapping assigned_files
5. Set task_group_id and priority_order for sequential/parallel work

Key Concepts:
- task_group_id: Groups sequential specs_task (e.g., "GROUP-31" for 4 phases)
- priority_order: Enforces order within group (1, 2, 3, 4)
- assigned_files: List of files this task can modify (must not overlap)

Database Integration:
- Uses TechnicalSpecSkill for reading specs (shared skill pattern)
- Direct database access only for specs_task table operations

Author: code_developer (implementing PRIORITY 32)
Date: 2025-10-23
Related: PRIORITY 32, SPEC-132, CFR-000
"""

import json
import logging
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Import shared skill for technical spec reading
import sys
from pathlib import Path

# Add .claude/skills/shared to path for skill imports
skills_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared"
if str(skills_path) not in sys.path:
    sys.path.insert(0, str(skills_path))

from coffee_maker.autonomous.technical_spec_skill import TechnicalSpecSkill

logger = logging.getLogger(__name__)


class FileConflictError(Exception):
    """Raised when assigned_files overlap between specs_task."""


class SpecNotFoundError(Exception):
    """Raised when technical spec doesn't exist."""


class ImplementationTaskCreator:
    """Creates specs_task from technical specs for parallel development.

    Analyzes spec structure, performs file dependency analysis,
    and creates specs_task with proper sequential ordering.
    """

    def __init__(self, db_path: str, agent_name: str = "architect"):
        """Initialize ImplementationTaskCreator.

        Args:
            db_path: Path to SQLite database
            agent_name: Agent using this creator (default: "architect")
        """
        self.db_path = db_path
        self.agent_name = agent_name
        # For testing: use direct database access if db_path is provided
        # For production: use TechnicalSpecSkill with unified database
        self.use_skill = not db_path.endswith(".db")  # Simple heuristic for testing
        if self.use_skill:
            self.spec_skill = TechnicalSpecSkill(agent_name=agent_name)
        else:
            self.spec_skill = None

    def create_works_for_spec(
        self,
        spec_id: str,
        priority_number: int,
        granularity: str = "phase",
    ) -> List[Dict[str, Any]]:
        """Create specs_task for a technical spec.

        Args:
            spec_id: Technical spec ID (e.g., "SPEC-131")
            priority_number: ROADMAP priority number (e.g., 31)
            granularity: Decomposition level ("phase", "section", "module")

        Returns:
            List of created specs_task with metadata

        Raises:
            FileConflictError: If assigned_files overlap
            SpecNotFoundError: If spec doesn't exist

        Example:
            >>> creator = ImplementationTaskCreator("coffee_maker.db")
            >>> specs_task = creator.create_works_for_spec("SPEC-131", 31)
            >>> # Creates: TASK-31-1, TASK-31-2, TASK-31-3...
        """
        logger.info(f"Creating specs_task for {spec_id} (priority {priority_number})")

        # 1. Read technical spec
        spec_content, spec_type = self._read_spec(spec_id)

        # 2. Identify work units
        work_units = self._identify_work_units(spec_content, spec_type, granularity)

        logger.info(f"Identified {len(work_units)} work units")

        # 3. Analyze file dependencies for each task unit
        for unit in work_units:
            unit["assigned_files"] = self._analyze_file_dependencies(unit, spec_content)

        # 4. Validate no file overlaps
        self._validate_file_independence(work_units)

        # 5. Create specs_task in database
        task_group_id = f"GROUP-{priority_number}"
        created_works = []

        for order, unit in enumerate(work_units, start=1):
            task_id = f"TASK-{priority_number}-{order}"

            # Extract sections from unit (strip leading '/')
            sections = unit.get("sections", [])
            spec_sections = [s.lstrip("/") for s in sections] if sections else None

            work_data = self._insert_work(
                task_id=task_id,
                priority_number=priority_number,
                task_group_id=task_group_id,
                priority_order=order,
                spec_id=spec_id,
                scope_description=unit["description"],
                assigned_files=unit["assigned_files"],
                spec_sections=spec_sections,
            )

            created_works.append(work_data)

        logger.info(f"✅ Created {len(created_works)} specs_task for {spec_id}")
        return created_works

    def _read_spec(self, spec_id: str) -> Tuple[Any, str]:
        """Read technical spec from database.

        Args:
            spec_id: Technical spec ID

        Returns:
            (spec_content, spec_type)

        Raises:
            SpecNotFoundError: If spec doesn't exist
        """
        if self.use_skill and self.spec_skill:
            # Production: use shared skill
            spec = self.spec_skill.get_spec_by_id(spec_id)

            if not spec:
                raise SpecNotFoundError(f"Technical spec {spec_id} not found")

            spec_type = spec.get("spec_type", "monolithic")
            content_str = spec.get("content", "")
        else:
            # Testing: use direct database access
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT content, spec_type FROM specs_specification WHERE id = ?",
                (spec_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                raise SpecNotFoundError(f"Technical spec {spec_id} not found")

            content_str, spec_type = result

        # Parse hierarchical JSON if needed
        if spec_type == "hierarchical":
            try:
                content = json.loads(content_str) if isinstance(content_str, str) else content_str
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse hierarchical spec {spec_id}, using as string")
                content = content_str
        else:
            content = content_str

        return content, spec_type

    def _identify_work_units(
        self,
        spec_content: Any,
        spec_type: str,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """Identify work units from spec structure.

        Args:
            spec_content: Spec content (string or JSON)
            spec_type: "hierarchical" or "markdown"
            granularity: "phase", "section", or "module"

        Returns:
            List of work units with descriptions
        """
        if spec_type == "hierarchical":
            return self._identify_hierarchical_units(spec_content, granularity)
        else:
            return self._identify_markdown_units(spec_content, granularity)

    def _identify_hierarchical_units(
        self,
        spec_json: Dict[str, str],
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """Identify work units from hierarchical spec.

        Args:
            spec_json: Hierarchical spec JSON
            granularity: Decomposition level

        Returns:
            List of work units

        Example:
            spec_json = {
                "overview": "...",
                "implementation": "Phase 1: ...\nPhase 2: ...",
                "testing": "..."
            }

            If granularity="phase", extracts phases from implementation section
        """
        units = []

        if granularity == "phase":
            # Extract phases from implementation section
            impl_section = spec_json.get("implementation", "")
            phases = self._extract_phases(impl_section)

            if phases:
                for i, phase in enumerate(phases, start=1):
                    units.append(
                        {
                            "description": f"Phase {i}: {phase['title']}",
                            "sections": ["/implementation"],
                            "phase_content": phase["content"],
                        }
                    )
            else:
                # No phases found, treat each section as a task unit
                for section_key in ["implementation", "testing"]:
                    if section_key in spec_json:
                        units.append(
                            {
                                "description": f"Section: /{section_key}",
                                "sections": [f"/{section_key}"],
                                "phase_content": spec_json[section_key],
                            }
                        )

        elif granularity == "section":
            # One task unit per hierarchical section
            for section_key, section_content in spec_json.items():
                if section_key in ["implementation", "testing", "api_design"]:
                    units.append(
                        {
                            "description": f"Section: /{section_key}",
                            "sections": [f"/{section_key}"],
                            "phase_content": section_content,
                        }
                    )

        return units

    def _extract_phases(self, content: str) -> List[Dict[str, str]]:
        """Extract phases from markdown content.

        Args:
            content: Markdown content with phases

        Returns:
            List of phases with title and content

        Example:
            "Phase 1: Database\n...\nPhase 2: API\n..."
            → [{"title": "Database", "content": "..."}, ...]
        """
        phases = []

        # Match "Phase N: Title" or "## Phase N: Title" with content
        # Group 1: phase number
        # Group 2: title (same line only)
        # Group 3: content (everything after newline until next phase or end)
        phase_pattern = r"(?:##\s*)?Phase\s+(\d+):\s*([^\n]+)(?:\n(.*?))?(?=\n(?:##\s*)?Phase\s+\d+:|\Z)"
        matches = re.finditer(phase_pattern, content, re.DOTALL | re.MULTILINE)

        for match in matches:
            phase_num = match.group(1)
            title = match.group(2).strip()
            phase_content = match.group(3).strip() if match.group(3) else ""

            phases.append({"number": int(phase_num), "title": title, "content": phase_content})

        return phases

    def _identify_markdown_units(
        self,
        spec_content: str,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """Identify work units from markdown spec.

        Args:
            spec_content: Markdown content
            granularity: Decomposition level

        Returns:
            List of work units
        """
        # Simple implementation: extract phases
        phases = self._extract_phases(spec_content)

        if phases:
            return [
                {
                    "description": f"Phase {p['number']}: {p['title']}",
                    "sections": [],
                    "phase_content": p["content"],
                }
                for p in phases
            ]
        else:
            # No phases, treat as single task unit
            return [
                {
                    "description": "Complete implementation",
                    "sections": [],
                    "phase_content": spec_content,
                }
            ]

    def _analyze_file_dependencies(
        self,
        work_unit: Dict[str, Any],
        spec_content: Any,
    ) -> List[str]:
        """Analyze file dependencies for task unit.

        Args:
            work_unit: Work unit with description and content
            spec_content: Full spec content for context

        Returns:
            List of file paths this task will modify

        Note:
            This is a simplified implementation. In production, this would:
            - Use code analysis skills to find related code
            - Use dependency-tracer to analyze imports
            - Parse spec content for file mentions
        """
        assigned_files = []

        # Extract file paths mentioned in phase content
        phase_content = work_unit.get("phase_content", "")

        # Pattern 1: `file_path.py`
        code_pattern = r"`([a-z_/]+\.py)`"
        matches = re.findall(code_pattern, phase_content)
        assigned_files.extend(matches)

        # Pattern 2: file_path.py (without backticks)
        path_pattern = r"\b([a-z_]+/[a-z_/]+\.py)\b"
        matches = re.findall(path_pattern, phase_content)
        assigned_files.extend(matches)

        # Pattern 3: Look for "Create file_name.py" or "Modify file_name.py"
        create_pattern = r"(?:Create|Modify|Update)\s+([a-z_]+\.py)"
        matches = re.findall(create_pattern, phase_content, re.IGNORECASE)
        assigned_files.extend(matches)

        # Remove duplicates and normalize paths
        assigned_files = list(set(assigned_files))

        # If no files found, assign a default based on task unit description
        if not assigned_files:
            logger.warning(f"No files found for task unit: {work_unit['description']}")
            # Generate placeholder file based on description
            # This would be improved in production with actual codebase analysis
            assigned_files = [self._generate_placeholder_file(work_unit)]

        logger.debug(f"Work unit '{work_unit['description']}' → files: {assigned_files}")

        return assigned_files

    def _generate_placeholder_file(self, work_unit: Dict[str, Any]) -> str:
        """Generate placeholder file path when none specified.

        Args:
            work_unit: Work unit metadata

        Returns:
            Placeholder file path
        """
        desc = work_unit["description"].lower()

        if "test" in desc:
            return "tests/placeholder_test.py"
        elif "api" in desc:
            return "coffee_maker/api/placeholder.py"
        elif "database" in desc or "db" in desc:
            return "coffee_maker/autonomous/placeholder_db.py"
        else:
            return "coffee_maker/placeholder.py"

    def _validate_file_independence(self, work_units: List[Dict[str, Any]]) -> None:
        """Validate specs_task have no file conflicts.

        Args:
            work_units: List of work units with assigned_files

        Raises:
            FileConflictError: If any files overlap

        Example:
            work_units = [
                {"assigned_files": ["a.py", "b.py"]},
                {"assigned_files": ["c.py"]},
            ]
            # OK - no overlaps

            work_units = [
                {"assigned_files": ["a.py"]},
                {"assigned_files": ["a.py"]},
            ]
            # ERROR - "a.py" overlap
        """
        all_files_map = {}  # file -> task unit indices

        for i, unit in enumerate(work_units):
            for file_path in unit["assigned_files"]:
                if file_path in all_files_map:
                    other_units = all_files_map[file_path]
                    raise FileConflictError(
                        f"File conflict detected: '{file_path}' appears in multiple work units:\n"
                        f"  - Work {other_units[0] + 1}: {work_units[other_units[0]]['description']}\n"
                        f"  - Work {i + 1}: {unit['description']}"
                    )
                else:
                    all_files_map[file_path] = [i]

        logger.info(f"✅ File independence validated - no conflicts across {len(work_units)} work units")

    def _insert_work(
        self,
        task_id: str,
        priority_number: int,
        task_group_id: str,
        priority_order: int,
        spec_id: str,
        scope_description: str,
        assigned_files: List[str],
        spec_sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Insert task into database.

        Args:
            task_id: Unique task ID (e.g., "TASK-31-1")
            priority_number: ROADMAP priority number
            task_group_id: Group ID (e.g., "GROUP-31")
            priority_order: Order within group (1, 2, 3...)
            spec_id: Technical spec ID
            scope_description: Human-readable description
            assigned_files: List of files this task touches
            spec_sections: Hierarchical spec sections to load (e.g., ["overview", "implementation"])

        Returns:
            Created task data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Prepare spec_sections JSON
        spec_sections_json = json.dumps(spec_sections) if spec_sections else None

        cursor.execute(
            """
            INSERT INTO specs_task (
                task_id, priority_number, task_group_id, priority_order,
                spec_id, scope_description, assigned_files, spec_sections,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
            (
                task_id,
                priority_number,
                task_group_id,
                priority_order,
                spec_id,
                scope_description,
                json.dumps(assigned_files),
                spec_sections_json,
                now,
            ),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"Created task {task_id} (order {priority_order}, " f"files: {assigned_files}, sections: {spec_sections})"
        )

        return {
            "task_id": task_id,
            "priority_number": priority_number,
            "task_group_id": task_group_id,
            "priority_order": priority_order,
            "spec_id": spec_id,
            "scope_description": scope_description,
            "assigned_files": assigned_files,
            "spec_sections": spec_sections,
            "status": "pending",
        }

    def analyze_parallelization_potential(
        self,
        spec_id_1: str,
        spec_id_2: str,
    ) -> Dict[str, Any]:
        """Analyze if two specs can be parallelized.

        Args:
            spec_id_1: First technical spec ID
            spec_id_2: Second technical spec ID

        Returns:
            {
                "can_parallelize": True/False,
                "reason": "...",
                "file_conflicts": [...]  # If any
            }

        Note:
            This is for orchestrator to decide if two separate
            priorities can be worked on in parallel.
        """
        # Read both specs
        content_1, spec_type_1 = self._read_spec(spec_id_1)
        content_2, spec_type_2 = self._read_spec(spec_id_2)

        # Identify work units for both
        units_1 = self._identify_work_units(content_1, spec_type_1, "phase")
        units_2 = self._identify_work_units(content_2, spec_type_2, "phase")

        # Analyze file dependencies
        for unit in units_1:
            unit["assigned_files"] = self._analyze_file_dependencies(unit, content_1)

        for unit in units_2:
            unit["assigned_files"] = self._analyze_file_dependencies(unit, content_2)

        # Check for file overlaps
        files_1 = set()
        for unit in units_1:
            files_1.update(unit["assigned_files"])

        files_2 = set()
        for unit in units_2:
            files_2.update(unit["assigned_files"])

        conflicts = files_1 & files_2

        if conflicts:
            return {
                "can_parallelize": False,
                "reason": f"File conflicts detected: {list(conflicts)}",
                "file_conflicts": list(conflicts),
            }
        else:
            return {
                "can_parallelize": True,
                "reason": "No file conflicts detected",
                "file_conflicts": [],
            }
