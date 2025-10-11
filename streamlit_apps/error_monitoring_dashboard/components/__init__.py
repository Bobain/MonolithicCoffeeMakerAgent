"""
Error Monitoring Dashboard Components Package.

This package provides reusable Streamlit components for error monitoring
and visualization including metric cards, charts, trace viewers, and alerts.
"""

from streamlit_apps.error_monitoring_dashboard.components.error_cards import (
    render_error_summary_cards,
    render_severity_metric_cards,
    render_error_delta_metric,
    render_model_error_cards,
    render_category_breakdown,
    render_status_indicator,
    render_time_since_last_error,
)

from streamlit_apps.error_monitoring_dashboard.components.error_charts import (
    create_error_timeline,
    create_severity_pie_chart,
    create_error_type_bar_chart,
    create_model_error_comparison,
    create_failure_rate_chart,
    create_error_heatmap,
    create_category_pie_chart,
    create_stacked_severity_timeline,
)

from streamlit_apps.error_monitoring_dashboard.components.trace_viewer import (
    render_trace_details,
    render_trace_list,
    render_trace_comparison,
    render_compact_trace,
    render_trace_table,
)

from streamlit_apps.error_monitoring_dashboard.components.alert_widget import (
    render_active_alerts,
    render_single_alert,
    render_alert_summary,
    render_alert_threshold_config,
    render_alert_banner,
    render_alert_timeline,
    render_notification_settings,
)

__all__ = [
    # Error Cards
    "render_error_summary_cards",
    "render_severity_metric_cards",
    "render_error_delta_metric",
    "render_model_error_cards",
    "render_category_breakdown",
    "render_status_indicator",
    "render_time_since_last_error",
    # Error Charts
    "create_error_timeline",
    "create_severity_pie_chart",
    "create_error_type_bar_chart",
    "create_model_error_comparison",
    "create_failure_rate_chart",
    "create_error_heatmap",
    "create_category_pie_chart",
    "create_stacked_severity_timeline",
    # Trace Viewer
    "render_trace_details",
    "render_trace_list",
    "render_trace_comparison",
    "render_compact_trace",
    "render_trace_table",
    # Alert Widget
    "render_active_alerts",
    "render_single_alert",
    "render_alert_summary",
    "render_alert_threshold_config",
    "render_alert_banner",
    "render_alert_timeline",
    "render_notification_settings",
]
