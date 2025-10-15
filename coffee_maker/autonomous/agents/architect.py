"""Architect agent with automatic ACE integration.

The architect agent handles:
- Architectural introspection and planning
- Technical specification creation
- Implementation guideline documentation
- Pre-implementation architectural decisions

Inherits from ACEAgent for automatic ACE supervision.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from coffee_maker.autonomous.ace.agent_wrapper import ACEAgent

logger = logging.getLogger(__name__)


class Architect(ACEAgent):
    """Architect agent with automatic ACE integration.

    Responsibilities:
    - Analyze architectural requirements
    - Create detailed technical specifications
    - Document architectural decisions (ADRs)
    - Provide implementation guidelines
    - Manage dependencies (pyproject.toml, poetry.lock)
    - Request user approval for important decisions

    Owned Directories/Files:
    - docs/architecture/ (all architectural documentation)
    - pyproject.toml (dependency management)
    - poetry.lock (dependency lock file)

    Key Behaviors:
    - PROACTIVE: Asks user for approval on important decisions
    - OWNERSHIP: Only agent that can modify pyproject.toml
    - DESIGN: All code-design decisions go through architect

    ACE Integration:
    - Automatic via ACEAgent base class
    - Enable/disable: ACE_ENABLED_ARCHITECT environment variable
    """

    @property
    def agent_name(self) -> str:
        """Agent name for ACE."""
        return "architect"

    @property
    def agent_objective(self) -> str:
        """Agent objective for ACE context."""
        return "Design system architecture, create technical specifications, and guide implementation decisions"

    @property
    def success_criteria(self) -> str:
        """Success criteria for ACE evaluation."""
        return "Clear architectural decisions, comprehensive technical specs, and actionable implementation guidelines"

    def __init__(self):
        """Initialize architect agent."""
        # Initialize ACE (automatic via base class)
        super().__init__()

        # Skip agent-specific initialization if already initialized (singleton)
        if hasattr(self, "_agent_initialized") and self._agent_initialized:
            logger.debug("Architect agent-specific components already initialized (singleton)")
            return

        # Initialize agent-specific components
        self.architecture_dir = Path("docs/architecture")
        self.specs_dir = self.architecture_dir / "specs"
        self.decisions_dir = self.architecture_dir / "decisions"
        self.guidelines_dir = self.architecture_dir / "guidelines"

        # Ensure directories exist
        for dir_path in [self.specs_dir, self.decisions_dir, self.guidelines_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Mark agent-specific init as complete
        self._agent_initialized = True

        logger.info("Architect initialized (with automatic ACE)")

    def _execute_implementation(self, task: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Core architecture task logic.

        This is called by:
        - execute_task() when ACE disabled (direct)
        - send_message() when ACE enabled (via generator)

        Args:
            task: Architectural task description
            context: Optional context (requirements, constraints, etc.)

        Returns:
            Architecture result with specs and decisions
        """
        # Set plan (generator will capture this)
        self._set_plan(
            [
                "Analyze architectural requirements",
                "Research existing patterns",
                "Design system architecture",
                "Create technical specification",
                "Document implementation guidelines",
            ]
        )

        # Step 1: Analyze requirements
        self._update_plan_progress("Analyze architectural requirements", "in_progress")
        requirements = self._analyze_requirements(task, context or {})
        self._update_plan_progress("Analyze architectural requirements", "completed")

        # Step 2: Research patterns
        self._update_plan_progress("Research existing patterns", "in_progress")
        patterns = self._research_patterns(requirements)
        self._update_plan_progress("Research existing patterns", "completed")

        # Step 3: Design architecture
        self._update_plan_progress("Design system architecture", "in_progress")
        design = self._design_architecture(requirements, patterns)
        self._update_plan_progress("Design system architecture", "completed")

        # Step 4: Create specification
        self._update_plan_progress("Create technical specification", "in_progress")
        spec_path = self._create_specification(task, design)
        self._update_plan_progress("Create technical specification", "completed")

        # Step 5: Document guidelines
        self._update_plan_progress("Document implementation guidelines", "in_progress")
        guidelines_path = self._create_guidelines(design)
        self._update_plan_progress("Document implementation guidelines", "completed")

        return {
            "status": "success",
            "specification": str(spec_path),
            "guidelines": str(guidelines_path),
            "design": design,
            "ready_for_implementation": True,
        }

    def _analyze_requirements(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze architectural requirements."""
        # TODO: Implement detailed requirement analysis
        return {
            "task": task,
            "functional_requirements": [],
            "non_functional_requirements": [],
            "constraints": [],
            "dependencies": [],
        }

    def _research_patterns(self, requirements: Dict[str, Any]) -> List[str]:
        """Research existing architectural patterns."""
        # TODO: Implement pattern research
        return ["singleton", "factory", "observer"]

    def _design_architecture(self, requirements: Dict[str, Any], patterns: List[str]) -> Dict[str, Any]:
        """Design system architecture."""
        # TODO: Implement architecture design
        return {"components": [], "interfaces": [], "data_flow": [], "patterns_used": patterns}

    def _create_specification(self, task: str, design: Dict[str, Any]) -> Path:
        """Create technical specification document."""
        # TODO: Implement spec creation
        spec_filename = f"{task.lower().replace(' ', '_')}_spec.md"
        spec_path = self.specs_dir / spec_filename

        # Create placeholder (will be enhanced)
        spec_path.write_text(
            f"""# Technical Specification: {task}

## Overview
{task}

## Design
{design}

## Implementation Plan
TBD by architect

## Guidelines
See docs/architecture/guidelines/
"""
        )

        return spec_path

    def _create_guidelines(self, design: Dict[str, Any]) -> Path:
        """Create implementation guidelines."""
        # TODO: Implement guideline creation
        guidelines_path = self.guidelines_dir / "IMPLEMENTATION_GUIDELINES.md"

        if not guidelines_path.exists():
            guidelines_path.write_text(
                """# Implementation Guidelines

## General Principles
- Follow architectural decisions in docs/architecture/decisions/
- Read specifications in docs/architecture/specs/ before implementing
- Maintain consistency with existing patterns
- Document deviations from architecture

## Review Process
1. Architect creates specification
2. User reviews and approves
3. code_developer reads specification
4. code_developer implements following guidelines
5. Architect reviews implementation
"""
            )

        return guidelines_path

    def create_adr(self, title: str, context: str, decision: str, consequences: str) -> Path:
        """Create Architectural Decision Record (ADR)."""
        # Find next ADR number
        existing_adrs = list(self.decisions_dir.glob("ADR-*.md"))
        next_num = len(existing_adrs) + 1

        adr_filename = f"ADR-{next_num:03d}-{title.lower().replace(' ', '-')}.md"
        adr_path = self.decisions_dir / adr_filename

        adr_content = f"""# ADR-{next_num:03d}: {title}

## Status
Accepted

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}

