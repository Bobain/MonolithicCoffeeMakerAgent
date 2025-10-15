"""Automatic ACE integration for all agents.

This module provides base classes and decorators to automatically wrap
ANY agent with ACE observation, ensuring consistent trace generation
across the entire system.

Philosophy:
- New agents automatically get ACE supervision
- No manual wrapper creation needed
- Consistent interface across all agents
- Environment variable controls ACE per agent
"""

import os
import logging
from datetime import datetime
from typing import Any, List
from abc import ABC, abstractmethod

from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.config import get_default_config

logger = logging.getLogger(__name__)


class ACEAgent(ABC):
    """Base class for all agents with automatic ACE integration.

    Any agent that inherits from this class will automatically:
    1. Use singleton pattern (only one instance per agent class)
    2. Check for ACE_ENABLED_{AGENT_NAME} environment variable
    3. Initialize ACEGenerator if enabled
    4. Route all executions through generator for trace creation
    5. Provide consistent send_message() interface

    Usage:
        class MyAgent(ACEAgent):
            @property
            def agent_name(self) -> str:
                return "my_agent"

            @property
            def agent_objective(self) -> str:
                return "Do something useful"

            @property
            def success_criteria(self) -> str:
                return "Task completed successfully"

            def execute_task(self, task: str, **kwargs) -> Dict[str, Any]:
                # Your agent logic here
                return {"result": "done"}

    That's it! ACE integration is automatic, and the agent is a singleton.
    """

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern for agents.

        Only one instance of each agent class will ever exist. Subsequent
        calls to instantiate the same agent class will return the existing instance.

        Returns:
            Singleton instance of the agent class
        """
        if not hasattr(cls, "_instance"):
            logger.debug(f"Creating new singleton instance for {cls.__name__}")
            cls._instance = super(ACEAgent, cls).__new__(cls)
            cls._instance._initialized = False  # Track initialization
        else:
            logger.debug(f"Returning existing singleton instance for {cls.__name__}")
        return cls._instance

    def __init__(self):
        """Initialize agent with automatic ACE integration.

        ACE is ENABLED BY DEFAULT for all agents.
        To disable ACE for a specific agent, set:
        ACE_ENABLED_{AGENT_NAME}="false"

        Examples:
        - ACE_ENABLED_USER_INTERPRET="false"  → Disables ACE for user_interpret
        - ACE_ENABLED_CODE_DEVELOPER="false"  → Disables ACE for code_developer
        - (no env var set)                    → ACE ENABLED (default)

        Note: Due to singleton pattern, __init__ may be called multiple times
        but initialization only happens once (tracked via _initialized flag).
        """
        # Skip initialization if already initialized (singleton pattern)
        if hasattr(self, "_initialized") and self._initialized:
            logger.debug(f"Agent {self.agent_name} already initialized (singleton)")
            return

        # Check if ACE disabled for this agent (default: ENABLED)
        env_var = f"ACE_ENABLED_{self.agent_name.upper()}"
        ace_disabled = os.getenv(env_var, "true").lower() == "false"

        if not ace_disabled:
            # ACE ENABLED (default)
            config = get_default_config()
            self.generator = ACEGenerator(
                agent_interface=self,
                config=config,
                agent_name=self.agent_name,
                agent_objective=self.agent_objective,
                success_criteria=self.success_criteria,
            )
            self.ace_enabled = True
            logger.info(f"✅ ACE enabled for {self.agent_name} (default, singleton)")
        else:
            # ACE DISABLED (user opted out)
            self.generator = None
            self.ace_enabled = False
            logger.info(f"❌ ACE disabled for {self.agent_name} (user opt-out, singleton)")

        # Mark as initialized
        self._initialized = True

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return agent name (used for env var and trace naming)."""

    @property
    @abstractmethod
    def agent_objective(self) -> str:
        """Return agent's primary objective for ACE context."""

    @property
    @abstractmethod
    def success_criteria(self) -> str:
        """Return success criteria for ACE evaluation."""

    @abstractmethod
    def _execute_implementation(self, *args, **kwargs) -> Any:
        """Implement your agent's core logic here.

        This is called by either:
        - send_message() (when ACE enabled, via generator)
        - execute_task() (when ACE disabled, direct call)

        Returns:
            Any: Your agent's result
        """

    def execute_task(self, *args, **kwargs) -> Any:
        """Execute agent task with automatic ACE observation.

        This is the PUBLIC interface for your agent.
        Users call this method, and ACE integration is automatic.

        Returns:
            Any: Agent result (from _execute_implementation)
        """
        if self.ace_enabled:
            # Execute through generator (creates trace)
            result = self.generator.execute_with_trace(
                prompt=self._format_prompt(*args, **kwargs),
                priority_context=kwargs.get("context", {}),
                **kwargs,
            )
            # Return actual agent result
            return result["agent_result"]
        else:
            # Direct execution (no trace)
            return self._execute_implementation(*args, **kwargs)

    def send_message(self, message: str, **kwargs) -> Any:
        """Interface method for ACEGenerator.

        Generator calls this during execute_with_trace().
        Routes to _execute_implementation().

        Args:
            message: Formatted prompt from _format_prompt()
            **kwargs: Additional context

        Returns:
            Any: Agent result
        """
        # Parse message back to args (or just pass through)
        return self._execute_implementation(message, **kwargs)

    def _format_prompt(self, *args, **kwargs) -> str:
        """Format args into prompt string for generator.

        Override this if your agent needs custom prompt formatting.

        Returns:
            str: Formatted prompt
        """
        # Default: stringify first arg
        if args:
            return str(args[0])
        return ""

    # Plan tracking interface methods (NEW)
    def _set_plan(self, plan: List[str]) -> None:
        """Set execution plan (generator will capture this).

        Agents should call this method at the start of execution to declare
        the steps they plan to take. This helps the reflector understand
        agent strategy and identify deviations from plan.

        Args:
            plan: List of steps the agent plans to execute

        Example:
            >>> self._set_plan([
            ...     "Analyze user sentiment",
            ...     "Interpret user intent",
            ...     "Choose appropriate agent",
            ...     "Generate response"
            ... ])
        """
        if not hasattr(self, "_current_plan"):
            self._current_plan = []
        self._current_plan = plan

    def _report_difficulty(self, difficulty: str, severity: str = "medium") -> None:
        """Report difficulty during execution.

        Agents should call this method whenever they encounter an issue,
        error, or unexpected condition. This helps the reflector identify
        problematic patterns and failure modes.

        Args:
            difficulty: Description of the difficulty encountered
            severity: Severity level ("low", "medium", "high")

        Example:
            >>> self._report_difficulty("Sentiment analysis failed: timeout", severity="high")
        """
        if not hasattr(self, "_current_difficulties"):
            self._current_difficulties = []
        self._current_difficulties.append(
            {"description": difficulty, "severity": severity, "timestamp": datetime.now().isoformat()}
        )

    def _report_concern(self, concern: str) -> None:
        """Report concern during execution.

        Agents should call this method to flag warnings, edge cases, or
        situations that worked but might be problematic. This helps the
        reflector identify areas for improvement.

        Args:
            concern: Description of the concern

        Example:
            >>> self._report_concern("Intent unclear, defaulting to general_question")
        """
        if not hasattr(self, "_current_concerns"):
            self._current_concerns = []
        self._current_concerns.append(concern)

    def _update_plan_progress(self, step: str, status: str) -> None:
        """Update progress through plan.

        Agents should call this method as they complete each step in their plan.
        This helps the reflector understand execution flow and identify bottlenecks.

        Args:
            step: Name of the step (should match entry in plan)
            status: Status of the step ("in_progress", "completed", "failed", "skipped")

        Example:
            >>> self._update_plan_progress("Analyze user sentiment", "in_progress")
            >>> # ... do work ...
            >>> self._update_plan_progress("Analyze user sentiment", "completed")
        """
        if not hasattr(self, "_plan_progress"):
            self._plan_progress = {}
        self._plan_progress[step] = {"status": status, "timestamp": datetime.now().isoformat()}


