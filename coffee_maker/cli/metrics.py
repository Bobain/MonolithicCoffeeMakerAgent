"""Metrics tracking database for user story estimation and velocity.

This module provides a metrics tracking system for measuring estimation accuracy
and team velocity. Uses SQLite with WAL mode for multi-process safety.

Database Schema:
    story_metrics table:
        - id: Auto-increment ID
        - story_id: User story identifier (e.g., "US-015")
        - story_title: User story title
        - estimated_min_days: Minimum estimated days
        - estimated_max_days: Maximum estimated days
        - actual_days: Actual days taken
        - started_at: Start timestamp
        - completed_at: Completion timestamp
        - estimation_error_days: Actual - estimated average
        - estimation_accuracy_pct: Accuracy percentage
        - complexity: Story complexity (low, medium, high)
        - category: Story category (feature, bug, refactor, docs)
        - story_points: Story points (optional)
        - spec_phase_metrics: JSON array of phase metrics
        - has_technical_spec: Whether story has a technical spec
        - technical_spec_path: Path to technical spec file
        - created_at: Creation timestamp

    velocity_snapshots table:
        - id: Auto-increment ID
        - period_start: Period start date
        - period_end: Period end date
        - stories_completed: Number of stories completed
        - story_points_completed: Story points completed
        - total_days_actual: Total actual days
        - avg_estimation_accuracy_pct: Average estimation accuracy
        - created_at: Creation timestamp

Features:
    - WAL mode enabled (multi-process safe)
    - Retry logic for database operations
    - JSON support for phase metrics
    - Automatic calculation of estimation accuracy
    - Velocity tracking per time period

Example:
    Track user story:
    >>> from coffee_maker.cli.metrics import MetricsDB
    >>>
    >>> db = MetricsDB()
    >>> # When story starts
    >>> db.start_story("US-015", "Metrics Tracking",
    ...                estimated_min=3.0, estimated_max=5.0,
    ...                complexity="medium", category="feature")
    >>>
    >>> # When story completes
    >>> db.complete_story("US-015")
    >>>
    >>> # Get accuracy metrics
    >>> accuracy = db.get_estimation_accuracy(last_n=5)
    >>> velocity = db.get_current_velocity(period_days=7)
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from coffee_maker.config import DATABASE_PATHS
from coffee_maker.observability.retry import with_retry

logger = logging.getLogger(__name__)

# Default timeout for database operations (30 seconds)
DB_TIMEOUT = 30.0

# Story complexity levels
COMPLEXITY_LOW = "low"
COMPLEXITY_MEDIUM = "medium"
COMPLEXITY_HIGH = "high"

# Story categories
CATEGORY_FEATURE = "feature"
CATEGORY_BUG = "bug"
CATEGORY_REFACTOR = "refactor"
CATEGORY_DOCS = "docs"

CREATE_METRICS_TABLES = """
CREATE TABLE IF NOT EXISTS story_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL UNIQUE,
    story_title TEXT NOT NULL,

    -- Time estimation
    estimated_min_days REAL,
    estimated_max_days REAL,
    actual_days REAL,

    -- Timestamps
    started_at TEXT,
    completed_at TEXT,

    -- Calculation fields
    estimation_error_days REAL,
    estimation_accuracy_pct REAL,

    -- Context
    complexity TEXT,
    category TEXT,
    story_points INTEGER,

    -- Technical spec phase metrics (JSON)
    spec_phase_metrics TEXT,
    has_technical_spec INTEGER DEFAULT 0,
    technical_spec_path TEXT,

    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_story_completed ON story_metrics(completed_at);
CREATE INDEX IF NOT EXISTS idx_story_id ON story_metrics(story_id);
CREATE INDEX IF NOT EXISTS idx_story_category ON story_metrics(category);
CREATE INDEX IF NOT EXISTS idx_story_complexity ON story_metrics(complexity);

