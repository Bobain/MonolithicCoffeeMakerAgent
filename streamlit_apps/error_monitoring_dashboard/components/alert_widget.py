"""
Alert widget component for the Error Monitoring Dashboard.

This module provides components for displaying active alerts with severity
indicators, thresholds, and actionable recommendations.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime, timedelta

from streamlit_apps.error_monitoring_dashboard.utils.error_classifier import ErrorClassifier


def render_active_alerts(alerts: List[Dict[str, Any]], max_display: int = 5) -> None:
    """
    Render active alerts with severity indicators and recommendations.

    Args:
        alerts: List of alert dictionaries with keys:
            - alert_id (str): Unique alert identifier
            - title (str): Alert title
            - severity (str): Alert severity (CRITICAL, HIGH, MEDIUM, LOW)
            - message (str): Alert description
            - recommendation (str): Suggested action
            - timestamp (datetime): When alert was triggered
            - metric_value (float): The metric value that triggered the alert
            - threshold (float): The threshold that was exceeded
        max_display: Maximum number of alerts to display (default: 5)

    Example:
        >>> alerts = [
        ...     {
        ...         "alert_id": "alert_1",
        ...         "title": "High Error Rate",
        ...         "severity": "HIGH",
        ...         "message": "Error rate exceeded 5%",
        ...         "recommendation": "Investigate recent deployments",
        ...         "timestamp": datetime.now(),
        ...         "metric_value": 7.5,
        ...         "threshold": 5.0
        ...     }
        ... ]
        >>> render_active_alerts(alerts)

    Notes:
        - Alerts are sorted by severity (highest first)
        - Each alert shows severity badge, message, and action button
        - Color-coded based on severity level
    """
    if not alerts:
        st.success("No active alerts - system is healthy")
        return

    st.markdown(f"### Active Alerts ({len(alerts)})")

    # Sort by severity
    sorted_alerts = sorted(
        alerts[:max_display], key=lambda x: ErrorClassifier.get_severity_order(x.get("severity", "UNKNOWN"))
    )

    for alert in sorted_alerts:
        render_single_alert(alert)


def render_single_alert(alert: Dict[str, Any]) -> None:
    """
    Render a single alert card with full details.

    Args:
        alert: Alert dictionary with keys:
            - alert_id (str): Unique identifier
            - title (str): Alert title
            - severity (str): Severity level
            - message (str): Alert description
            - recommendation (str): Suggested action
            - timestamp (datetime): When triggered
            - metric_value (float): Current metric value
            - threshold (float): Alert threshold

    Example:
        >>> alert = {
        ...     "alert_id": "alert_1",
        ...     "title": "Critical Error Spike",
        ...     "severity": "CRITICAL",
        ...     "message": "Critical errors increased by 300% in last hour",
        ...     "recommendation": "Check API status and recent deployments",
        ...     "timestamp": datetime.now()
        ... }
        >>> render_single_alert(alert)

    Notes:
        - Displays as colored card based on severity
        - Shows timestamp and metric details
        - Includes expandable recommendation section
    """
    severity = alert.get("severity", "UNKNOWN")
    color = ErrorClassifier.get_severity_color(severity)
    emoji = ErrorClassifier.get_severity_emoji(severity)

    # Create colored container
    with st.container():
        st.markdown(
            f"""
            <div style='padding: 15px; border-left: 5px solid {color};
                        background-color: rgba(255,255,255,0.05);
                        border-radius: 5px; margin-bottom: 10px;'>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"{emoji} **{alert.get('title', 'Unknown Alert')}**")
            st.caption(alert.get("message", "No description"))

        with col2:
            st.markdown(f"**{severity}**")
            timestamp = alert.get("timestamp")
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                time_ago = _format_time_ago(timestamp)
                st.caption(time_ago)

        # Metric details
        metric_value = alert.get("metric_value")
        threshold = alert.get("threshold")

        if metric_value is not None and threshold is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Value", f"{metric_value:.2f}")
            with col2:
                st.metric("Threshold", f"{threshold:.2f}")

        # Recommendation
        recommendation = alert.get("recommendation")
        if recommendation:
            with st.expander("Recommendation"):
                st.info(recommendation)

        st.divider()


