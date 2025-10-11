"""
Streamlit Analytics Dashboard for LLM Metrics.

This package provides a comprehensive analytics dashboard for monitoring
LLM usage, costs, and performance metrics from Langfuse exports.

Main Features:
- Real-time analytics with caching
- Interactive visualizations using Plotly
- Cost tracking and budget monitoring
- Model performance comparison
- Agent-specific analytics
- Data export capabilities (CSV, PDF)

Usage:
    $ cd /path/to/MonolithicCoffeeMakerAgent
    $ streamlit run streamlit_apps/analytics_dashboard/app.py

Modules:
    - config: Configuration management
    - queries: Database query functions
    - components: Reusable UI components
    - utils: Utility functions
    - pages: Dashboard page modules

Environment Variables:
    SQLITE_PATH: Path to SQLite database (default: llm_metrics.db)
    DASHBOARD_TITLE: Dashboard title
    CACHE_TTL: Cache TTL in seconds (default: 300)

For more information, see README.md and DEVELOPMENT.md.
"""

__version__ = "1.0.0"
__author__ = "MonolithicCoffeeMakerAgent Team"
