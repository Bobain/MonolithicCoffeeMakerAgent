"""API layer for Streamlit app to interact with ACE framework.

This module provides a clean API interface for the Streamlit UI to interact
with the ACE framework components (Generator, Reflector, Curator).

Example:
    api = ACEApi()

    # Get traces
    traces = api.get_traces(agent="user_interpret", hours=24)

    # Get playbook
    playbook = api.get_playbook("user_interpret")

    # Get metrics
    metrics = api.get_metrics(days=7)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.ace.config import ACEConfig, get_default_config
from coffee_maker.autonomous.ace.models import ExecutionTrace
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.streamlit_app.utils.env_manager import EnvManager

logger = logging.getLogger(__name__)


class ACEApi:
    """API for Streamlit app to interact with ACE framework."""

    def __init__(self, config: Optional[ACEConfig] = None):
        """Initialize ACE API.

        Args:
            config: ACE configuration (optional, uses default if not provided)
        """
        self.config = config or get_default_config()
        self.trace_manager = TraceManager(self.config.trace_dir)
        self.env_manager = EnvManager()
        logger.info("ACEApi initialized")

    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get ACE status for all agents.

        Returns:
            Dictionary mapping agent names to status info

        Example:
            {
                "user_interpret": {
                    "ace_enabled": True,
                    "traces_today": 127,
                    "traces_total": 1453,
                    "playbook_size": 147
                },
                ...
            }
        """
        agent_statuses = {}

        # Known agents
        agents = [
            "user_interpret",
            "assistant",
            "code_searcher",
            "code_developer",
            "user_listener",
            "project_manager",
            "architect",
            "generator",
            "reflector",
            "curator",
        ]

        for agent_name in agents:
            try:
                # Check ACE status from .env
                ace_enabled = self.env_manager.get_agent_ace_status(agent_name)

                # Get trace counts
                today = datetime.now().strftime("%Y-%m-%d")
                traces_today = len(self.trace_manager.list_traces(date=today, agent=agent_name))
                traces_total = len(self.trace_manager.list_traces(agent=agent_name))

                # Get playbook size
                playbook_size = 0
                try:
                    loader = PlaybookLoader(agent_name, self.config)
                    playbook = loader.load()
                    playbook_size = playbook.total_bullets
                except Exception as e:
                    logger.debug(f"No playbook for {agent_name}: {e}")

                agent_statuses[agent_name] = {
                    "ace_enabled": ace_enabled,
                    "traces_today": traces_today,
                    "traces_total": traces_total,
                    "playbook_size": playbook_size,
                }
            except Exception as e:
                logger.warning(f"Failed to get status for {agent_name}: {e}")
                agent_statuses[agent_name] = {
                    "ace_enabled": False,
                    "traces_today": 0,
                    "traces_total": 0,
                    "playbook_size": 0,
                }

        return agent_statuses

    def enable_agent(self, agent_name: str) -> bool:
        """Enable ACE for specific agent.

        Args:
            agent_name: Agent to enable ACE for

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.env_manager.set_agent_ace_status(agent_name, True)
            if success:
                logger.info(f"Enabled ACE for {agent_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to enable ACE for {agent_name}: {e}")
            return False

    def disable_agent(self, agent_name: str) -> bool:
        """Disable ACE for specific agent.

        Args:
            agent_name: Agent to disable ACE for

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.env_manager.set_agent_ace_status(agent_name, False)
            if success:
                logger.info(f"Disabled ACE for {agent_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to disable ACE for {agent_name}: {e}")
            return False

    def get_traces(
        self,
        agent: Optional[str] = None,
        date: Optional[str] = None,
        hours: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get traces (optionally filtered).

        Args:
            agent: Filter by agent name
            date: Filter by date (YYYY-MM-DD)
            hours: Get traces from last N hours
            limit: Maximum number of traces to return

        Returns:
            List of trace dictionaries (serializable)

        Example:
            # Get last 24 hours of user_interpret traces
            traces = api.get_traces(agent="user_interpret", hours=24)
        """
        try:
            if hours:
                traces = self.trace_manager.get_traces_since(hours=hours, agent=agent)
            elif date:
                traces = self.trace_manager.list_traces(date=date, agent=agent)
            else:
                traces = self.trace_manager.list_traces(agent=agent)

            # Sort by timestamp descending (newest first)
            traces.sort(key=lambda t: t.timestamp, reverse=True)

            # Apply limit
            traces = traces[:limit]

            # Convert to dictionaries for JSON serialization
            return [trace.to_dict() for trace in traces]
        except Exception as e:
            logger.error(f"Failed to get traces: {e}")
            return []

    def get_trace_by_id(self, trace_id: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get specific trace by ID.

        Args:
            trace_id: Trace ID to retrieve
            date: Optional date hint (YYYY-MM-DD) to speed up search

        Returns:
            Trace dictionary or None if not found
        """
        try:
            trace = self.trace_manager.read_trace(trace_id, date=date)
            return trace.to_dict()
        except FileNotFoundError:
            logger.warning(f"Trace not found: {trace_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get trace {trace_id}: {e}")
            return None

    def get_playbook(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get playbook for agent.

        Args:
            agent_name: Agent name

        Returns:
            Playbook dictionary or None if not found

        Example:
            playbook = api.get_playbook("user_interpret")
            print(f"Total bullets: {playbook['total_bullets']}")
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            return playbook.to_dict()
        except Exception as e:
            logger.error(f"Failed to get playbook for {agent_name}: {e}")
            return None

    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get ACE metrics for analytics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with aggregated metrics

        Example:
            metrics = api.get_metrics(days=7)
            print(f"Total traces: {metrics['total_traces']}")
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()

            # Filter by date range
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]

            # Calculate metrics
            total_traces = len(recent_traces)
            success_traces = len([t for t in recent_traces if self._is_success(t)])
            failure_traces = len([t for t in recent_traces if not self._is_success(t)])

            success_rate = (success_traces / total_traces * 100) if total_traces > 0 else 0.0

            # Per-agent metrics
            agent_metrics = {}
            agents = set(t.agent_identity.get("target_agent", "unknown") for t in recent_traces)

            for agent_name in agents:
                agent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent_name]
                agent_success = len([t for t in agent_traces if self._is_success(t)])
                agent_total = len(agent_traces)

                avg_duration = (
                    sum(sum(e.duration_seconds for e in t.executions) for t in agent_traces) / agent_total
                    if agent_total > 0
                    else 0.0
                )

                agent_metrics[agent_name] = {
                    "total_traces": agent_total,
                    "success_count": agent_success,
                    "failure_count": agent_total - agent_success,
                    "success_rate": ((agent_success / agent_total * 100) if agent_total > 0 else 0.0),
                    "avg_duration_seconds": round(avg_duration, 2),
                }

            # Trace stats by day
            traces_by_day = {}
            for trace in recent_traces:
                day = trace.timestamp.strftime("%Y-%m-%d")
                traces_by_day[day] = traces_by_day.get(day, 0) + 1

            return {
                "date_range_days": days,
                "total_traces": total_traces,
                "success_count": success_traces,
                "failure_count": failure_traces,
                "success_rate": round(success_rate, 2),
                "agent_metrics": agent_metrics,
                "traces_by_day": traces_by_day,
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "date_range_days": days,
                "total_traces": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "agent_metrics": {},
                "traces_by_day": {},
            }

    def get_reflection_status(self) -> Dict[str, Any]:
        """Get reflector status.

        Returns:
            Dictionary with reflector status info
        """
        try:
            # Check for latest delta files
            delta_dir = self.config.delta_dir
            if not delta_dir.exists():
                return {
                    "last_run": None,
                    "pending_traces": 0,
                    "delta_items_generated": 0,
                }

            # Find most recent delta file
            delta_files = sorted(delta_dir.glob("delta_*.json"), reverse=True)
            last_run = None
            delta_items_generated = 0

            if delta_files:
                latest_delta = delta_files[0]
                last_run = datetime.fromtimestamp(latest_delta.stat().st_mtime)

                # Count delta items in latest file
                try:
                    import json

                    with open(latest_delta, "r") as f:
                        deltas = json.load(f)
                        delta_items_generated = len(deltas.get("deltas", []))
                except Exception as e:
                    logger.warning(f"Failed to read delta file: {e}")

            # Count pending traces (traces without corresponding delta)
            all_traces = self.trace_manager.list_traces()
            pending_traces = len(all_traces)  # Simplified - could be more sophisticated

            return {
                "last_run": last_run.isoformat() if last_run else None,
                "pending_traces": pending_traces,
                "delta_items_generated": delta_items_generated,
            }
        except Exception as e:
            logger.error(f"Failed to get reflection status: {e}")
            return {
                "last_run": None,
                "pending_traces": 0,
                "delta_items_generated": 0,
            }

    def _is_success(self, trace: ExecutionTrace) -> bool:
        """Check if trace represents successful execution.

        Args:
            trace: ExecutionTrace to check

        Returns:
            True if all executions succeeded, False otherwise
        """
        if not trace.executions:
            return False
        return all(e.result_status == "success" for e in trace.executions)

    # Playbook curation methods

    def get_playbook_bullets(
        self,
        agent_name: str,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_effectiveness: Optional[float] = None,
        max_effectiveness: Optional[float] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get playbook bullets with optional filtering.

        Args:
            agent_name: Agent name
            category: Filter by category
            status: Filter by status (active, pending, archived)
            min_effectiveness: Minimum effectiveness score
            max_effectiveness: Maximum effectiveness score
            search_query: Text search in bullet content

        Returns:
            List of bullet dictionaries
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            bullets = playbook.bullets

            # Apply filters
            if category:
                bullets = [b for b in bullets if b.category == category]

            if status:
                bullets = [b for b in bullets if b.status == status]

            if min_effectiveness is not None:
                bullets = [b for b in bullets if b.effectiveness >= min_effectiveness]

            if max_effectiveness is not None:
                bullets = [b for b in bullets if b.effectiveness <= max_effectiveness]

            if search_query:
                query_lower = search_query.lower()
                bullets = [b for b in bullets if query_lower in b.content.lower()]

            return [b.to_dict() for b in bullets]
        except Exception as e:
            logger.error(f"Failed to get playbook bullets: {e}")
            return []

    def approve_bullet(self, agent_name: str, bullet_id: str) -> bool:
        """Approve a playbook bullet.

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID to approve

        Returns:
            True if successful, False otherwise
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()

            # Find and update bullet
            for bullet in playbook.bullets:
                if bullet.bullet_id == bullet_id:
                    bullet.status = "active"
                    bullet.metadata["approved_at"] = datetime.now().isoformat()
                    logger.info(f"Approved bullet {bullet_id} for {agent_name}")

                    # Save updated playbook
                    return loader.save(playbook)

            logger.warning(f"Bullet not found: {bullet_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to approve bullet: {e}")
            return False

    def reject_bullet(self, agent_name: str, bullet_id: str) -> bool:
        """Reject and archive a playbook bullet.

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID to reject

        Returns:
            True if successful, False otherwise
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()

            # Find and update bullet
            for bullet in playbook.bullets:
                if bullet.bullet_id == bullet_id:
                    bullet.status = "archived"
                    bullet.metadata["rejected_at"] = datetime.now().isoformat()
                    logger.info(f"Rejected bullet {bullet_id} for {agent_name}")

                    # Update playbook stats
                    playbook.total_bullets = len([b for b in playbook.bullets if b.status == "active"])
                    active_bullets = [b for b in playbook.bullets if b.status == "active"]
                    if active_bullets:
                        playbook.avg_effectiveness = sum(b.effectiveness for b in active_bullets) / len(active_bullets)

                    # Save updated playbook
                    return loader.save(playbook)

            logger.warning(f"Bullet not found: {bullet_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to reject bullet: {e}")
            return False

    def bulk_approve_bullets(self, agent_name: str, bullet_ids: List[str]) -> Dict[str, int]:
        """Approve multiple bullets at once.

        Args:
            agent_name: Agent name
            bullet_ids: List of bullet IDs to approve

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for bullet_id in bullet_ids:
            if self.approve_bullet(agent_name, bullet_id):
                success_count += 1
            else:
                failure_count += 1

        return {"success": success_count, "failure": failure_count}

    def bulk_reject_bullets(self, agent_name: str, bullet_ids: List[str]) -> Dict[str, int]:
        """Reject multiple bullets at once.

        Args:
            agent_name: Agent name
            bullet_ids: List of bullet IDs to reject

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for bullet_id in bullet_ids:
            if self.reject_bullet(agent_name, bullet_id):
                success_count += 1
            else:
                failure_count += 1

        return {"success": success_count, "failure": failure_count}

    def get_curation_queue(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get pending bullets awaiting curation.

        Args:
            agent_name: Agent name

        Returns:
            List of pending bullet dictionaries
        """
        try:
            bullets = self.get_playbook_bullets(agent_name, status="pending")
            logger.info(f"Retrieved {len(bullets)} pending bullets for {agent_name}")
            return bullets
        except Exception as e:
            logger.error(f"Failed to get curation queue: {e}")
            return []

    def get_playbook_categories(self, agent_name: str) -> List[str]:
        """Get all unique categories in playbook.

        Args:
            agent_name: Agent name

        Returns:
            List of category names
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            categories = sorted(set(b.category for b in playbook.bullets))
            return categories
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
