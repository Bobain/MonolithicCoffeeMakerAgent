"""Data models for ACE framework.

This module defines all data structures used by the Generator, Reflector, and Curator
components of the ACE (Agentic Context Engineering) framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ExternalObservation:
    """External observation of agent execution (git, files, commands)."""

    git_changes: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "git_changes": self.git_changes,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "files_deleted": self.files_deleted,
            "commands_executed": self.commands_executed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExternalObservation":
        """Load from dictionary."""
        return cls(
            git_changes=data.get("git_changes", []),
            files_created=data.get("files_created", []),
            files_modified=data.get("files_modified", []),
            files_deleted=data.get("files_deleted", []),
            commands_executed=data.get("commands_executed", []),
        )


@dataclass
class InternalObservation:
    """Internal observation of agent execution (reasoning, tools, decisions)."""

    reasoning_steps: List[str] = field(default_factory=list)
    decisions_made: List[str] = field(default_factory=list)
    tools_called: List[Dict[str, Any]] = field(default_factory=list)
    context_used: List[str] = field(default_factory=list)  # bullet IDs
    context_ignored: List[str] = field(default_factory=list)  # bullet IDs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "reasoning_steps": self.reasoning_steps,
            "decisions_made": self.decisions_made,
            "tools_called": self.tools_called,
            "context_used": self.context_used,
            "context_ignored": self.context_ignored,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InternalObservation":
        """Load from dictionary."""
        return cls(
            reasoning_steps=data.get("reasoning_steps", []),
            decisions_made=data.get("decisions_made", []),
            tools_called=data.get("tools_called", []),
            context_used=data.get("context_used", []),
            context_ignored=data.get("context_ignored", []),
        )


@dataclass
class Execution:
    """Single execution run."""

    execution_id: int
    external_observation: ExternalObservation
    internal_observation: InternalObservation
    result_status: str  # "success" or "failure"
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    token_usage: int = 0
    agent_response: Optional[Any] = None  # Actual agent result (not serialized in trace)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "execution_id": self.execution_id,
            "external_observation": self.external_observation.to_dict(),
            "internal_observation": self.internal_observation.to_dict(),
            "result_status": self.result_status,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "token_usage": self.token_usage,
            # Don't serialize agent_response (too large, not needed in trace)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Execution":
        """Load from dictionary."""
        return cls(
            execution_id=data["execution_id"],
            external_observation=ExternalObservation.from_dict(data.get("external_observation", {})),
            internal_observation=InternalObservation.from_dict(data.get("internal_observation", {})),
            result_status=data.get("result_status", "unknown"),
            errors=data.get("errors", []),
            duration_seconds=data.get("duration_seconds", 0.0),
            token_usage=data.get("token_usage", 0),
        )


@dataclass
class ComparativeObservations:
    """Comparison between two executions."""

    consistency: str  # "same_outcome" or "different_outcomes"
    strategy_variance: str  # Description of differences
    effectiveness_comparison: str  # Which was better and why
    patterns_identified: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "consistency": self.consistency,
            "strategy_variance": self.strategy_variance,
            "effectiveness_comparison": self.effectiveness_comparison,
            "patterns_identified": self.patterns_identified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComparativeObservations":
        """Load from dictionary."""
        return cls(
            consistency=data.get("consistency", "unknown"),
            strategy_variance=data.get("strategy_variance", ""),
            effectiveness_comparison=data.get("effectiveness_comparison", ""),
            patterns_identified=data.get("patterns_identified", []),
        )


@dataclass
class ExecutionTrace:
    """Complete execution trace for ACE framework."""

    trace_id: str
    timestamp: datetime
    agent_identity: Dict[str, str]  # target_agent, agent_objective, success_criteria
    user_query: str
    current_context: str  # Playbook snapshot
    executions: List[Execution] = field(default_factory=list)
    comparative_observations: Optional[ComparativeObservations] = None
    helpful_context_elements: List[str] = field(default_factory=list)
    problematic_context_elements: List[str] = field(default_factory=list)
    new_insights_surfaced: List[str] = field(default_factory=list)
    skip_reason: Optional[str] = None  # Why second execution was skipped
    user_satisfaction: Optional[Dict[str, Any]] = None  # {"score": 1-5, "feedback": str, "timestamp": str}
    parent_trace_id: Optional[str] = None  # If this execution was delegated from another agent
    delegation_chain: List[Dict[str, str]] = field(default_factory=list)  # Chain of delegation
    # delegation_chain format: [{"agent": "user_listener", "trace_id": "trace_123", "timestamp": "2025-10-15T..."}, ...]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_identity": self.agent_identity,
            "user_query": self.user_query,
            "current_context": self.current_context,
            "executions": [e.to_dict() for e in self.executions],
            "comparative_observations": (
                self.comparative_observations.to_dict() if self.comparative_observations else None
            ),
            "helpful_context_elements": self.helpful_context_elements,
            "problematic_context_elements": self.problematic_context_elements,
            "new_insights_surfaced": self.new_insights_surfaced,
            "skip_reason": self.skip_reason,
            "user_satisfaction": self.user_satisfaction,
            "parent_trace_id": self.parent_trace_id,
            "delegation_chain": self.delegation_chain,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionTrace":
        """Load from dictionary."""
        return cls(
            trace_id=data["trace_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_identity=data.get("agent_identity", {}),
            user_query=data.get("user_query", ""),
            current_context=data.get("current_context", ""),
            executions=[Execution.from_dict(e) for e in data.get("executions", [])],
            comparative_observations=(
                ComparativeObservations.from_dict(data["comparative_observations"])
                if data.get("comparative_observations")
                else None
            ),
            helpful_context_elements=data.get("helpful_context_elements", []),
            problematic_context_elements=data.get("problematic_context_elements", []),
            new_insights_surfaced=data.get("new_insights_surfaced", []),
            skip_reason=data.get("skip_reason"),
            user_satisfaction=data.get("user_satisfaction"),
            parent_trace_id=data.get("parent_trace_id"),
            delegation_chain=data.get("delegation_chain", []),
        )

    def to_markdown(self) -> str:
        """Generate human-readable markdown representation."""
        lines = [
            f"# Execution Trace: {self.trace_id}",
            "",
            f"**Timestamp**: {self.timestamp.isoformat()}",
            f"**Agent**: {self.agent_identity.get('target_agent', 'Unknown')}",
            f"**Query**: {self.user_query}",
            "",
        ]

        # Show delegation chain if present
        if self.delegation_chain:
            lines.extend(["## Delegation Chain", ""])
            for i, entry in enumerate(self.delegation_chain, 1):
                agent = entry.get("agent", "unknown")
                entry_trace_id = entry.get("trace_id", "N/A")
                timestamp = entry.get("timestamp", "N/A")
                lines.append(f"{i}. **{agent}** (trace: `{entry_trace_id}`, time: {timestamp})")
            lines.append("")

        if self.parent_trace_id:
            lines.extend([f"**Parent Trace**: {self.parent_trace_id}", ""])

        lines.extend(
            [
                "## Agent Identity",
                "",
                f"- **Objective**: {self.agent_identity.get('agent_objective', 'N/A')}",
                f"- **Success Criteria**: {self.agent_identity.get('success_criteria', 'N/A')}",
                "",
                "## Executions",
                "",
            ]
        )

        for execution in self.executions:
            lines.extend(
                [
                    f"### Execution {execution.execution_id}",
                    "",
                    f"**Status**: {execution.result_status}",
                    f"**Duration**: {execution.duration_seconds:.2f}s",
                    f"**Tokens**: {execution.token_usage}",
                    "",
                    "**External Observation**:",
                    f"- Files created: {len(execution.external_observation.files_created)}",
                    f"- Files modified: {len(execution.external_observation.files_modified)}",
                    f"- Commands: {len(execution.external_observation.commands_executed)}",
                    "",
                    "**Internal Observation**:",
                    f"- Reasoning steps: {len(execution.internal_observation.reasoning_steps)}",
                    f"- Decisions made: {len(execution.internal_observation.decisions_made)}",
                    f"- Tools called: {len(execution.internal_observation.tools_called)}",
                    "",
                ]
            )

            if execution.errors:
                lines.extend(["**Errors**:", ""])
                for error in execution.errors:
                    lines.append(f"- {error}")
                lines.append("")

        if self.comparative_observations:
            lines.extend(
                [
                    "## Comparative Analysis",
                    "",
                    f"**Consistency**: {self.comparative_observations.consistency}",
                    f"**Strategy Variance**: {self.comparative_observations.strategy_variance}",
                    f"**Effectiveness**: {self.comparative_observations.effectiveness_comparison}",
                    "",
                ]
            )

            if self.comparative_observations.patterns_identified:
                lines.extend(["**Patterns Identified**:", ""])
                for pattern in self.comparative_observations.patterns_identified:
                    lines.append(f"- {pattern}")
                lines.append("")

        if self.helpful_context_elements:
            lines.extend(["## Helpful Context Elements", ""])
            for element in self.helpful_context_elements:
                lines.append(f"- {element}")
            lines.append("")

        if self.problematic_context_elements:
            lines.extend(["## Problematic Context Elements", ""])
            for element in self.problematic_context_elements:
                lines.append(f"- {element}")
            lines.append("")

        if self.new_insights_surfaced:
            lines.extend(["## New Insights", ""])
            for insight in self.new_insights_surfaced:
                lines.append(f"- {insight}")
            lines.append("")

        if self.user_satisfaction:
            lines.extend(["## User Satisfaction", ""])
            score = self.user_satisfaction.get("score", "N/A")
            feedback = self.user_satisfaction.get("feedback", "")
            timestamp = self.user_satisfaction.get("timestamp", "N/A")

            lines.append(f"**Score**: {score}/5")
            lines.append(f"**Timestamp**: {timestamp}")
            if feedback:
                lines.append(f"**Feedback**: {feedback}")
            lines.append("")

        return "\n".join(lines)


@dataclass
class Evidence:
    """Evidence for a delta item."""

    trace_id: str
    execution_id: int
    example: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "execution_id": self.execution_id,
            "example": self.example,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        """Load from dictionary."""
        return cls(
            trace_id=data["trace_id"],
            execution_id=data["execution_id"],
            example=data.get("example", ""),
        )


@dataclass
class DeltaItem:
    """Actionable insight extracted from traces."""

    delta_id: str
    insight_type: str  # success_pattern, failure_mode, optimization, etc.
    title: str
    description: str
    recommendation: str
    evidence: List[Evidence] = field(default_factory=list)
    applicability: str = ""
    priority: int = 3  # 1-5
    confidence: float = 0.5  # 0.0-1.0
    action: str = "add_new"  # add_new, update_existing, mark_harmful
    related_bullets: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "delta_id": self.delta_id,
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "evidence": [e.to_dict() for e in self.evidence],
            "applicability": self.applicability,
            "priority": self.priority,
            "confidence": self.confidence,
            "action": self.action,
            "related_bullets": self.related_bullets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeltaItem":
        """Load from dictionary."""
        return cls(
            delta_id=data["delta_id"],
            insight_type=data.get("insight_type", "unknown"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            recommendation=data.get("recommendation", ""),
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
            applicability=data.get("applicability", ""),
            priority=data.get("priority", 3),
            confidence=data.get("confidence", 0.5),
            action=data.get("action", "add_new"),
            related_bullets=data.get("related_bullets", []),
        )


@dataclass
class PlaybookBullet:
    """Single bullet in agent playbook."""

    bullet_id: str
    type: str  # success_pattern, failure_mode, etc.
    content: str
    helpful_count: int = 0
    harmful_count: int = 0
    confidence: float = 0.5
    priority: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    evidence_sources: List[str] = field(default_factory=list)  # trace IDs
    applicability: str = ""
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    deprecated: bool = False
    deprecation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "bullet_id": self.bullet_id,
            "type": self.type,
            "content": self.content,
            "helpful_count": self.helpful_count,
            "harmful_count": self.harmful_count,
            "confidence": self.confidence,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "evidence_sources": self.evidence_sources,
            "applicability": self.applicability,
            "tags": self.tags,
            "embedding": self.embedding,
            "deprecated": self.deprecated,
            "deprecation_reason": self.deprecation_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaybookBullet":
        """Load from dictionary."""
        return cls(
            bullet_id=data["bullet_id"],
            type=data.get("type", "unknown"),
            content=data.get("content", ""),
            helpful_count=data.get("helpful_count", 0),
            harmful_count=data.get("harmful_count", 0),
            confidence=data.get("confidence", 0.5),
            priority=data.get("priority", 3),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            evidence_sources=data.get("evidence_sources", []),
            applicability=data.get("applicability", ""),
            tags=data.get("tags", []),
            embedding=data.get("embedding"),
            deprecated=data.get("deprecated", False),
            deprecation_reason=data.get("deprecation_reason"),
        )


@dataclass
class HealthMetrics:
    """Playbook health metrics."""

    total_bullets: int = 0
    avg_helpful_count: float = 0.0
    effectiveness_ratio: float = 0.0
    bullets_added_this_session: int = 0
    bullets_updated_this_session: int = 0
    bullets_pruned_this_session: int = 0
    coverage_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_bullets": self.total_bullets,
            "avg_helpful_count": self.avg_helpful_count,
            "effectiveness_ratio": self.effectiveness_ratio,
            "bullets_added_this_session": self.bullets_added_this_session,
            "bullets_updated_this_session": self.bullets_updated_this_session,
            "bullets_pruned_this_session": self.bullets_pruned_this_session,
            "coverage_score": self.coverage_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthMetrics":
        """Load from dictionary."""
        return cls(
            total_bullets=data.get("total_bullets", 0),
            avg_helpful_count=data.get("avg_helpful_count", 0.0),
            effectiveness_ratio=data.get("effectiveness_ratio", 0.0),
            bullets_added_this_session=data.get("bullets_added_this_session", 0),
            bullets_updated_this_session=data.get("bullets_updated_this_session", 0),
            bullets_pruned_this_session=data.get("bullets_pruned_this_session", 0),
            coverage_score=data.get("coverage_score", 0.0),
        )


@dataclass
class Playbook:
    """Agent playbook with categorized bullets."""

    playbook_version: str
    agent_name: str
    agent_objective: str
    success_criteria: str
    last_updated: datetime
    total_bullets: int
    effectiveness_score: float
    categories: Dict[str, List[PlaybookBullet]] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    health_metrics: Optional[HealthMetrics] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "playbook_version": self.playbook_version,
            "agent_name": self.agent_name,
            "agent_objective": self.agent_objective,
            "success_criteria": self.success_criteria,
            "last_updated": self.last_updated.isoformat(),
            "total_bullets": self.total_bullets,
            "effectiveness_score": self.effectiveness_score,
            "categories": {cat: [bullet.to_dict() for bullet in bullets] for cat, bullets in self.categories.items()},
            "statistics": self.statistics,
            "health_metrics": (self.health_metrics.to_dict() if self.health_metrics else None),
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Playbook":
        """Load from dictionary."""
        return cls(
            playbook_version=data.get("playbook_version", "1.0"),
            agent_name=data.get("agent_name", ""),
            agent_objective=data.get("agent_objective", ""),
            success_criteria=data.get("success_criteria", ""),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            total_bullets=data.get("total_bullets", 0),
            effectiveness_score=data.get("effectiveness_score", 0.0),
            categories={
                cat: [PlaybookBullet.from_dict(b) for b in bullets]
                for cat, bullets in data.get("categories", {}).items()
            },
            statistics=data.get("statistics", {}),
            health_metrics=(HealthMetrics.from_dict(data["health_metrics"]) if data.get("health_metrics") else None),
            history=data.get("history", []),
        )


@dataclass
class ConsolidatedInsight:
    """Consolidated insight from curator."""

    insight_id: str
    content: str
    confidence: float
    priority: int
    sources: List[str]  # trace IDs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "insight_id": self.insight_id,
            "content": self.content,
            "confidence": self.confidence,
            "priority": self.priority,
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsolidatedInsight":
        """Load from dictionary."""
        return cls(
            insight_id=data["insight_id"],
            content=data.get("content", ""),
            confidence=data.get("confidence", 0.5),
            priority=data.get("priority", 3),
            sources=data.get("sources", []),
        )