def render_alert_summary(alert_counts: Dict[str, int]) -> None:
    """
    Render a compact summary of alert counts by severity.

    Args:
        alert_counts: Dictionary mapping severity levels to counts
            Example: {"CRITICAL": 2, "HIGH": 5, "MEDIUM": 8, "LOW": 3}

    Example:
        >>> counts = {"CRITICAL": 2, "HIGH": 5, "MEDIUM": 8, "LOW": 3}
        >>> render_alert_summary(counts)

    Notes:
        - Displays as horizontal bar with severity indicators
        - Shows total alert count
        - Color-coded by severity
    """
    total = sum(alert_counts.values())

    if total == 0:
        st.success("No active alerts")
        return

    st.markdown(f"### Alert Summary ({total} total)")

    # Create columns for each severity
    cols = st.columns(4)
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    for idx, severity in enumerate(severities):
        with cols[idx]:
            count = alert_counts.get(severity, 0)
            emoji = ErrorClassifier.get_severity_emoji(severity)
            color = ErrorClassifier.get_severity_color(severity)

            st.markdown(
                f"<div style='text-align: center;'>"
                f"<span style='font-size: 32px;'>{emoji}</span><br>"
                f"<span style='font-size: 24px; font-weight: bold; color: {color};'>{count}</span><br>"
                f"<span style='font-size: 12px;'>{severity}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_alert_threshold_config(
    current_thresholds: Dict[str, float], editable: bool = True
) -> Optional[Dict[str, float]]:
    """
    Render alert threshold configuration interface.

    Args:
        current_thresholds: Dictionary of current threshold values
            Example: {
                "error_rate": 5.0,
                "critical_errors": 10,
                "failure_rate": 3.0
            }
        editable: Whether thresholds can be edited (default: True)

    Returns:
        Updated thresholds dictionary if editable, None otherwise

    Example:
        >>> thresholds = {
        ...     "error_rate": 5.0,
        ...     "critical_errors": 10,
        ...     "failure_rate": 3.0
        ... }
        >>> new_thresholds = render_alert_threshold_config(thresholds)

    Notes:
        - Provides sliders or number inputs for each threshold
        - Shows current values and allows adjustment
        - Returns updated values if changed
    """
    st.markdown("### Alert Thresholds")

    if not editable:
        for metric, value in current_thresholds.items():
            st.text(f"{metric.replace('_', ' ').title()}: {value}")
        return None

    updated_thresholds = {}

    col1, col2 = st.columns(2)

    with col1:
        if "error_rate" in current_thresholds:
            updated_thresholds["error_rate"] = st.slider(
                "Error Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=current_thresholds["error_rate"],
                step=0.5,
                help="Trigger alert when error rate exceeds this percentage",
            )

        if "critical_errors" in current_thresholds:
            updated_thresholds["critical_errors"] = st.number_input(
                "Critical Errors Threshold",
                min_value=1,
                max_value=100,
                value=int(current_thresholds["critical_errors"]),
                help="Trigger alert when critical errors exceed this count",
            )

    with col2:
        if "failure_rate" in current_thresholds:
            updated_thresholds["failure_rate"] = st.slider(
                "Failure Rate (%)",
                min_value=0.0,
                max_value=10.0,
                value=current_thresholds["failure_rate"],
                step=0.1,
                help="Trigger alert when failure rate exceeds this percentage",
            )

        if "latency_p95" in current_thresholds:
            updated_thresholds["latency_p95"] = st.number_input(
                "P95 Latency (ms)",
                min_value=100,
                max_value=10000,
                value=int(current_thresholds["latency_p95"]),
                step=100,
                help="Trigger alert when P95 latency exceeds this value",
            )

    return updated_thresholds


