"""Runtime token tracking decorator for command execution.

This module provides decorators and utilities for tracking actual token usage
during command execution, as required by CFR-018.

Usage:
    @track_tokens(agent_type="code_developer", command_name="implement")
    def implement_task(task_id: str) -> dict:
        # Token tracking happens automatically
        ...
"""

import logging
import sqlite3
import time
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from coffee_maker.utils.token_counter import validate_command_file

logger = logging.getLogger(__name__)

# Default database path (CFR-015: centralized in data/)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "development.db"


@dataclass
class TokenUsageResult:
    """Result of token usage tracking."""

    # Pre-execution
    estimated_input_tokens: int
    command_tokens: int
    readme_tokens: int
    skills_tokens: int

    # Post-execution
    actual_input_tokens: Optional[int]
    actual_output_tokens: Optional[int]
    total_tokens: Optional[int]
    duration_seconds: float

    # Accuracy
    estimate_accuracy_percent: Optional[float]
    within_budget: bool

    def __str__(self) -> str:
        if self.actual_input_tokens:
            status = "✅" if self.within_budget else "❌"
            return (
                f"{status} Estimated: {self.estimated_input_tokens:,} | "
                f"Actual: {self.actual_input_tokens:,} + {self.actual_output_tokens:,} "
                f"= {self.total_tokens:,} ({self.estimate_accuracy_percent:.1f}% accurate)"
            )
        else:
            return f"📊 Estimated: {self.estimated_input_tokens:,} tokens"


def store_token_usage(
    agent_type: str,
    command_name: str,
    result: TokenUsageResult,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    model: str = "claude-sonnet-4.5",
    success: bool = True,
    error_message: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Store token usage in database.

    Args:
        agent_type: Agent type (e.g., "code_developer")
        command_name: Command name (e.g., "implement")
        result: Token usage result
        task_id: Optional task ID
        session_id: Optional session ID
        model: AI model used
        success: Whether command succeeded
        error_message: Error message if failed
        db_path: Database file path

    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO command_token_usage (
                agent_type, command_name, duration_seconds,
                estimated_input_tokens, command_tokens, readme_tokens, skills_tokens,
                actual_input_tokens, actual_output_tokens,
                task_id, session_id, model, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_type,
                command_name,
                result.duration_seconds,
                result.estimated_input_tokens,
                result.command_tokens,
                result.readme_tokens,
                result.skills_tokens,
                result.actual_input_tokens,
                result.actual_output_tokens,
                task_id,
                session_id,
                model,
                success,
                error_message,
            ),
        )

        conn.commit()
        conn.close()

        logger.debug(f"Stored token usage for {agent_type}.{command_name}")

    except sqlite3.Error as e:
        logger.error(f"Failed to store token usage: {e}")
        # Don't raise - token tracking is observability, not critical path