## Date
{self._get_current_date()}
"""

        adr_path.write_text(adr_content)
        logger.info(f"Created ADR: {adr_path}")

        return adr_path

    def _get_current_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().strftime("%Y-%m-%d")

    def add_dependency(self, package_name: str, user_approved: bool = False) -> Dict[str, Any]:
        """Add dependency to pyproject.toml (requires user approval).

        IMPORTANT: Only architect can modify pyproject.toml (dependency management).
        This method requires explicit user approval before making changes.

        Args:
            package_name: Package to add (e.g., "requests", "fastapi[all]")
            user_approved: Whether user has approved this dependency

        Returns:
            Result with approval status
        """
        if not user_approved:
            self._report_concern(
                f"Dependency '{package_name}' requires user approval before adding"
            )
            return {
                "status": "pending_approval",
                "package": package_name,
                "message": "architect needs user approval to add dependency",
                "action_required": f"User must approve adding '{package_name}' before architect can proceed"
            }

        # User approved - proceed with adding dependency
        import subprocess
        result = subprocess.run(
            ["poetry", "add", package_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"✅ Added dependency: {package_name}")
            return {
                "status": "success",
                "package": package_name,
                "message": f"Successfully added {package_name}"
            }
        else:
            self._report_difficulty(
                f"Failed to add dependency '{package_name}': {result.stderr}",
                severity="high"
            )
            return {
                "status": "error",
                "package": package_name,
                "message": result.stderr
            }

    def remove_dependency(self, package_name: str, user_approved: bool = False) -> Dict[str, Any]:
        """Remove dependency from pyproject.toml (requires user approval).

        Args:
            package_name: Package to remove
            user_approved: Whether user has approved this removal

        Returns:
            Result with approval status
        """
        if not user_approved:
            self._report_concern(
                f"Removing dependency '{package_name}' requires user approval"
            )
            return {
                "status": "pending_approval",
                "package": package_name,
                "message": "architect needs user approval to remove dependency",
                "action_required": f"User must approve removing '{package_name}' before architect can proceed"
            }

        # User approved - proceed with removing dependency
        import subprocess
        result = subprocess.run(
            ["poetry", "remove", package_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"✅ Removed dependency: {package_name}")
            return {
                "status": "success",
                "package": package_name,
                "message": f"Successfully removed {package_name}"
            }
        else:
            self._report_difficulty(
                f"Failed to remove dependency '{package_name}': {result.stderr}",
                severity="high"
            )
            return {
                "status": "error",
                "package": package_name,
                "message": result.stderr
            }

    def request_user_approval(self, decision: str, context: str) -> Dict[str, Any]:
        """Request user approval for architectural decision.

        Use this for important decisions like:
        - Adding/removing dependencies
        - Major architectural changes
        - Breaking changes to interfaces

        Args:
            decision: What architect wants to do
            context: Why this decision is needed

        Returns:
            Request for user_listener to present to user
        """
        return {
            "type": "approval_request",
            "decision": decision,
            "context": context,
            "requested_by": "architect",
            "message": f"architect requests approval: {decision}"
        }
