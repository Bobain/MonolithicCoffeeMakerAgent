"""Trace storage manager for ACE framework.

This module manages the storage, retrieval, and querying of execution traces.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from coffee_maker.autonomous.ace.models import ExecutionTrace
from coffee_maker.utils.file_io import atomic_write_json, read_json_file

logger = logging.getLogger(__name__)


class TraceManager:
    """Manages execution trace storage and retrieval.

    Traces are stored in a date-based directory structure:
        docs/generator/traces/YYYY-MM-DD/trace_<timestamp>.json

    Example:
        manager = TraceManager()
        trace_path = manager.write_trace(trace)
        loaded_trace = manager.read_trace(trace.trace_id)
        recent_traces = manager.get_latest_traces(n=10)
    """

    def __init__(self, base_dir: Path):
        """Initialize trace manager.

        Args:
            base_dir: Base directory for trace storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TraceManager initialized with base_dir: {self.base_dir}")

    def write_trace(self, trace: ExecutionTrace) -> Path:
        """Write trace to JSON and Markdown.

        Args:
            trace: ExecutionTrace to write

        Returns:
            Path to the JSON file

        Example:
            trace_path = manager.write_trace(trace)
            print(f"Trace written to: {trace_path}")
        """
        # Create date-based subdirectory
        date_str = trace.timestamp.strftime("%Y-%m-%d")
        date_dir = self.base_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate file paths
        json_path = date_dir / f"trace_{trace.trace_id}.json"
        md_path = date_dir / f"trace_{trace.trace_id}.md"

        # Write JSON
        try:
            atomic_write_json(json_path, trace.to_dict())
            logger.info(f"Wrote trace JSON: {json_path}")
        except Exception as e:
            logger.error(f"Failed to write trace JSON: {e}")
            raise

        # Write Markdown
        try:
            md_content = trace.to_markdown()
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            logger.info(f"Wrote trace Markdown: {md_path}")
        except Exception as e:
            logger.warning(f"Failed to write trace Markdown: {e}")
            # Don't raise - Markdown is optional

        return json_path

    def read_trace(self, trace_id: str, date: Optional[str] = None) -> ExecutionTrace:
        """Read trace by ID.

        Args:
            trace_id: Trace ID to read
            date: Optional date string (YYYY-MM-DD) to narrow search

        Returns:
            ExecutionTrace instance

        Raises:
            FileNotFoundError: If trace not found

        Example:
            trace = manager.read_trace("1728925234")
            print(f"Loaded trace: {trace.user_query}")
        """
        if date:
            # Search specific date
            json_path = self.base_dir / date / f"trace_{trace_id}.json"
            if json_path.exists():
                data = read_json_file(json_path)
                return ExecutionTrace.from_dict(data)
        else:
            # Search all dates
            for date_dir in sorted(self.base_dir.iterdir(), reverse=True):
                if not date_dir.is_dir():
                    continue

                json_path = date_dir / f"trace_{trace_id}.json"
                if json_path.exists():
                    data = read_json_file(json_path)
                    return ExecutionTrace.from_dict(data)

        raise FileNotFoundError(f"Trace not found: {trace_id}")

    def list_traces(self, date: Optional[str] = None, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """List traces with optional filters.

        Args:
            date: Optional date string (YYYY-MM-DD) to filter
            agent: Optional agent name to filter

        Returns:
            List of ExecutionTrace instances

        Example:
            # All traces from today
            traces = manager.list_traces(date="2025-10-14")

            # All traces for code_developer
            traces = manager.list_traces(agent="code_developer")
        """
        traces = []

        if date:
            # Search specific date
            date_dir = self.base_dir / date
            if date_dir.exists():
                traces.extend(self._load_traces_from_dir(date_dir, agent))
        else:
            # Search all dates
            for date_dir in sorted(self.base_dir.iterdir(), reverse=True):
                if not date_dir.is_dir():
                    continue
                traces.extend(self._load_traces_from_dir(date_dir, agent))

        return traces

    def get_latest_traces(self, n: int = 10, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """Get N most recent traces.

        Args:
            n: Number of traces to return
            agent: Optional agent name to filter

        Returns:
            List of most recent ExecutionTrace instances

        Example:
            recent = manager.get_latest_traces(n=5, agent="code_developer")
            for trace in recent:
                print(f"{trace.timestamp}: {trace.user_query}")
        """
        all_traces = self.list_traces(agent=agent)

        # Sort by timestamp descending
        all_traces.sort(key=lambda t: t.timestamp, reverse=True)

        return all_traces[:n]

    def get_traces_since(self, hours: int, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """Get traces from the last N hours.

        Args:
            hours: Number of hours to look back
            agent: Optional agent name to filter

        Returns:
            List of ExecutionTrace instances from last N hours

        Example:
            # Get all traces from last 24 hours
            recent = manager.get_traces_since(hours=24)
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        all_traces = self.list_traces(agent=agent)

        return [trace for trace in all_traces if trace.timestamp >= cutoff]

    def _load_traces_from_dir(self, date_dir: Path, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """Load all traces from a date directory.

        Args:
            date_dir: Directory containing traces
            agent: Optional agent name to filter

        Returns:
            List of ExecutionTrace instances
        """
        traces = []

        for json_path in date_dir.glob("trace_*.json"):
            try:
                data = read_json_file(json_path)
                trace = ExecutionTrace.from_dict(data)

                # Apply agent filter if specified
                if agent and trace.agent_identity.get("target_agent") != agent:
                    continue

                traces.append(trace)
            except Exception as e:
                logger.warning(f"Failed to load trace {json_path}: {e}")
                continue

        return traces

    def delete_old_traces(self, days: int = 90):
        """Delete traces older than specified days.

        Args:
            days: Number of days to keep (default: 90)

        Example:
            # Delete traces older than 90 days
            manager.delete_old_traces(days=90)
        """
        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for date_dir in self.base_dir.iterdir():
            if not date_dir.is_dir():
                continue

            # Parse date from directory name
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Skipping non-date directory: {date_dir}")
                continue

            if dir_date < cutoff:
                # Delete entire directory
                for file_path in date_dir.iterdir():
                    file_path.unlink()
                    deleted_count += 1
                date_dir.rmdir()
                logger.info(f"Deleted old traces from {date_dir.name}")

        logger.info(f"Deleted {deleted_count} old trace files")

    def get_stats(self) -> dict:
        """Get statistics about stored traces.

        Returns:
            Dictionary with statistics

        Example:
            stats = manager.get_stats()
            print(f"Total traces: {stats['total_traces']}")
        """
        total_traces = 0
        total_size_bytes = 0
        dates = []

        for date_dir in self.base_dir.iterdir():
            if not date_dir.is_dir():
                continue

            dates.append(date_dir.name)
            for json_path in date_dir.glob("trace_*.json"):
                total_traces += 1
                total_size_bytes += json_path.stat().st_size

        return {
            "total_traces": total_traces,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "date_range": f"{min(dates)} to {max(dates)}" if dates else "No traces",
            "dates_with_traces": len(dates),
        }
