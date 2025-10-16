# PRIORITY 5: Streamlit Analytics Dashboard - Technical Specification

**Version**: 1.0
**Created**: 2025-10-11
**Status**: Ready for Implementation
**Estimated Duration**: 1-2 weeks (60-80 hours)
**Impact**: ⭐⭐⭐⭐⭐

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Dependencies](#prerequisites--dependencies)
3. [Architecture Overview](#architecture-overview)
4. [Database Schema Analysis](#database-schema-analysis)
5. [Component Specifications](#component-specifications)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Security Considerations](#security-considerations)
10. [Performance Requirements](#performance-requirements)
11. [Risk Analysis](#risk-analysis)
12. [Success Criteria](#success-criteria)
13. [Appendix](#appendix)

---

## Executive Summary

### Objective

Create a comprehensive Streamlit-based analytics dashboard that provides interactive visualization and analysis of LLM usage, costs, performance metrics, and trends. The dashboard will leverage the existing analytics infrastructure from PRIORITY 1 to provide actionable insights for cost optimization and performance monitoring.

### Key Value Proposition

- **Immediate Cost Visibility**: Real-time view of LLM expenses across models and agents
- **Performance Insights**: Identify bottlenecks and optimize latency
- **Budget Management**: Track spending against budgets with predictive alerts
- **Data-Driven Decisions**: Enable optimization based on actual usage patterns
- **Non-Technical Access**: User-friendly interface for business stakeholders

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Overview │  │   Cost   │  │  Model   │  │  Agent   │   │
│  │   Page   │  │ Analysis │  │ Compare  │  │  Perf.   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Analytics Query Layer      │
        │  (analytics_queries.py)      │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │    SQLite/PostgreSQL DB      │
        │  (llm_metrics.db)            │
        │  Tables: traces, generations,│
        │  spans, performance_metrics  │
        └──────────────────────────────┘
                       ▲
                       │
        ┌──────────────┴───────────────┐
        │   Langfuse Exporter          │
        │  (PRIORITY 1 - Complete)     │
        └──────────────────────────────┘
```

---

## Prerequisites & Dependencies

### ✅ Completed Dependencies

1. **PRIORITY 1: Analytics & Observability** - COMPLETE
   - Langfuse integration: `coffee_maker/langchain_observe/analytics/`
   - Database models: `models.py` (Trace, Generation, Span, PerformanceMetric)
   - Data exporter: `exporter.py` (LangfuseExporter)
   - Configuration: `config.py` (ExportConfig)
   - SQLite database: `llm_metrics.db`

### Required Python Packages

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
streamlit = "^1.32.0"
plotly = "^5.19.0"
pandas = "^2.2.0"
altair = "^5.2.0"
sqlalchemy = "^2.0.27"  # Already present
reportlab = "^4.1.0"    # For PDF export
```

### System Requirements

- Python >=3.11,<3.14
- SQLite 3.35+ (for JSON functions) or PostgreSQL 12+
- Minimum 2GB RAM for dashboard operation
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Database Schema Availability

**Existing Tables** (from PRIORITY 1):

- `traces`: Complete LLM execution traces
- `generations`: Individual LLM API calls with metrics
- `spans`: Intermediate steps/operations within traces
- `performance_metrics`: Pre-aggregated performance metrics
- `rate_limit_counters`: Rate limit tracking

**Database Path**: `llm_metrics.db` (configurable via `SQLITE_PATH` env var)

---

## Architecture Overview

### Directory Structure

```
streamlit_apps/
├── __init__.py                       # Package initialization
├── analytics_dashboard/
│   ├── __init__.py
│   ├── app.py                        # Main Streamlit app (entry point)
│   ├── config.py                     # Dashboard configuration
│   ├── README.md                     # Dashboard documentation
│   │
│   ├── pages/                        # Multi-page Streamlit app
│   │   ├── __init__.py
│   │   ├── 01_overview.py            # Global metrics overview
│   │   ├── 02_cost_analysis.py       # Detailed cost analysis
│   │   ├── 03_model_comparison.py    # Model performance comparison
│   │   ├── 04_agent_performance.py   # Agent-specific metrics
│   │   └── 05_exports.py             # Report generation & exports
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── __init__.py
│   │   ├── charts.py                 # Chart components (Plotly/Altair)
│   │   ├── metrics.py                # Metric display widgets
│   │   ├── filters.py                # Date/agent/model filters
│   │   └── tables.py                 # Data tables with sorting/filtering
│   │
│   ├── queries/                      # Database query layer
│   │   ├── __init__.py
│   │   ├── analytics_queries.py      # Core analytics queries
│   │   ├── cost_queries.py           # Cost-specific queries
│   │   ├── performance_queries.py    # Performance metric queries
│   │   └── export_queries.py         # Data export queries
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── data_processing.py        # Data transformation utilities
│   │   ├── export_utils.py           # PDF/CSV export utilities
│   │   ├── cache_utils.py            # Caching utilities
│   │   └── format_utils.py           # Formatting utilities
│   │
│   └── tests/                        # Dashboard tests
│       ├── __init__.py
│       ├── test_queries.py
│       ├── test_components.py
│       └── test_exports.py
```

### Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Web Framework** | Streamlit 1.32+ | Rapid development, native Python, built-in widgets |
| **Charting** | Plotly 5.19+ | Interactive charts, zoom/pan, hover tooltips |
| **Secondary Charts** | Altair 5.2+ | Declarative syntax, excellent for time-series |
| **Data Processing** | Pandas 2.2+ | Powerful data manipulation, aggregation |
| **Database ORM** | SQLAlchemy 2.0+ | Already integrated, supports SQLite & PostgreSQL |
| **PDF Export** | ReportLab 4.1+ | Comprehensive PDF generation |
| **CSV Export** | Built-in Python csv | No external dependency needed |

### Architectural Patterns

1. **Layered Architecture**
   ```
   Presentation Layer (Streamlit Pages/Components)
          ↓
   Query Layer (analytics_queries.py)
          ↓
   Data Layer (SQLAlchemy Models)
          ↓
   Database (SQLite/PostgreSQL)
   ```

2. **Component-Based UI**
   - Reusable chart components (`components/charts.py`)
   - Shared filter components (`components/filters.py`)
   - Consistent metric displays (`components/metrics.py`)

3. **Caching Strategy**
   - Use `@st.cache_data` for database queries
   - Cache TTL: 5 minutes for real-time data
   - Cache TTL: 30 minutes for historical analysis

---

## Database Schema Analysis

### Key Tables and Fields

#### 1. `traces` Table
```sql
CREATE TABLE traces (
    id VARCHAR(255) PRIMARY KEY,           -- Unique trace ID
    name VARCHAR(255),                     -- Trace name
    user_id VARCHAR(255),                  -- User identifier
    session_id VARCHAR(255),               -- Session identifier
    trace_metadata JSON,                   -- Additional metadata
    input JSON,                            -- Trace input
    output JSON,                           -- Trace output
    created_at DATETIME NOT NULL,          -- Creation timestamp
    updated_at DATETIME,                   -- Last update
    release VARCHAR(100),                  -- Release/version tag
    tags JSON                              -- Tags array
);

-- Indexes
CREATE INDEX idx_trace_created_at ON traces(created_at);
CREATE INDEX idx_trace_user_session ON traces(user_id, session_id);
```

**Dashboard Usage**:
- Session tracking
- User activity analysis
- Trace timeline visualization

#### 2. `generations` Table (PRIMARY DATA SOURCE)
```sql
CREATE TABLE generations (
    id VARCHAR(255) PRIMARY KEY,           -- Unique generation ID
    trace_id VARCHAR(255) NOT NULL,        -- Parent trace
    name VARCHAR(255),                     -- Generation name
    model VARCHAR(255),                    -- Model identifier (e.g., "openai/gpt-4o")
    model_parameters JSON,                 -- Model parameters
    input TEXT,                            -- Prompt
    output TEXT,                           -- Completion

    -- Token metrics
    input_tokens INTEGER,                  -- Input token count
    output_tokens INTEGER,                 -- Output token count
    total_tokens INTEGER,                  -- Total tokens

    -- Cost metrics (USD)
    input_cost FLOAT,                      -- Input cost
    output_cost FLOAT,                     -- Output cost
    total_cost FLOAT,                      -- Total cost

    -- Performance metrics
    latency_ms FLOAT,                      -- Latency in milliseconds

    -- Timestamps
    created_at DATETIME NOT NULL,          -- Creation time
    completion_start_time DATETIME,        -- Start time
    completion_end_time DATETIME,          -- End time

    -- Metadata
    generation_metadata JSON,              -- Additional metadata
    level VARCHAR(50),                     -- Level (DEFAULT, ERROR)
    status_message TEXT,                   -- Status/error message

    FOREIGN KEY (trace_id) REFERENCES traces(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_generation_created_at ON generations(created_at);
CREATE INDEX idx_generation_model ON generations(model);
CREATE INDEX idx_generation_trace_created ON generations(trace_id, created_at);
```

**Dashboard Usage**:
- Cost analysis (primary source)
- Token usage tracking
- Model comparison
- Latency analysis
- Error tracking

#### 3. `performance_metrics` Table (AGGREGATED DATA)
```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type VARCHAR(100) NOT NULL,     -- Metric type
    model VARCHAR(255),                    -- Model name
    dimension VARCHAR(100),                -- Dimension (e.g., "prompt_template")
    dimension_value VARCHAR(255),          -- Dimension value
    time_bucket DATETIME NOT NULL,         -- Time bucket

    -- Latency percentiles
    avg_latency_ms FLOAT,
    p50_latency_ms FLOAT,
    p95_latency_ms FLOAT,
    p99_latency_ms FLOAT,

    -- Usage metrics
    total_requests INTEGER,
    total_tokens INTEGER,
    total_cost FLOAT,
    avg_tokens_per_request FLOAT,
    avg_cost_per_request FLOAT,

    -- Error metrics
    error_count INTEGER,
    error_rate FLOAT,

    created_at DATETIME NOT NULL
);

-- Indexes
CREATE INDEX idx_perf_metric_model_time ON performance_metrics(metric_type, model, time_bucket);
CREATE INDEX idx_perf_metric_dimension ON performance_metrics(dimension, dimension_value);
```

**Dashboard Usage**:
- Performance trend analysis
- Pre-aggregated metrics for faster queries
- Percentile analysis

### Critical Query Patterns

```sql
-- Cost by model (last 7 days)
SELECT
    model,
    COUNT(*) as request_count,
    SUM(total_tokens) as total_tokens,
    SUM(total_cost) as total_cost,
    AVG(latency_ms) as avg_latency
FROM generations
WHERE created_at >= datetime('now', '-7 days')
GROUP BY model
ORDER BY total_cost DESC;

-- Daily cost trend
SELECT
    DATE(created_at) as date,
    SUM(total_cost) as daily_cost,
    COUNT(*) as request_count
FROM generations
WHERE created_at >= datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date;

-- Model performance comparison
SELECT
    model,
    AVG(latency_ms) as avg_latency,
    MIN(latency_ms) as min_latency,
    MAX(latency_ms) as max_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency
FROM generations
WHERE created_at >= datetime('now', '-24 hours')
GROUP BY model;

-- Agent analysis (via trace metadata)
SELECT
    json_extract(t.trace_metadata, '$.agent_name') as agent,
    COUNT(g.id) as generation_count,
    SUM(g.total_cost) as total_cost,
    AVG(g.latency_ms) as avg_latency
FROM traces t
JOIN generations g ON t.id = g.trace_id
WHERE t.created_at >= datetime('now', '-7 days')
GROUP BY agent
ORDER BY total_cost DESC;
```

---

## Component Specifications

### 1. Main Application (`app.py`)

**Purpose**: Entry point for the Streamlit dashboard, handles navigation and global state.

**Implementation**:

```python
"""Streamlit Analytics Dashboard - Main Entry Point

This is the main application file for the Coffee Maker Analytics Dashboard.
It provides a multi-page interface for analyzing LLM usage, costs, and performance.

Usage:
    streamlit run streamlit_apps/analytics_dashboard/app.py

    # With custom database
    SQLITE_PATH=/path/to/llm_metrics.db streamlit run streamlit_apps/analytics_dashboard/app.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.langchain_observe.analytics.config import ExportConfig
from streamlit_apps.analytics_dashboard.config import DashboardConfig
from streamlit_apps.analytics_dashboard.components.filters import render_global_filters

# Configure page
st.set_page_config(
    page_title="Coffee Maker Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Bobain/MonolithicCoffeeMakerAgent',
        'Report a bug': 'https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues',
        'About': """
        # Coffee Maker Analytics Dashboard

        Interactive dashboard for analyzing LLM usage, costs, and performance.

        **Version**: 1.0.0
        **Built with**: Streamlit, Plotly, Pandas
        """
    }
)

def init_session_state():
    """Initialize session state variables."""
    if 'db_config' not in st.session_state:
        try:
            st.session_state.db_config = ExportConfig.from_env()
        except ValueError as e:
            st.error(f"Configuration error: {e}")
            st.stop()

    if 'dashboard_config' not in st.session_state:
        st.session_state.dashboard_config = DashboardConfig()

    # Initialize filter state
    if 'date_range' not in st.session_state:
        st.session_state.date_range = 'last_7_days'

    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = []

    if 'selected_agents' not in st.session_state:
        st.session_state.selected_agents = []

def render_sidebar():
    """Render sidebar with navigation and global filters."""
    with st.sidebar:
        st.title("📊 Analytics Dashboard")
        st.markdown("---")

        # Database info
        st.subheader("Database")
        db_path = st.session_state.db_config.db_url
        if db_path.startswith("sqlite:///"):
            db_file = db_path.replace("sqlite:///", "")
            if Path(db_file).exists():
                st.success(f"✅ Connected: {Path(db_file).name}")
            else:
                st.error(f"❌ Not found: {Path(db_file).name}")
        else:
            st.info(f"Connected to: {st.session_state.db_config.db_type}")

        st.markdown("---")

        # Global filters
        st.subheader("Filters")
        render_global_filters()

        st.markdown("---")

        # Quick stats
        st.subheader("Quick Stats")
        with st.spinner("Loading..."):
            from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_quick_stats
            stats = get_quick_stats(st.session_state.db_config)

            st.metric("Total Requests", f"{stats['total_requests']:,}")
            st.metric("Total Cost", f"${stats['total_cost']:.2f}")
            st.metric("Avg Latency", f"{stats['avg_latency']:.0f}ms")

def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()

    # Main content
    st.title("Welcome to Coffee Maker Analytics")
    st.markdown("""
    This dashboard provides comprehensive analytics for your LLM usage:

    - **📊 Overview**: Global metrics and trends
    - **💰 Cost Analysis**: Detailed cost breakdown by model and agent
    - **📈 Model Comparison**: Performance comparison across models
    - **🤖 Agent Performance**: Agent-specific metrics and optimization
    - **📥 Exports**: Generate and download custom reports

    👈 **Select a page from the sidebar to get started**
    """)

    # Recent activity
    st.subheader("Recent Activity")
    with st.spinner("Loading recent activity..."):
        from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_recent_generations
        recent = get_recent_generations(st.session_state.db_config, limit=10)

        if recent:
            st.dataframe(
                recent,
                use_container_width=True,
                column_config={
                    "created_at": st.column_config.DatetimeColumn("Time", format="MM/DD/YYYY HH:mm:ss"),
                    "model": st.column_config.TextColumn("Model"),
                    "total_tokens": st.column_config.NumberColumn("Tokens", format="%d"),
                    "total_cost": st.column_config.NumberColumn("Cost", format="$%.4f"),
                    "latency_ms": st.column_config.NumberColumn("Latency", format="%.0f ms"),
                }
            )
        else:
            st.info("No recent activity. Ensure Langfuse exporter is running.")

if __name__ == "__main__":
    main()
```

**File Path**: `streamlit_apps/analytics_dashboard/app.py`
**Lines of Code**: ~150
**Dependencies**: `streamlit`, `coffee_maker.langchain_observe.analytics.config`

---

### 2. Configuration Module (`config.py`)

**Purpose**: Dashboard-specific configuration and settings.

**Implementation**:

```python
"""Dashboard configuration and settings.

This module provides configuration for the Streamlit dashboard,
including UI settings, chart defaults, and display options.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DashboardConfig:
    """Dashboard configuration settings.

    Attributes:
        cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        max_rows_display: Maximum rows to display in tables (default: 100)
        chart_height: Default chart height in pixels (default: 400)
        date_range_options: Available date range filters
        currency_symbol: Currency symbol for cost display (default: $)
        cost_precision: Decimal places for cost display (default: 4)
    """

    cache_ttl: int = 300  # 5 minutes
    max_rows_display: int = 100
    chart_height: int = 400
    currency_symbol: str = "$"
    cost_precision: int = 4

    date_range_options: Dict[str, str] = None
    model_colors: Dict[str, str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.date_range_options is None:
            self.date_range_options = {
                'last_1_hour': 'Last 1 Hour',
                'last_6_hours': 'Last 6 Hours',
                'last_24_hours': 'Last 24 Hours',
                'last_7_days': 'Last 7 Days',
                'last_30_days': 'Last 30 Days',
                'last_90_days': 'Last 90 Days',
                'custom': 'Custom Range'
            }

        if self.model_colors is None:
            # Consistent colors for common models
            self.model_colors = {
                'openai/gpt-4': '#10a37f',
                'openai/gpt-4o': '#10a37f',
                'openai/gpt-4-turbo': '#0c8a6a',
                'openai/gpt-3.5-turbo': '#48bfa5',
                'anthropic/claude-3-opus': '#cc785c',
                'anthropic/claude-3-sonnet': '#e89a7b',
                'anthropic/claude-3-haiku': '#f0b79d',
                'google/gemini-pro': '#4285f4',
                'google/gemini-ultra': '#185abc',
            }

    def get_date_range_label(self, key: str) -> str:
        """Get display label for date range key."""
        return self.date_range_options.get(key, key)

    def get_model_color(self, model: str) -> str:
        """Get color for model (or default)."""
        return self.model_colors.get(model, '#636efa')  # Plotly default blue
```

**File Path**: `streamlit_apps/analytics_dashboard/config.py`
**Lines of Code**: ~80
**Dependencies**: None (pure Python)

---

### 3. Analytics Query Layer (`queries/analytics_queries.py`)

**Purpose**: Core database queries with caching and error handling.

**Implementation** (excerpt, full file ~500 LOC):

```python
"""Core analytics queries for the dashboard.

This module provides cached database queries for retrieving
LLM usage metrics, costs, and performance data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from coffee_maker.langchain_observe.analytics.config import ExportConfig
from coffee_maker.langchain_observe.analytics.models import Generation, Trace

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_quick_stats(config: ExportConfig) -> Dict[str, float]:
    """Get quick summary statistics for sidebar.

    Args:
        config: Database configuration

    Returns:
        Dictionary with total_requests, total_cost, avg_latency
    """
    engine = create_engine(config.db_url)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        query = text("""
            SELECT
                COUNT(*) as total_requests,
                COALESCE(SUM(total_cost), 0) as total_cost,
                COALESCE(AVG(latency_ms), 0) as avg_latency
            FROM generations
            WHERE created_at >= datetime('now', '-7 days')
        """)

        result = session.execute(query).fetchone()

        return {
            'total_requests': result[0] if result else 0,
            'total_cost': result[1] if result else 0.0,
            'avg_latency': result[2] if result else 0.0
        }


@st.cache_data(ttl=300)
def get_recent_generations(config: ExportConfig, limit: int = 10) -> pd.DataFrame:
    """Get recent generation records.

    Args:
        config: Database configuration
        limit: Maximum number of records

    Returns:
        DataFrame with recent generations
    """
    engine = create_engine(config.db_url)

    query = f"""
        SELECT
            created_at,
            model,
            total_tokens,
            total_cost,
            latency_ms,
            level
        FROM generations
        ORDER BY created_at DESC
        LIMIT {limit}
    """

    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def get_cost_by_model(
    config: ExportConfig,
    start_date: datetime,
    end_date: datetime,
    models: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get cost breakdown by model.

    Args:
        config: Database configuration
        start_date: Start of date range
        end_date: End of date range
        models: Optional list of models to filter

    Returns:
        DataFrame with columns: model, request_count, total_tokens, total_cost, avg_latency
    """
    engine = create_engine(config.db_url)

    model_filter = ""
    if models:
        model_list = "', '".join(models)
        model_filter = f"AND model IN ('{model_list}')"

    query = f"""
        SELECT
            model,
            COUNT(*) as request_count,
            SUM(total_tokens) as total_tokens,
            SUM(total_cost) as total_cost,
            AVG(latency_ms) as avg_latency,
            SUM(input_tokens) as total_input_tokens,
            SUM(output_tokens) as total_output_tokens
        FROM generations
        WHERE created_at BETWEEN :start_date AND :end_date
        {model_filter}
        GROUP BY model
        ORDER BY total_cost DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={'start_date': start_date, 'end_date': end_date}
    )


@st.cache_data(ttl=300)
def get_daily_cost_trend(
    config: ExportConfig,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """Get daily cost trend data.

    Args:
        config: Database configuration
        start_date: Start of date range
        end_date: End of date range

    Returns:
        DataFrame with columns: date, daily_cost, request_count, total_tokens
    """
    engine = create_engine(config.db_url)

    query = """
        SELECT
            DATE(created_at) as date,
            SUM(total_cost) as daily_cost,
            COUNT(*) as request_count,
            SUM(total_tokens) as total_tokens
        FROM generations
        WHERE created_at BETWEEN :start_date AND :end_date
        GROUP BY DATE(created_at)
        ORDER BY date
    """

    return pd.read_sql(
        query,
        engine,
        params={'start_date': start_date, 'end_date': end_date}
    )


@st.cache_data(ttl=300)
def get_model_performance_comparison(
    config: ExportConfig,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """Get performance metrics by model.

    Args:
        config: Database configuration
        start_date: Start of date range
        end_date: End of date range

    Returns:
        DataFrame with latency percentiles and performance metrics
    """
    engine = create_engine(config.db_url)

    # Note: SQLite doesn't have native PERCENTILE_CONT, so we approximate
    # For production with PostgreSQL, use proper percentile functions
    query = """
        SELECT
            model,
            COUNT(*) as request_count,
            AVG(latency_ms) as avg_latency,
            MIN(latency_ms) as min_latency,
            MAX(latency_ms) as max_latency,
            AVG(total_tokens) as avg_tokens,
            AVG(total_cost) as avg_cost
        FROM generations
        WHERE created_at BETWEEN :start_date AND :end_date
        AND latency_ms IS NOT NULL
        GROUP BY model
        ORDER BY request_count DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={'start_date': start_date, 'end_date': end_date}
    )


@st.cache_data(ttl=300)
def get_agent_analysis(
    config: ExportConfig,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """Get metrics grouped by agent (from trace metadata).

    Args:
        config: Database configuration
        start_date: Start of date range
        end_date: End of date range

    Returns:
        DataFrame with agent metrics
    """
    engine = create_engine(config.db_url)

    # Extract agent name from trace metadata
    query = """
        SELECT
            json_extract(t.trace_metadata, '$.agent_name') as agent,
            COUNT(g.id) as generation_count,
            SUM(g.total_cost) as total_cost,
            AVG(g.latency_ms) as avg_latency,
            SUM(g.total_tokens) as total_tokens
        FROM traces t
        JOIN generations g ON t.id = g.trace_id
        WHERE t.created_at BETWEEN :start_date AND :end_date
        GROUP BY agent
        HAVING agent IS NOT NULL
        ORDER BY total_cost DESC
    """

    return pd.read_sql(
        query,
        engine,
        params={'start_date': start_date, 'end_date': end_date}
    )


def parse_date_range(range_key: str) -> Tuple[datetime, datetime]:
    """Convert date range key to datetime tuple.

    Args:
        range_key: Date range key (e.g., 'last_7_days')

    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.utcnow()

    range_map = {
        'last_1_hour': timedelta(hours=1),
        'last_6_hours': timedelta(hours=6),
        'last_24_hours': timedelta(hours=24),
        'last_7_days': timedelta(days=7),
        'last_30_days': timedelta(days=30),
        'last_90_days': timedelta(days=90),
    }

    delta = range_map.get(range_key, timedelta(days=7))
    start_date = end_date - delta

    return start_date, end_date
```

**File Path**: `streamlit_apps/analytics_dashboard/queries/analytics_queries.py`
**Lines of Code**: ~500 (full implementation)
**Dependencies**: `streamlit`, `pandas`, `sqlalchemy`, `coffee_maker.langchain_observe.analytics`

**Additional Query Files**:
- `cost_queries.py`: Cost-specific queries (budget tracking, forecasting)
- `performance_queries.py`: Performance metric queries (latency percentiles)
- `export_queries.py`: Data export queries (CSV/PDF generation)

---

### 4. Chart Components (`components/charts.py`)

**Purpose**: Reusable Plotly chart components.

**Implementation** (excerpt, full file ~600 LOC):

```python
"""Reusable chart components using Plotly.

This module provides pre-configured chart components for
common visualization patterns in the dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List


def create_cost_breakdown_pie(
    data: pd.DataFrame,
    values_col: str = 'total_cost',
    names_col: str = 'model',
    title: str = 'Cost Breakdown by Model',
    height: int = 400
) -> go.Figure:
    """Create pie chart for cost breakdown.

    Args:
        data: DataFrame with cost data
        values_col: Column name for values
        names_col: Column name for labels
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    fig = px.pie(
        data,
        values=values_col,
        names=names_col,
        title=title,
        height=height,
        hole=0.4  # Donut chart
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cost: $%{value:.4f}<br>Percentage: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )

    return fig


def create_cost_trend_line(
    data: pd.DataFrame,
    x_col: str = 'date',
    y_col: str = 'daily_cost',
    title: str = 'Daily Cost Trend',
    height: int = 400,
    show_markers: bool = True
) -> go.Figure:
    """Create line chart for cost trends over time.

    Args:
        data: DataFrame with time-series data
        x_col: Column name for x-axis (date)
        y_col: Column name for y-axis (cost)
        title: Chart title
        height: Chart height in pixels
        show_markers: Whether to show markers on the line

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='lines+markers' if show_markers else 'lines',
        name='Daily Cost',
        line=dict(color='#10a37f', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>Cost: $%{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Cost (USD)',
        height=height,
        hovermode='x unified',
        showlegend=False
    )

    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig


def create_model_comparison_bar(
    data: pd.DataFrame,
    x_col: str = 'model',
    y_col: str = 'avg_latency',
    color_col: Optional[str] = None,
    title: str = 'Model Performance Comparison',
    y_label: str = 'Average Latency (ms)',
    height: int = 400
) -> go.Figure:
    """Create bar chart for model comparison.

    Args:
        data: DataFrame with model metrics
        x_col: Column name for x-axis (model)
        y_col: Column name for y-axis (metric)
        color_col: Optional column for color grouping
        title: Chart title
        y_label: Y-axis label
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    if color_col:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            height=height,
            barmode='group'
        )
    else:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            height=height
        )

    fig.update_layout(
        xaxis_title='Model',
        yaxis_title=y_label,
        xaxis_tickangle=-45,
        hovermode='x unified'
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' + y_label + ': %{y:.2f}<extra></extra>'
    )

    return fig


def create_token_usage_stacked_bar(
    data: pd.DataFrame,
    x_col: str = 'date',
    input_col: str = 'total_input_tokens',
    output_col: str = 'total_output_tokens',
    title: str = 'Token Usage Over Time',
    height: int = 400
) -> go.Figure:
    """Create stacked bar chart for token usage.

    Args:
        data: DataFrame with token usage data
        x_col: Column name for x-axis (date)
        input_col: Column name for input tokens
        output_col: Column name for output tokens
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[input_col],
        name='Input Tokens',
        marker_color='#48bfa5',
        hovertemplate='<b>%{x}</b><br>Input: %{y:,} tokens<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[output_col],
        name='Output Tokens',
        marker_color='#10a37f',
        hovertemplate='<b>%{x}</b><br>Output: %{y:,} tokens<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Tokens',
        height=height,
        barmode='stack',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def create_latency_distribution_box(
    data: pd.DataFrame,
    group_col: str = 'model',
    value_col: str = 'latency_ms',
    title: str = 'Latency Distribution by Model',
    height: int = 400
) -> go.Figure:
    """Create box plot for latency distribution.

    Args:
        data: DataFrame with latency data
        group_col: Column name for grouping (e.g., model)
        value_col: Column name for values (latency)
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    fig = px.box(
        data,
        x=group_col,
        y=value_col,
        title=title,
        height=height,
        points='outliers'  # Show only outlier points
    )

    fig.update_layout(
        xaxis_title='Model',
        yaxis_title='Latency (ms)',
        xaxis_tickangle=-45,
        hovermode='closest'
    )

    return fig


def create_heatmap_hourly_usage(
    data: pd.DataFrame,
    title: str = 'Hourly Usage Heatmap',
    height: int = 400
) -> go.Figure:
    """Create heatmap for hourly usage patterns.

    Args:
        data: DataFrame with hour and day columns
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    # Pivot data to create matrix
    pivot = data.pivot(index='day_of_week', columns='hour', values='request_count')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=days,
        colorscale='Viridis',
        hovertemplate='<b>%{y}</b> at %{x}:00<br>Requests: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        height=height
    )

    return fig
```

**File Path**: `streamlit_apps/analytics_dashboard/components/charts.py`
**Lines of Code**: ~600 (full implementation)
**Dependencies**: `plotly`, `pandas`

---

### 5. Page: Overview (`pages/01_overview.py`)

**Purpose**: Global metrics overview with key performance indicators.

**Implementation**:

```python
"""Overview page showing global metrics and trends.

This page provides a high-level summary of LLM usage, costs,
and performance across all models and agents.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_cost_by_model,
    get_daily_cost_trend,
    get_quick_stats,
    parse_date_range
)
from streamlit_apps.analytics_dashboard.components.charts import (
    create_cost_breakdown_pie,
    create_cost_trend_line,
    create_token_usage_stacked_bar
)
from streamlit_apps.analytics_dashboard.components.metrics import render_metric_cards

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("📊 Overview")
st.markdown("Global metrics and trends across all LLM usage")

# Get config from session state
config = st.session_state.db_config
dashboard_config = st.session_state.dashboard_config

# Parse date range from filters
start_date, end_date = parse_date_range(st.session_state.date_range)

# Metric cards
st.subheader("Key Metrics")

with st.spinner("Loading metrics..."):
    stats = get_quick_stats(config)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Requests",
            value=f"{stats['total_requests']:,}",
            delta=None  # TODO: Add delta from previous period
        )

    with col2:
        st.metric(
            label="Total Cost",
            value=f"${stats['total_cost']:.2f}",
            delta=None
        )

    with col3:
        st.metric(
            label="Avg Latency",
            value=f"{stats['avg_latency']:.0f}ms",
            delta=None
        )

    with col4:
        avg_cost_per_request = stats['total_cost'] / stats['total_requests'] if stats['total_requests'] > 0 else 0
        st.metric(
            label="Avg Cost/Request",
            value=f"${avg_cost_per_request:.4f}",
            delta=None
        )

st.markdown("---")

# Charts row 1: Cost breakdown and trend
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cost Breakdown by Model")
    with st.spinner("Loading chart..."):
        cost_data = get_cost_by_model(config, start_date, end_date)
        if not cost_data.empty:
            fig = create_cost_breakdown_pie(cost_data)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected period")

with col2:
    st.subheader("Daily Cost Trend")
    with st.spinner("Loading chart..."):
        trend_data = get_daily_cost_trend(config, start_date, end_date)
        if not trend_data.empty:
            fig = create_cost_trend_line(trend_data)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected period")

st.markdown("---")

# Token usage
st.subheader("Token Usage Over Time")
with st.spinner("Loading chart..."):
    # Query data with input/output token breakdown
    from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_daily_token_usage
    token_data = get_daily_token_usage(config, start_date, end_date)

    if not token_data.empty:
        fig = create_token_usage_stacked_bar(token_data)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected period")

st.markdown("---")

# Model summary table
st.subheader("Model Summary")
with st.spinner("Loading data..."):
    cost_data = get_cost_by_model(config, start_date, end_date)

    if not cost_data.empty:
        # Format the dataframe for display
        display_df = cost_data.copy()
        display_df['total_cost'] = display_df['total_cost'].apply(lambda x: f"${x:.4f}")
        display_df['avg_latency'] = display_df['avg_latency'].apply(lambda x: f"{x:.0f}ms")
        display_df['request_count'] = display_df['request_count'].apply(lambda x: f"{x:,}")
        display_df['total_tokens'] = display_df['total_tokens'].apply(lambda x: f"{x:,}")

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "model": "Model",
                "request_count": "Requests",
                "total_tokens": "Total Tokens",
                "total_cost": "Total Cost",
                "avg_latency": "Avg Latency"
            },
            hide_index=True
        )
    else:
        st.info("No data available for the selected period")
```

**File Path**: `streamlit_apps/analytics_dashboard/pages/01_overview.py`
**Lines of Code**: ~180
**Dependencies**: `streamlit`, query layer, chart components

---

### 6. Filter Components (`components/filters.py`)

**Purpose**: Reusable filter widgets for date ranges, models, agents.

**Implementation**:

```python
"""Reusable filter components for the dashboard.

This module provides filter widgets that update session state
and are used across multiple pages.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional

from coffee_maker.langchain_observe.analytics.config import ExportConfig
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_available_models,
    get_available_agents
)


def render_global_filters():
    """Render global filters in sidebar.

    Updates session state with selected filters:
    - date_range: Date range key
    - custom_start_date: Start date (if custom range)
    - custom_end_date: End date (if custom range)
    - selected_models: List of selected models
    - selected_agents: List of selected agents
    """
    config = st.session_state.db_config
    dashboard_config = st.session_state.dashboard_config

    # Date range filter
    date_range = st.selectbox(
        "Time Range",
        options=list(dashboard_config.date_range_options.keys()),
        format_func=lambda x: dashboard_config.get_date_range_label(x),
        key='date_range_select',
        index=3  # Default to 'last_7_days'
    )

    st.session_state.date_range = date_range

    # Custom date range (if selected)
    if date_range == 'custom':
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=7),
                key='custom_start_date'
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                key='custom_end_date'
            )

        st.session_state.custom_start_date = datetime.combine(start_date, datetime.min.time())
        st.session_state.custom_end_date = datetime.combine(end_date, datetime.max.time())

    # Model filter
    with st.spinner("Loading models..."):
        available_models = get_available_models(config)

    if available_models:
        selected_models = st.multiselect(
            "Filter by Model",
            options=available_models,
            default=[],
            key='model_filter'
        )
        st.session_state.selected_models = selected_models

    # Agent filter
    with st.spinner("Loading agents..."):
        available_agents = get_available_agents(config)

    if available_agents:
        selected_agents = st.multiselect(
            "Filter by Agent",
            options=available_agents,
            default=[],
            key='agent_filter'
        )
        st.session_state.selected_agents = selected_agents

    # Reset filters button
    if st.button("Reset Filters", use_container_width=True):
        st.session_state.date_range = 'last_7_days'
        st.session_state.selected_models = []
        st.session_state.selected_agents = []
        st.rerun()


def get_active_filters() -> dict:
    """Get currently active filters from session state.

    Returns:
        Dictionary with active filter values
    """
    return {
        'date_range': st.session_state.get('date_range', 'last_7_days'),
        'selected_models': st.session_state.get('selected_models', []),
        'selected_agents': st.session_state.get('selected_agents', [])
    }
```

**File Path**: `streamlit_apps/analytics_dashboard/components/filters.py`
**Lines of Code**: ~130
**Dependencies**: `streamlit`, query layer

---

## Data Flow Diagrams

### 1. Overall System Data Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      LLM Applications                           │
│  (coffee_maker agents, code_developer, project-manager, etc.)  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         │ LangChain/Langfuse instrumentation
                         │
                         ▼
        ┌────────────────────────────────────┐
        │     Langfuse Cloud Service         │
        │  (Trace storage and aggregation)   │
        └────────────────┬───────────────────┘
                         │
                         │ API (fetch traces)
                         │
                         ▼
        ┌────────────────────────────────────┐
        │      LangfuseExporter              │
        │  (PRIORITY 1 - exporter.py)        │
        │  - Fetches traces via API          │
        │  - Transforms to local schema      │
        │  - Writes to SQLite/PostgreSQL     │
        └────────────────┬───────────────────┘
                         │
                         │ SQL writes
                         │
                         ▼
        ┌────────────────────────────────────┐
        │    Local Analytics Database        │
        │      (llm_metrics.db)              │
        │  Tables:                           │
        │  - traces                          │
        │  - generations ★ (primary data)    │
        │  - spans                           │
        │  - performance_metrics             │
        └────────────────┬───────────────────┘
                         │
                         │ SQL queries
                         │
                         ▼
        ┌────────────────────────────────────┐
        │   Analytics Query Layer            │
        │  (queries/analytics_queries.py)    │
        │  - Cached queries (@st.cache_data) │
        │  - Data transformations            │
        │  - Pandas DataFrames               │
        └────────────────┬───────────────────┘
                         │
                         │ DataFrames
                         │
                         ▼
        ┌────────────────────────────────────┐
        │    Streamlit Dashboard Pages       │
        │  - 01_overview.py                  │
        │  - 02_cost_analysis.py             │
        │  - 03_model_comparison.py          │
        │  - 04_agent_performance.py         │
        │  - 05_exports.py                   │
        └────────────────┬───────────────────┘
                         │
                         │ Plotly charts, metrics
                         │
                         ▼
        ┌────────────────────────────────────┐
        │         User Browser               │
        │  (Interactive web interface)       │
        └────────────────────────────────────┘
```

### 2. Dashboard Page Load Sequence

```
User navigates to Overview page
        │
        ▼
01_overview.py loads
        │
        ├─> render_global_filters() [sidebar]
        │   │
        │   ├─> get_available_models(config) [cached]
        │   │   └─> SQL: SELECT DISTINCT model FROM generations
        │   │
        │   └─> get_available_agents(config) [cached]
        │       └─> SQL: SELECT DISTINCT agent FROM traces
        │
        ├─> parse_date_range(st.session_state.date_range)
        │   └─> Returns (start_date, end_date)
        │
        ├─> get_quick_stats(config) [cached 5min]
        │   └─> SQL: SELECT COUNT(*), SUM(cost), AVG(latency) FROM generations
        │   └─> Render metric cards
        │
        ├─> get_cost_by_model(config, start_date, end_date) [cached 5min]
        │   └─> SQL: SELECT model, SUM(cost), COUNT(*) GROUP BY model
        │   └─> create_cost_breakdown_pie(data)
        │       └─> Plotly pie chart
        │
        ├─> get_daily_cost_trend(config, start_date, end_date) [cached 5min]
        │   └─> SQL: SELECT DATE(created_at), SUM(cost) GROUP BY date
        │   └─> create_cost_trend_line(data)
        │       └─> Plotly line chart
        │
        └─> get_daily_token_usage(config, start_date, end_date) [cached 5min]
            └─> SQL: SELECT date, SUM(input_tokens), SUM(output_tokens)
            └─> create_token_usage_stacked_bar(data)
                └─> Plotly stacked bar chart

Dashboard rendered in browser ✓
```

### 3. Caching Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                  Streamlit Caching Layers                     │
└──────────────────────────────────────────────────────────────┘

Layer 1: Query Results (@st.cache_data, TTL=300s)
┌──────────────────────────────────────────────────────────────┐
│  Cached Function          │  Cache Key                        │
├───────────────────────────┼───────────────────────────────────┤
│ get_quick_stats()         │ config.db_url                     │
│ get_cost_by_model()       │ config.db_url + start + end + ... │
│ get_daily_cost_trend()    │ config.db_url + start + end       │
│ get_available_models()    │ config.db_url                     │
└──────────────────────────────────────────────────────────────┘
Cache Invalidation: Automatic after 300 seconds (5 minutes)
Manual Clear: "Clear Cache" button in sidebar

Layer 2: Database Connection Pool
┌──────────────────────────────────────────────────────────────┐
│  SQLAlchemy Engine Pool                                       │
│  - Pool size: 5 connections                                   │
│  - Pool recycle: 3600s (1 hour)                               │
│  - Connection reuse for multiple queries                      │
└──────────────────────────────────────────────────────────────┘

Layer 3: Browser-Side Caching
┌──────────────────────────────────────────────────────────────┐
│  Streamlit Component State                                    │
│  - Widget state persisted in session_state                    │
│  - Filter selections cached client-side                       │
│  - Chart interactions (zoom, pan) maintained                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Foundation (Days 1-2) - 12-16 hours

#### Task 1.1: Project Setup (2 hours)

**Objective**: Create directory structure and configuration files.

**Steps**:
1. Create `streamlit_apps/analytics_dashboard/` directory structure
2. Add `__init__.py` files to all packages
3. Create `config.py` with `DashboardConfig` class
4. Create `README.md` with setup instructions
5. Update `pyproject.toml` with Streamlit dependencies

**Deliverables**:
- [ ] Directory structure matches spec
- [ ] All `__init__.py` files created
- [ ] `config.py` implemented (~80 LOC)
- [ ] `README.md` with quick start guide

**Time Estimate**: 2 hours
**Dependencies**: None
**Assignee**: code-developer daemon

---

#### Task 1.2: Database Query Layer (6-8 hours)

**Objective**: Implement core analytics queries with caching.

**Steps**:
1. Create `queries/analytics_queries.py` (~500 LOC)
   - `get_quick_stats()`
   - `get_recent_generations()`
   - `get_cost_by_model()`
   - `get_daily_cost_trend()`
   - `get_model_performance_comparison()`
   - `get_agent_analysis()`
   - `parse_date_range()`
   - `get_available_models()`
   - `get_available_agents()`

2. Create `queries/cost_queries.py` (~300 LOC)
   - `get_cost_by_day_and_model()`
   - `get_hourly_cost_breakdown()`
   - `get_budget_tracking()`
   - `get_cost_forecast()`

3. Create `queries/performance_queries.py` (~200 LOC)
   - `get_latency_percentiles()`
   - `get_hourly_usage_heatmap()`
   - `get_error_rate_by_model()`

4. Create `queries/export_queries.py` (~150 LOC)
   - `get_detailed_export_data()`
   - `get_summary_export_data()`

5. Write unit tests for all query functions

**Deliverables**:
- [ ] `analytics_queries.py` complete (~500 LOC)
- [ ] `cost_queries.py` complete (~300 LOC)
- [ ] `performance_queries.py` complete (~200 LOC)
- [ ] `export_queries.py` complete (~150 LOC)
- [ ] Unit tests for all queries (90%+ coverage)
- [ ] Query performance < 500ms for typical datasets

**Time Estimate**: 6-8 hours
**Dependencies**: Task 1.1
**Assignee**: code-developer daemon

**Testing Checklist**:
- [ ] Queries work with empty database
- [ ] Queries handle date range edge cases
- [ ] Caching works correctly (@st.cache_data)
- [ ] Queries return expected DataFrame schema
- [ ] SQL injection protection (parameterized queries)

---

#### Task 1.3: Chart Components (4-6 hours)

**Objective**: Create reusable Plotly chart components.

**Steps**:
1. Create `components/charts.py` (~600 LOC)
   - `create_cost_breakdown_pie()`
   - `create_cost_trend_line()`
   - `create_model_comparison_bar()`
   - `create_token_usage_stacked_bar()`
   - `create_latency_distribution_box()`
   - `create_heatmap_hourly_usage()`
   - Additional chart helpers

2. Create `components/metrics.py` (~150 LOC)
   - `render_metric_cards()`
   - `render_delta_metric()`
   - `render_progress_bar()`

3. Create `components/filters.py` (~150 LOC)
   - `render_global_filters()`
   - `get_active_filters()`

4. Create `components/tables.py` (~150 LOC)
   - `render_sortable_table()`
   - `render_paginated_table()`

**Deliverables**:
- [ ] `charts.py` complete (~600 LOC)
- [ ] `metrics.py` complete (~150 LOC)
- [ ] `filters.py` complete (~150 LOC)
- [ ] `tables.py` complete (~150 LOC)
- [ ] Visual tests for all chart types
- [ ] Charts responsive to window resizing

**Time Estimate**: 4-6 hours
**Dependencies**: Task 1.2
**Assignee**: code-developer daemon

**Testing Checklist**:
- [ ] Charts render with sample data
- [ ] Hover tooltips work correctly
- [ ] Charts handle empty data gracefully
- [ ] Color scheme consistent across charts
- [ ] Charts export to PNG (Plotly feature)

---

### Phase 2: Core Pages (Days 3-5) - 18-24 hours

#### Task 2.1: Main App & Overview Page (4-6 hours)

**Objective**: Implement main entry point and overview page.

**Steps**:
1. Create `app.py` (~150 LOC)
   - Streamlit page config
   - Session state initialization
   - Sidebar rendering
   - Home page content

2. Create `pages/01_overview.py` (~180 LOC)
   - Global metrics (4 metric cards)
   - Cost breakdown pie chart
   - Daily cost trend line chart
   - Token usage stacked bar chart
   - Model summary table

3. Test complete navigation flow

**Deliverables**:
- [ ] `app.py` complete (~150 LOC)
- [ ] `pages/01_overview.py` complete (~180 LOC)
- [ ] Dashboard accessible via `streamlit run app.py`
- [ ] Sidebar navigation works
- [ ] All overview charts render correctly

**Time Estimate**: 4-6 hours
**Dependencies**: Tasks 1.2, 1.3
**Assignee**: code-developer daemon

**Testing Checklist**:
- [ ] Page loads without errors
- [ ] Filters update charts correctly
- [ ] Cache works (check load time after refresh)
- [ ] Responsive layout on different screen sizes

---

#### Task 2.2: Cost Analysis Page (5-7 hours)

**Objective**: Implement detailed cost analysis page.

**Steps**:
1. Create `pages/02_cost_analysis.py` (~250 LOC)
   - Cost by model over time (line chart with multiple traces)
   - Hourly cost breakdown (heatmap)
   - Top 10 most expensive requests (table)
   - Cost per token analysis (scatter plot)
   - Budget tracking widget
   - Cost forecast (linear regression)

2. Add budget configuration UI
3. Implement cost alerts

**Deliverables**:
- [ ] `pages/02_cost_analysis.py` complete (~250 LOC)
- [ ] All cost charts render correctly
- [ ] Budget tracking functional
- [ ] Cost forecast accurate (MAE < 10%)

**Time Estimate**: 5-7 hours
**Dependencies**: Task 2.1
**Assignee**: code-developer daemon

**Features**:
- Interactive cost breakdown by date + model
- Cost per token comparison across models
- Identify most expensive individual requests
- Budget vs actual spending visualization
- Predictive cost forecast (next 7 days)

---

#### Task 2.3: Model Comparison Page (4-5 hours)

**Objective**: Implement model performance comparison page.

**Steps**:
1. Create `pages/03_model_comparison.py` (~200 LOC)
   - Latency comparison (box plot)
   - Throughput comparison (bar chart)
   - Cost efficiency scatter plot (cost vs latency)
   - Token efficiency analysis
   - Model selection recommendation engine

2. Implement model scoring algorithm

**Deliverables**:
- [ ] `pages/03_model_comparison.py` complete (~200 LOC)
- [ ] All comparison charts functional
- [ ] Recommendation engine working

**Time Estimate**: 4-5 hours
**Dependencies**: Task 2.2
**Assignee**: code-developer daemon

**Features**:
- Side-by-side latency comparison
- Cost per 1K tokens normalized
- Quality vs speed trade-off visualization
- Model recommendation based on use case

---

#### Task 2.4: Agent Performance Page (4-5 hours)

**Objective**: Implement agent-specific analytics page.

**Steps**:
1. Create `pages/04_agent_performance.py` (~200 LOC)
   - Agent cost breakdown (pie chart)
   - Agent request volume over time (area chart)
   - Agent latency comparison (bar chart)
   - Most expensive agents table
   - Agent efficiency score

2. Extract agent metadata from traces
3. Handle cases where agent metadata is missing

**Deliverables**:
- [ ] `pages/04_agent_performance.py` complete (~200 LOC)
- [ ] Agent extraction from trace metadata works
- [ ] All agent charts functional
- [ ] Graceful handling of missing agent data

**Time Estimate**: 4-5 hours
**Dependencies**: Task 2.3
**Assignee**: code-developer daemon

**Features**:
- Cost attribution by agent
- Agent utilization patterns
- Performance bottleneck identification
- Agent optimization recommendations

---

#### Task 2.5: Exports Page (5-6 hours)

**Objective**: Implement report generation and data export functionality.

**Steps**:
1. Create `pages/05_exports.py` (~150 LOC)
   - CSV export (raw data)
   - PDF report generation (summary + charts)
   - Custom date range selection
   - Export preview
   - Download buttons

2. Create `utils/export_utils.py` (~300 LOC)
   - `generate_csv_export()`
   - `generate_pdf_report()`
   - `create_pdf_charts()` (embed Plotly as images)

3. Implement PDF report template with ReportLab

**Deliverables**:
- [ ] `pages/05_exports.py` complete (~150 LOC)
- [ ] `utils/export_utils.py` complete (~300 LOC)
- [ ] CSV export works for all data
- [ ] PDF reports generate with charts
- [ ] Download buttons functional

**Time Estimate**: 5-6 hours
**Dependencies**: Task 2.4
**Assignee**: code-developer daemon

**Features**:
- Export raw data to CSV
- Generate executive summary PDF
- Include charts in PDF report
- Custom report date ranges
- Scheduled report generation (future)

---

### Phase 3: Polish & Testing (Days 6-7) - 12-16 hours

#### Task 3.1: Utilities & Error Handling (3-4 hours)

**Objective**: Implement utility functions and robust error handling.

**Steps**:
1. Create `utils/data_processing.py` (~200 LOC)
   - Data validation functions
   - DataFrame transformation helpers
   - Aggregation utilities

2. Create `utils/format_utils.py` (~100 LOC)
   - Currency formatting
   - Number formatting
   - Date/time formatting

3. Create `utils/cache_utils.py` (~100 LOC)
   - Cache management functions
   - Cache warming
   - Cache invalidation

4. Add comprehensive error handling to all pages
5. Add loading spinners and progress indicators

**Deliverables**:
- [ ] All utility modules complete (~400 LOC total)
- [ ] Error handling on all pages
- [ ] User-friendly error messages
- [ ] Loading states for all async operations

**Time Estimate**: 3-4 hours
**Dependencies**: Phase 2 complete
**Assignee**: code-developer daemon

---

#### Task 3.2: Testing Suite (5-7 hours)

**Objective**: Comprehensive testing of all components.

**Steps**:
1. Create `tests/test_queries.py` (~400 LOC)
   - Unit tests for all query functions
   - Test with empty database
   - Test with sample data
   - Test caching behavior

2. Create `tests/test_components.py` (~300 LOC)
   - Unit tests for chart components
   - Test with various data shapes
   - Test edge cases (empty data, single data point)

3. Create `tests/test_exports.py` (~200 LOC)
   - Test CSV export
   - Test PDF generation
   - Test file downloads

4. Create `tests/test_integration.py` (~200 LOC)
   - End-to-end page load tests
   - Filter interaction tests
   - Navigation tests

5. Run full test suite and achieve 85%+ coverage

**Deliverables**:
- [ ] All test files complete (~1100 LOC total)
- [ ] Test coverage ≥ 85%
- [ ] All tests passing
- [ ] CI/CD integration (GitHub Actions)

**Time Estimate**: 5-7 hours
**Dependencies**: Task 3.1
**Assignee**: code-developer daemon

**Testing Checklist**:
- [ ] Unit tests for all query functions
- [ ] Unit tests for all chart components
- [ ] Integration tests for each page
- [ ] Export functionality tests
- [ ] Error handling tests
- [ ] Performance tests (page load < 3s)

---

#### Task 3.3: Documentation & Polish (4-5 hours)

**Objective**: Create comprehensive documentation and polish UI.

**Steps**:
1. Create `README.md` in dashboard directory (~300 lines)
   - Installation instructions
   - Configuration guide
   - Usage examples
   - Troubleshooting
   - Architecture overview

2. Add inline documentation to all pages
   - Help tooltips (ℹ️ icons)
   - Explanation text for metrics
   - Chart interpretation guides

3. Create `DEVELOPMENT.md` (~200 lines)
   - Developer setup guide
   - Code organization
   - Adding new pages/charts
   - Testing procedures

4. UI/UX polish:
   - Consistent styling across all pages
   - Responsive layout adjustments
   - Accessibility improvements (ARIA labels)
   - Dark mode support (Streamlit theme)

5. Performance optimization:
   - Query optimization
   - Cache tuning
   - Lazy loading for heavy components

**Deliverables**:
- [ ] `README.md` complete and comprehensive
- [ ] `DEVELOPMENT.md` complete
- [ ] Help tooltips on all pages
- [ ] UI polished and consistent
- [ ] Performance benchmarks met (< 3s page load)
- [ ] Accessibility score ≥ 90 (Lighthouse)

**Time Estimate**: 4-5 hours
**Dependencies**: Task 3.2
**Assignee**: code-developer daemon

---

### Phase 4: Deployment & Validation (Days 8-10) - 8-12 hours

#### Task 4.1: Deployment Setup (3-4 hours)

**Objective**: Prepare dashboard for production deployment.

**Steps**:
1. Create `Dockerfile` for containerized deployment
2. Create `docker-compose.yml` for local testing
3. Create deployment scripts for common platforms:
   - Streamlit Cloud
   - Heroku
   - AWS ECS
   - Google Cloud Run

4. Environment configuration:
   - `.env.template` file
   - Environment variable documentation
   - Secrets management guide

5. Create deployment checklist

**Deliverables**:
- [ ] `Dockerfile` complete
- [ ] `docker-compose.yml` complete
- [ ] Deployment scripts for 4 platforms
- [ ] Environment configuration documented
- [ ] Deployment checklist created

**Time Estimate**: 3-4 hours
**Dependencies**: Phase 3 complete
**Assignee**: code-developer daemon

---

#### Task 4.2: Performance Testing (2-3 hours)

**Objective**: Validate performance under load.

**Steps**:
1. Create performance test suite
2. Test with varying database sizes:
   - 1K generations
   - 10K generations
   - 100K generations
   - 1M generations

3. Measure key metrics:
   - Page load time
   - Query execution time
   - Cache hit rate
   - Memory usage

4. Optimize bottlenecks
5. Document performance characteristics

**Deliverables**:
- [ ] Performance test suite complete
- [ ] Performance benchmarks documented
- [ ] Bottlenecks identified and optimized
- [ ] Performance targets met:
   - Page load < 3s (100K rows)
   - Query time < 500ms (100K rows)
   - Cache hit rate > 80%
   - Memory usage < 500MB

**Time Estimate**: 2-3 hours
**Dependencies**: Task 4.1
**Assignee**: code-developer daemon

---

#### Task 4.3: User Acceptance Testing (3-5 hours)

**Objective**: Validate dashboard with real users and data.

**Steps**:
1. Deploy dashboard to staging environment
2. Load production data (or anonymized subset)
3. Conduct user testing sessions with stakeholders
4. Collect feedback on:
   - Usability
   - Missing features
   - UI/UX issues
   - Performance

5. Prioritize and address feedback
6. Create user feedback log
7. Update roadmap based on feedback

**Deliverables**:
- [ ] Dashboard deployed to staging
- [ ] User testing sessions completed (≥3 users)
- [ ] Feedback collected and documented
- [ ] Critical issues fixed
- [ ] User sign-off obtained

**Time Estimate**: 3-5 hours
**Dependencies**: Task 4.2
**Assignee**: Human (with code-developer support)

---

### Summary Timeline

| Phase | Duration | Total Hours | Key Deliverables |
|-------|----------|-------------|------------------|
| **Phase 1: Foundation** | Days 1-2 | 12-16h | Query layer, charts, config |
| **Phase 2: Core Pages** | Days 3-5 | 18-24h | All 5 pages functional |
| **Phase 3: Polish & Testing** | Days 6-7 | 12-16h | Tests, docs, UI polish |
| **Phase 4: Deployment** | Days 8-10 | 8-12h | Production-ready deployment |
| **Total** | **8-10 days** | **50-68h** | Complete dashboard |

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (sequential)

**Parallelization Opportunities**:
- Task 1.2 and 1.3 can partially overlap (start charts once first queries are done)
- Tasks 2.2, 2.3, 2.4 can be worked on by multiple developers concurrently
- Task 3.1 and 3.2 can partially overlap

**Buffer**: Include 10-20% time buffer for unforeseen issues

---

## Testing Strategy

### 1. Unit Testing

**Framework**: pytest
**Coverage Target**: ≥85%

**Test Categories**:

#### Query Layer Tests (`tests/test_queries.py`)

```python
"""Unit tests for analytics queries."""

import pytest
from datetime import datetime, timedelta
from coffee_maker.langchain_observe.analytics.config import ExportConfig
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_quick_stats,
    get_cost_by_model,
    parse_date_range
)

@pytest.fixture
def test_config(tmp_path):
    """Create test database config."""
    db_path = tmp_path / "test_metrics.db"
    return ExportConfig(
        langfuse_public_key="test",
        langfuse_secret_key="test",
        db_type="sqlite",
        sqlite_path=str(db_path)
    )

@pytest.fixture
def populated_db(test_config):
    """Create database with sample data."""
    from coffee_maker.langchain_observe.analytics.models import Base, Generation
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(test_config.db_url)
    Base.metadata.create_all(engine)

    # Insert sample data
    with Session(engine) as session:
        for i in range(100):
            gen = Generation(
                id=f"gen_{i}",
                trace_id=f"trace_{i % 10}",
                model="openai/gpt-4",
                total_tokens=1000,
                total_cost=0.03,
                latency_ms=500,
                created_at=datetime.utcnow() - timedelta(days=i % 7)
            )
            session.add(gen)
        session.commit()

    return test_config

def test_get_quick_stats_empty_db(test_config):
    """Test quick stats with empty database."""
    stats = get_quick_stats(test_config)

    assert stats['total_requests'] == 0
    assert stats['total_cost'] == 0.0
    assert stats['avg_latency'] == 0.0

def test_get_quick_stats_populated(populated_db):
    """Test quick stats with populated database."""
    stats = get_quick_stats(populated_db)

    assert stats['total_requests'] > 0
    assert stats['total_cost'] > 0
    assert stats['avg_latency'] > 0

def test_get_cost_by_model(populated_db):
    """Test cost breakdown by model."""
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()

    result = get_cost_by_model(populated_db, start, end)

    assert not result.empty
    assert 'model' in result.columns
    assert 'total_cost' in result.columns
    assert result['total_cost'].sum() > 0

def test_parse_date_range():
    """Test date range parsing."""
    start, end = parse_date_range('last_7_days')

    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert (end - start).days == 7
```

#### Component Tests (`tests/test_components.py`)

```python
"""Unit tests for dashboard components."""

import pytest
import pandas as pd
from streamlit_apps.analytics_dashboard.components.charts import (
    create_cost_breakdown_pie,
    create_cost_trend_line
)

def test_cost_breakdown_pie_with_data():
    """Test pie chart creation with valid data."""
    data = pd.DataFrame({
        'model': ['gpt-4', 'claude-3', 'gemini'],
        'total_cost': [10.5, 8.2, 3.1]
    })

    fig = create_cost_breakdown_pie(data)

    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].type == 'pie'

def test_cost_breakdown_pie_empty_data():
    """Test pie chart with empty DataFrame."""
    data = pd.DataFrame(columns=['model', 'total_cost'])

    fig = create_cost_breakdown_pie(data)

    # Should still create figure, just empty
    assert fig is not None

def test_cost_trend_line():
    """Test line chart creation."""
    data = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=7),
        'daily_cost': [1.5, 2.3, 1.8, 2.9, 3.1, 2.5, 2.8]
    })

    fig = create_cost_trend_line(data)

    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].type == 'scatter'
```

### 2. Integration Testing

**Framework**: pytest + Selenium (for UI testing)

**Test Scenarios**:
- Full page load cycle
- Filter interactions
- Chart interactivity
- Export functionality

```python
"""Integration tests for dashboard pages."""

import pytest
from streamlit.testing.v1 import AppTest

def test_overview_page_load():
    """Test that overview page loads without errors."""
    at = AppTest.from_file("streamlit_apps/analytics_dashboard/app.py")
    at.run()

    assert not at.exception
    assert "Overview" in at.title[0].value

def test_filter_interaction():
    """Test that filters update page content."""
    at = AppTest.from_file("streamlit_apps/analytics_dashboard/app.py")
    at.run()

    # Change date range filter
    at.selectbox[0].select("last_30_days").run()

    # Verify page updated
    assert at.session_state.date_range == "last_30_days"
```

### 3. Performance Testing

**Framework**: pytest-benchmark + locust (for load testing)

**Metrics**:
- Page load time < 3s (with 100K rows)
- Query execution time < 500ms
- Memory usage < 500MB
- Cache hit rate > 80%

```python
"""Performance tests for dashboard."""

import pytest
from datetime import datetime, timedelta

def test_query_performance(benchmark, populated_db):
    """Benchmark query performance."""
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()

    result = benchmark(get_cost_by_model, populated_db, start, end)

    # Should complete in < 500ms
    assert benchmark.stats.stats.mean < 0.5
```

### 4. User Acceptance Testing

**Process**:
1. Deploy to staging environment
2. Invite 3-5 stakeholders
3. Provide test scenarios
4. Collect feedback via form
5. Address critical issues

**Test Scenarios**:
- View overall cost trends
- Identify most expensive model
- Compare model performance
- Export cost report for last month
- Find agent with highest latency

---

## Security Considerations

### 1. Authentication & Authorization

**Requirement**: Dashboard should only be accessible to authorized users.

**Implementation Options**:

#### Option A: Streamlit Native Authentication (Streamlit Cloud)
```python
# app.py
import streamlit as st

# Streamlit Cloud provides built-in authentication
# Configure in Streamlit Cloud dashboard
if not st.session_state.get("authenticated"):
    st.error("Please log in via Streamlit Cloud")
    st.stop()
```

#### Option B: Custom Authentication
```python
# utils/auth.py
import streamlit as st
import hashlib

def check_authentication():
    """Check if user is authenticated."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.stop()

def authenticate_user(username: str, password: str) -> bool:
    """Verify user credentials."""
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Check against environment variables or database
    valid_users = {
        "admin": os.getenv("ADMIN_PASSWORD_HASH")
    }

    return valid_users.get(username) == password_hash
```

#### Option C: OAuth Integration (Google, GitHub, etc.)
```python
# Use streamlit-authenticator library
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials={
        'usernames': {
            'admin': {
                'name': 'Admin User',
                'password': hashed_password
            }
        }
    },
    cookie_name='analytics_dashboard',
    key='dashboard_auth',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if not authentication_status:
    st.stop()
```

**Recommendation**: Start with Option A (Streamlit Cloud), add Option C for self-hosted deployments.

---

### 2. Data Access Control

**Requirement**: Restrict data visibility based on user roles.

**Implementation**:

```python
# utils/access_control.py
from enum import Enum
from typing import List

class Role(Enum):
    ADMIN = "admin"          # Full access
    ANALYST = "analyst"      # Read-only access
    DEVELOPER = "developer"  # Access to own agent data

class AccessControl:
    """Manage data access based on user roles."""

    def __init__(self, username: str, role: Role):
        self.username = username
        self.role = role

    def can_view_all_agents(self) -> bool:
        """Check if user can view all agent data."""
        return self.role in [Role.ADMIN, Role.ANALYST]

    def can_export_data(self) -> bool:
        """Check if user can export data."""
        return self.role in [Role.ADMIN, Role.ANALYST]

    def get_allowed_agents(self) -> List[str]:
        """Get list of agents user can access."""
        if self.can_view_all_agents():
            return []  # Empty list = all agents
        else:
            # Return only user's agents
            return [self.username]

# Usage in queries
def get_cost_by_model(config, start_date, end_date, access_control: AccessControl):
    """Get cost breakdown with access control."""
    allowed_agents = access_control.get_allowed_agents()

    if allowed_agents:
        # Filter by allowed agents
        agent_filter = f"AND agent IN ({','.join(allowed_agents)})"
    else:
        agent_filter = ""

    # ... rest of query
```

---

### 3. SQL Injection Prevention

**Requirement**: All database queries must use parameterized queries.

**Implementation**:

✅ **Correct** (parameterized):
```python
query = """
    SELECT * FROM generations
    WHERE created_at BETWEEN :start_date AND :end_date
    AND model = :model
"""
pd.read_sql(query, engine, params={
    'start_date': start_date,
    'end_date': end_date,
    'model': selected_model
})
```

❌ **Incorrect** (string interpolation):
```python
# NEVER DO THIS - vulnerable to SQL injection
query = f"""
    SELECT * FROM generations
    WHERE model = '{selected_model}'
"""
```

**Validation**: All queries in `queries/` directory use parameterized queries.

---

### 4. Sensitive Data Protection

**Requirement**: PII and sensitive data must not be exposed in the dashboard.

**Implementation**:

```python
# utils/data_sanitization.py
import re

def sanitize_trace_input(input_text: str) -> str:
    """Remove sensitive data from trace inputs."""
    if not input_text:
        return input_text

    # Redact email addresses
    input_text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', input_text)

    # Redact API keys (common patterns)
    input_text = re.sub(r'sk-[a-zA-Z0-9]{48}', '[API_KEY]', input_text)
    input_text = re.sub(r'pk-[a-zA-Z0-9]{48}', '[API_KEY]', input_text)

    # Redact phone numbers
    input_text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', input_text)

    return input_text

# Apply in queries
def get_recent_generations(config, limit=10):
    """Get recent generations with sanitized inputs."""
    df = pd.read_sql(query, engine)

    # Sanitize input/output columns
    df['input'] = df['input'].apply(sanitize_trace_input)
    df['output'] = df['output'].apply(sanitize_trace_input)

    return df
```

---

### 5. Environment Variables

**Requirement**: Credentials must never be hardcoded.

**Implementation**:

```bash
# .env.template
# Copy to .env and fill in values

# Langfuse credentials
LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-secret-here
LANGFUSE_HOST=https://cloud.langfuse.com

# Database (optional, defaults to SQLite)
DB_TYPE=sqlite
SQLITE_PATH=llm_metrics.db

# Dashboard authentication (optional)
DASHBOARD_PASSWORD_HASH=your-hashed-password-here

# Optional: PostgreSQL
# DB_TYPE=postgresql
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DATABASE=llm_metrics
# POSTGRES_USER=your-username
# POSTGRES_PASSWORD=your-password
```

**Validation**: Use `python-dotenv` and fail fast if required vars missing.

---

### 6. Audit Logging

**Requirement**: Log all data access and exports for compliance.

**Implementation**:

```python
# utils/audit_log.py
import logging
from datetime import datetime

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Log to separate file
handler = logging.FileHandler("audit.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s'
))
audit_logger.addHandler(handler)

def log_data_access(username: str, action: str, details: dict):
    """Log data access for audit trail."""
    audit_logger.info(f"USER={username} | ACTION={action} | DETAILS={details}")

# Usage
log_data_access(
    username=st.session_state.username,
    action="VIEW_COST_ANALYSIS",
    details={
        "date_range": "last_7_days",
        "models": ["gpt-4", "claude-3"]
    }
)

log_data_access(
    username=st.session_state.username,
    action="EXPORT_CSV",
    details={
        "date_range": "2025-01-01 to 2025-01-31",
        "row_count": 1234
    }
)
```

---

## Performance Requirements

### 1. Response Time Targets

| Operation | Target | Maximum Acceptable |
|-----------|--------|-------------------|
| Page Load (first visit) | < 3s | < 5s |
| Page Load (cached) | < 1s | < 2s |
| Query Execution | < 500ms | < 1s |
| Chart Rendering | < 200ms | < 500ms |
| Export Generation | < 5s | < 10s |

### 2. Scalability Requirements

| Database Size | Expected Performance |
|---------------|---------------------|
| 1K generations | All operations < 1s |
| 10K generations | All operations < 2s |
| 100K generations | Page load < 3s, queries < 1s |
| 1M generations | Page load < 5s, queries < 2s (requires indexing) |

### 3. Caching Strategy

**Cache Configuration**:
```python
# Streamlit cache configuration
@st.cache_data(
    ttl=300,  # 5 minutes
    max_entries=100,  # Store up to 100 cached results
    show_spinner="Loading data..."
)
def get_cost_by_model(config, start_date, end_date):
    """Cached query function."""
    pass
```

**Cache Warming**:
```python
# On dashboard startup, pre-load common queries
def warm_cache():
    """Pre-load frequently accessed data."""
    config = st.session_state.db_config

    # Common date ranges
    for range_key in ['last_24_hours', 'last_7_days', 'last_30_days']:
        start, end = parse_date_range(range_key)
        get_cost_by_model(config, start, end)
        get_daily_cost_trend(config, start, end)
```

### 4. Database Optimization

**Required Indexes** (ensure these exist from PRIORITY 1):
```sql
-- Ensure these indexes exist
CREATE INDEX IF NOT EXISTS idx_generation_created_at ON generations(created_at);
CREATE INDEX IF NOT EXISTS idx_generation_model ON generations(model);
CREATE INDEX IF NOT EXISTS idx_generation_trace_created ON generations(trace_id, created_at);
CREATE INDEX IF NOT EXISTS idx_trace_created_at ON traces(created_at);
```

**Query Optimization**:
- Use `EXPLAIN QUERY PLAN` to verify index usage
- Limit result sets with `LIMIT` clauses
- Use aggregations in SQL rather than pandas where possible
- Avoid `SELECT *`, only select needed columns

### 5. Memory Management

**Techniques**:
- Stream large result sets using `chunksize` parameter
- Release DataFrame memory after use: `del df`
- Use `pd.read_sql_query()` with `chunksize` for large exports
- Monitor memory usage with `psutil`

```python
# Example: Chunked reading for large exports
def export_large_dataset(config, start_date, end_date):
    """Export large dataset in chunks to avoid memory issues."""
    engine = create_engine(config.db_url)

    query = "SELECT * FROM generations WHERE created_at BETWEEN :start AND :end"

    # Read in chunks of 10K rows
    chunks = []
    for chunk in pd.read_sql(query, engine, params={'start': start_date, 'end': end_date}, chunksize=10000):
        chunks.append(chunk)

    # Concatenate at the end
    result = pd.concat(chunks, ignore_index=True)
    return result
```

---

## Risk Analysis

### 1. Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Database performance degrades with large datasets** | High | High | - Implement proper indexing<br>- Add query optimization<br>- Consider data archiving strategy |
| **Streamlit caching issues** | Medium | Medium | - Thoroughly test cache invalidation<br>- Add manual cache clear button<br>- Monitor cache hit rates |
| **Memory leaks in long-running sessions** | Medium | High | - Implement session timeouts<br>- Add memory monitoring<br>- Test with long sessions |
| **Plotly charts slow to render** | Low | Medium | - Use Altair for simple charts<br>- Implement chart virtualization<br>- Add loading indicators |
| **Export generation timeout** | Medium | Medium | - Implement background task queue<br>- Add progress indicators<br>- Set reasonable export limits |

### 2. Data Quality Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Missing or incomplete trace data** | High | Medium | - Add data validation<br>- Handle null values gracefully<br>- Show data quality metrics |
| **Inconsistent model naming** | Medium | Low | - Normalize model names<br>- Add model aliases<br>- Document naming conventions |
| **Agent metadata not captured** | High | Medium | - Provide fallback aggregations<br>- Document metadata requirements<br>- Add metadata validation |

### 3. User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Dashboard too complex for non-technical users** | Medium | High | - Add guided tour<br>- Provide contextual help<br>- Include example use cases |
| **Overwhelming amount of data** | Medium | Medium | - Implement smart defaults<br>- Add data summarization<br>- Provide drill-down capabilities |
| **Confusion about metrics** | High | Medium | - Add tooltips to all metrics<br>- Provide glossary<br>- Include calculation explanations |

### 4. Security Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Unauthorized access to sensitive data** | Medium | High | - Implement authentication<br>- Add role-based access control<br>- Audit logging |
| **SQL injection vulnerabilities** | Low | High | - Use parameterized queries only<br>- Code review all queries<br>- Add SQL injection tests |
| **Exposure of PII in traces** | High | High | - Implement data sanitization<br>- Redact sensitive fields<br>- Add PII detection |

### 5. Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Dashboard downtime** | Low | Medium | - Deploy to reliable platform<br>- Add health checks<br>- Set up monitoring |
| **Broken dashboard after Streamlit upgrade** | Medium | Medium | - Pin Streamlit version<br>- Add upgrade testing<br>- Maintain changelog |
| **Data export failures** | Low | Low | - Add retry logic<br>- Implement error reporting<br>- Test with various data sizes |

---

## Success Criteria

### 1. Functional Requirements

- [ ] **Dashboard Accessibility**: Dashboard loads successfully at `http://localhost:8501`
- [ ] **All Pages Functional**: All 5 pages (Overview, Cost Analysis, Model Comparison, Agent Performance, Exports) load without errors
- [ ] **Data Visualization**: All charts render correctly with sample data
- [ ] **Filters Work**: Date range, model, and agent filters update page content
- [ ] **Export Functionality**: CSV and PDF exports generate successfully
- [ ] **Responsive Design**: Dashboard usable on desktop (1920x1080) and laptop (1366x768) screens

### 2. Performance Requirements

- [ ] **Page Load Time**: First page load < 3s with 100K generations in database
- [ ] **Query Performance**: All database queries execute in < 500ms (95th percentile)
- [ ] **Cache Effectiveness**: Cache hit rate > 80% after warm-up period
- [ ] **Memory Efficiency**: Dashboard memory usage < 500MB during normal operation
- [ ] **Export Speed**: CSV export of 10K rows completes in < 5s

### 3. Data Quality Requirements

- [ ] **Data Accuracy**: Cost calculations match source data (Langfuse) within 0.01%
- [ ] **No Data Loss**: All generations in database appear in dashboard
- [ ] **Proper Aggregations**: Aggregated metrics (sum, average) are mathematically correct
- [ ] **Handle Missing Data**: Dashboard gracefully handles null values and missing fields

### 4. Usability Requirements

- [ ] **Intuitive Navigation**: Users can navigate to any page within 2 clicks
- [ ] **Clear Metrics**: All metrics have labels and tooltips explaining what they mean
- [ ] **Helpful Errors**: Error messages are user-friendly and actionable
- [ ] **Onboarding**: First-time users can understand dashboard purpose within 30 seconds
- [ ] **Accessibility**: Dashboard meets WCAG 2.1 Level AA standards (Lighthouse score ≥90)

### 5. Testing Requirements

- [ ] **Test Coverage**: Code coverage ≥ 85% for query layer and components
- [ ] **All Tests Pass**: 100% of unit, integration, and performance tests pass
- [ ] **No Critical Bugs**: Zero P0/P1 bugs in issue tracker
- [ ] **Browser Compatibility**: Dashboard works in Chrome, Firefox, Safari, Edge (latest versions)

### 6. Documentation Requirements

- [ ] **README Complete**: README.md includes installation, configuration, and usage instructions
- [ ] **API Documentation**: All functions have docstrings with examples
- [ ] **Architecture Documented**: Architecture diagram and component descriptions available
- [ ] **Troubleshooting Guide**: Common issues and solutions documented

### 7. User Acceptance Criteria

- [ ] **Stakeholder Sign-Off**: At least 3 stakeholders approve dashboard
- [ ] **User Feedback**: Average user satisfaction score ≥ 4/5
- [ ] **Identified Value**: Users identify at least 1 actionable insight from dashboard
- [ ] **Adoption**: Dashboard accessed at least weekly by intended users

### 8. Deployment Requirements

- [ ] **Deployable**: Dashboard can be deployed to at least 2 platforms (Streamlit Cloud, Docker)
- [ ] **Environment Config**: All configuration via environment variables (no hardcoded credentials)
- [ ] **Health Check**: Dashboard includes health check endpoint
- [ ] **Logging**: All critical operations logged with appropriate levels

---

## Appendix

### A. Model Pricing Reference

For accurate cost calculations, maintain this reference table:

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
|-------|---------------------------|----------------------------|
| openai/gpt-4o | $2.50 | $10.00 |
| openai/gpt-4-turbo | $10.00 | $30.00 |
| openai/gpt-4 | $30.00 | $60.00 |
| openai/gpt-3.5-turbo | $0.50 | $1.50 |
| anthropic/claude-3-opus | $15.00 | $75.00 |
| anthropic/claude-3-sonnet | $3.00 | $15.00 |
| anthropic/claude-3-haiku | $0.25 | $1.25 |
| google/gemini-pro | $0.50 | $1.50 |
| google/gemini-ultra | $10.00 | $30.00 |

**Source**: https://openai.com/pricing, https://anthropic.com/pricing, https://cloud.google.com/vertex-ai/pricing

**Update Frequency**: Monthly (prices change periodically)

---

### B. Database Schema Reference

See **Database Schema Analysis** section for complete schema.

Key tables:
- `generations`: Primary data source (token counts, costs, latency)
- `traces`: Session/user tracking
- `performance_metrics`: Pre-aggregated metrics

---

### C. Environment Variables Reference

```bash
# Required
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx

# Optional
LANGFUSE_HOST=https://cloud.langfuse.com  # Default
DB_TYPE=sqlite                             # sqlite or postgresql
SQLITE_PATH=llm_metrics.db                 # SQLite database path

# PostgreSQL (if DB_TYPE=postgresql)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=llm_metrics
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Dashboard configuration (optional)
DASHBOARD_CACHE_TTL=300                    # Cache TTL in seconds (default: 300)
DASHBOARD_MAX_ROWS=100                     # Max rows in tables (default: 100)
```

---

### D. Troubleshooting Guide

#### Issue: Dashboard fails to start with "No module named 'streamlit'"

**Solution**:
```bash
poetry install
poetry run streamlit run streamlit_apps/analytics_dashboard/app.py
```

#### Issue: "Database not found" error

**Solution**:
1. Verify `SQLITE_PATH` environment variable is set correctly
2. Ensure Langfuse exporter has run at least once:
   ```bash
   poetry run python -m coffee_maker.langchain_observe.analytics.exporter
   ```
3. Check database file exists: `ls -l llm_metrics.db`

#### Issue: Charts not displaying

**Solution**:
1. Check browser console for JavaScript errors
2. Verify Plotly is installed: `poetry show plotly`
3. Try clearing browser cache
4. Check Streamlit version: `poetry show streamlit` (requires ≥1.32.0)

#### Issue: Queries are very slow

**Solution**:
1. Check database indexes exist:
   ```sql
   sqlite3 llm_metrics.db ".indexes"
   ```
2. Analyze query plan:
   ```sql
   EXPLAIN QUERY PLAN SELECT * FROM generations WHERE created_at > datetime('now', '-7 days');
   ```
3. Consider archiving old data
4. Reduce date range in filters

---

### E. Future Enhancements

**Post-MVP Features** (not in initial scope):

1. **Real-Time Updates**: WebSocket integration for live data
2. **Advanced Forecasting**: ML-based cost prediction models
3. **Anomaly Detection**: Automatic detection of cost spikes
4. **Custom Dashboards**: User-configurable dashboard layouts
5. **Slack/Discord Integration**: Automated cost alerts
6. **Multi-Tenant Support**: Separate dashboards per team
7. **API Access**: REST API for programmatic access to metrics
8. **Mobile Optimization**: Responsive design for mobile devices
9. **Dark Mode**: Theme toggle for dark mode
10. **Scheduled Reports**: Automated email reports

---

### F. References

**Documentation**:
- Streamlit Docs: https://docs.streamlit.io/
- Plotly Python: https://plotly.com/python/
- Pandas: https://pandas.pydata.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/

**Related Project Files**:
- PRIORITY 1 spec: `coffee_maker/langchain_observe/analytics/`
- Database models: `coffee_maker/langchain_observe/analytics/models.py`
- Exporter: `coffee_maker/langchain_observe/analytics/exporter.py`

**Issue Tracker**:
- GitHub Issues: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-11 | Claude (code-developer) | Initial technical specification |

---

**End of Technical Specification**

This specification is ready for implementation. Estimated completion: **8-10 days** with dedicated focus.

**Next Steps**:
1. Review and approve this specification
2. Create implementation branch: `feature/priority-5-analytics-dashboard`
3. Begin Phase 1: Foundation (Tasks 1.1-1.3)
4. Track progress in GitHub Issues

For questions or clarifications, please create an issue on GitHub or contact the project maintainer.
