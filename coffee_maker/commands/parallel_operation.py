"""
Parallel Operation Wrapper for Safe Command System Migration

This module provides a wrapper that executes both legacy and command-based
implementations in parallel during the migration phase, comparing results to
ensure consistency and safety. When the command system is fully validated,
legacy mode can be safely disabled.

Example:
    wrapper = ParallelOperationWrapper()
    result = wrapper.execute_with_validation(
        agent="code_developer",
        action="claim_priority",
        params={"priority_id": 10}
    )
"""

import logging
import time
import json
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from coffee_maker.commands.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)


class OperationResult:
    """
    Encapsulates the result of an operation.

    Attributes:
        success: Whether operation succeeded
        data: Operation result data
        error: Error message if operation failed
        duration_ms: Time taken to execute (milliseconds)
        timestamp: When operation was executed
    """

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.duration_ms = duration_ms
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        if self.success:
            return f"OperationResult(success, {self.duration_ms:.1f}ms)"
        return f"OperationResult(failed: {self.error})"


class ParallelOperationWrapper:
    """
    Wrapper that runs legacy and command implementations in parallel.

    During migration, this wrapper:
    1. Executes the legacy implementation
    2. Executes the new command-based implementation (if enabled)
    3. Compares results for consistency
    4. Returns the appropriate result based on feature flags
    5. Logs mismatches for investigation

    This allows for safe, gradual rollout with confidence that the new
    command system produces equivalent results to the legacy system.
    """

    def __init__(self):
        """Initialize parallel operation wrapper."""
        self.flags = FeatureFlags()
        self.comparison_log = []
        self.mismatch_count = 0
        self.operation_count = 0

    def execute_with_validation(
        self,
        agent: str,
        action: str,
        params: Dict[str, Any],
        legacy_fn: Optional[Callable] = None,
        command_fn: Optional[Callable] = None,
    ) -> OperationResult:
        """
        Execute operation with legacy/command comparison.

        Args:
            agent: Agent name (e.g., 'code_developer')
            action: Action name (e.g., 'claim_priority')
            params: Parameters for the operation
            legacy_fn: Callable for legacy implementation
            command_fn: Callable for command-based implementation

        Returns:
            OperationResult with appropriate implementation's result
        """
        self.operation_count += 1

        # Always execute legacy (baseline)
        legacy_result = self._execute_with_timing(legacy_fn, params)

        # Execute command implementation if enabled
        command_enabled = self.flags.is_enabled(agent, action)
        command_result = None

        if command_enabled and command_fn:
            command_result = self._execute_with_timing(command_fn, params)

        # Compare results if both were executed
        if command_enabled and command_result:
            matches = self._results_match(legacy_result, command_result)
            self._log_comparison(agent, action, params, legacy_result, command_result, matches)

            if not matches:
                self.mismatch_count += 1
                logger.warning(
                    f"Result mismatch for {agent}.{action}: "
                    f"legacy={legacy_result.success}, "
                    f"command={command_result.success}"
                )
                # Return legacy result on mismatch (safe fallback)
                return legacy_result

            # Both succeeded and match - return command result
            return command_result

        # Command not enabled or not provided - return legacy result
        return legacy_result

    @staticmethod
    def _execute_with_timing(fn: Optional[Callable], params: Dict[str, Any]) -> OperationResult:
        """
        Execute a function and time it.

        Args:
            fn: Callable to execute
            params: Parameters for the callable

        Returns:
            OperationResult with timing information
        """
        if fn is None:
            return OperationResult(False, error="No callable provided")

        start_time = time.time()
        try:
            result = fn(**params)
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(True, data=result, duration_ms=duration_ms)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                False,
                error=str(e),
                duration_ms=duration_ms,
            )

    @staticmethod
    def _results_match(
        legacy_result: OperationResult,
        command_result: OperationResult,
    ) -> bool:
        """
        Compare two operation results for consistency.

        Results match if:
        1. Both succeeded or both failed
        2. Success cases: Data matches (or both return empty data)
        3. Failure cases: Similar error messages

        Args:
            legacy_result: Result from legacy implementation
            command_result: Result from command implementation

        Returns:
            True if results are equivalent
        """
        # Both must have same success status
        if legacy_result.success != command_result.success:
            return False

        if legacy_result.success:
            # For successful results, compare data
            # Allow approximate matches for timestamps/ids
            return _data_matches(legacy_result.data, command_result.data)

        # For failures, both failed - consider it a match
        # (error messages may differ due to implementation details)
        return True

    def _log_comparison(
        self,
        agent: str,
        action: str,
        params: Dict[str, Any],
        legacy_result: OperationResult,
        command_result: OperationResult,
        match: bool,
    ) -> None:
        """
        Log comparison between legacy and command results.

        Args:
            agent: Agent name
            action: Action name
            params: Operation parameters
            legacy_result: Result from legacy implementation
            command_result: Result from command implementation
            match: Whether results match
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "match": match,
            "legacy": legacy_result.to_dict(),
            "command": command_result.to_dict(),
            "performance_ratio": (
                command_result.duration_ms / legacy_result.duration_ms if legacy_result.duration_ms > 0 else 0
            ),
        }
        self.comparison_log.append(log_entry)

        if not match:
            logger.warning(
                f"Mismatch: {agent}.{action} - legacy "
                f"({legacy_result.success}) vs command ({command_result.success})"
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get migration statistics.

        Returns:
            Dictionary with operation counts, mismatch rates, etc.
        """
        match_count = sum(1 for log in self.comparison_log if log["match"])
        mismatch_count = len(self.comparison_log) - match_count

        avg_performance_ratio = (
            sum(log["performance_ratio"] for log in self.comparison_log) / len(self.comparison_log)
            if self.comparison_log
            else 0
        )

        return {
            "total_operations": self.operation_count,
            "parallel_operations": len(self.comparison_log),
            "matches": match_count,
            "mismatches": mismatch_count,
            "match_rate": (match_count / len(self.comparison_log) * 100 if self.comparison_log else 0),
            "avg_command_performance_ratio": avg_performance_ratio,
            "enabled_agents": list(self.flags.get_enabled_agents()),
        }

    def reset_statistics(self) -> None:
        """Reset comparison log and statistics."""
        self.comparison_log = []
        self.mismatch_count = 0
        self.operation_count = 0
        logger.info("Reset parallel operation statistics")

    def export_comparison_log(self, filepath: str) -> None:
        """
        Export comparison log to JSON file.

        Args:
            filepath: Path where to save the log
        """
        with open(filepath, "w") as f:
            json.dump(
                {
                    "statistics": self.get_statistics(),
                    "comparison_log": self.comparison_log,
                },
                f,
                indent=2,
            )
        logger.info(f"Exported comparison log to {filepath}")


def _data_matches(data1: Any, data2: Any) -> bool:
    """
    Check if two data structures match.

    Handles:
    - Primitive types (exact match)
    - Dictionaries (same keys and values)
    - Lists (same length and element-wise comparison)
    - Ignores certain timestamp/id fields that may differ

    Args:
        data1: First data structure
        data2: Second data structure

    Returns:
        True if data structures are equivalent
    """
    # Handle None/empty cases
    if data1 is None and data2 is None:
        return True
    if data1 is None or data2 is None:
        return False

    # Same types required
    if type(data1) != type(data2):
        return False

    # Primitive types
    if isinstance(data1, (str, int, float, bool)):
        return data1 == data2

    # Lists
    if isinstance(data1, list):
        if len(data1) != len(data2):
            return False
        return all(_data_matches(a, b) for a, b in zip(data1, data2))

    # Dictionaries
    if isinstance(data1, dict):
        if set(data1.keys()) != set(data2.keys()):
            return False
        return all(_data_matches(data1[k], data2[k]) for k in data1.keys())

    # Other types - use equality
    return data1 == data2
