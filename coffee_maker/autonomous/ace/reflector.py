"""ACE Reflector - Insight extraction from execution traces.

This module implements the Reflector component of the ACE framework,
which analyzes execution traces and extracts actionable insights.

Reference: https://www.arxiv.org/abs/2510.04618
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.ace.models import DeltaItem, Evidence, ExecutionTrace
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.utils.file_io import atomic_write_json

logger = logging.getLogger(__name__)


class ACEReflector:
    """Analyzes execution traces and extracts actionable insights.

    The Reflector performs cross-trace analysis to identify patterns,
    success strategies, failure modes, and missing knowledge. It generates
    structured delta items for the Curator to integrate into playbooks.

    Example:
        reflector = ACEReflector(agent_name="code_developer")
        deltas = reflector.analyze_traces(trace_ids=["trace_123", "trace_456"])
        reflector.save_deltas(deltas)
    """

    def __init__(
        self,
        agent_name: str,
        traces_base_dir: Optional[Path] = None,
        deltas_base_dir: Optional[Path] = None,
    ):
        """Initialize ACE Reflector.

        Args:
            agent_name: Name of agent being analyzed
            traces_base_dir: Base directory for traces (default: docs/generator/traces)
            deltas_base_dir: Base directory for deltas (default: docs/reflector/deltas)
        """
        self.agent_name = agent_name
        self.traces_base_dir = traces_base_dir or Path("docs/generator/traces")
        self.deltas_base_dir = deltas_base_dir or Path("docs/reflector/deltas")

        # Initialize trace manager
        self.trace_manager = TraceManager(base_dir=self.traces_base_dir)

        # Initialize Claude CLI interface
        self.claude_cli = ClaudeCLIInterface()

        # Ensure deltas directory exists
        self.deltas_base_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ACEReflector initialized for agent: {agent_name}")

    def analyze_traces(
        self,
        trace_ids: Optional[List[str]] = None,
        hours: Optional[int] = None,
        n_latest: Optional[int] = None,
    ) -> List[DeltaItem]:
        """Analyze traces and extract insights.

        Args:
            trace_ids: Specific trace IDs to analyze (mutually exclusive with other args)
            hours: Analyze traces from last N hours (mutually exclusive)
            n_latest: Analyze N most recent traces (mutually exclusive)

        Returns:
            List of DeltaItem insights extracted

        Raises:
            ValueError: If multiple mutually exclusive args provided or no traces found

        Example:
            # Analyze specific traces
            deltas = reflector.analyze_traces(trace_ids=["trace_123", "trace_456"])

            # Analyze last 24 hours
            deltas = reflector.analyze_traces(hours=24)

            # Analyze 10 most recent
            deltas = reflector.analyze_traces(n_latest=10)
        """
        # Validate arguments
        args_provided = sum([trace_ids is not None, hours is not None, n_latest is not None])
        if args_provided == 0:
            raise ValueError("Must provide one of: trace_ids, hours, or n_latest")
        if args_provided > 1:
            raise ValueError("Only one of trace_ids, hours, or n_latest can be provided")

        # Load traces
        traces = self._load_traces(trace_ids=trace_ids, hours=hours, n_latest=n_latest)

        if not traces:
            logger.warning("No traces found to analyze")
            return []

        logger.info(f"Analyzing {len(traces)} traces...")

        # Extract insights
        deltas = self._extract_insights(traces)

        # Extract satisfaction signals
        satisfaction_deltas = self._extract_satisfaction_signals(traces)
        deltas.extend(satisfaction_deltas)

        logger.info(
            f"Extracted {len(deltas)} insights from {len(traces)} traces "
            f"({len(satisfaction_deltas)} from satisfaction signals)"
        )

        return deltas

    def _load_traces(
        self,
        trace_ids: Optional[List[str]] = None,
        hours: Optional[int] = None,
        n_latest: Optional[int] = None,
    ) -> List[ExecutionTrace]:
        """Load traces based on specified criteria.

        Args:
            trace_ids: Specific trace IDs to load
            hours: Load traces from last N hours
            n_latest: Load N most recent traces

        Returns:
            List of ExecutionTrace instances

        Example:
            traces = self._load_traces(trace_ids=["trace_123"])
        """
        traces = []

        if trace_ids:
            # Load specific traces
            for trace_id in trace_ids:
                try:
                    trace = self.trace_manager.read_trace(trace_id)
                    # Filter by agent
                    if trace.agent_identity.get("target_agent") == self.agent_name:
                        traces.append(trace)
                    else:
                        logger.warning(f"Trace {trace_id} is for different agent, skipping")
                except FileNotFoundError:
                    logger.warning(f"Trace not found: {trace_id}")
                    continue

        elif hours:
            # Load traces from last N hours
            traces = self.trace_manager.get_traces_since(hours=hours, agent=self.agent_name)

        elif n_latest:
            # Load N most recent traces
            traces = self.trace_manager.get_latest_traces(n=n_latest, agent=self.agent_name)

        logger.info(f"Loaded {len(traces)} traces for agent: {self.agent_name}")
        return traces

    def _extract_insights(self, traces: List[ExecutionTrace]) -> List[DeltaItem]:
        """Extract insights from traces using Claude CLI.

        Args:
            traces: List of execution traces to analyze

        Returns:
            List of DeltaItem insights

        Example:
            deltas = self._extract_insights(traces)
        """
        # Convert traces to JSON format for prompt
        traces_json = [trace.to_dict() for trace in traces]

        # Load current playbook if available (optional)
        current_playbook = self._load_current_playbook()

        # Load prompt template
        prompt = load_prompt(
            PromptNames.ACE_REFLECTOR_EXTRACT,
            {
                "TRACES": json.dumps(traces_json, indent=2),
                "NUM_TRACES": str(len(traces)),
                "AGENT_NAME": self.agent_name,
                "CURRENT_PLAYBOOK": current_playbook or "No existing playbook",
            },
        )

        logger.info(f"Sending {len(traces)} traces to Claude for analysis...")

        # Use Claude CLI to analyze traces
        try:
            result = self.claude_cli.execute_prompt(prompt)
            if not result.success:
                raise RuntimeError(f"Claude CLI execution failed: {result.error}")
            response = result.content
            logger.info("Received analysis from Claude")
        except Exception as e:
            logger.error(f"Failed to get analysis from Claude: {e}")
            raise

        # Parse response to extract delta items
        deltas = self._parse_deltas_from_response(response, traces)

        # Assign priority and confidence if not already set
        for delta in deltas:
            if delta.priority == 3:  # Default priority
                delta.priority = self._assign_priority(delta)
            if delta.confidence == 0.5:  # Default confidence
                delta.confidence = self._assign_confidence(delta)

        return deltas

    def _parse_deltas_from_response(self, response: str, traces: List[ExecutionTrace]) -> List[DeltaItem]:
        """Parse delta items from Claude's response.

        Args:
            response: Claude's analysis response
            traces: Original traces (for trace IDs)

        Returns:
            List of DeltaItem instances

        Example:
            deltas = self._parse_deltas_from_response(response, traces)
        """
        deltas = []

        # Try to find JSON in response
        # Claude might return JSON in markdown code blocks or plain text
        try:
            # Try to extract JSON from markdown code block
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to parse entire response as JSON
                json_str = response.strip()

            # Parse JSON
            data = json.loads(json_str)

            # Extract deltas array
            if isinstance(data, dict) and "deltas" in data:
                deltas_data = data["deltas"]
            elif isinstance(data, list):
                deltas_data = data
            else:
                logger.error("Unexpected JSON structure in response")
                return []

            # Convert to DeltaItem instances
            for delta_dict in deltas_data:
                try:
                    delta = DeltaItem.from_dict(delta_dict)
                    deltas.append(delta)
                except Exception as e:
                    logger.warning(f"Failed to parse delta: {e}")
                    continue

            logger.info(f"Parsed {len(deltas)} deltas from response")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Response content: {response[:500]}...")

            # Fallback: Create a single delta with the raw response
            deltas.append(
                DeltaItem(
                    delta_id=f"delta_{int(datetime.now().timestamp())}",
                    insight_type="raw_analysis",
                    title="Raw Reflector Analysis",
                    description=f"Could not parse structured deltas. Raw analysis: {response[:200]}...",
                    recommendation="Review raw analysis manually",
                    evidence=[
                        Evidence(
                            trace_id=traces[0].trace_id if traces else "unknown",
                            execution_id=1,
                            example="See raw analysis",
                        )
                    ],
                    priority=3,
                    confidence=0.3,
                )
            )

        return deltas

    def _assign_priority(self, delta: DeltaItem) -> int:
        """Assign priority level (1-5) based on insight characteristics.

        Priority levels:
        - 5 (Critical): Prevents failures, fixes major issues
        - 4 (High): Significantly improves success rate
        - 3 (Medium): Useful optimization or best practice
        - 2 (Low): Minor improvement or edge case handling
        - 1 (Nice-to-have): Informational or optional enhancement

        Args:
            delta: DeltaItem to assign priority

        Returns:
            Priority level (1-5)

        Example:
            priority = self._assign_priority(delta)
        """
        # Critical failure modes get highest priority
        if delta.insight_type == "failure_mode":
            return 5

        # Success patterns that appear in multiple traces are high priority
        if delta.insight_type == "success_pattern" and len(delta.evidence) >= 2:
            return 4

        # Optimizations with high confidence are medium-high
        if delta.insight_type == "optimization" and delta.confidence >= 0.7:
            return 4

        # Best practices are medium priority
        if delta.insight_type == "best_practice":
            return 3

        # Tool usage guidance is medium priority
        if delta.insight_type == "tool_usage":
            return 3

        # Domain concepts are medium-low
        if delta.insight_type == "domain_concept":
            return 2

        # Default medium priority
        return 3

    def _assign_confidence(self, delta: DeltaItem) -> float:
        """Assign confidence level (0.0-1.0) based on evidence strength.

        Confidence levels:
        - 0.9-1.0 (High): Observed in multiple traces, clear causal link
        - 0.7-0.8 (Medium-High): Observed in multiple traces, plausible causal link
        - 0.5-0.6 (Medium): Observed in one trace, clear causal link
        - 0.3-0.4 (Low): Hypothesis based on limited evidence
        - 0.0-0.2 (Very Low): Speculation, needs more validation

        Args:
            delta: DeltaItem to assign confidence

        Returns:
            Confidence level (0.0-1.0)

        Example:
            confidence = self._assign_confidence(delta)
        """
        # Count evidence strength
        num_evidence = len(delta.evidence)

        if num_evidence >= 3:
            # Strong evidence from multiple traces
            return 0.9
        elif num_evidence == 2:
            # Medium evidence from two traces
            return 0.75
        elif num_evidence == 1:
            # Single trace evidence
            return 0.6
        else:
            # No direct evidence
            return 0.4

    def save_deltas(self, deltas: List[DeltaItem], custom_filename: Optional[str] = None) -> Path:
        """Save delta items to JSON file.

        Args:
            deltas: List of DeltaItem to save
            custom_filename: Optional custom filename (default: deltas_<timestamp>.json)

        Returns:
            Path to saved delta file

        Example:
            delta_path = reflector.save_deltas(deltas)
            print(f"Deltas saved to: {delta_path}")
        """
        # Create date-based subdirectory
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.deltas_base_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            timestamp = int(datetime.now().timestamp())
            filename = f"deltas_{timestamp}.json"

        delta_path = date_dir / filename

        # Prepare data structure
        data = {
            "metadata": {
                "agent_name": self.agent_name,
                "num_traces_analyzed": len(deltas),
                "analysis_timestamp": datetime.now().isoformat(),
                "reflector_version": "1.0",
            },
            "deltas": [delta.to_dict() for delta in deltas],
            "summary": self._compute_summary(deltas),
        }

        # Write to file
        atomic_write_json(delta_path, data)
        logger.info(f"Saved {len(deltas)} deltas to: {delta_path}")

        return delta_path

    def _compute_summary(self, deltas: List[DeltaItem]) -> dict:
        """Compute summary statistics for deltas.

        Args:
            deltas: List of DeltaItem instances

        Returns:
            Dictionary with summary statistics

        Example:
            summary = self._compute_summary(deltas)
        """
        if not deltas:
            return {
                "total_deltas": 0,
                "by_type": {},
                "by_priority": {},
                "avg_confidence": 0.0,
            }

        # Count by type
        by_type = {}
        for delta in deltas:
            by_type[delta.insight_type] = by_type.get(delta.insight_type, 0) + 1

        # Count by priority
        by_priority = {}
        for delta in deltas:
            by_priority[str(delta.priority)] = by_priority.get(str(delta.priority), 0) + 1

        # Average confidence
        avg_confidence = sum(delta.confidence for delta in deltas) / len(deltas)

        return {
            "total_deltas": len(deltas),
            "by_type": by_type,
            "by_priority": by_priority,
            "avg_confidence": round(avg_confidence, 2),
        }

    def _load_current_playbook(self) -> Optional[str]:
        """Load current playbook for agent (if exists).

        Returns:
            Playbook content as string, or None if not found

        Example:
            playbook = self._load_current_playbook()
        """
        playbook_path = Path(f"docs/curator/playbooks/{self.agent_name}_playbook.json")

        if not playbook_path.exists():
            logger.debug(f"No existing playbook found at: {playbook_path}")
            return None

        try:
            with open(playbook_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert to readable format
            playbook_str = json.dumps(data, indent=2)
            logger.info(f"Loaded playbook from: {playbook_path}")
            return playbook_str

        except Exception as e:
            logger.warning(f"Failed to load playbook: {e}")
            return None

    def _extract_satisfaction_signals(self, traces: List[ExecutionTrace]) -> List[DeltaItem]:
        """Extract insights based on user satisfaction signals.

        Handles both explicit and implicit satisfaction:
        - Explicit: High satisfaction (4-5) → success patterns, Low (1-2) → failure modes
        - Implicit: Sentiment analysis (frustration, satisfaction, confusion, etc.)

        Args:
            traces: List of execution traces to analyze

        Returns:
            List of DeltaItem insights weighted by satisfaction

        Example:
            >>> deltas = reflector._extract_satisfaction_signals(traces)
            >>> high_sat_deltas = [d for d in deltas if d.confidence >= 0.8]
        """
        satisfaction_deltas = []

        for trace in traces:
            if not trace.user_satisfaction:
                continue

            # Handle explicit satisfaction score (1-5)
            score = trace.user_satisfaction.get("score", 0)
            if score != 0:
                satisfaction_deltas.extend(self._extract_explicit_satisfaction(trace, score))

            # Handle implicit sentiment signals
            implicit_sentiment = trace.user_satisfaction.get("implicit_sentiment", [])
            if implicit_sentiment:
                satisfaction_deltas.extend(self._extract_implicit_sentiment(trace, implicit_sentiment))

        return satisfaction_deltas

    def _extract_explicit_satisfaction(self, trace: ExecutionTrace, score: int) -> List[DeltaItem]:
        """Extract deltas from explicit satisfaction score (1-5).

        Args:
            trace: Execution trace with satisfaction score
            score: Satisfaction score (1-5)

        Returns:
            List of DeltaItem insights
        """
        deltas = []

        if score == 0:
            return deltas

        # Extract actions taken (from external observation)
        if not trace.executions:
            return deltas

        execution = trace.executions[0]  # Use first execution
        actions = []

        # Collect actions from external observation
        if execution.external_observation.files_created:
            actions.append(f"Created files: {', '.join(execution.external_observation.files_created[:3])}")
        if execution.external_observation.files_modified:
            actions.append(f"Modified files: {', '.join(execution.external_observation.files_modified[:3])}")
        if execution.external_observation.commands_executed:
            actions.append(f"Executed commands: {', '.join(execution.external_observation.commands_executed[:3])}")

        # Collect reasoning from internal observation
        reasoning = (
            execution.internal_observation.reasoning_steps[:2] if execution.internal_observation.reasoning_steps else []
        )

        # Determine insight type and priority based on satisfaction score
        if score >= 4:
            # High satisfaction → Success pattern
            insight_type = "success_pattern"
            priority = 4
            confidence = 0.8 + (score - 4) * 0.1  # 0.8 for score=4, 0.9 for score=5
            title = f"High satisfaction pattern: {trace.user_query[:50]}"
            recommendation = f"Continue using this approach for similar tasks. User rated {score}/5."

        elif score <= 2:
            # Low satisfaction → Failure mode
            insight_type = "failure_mode"
            priority = 5  # High priority to avoid failures
            confidence = 0.7 + (2 - score) * 0.1  # 0.8 for score=1, 0.7 for score=2
            title = f"Low satisfaction failure: {trace.user_query[:50]}"
            recommendation = f"Avoid this approach. User rated {score}/5. Needs improvement."

        else:
            # Neutral satisfaction (score=3) → Skip
            return deltas

        # Build description
        description_parts = []
        if trace.user_satisfaction.get("positive_feedback"):
            description_parts.append(f"Positive: {trace.user_satisfaction['positive_feedback']}")
        if trace.user_satisfaction.get("improvement_areas"):
            description_parts.append(f"Improvement: {trace.user_satisfaction['improvement_areas']}")
        if actions:
            description_parts.append(f"Actions: {'; '.join(actions)}")
        if reasoning:
            description_parts.append(f"Reasoning: {'; '.join(reasoning)}")

        description = " | ".join(description_parts) if description_parts else "See trace for details"

        # Create delta item
        delta = DeltaItem(
            delta_id=f"satisfaction_{trace.trace_id}_{int(datetime.now().timestamp())}",
            insight_type=insight_type,
            title=title,
            description=description,
            recommendation=recommendation,
            evidence=[
                Evidence(
                    trace_id=trace.trace_id,
                    execution_id=1,
                    example=f"User satisfaction: {score}/5",
                )
            ],
            applicability=f"Similar to: {trace.user_query[:100]}",
            priority=priority,
            confidence=confidence,
            action="add_new",
            related_bullets=[],
        )

        deltas.append(delta)
        logger.info(
            f"Extracted explicit satisfaction signal: {insight_type} "
            f"(score={score}, confidence={confidence:.2f}, priority={priority})"
        )

        return deltas

    def _extract_implicit_sentiment(
        self, trace: ExecutionTrace, sentiment_signals: List[Dict[str, Any]]
    ) -> List[DeltaItem]:
        """Extract deltas from implicit sentiment signals.

        Processes sentiment analysis results (frustration, satisfaction, confusion, etc.)
        and creates appropriate delta items.

        Args:
            trace: Execution trace
            sentiment_signals: List of sentiment signal dicts from SentimentAnalyzer

        Returns:
            List of DeltaItem insights

        Example:
            >>> signals = [{"sentiment": "frustration", "confidence": 0.8, ...}]
            >>> deltas = reflector._extract_implicit_sentiment(trace, signals)
        """
        deltas = []

        for sentiment_data in sentiment_signals:
            sentiment_type = sentiment_data.get("sentiment")
            confidence = sentiment_data.get("confidence", 0.5)
            severity = sentiment_data.get("severity", 3)
            indicators = sentiment_data.get("indicators", [])

            # Determine insight type and priority based on sentiment
            if sentiment_type in ["frustration", "annoyance_repetition"]:
                # Negative sentiment → failure mode
                insight_type = "failure_mode"
                priority = min(5, severity)  # Map severity (1-5) to priority
                title = f"User {sentiment_type} detected: {trace.user_query[:50]}"
                recommendation = (
                    f"Avoid patterns that lead to {sentiment_type}. "
                    f"Review execution for root cause and improve approach."
                )
                action = "mark_harmful"

            elif sentiment_type == "impatience":
                # Impatience → optimization opportunity
                insight_type = "optimization"
                priority = min(4, severity)
                title = f"User impatience detected: {trace.user_query[:50]}"
                recommendation = (
                    f"Improve response time or provide progress updates. "
                    f"User expects faster results for this type of request."
                )
                action = "add_new"

            elif sentiment_type == "satisfaction":
                # Positive sentiment → success pattern
                insight_type = "success_pattern"
                priority = min(4, severity)
                title = f"User satisfaction expressed: {trace.user_query[:50]}"
                recommendation = (
                    f"Continue using this approach for similar tasks. "
                    f"User found this approach effective and satisfying."
                )
                action = "add_new"

            elif sentiment_type == "confusion":
                # Confusion → missing knowledge or unclear communication
                insight_type = "missing_knowledge"
                priority = min(3, severity)
                title = f"User confusion detected: {trace.user_query[:50]}"
                recommendation = (
                    f"Provide clearer explanations or better context. " f"User needed more information or guidance."
                )
                action = "add_new"

            else:
                # Unknown sentiment type - skip
                logger.warning(f"Unknown sentiment type: {sentiment_type}")
                continue

            # Extract actions from trace
            actions = []
            if trace.executions:
                execution = trace.executions[0]
                if execution.external_observation.files_created:
                    actions.append(f"Created: {', '.join(execution.external_observation.files_created[:3])}")
                if execution.external_observation.files_modified:
                    actions.append(f"Modified: {', '.join(execution.external_observation.files_modified[:3])}")
                if execution.external_observation.commands_executed:
                    actions.append(f"Commands: {', '.join(execution.external_observation.commands_executed[:3])}")

            # Build description
            indicators_str = ", ".join(str(i) for i in indicators[:3])
            description_parts = [
                f"Sentiment: {sentiment_type}",
                f"Indicators: {indicators_str}",
                f"Confidence: {confidence:.2f}",
                f"Severity: {severity}/5",
            ]
            if actions:
                description_parts.append(f"Actions: {'; '.join(actions)}")

            description = " | ".join(description_parts)

            # Create delta item
            delta = DeltaItem(
                delta_id=f"sentiment_{sentiment_type}_{trace.trace_id}_{int(datetime.now().timestamp())}",
                insight_type=insight_type,
                title=title,
                description=description,
                recommendation=recommendation,
                evidence=[
                    Evidence(
                        trace_id=trace.trace_id,
                        execution_id=1,
                        example=f"Sentiment: {sentiment_type} (confidence={confidence:.2f})",
                    )
                ],
                applicability=f"Similar to: {trace.user_query[:100]}",
                priority=priority,
                confidence=confidence,
                action=action,
                related_bullets=[],
            )

            deltas.append(delta)
            logger.info(
                f"Extracted implicit sentiment signal: {sentiment_type} "
                f"→ {insight_type} (confidence={confidence:.2f}, priority={priority})"
            )

        return deltas

    def analyze_recent_traces(self, hours: int = 24) -> List[DeltaItem]:
        """Convenience method to analyze traces from last N hours.

        Args:
            hours: Number of hours to look back (default: 24)

        Returns:
            List of DeltaItem insights

        Example:
            # Analyze last 24 hours
            deltas = reflector.analyze_recent_traces()

            # Analyze last week
            deltas = reflector.analyze_recent_traces(hours=168)
        """
        return self.analyze_traces(hours=hours)

    def get_stats(self) -> dict:
        """Get statistics about reflector activity.

        Returns:
            Dictionary with statistics

        Example:
            stats = reflector.get_stats()
            print(f"Total deltas: {stats['total_deltas']}")
        """
        total_deltas = 0
        dates = []

        for date_dir in self.deltas_base_dir.iterdir():
            if not date_dir.is_dir():
                continue

            dates.append(date_dir.name)
            for delta_path in date_dir.glob("deltas_*.json"):
                total_deltas += 1

        return {
            "total_deltas_files": total_deltas,
            "date_range": f"{min(dates)} to {max(dates)}" if dates else "No deltas",
            "dates_with_deltas": len(dates),
        }

    def propagate_satisfaction(self, trace_id: str) -> int:
        """Propagate satisfaction from parent trace to all child traces in delegation chain.

        When user provides satisfaction to user_listener, propagate it to
        all agents in the delegation chain (code_developer, etc.).

        This ensures that real work satisfaction signals reach the agents that
        performed the actual execution, enabling proper learning from user feedback.

        Args:
            trace_id: Trace ID that received satisfaction (parent)

        Returns:
            Number of child traces that received propagated satisfaction

        Example:
            >>> reflector = ACEReflector(agent_name="user_listener")
            >>> # User provides satisfaction to user_listener trace
            >>> num_propagated = reflector.propagate_satisfaction("trace_123")
            >>> print(f"Propagated to {num_propagated} child traces")
        """
        try:
            # Load parent trace
            parent_trace = self.trace_manager.read_trace(trace_id)
        except FileNotFoundError:
            logger.error(f"Parent trace not found: {trace_id}")
            return 0

        if not parent_trace.user_satisfaction:
            logger.warning(f"No satisfaction data to propagate from trace: {trace_id}")
            return 0

        satisfaction = parent_trace.user_satisfaction
        logger.info(f"Propagating satisfaction (score={satisfaction.get('score')}) " f"from trace {trace_id}")

        # Find all child traces in delegation chain
        # Search for traces with parent_trace_id == trace_id
        all_traces = self._load_all_traces()

        propagated_count = 0

        for trace in all_traces:
            if trace.parent_trace_id == trace_id:
                # This is a child trace - propagate satisfaction
                child_agent = trace.agent_identity.get("target_agent", "unknown")
                logger.info(f"Propagating satisfaction to child trace: {trace.trace_id} " f"(agent: {child_agent})")

                # Attach satisfaction with note that it's propagated
                propagated_satisfaction = satisfaction.copy()
                propagated_satisfaction["propagated_from"] = trace_id
                propagated_satisfaction["propagated_from_agent"] = parent_trace.agent_identity.get(
                    "target_agent", "unknown"
                )
                propagated_satisfaction["note"] = (
                    f"Satisfaction propagated from parent agent " f"({parent_trace.agent_identity.get('target_agent')})"
                )

                trace.user_satisfaction = propagated_satisfaction
                self.trace_manager.write_trace(trace)
                propagated_count += 1

                # Recursively propagate to grandchildren
                grandchildren_count = self.propagate_satisfaction(trace.trace_id)
                propagated_count += grandchildren_count

        if propagated_count > 0:
            logger.info(
                f"Successfully propagated satisfaction to {propagated_count} " f"child trace(s) from {trace_id}"
            )
        else:
            logger.info(f"No child traces found for {trace_id}")

        return propagated_count

    def _load_all_traces(self) -> List[ExecutionTrace]:
        """Load all traces from trace directory.

        Returns:
            List of all ExecutionTrace instances

        Example:
            traces = self._load_all_traces()
        """
        # Use TraceManager's list_traces method which handles this correctly
        all_traces = self.trace_manager.list_traces()
        logger.debug(f"Loaded {len(all_traces)} traces from {self.traces_base_dir}")
        return all_traces