CREATE TABLE IF NOT EXISTS velocity_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,

    -- Velocity metrics
    stories_completed INTEGER NOT NULL DEFAULT 0,
    story_points_completed INTEGER NOT NULL DEFAULT 0,
    total_days_actual REAL NOT NULL DEFAULT 0.0,

    -- Estimation accuracy for this period
    avg_estimation_accuracy_pct REAL,

    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_velocity_period ON velocity_snapshots(period_start, period_end);
"""


class MetricsDB:
    """Metrics tracking database for user stories and velocity.

    This class provides estimation accuracy tracking and velocity measurement
    using SQLite with WAL mode and retry logic for reliability.

    Attributes:
        db_path: Path to SQLite database

    Example:
        >>> db = MetricsDB()
        >>> db.start_story("US-015", "Metrics Tracking", 3.0, 5.0, "medium", "feature")
        >>> # ... work happens ...
        >>> db.complete_story("US-015")
        >>> accuracy = db.get_estimation_accuracy(last_n=5)
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize metrics database.

        Args:
            db_path: Path to database file (defaults to DATABASE_PATHS['metrics'])
        """
        if db_path is None:
            # Use same directory as notifications.db
            notifications_path = Path(DATABASE_PATHS["notifications"])
            db_path = str(notifications_path.parent / "metrics.db")

        self.db_path = db_path

        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.debug(f"MetricsDB initialized: {db_path}")

    def _init_database(self):
        """Initialize database schema and enable WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=DB_TIMEOUT)

        # Enable WAL mode for multi-process safety
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second busy timeout

        # Create schema
        conn.executescript(CREATE_METRICS_TABLES)
        conn.commit()
        conn.close()

        logger.debug("Metrics database schema initialized with WAL mode")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration.

        Returns:
            Configured SQLite connection
        """
        conn = sqlite3.connect(self.db_path, timeout=DB_TIMEOUT)
        conn.row_factory = sqlite3.Row  # Dict-like row access
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def start_story(
        self,
        story_id: str,
        story_title: str,
        estimated_min_days: Optional[float] = None,
        estimated_max_days: Optional[float] = None,
        complexity: str = COMPLEXITY_MEDIUM,
        category: str = CATEGORY_FEATURE,
        story_points: Optional[int] = None,
        has_technical_spec: bool = False,
        technical_spec_path: Optional[str] = None,
    ) -> int:
        """Start tracking a user story.

        Records the start timestamp and initial estimates for a user story.

        Args:
            story_id: User story identifier (e.g., "US-015")
            story_title: User story title
            estimated_min_days: Minimum estimated days
            estimated_max_days: Maximum estimated days
            complexity: Story complexity (low, medium, high)
            category: Story category (feature, bug, refactor, docs)
            story_points: Optional story points
            has_technical_spec: Whether story has a technical spec
            technical_spec_path: Path to technical spec file

        Returns:
            Database row ID

        Example:
            >>> db = MetricsDB()
            >>> db.start_story("US-015", "Metrics Tracking", 3.0, 5.0, "medium", "feature")
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO story_metrics
                (story_id, story_title, estimated_min_days, estimated_max_days,
                 started_at, complexity, category, story_points,
                 has_technical_spec, technical_spec_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    story_id,
                    story_title,
                    estimated_min_days,
                    estimated_max_days,
                    now,
                    complexity,
                    category,
                    story_points,
                    1 if has_technical_spec else 0,
                    technical_spec_path,
                    now,
                ),
            )
            conn.commit()
            row_id = cursor.lastrowid

        logger.info(f"Started tracking story {story_id}: {story_title}")
        return row_id

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def complete_story(self, story_id: str, spec_phase_metrics: Optional[List[Dict]] = None) -> Tuple[float, float]:
        """Complete a user story and calculate metrics.

        Calculates actual time taken, estimation error, and accuracy percentage.

        Args:
            story_id: User story identifier
            spec_phase_metrics: Optional list of phase metrics from technical spec
                               Format: [{"phase": "Phase 1", "estimated_hours": 6,
                                        "actual_hours": 8, "accuracy_pct": 75}, ...]

        Returns:
            Tuple of (actual_days, estimation_accuracy_pct)

        Raises:
            ValueError: If story not found or not started

        Example:
            >>> db = MetricsDB()
            >>> actual, accuracy = db.complete_story("US-015")
            >>> print(f"Took {actual} days, {accuracy}% accuracy")
        """
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            # Get story data
            cursor = conn.execute("SELECT * FROM story_metrics WHERE story_id = ?", (story_id,))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Story {story_id} not found")

            if not row["started_at"]:
                raise ValueError(f"Story {story_id} not started")

            # Calculate actual days (simplified - using ISO timestamps)
            started = datetime.fromisoformat(row["started_at"])
            completed = datetime.fromisoformat(now)
            actual_days = (completed - started).total_seconds() / (24 * 3600)

            # Calculate estimation error and accuracy
            estimated_min = row["estimated_min_days"] or 0
            estimated_max = row["estimated_max_days"] or 0
            estimated_avg = (estimated_min + estimated_max) / 2 if estimated_max else estimated_min

            if estimated_avg > 0:
                estimation_error = actual_days - estimated_avg
                # Accuracy: 100% if exact, decreases with error
                # Formula: 100 - abs(error/estimated * 100), minimum 0%
                accuracy_pct = max(0, 100 - abs(estimation_error / estimated_avg * 100))
            else:
                estimation_error = None
                accuracy_pct = None

            # Convert spec phase metrics to JSON
            spec_metrics_json = json.dumps(spec_phase_metrics) if spec_phase_metrics else None

            # Update story
            conn.execute(
                """
                UPDATE story_metrics
                SET completed_at = ?,
                    actual_days = ?,
                    estimation_error_days = ?,
                    estimation_accuracy_pct = ?,
                    spec_phase_metrics = ?
                WHERE story_id = ?
                """,
                (now, actual_days, estimation_error, accuracy_pct, spec_metrics_json, story_id),
            )
            conn.commit()

        logger.info(f"Completed story {story_id}: {actual_days:.1f} days, " f"{accuracy_pct:.1f}% accuracy")

        return actual_days, accuracy_pct or 0.0

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_story_metrics(self, story_id: str) -> Optional[Dict]:
        """Get metrics for a specific story.

        Args:
            story_id: User story identifier

        Returns:
            Dictionary with story metrics or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM story_metrics WHERE story_id = ?", (story_id,))
            row = cursor.fetchone()

        if not row:
            return None

        metrics = dict(row)

        # Parse JSON spec_phase_metrics if present
        if metrics.get("spec_phase_metrics"):
            try:
                metrics["spec_phase_metrics"] = json.loads(metrics["spec_phase_metrics"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse spec_phase_metrics JSON")
                metrics["spec_phase_metrics"] = []

        return metrics

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_estimation_accuracy(self, last_n: Optional[int] = None, category: Optional[str] = None) -> Dict:
        """Get estimation accuracy metrics.

        Args:
            last_n: Number of recent stories to analyze (None = all)
            category: Filter by category (None = all categories)

        Returns:
            Dictionary with accuracy metrics:
            {
                "overall_accuracy_pct": 87.5,
                "stories_analyzed": 10,
                "within_20pct_count": 8,
                "within_20pct_rate": 0.8,
                "stories": [...]
            }
        """
        with self._get_connection() as conn:
            query = """
                SELECT story_id, story_title, estimated_min_days, estimated_max_days,
                       actual_days, estimation_accuracy_pct, category, completed_at
                FROM story_metrics
                WHERE completed_at IS NOT NULL
            """
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY completed_at DESC"

            if last_n:
                query += " LIMIT ?"
                params.append(last_n)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            return {
                "overall_accuracy_pct": 0.0,
                "stories_analyzed": 0,
                "within_20pct_count": 0,
                "within_20pct_rate": 0.0,
                "stories": [],
            }

        stories = [dict(row) for row in rows]

        # Calculate overall accuracy
        accuracies = [s["estimation_accuracy_pct"] for s in stories if s["estimation_accuracy_pct"]]
        overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0

        # Count stories within ±20% of estimate
        within_20pct = sum(1 for s in stories if s["estimation_accuracy_pct"] and s["estimation_accuracy_pct"] >= 80)
        within_20pct_rate = within_20pct / len(stories) if stories else 0.0

        return {
            "overall_accuracy_pct": overall_accuracy,
            "stories_analyzed": len(stories),
            "within_20pct_count": within_20pct,
            "within_20pct_rate": within_20pct_rate,
            "stories": stories,
        }

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_current_velocity(self, period_days: int = 7) -> Dict:
        """Get current velocity metrics.

        Args:
            period_days: Number of days to look back (default: 7 for weekly velocity)

        Returns:
            Dictionary with velocity metrics:
            {
                "period_start": "2025-10-06T00:00:00",
                "period_end": "2025-10-13T00:00:00",
                "stories_completed": 3,
                "total_days_actual": 12.5,
                "avg_days_per_story": 4.17,
                "story_points_completed": 13
            }
        """
        period_start = datetime.utcnow() - timedelta(days=period_days)
        period_start_iso = period_start.isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) as count,
                       SUM(actual_days) as total_days,
                       SUM(story_points) as total_points
                FROM story_metrics
                WHERE completed_at IS NOT NULL
                  AND completed_at >= ?
                """,
                (period_start_iso,),
            )
            row = cursor.fetchone()

        count = row["count"] or 0
        total_days = row["total_days"] or 0.0
        total_points = row["total_points"] or 0

        return {
            "period_start": period_start_iso,
            "period_end": datetime.utcnow().isoformat(),
            "stories_completed": count,
            "total_days_actual": total_days,
            "avg_days_per_story": total_days / count if count > 0 else 0.0,
            "story_points_completed": total_points,
        }

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def create_velocity_snapshot(self, period_days: int = 7) -> int:
        """Create a velocity snapshot for the specified period.

        Args:
            period_days: Number of days in the period

        Returns:
            Snapshot ID
        """
        velocity = self.get_current_velocity(period_days)
        accuracy = self.get_estimation_accuracy(last_n=None)  # All in period

        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO velocity_snapshots
                (period_start, period_end, stories_completed, story_points_completed,
                 total_days_actual, avg_estimation_accuracy_pct, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    velocity["period_start"],
                    velocity["period_end"],
                    velocity["stories_completed"],
                    velocity["story_points_completed"],
                    velocity["total_days_actual"],
                    accuracy["overall_accuracy_pct"],
                    now,
                ),
            )
            conn.commit()
            snapshot_id = cursor.lastrowid

        logger.info(f"Created velocity snapshot {snapshot_id} for {period_days} days")
        return snapshot_id

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_all_completed_stories(self) -> List[Dict]:
        """Get all completed stories with metrics.

        Returns:
            List of story dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM story_metrics
                WHERE completed_at IS NOT NULL
                ORDER BY completed_at DESC
                """
            )
            rows = cursor.fetchall()

        stories = []
        for row in rows:
            story = dict(row)
            # Parse JSON spec_phase_metrics if present
            if story.get("spec_phase_metrics"):
                try:
                    story["spec_phase_metrics"] = json.loads(story["spec_phase_metrics"])
                except json.JSONDecodeError:
                    story["spec_phase_metrics"] = []
            stories.append(story)

        return stories

    def close(self):
        """Close database connection."""
        # Connection is opened per-operation, nothing to close
        logger.debug("MetricsDB closed")
