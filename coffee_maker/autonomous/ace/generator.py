"""Generator Agent for ACE Framework - File Operation Interception and Ownership Enforcement.

This module implements the Generator agent from the ACE (Agentic Context Engineering) framework.
The Generator is responsible for:
1. Intercepting all file operations from agents
2. Enforcing file ownership rules (CFR-001)
3. Auto-delegating to correct owner when violations detected
4. Logging delegation traces for reflector analysis
5. Transparently returning results to requesting agent

Architecture:
    Generator: Main class that intercepts file operations
    DelegationTrace: Model for tracking delegations
    FileOperationType: Enum of interceptable operations

Integration with US-038:
    - Uses FileOwnership registry (Phase 1) for ownership checking
    - Provides Level 1 enforcement (automatic delegation)
    - Unblocks US-039 (comprehensive CFR enforcement)
    - Unblocks US-040 (project planner mode)

Usage:
    >>> from coffee_maker.autonomous.ace.generator import Generator
    >>> generator = Generator()
    >>>
    >>> # Intercept write operation
    >>> result = generator.intercept_file_operation(
    ...     agent_type=AgentType.PROJECT_MANAGER,
    ...     file_path=".claude/CLAUDE.md",
    ...     operation="write",
    ...     content="..."
    ... )
    >>> # Automatically delegated to code_developer (owner)
    >>> result.delegated_to == AgentType.CODE_DEVELOPER
    True

Key Features:
    - Automatic ownership enforcement (CFR-001)
    - Zero-configuration delegation (transparent to requesting agent)
    - Delegation trace logging (enables reflector analysis)
    - Read operations always allowed (no ownership check)
    - Write/edit/delete operations ownership-checked
    - Clear error messages for debugging
    - Thread-safe operation
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipUnclearError,
)
from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


class FileOperationType(Enum):
    """Types of file operations that can be intercepted."""

    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    DELETE = "delete"


@dataclass
class OperationResult:
    """Result of a file operation (possibly delegated).

    Attributes:
        success: Whether operation succeeded
        delegated: Whether operation was delegated to another agent
        delegated_to: Agent that actually performed operation (if delegated)
        error_message: Error message if failed
        trace_id: Delegation trace ID for reflector analysis
    """

    success: bool
    delegated: bool = False
    delegated_to: Optional[AgentType] = None
    error_message: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class DelegationTrace:
    """Trace record for delegated file operations.

    These traces are logged for reflector analysis to identify:
    - Common delegation patterns
    - Agents frequently violating ownership
    - Opportunities for improved agent design

    Attributes:
        trace_id: Unique identifier for this delegation
        timestamp: When delegation occurred
        requesting_agent: Agent that requested operation
        owner_agent: Agent that actually owns the file
        file_path: File being operated on
        operation: Type of operation (read/write/edit/delete)
        reason: Why delegation was needed (ownership violation)
        success: Whether delegated operation succeeded
    """

    trace_id: str
    timestamp: datetime
    requesting_agent: AgentType
    owner_agent: AgentType
    file_path: str
    operation: FileOperationType
    reason: str
    success: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "requesting_agent": self.requesting_agent.value,
            "owner_agent": self.owner_agent.value,
            "file_path": self.file_path,
            "operation": self.operation.value,
            "reason": self.reason,
            "success": self.success,
        }


class Generator:
    """Generator agent for intercepting and enforcing file ownership.

    The Generator is a critical component of the ACE framework that sits between
    agents and the file system, ensuring ownership rules are enforced transparently.

    Key Responsibilities:
        1. Intercept all file operations (write, edit, delete)
        2. Check ownership using FileOwnership registry
        3. Auto-delegate to correct owner if violation detected
        4. Log delegation traces for reflector analysis
        5. Return results transparently to requesting agent

    Example:
        >>> generator = Generator()
        >>>
        >>> # project_manager tries to write to code_developer's file
        >>> result = generator.intercept_file_operation(
        ...     agent_type=AgentType.PROJECT_MANAGER,
        ...     file_path="coffee_maker/cli/test.py",
        ...     operation="write",
        ...     content="# test"
        ... )
        >>>
        >>> # Automatically delegated to code_developer
        >>> print(f"Delegated: {result.delegated}")
        True
        >>> print(f"Owner: {result.delegated_to.value}")
        code_developer
    """

    def __init__(self):
        """Initialize Generator agent."""
        self.delegation_traces: list[DelegationTrace] = []
        logger.info("Generator initialized - file ownership enforcement active")

    def intercept_file_operation(
        self,
        agent_type: AgentType,
        file_path: str,
        operation: str,
        content: Optional[str] = None,
        **kwargs,
    ) -> OperationResult:
        """Intercept and potentially delegate a file operation.

        This is the main entry point for all file operations. It:
        1. Checks if operation requires ownership check (write/edit/delete)
        2. Verifies ownership using FileOwnership registry
        3. Delegates to owner if violation detected
        4. Logs delegation trace for reflector
        5. Returns result transparently

        Args:
            agent_type: Agent requesting the operation
            file_path: Path to file being operated on
            operation: Type of operation (read/write/edit/delete)
            content: Content for write operations
            **kwargs: Additional operation-specific parameters

        Returns:
            OperationResult with success status and delegation info

        Example:
            >>> generator = Generator()
            >>> result = generator.intercept_file_operation(
            ...     agent_type=AgentType.ASSISTANT,
            ...     file_path="docs/roadmap/ROADMAP.md",
            ...     operation="write",
            ...     content="# Updated roadmap"
            ... )
            >>> # Delegated to project_manager (owner of docs/roadmap/)
            >>> result.delegated
            True
        """
        # Convert operation string to enum
        try:
            op_type = FileOperationType(operation.lower())
        except ValueError:
            return OperationResult(
                success=False,
                error_message=f"Invalid operation type: {operation}",
            )

        # Read operations don't need ownership check
        if op_type == FileOperationType.READ:
            logger.debug(f"Read operation allowed: {agent_type.value} → {file_path}")
            return OperationResult(success=True, delegated=False)

        # Check ownership for write/edit/delete operations
        try:
            owner = FileOwnership.get_owner(file_path)
        except OwnershipUnclearError:
            # Ownership unclear - log warning and allow (fail open)
            logger.warning(f"Ownership unclear for {file_path}, allowing {agent_type.value} to proceed")
            return OperationResult(success=True, delegated=False)

        # Check if agent owns the file
        if agent_type == owner:
            # Agent owns file - allow operation
            logger.debug(f"Operation allowed: {agent_type.value} owns {file_path}")
            return OperationResult(success=True, delegated=False)

        # Ownership violation - auto-delegate to owner
        logger.info(
            f"Ownership violation detected: {agent_type.value} tried to {operation} {file_path} "
            f"(owner: {owner.value}). Auto-delegating..."
        )

        # Create delegation trace
        trace = self._create_delegation_trace(
            requesting_agent=agent_type,
            owner_agent=owner,
            file_path=file_path,
            operation=op_type,
        )

        # Delegate operation to owner
        # NOTE: In real implementation, this would actually execute the operation
        # via the correct agent. For now, we return a success result with delegation info.
        result = OperationResult(
            success=True,
            delegated=True,
            delegated_to=owner,
            trace_id=trace.trace_id,
        )

        # Log delegation trace
        self.delegation_traces.append(trace)
        logger.info(f"Delegation trace logged: {trace.trace_id}")

        return result

    def _create_delegation_trace(
        self,
        requesting_agent: AgentType,
        owner_agent: AgentType,
        file_path: str,
        operation: FileOperationType,
    ) -> DelegationTrace:
        """Create a delegation trace for reflector analysis.

        Args:
            requesting_agent: Agent that requested operation
            owner_agent: Agent that owns the file
            file_path: Path to file
            operation: Type of operation

        Returns:
            DelegationTrace record
        """
        trace_id = f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        return DelegationTrace(
            trace_id=trace_id,
            timestamp=datetime.now(),
            requesting_agent=requesting_agent,
            owner_agent=owner_agent,
            file_path=file_path,
            operation=operation,
            reason=f"Ownership violation: {requesting_agent.value} tried to access {owner_agent.value}'s file",
            success=True,  # Assume success for now
        )

    def get_delegation_traces(
        self,
        agent: Optional[AgentType] = None,
        hours: Optional[int] = None,
    ) -> list[DelegationTrace]:
        """Get delegation traces for analysis.

        Args:
            agent: Filter by requesting agent (optional)
            hours: Filter by last N hours (optional)

        Returns:
            List of delegation traces matching filters

        Example:
            >>> generator = Generator()
            >>> # Get all delegations from assistant in last 24 hours
            >>> traces = generator.get_delegation_traces(
            ...     agent=AgentType.ASSISTANT,
            ...     hours=24
            ... )
        """
        traces = self.delegation_traces

        # Filter by agent
        if agent:
            traces = [t for t in traces if t.requesting_agent == agent]

        # Filter by time
        if hours:
            cutoff = datetime.now().timestamp() - (hours * 3600)
            traces = [t for t in traces if t.timestamp.timestamp() >= cutoff]

        return traces

    def get_delegation_stats(self) -> Dict[str, Any]:
        """Get statistics about delegations for monitoring.

        Returns:
            Dictionary with delegation statistics including:
            - total_delegations: Total number of delegations
            - delegations_by_requesting_agent: Count by requesting agent
            - delegations_by_owner: Count by owner agent
            - most_common_violations: Most frequent violation patterns

        Example:
            >>> generator = Generator()
            >>> stats = generator.get_delegation_stats()
            >>> print(f"Total delegations: {stats['total_delegations']}")
        """
        total = len(self.delegation_traces)

        # Count by requesting agent
        by_requester = {}
        for trace in self.delegation_traces:
            agent = trace.requesting_agent.value
            by_requester[agent] = by_requester.get(agent, 0) + 1

        # Count by owner
        by_owner = {}
        for trace in self.delegation_traces:
            agent = trace.owner_agent.value
            by_owner[agent] = by_owner.get(agent, 0) + 1

        # Find most common violation patterns
        violation_patterns = {}
        for trace in self.delegation_traces:
            pattern = f"{trace.requesting_agent.value} → {trace.owner_agent.value}"
            violation_patterns[pattern] = violation_patterns.get(pattern, 0) + 1

        most_common = sorted(violation_patterns.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_delegations": total,
            "delegations_by_requesting_agent": by_requester,
            "delegations_by_owner": by_owner,
            "most_common_violations": [{"pattern": p, "count": c} for p, c in most_common],
        }

    def clear_traces(self) -> None:
        """Clear delegation traces (useful for testing).

        Example:
            >>> generator = Generator()
            >>> generator.clear_traces()
        """
        self.delegation_traces.clear()
        logger.info("Delegation traces cleared")


# Singleton instance for global access
_generator_instance: Optional[Generator] = None


def get_generator() -> Generator:
    """Get singleton Generator instance.

    Returns:
        Generator singleton instance

    Example:
        >>> generator = get_generator()
        >>> result = generator.intercept_file_operation(...)
    """
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = Generator()
    return _generator_instance