class ACEAgentWrapper:
    """Wrapper for agents not using ACEAgent base class.

    Use this to wrap existing agents without refactoring them.

    Usage:
        # Wrap existing agent
        my_agent = MyExistingAgent()
        wrapped_agent = ACEAgentWrapper(
            agent=my_agent,
            agent_name="my_agent",
            agent_objective="Do something",
            success_criteria="Success",
            execute_method="process",  # Which method to wrap
        )

        # Call wrapped method
        result = wrapped_agent.execute_task(input_data)
    """

    def __init__(
        self,
        agent: Any,
        agent_name: str,
        agent_objective: str,
        success_criteria: str,
        execute_method: str = "execute",
    ):
        """Initialize wrapper around existing agent.

        Args:
            agent: Existing agent instance
            agent_name: Agent name for ACE
            agent_objective: Agent objective for ACE
            success_criteria: Success criteria for ACE
            execute_method: Name of method to wrap (default: "execute")
        """
        self.agent = agent
        self.agent_name = agent_name
        self.agent_objective = agent_objective
        self.success_criteria = success_criteria
        self.execute_method = execute_method

        # Get the actual method from agent
        self._execute_impl = getattr(agent, execute_method)

        # Check if ACE enabled
        env_var = f"ACE_ENABLED_{agent_name.upper()}"
        ace_enabled = os.getenv(env_var, "false").lower() == "true"

        if ace_enabled:
            config = get_default_config()
            self.generator = ACEGenerator(
                agent_interface=self,
                config=config,
                agent_name=agent_name,
                agent_objective=agent_objective,
                success_criteria=success_criteria,
            )
            self.ace_enabled = True
            logger.info(f"ACE enabled for {agent_name} (wrapped)")
        else:
            self.generator = None
            self.ace_enabled = False
            logger.info(f"ACE disabled for {agent_name} (wrapped)")

    def execute_task(self, *args, **kwargs) -> Any:
        """Execute agent task with automatic ACE observation."""
        if self.ace_enabled:
            # Execute through generator
            prompt = str(args[0]) if args else ""
            result = self.generator.execute_with_trace(
                prompt=prompt,
                priority_context=kwargs.get("context", {}),
                args=args,
                kwargs=kwargs,
            )
            return result["agent_result"]
        else:
            # Direct execution
            return self._execute_impl(*args, **kwargs)

    def send_message(self, message: str, **kwargs) -> Any:
        """Interface for generator."""
        # Extract original args if stored
        args = kwargs.pop("args", ())
        kwargs_orig = kwargs.pop("kwargs", {})

        if args or kwargs_orig:
            # Use original args
            return self._execute_impl(*args, **kwargs_orig)
        else:
            # Use message
            return self._execute_impl(message, **kwargs)


