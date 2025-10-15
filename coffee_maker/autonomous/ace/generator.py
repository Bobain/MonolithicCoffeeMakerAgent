"""Generator component for ACE framework.

The Generator wraps agent execution with dual observation, capturing both external
(git, files) and internal (reasoning, tools) observations for later analysis.
"""

import logging
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.ace.config import ACEConfig, get_default_config

logger = logging.getLogger(__name__)
from coffee_maker.autonomous.ace.models import (
    ComparativeObservations,
    Execution,
    ExecutionTrace,
    ExternalObservation,
    InternalObservation,
)
from coffee_maker.autonomous.ace.trace_manager import TraceManager


class ACEGenerator:
    """Generator component - wraps agent execution with observation.

    The Generator is responsible for:
    1. Executing the target agent twice (dual execution)
    2. Capturing external observations (git changes, files)
    3. Capturing internal observations (reasoning, tools, decisions)
    4. Performing comparative analysis between executions
    5. Saving execution traces for the Reflector

    Example:
        generator = ACEGenerator(
            agent_interface=claude_cli,
            config=config
        )

        result = generator.execute_with_trace(
            prompt="Implement feature X",
            priority_context={"priority": 5, "name": "Feature X"}
        )
    """

    def __init__(
        self,
        agent_interface: Any,
        config: Optional[ACEConfig] = None,
        agent_name: str = "code_developer",
        agent_objective: str = "Implement features from ROADMAP autonomously",
        success_criteria: str = "Code runs, tests pass, DoD verified, PR created",
    ):
        """Initialize Generator.

        Args:
            agent_interface: Interface to execute agent (e.g., ClaudeCLIInterface)
            config: ACE configuration (defaults to get_default_config())
            agent_name: Name of the target agent
            agent_objective: What the agent is designed to accomplish
            success_criteria: Explicit criteria for measuring success
        """
        self.agent_interface = agent_interface
        self.config = config or get_default_config()
        self.agent_name = agent_name
        self.agent_objective = agent_objective
        self.success_criteria = success_criteria

        # Ensure directories exist
        self.config.ensure_directories()

        # Initialize trace manager
        self.trace_manager = TraceManager(self.config.trace_dir)

        logger.info(f"ACEGenerator initialized for agent: {agent_name}")

    def execute_with_trace(
        self,
        prompt: str,
        priority_context: Optional[Dict[str, Any]] = None,
        parent_trace_id: Optional[str] = None,
        delegation_chain: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute agent with full ACE observation and tracing.

        Args:
            prompt: User query/task for the agent
            priority_context: Context about the priority being worked on
            parent_trace_id: Trace ID of delegating agent (if applicable)
            delegation_chain: List of agents in delegation chain
            **kwargs: Additional parameters to pass to agent

        Returns:
            Dictionary with result and trace_id

        Example:
            result = generator.execute_with_trace(
                prompt="Implement authentication",
                priority_context={"priority": 10, "name": "User Auth"},
                parent_trace_id="trace_123",
                delegation_chain=[{"agent": "user_listener", "trace_id": "trace_123"}]
            )
        """
        # Use microsecond-level timestamp to avoid collisions
        timestamp = datetime.now()
        trace_id = str(int(timestamp.timestamp() * 1000000))  # Microseconds since epoch

        logger.info(f"Starting ACE execution with trace_id: {trace_id}")

        # Build delegation chain
        if delegation_chain is None:
            delegation_chain = []
        else:
            # Make a copy to avoid mutating the input
            delegation_chain = delegation_chain.copy()

        # Add current agent to chain
        current_entry = {"agent": self.agent_name, "trace_id": trace_id, "timestamp": timestamp.isoformat()}
        delegation_chain.append(current_entry)

        if parent_trace_id:
            logger.info(f"Delegation from parent trace: {parent_trace_id}")

        # Create trace object
        trace = ExecutionTrace(
            trace_id=trace_id,
            timestamp=timestamp,
            agent_identity={
                "target_agent": self.agent_name,
                "agent_objective": self.agent_objective,
                "success_criteria": self.success_criteria,
            },
            user_query=prompt,
            current_context=self._load_current_context(),
            parent_trace_id=parent_trace_id,
            delegation_chain=delegation_chain,
        )

        # Execute first
        execution1 = self._execute_once(execution_id=1, prompt=prompt, **kwargs)

        # Conditional second execution
        should_run_second = self._should_run_second_execution(execution1)

        if should_run_second:
            execution2 = self._execute_once(execution_id=2, prompt=prompt, **kwargs)
            trace.executions = [execution1, execution2]
            trace.comparative_observations = self._compare_executions(execution1, execution2)
        else:
            trace.executions = [execution1]
            trace.comparative_observations = ComparativeObservations(
                consistency="single_execution",
                strategy_variance="Second execution skipped - see skip_reason",
                effectiveness_comparison="N/A",
                patterns_identified=[],
            )
            trace.skip_reason = self._get_skip_reason(execution1)

        # Identify helpful/problematic context (only if we have two executions)
        if should_run_second:
            trace.helpful_context_elements = self._identify_helpful_context(execution1, execution2)
            trace.problematic_context_elements = self._identify_problematic_context(execution1, execution2)

            # Identify new insights
            trace.new_insights_surfaced = self._identify_new_insights(execution1, execution2)
        else:
            trace.helpful_context_elements = []
            trace.problematic_context_elements = []
            trace.new_insights_surfaced = []

        # Write trace
        try:
            trace_path = self.trace_manager.write_trace(trace)
            logger.info(f"Trace written to: {trace_path}")
        except Exception as e:
            logger.error(f"Failed to write trace: {e}")

        # Return first execution result with agent's actual response
        return {
            "agent_result": execution1.agent_response,  # Actual agent result
            "result": execution1.result_status,  # success/failure status
            "trace_id": trace_id,
            "duration": execution1.duration_seconds,
            "errors": execution1.errors,
        }

    def _execute_once(self, execution_id: int, prompt: str, **kwargs) -> Execution:
        """Execute agent once and capture observations.

        Args:
            execution_id: 1 or 2
            prompt: User query
            **kwargs: Additional parameters

        Returns:
            Execution object with observations
        """
        logger.info(f"Starting execution {execution_id}")
        start_time = time.time()

        # Capture pre-execution state
        pre_state = self._capture_git_state()

        # Execute agent
        try:
            response = self.agent_interface.send_message(prompt, **kwargs)
            result_status = "success"
            errors = []
            agent_response = response  # Store actual response
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            response = {"error": str(e)}
            result_status = "failure"
            errors = [str(e)]
            agent_response = None  # No valid response on failure

        # Capture post-execution state
        post_state = self._capture_git_state()

        # Calculate duration
        duration = time.time() - start_time

        # Build external observation
        external_obs = self._diff_states(pre_state, post_state)

        # Build internal observation
        internal_obs = self._extract_internal_observation(response)

        # Build execution object
        execution = Execution(
            execution_id=execution_id,
            external_observation=external_obs,
            internal_observation=internal_obs,
            result_status=result_status,
            errors=errors,
            duration_seconds=duration,
            token_usage=(response.get("token_usage", 0) if isinstance(response, dict) else 0),
            agent_response=agent_response,  # Store agent's actual result
        )

        logger.info(f"Execution {execution_id} complete: {result_status}")
        return execution

    def _capture_git_state(self) -> Dict[str, Any]:
        """Capture current git state.

        Returns:
            Dictionary with git status, staged files, unstaged files
        """
        try:
            # Get git status
            status_output = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout

            # Parse status
            staged = []
            unstaged = []
            untracked = []

            for line in status_output.strip().split("\n"):
                if not line:
                    continue

                status = line[:2]
                filepath = line[3:]

                if status[0] != " " and status[0] != "?":
                    staged.append(filepath)
                if status[1] != " ":
                    unstaged.append(filepath)
                if status == "??":
                    untracked.append(filepath)

            return {
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "status_output": status_output,
            }
        except Exception as e:
            logger.warning(f"Failed to capture git state: {e}")
            return {"staged": [], "unstaged": [], "untracked": [], "status_output": ""}

    def _diff_states(self, pre: Dict[str, Any], post: Dict[str, Any]) -> ExternalObservation:
        """Calculate changes between pre and post git states.

        Args:
            pre: Pre-execution git state
            post: Post-execution git state

        Returns:
            ExternalObservation with detected changes
        """
        # Files created (new in untracked)
        files_created = list(set(post["untracked"]) - set(pre["untracked"]))

        # Files modified (new in staged or unstaged)
        files_modified = list(set(post["staged"] + post["unstaged"]) - set(pre["staged"] + pre["unstaged"]))

        # Files deleted would show up in status
        files_deleted = []

        # Git changes summary
        git_changes = []
        if files_created:
            git_changes.append(f"Created {len(files_created)} files")
        if files_modified:
            git_changes.append(f"Modified {len(files_modified)} files")

        return ExternalObservation(
            git_changes=git_changes,
            files_created=files_created,
            files_modified=files_modified,
            files_deleted=files_deleted,
            commands_executed=[],  # Would need to instrument agent to capture this
        )

    def _extract_internal_observation(self, response: Any) -> InternalObservation:
        """Extract internal observation from agent response.

        Args:
            response: Agent response (format varies by interface)

        Returns:
            InternalObservation
        """
        # This is a simplified version - in reality, we'd need to parse
        # the agent's actual reasoning steps, tool calls, etc.
        # The agent interface would need to provide this structured data.

        reasoning_steps = []
        decisions_made = []
        tools_called = []

        if isinstance(response, dict):
            # Try to extract reasoning if available
            if "reasoning" in response:
                reasoning_steps = response["reasoning"]
            if "decisions" in response:
                decisions_made = response["decisions"]
            if "tool_calls" in response:
                tools_called = response["tool_calls"]

        return InternalObservation(
            reasoning_steps=reasoning_steps,
            decisions_made=decisions_made,
            tools_called=tools_called,
            context_used=[],  # Would need playbook tracking
            context_ignored=[],  # Would need playbook tracking
        )

    def _compare_executions(self, exec1: Execution, exec2: Execution) -> ComparativeObservations:
        """Compare two executions and identify patterns.

        Args:
            exec1: First execution
            exec2: Second execution

        Returns:
            ComparativeObservations with analysis
        """
        # Check consistency
        consistency = "same_outcome" if exec1.result_status == exec2.result_status else "different_outcomes"

        # Analyze strategy variance
        strategy_variance = "Both executions followed similar approach"
        if len(exec1.external_observation.files_created) != len(exec2.external_observation.files_created):
            strategy_variance = "Different numbers of files created"

        # Effectiveness comparison
        effectiveness = "Both executions equally effective"
        if exec1.result_status == "success" and exec2.result_status == "failure":
            effectiveness = "Execution 1 was more effective"
        elif exec2.result_status == "success" and exec1.result_status == "failure":
            effectiveness = "Execution 2 was more effective"
        elif exec1.duration_seconds < exec2.duration_seconds:
            effectiveness = f"Execution 1 was faster ({exec1.duration_seconds:.2f}s vs {exec2.duration_seconds:.2f}s)"
        elif exec2.duration_seconds < exec1.duration_seconds:
            effectiveness = f"Execution 2 was faster ({exec2.duration_seconds:.2f}s vs {exec1.duration_seconds:.2f}s)"

        # Identify patterns
        patterns = []
        if exec1.result_status == exec2.result_status:
            patterns.append(f"Consistent result: {exec1.result_status}")
        if len(exec1.errors) > 0 and len(exec2.errors) > 0:
            patterns.append("Both executions encountered errors")

        return ComparativeObservations(
            consistency=consistency,
            strategy_variance=strategy_variance,
            effectiveness_comparison=effectiveness,
            patterns_identified=patterns,
        )

    def _identify_helpful_context(self, exec1: Execution, exec2: Execution) -> List[str]:
        """Identify context elements that were helpful.

        Args:
            exec1: First execution
            exec2: Second execution

        Returns:
            List of helpful context element IDs
        """
        # This would require tracking which playbook bullets were referenced
        # For now, return empty list
        return []

    def _identify_problematic_context(self, exec1: Execution, exec2: Execution) -> List[str]:
        """Identify context elements that were problematic.

        Args:
            exec1: First execution
            exec2: Second execution

        Returns:
            List of problematic context element IDs
        """
        # This would require tracking which playbook bullets caused issues
        # For now, return empty list
        return []

    def _identify_new_insights(self, exec1: Execution, exec2: Execution) -> List[str]:
        """Identify new insights not yet in context.

        Args:
            exec1: First execution
            exec2: Second execution

        Returns:
            List of new insight descriptions
        """
        insights = []

        # Check for consistent errors
        if exec1.errors and exec2.errors:
            common_errors = set(exec1.errors) & set(exec2.errors)
            if common_errors:
                insights.append(f"Consistent error pattern: {list(common_errors)[0]}")

        # Check for consistent file patterns
        common_files = set(exec1.external_observation.files_created) & set(exec2.external_observation.files_created)
        if common_files:
            insights.append(f"Consistently created files: {', '.join(list(common_files)[:3])}")

        return insights

    def _load_current_context(self) -> str:
        """Load current playbook context for the agent.

        Returns:
            Playbook snapshot as markdown string
        """
        # This would load the actual playbook
        # For now, return placeholder
        return f"# Playbook for {self.agent_name}\n\nNo playbook loaded yet."

    def _should_run_second_execution(self, exec1: Execution) -> bool:
        """Determine if second execution should run.

        Second execution only runs if:
        1. First execution was quick (< 30 seconds)
        2. No owned agent directories were modified

        Args:
            exec1: First execution result

        Returns:
            True if second execution should run, False otherwise
        """
        # Check duration threshold
        if exec1.duration_seconds >= 30:
            logger.info(f"Skipping second execution: duration {exec1.duration_seconds:.1f}s >= 30s threshold")
            return False

        # Check if owned directories were modified
        owned_dirs_modified = self._check_owned_directories_modified(exec1.external_observation)
        if owned_dirs_modified:
            logger.info("Skipping second execution: owned directories were modified")
            return False

        logger.info("Running second execution: quick execution with no owned files modified")
        return True

    def _check_owned_directories_modified(self, external_obs: ExternalObservation) -> bool:
        """Check if any owned agent directories were modified.

        Owned directories are defined in .claude/agents/*.md for each agent.
        For code_developer: coffee_maker/, tests/, scripts/, pyproject.toml
        For project_manager: docs/, .claude/

        Args:
            external_obs: External observation from execution

        Returns:
            True if owned directories modified, False otherwise
        """
        # Define owned directories per agent
        # TODO: Could load this from agent config in future
        owned_dirs = {
            "code_developer": ["coffee_maker/", "tests/", "scripts/", "pyproject.toml"],
            "project_manager": ["docs/", ".claude/"],
            "user_listener": [],  # UI only, no file ownership
            "assistant": [],  # Documentation expert, no file ownership
            "code-searcher": ["docs/code-searcher/"],
            "curator": ["docs/curator/"],
            "reflector": ["docs/reflector/"],
            "generator": ["docs/generator/"],
        }

        agent_owned = owned_dirs.get(self.agent_name, [])

        # Check if any created or modified files are in owned directories
        all_changed_files = external_obs.files_created + external_obs.files_modified + external_obs.files_deleted

        for file_path in all_changed_files:
            for owned_dir in agent_owned:
                if file_path.startswith(owned_dir):
                    logger.debug(f"Owned file modified: {file_path} in {owned_dir}")
                    return True

        return False

    def _get_skip_reason(self, exec1: Execution) -> str:
        """Get human-readable reason why second execution was skipped.

        Args:
            exec1: First execution

        Returns:
            Skip reason string
        """
        if exec1.duration_seconds >= 30:
            return f"Second execution skipped: first execution took {exec1.duration_seconds:.1f}s (>= 30s threshold). Long executions are expensive to duplicate."

        if self._check_owned_directories_modified(exec1.external_observation):
            modified = exec1.external_observation.files_created + exec1.external_observation.files_modified
            return f"Second execution skipped: owned directories were modified ({len(modified)} files changed). Real work was done, comparison less valuable."

        return "Second execution skipped: unknown reason"

    def attach_satisfaction(self, trace_id: str, satisfaction_data: Dict[str, Any]) -> None:
        """Attach user satisfaction feedback to existing trace.

        This method loads an existing trace and adds user satisfaction data.
        The satisfaction data is used by the Reflector to weight insights:
        - High satisfaction (4-5) → Success patterns
        - Low satisfaction (1-2) → Failure modes

        Args:
            trace_id: ID of trace to update
            satisfaction_data: User satisfaction dict with keys:
                - score (int): 1-5 rating
                - positive_feedback (str): What worked well
                - improvement_areas (str): What could be improved
                - timestamp (str): ISO timestamp of feedback

        Raises:
            FileNotFoundError: If trace doesn't exist
            ValueError: If satisfaction_data is invalid

        Example:
            >>> generator = ACEGenerator(agent_interface=cli)
            >>> generator.attach_satisfaction("trace_123", {
            ...     "score": 4,
            ...     "positive_feedback": "Fast and accurate",
            ...     "improvement_areas": "Could add more tests",
            ...     "timestamp": "2025-10-15T12:00:00"
            ... })
        """
        # Validate satisfaction data
        if not satisfaction_data:
            raise ValueError("satisfaction_data cannot be empty")

        if "score" not in satisfaction_data:
            raise ValueError("satisfaction_data must contain 'score' field")

        score = satisfaction_data["score"]
        if not isinstance(score, int) or not (1 <= score <= 5):
            raise ValueError(f"score must be integer between 1-5, got: {score}")

        logger.info(f"Attaching satisfaction (score={score}) to trace: {trace_id}")

        try:
            # Load existing trace
            trace = self.trace_manager.read_trace(trace_id)

            # Attach satisfaction
            trace.user_satisfaction = satisfaction_data

            # Save updated trace
            self.trace_manager.write_trace(trace)

            logger.info(f"Successfully attached satisfaction to trace: {trace_id}")

        except FileNotFoundError:
            logger.error(f"Trace not found: {trace_id}")
            raise
        except Exception as e:
            logger.error(f"Failed to attach satisfaction to trace {trace_id}: {e}")
            raise
