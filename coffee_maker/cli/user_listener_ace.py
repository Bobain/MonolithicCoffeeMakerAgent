"""ACE integration for user_listener agent.

This module provides ACE (Agentic Context Engineering) integration for the
user_listener agent.

IMPORTANT: user_listener does NOT generate traces - that's generator's job!

user_listener only:
1. Prepares observation data
2. Loads playbook context
3. Collects satisfaction feedback

The generator wraps user_interpret (not user_listener) to create traces.

Example:
    >>> ace = UserListenerACE()
    >>> playbook_context = ace.get_playbook_context()
    >>> # Use playbook_context to inform delegation decisions
    >>> observation_data = ace.prepare_observation_data(
    ...     user_query="Fix the bug in roadmap_cli.py",
    ...     delegated_to="code_developer",
    ...     success=True,
    ...     duration_seconds=8.5
    ... )
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

from coffee_maker.autonomous.ace.config import get_default_config
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class UserListenerACE:
    """ACE wrapper for user_listener agent.

    IMPORTANT: Does NOT generate traces - that's generator's job!

    user_listener just prepares observation data for generator to use.
    The generator wraps user_interpret to create traces.

    Attributes:
        enabled: Whether ACE is enabled for user_listener
        config: ACE configuration
        playbook_loader: Loader for user_listener playbook
        sentiment_analyzer: Sentiment analyzer for implicit feedback

    Example:
        >>> ace = UserListenerACE(enabled=True)
        >>> if ace.enabled:
        ...     playbook = ace.get_playbook_context()
        ...     # Use playbook to inform delegation
    """

    def __init__(self, enabled: bool = None):
        """Initialize ACE for user_listener.

        Args:
            enabled: Enable ACE (defaults to ACE_ENABLED_USER_LISTENER env var)
                    If not specified, reads from environment variable.
        """
        if enabled is None:
            enabled = os.getenv("ACE_ENABLED_USER_LISTENER", "false").lower() == "true"

        self.enabled = enabled

        if not self.enabled:
            logger.info("ACE disabled for user_listener")
            return

        # Initialize ACE components
        config = get_default_config()
        config.ensure_directories()

        # Note: user_listener doesn't generate traces
        # It only loads playbooks and collects satisfaction
        self.config = config
        self.playbook_loader = PlaybookLoader(agent_name="user_listener", config=config)
        self.claude_cli = ClaudeCLIInterface()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_history: List[str] = []  # Track recent messages

        logger.info("✅ ACE enabled for user_listener")
        logger.info(f"   Playbook: {self.playbook_loader.playbook_path}")
        logger.info(f"   Sentiment analysis: enabled")

    def get_playbook_context(self) -> str:
        """Get current playbook as context for delegation decisions.

        Returns:
            Playbook markdown or empty string if no playbook available

        Example:
            >>> ace = UserListenerACE()
            >>> context = ace.get_playbook_context()
            >>> if context:
            ...     print("Using playbook to inform delegation")
        """
        if not self.enabled:
            return ""

        try:
            playbook = self.playbook_loader.load()
            return self.playbook_loader.to_markdown(playbook)
        except FileNotFoundError:
            logger.debug("No playbook found yet")
            return ""
        except Exception as e:
            logger.warning(f"Failed to load playbook: {e}")
            return ""

    def prepare_observation_data(
        self,
        user_query: str,
        delegated_to: str,
        success: bool,
        duration_seconds: float,
        user_feedback: Optional[str] = None,
        user_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Prepare observation data for generator to use.

        IMPORTANT: This does NOT create a trace - that's generator's job!

        This method only prepares the data that will be used by generator
        when wrapping user_interpret execution.

        Args:
            user_query: User's original query
            delegated_to: Agent delegated to
            success: Whether delegation solved the problem
            duration_seconds: Time taken to complete delegation
            user_feedback: Optional user feedback on quality of response
            user_message: Optional raw user message for sentiment analysis

        Returns:
            Observation data dict for generator to use

        Example:
            >>> data = ace.prepare_observation_data(
            ...     user_query="What's the status of PRIORITY-5?",
            ...     delegated_to="project_manager",
            ...     success=True,
            ...     duration_seconds=2.3
            ... )
        """
        if not self.enabled:
            return {}

        logger.info(
            f"Preparing observation data: '{user_query[:50]}...' "
            f"→ {delegated_to} "
            f"(success={success}, duration={duration_seconds:.1f}s)"
        )

        # Analyze sentiment from user message
        sentiment_signals = []
        message_for_analysis = user_message or user_query
        if message_for_analysis:
            self.conversation_history.append(message_for_analysis)
            self.conversation_history = self.conversation_history[-10:]

            sentiment_signals = self.sentiment_analyzer.analyze(
                message_for_analysis,
                self.conversation_history[:-1],
            )

            # Log sentiment signals
            if sentiment_signals:
                for sig in sentiment_signals:
                    logger.info(
                        f"  Sentiment detected: {sig.sentiment} "
                        f"(confidence={sig.confidence:.2f}, severity={sig.severity}/5)"
                    )

        # Prepare observation data
        observation_data = {
            "delegation_target": delegated_to,
            "success": success,
            "duration": duration_seconds,
            "query": user_query,
        }

        # Add sentiment if detected
        if sentiment_signals:
            observation_data["implicit_sentiment"] = [
                {
                    "sentiment": sig.sentiment,
                    "confidence": sig.confidence,
                    "indicators": sig.indicators,
                    "severity": sig.severity,
                }
                for sig in sentiment_signals
            ]

        # Add explicit feedback if provided
        if user_feedback:
            observation_data["feedback"] = user_feedback

        return observation_data

    def collect_satisfaction(self, trace_id: str, session_summary: str) -> Dict[str, Any]:
        """Collect user satisfaction feedback for completed session.

        Uses Claude CLI to prompt user for satisfaction rating and feedback,
        then returns structured data for attachment to execution trace.

        Args:
            trace_id: Execution trace ID to attach feedback to
            session_summary: Brief summary of work done in session

        Returns:
            Satisfaction data: {"score": int, "feedback": str, "timestamp": str}

        Example:
            >>> ace = UserListenerACE()
            >>> satisfaction = ace.collect_satisfaction(
            ...     trace_id="trace_123",
            ...     session_summary="Implemented authentication feature with tests"
            ... )
            >>> print(satisfaction["score"])  # 1-5
            4
        """
        if not self.enabled:
            logger.warning("ACE not enabled, skipping satisfaction collection")
            return {}

        logger.info(f"Collecting satisfaction feedback for trace: {trace_id}")

        # Load satisfaction prompt
        prompt = load_prompt(
            PromptNames.ACE_SATISFACTION_PROMPT,
            {"SESSION_SUMMARY": session_summary},
        )

        try:
            # Execute prompt via Claude CLI
            result = self.claude_cli.execute_prompt(prompt)

            if not result.success:
                logger.error(f"Failed to collect satisfaction: {result.error}")
                return {}

            # Parse response to extract satisfaction data
            satisfaction = self._parse_satisfaction_response(result.content)

            if satisfaction:
                logger.info(f"Collected satisfaction: {satisfaction['score']}/5")
                if satisfaction.get("positive_feedback"):
                    logger.info(f"  Positive: {satisfaction['positive_feedback'][:50]}...")
                if satisfaction.get("improvement_areas"):
                    logger.info(f"  Improvement: {satisfaction['improvement_areas'][:50]}...")

            return satisfaction

        except Exception as e:
            logger.error(f"Error collecting satisfaction: {e}")
            return {}

    def _parse_satisfaction_response(self, response: str) -> Dict[str, Any]:
        """Parse satisfaction feedback from Claude's response.

        Looks for JSON structure or extracts from natural language.

        Args:
            response: Claude's response text

        Returns:
            Satisfaction data dict or empty dict if parsing fails

        Example:
            >>> ace = UserListenerACE()
            >>> data = ace._parse_satisfaction_response('{"score": 4, ...}')
            >>> data["score"]
            4
        """
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON in code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON-like structure
                json_match = re.search(r"\{[^{}]*\"score\"[^{}]*\}", response)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # Fallback: try to parse entire response
                    json_str = response.strip()

            # Parse JSON
            data = json.loads(json_str)

            # Validate required fields
            if "score" not in data:
                logger.warning("Satisfaction response missing 'score' field")
                return {}

            # Ensure score is in valid range
            score = int(data["score"])
            if not (1 <= score <= 5):
                logger.warning(f"Invalid satisfaction score: {score} (must be 1-5)")
                return {}

            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

            return {
                "score": score,
                "positive_feedback": data.get("positive_feedback", ""),
                "improvement_areas": data.get("improvement_areas", ""),
                "timestamp": data.get("timestamp"),
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from satisfaction response: {e}")
            logger.debug(f"Response: {response[:200]}...")

            # Fallback: Try to extract score from natural language
            score_match = re.search(r"(?:score|rating)[:=\s]+([1-5])", response, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                logger.info(f"Extracted score from natural language: {score}")
                return {
                    "score": score,
                    "positive_feedback": "",
                    "improvement_areas": "",
                    "timestamp": datetime.now().isoformat(),
                }

            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing satisfaction: {e}")
            return {}
