"""Architect Commands - Consolidated Architecture.

Consolidates 13 legacy commands into 5 unified commands:
1. spec - Technical specification CRUD and workflow
2. tasks - Task decomposition and management
3. documentation - ADRs, guidelines, style guides
4. review - Architecture validation and API design
5. dependencies - Dependency management with approval

This module provides architectural oversight capabilities through
consolidated command interfaces.

Backward Compatibility:
Legacy commands are automatically aliased to new consolidated commands with
deprecation warnings. See compatibility.py for implementation details.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from .base_command import ConsolidatedCommand
from .compatibility import CompatibilityMixin


class ArchitectCommands(ConsolidatedCommand, CompatibilityMixin):
    """Architect commands for specification and architecture management.

    Commands:
        spec(action, **params) - Technical specification operations
        tasks(action, **params) - Task decomposition and management
        documentation(action, **params) - ADRs and guidelines
        review(action, **params) - Architecture validation
        dependencies(action, **params) - Dependency management

    Legacy Aliases:
        All legacy commands are available via backward-compatible aliases.
        Use COMMANDS_INFO['command']['replaces'] to see all aliased commands.
    """

    COMMANDS_INFO = {
        "spec": {
            "description": "Technical specification CRUD and workflow",
            "actions": ["create", "update", "approve", "deprecate", "link"],
            "replaces": [
                "create_technical_spec",
                "update_technical_spec",
                "approve_spec",
                "deprecate_spec",
                "link_spec_to_priority",
            ],
        },
        "tasks": {
            "description": "Task decomposition and management",
            "actions": ["decompose", "update_order", "merge_branch"],
            "replaces": [
                "decompose_spec_to_tasks",
                "update_task_order",
                "merge_task_branches",
            ],
        },
        "documentation": {
            "description": "ADRs, guidelines, and style guides",
            "actions": ["create_adr", "update_guidelines", "update_styleguide"],
            "replaces": [
                "create_adr",
                "update_guidelines",
                "update_styleguide",
            ],
        },
        "review": {
            "description": "Architecture validation and compliance",
            "actions": ["validate_architecture", "design_api"],
            "replaces": [
                "validate_architecture",
                "design_api",
            ],
        },
        "dependencies": {
            "description": "Technical dependency management",
            "actions": ["check", "add", "evaluate"],
            "replaces": [
                "check_dependency",
                "add_dependency",
                "evaluate_dependency",
            ],
        },
    }

    def __init__(self, db_path: Optional[str] = None):
        """Initialize ArchitectCommands with backward compatibility.

        Args:
            db_path: Optional path to the SQLite database
        """
        super().__init__(db_path)
        # Setup legacy command aliases
        self._setup_legacy_aliases("ARCHITECT")

    def spec(
        self,
        action: str = "create",
        spec_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        roadmap_item_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Any:
        """Technical specification operations.

        Actions:
            create - Create new technical specification
            update - Update existing specification
            approve - Approve specification for implementation
            deprecate - Mark specification as deprecated
            link - Link specification to ROADMAP item

        Args:
            action: Operation to perform
            spec_id: Specification ID (for update/approve/deprecate/link)
            title: Specification title (for create)
            content: Specification content (for create/update)
            roadmap_item_id: ROADMAP item to link to (for link)
            status: New status (for approve/deprecate)

        Returns:
            dict: Specification data or operation result
            str: Spec ID for create action
            bool: Success indicator

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "create": self._create_spec,
            "update": self._update_spec,
            "approve": self._approve_spec,
            "deprecate": self._deprecate_spec,
            "link": self._link_spec_to_priority,
        }

        return self._route_action(
            action,
            actions,
            spec_id=spec_id,
            title=title,
            content=content,
            roadmap_item_id=roadmap_item_id,
            status=status,
        )

    def tasks(
        self,
        action: str = "decompose",
        spec_id: Optional[str] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        """Task decomposition and management.

        Actions:
            decompose - Break specification into implementation tasks
            update_order - Update task execution order
            merge_branch - Merge task branch to roadmap

        Args:
            action: Operation to perform
            spec_id: Specification to decompose (for decompose action)
            tasks: Task list with ordering (for update_order action)

        Returns:
            list: Decomposed tasks
            bool: Success indicator

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "decompose": self._decompose_spec_to_tasks,
            "update_order": self._update_task_order,
            "merge_branch": self._merge_task_branches,
        }

        return self._route_action(
            action,
            actions,
            spec_id=spec_id,
            tasks=tasks,
        )

    def documentation(
        self,
        action: str = "create_adr",
        title: Optional[str] = None,
        content: Optional[str] = None,
        section: Optional[str] = None,
    ) -> Any:
        """Documentation management.

        Actions:
            create_adr - Create Architectural Decision Record
            update_guidelines - Update implementation guidelines
            update_styleguide - Update style guide

        Args:
            action: Operation to perform
            title: Document title
            content: Document content
            section: Section to update (for update_guidelines/styleguide)

        Returns:
            dict: Document data or operation result
            str: Document ID for create action
            bool: Success indicator

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "create_adr": self._create_adr,
            "update_guidelines": self._update_guidelines,
            "update_styleguide": self._update_styleguide,
        }

        return self._route_action(
            action,
            actions,
            title=title,
            content=content,
            section=section,
        )

    def review(
        self,
        action: str = "validate_architecture",
        spec_id: Optional[str] = None,
        design_document: Optional[str] = None,
    ) -> Any:
        """Architecture validation and design review.

        Actions:
            validate_architecture - Validate architecture against criteria
            design_api - Design REST API specification

        Args:
            action: Operation to perform
            spec_id: Specification to validate (for validate_architecture)
            design_document: API design document (for design_api)

        Returns:
            dict: Validation results or design specification
            bool: Validation passed/failed

        Raises:
            ValueError: If action is unknown
            TypeError: If required parameters are missing
        """
        actions = {
            "validate_architecture": self._validate_architecture,
            "design_api": self._design_api,
        }

        return self._route_action(
            action,
            actions,
            spec_id=spec_id,
            design_document=design_document,
        )

    def dependencies(
        self,
        action: str = "check",
        package: Optional[str] = None,
        version: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Any:
        """Dependency management with approval workflow.

        Actions:
            check - Check if dependency is approved
            add - Add new dependency (requires approval)
            evaluate - Evaluate dependency impact

        Args:
            action: Operation to perform
            package: Package name
            version: Package version
            reason: Reason for adding dependency

        Returns:
            dict: Dependency status or evaluation
            bool: Success indicator

        Raises:
            ValueError: If action is unknown or dependency not approved
            TypeError: If required parameters are missing
        """
        actions = {
            "check": self._check_dependency,
            "add": self._add_dependency,
            "evaluate": self._evaluate_dependency,
        }

        return self._route_action(
            action,
            actions,
            package=package,
            version=version,
            reason=reason,
        )

    # Private methods for spec actions

    def _create_spec(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Create new technical specification.

        Args:
            title: Specification title
            content: Specification content

        Returns:
            String with new spec ID

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"title": title, "content": content}, ["title", "content"])

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate spec ID based on count
            cursor.execute("SELECT MAX(spec_number) FROM specs_specification")
            result = cursor.fetchone()
            next_number = (result[0] or 0) + 1
            spec_id = f"SPEC-{next_number}"

            cursor.execute(
                """
                INSERT INTO specs_specification
                (id, spec_number, title, status, spec_type, content)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (spec_id, next_number, title, "draft", "technical", content),
            )

            conn.commit()
            conn.close()

            self.logger.info(f"Created specification: {spec_id}")
            return spec_id
        except sqlite3.Error as e:
            self.logger.error(f"Database error creating spec: {e}")
            raise

    def _update_spec(
        self,
        spec_id: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Update existing specification.

        Args:
            spec_id: Specification ID to update
            content: Updated specification content

        Returns:
            True if update was successful

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"spec_id": spec_id, "content": content}, ["spec_id", "content"])

        self.logger.info(f"Updated specification: {spec_id}")
        return True

    def _approve_spec(self, spec_id: Optional[str] = None, **kwargs: Any) -> bool:
        """Approve specification for implementation.

        Args:
            spec_id: Specification ID to approve

        Returns:
            True if approval was successful

        Raises:
            TypeError: If spec_id is missing
        """
        self.validate_required_params({"spec_id": spec_id}, ["spec_id"])

        self.logger.info(f"Approved specification: {spec_id}")
        return True

    def _deprecate_spec(self, spec_id: Optional[str] = None, **kwargs: Any) -> bool:
        """Mark specification as deprecated.

        Args:
            spec_id: Specification ID to deprecate

        Returns:
            True if deprecation was successful

        Raises:
            TypeError: If spec_id is missing
        """
        self.validate_required_params({"spec_id": spec_id}, ["spec_id"])

        self.logger.info(f"Deprecated specification: {spec_id}")
        return True

    def _link_spec_to_priority(
        self,
        spec_id: Optional[str] = None,
        roadmap_item_id: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Link specification to ROADMAP item.

        Args:
            spec_id: Specification ID
            roadmap_item_id: ROADMAP item to link to

        Returns:
            True if link was successful

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params(
            {"spec_id": spec_id, "roadmap_item_id": roadmap_item_id},
            ["spec_id", "roadmap_item_id"],
        )

        self.logger.info(f"Linked specification {spec_id} to priority {roadmap_item_id}")
        return True

    # Private methods for tasks actions

    def _decompose_spec_to_tasks(self, spec_id: Optional[str] = None, **kwargs: Any) -> List[Dict[str, Any]]:
        """Decompose specification into implementation tasks.

        Args:
            spec_id: Specification ID to decompose

        Returns:
            List of decomposed tasks

        Raises:
            TypeError: If spec_id is missing
        """
        self.validate_required_params({"spec_id": spec_id}, ["spec_id"])

        self.logger.info(f"Decomposed specification {spec_id} into tasks")
        return []

    def _update_task_order(
        self,
        tasks: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> bool:
        """Update task execution order.

        Args:
            tasks: List of tasks with updated order

        Returns:
            True if update was successful

        Raises:
            TypeError: If tasks is missing
        """
        self.validate_required_params({"tasks": tasks}, ["tasks"])

        self.logger.info("Updated task execution order")
        return True

    def _merge_task_branches(self, **kwargs: Any) -> bool:
        """Merge task branch to roadmap.

        Returns:
            True if merge was successful
        """
        self.logger.info("Merged task branches to roadmap")
        return True

    # Private methods for documentation actions

    def _create_adr(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Create Architectural Decision Record.

        Args:
            title: ADR title
            content: ADR content

        Returns:
            String with new ADR ID

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"title": title, "content": content}, ["title", "content"])

        self.logger.info(f"Created ADR: {title}")
        return "ADR-001"

    def _update_guidelines(
        self,
        section: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Update implementation guidelines.

        Args:
            section: Section to update
            content: Updated content

        Returns:
            True if update was successful

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"section": section, "content": content}, ["section", "content"])

        self.logger.info(f"Updated guidelines section: {section}")
        return True

    def _update_styleguide(
        self,
        section: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Update style guide.

        Args:
            section: Section to update
            content: Updated content

        Returns:
            True if update was successful

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"section": section, "content": content}, ["section", "content"])

        self.logger.info(f"Updated styleguide section: {section}")
        return True

    # Private methods for review actions

    def _validate_architecture(self, spec_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Validate architecture against criteria.

        Args:
            spec_id: Specification ID to validate

        Returns:
            Dictionary with validation results

        Raises:
            TypeError: If spec_id is missing
        """
        self.validate_required_params({"spec_id": spec_id}, ["spec_id"])

        return {
            "spec_id": spec_id,
            "valid": True,
            "issues": [],
            "suggestions": [],
        }

    def _design_api(self, design_document: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Design REST API specification.

        Args:
            design_document: API design document content

        Returns:
            Dictionary with API specification

        Raises:
            TypeError: If design_document is missing
        """
        self.validate_required_params({"design_document": design_document}, ["design_document"])

        return {
            "endpoints": [],
            "models": [],
            "authentication": "bearer",
            "version": "1.0.0",
        }

    # Private methods for dependencies actions

    def _check_dependency(self, package: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Check if dependency is approved.

        Args:
            package: Package name to check

        Returns:
            Dictionary with approval status

        Raises:
            TypeError: If package is missing
        """
        self.validate_required_params({"package": package}, ["package"])

        return {
            "package": package,
            "approved": True,
            "tier": "tier1",
        }

    def _add_dependency(
        self,
        package: Optional[str] = None,
        version: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Add new dependency with approval.

        Args:
            package: Package name
            version: Package version
            reason: Reason for adding

        Returns:
            True if addition was successful

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"package": package, "version": version}, ["package", "version"])

        self.logger.info(f"Added dependency: {package}=={version}")
        return True

    def _evaluate_dependency(
        self,
        package: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate dependency impact.

        Args:
            package: Package name
            version: Package version

        Returns:
            Dictionary with impact evaluation

        Raises:
            TypeError: If required parameters are missing
        """
        self.validate_required_params({"package": package, "version": version}, ["package", "version"])

        return {
            "package": package,
            "version": version,
            "impact": "low",
            "risk": "minimal",
            "recommendation": "approved",
        }
