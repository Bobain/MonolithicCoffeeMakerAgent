"""Alert management logic for error monitoring.

This module provides alert triggering and notification logic for the error
monitoring dashboard. It checks error rates and conditions against configured
thresholds and generates alerts.

Example:
    >>> from alert_manager import AlertManager
    >>> manager = AlertManager(error_rate_threshold=0.10)
    >>> alerts = manager.check_alerts("llm_metrics.db")
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

import pandas as pd


class AlertManager:
    """Manages alert rules and notifications for error monitoring."""

    def __init__(
        self,
        error_rate_threshold: float = 0.10,
        critical_error_threshold: int = 5,
        model_error_rate_threshold: float = 0.15,
        check_window_hours: int = 1,
    ):
        """Initialize AlertManager.

        Args:
            error_rate_threshold: Overall error rate threshold (default: 0.10 = 10%)
            critical_error_threshold: Critical error count threshold (default: 5)
            model_error_rate_threshold: Per-model error rate threshold (default: 0.15 = 15%)
            check_window_hours: Time window for checking alerts (default: 1 hour)
        """
        self.error_rate_threshold = error_rate_threshold
        self.critical_error_threshold = critical_error_threshold
        self.model_error_rate_threshold = model_error_rate_threshold
        self.check_window_hours = check_window_hours

    def check_alerts(self, db_path: str) -> List[Dict]:
        """Check all alert conditions and return triggered alerts.

        Args:
            db_path: Path to SQLite database

        Returns:
            List of triggered alert dictionaries

        Example:
            >>> manager = AlertManager()
            >>> alerts = manager.check_alerts("llm_metrics.db")
            >>> for alert in alerts:
            ...     print(f"{alert['severity']}: {alert['message']}")
        """
        alerts = []

        # Check high error rate
        error_rate_alert = self._check_error_rate(db_path)
        if error_rate_alert:
            alerts.append(error_rate_alert)

        # Check critical errors
        critical_alert = self._check_critical_errors(db_path)
        if critical_alert:
            alerts.append(critical_alert)

        # Check model degradation
        model_alerts = self._check_model_degradation(db_path)
        alerts.extend(model_alerts)

        # Check error spike
        spike_alert = self._check_error_spike(db_path)
        if spike_alert:
            alerts.append(spike_alert)

        return alerts

    def _check_error_rate(self, db_path: str) -> Optional[Dict]:
        """Check if overall error rate exceeds threshold.

        Args:
            db_path: Path to SQLite database

        Returns:
            Alert dict if threshold exceeded, None otherwise
        """
        conn = sqlite3.connect(db_path)
        cutoff_time = datetime.now() - timedelta(hours=self.check_window_hours)

        # Count errors and total traces
        query = """
            SELECT
                COUNT(DISTINCT CASE WHEN (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
                      THEN t.id END) as error_count,
                COUNT(DISTINCT t.id) as total_count
            FROM traces t
            LEFT JOIN events e ON t.id = e.trace_id
            WHERE t.timestamp >= ?
        """

        df = pd.read_sql_query(query, conn, params=[cutoff_time])
        conn.close()

        if df.empty or df.iloc[0]["total_count"] == 0:
            return None

        error_count = int(df.iloc[0]["error_count"])
        total_count = int(df.iloc[0]["total_count"])
        error_rate = error_count / total_count

        if error_rate > self.error_rate_threshold:
            return {
                "type": "high_error_rate",
                "severity": "HIGH",
                "timestamp": datetime.now(),
                "message": f"Error rate is {error_rate:.2%} (threshold: {self.error_rate_threshold:.2%})",
                "details": {
                    "error_count": error_count,
                    "total_count": total_count,
                    "error_rate": error_rate,
                    "window_hours": self.check_window_hours,
                },
            }

        return None

    def _check_critical_errors(self, db_path: str) -> Optional[Dict]:
        """Check if critical error count exceeds threshold.

        Args:
            db_path: Path to SQLite database

        Returns:
            Alert dict if threshold exceeded, None otherwise
        """
        conn = sqlite3.connect(db_path)
        cutoff_time = datetime.now() - timedelta(hours=self.check_window_hours)

        # Count critical-level errors (approximation based on keywords)
        query = """
            SELECT COUNT(DISTINCT t.id) as critical_count
            FROM traces t
            LEFT JOIN events e ON t.id = e.trace_id
            WHERE t.timestamp >= ?
              AND (e.level = 'ERROR' OR t.status_message IS NOT NULL)
              AND (
                  LOWER(e.message) LIKE '%critical%' OR
                  LOWER(e.message) LIKE '%fatal%' OR
                  LOWER(e.message) LIKE '%connection%' OR
                  LOWER(e.message) LIKE '%authentication%' OR
                  LOWER(t.status_message) LIKE '%critical%' OR
                  LOWER(t.status_message) LIKE '%fatal%'
              )
        """

        df = pd.read_sql_query(query, conn, params=[cutoff_time])
        conn.close()

        if df.empty:
            return None

        critical_count = int(df.iloc[0]["critical_count"])

        if critical_count > self.critical_error_threshold:
            return {
                "type": "critical_errors",
                "severity": "CRITICAL",
                "timestamp": datetime.now(),
                "message": f"{critical_count} critical errors detected (threshold: {self.critical_error_threshold})",
                "details": {
                    "critical_count": critical_count,
                    "window_hours": self.check_window_hours,
                },
            }

        return None

    def _check_model_degradation(self, db_path: str) -> List[Dict]:
        """Check if any model's error rate exceeds threshold.

        Args:
            db_path: Path to SQLite database

        Returns:
            List of alert dicts for models exceeding threshold
        """
        conn = sqlite3.connect(db_path)
        cutoff_time = datetime.now() - timedelta(hours=self.check_window_hours)

        query = """
            SELECT
                g.model,
                COUNT(DISTINCT CASE WHEN (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
                      THEN t.id END) as error_count,
                COUNT(DISTINCT t.id) as total_count
            FROM traces t
            LEFT JOIN events e ON t.id = e.trace_id
            LEFT JOIN generations g ON t.id = g.trace_id
            WHERE t.timestamp >= ? AND g.model IS NOT NULL
            GROUP BY g.model
            HAVING COUNT(DISTINCT t.id) > 0
        """

        df = pd.read_sql_query(query, conn, params=[cutoff_time])
        conn.close()

        alerts = []

        for _, row in df.iterrows():
            error_rate = row["error_count"] / row["total_count"]
            if error_rate > self.model_error_rate_threshold:
                alerts.append(
                    {
                        "type": "model_degradation",
                        "severity": "HIGH",
                        "timestamp": datetime.now(),
                        "message": f"Model '{row['model']}' error rate is {error_rate:.2%} (threshold: {self.model_error_rate_threshold:.2%})",
                        "details": {
                            "model": row["model"],
                            "error_count": int(row["error_count"]),
                            "total_count": int(row["total_count"]),
                            "error_rate": error_rate,
                            "window_hours": self.check_window_hours,
                        },
                    }
                )

        return alerts

    def _check_error_spike(self, db_path: str) -> Optional[Dict]:
        """Check if there's been a sudden spike in errors.

        Args:
            db_path: Path to SQLite database

        Returns:
            Alert dict if spike detected, None otherwise
        """
        conn = sqlite3.connect(db_path)

        # Compare last hour to previous hour
        current_hour = datetime.now() - timedelta(hours=1)
        previous_hour = datetime.now() - timedelta(hours=2)

        query = """
            SELECT
                CASE
                    WHEN t.timestamp >= ? THEN 'current'
                    ELSE 'previous'
                END as period,
                COUNT(DISTINCT t.id) as error_count
            FROM traces t
            LEFT JOIN events e ON t.id = e.trace_id
            WHERE t.timestamp >= ?
              AND (e.level IN ('ERROR', 'WARNING') OR t.status_message IS NOT NULL)
            GROUP BY period
        """

        df = pd.read_sql_query(query, conn, params=[current_hour, previous_hour])
        conn.close()

        if len(df) < 2:
            return None

        current_errors = df[df["period"] == "current"]["error_count"].values
        previous_errors = df[df["period"] == "previous"]["error_count"].values

        if len(current_errors) == 0 or len(previous_errors) == 0:
            return None

        current_count = int(current_errors[0])
        previous_count = int(previous_errors[0])

        # Check if errors doubled or increased by more than 10
        if current_count > previous_count * 2 or (current_count - previous_count) > 10:
            return {
                "type": "error_spike",
                "severity": "HIGH",
                "timestamp": datetime.now(),
                "message": f"Error spike detected: {current_count} errors in last hour vs {previous_count} in previous hour",
                "details": {
                    "current_hour_errors": current_count,
                    "previous_hour_errors": previous_count,
                    "increase_percentage": (
                        (current_count - previous_count) / previous_count * 100 if previous_count > 0 else 0
                    ),
                },
            }

        return None

    def get_alert_summary(self, alerts: List[Dict]) -> Dict:
        """Get summary statistics for a list of alerts.

        Args:
            alerts: List of alert dictionaries

        Returns:
            Summary dictionary with counts by severity

        Example:
            >>> summary = manager.get_alert_summary(alerts)
            >>> print(f"Critical: {summary['CRITICAL']}")
        """
        summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for alert in alerts:
            severity = alert.get("severity", "MEDIUM")
            summary[severity] = summary.get(severity, 0) + 1

        summary["total"] = len(alerts)

        return summary

    def format_alert(self, alert: Dict) -> str:
        """Format an alert for display.

        Args:
            alert: Alert dictionary

        Returns:
            Formatted alert string

        Example:
            >>> alert = {"severity": "HIGH", "message": "Error rate high"}
            >>> print(manager.format_alert(alert))
        """
        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
        emoji = severity_emoji.get(alert["severity"], "⚪")

        timestamp = alert.get("timestamp", datetime.now())
        formatted_time = timestamp.strftime("%H:%M:%S")

        return f"{emoji} {formatted_time} | {alert['severity']} | {alert['message']}"
