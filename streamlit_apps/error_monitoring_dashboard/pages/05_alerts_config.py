"""Alerts Configuration Page for Error Monitoring Dashboard.

This page provides alert management including active alerts display, threshold
configuration, alert rule management, and notification settings.
"""

import streamlit as st
from datetime import datetime

from streamlit_apps.error_monitoring_dashboard.config import get_config
from streamlit_apps.error_monitoring_dashboard.utils.alert_manager import AlertManager
from streamlit_apps.error_monitoring_dashboard.components import (
    render_active_alerts,
    render_alert_summary,
    render_alert_threshold_config,
    render_alert_timeline,
    render_notification_settings,
    render_alert_banner,
)

# Page configuration
st.set_page_config(
    page_title="Alerts Configuration - Error Monitoring",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
config = get_config()

# Page header
st.title("🚨 Alerts Configuration")
st.markdown(
    """
    Manage error monitoring alerts, configure thresholds, and set up notifications.
    Stay informed about critical issues in your LLM applications.
    """
)

# Sidebar - Alert Settings
st.sidebar.header("Alert Settings")

# Alert check interval
check_interval = st.sidebar.slider(
    "Check Interval (minutes)",
    min_value=1,
    max_value=60,
    value=config.alert_check_interval // 60,
    help="How often to check for new alerts",
)

# Alert window
alert_window = st.sidebar.selectbox(
    "Alert Time Window",
    options=[1, 2, 6, 12, 24],
    index=0,
    help="Time window in hours to check for alert conditions",
)

# Auto-refresh
auto_refresh = st.sidebar.checkbox(
    "Auto-refresh alerts",
    value=False,
    help="Automatically refresh alerts every check interval",
)

if auto_refresh:
    st.sidebar.info(f"Auto-refreshing every {check_interval} minutes")

# Manual refresh
if st.sidebar.button("🔄 Check Alerts Now"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Alert Types**

    - **High Error Rate**: Overall error rate exceeds threshold
    - **Critical Errors**: Critical error count exceeds limit
    - **Model Degradation**: Specific model error rate too high
    - **Error Spike**: Sudden increase in error volume
    """
)

# Main content
try:
    db_path = config.absolute_db_path

    # Initialize alert manager with current settings
    alert_manager = AlertManager(
        error_rate_threshold=config.error_rate_threshold,
        critical_error_threshold=config.critical_error_threshold,
        model_error_rate_threshold=0.15,  # 15%
        check_window_hours=alert_window,
    )

    # Check for active alerts
    active_alerts = alert_manager.check_alerts(db_path)

    # Format alerts for display
    formatted_alerts = []
    for alert in active_alerts:
        formatted_alerts.append(
            {
                "alert_id": f"alert_{hash(alert['message'])}",
                "title": alert["type"].replace("_", " ").title(),
                "severity": alert["severity"],
                "message": alert["message"],
                "recommendation": _get_recommendation(alert["type"]),
                "timestamp": alert["timestamp"],
                "metric_value": (
                    alert["details"].get("error_rate", 0) * 100
                    if "error_rate" in alert["details"]
                    else alert["details"].get("critical_count", 0)
                ),
                "threshold": (
                    config.error_rate_threshold * 100
                    if alert["type"] == "high_error_rate"
                    else config.critical_error_threshold
                ),
            }
        )

    # Display alert banner if critical alerts exist
    critical_alerts = [a for a in formatted_alerts if a["severity"] == "CRITICAL"]
    high_alerts = [a for a in formatted_alerts if a["severity"] == "HIGH"]

    if critical_alerts:
        render_alert_banner(
            "critical",
            f"🔴 {len(critical_alerts)} critical alert(s) detected! Immediate action required.",
        )
    elif high_alerts:
        render_alert_banner(
            "warning",
            f"🟡 {len(high_alerts)} high-priority alert(s) detected.",
        )
    elif not formatted_alerts:
        render_alert_banner(
            "success",
            "✅ All systems operational - no active alerts.",
        )

    st.divider()

    # Active Alerts Section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Active Alerts")

    with col2:
        # Alert summary
        alert_summary = alert_manager.get_alert_summary(active_alerts)
        st.metric("Total Active", alert_summary["total"])

    if formatted_alerts:
        # Show alert summary cards
        render_alert_summary(
            {
                "CRITICAL": alert_summary["CRITICAL"],
                "HIGH": alert_summary["HIGH"],
                "MEDIUM": alert_summary["MEDIUM"],
                "LOW": alert_summary["LOW"],
            }
        )

        st.markdown("---")

        # Show individual alerts
        render_active_alerts(formatted_alerts, max_display=10)

    else:
        st.success("✅ No active alerts - all systems operating normally")

    st.divider()

    # Alert Threshold Configuration
    st.header("Alert Threshold Configuration")
    st.caption("Configure when alerts should be triggered")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Thresholds")

        current_thresholds = {
            "error_rate": config.error_rate_threshold * 100,  # Convert to percentage
            "critical_errors": config.critical_error_threshold,
            "failure_rate": 3.0,
            "latency_p95": 5000,
        }

        updated_thresholds = render_alert_threshold_config(current_thresholds, editable=True)

        if updated_thresholds:
            if st.button("💾 Save Threshold Changes"):
                st.success("Threshold changes saved! (Note: In production, this would update config)")
                st.info(
                    """
                    **Note**: Threshold changes are session-only in this demo.
                    In production, these would be persisted to configuration.
                    """
                )

    with col2:
        st.subheader("Alert Rules")

        st.markdown("#### High Error Rate")
        st.write(f"Triggers when error rate exceeds {config.error_rate_threshold * 100:.1f}%")
        st.caption(f"Check window: {alert_window} hour(s)")

        st.markdown("#### Critical Errors")
        st.write(f"Triggers when critical errors exceed {config.critical_error_threshold}")
        st.caption(f"Check window: {alert_window} hour(s)")

        st.markdown("#### Model Degradation")
        st.write("Triggers when any model's error rate exceeds 15%")
        st.caption(f"Check window: {alert_window} hour(s)")

        st.markdown("#### Error Spike")
        st.write("Triggers when errors double compared to previous hour")
        st.caption("Compares last 2 hours of data")

    st.divider()

    # Alert Timeline
    st.header("Alert History Timeline")
    st.caption(f"Alert history for the last {alert_window * 2} hours")

    # Get historical alerts (in production, these would be stored)
    # For demo, we'll show current alerts as history
    render_alert_timeline(formatted_alerts, hours=alert_window * 2)

    st.divider()

    # Notification Settings
    st.header("Notification Settings")
    st.caption("Configure how and when you receive alert notifications")

    # Initialize with default settings
    if "notification_settings" not in st.session_state:
        st.session_state.notification_settings = {
            "email_enabled": False,
            "slack_enabled": False,
            "webhook_url": "",
            "min_severity": "HIGH",
        }

    # Render notification settings
    updated_settings = render_notification_settings(st.session_state.notification_settings)

    # Update session state
    if updated_settings != st.session_state.notification_settings:
        st.session_state.notification_settings = updated_settings

    # Save settings button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Notification Settings"):
            st.success("Notification settings saved!")
            st.info(
                """
                **Note**: Notification settings are session-only in this demo.
                In production, these would be persisted and used for real notifications.
                """
            )

    st.divider()

    # Test Alert Functionality
    st.header("Test Alert Functionality")
    st.caption("Simulate alerts to test your configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧪 Test High Error Rate Alert"):
            test_alert = {
                "alert_id": "test_high_error_rate",
                "title": "Test: High Error Rate",
                "severity": "HIGH",
                "message": "This is a test alert for high error rate (5.5% > 5.0%)",
                "recommendation": "This is a test - no action required",
                "timestamp": datetime.now(),
                "metric_value": 5.5,
                "threshold": 5.0,
            }
            st.info("Test alert generated:")
            from streamlit_apps.error_monitoring_dashboard.components.alert_widget import (
                render_single_alert,
            )

            render_single_alert(test_alert)

    with col2:
        if st.button("🧪 Test Critical Alert"):
            test_alert = {
                "alert_id": "test_critical",
                "title": "Test: Critical Error Threshold",
                "severity": "CRITICAL",
                "message": "This is a test critical alert (8 critical errors > 5 threshold)",
                "recommendation": "This is a test - no action required",
                "timestamp": datetime.now(),
                "metric_value": 8,
                "threshold": 5,
            }
            st.error("Test critical alert generated:")
            from streamlit_apps.error_monitoring_dashboard.components.alert_widget import (
                render_single_alert,
            )

            render_single_alert(test_alert)

    with col3:
        if st.button("🧪 Test Model Degradation"):
            test_alert = {
                "alert_id": "test_model_degradation",
                "title": "Test: Model Degradation",
                "severity": "HIGH",
                "message": "Test: Model 'gpt-4' error rate is 18% (threshold: 15%)",
                "recommendation": "This is a test - no action required",
                "timestamp": datetime.now(),
                "metric_value": 18.0,
                "threshold": 15.0,
            }
            st.warning("Test model degradation alert generated:")
            from streamlit_apps.error_monitoring_dashboard.components.alert_widget import (
                render_single_alert,
            )

            render_single_alert(test_alert)

    # Alert documentation
    with st.expander("📚 Alert Configuration Guide"):
        st.markdown(
            """
            ### How to Configure Alerts

            #### 1. Set Thresholds
            - Adjust error rate threshold based on your application's normal behavior
            - Set critical error count based on your tolerance for severe issues
            - Configure model-specific thresholds if certain models are more critical

            #### 2. Configure Notifications
            - Enable email or Slack notifications
            - Set minimum severity level to avoid alert fatigue
            - Test notifications to ensure they work correctly

            #### 3. Monitor and Adjust
            - Review alert history to identify false positives
            - Adjust thresholds based on actual operational patterns
            - Fine-tune notification settings over time

            #### 4. Alert Response Workflow
            1. **Critical Alerts**: Immediate investigation required
            2. **High Alerts**: Investigate within 1 hour
            3. **Medium Alerts**: Review within 4 hours
            4. **Low Alerts**: Monitor and review during next maintenance window

            #### Best Practices
            - Start with conservative thresholds and adjust based on experience
            - Use different thresholds for different time periods (e.g., higher during off-peak)
            - Set up escalation procedures for unresolved critical alerts
            - Regularly review and update alert rules based on system changes
            """
        )

except FileNotFoundError as e:
    st.error(f"❌ Database not found: {e}")
    st.info(
        "Please ensure the Langfuse export database exists at the configured path. "
        "Run the analytics export process first."
    )
except Exception as e:
    st.error(f"❌ Error loading alerts configuration: {e}")
    st.exception(e)


def _get_recommendation(alert_type: str) -> str:
    """Get recommendation text for alert type."""
    recommendations = {
        "high_error_rate": "Investigate recent deployments, check API status, and review error logs for common patterns.",
        "critical_errors": "Immediate action required: Check for system outages, authentication issues, or API connectivity problems.",
        "model_degradation": "Review model-specific issues: check API limits, model availability, and recent configuration changes.",
        "error_spike": "Investigate sudden increase: check for traffic spikes, recent code changes, or external API issues.",
    }
    return recommendations.get(alert_type, "Review error details and take appropriate action.")