def track_tokens(
    agent_type: str,
    command_name: str,
    task_id_param: Optional[str] = None,
    session_id_param: Optional[str] = None,
) -> Callable:
    """Decorator to track token usage for command execution.

    Reports token usage at start and end of execution, stores results in database.

    Args:
        agent_type: Agent type (e.g., "code_developer")
        command_name: Command name (e.g., "implement")
        task_id_param: Optional parameter name for task_id in wrapped function
        session_id_param: Optional parameter name for session_id

    Returns:
        Decorator function

    Example:
        @track_tokens(agent_type="code_developer", command_name="implement")
        def implement_task(task_id: str, **kwargs) -> dict:
            # Implementation
            return {"status": "success", "tokens_used": 4500}

        # Automatic output:
        # 🚀 code_developer.implement STARTING
        #    Estimated context: 4,601 tokens (7.7%)
        #    ...
        # ✅ code_developer.implement COMPLETED (23.4s)
        #    Actual tokens: 4,823 input + 2,156 output = 6,979 total
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 1. Pre-execution: Estimate tokens
            try:
                usage = validate_command_file(agent_type, command_name)
            except Exception as e:
                logger.warning(f"Could not validate token budget: {e}")
                # Continue execution even if validation fails
                usage = None

            # 2. Report estimated usage
            if usage:
                logger.info(
                    f"🚀 {agent_type}.{command_name} STARTING\n"
                    f"   Estimated context: {usage.total_tokens:,} tokens ({usage.usage_percent:.1f}%)\n"
                    f"   - Command: {usage.command_tokens:,}\n"
                    f"   - README: {usage.readme_tokens:,}\n"
                    f"   - Skills: {usage.skills_tokens:,}"
                )
            else:
                logger.info(f"🚀 {agent_type}.{command_name} STARTING")

            start_time = time.time()

            # 3. Execute command
            try:
                result = func(*args, **kwargs)
                error_message = None
            except Exception as e:
                error_message = str(e)
                duration = time.time() - start_time

                # Log failure
                logger.error(f"❌ {agent_type}.{command_name} FAILED ({duration:.1f}s)\n" f"   Error: {error_message}")

                # Store failure info
                if usage:
                    failure_result = TokenUsageResult(
                        estimated_input_tokens=usage.total_tokens,
                        command_tokens=usage.command_tokens,
                        readme_tokens=usage.readme_tokens,
                        skills_tokens=usage.skills_tokens,
                        actual_input_tokens=None,
                        actual_output_tokens=None,
                        total_tokens=None,
                        duration_seconds=duration,
                        estimate_accuracy_percent=None,
                        within_budget=usage.within_budget,
                    )

                    # Extract task_id/session_id from kwargs if specified
                    task_id = kwargs.get(task_id_param) if task_id_param else None
                    session_id = kwargs.get(session_id_param) if session_id_param else None

                    store_token_usage(
                        agent_type=agent_type,
                        command_name=command_name,
                        result=failure_result,
                        task_id=task_id,
                        session_id=session_id,
                        success=False,
                        error_message=error_message,
                    )

                raise  # Re-raise exception

            duration = time.time() - start_time

            # 4. Extract actual token usage from result (if available)
            actual_input = None
            actual_output = None

            if isinstance(result, dict):
                # Check if result contains token usage
                if "tokens" in result:
                    tokens = result["tokens"]
                    actual_input = tokens.get("input")
                    actual_output = tokens.get("output")

            # 5. Report actual usage
            if actual_input and actual_output:
                total = actual_input + actual_output
                accuracy = (usage.total_tokens / actual_input * 100) if usage and actual_input > 0 else None

                logger.info(
                    f"✅ {agent_type}.{command_name} COMPLETED ({duration:.1f}s)\n"
                    f"   Actual tokens:\n"
                    f"   - Input:  {actual_input:,} "
                    f"(estimate: {usage.total_tokens:,}, accuracy: {accuracy:.1f}%)\n"
                    f"   - Output: {actual_output:,}\n"
                    f"   - Total:  {total:,}\n"
                    f"   Context used: {(total)/200000*100:.1f}% of 200K"
                )
            else:
                logger.info(f"✅ {agent_type}.{command_name} COMPLETED ({duration:.1f}s)")

            # 6. Store in database
            if usage:
                tracking_result = TokenUsageResult(
                    estimated_input_tokens=usage.total_tokens,
                    command_tokens=usage.command_tokens,
                    readme_tokens=usage.readme_tokens,
                    skills_tokens=usage.skills_tokens,
                    actual_input_tokens=actual_input,
                    actual_output_tokens=actual_output,
                    total_tokens=actual_input + actual_output if actual_input and actual_output else None,
                    duration_seconds=duration,
                    estimate_accuracy_percent=(
                        (usage.total_tokens / actual_input * 100) if actual_input and actual_input > 0 else None
                    ),
                    within_budget=usage.within_budget,
                )

                # Extract task_id/session_id from kwargs if specified
                task_id = kwargs.get(task_id_param) if task_id_param else None
                session_id = kwargs.get(session_id_param) if session_id_param else None

                store_token_usage(
                    agent_type=agent_type,
                    command_name=command_name,
                    result=tracking_result,
                    task_id=task_id,
                    session_id=session_id,
                    success=True,
                )

            return result

        return wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    pass

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    @track_tokens(agent_type="code_developer", command_name="implement", task_id_param="task_id")
    def mock_implement(task_id: str) -> dict:
        """Mock implementation for testing."""
        import time

        time.sleep(1)  # Simulate work

        # Simulate API response with token usage
        return {
            "status": "success",
            "files_changed": 3,
            "tokens": {"input": 4823, "output": 2156},  # Simulated API response
        }

    # Test the decorator
    result = mock_implement(task_id="TASK-1-1")
    print(f"\nResult: {result}")
