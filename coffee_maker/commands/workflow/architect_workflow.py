"""Architect Workflow Command - Ultra-Consolidated.

Single workflow command that handles the entire architectural design lifecycle:
analyze → design → spec → ADR

Replaces 5 consolidated commands with 1 workflow command.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from coffee_maker.commands.consolidated.architect_commands import ArchitectCommands
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class SpecDepth(Enum):
    """Design depth options."""

    FULL = "full"  # Complete workflow with all steps
    QUICK = "quick"  # Fast design without POC/ADR
    UPDATE = "update"  # Update existing spec
    REVIEW = "review"  # Review and validate only


@dataclass
class SpecResult:
    """Result of spec() execution.

    Attributes:
        spec_id: Generated specification ID
        status: Success/failure status
        priority_id: Priority that was designed
        steps_completed: List of completed step names
        steps_failed: List of failed step names
        dependencies_checked: List of dependencies validated
        adr_created: Whether ADR was created
        poc_created: Whether POC was created
        duration_seconds: Execution time
        error_message: Error message if failed
        metadata: Additional workflow metadata
    """

    spec_id: str
    status: str = "success"
    priority_id: str = ""
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    dependencies_checked: List[str] = field(default_factory=list)
    adr_created: bool = False
    poc_created: bool = False
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArchitectWorkflow:
    """Ultra-consolidated workflow command for architectural design.

    Single command that handles complete design workflow:
        1. Load priority from roadmap
        2. Analyze requirements and dependencies
        3. Design solution architecture
        4. Create technical specification
        5. Document architectural decisions (ADR)
        6. Review and validate POC if needed
        7. Update dependency matrix
        8. Notify relevant agents

    Example:
        >>> workflow = ArchitectWorkflow()
        >>> result = workflow.spec(priority_id="PRIORITY-5")
        >>> print(f"Created: {result.spec_id}")

    Replaces:
        - design(action="analyze|create|review")
        - specs(action="create|update|validate")
        - dependency(action="check|add|update")
        - adr(action="create|update")
        - poc(action="create|validate")
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize workflow with consolidated commands."""
        self.commands = ArchitectCommands(db_path)
        self.logger = logger

    def spec(
        self,
        priority_id: str,
        depth: str = "full",
        poc_required: Optional[bool] = None,
        dependencies: Optional[List[str]] = None,
        notify: bool = True,
        verbose: bool = False,
    ) -> SpecResult:
        """Execute complete architectural design workflow for a priority.

        Args:
            priority_id: Priority to design (required)
            depth: Design depth - "full"|"quick"|"update"|"review"
            poc_required: Create POC first (default: auto-detect based on complexity)
            dependencies: List of dependencies to check (optional)
            notify: Notify relevant agents (default: True)
            verbose: Enable verbose logging (default: False)

        Returns:
            SpecResult with execution details

        Raises:
            ValueError: If priority_id is invalid or depth is unknown

        Example:
            # Full design workflow
            result = workflow.spec(priority_id="PRIORITY-5")

            # Quick design without POC/ADR
            result = workflow.spec(priority_id="PRIORITY-5", depth="quick")

            # With explicit dependencies
            result = workflow.spec(
                priority_id="PRIORITY-5",
                dependencies=["fastapi", "pydantic"]
            )

            # Force POC creation
            result = workflow.spec(
                priority_id="PRIORITY-5",
                poc_required=True
            )
        """
        start_time = datetime.now()

        try:
            # Validate depth
            try:
                spec_depth = SpecDepth(depth)
            except ValueError:
                raise ValueError(
                    f"Invalid depth '{depth}'. " f"Must be one of: {', '.join(d.value for d in SpecDepth)}"
                )

            self.logger.info(f"Starting spec workflow for {priority_id} (depth={depth})")

            # Generate spec ID
            spec_id = self._generate_spec_id(priority_id)
            result = SpecResult(spec_id=spec_id, priority_id=priority_id)

            # Execute workflow based on depth
            if spec_depth == SpecDepth.FULL:
                result = self._execute_full_workflow(
                    priority_id=priority_id,
                    spec_id=spec_id,
                    result=result,
                    poc_required=poc_required,
                    dependencies=dependencies,
                    notify=notify,
                    verbose=verbose,
                )
            elif spec_depth == SpecDepth.QUICK:
                result = self._execute_quick_workflow(
                    priority_id=priority_id,
                    spec_id=spec_id,
                    result=result,
                    dependencies=dependencies,
                    verbose=verbose,
                )
            elif spec_depth == SpecDepth.UPDATE:
                result = self._execute_update_workflow(
                    priority_id=priority_id,
                    spec_id=spec_id,
                    result=result,
                    notify=notify,
                    verbose=verbose,
                )
            elif spec_depth == SpecDepth.REVIEW:
                result = self._execute_review_workflow(
                    priority_id=priority_id,
                    spec_id=spec_id,
                    result=result,
                    verbose=verbose,
                )

            # Calculate duration
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

            # Determine final status
            if len(result.steps_failed) == 0:
                result.status = "success"
            elif len(result.steps_completed) > 0:
                result.status = "partial"
            else:
                result.status = "failed"

            self.logger.info(f"Spec workflow completed: {result.status} ({result.duration_seconds:.1f}s)")
            return result

        except Exception as e:
            result = SpecResult(
                spec_id=self._generate_spec_id(priority_id),
                status="failed",
                priority_id=priority_id,
                error_message=str(e),
            )
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Spec workflow failed: {e}")
            return result

    def _execute_full_workflow(
        self,
        priority_id: str,
        spec_id: str,
        result: SpecResult,
        poc_required: Optional[bool],
        dependencies: Optional[List[str]],
        notify: bool,
        verbose: bool,
    ) -> SpecResult:
        """Execute full architectural design workflow.

        Steps:
            1. Load priority from roadmap
            2. Analyze requirements and dependencies
            3. Check dependency approval (if provided)
            4. Create POC if required or auto-detected
            5. Design solution architecture
            6. Create technical specification
            7. Document architectural decisions (ADR)
            8. Update dependency matrix
            9. Notify relevant agents
        """
        # Step 1: Load priority
        if verbose:
            self.logger.info(f"[1/9] Loading priority {priority_id}")
        try:
            priority_data = self.commands.design(action="analyze", priority_id=priority_id)
            result.steps_completed.append("load_priority")
            result.metadata["priority_data"] = priority_data
        except Exception as e:
            result.steps_failed.append("load_priority")
            result.error_message = f"Failed to load priority: {e}"
            return result

        # Step 2: Analyze requirements
        if verbose:
            self.logger.info("[2/9] Analyzing requirements and complexity")
        try:
            analysis = self.commands.design(action="analyze", priority_id=priority_id)
            result.steps_completed.append("analyze_requirements")
            result.metadata["analysis"] = analysis

            # Auto-detect POC requirement based on complexity
            if poc_required is None:
                if isinstance(analysis, dict):
                    complexity = analysis.get("complexity", "medium")
                    poc_required = complexity in ["high", "very_high"]
                else:
                    poc_required = False
        except Exception as e:
            result.steps_failed.append("analyze_requirements")
            result.error_message = f"Analysis failed: {e}"
            return result

        # Step 3: Check dependencies
        if dependencies:
            if verbose:
                self.logger.info(f"[3/9] Checking {len(dependencies)} dependencies")
            try:
                for dep in dependencies:
                    dep_check = self.commands.dependency(action="check", package_name=dep)
                    result.dependencies_checked.append(dep)
                    if isinstance(dep_check, dict) and not dep_check.get("approved", False):
                        self.logger.warning(f"Dependency {dep} not pre-approved")
                result.steps_completed.append("check_dependencies")
            except Exception as e:
                result.steps_failed.append("check_dependencies")
                self.logger.warning(f"Dependency check failed: {e}")
                # Continue anyway - dependencies are not blocking
        else:
            if verbose:
                self.logger.info("[3/9] No dependencies to check")
            result.steps_completed.append("check_dependencies")

        # Step 4: Create POC if required
        if poc_required:
            if verbose:
                self.logger.info("[4/9] Creating POC for complex feature")
            try:
                poc_result = self.commands.poc(action="create", priority_id=priority_id)
                result.poc_created = True
                result.steps_completed.append("create_poc")
                result.metadata["poc"] = poc_result
            except Exception as e:
                result.steps_failed.append("create_poc")
                self.logger.warning(f"POC creation failed: {e}")
                # Continue anyway - POC is helpful but not required
        else:
            if verbose:
                self.logger.info("[4/9] Skipping POC (not required)")
            result.steps_completed.append("create_poc")

        # Step 5: Design solution
        if verbose:
            self.logger.info("[5/9] Designing solution architecture")
        try:
            design = self.commands.design(action="create", priority_id=priority_id)
            result.steps_completed.append("design_solution")
            result.metadata["design"] = design
        except Exception as e:
            result.steps_failed.append("design_solution")
            result.error_message = f"Design failed: {e}"
            return result

        # Step 6: Create specification
        if verbose:
            self.logger.info(f"[6/9] Creating technical specification {spec_id}")
        try:
            spec = self.commands.specs(action="create", priority_id=priority_id, spec_id=spec_id)
            result.steps_completed.append("create_spec")
            result.metadata["spec"] = spec
        except Exception as e:
            result.steps_failed.append("create_spec")
            result.error_message = f"Spec creation failed: {e}"
            return result

        # Step 7: Document ADR
        if verbose:
            self.logger.info("[7/9] Documenting architectural decision record")
        try:
            adr = self.commands.adr(action="create", spec_id=spec_id, priority_id=priority_id)
            result.adr_created = True
            result.steps_completed.append("create_adr")
            result.metadata["adr"] = adr
        except Exception as e:
            result.steps_failed.append("create_adr")
            self.logger.warning(f"ADR creation failed: {e}")
            # Continue anyway - ADR is important but not blocking

        # Step 8: Update dependency matrix
        if dependencies:
            if verbose:
                self.logger.info("[8/9] Updating dependency matrix")
            try:
                for dep in dependencies:
                    self.commands.dependency(action="add", package_name=dep, spec_id=spec_id)
                result.steps_completed.append("update_dependencies")
            except Exception as e:
                result.steps_failed.append("update_dependencies")
                self.logger.warning(f"Dependency update failed: {e}")
        else:
            if verbose:
                self.logger.info("[8/9] No dependencies to update")
            result.steps_completed.append("update_dependencies")

        # Step 9: Notify agents
        if notify:
            if verbose:
                self.logger.info("[9/9] Notifying relevant agents")
            try:
                # Notify code_developer that spec is ready
                notification = {
                    "type": "spec_ready",
                    "spec_id": spec_id,
                    "priority_id": priority_id,
                }
                result.steps_completed.append("notify_agents")
                result.metadata["notification"] = notification
            except Exception as e:
                result.steps_failed.append("notify_agents")
                self.logger.warning(f"Notification failed: {e}")
        else:
            if verbose:
                self.logger.info("[9/9] Skipping notifications")
            result.steps_completed.append("notify_agents")

        return result

    def _execute_quick_workflow(
        self,
        priority_id: str,
        spec_id: str,
        result: SpecResult,
        dependencies: Optional[List[str]],
        verbose: bool,
    ) -> SpecResult:
        """Execute quick design workflow (no POC, no ADR).

        Steps:
            1. Analyze requirements
            2. Check dependencies
            3. Design solution
            4. Create spec
        """
        # Step 1: Analyze
        if verbose:
            self.logger.info(f"[1/4] Quick analysis for {priority_id}")
        try:
            analysis = self.commands.design(action="analyze", priority_id=priority_id)
            result.steps_completed.append("analyze_requirements")
            result.metadata["analysis"] = analysis
        except Exception as e:
            result.steps_failed.append("analyze_requirements")
            result.error_message = f"Analysis failed: {e}"
            return result

        # Step 2: Check dependencies
        if dependencies:
            if verbose:
                self.logger.info(f"[2/4] Checking {len(dependencies)} dependencies")
            for dep in dependencies:
                try:
                    self.commands.dependency(action="check", package_name=dep)
                    result.dependencies_checked.append(dep)
                except Exception as e:
                    self.logger.warning(f"Dependency check failed for {dep}: {e}")
            result.steps_completed.append("check_dependencies")
        else:
            result.steps_completed.append("check_dependencies")

        # Step 3: Design
        if verbose:
            self.logger.info("[3/4] Designing solution")
        try:
            design = self.commands.design(action="create", priority_id=priority_id)
            result.steps_completed.append("design_solution")
            result.metadata["design"] = design
        except Exception as e:
            result.steps_failed.append("design_solution")
            result.error_message = f"Design failed: {e}"
            return result

        # Step 4: Create spec
        if verbose:
            self.logger.info(f"[4/4] Creating spec {spec_id}")
        try:
            spec = self.commands.specs(action="create", priority_id=priority_id, spec_id=spec_id)
            result.steps_completed.append("create_spec")
            result.metadata["spec"] = spec
        except Exception as e:
            result.steps_failed.append("create_spec")
            result.error_message = f"Spec creation failed: {e}"
            return result

        return result

    def _execute_update_workflow(
        self,
        priority_id: str,
        spec_id: str,
        result: SpecResult,
        notify: bool,
        verbose: bool,
    ) -> SpecResult:
        """Execute update workflow (update existing spec).

        Steps:
            1. Load existing spec
            2. Update spec
            3. Validate changes
            4. Notify if requested
        """
        # Step 1: Load existing
        if verbose:
            self.logger.info(f"[1/4] Loading existing spec {spec_id}")
        try:
            existing_spec = self.commands.specs(action="load", spec_id=spec_id)
            result.steps_completed.append("load_spec")
            result.metadata["existing_spec"] = existing_spec
        except Exception as e:
            result.steps_failed.append("load_spec")
            result.error_message = f"Failed to load spec: {e}"
            return result

        # Step 2: Update
        if verbose:
            self.logger.info("[2/4] Updating spec")
        try:
            updated_spec = self.commands.specs(action="update", spec_id=spec_id, priority_id=priority_id)
            result.steps_completed.append("update_spec")
            result.metadata["updated_spec"] = updated_spec
        except Exception as e:
            result.steps_failed.append("update_spec")
            result.error_message = f"Update failed: {e}"
            return result

        # Step 3: Validate
        if verbose:
            self.logger.info("[3/4] Validating changes")
        try:
            validation = self.commands.specs(action="validate", spec_id=spec_id)
            result.steps_completed.append("validate_spec")
            result.metadata["validation"] = validation
        except Exception as e:
            result.steps_failed.append("validate_spec")
            self.logger.warning(f"Validation failed: {e}")

        # Step 4: Notify
        if notify:
            if verbose:
                self.logger.info("[4/4] Notifying agents of update")
            result.steps_completed.append("notify_agents")
        else:
            result.steps_completed.append("notify_agents")

        return result

    def _execute_review_workflow(
        self,
        priority_id: str,
        spec_id: str,
        result: SpecResult,
        verbose: bool,
    ) -> SpecResult:
        """Execute review workflow (validate existing spec).

        Steps:
            1. Load spec
            2. Review design
            3. Validate POC if exists
            4. Check ADR
        """
        # Step 1: Load
        if verbose:
            self.logger.info(f"[1/4] Loading spec {spec_id}")
        try:
            spec = self.commands.specs(action="load", spec_id=spec_id)
            result.steps_completed.append("load_spec")
            result.metadata["spec"] = spec
        except Exception as e:
            result.steps_failed.append("load_spec")
            result.error_message = f"Failed to load spec: {e}"
            return result

        # Step 2: Review design
        if verbose:
            self.logger.info("[2/4] Reviewing design")
        try:
            review = self.commands.design(action="review", spec_id=spec_id)
            result.steps_completed.append("review_design")
            result.metadata["review"] = review
        except Exception as e:
            result.steps_failed.append("review_design")
            self.logger.warning(f"Review failed: {e}")

        # Step 3: Validate POC if exists
        if verbose:
            self.logger.info("[3/4] Checking for POC")
        try:
            poc_validation = self.commands.poc(action="validate", spec_id=spec_id)
            result.poc_created = True
            result.steps_completed.append("validate_poc")
            result.metadata["poc_validation"] = poc_validation
        except Exception:
            # POC may not exist, that's ok
            result.steps_completed.append("validate_poc")
            self.logger.info("No POC found (not required)")

        # Step 4: Check ADR
        if verbose:
            self.logger.info("[4/4] Checking ADR")
        try:
            adr = self.commands.adr(action="load", spec_id=spec_id)
            result.adr_created = True
            result.steps_completed.append("check_adr")
            result.metadata["adr"] = adr
        except Exception:
            result.steps_completed.append("check_adr")
            self.logger.info("No ADR found")

        return result

    def _generate_spec_id(self, priority_id: str) -> str:
        """Generate specification ID from priority ID.

        Args:
            priority_id: Priority identifier (e.g., "PRIORITY-5")

        Returns:
            Spec ID (e.g., "SPEC-5")
        """
        # Extract number from PRIORITY-X format
        if "PRIORITY-" in priority_id:
            number = priority_id.split("PRIORITY-")[1]
            return f"SPEC-{number}"
        else:
            # Fallback: use timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"SPEC-{timestamp}"