def ace_integrated(
    agent_name: str,
    agent_objective: str,
    success_criteria: str,
    execute_method: str = "execute",
):
    """Decorator for automatic ACE integration.

    Usage:
        @ace_integrated(
            agent_name="my_agent",
            agent_objective="Process data",
            success_criteria="Data processed successfully"
        )
        class MyAgent:
            def execute(self, data):
                return {"processed": data}

        # ACE is now automatic!
        agent = MyAgent()
        result = agent.execute("test")  # Traced if ACE_ENABLED_MY_AGENT=true
    """

    def decorator(agent_class):
        """Wrap agent class with ACE integration."""

        class ACEIntegratedAgent(agent_class):
            """Agent with automatic ACE integration."""

            def __init__(self, *args, **kwargs):
                # Initialize original agent
                super().__init__(*args, **kwargs)

                # Add ACE integration
                self._ace_agent_name = agent_name
                self._ace_agent_objective = agent_objective
                self._ace_success_criteria = success_criteria
                self._ace_execute_method = execute_method

                # Store original execute method
                self._original_execute = getattr(self, execute_method)

                # Check if ACE enabled
                env_var = f"ACE_ENABLED_{agent_name.upper()}"
                ace_enabled = os.getenv(env_var, "false").lower() == "true"

                if ace_enabled:
                    config = get_default_config()
                    self._ace_generator = ACEGenerator(
                        agent_interface=self,
                        config=config,
                        agent_name=agent_name,
                        agent_objective=agent_objective,
                        success_criteria=success_criteria,
                    )
                    self._ace_enabled = True

                    # Replace execute method with wrapped version
                    setattr(self, execute_method, self._ace_execute)

                    logger.info(f"ACE enabled for {agent_name} (decorated)")
                else:
                    self._ace_generator = None
                    self._ace_enabled = False
                    logger.info(f"ACE disabled for {agent_name} (decorated)")

            def _ace_execute(self, *args, **kwargs):
                """Execute with ACE observation."""
                prompt = str(args[0]) if args else ""
                result = self._ace_generator.execute_with_trace(
                    prompt=prompt,
                    priority_context=kwargs.get("context", {}),
                    args=args,
                    kwargs=kwargs,
                )
                return result["agent_result"]

            def send_message(self, message: str, **kwargs):
                """Interface for generator."""
                args = kwargs.pop("args", ())
                kwargs_orig = kwargs.pop("kwargs", {})

                if args or kwargs_orig:
                    return self._original_execute(*args, **kwargs_orig)
                else:
                    return self._original_execute(message, **kwargs)

        return ACEIntegratedAgent

    return decorator


# Convenience function for quick wrapping
def wrap_agent_with_ace(
    agent: Any,
    agent_name: str,
    agent_objective: str,
    success_criteria: str,
    execute_method: str = "execute",
) -> ACEAgentWrapper:
    """Quick function to wrap any agent with ACE.

    Args:
        agent: Agent instance
        agent_name: Agent name for ACE
        agent_objective: Agent objective
        success_criteria: Success criteria
        execute_method: Method name to wrap

    Returns:
        ACEAgentWrapper: Wrapped agent with ACE integration

    Usage:
        my_agent = MyAgent()
        wrapped = wrap_agent_with_ace(
            agent=my_agent,
            agent_name="my_agent",
            agent_objective="Process data",
            success_criteria="Data processed"
        )
        result = wrapped.execute_task(data)
    """
    return ACEAgentWrapper(
        agent=agent,
        agent_name=agent_name,
        agent_objective=agent_objective,
        success_criteria=success_criteria,
        execute_method=execute_method,
    )