def render_alert_banner(
    alert_level: Literal["critical", "warning", "info", "success"], message: str, dismissible: bool = True
) -> None:
    """
    Render a prominent alert banner at the top of the page.

    Args:
        alert_level: Level of alert (critical, warning, info, success)
        message: Message to display
        dismissible: Whether the banner can be dismissed (default: True)

    Example:
        >>> render_alert_banner("critical", "Critical system error detected!")
        >>> render_alert_banner("warning", "Error rate elevated")
        >>> render_alert_banner("success", "All systems operational")

    Notes:
        - Banner spans full width of page
        - Color-coded by alert level
        - Can be dismissed by user if dismissible=True
    """
    alert_config = {
        "critical": {"icon": "🔴", "func": st.error},
        "warning": {"icon": "🟡", "func": st.warning},
        "info": {"icon": "🔵", "func": st.info},
        "success": {"icon": "🟢", "func": st.success},
    }

    config = alert_config.get(alert_level, alert_config["info"])
    icon = config["icon"]
    func = config["func"]

    func(f"{icon} {message}")


def render_alert_timeline(alerts: List[Dict[str, Any]], hours: int = 24) -> None:
    """
    Render a timeline view of alerts over a time period.

    Args:
        alerts: List of alert dictionaries
        hours: Number of hours to display (default: 24)

    Example:
        >>> alerts = [
        ...     {"timestamp": datetime.now(), "severity": "HIGH", "title": "Error spike"},
        ...     {"timestamp": datetime.now() - timedelta(hours=2), "severity": "MEDIUM", "title": "Latency"}
        ... ]
        >>> render_alert_timeline(alerts, hours=24)

    Notes:
        - Shows alerts in chronological order
        - Groups alerts by hour
        - Color-coded by severity
    """
    if not alerts:
        st.info("No alerts in the selected time period")
        return

    st.markdown(f"### Alert Timeline (Last {hours} hours)")

    # Filter alerts within time range
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_alerts = [
        alert for alert in alerts if isinstance(alert.get("timestamp"), datetime) and alert["timestamp"] >= cutoff_time
    ]

    if not recent_alerts:
        st.info("No alerts in the selected time period")
        return

    # Sort by timestamp (newest first)
    recent_alerts.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)

    # Display timeline
    for alert in recent_alerts:
        timestamp = alert.get("timestamp")
        title = alert.get("title", "Unknown Alert")
        severity = alert.get("severity", "UNKNOWN")
        emoji = ErrorClassifier.get_severity_emoji(severity)

        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "Unknown"

        col1, col2, col3 = st.columns([2, 1, 6])

        with col1:
            st.text(time_str)
        with col2:
            st.markdown(f"**{emoji} {severity}**")
        with col3:
            st.text(title)


def render_notification_settings(current_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render notification settings interface.

    Args:
        current_settings: Dictionary of current notification settings
            Example: {
                "email_enabled": True,
                "slack_enabled": False,
                "webhook_url": "https://hooks.slack.com/...",
                "min_severity": "HIGH"
            }

    Returns:
        Updated settings dictionary

    Example:
        >>> settings = {
        ...     "email_enabled": True,
        ...     "min_severity": "HIGH"
        ... }
        >>> new_settings = render_notification_settings(settings)

    Notes:
        - Allows configuration of notification channels
        - Sets minimum severity for notifications
        - Provides test notification button
    """
    st.markdown("### Notification Settings")

    updated_settings = {}

    col1, col2 = st.columns(2)

    with col1:
        updated_settings["email_enabled"] = st.checkbox(
            "Enable Email Notifications", value=current_settings.get("email_enabled", False)
        )

        updated_settings["slack_enabled"] = st.checkbox(
            "Enable Slack Notifications", value=current_settings.get("slack_enabled", False)
        )

    with col2:
        updated_settings["min_severity"] = st.selectbox(
            "Minimum Severity",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            index=["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(current_settings.get("min_severity", "HIGH")),
            help="Only send notifications for alerts at or above this severity",
        )

    if updated_settings["slack_enabled"]:
        updated_settings["webhook_url"] = st.text_input(
            "Slack Webhook URL", value=current_settings.get("webhook_url", ""), type="password"
        )

    if st.button("Send Test Notification"):
        st.info("Test notification sent (this is a simulation)")

    return updated_settings


def _format_time_ago(timestamp: datetime) -> str:
    """
    Format timestamp as "X minutes/hours/days ago".

    Args:
        timestamp: Datetime to format

    Returns:
        Formatted time string

    Example:
        >>> now = datetime.now()
        >>> _format_time_ago(now - timedelta(minutes=5))
        '5 minutes ago'
    """
    now = datetime.now()
    diff = now - timestamp

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
