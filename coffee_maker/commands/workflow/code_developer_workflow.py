"""Code Developer Workflow Command - Ultra-Consolidated.

Single workflow command that handles the entire development lifecycle:
spec → code → test → commit

Replaces 6 consolidated commands with 1 workflow command.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from coffee_maker.commands.consolidated.code_developer_commands import (
    CodeDeveloperCommands,
)
from coffee_maker.config.logging_config import get_logger

logger = get_logger(__name__)


class WorkMode(Enum):
    """Execution modes for work() command."""

    AUTO = "auto"  # Full workflow, autonomous
    STEP = "step"  # Interactive, step-by-step
    TEST_ONLY = "test-only"  # Just run tests
    COMMIT_ONLY = "commit-only"  # Just commit existing changes
    CODE_ONLY = "code-only"  # Just write code, no tests/commit


class WorkStatus(Enum):
    """Status of work execution."""

    SUCCESS = "success"
    PARTIAL = "partial"  # Some steps succeeded
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkResult:
    """Result of work() execution.

    Attributes:
        status: Overall work status
        task_id: Task that was worked on
        steps_completed: List of completed step names
        steps_failed: List of failed step names
        files_changed: List of files that were modified
        tests_run: Number of tests run
        tests_passed: Number of tests that passed
        commit_sha: Git commit SHA if committed
        duration_seconds: Total execution time
        error_message: Error message if failed
        metadata: Additional workflow metadata
    """

    status: WorkStatus
    task_id: str
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    tests_run: int = 0
    tests_passed: int = 0
    commit_sha: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Work Result: {self.status.value}",
            f"Task: {self.task_id}",
            f"Steps: {len(self.steps_completed)} completed, {len(self.steps_failed)} failed",
        ]
        if self.files_changed:
            lines.append(f"Files: {len(self.files_changed)} changed")
        if self.tests_run > 0:
            lines.append(f"Tests: {self.tests_passed}/{self.tests_run} passed")
        if self.commit_sha:
            lines.append(f"Commit: {self.commit_sha[:8]}")
        if self.duration_seconds > 0:
            lines.append(f"Duration: {self.duration_seconds:.1f}s")
        if self.error_message:
            lines.append(f"Error: {self.error_message}")
        return "\n".join(lines)


class CodeDeveloperWorkflow:
    """Ultra-consolidated workflow command for code development.

    Single command that handles complete development workflow:
        1. Load task/spec from database
        2. Analyze requirements
        3. Generate/modify code
        4. Run tests automatically
        5. Fix any test failures (if auto mode)
        6. Run quality checks (black, mypy, pre-commit)
        7. Commit with conventional message
        8. Update task status

    Example:
        >>> workflow = CodeDeveloperWorkflow()
        >>> result = workflow.work(task_id="TASK-31-1")
        >>> print(result)
        Work Result: success
        Task: TASK-31-1
        Steps: 7 completed, 0 failed
        Files: 3 changed
        Tests: 15/15 passed
        Commit: abc123def
        Duration: 45.2s

    Replaces:
        - implement(action="load|write_code|refactor")
        - test(action="run|fix|generate")
        - docs(action="update|generate")
        - git(action="commit|create_pr")
        - quality(action="pre_commit|type_check")
        - refactor(action="optimize|simplify")
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize workflow with consolidated commands.

        Args:
            db_path: Optional path to SQLite database
        """
        self.commands = CodeDeveloperCommands(db_path)
        self.logger = logger

    def work(
        self,
        task_id: str,
        mode: str = "auto",
        skip_tests: bool = False,
        skip_quality: bool = False,
        auto_commit: bool = True,
        commit_message: Optional[str] = None,
        verbose: bool = False,
    ) -> WorkResult:
        """Execute complete development workflow for a task.

        This is the ONE command code_developer needs. It handles everything
        from loading the spec to committing the final code.

        Args:
            task_id: Task to implement (required)
            mode: Execution mode - "auto"|"step"|"test-only"|"commit-only"|"code-only"
            skip_tests: Skip test execution (default: False)
            skip_quality: Skip quality checks (default: False)
            auto_commit: Auto-commit on success (default: True)
            commit_message: Custom commit message (optional, auto-generated if not provided)
            verbose: Enable verbose logging (default: False)

        Returns:
            WorkResult with execution details

        Raises:
            ValueError: If task_id is invalid or mode is unknown
            RuntimeError: If critical workflow step fails

        Example:
            # Simple autonomous mode
            result = workflow.work(task_id="TASK-31-1")

            # Step-by-step interactive
            result = workflow.work(task_id="TASK-31-1", mode="step")

            # Just run tests
            result = workflow.work(task_id="TASK-31-1", mode="test-only")

            # Code without committing
            result = workflow.work(
                task_id="TASK-31-1",
                auto_commit=False
            )
        """
        start_time = datetime.now()
        result = WorkResult(status=WorkStatus.SUCCESS, task_id=task_id)

        try:
            # Validate mode
            try:
                work_mode = WorkMode(mode)
            except ValueError:
                raise ValueError(f"Invalid mode '{mode}'. " f"Must be one of: {', '.join(m.value for m in WorkMode)}")

            self.logger.info(f"Starting work on {task_id} in {mode} mode")

            # Execute workflow based on mode
            if work_mode == WorkMode.AUTO:
                result = self._execute_full_workflow(
                    task_id=task_id,
                    result=result,
                    skip_tests=skip_tests,
                    skip_quality=skip_quality,
                    auto_commit=auto_commit,
                    commit_message=commit_message,
                    verbose=verbose,
                )
            elif work_mode == WorkMode.STEP:
                result = self._execute_step_by_step(
                    task_id=task_id,
                    result=result,
                    skip_tests=skip_tests,
                    skip_quality=skip_quality,
                    auto_commit=auto_commit,
                    verbose=verbose,
                )
            elif work_mode == WorkMode.TEST_ONLY:
                result = self._execute_tests_only(task_id=task_id, result=result, verbose=verbose)
            elif work_mode == WorkMode.COMMIT_ONLY:
                result = self._execute_commit_only(
                    task_id=task_id,
                    result=result,
                    commit_message=commit_message,
                    verbose=verbose,
                )
            elif work_mode == WorkMode.CODE_ONLY:
                result = self._execute_code_only(task_id=task_id, result=result, verbose=verbose)

            # Calculate duration
            end_time = datetime.now()
            result.duration_seconds = (end_time - start_time).total_seconds()

            # Determine final status
            if len(result.steps_failed) == 0:
                result.status = WorkStatus.SUCCESS
            elif len(result.steps_completed) > 0:
                result.status = WorkStatus.PARTIAL
            else:
                result.status = WorkStatus.FAILED

            self.logger.info(f"Work completed: {result.status.value} ({result.duration_seconds:.1f}s)")
            return result

        except Exception as e:
            result.status = WorkStatus.FAILED
            result.error_message = str(e)
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Work failed: {e}")
            return result

    def _execute_full_workflow(
        self,
        task_id: str,
        result: WorkResult,
        skip_tests: bool,
        skip_quality: bool,
        auto_commit: bool,
        commit_message: Optional[str],
        verbose: bool,
    ) -> WorkResult:
        """Execute full autonomous workflow.

        Steps:
            1. Load task/spec
            2. Write code
            3. Run tests (if not skipped)
            4. Fix test failures (up to 3 attempts)
            5. Run quality checks (if not skipped)
            6. Commit (if auto_commit)
        """
        # Step 1: Load task/spec
        if verbose:
            self.logger.info(f"[1/6] Loading task {task_id}")
        try:
            task_data = self.commands.implement(action="load", task_id=task_id)
            result.steps_completed.append("load_task")
            result.metadata["task_data"] = task_data
        except Exception as e:
            result.steps_failed.append("load_task")
            result.error_message = f"Failed to load task: {e}"
            return result

        # Step 2: Write code
        if verbose:
            self.logger.info("[2/6] Writing code")
        try:
            code_result = self.commands.implement(action="write_code", task_id=task_id)
            result.steps_completed.append("write_code")
            if isinstance(code_result, dict) and "files" in code_result:
                result.files_changed.extend(code_result["files"])
        except Exception as e:
            result.steps_failed.append("write_code")
            result.error_message = f"Failed to write code: {e}"
            return result

        # Step 3: Run tests
        if not skip_tests:
            if verbose:
                self.logger.info("[3/6] Running tests")
            test_success = False
            attempts = 0
            max_attempts = 3

            while not test_success and attempts < max_attempts:
                attempts += 1
                try:
                    test_result = self.commands.test(action="run", task_id=task_id)
                    if isinstance(test_result, dict):
                        result.tests_run = test_result.get("total", 0)
                        result.tests_passed = test_result.get("passed", 0)
                        test_success = result.tests_passed == result.tests_run

                    if test_success:
                        result.steps_completed.append("run_tests")
                        break
                    elif attempts < max_attempts:
                        # Try to fix failing tests
                        if verbose:
                            self.logger.info(f"[3/6] Fixing test failures (attempt {attempts}/{max_attempts})")
                        try:
                            self.commands.test(action="fix", task_id=task_id)
                        except Exception as fix_error:
                            self.logger.warning(f"Auto-fix attempt failed: {fix_error}")
                            break
                except Exception as e:
                    result.steps_failed.append("run_tests")
                    result.error_message = f"Tests failed: {e}"
                    break

            if not test_success:
                result.steps_failed.append("run_tests")
                if not result.error_message:
                    result.error_message = f"Tests failed: {result.tests_passed}/{result.tests_run} passed"
        else:
            result.steps_completed.append("run_tests")
            result.metadata["tests_skipped"] = True

        # Step 4: Quality checks
        if not skip_quality:
            if verbose:
                self.logger.info("[4/6] Running quality checks")
            try:
                quality_result = self.commands.quality(action="pre_commit", task_id=task_id)
                result.steps_completed.append("quality_checks")
                result.metadata["quality_result"] = quality_result
            except Exception as e:
                result.steps_failed.append("quality_checks")
                result.error_message = f"Quality checks failed: {e}"
                # Continue anyway - quality checks are not blocking
        else:
            result.steps_completed.append("quality_checks")
            result.metadata["quality_skipped"] = True

        # Step 5: Commit
        if auto_commit and len(result.steps_failed) == 0:
            if verbose:
                self.logger.info("[5/6] Committing changes")
            try:
                # Generate commit message if not provided
                if not commit_message:
                    commit_message = self._generate_commit_message(task_id, result)

                commit_sha = self.commands.git(
                    action="commit",
                    message=commit_message,
                    files=result.files_changed if result.files_changed else None,
                )
                result.commit_sha = commit_sha
                result.steps_completed.append("commit")
            except Exception as e:
                result.steps_failed.append("commit")
                result.error_message = f"Commit failed: {e}"
        else:
            if verbose:
                self.logger.info("[5/6] Skipping commit (auto_commit=False or failures detected)")
            result.metadata["commit_skipped"] = True

        return result

    def _execute_step_by_step(
        self,
        task_id: str,
        result: WorkResult,
        skip_tests: bool,
        skip_quality: bool,
        auto_commit: bool,
        verbose: bool,
    ) -> WorkResult:
        """Execute workflow step-by-step with user confirmation.

        Similar to full workflow but prompts user before each step.
        """
        # TODO: Implement interactive step-by-step mode
        # For now, delegate to full workflow
        self.logger.warning("Step mode not yet implemented, using auto mode")
        return self._execute_full_workflow(
            task_id=task_id,
            result=result,
            skip_tests=skip_tests,
            skip_quality=skip_quality,
            auto_commit=auto_commit,
            commit_message=None,
            verbose=verbose,
        )

    def _execute_tests_only(self, task_id: str, result: WorkResult, verbose: bool) -> WorkResult:
        """Execute tests only, no code changes."""
        if verbose:
            self.logger.info("Running tests only")
        try:
            test_result = self.commands.test(action="run", task_id=task_id)
            if isinstance(test_result, dict):
                result.tests_run = test_result.get("total", 0)
                result.tests_passed = test_result.get("passed", 0)
            result.steps_completed.append("run_tests")
        except Exception as e:
            result.steps_failed.append("run_tests")
            result.error_message = f"Tests failed: {e}"

        return result

    def _execute_commit_only(
        self,
        task_id: str,
        result: WorkResult,
        commit_message: Optional[str],
        verbose: bool,
    ) -> WorkResult:
        """Commit existing changes only."""
        if verbose:
            self.logger.info("Committing existing changes")
        try:
            if not commit_message:
                commit_message = self._generate_commit_message(task_id, result)

            commit_sha = self.commands.git(action="commit", message=commit_message)
            result.commit_sha = commit_sha
            result.steps_completed.append("commit")
        except Exception as e:
            result.steps_failed.append("commit")
            result.error_message = f"Commit failed: {e}"

        return result

    def _execute_code_only(self, task_id: str, result: WorkResult, verbose: bool) -> WorkResult:
        """Write code only, no tests or commit."""
        if verbose:
            self.logger.info("Writing code only")
        try:
            # Load task
            task_data = self.commands.implement(action="load", task_id=task_id)
            result.steps_completed.append("load_task")

            # Write code
            code_result = self.commands.implement(action="write_code", task_id=task_id)
            result.steps_completed.append("write_code")
            if isinstance(code_result, dict) and "files" in code_result:
                result.files_changed.extend(code_result["files"])
        except Exception as e:
            result.steps_failed.append("write_code")
            result.error_message = f"Code generation failed: {e}"

        return result

    def _generate_commit_message(self, task_id: str, result: WorkResult) -> str:
        """Generate conventional commit message.

        Args:
            task_id: Task identifier
            result: Current work result

        Returns:
            Formatted commit message
        """
        # Extract task info from result metadata
        task_data = result.metadata.get("task_data", {})
        spec_id = task_data.get("spec_id", "")
        description = task_data.get("description", f"Implement {task_id}")

        # Determine commit type based on task
        commit_type = "feat"  # Default to feature
        if "fix" in description.lower() or "bug" in description.lower():
            commit_type = "fix"
        elif "refactor" in description.lower():
            commit_type = "refactor"
        elif "test" in description.lower():
            commit_type = "test"
        elif "docs" in description.lower() or "doc" in description.lower():
            commit_type = "docs"

        # Build commit message
        lines = [f"{commit_type}: {description}"]

        # Add body with details
        if spec_id:
            lines.append("")
            lines.append(f"Implements {spec_id}")
        if result.files_changed:
            lines.append(f"Modified {len(result.files_changed)} files")
        if result.tests_run > 0:
            lines.append(f"Tests: {result.tests_passed}/{result.tests_run} passing")

        # Add footer
        lines.extend(
            [
                "",
                "🤖 Generated with [Claude Code](https://claude.com/claude-code)",
                "",
                "Co-Authored-By: Claude <noreply@anthropic.com>",
            ]
        )

        return "\n".join(lines)
