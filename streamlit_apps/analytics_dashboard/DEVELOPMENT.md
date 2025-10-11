# Analytics Dashboard - Developer Guide

This guide provides comprehensive documentation for developers working on the LLM Analytics Dashboard. It covers architecture, code organization, development workflows, and best practices.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Code Organization](#code-organization)
- [Development Setup](#development-setup)
- [Adding New Features](#adding-new-features)
- [Database Schema](#database-schema)
- [Query Optimization](#query-optimization)
- [Testing](#testing)
- [Code Style Guidelines](#code-style-guidelines)
- [Contributing](#contributing)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                 │
│  (app.py + pages/01_*.py, 02_*.py, ...)           │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Components  │  │   Filters    │
│  (UI Layer)  │  │  (Sidebar)   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
        ┌───────────────┐
        │    Queries    │
        │ (Data Layer)  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │   Database    │
        │ SQLite/Postgres│
        └───────────────┘
```

### Design Principles

1. **Separation of Concerns**: UI components, data queries, and business logic are separated
2. **Caching**: All queries use `@st.cache_data` for performance
3. **Modularity**: Reusable components and utility functions
4. **Configuration-Driven**: Environment variables for all settings
5. **Error Handling**: Graceful degradation with user-friendly error messages

### Key Technologies

- **Frontend**: Streamlit 1.32+
- **Visualization**: Plotly Express & Plotly Graph Objects
- **Data Processing**: pandas
- **Database**: SQLite (primary), PostgreSQL (supported)
- **Configuration**: python-dotenv

## Directory Structure

```
streamlit_apps/analytics_dashboard/
├── app.py                          # Main entry point & home page
├── config.py                       # Configuration management
├── README.md                       # User documentation
├── DEVELOPMENT.md                  # This file
│
├── pages/                          # Multi-page app pages
│   ├── __init__.py
│   ├── 01_📈_Overview.py          # Overview page
│   ├── 02_💰_Cost_Analysis.py     # Cost analysis page
│   ├── 03_🔍_Model_Comparison.py  # Model comparison page
│   ├── 04_🤖_Agent_Performance.py # Agent performance page
│   └── 05_📥_Exports.py           # Export functionality page
│
├── components/                     # Reusable UI components
│   ├── __init__.py
│   ├── charts.py                  # Chart creation functions
│   ├── filters.py                 # Filter UI components
│   ├── metrics.py                 # Metric card components
│   └── tables.py                  # Table rendering components
│
├── queries/                        # Database query functions
│   ├── __init__.py
│   ├── analytics_queries.py       # Core analytics queries
│   ├── cost_queries.py            # Cost-specific queries
│   ├── performance_queries.py     # Performance queries
│   └── export_queries.py          # Export data queries
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── format_utils.py            # Formatting helpers
│   ├── data_processing.py         # Data transformation
│   └── export_utils.py            # Export helpers
│
└── tests/                          # Test files
    ├── __init__.py
    ├── test_queries.py
    ├── test_components.py
    └── test_utils.py
```

### File Responsibilities

| File/Directory | Purpose |
|----------------|---------|
| `app.py` | Main entry point, home page, global configuration |
| `config.py` | DashboardConfig class, environment variable loading |
| `pages/` | Individual dashboard pages (Streamlit multi-page app) |
| `components/` | Reusable UI components (charts, tables, filters) |
| `queries/` | Database query functions with caching |
| `utils/` | Pure utility functions (formatting, data processing) |
| `tests/` | Unit and integration tests |

## Code Organization

### 1. Configuration Layer (`config.py`)

The `DashboardConfig` class manages all configuration:

```python
from streamlit_apps.analytics_dashboard.config import get_config

config = get_config()  # Singleton instance
print(config.db_path)  # Database path or connection string
config.validate()      # Validates configuration
```

**Key Methods**:
- `from_env()`: Load configuration from environment variables
- `db_path`: Get database path/connection string
- `absolute_db_path`: Get absolute path to SQLite database
- `validate()`: Validate configuration and database existence

### 2. Query Layer (`queries/`)

All database queries follow these patterns:

```python
import streamlit as st
import pandas as pd

@st.cache_data(ttl=300)
def get_sample_data(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> pd.DataFrame:
    """
    Query description.

    Args:
        db_path: Path to SQLite database or PostgreSQL connection string
        date_range: Optional (start_date, end_date) tuple for filtering

    Returns:
        DataFrame with columns: col1, col2, col3

    Example:
        >>> df = get_sample_data("llm_metrics.db")
        >>> print(df.head())
    """
    conn = sqlite3.connect(db_path)

    # Build WHERE clause dynamically
    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT col1, col2, col3
        FROM table_name
        {where_clause}
        ORDER BY col1
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df
```

**Query Guidelines**:
- Always use `@st.cache_data(ttl=300)` for caching
- Accept `db_path` as first parameter
- Use parameterized queries to prevent SQL injection
- Return pandas DataFrames
- Include comprehensive docstrings with examples

### 3. Component Layer (`components/`)

UI components are pure functions that accept data and return Streamlit elements:

```python
import streamlit as st
import plotly.graph_objects as go

def create_example_chart(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """
    Create an example chart.

    Args:
        df: DataFrame with columns: x, y
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object

    Example:
        >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 30]})
        >>> fig = create_example_chart(df)
        >>> st.plotly_chart(fig, use_container_width=True)
    """
    if df.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(text="No data available", ...)
        return fig

    # Create chart
    fig = px.line(df, x='x', y='y', title='Example Chart')
    fig.update_layout(height=height)

    return fig
```

**Component Guidelines**:
- Always handle empty data gracefully
- Use type hints for parameters
- Return Plotly figures, not direct Streamlit calls
- Make height and colors configurable
- Include clear docstrings with examples

### 4. Utility Layer (`utils/`)

Pure utility functions for formatting and data processing:

```python
def format_example(value: Optional[float]) -> str:
    """
    Format a value for display.

    Args:
        value: Value to format (can be None)

    Returns:
        Formatted string

    Example:
        >>> format_example(1234.56)
        '1.23K'
    """
    if value is None:
        return "N/A"

    # Implementation
    return formatted_value
```

## Development Setup

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Bobain/MonolithicCoffeeMakerAgent.git
   cd MonolithicCoffeeMakerAgent
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   poetry shell
   ```

3. **Create test database**:
   ```bash
   # Create a test database with sample data
   python scripts/create_test_db.py  # If available
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the dashboard**:
   ```bash
   streamlit run streamlit_apps/analytics_dashboard/app.py
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes and test**:
   ```bash
   # Make your changes
   # Test locally
   streamlit run streamlit_apps/analytics_dashboard/app.py
   ```

3. **Run tests**:
   ```bash
   pytest streamlit_apps/analytics_dashboard/tests/
   ```

4. **Format code**:
   ```bash
   # Run pre-commit hooks
   pre-commit run --all-files
   ```

5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push origin feature/my-new-feature
   ```

6. **Create pull request**:
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Wait for review

## Adding New Features

### Adding a New Page

**Step 1: Create the page file**

Create a new file in `pages/` with the naming convention `XX_emoji_PageName.py`:

```bash
touch streamlit_apps/analytics_dashboard/pages/06_🔔_Alerts.py
```

**Step 2: Implement the page**

```python
"""Alerts Page - LLM Analytics Dashboard.

This page displays alerts and notifications for LLM usage anomalies.
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_apps.analytics_dashboard.config import get_config
from streamlit_apps.analytics_dashboard.components.filters import render_global_filters
from streamlit_apps.analytics_dashboard.queries.analytics_queries import (
    get_available_models,
    get_available_agents,
)

def main():
    """Main function for the Alerts page."""
    st.title("🔔 Alerts")
    st.markdown("### Usage Anomalies and Notifications")

    # Load configuration
    try:
        config = get_config()
        config.validate()
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.stop()

    # Render filters
    try:
        available_models = get_available_models(config.db_path)
        available_agents = get_available_agents(config.db_path)
    except Exception as e:
        st.error(f"Failed to load filter options: {e}")
        st.stop()

    filters = render_global_filters(available_models, available_agents)

    # Your page implementation here
    st.info("Alerts page implementation goes here")

if __name__ == "__main__":
    main()
```

**Step 3: Add to navigation**

Update `app.py` to include the new page in the sidebar description:

```python
st.markdown(
    """
    - **📈 Overview**: Global metrics and trends
    - **💰 Cost Analysis**: Detailed cost breakdown
    - **🔍 Model Comparison**: Compare model performance
    - **🤖 Agent Performance**: Agent-specific analytics
    - **📥 Exports**: Download reports and data
    - **🔔 Alerts**: Usage anomalies and notifications  # NEW
    """
)
```

**Step 4: Test the page**

```bash
streamlit run streamlit_apps/analytics_dashboard/app.py
# Navigate to the new page in the sidebar
```

### Adding a New Chart Type

**Step 1: Create the chart function**

Add to `components/charts.py`:

```python
def create_anomaly_scatter(
    df: pd.DataFrame,
    height: int = 400
) -> go.Figure:
    """
    Create a scatter plot showing cost anomalies.

    Args:
        df: DataFrame with columns:
            - timestamp (datetime): Time of request
            - cost (float): Request cost
            - is_anomaly (bool): Whether this is an anomaly
        height: Chart height in pixels (default: 400)

    Returns:
        Plotly Figure object with scatter plot

    Examples:
        >>> df = pd.DataFrame({
        ...     'timestamp': pd.date_range('2025-10-01', periods=100),
        ...     'cost': np.random.normal(10, 2, 100),
        ...     'is_anomaly': [False] * 95 + [True] * 5
        ... })
        >>> fig = create_anomaly_scatter(df)
        >>> st.plotly_chart(fig, use_container_width=True)
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=height)
        return fig

    # Separate normal and anomaly points
    normal = df[~df['is_anomaly']]
    anomalies = df[df['is_anomaly']]

    fig = go.Figure()

    # Add normal points
    fig.add_trace(go.Scatter(
        x=normal['timestamp'],
        y=normal['cost'],
        mode='markers',
        name='Normal',
        marker=dict(color='blue', size=6),
        hovertemplate='<b>Time: %{x}</b><br>Cost: $%{y:.2f}<extra></extra>'
    ))

    # Add anomaly points
    fig.add_trace(go.Scatter(
        x=anomalies['timestamp'],
        y=anomalies['cost'],
        mode='markers',
        name='Anomaly',
        marker=dict(color='red', size=12, symbol='x'),
        hovertemplate='<b>ANOMALY</b><br>Time: %{x}<br>Cost: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Cost Anomaly Detection',
        xaxis_title='Time',
        yaxis_title='Cost ($)',
        height=height,
        hovermode='closest',
        showlegend=True
    )

    return fig
```

**Step 2: Create supporting query**

Add to `queries/analytics_queries.py` or create new query file:

```python
@st.cache_data(ttl=300)
def get_cost_anomalies(
    db_path: str,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    threshold_std: float = 3.0
) -> pd.DataFrame:
    """
    Detect cost anomalies using statistical methods.

    Args:
        db_path: Path to SQLite database
        date_range: Optional (start_date, end_date) tuple
        threshold_std: Number of standard deviations for anomaly threshold

    Returns:
        DataFrame with columns: timestamp, cost, is_anomaly, z_score

    Example:
        >>> df = get_cost_anomalies("llm_metrics.db", threshold_std=2.5)
        >>> anomalies = df[df['is_anomaly']]
        >>> print(f"Found {len(anomalies)} anomalies")
    """
    conn = sqlite3.connect(db_path)

    where_clause = ""
    params = []
    if date_range:
        where_clause = "WHERE created_at BETWEEN ? AND ?"
        params = [date_range[0], date_range[1]]

    query = f"""
        SELECT
            created_at as timestamp,
            total_cost as cost
        FROM generations
        {where_clause}
        ORDER BY created_at
    """

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Calculate anomalies
    mean_cost = df['cost'].mean()
    std_cost = df['cost'].std()
    df['z_score'] = (df['cost'] - mean_cost) / std_cost
    df['is_anomaly'] = df['z_score'].abs() > threshold_std

    return df
```

**Step 3: Use in a page**

```python
# In your page file
from streamlit_apps.analytics_dashboard.components.charts import create_anomaly_scatter
from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_cost_anomalies

# In your main() function
st.subheader("Cost Anomaly Detection")

try:
    with st.spinner("Detecting anomalies..."):
        anomaly_data = get_cost_anomalies(config.db_path, date_range)

        if anomaly_data.empty:
            st.info("No data available for anomaly detection.")
        else:
            fig = create_anomaly_scatter(anomaly_data)
            st.plotly_chart(fig, use_container_width=True)

            # Show anomaly count
            anomaly_count = anomaly_data['is_anomaly'].sum()
            st.warning(f"⚠️ Detected {anomaly_count} anomalies")
except Exception as e:
    st.error(f"Failed to detect anomalies: {e}")
```

### Adding a New Metric Card

Add to `components/metrics.py`:

```python
def render_efficiency_card(
    total_tokens: int,
    total_cost: float,
    label: str = "Token Efficiency"
) -> None:
    """
    Render a metric card showing cost per 1K tokens.

    Args:
        total_tokens: Total number of tokens used
        total_cost: Total cost in USD
        label: Label for the metric card

    Example:
        >>> render_efficiency_card(
        ...     total_tokens=1000000,
        ...     total_cost=50.0,
        ...     label="Overall Efficiency"
        ... )
    """
    if total_tokens == 0:
        cost_per_1k = 0
    else:
        cost_per_1k = (total_cost / total_tokens) * 1000

    st.metric(
        label=label,
        value=f"${cost_per_1k:.4f}/1K tokens",
        delta=None,
        help="Cost per 1,000 tokens"
    )
```

## Database Schema

### Core Tables

#### `generations` Table

```sql
CREATE TABLE generations (
    id TEXT PRIMARY KEY,                 -- Unique generation ID
    created_at TIMESTAMP NOT NULL,       -- Creation timestamp
    model TEXT NOT NULL,                 -- Model name (e.g., "gpt-4o-mini")
    total_tokens INTEGER DEFAULT 0,      -- Total tokens used
    input_tokens INTEGER DEFAULT 0,      -- Input/prompt tokens
    output_tokens INTEGER DEFAULT 0,     -- Output/completion tokens
    total_cost REAL DEFAULT 0.0,         -- Total cost in USD
    latency_ms REAL DEFAULT 0.0,         -- Latency in milliseconds
    trace_id TEXT,                       -- Associated trace ID
    status TEXT,                         -- Request status (success, error, etc.)
    FOREIGN KEY (trace_id) REFERENCES traces(id)
);

-- Indexes for performance
CREATE INDEX idx_generations_created_at ON generations(created_at);
CREATE INDEX idx_generations_model ON generations(model);
CREATE INDEX idx_generations_trace_id ON generations(trace_id);
```

#### `traces` Table

```sql
CREATE TABLE traces (
    id TEXT PRIMARY KEY,                 -- Unique trace ID
    name TEXT,                           -- Trace/agent name
    created_at TIMESTAMP NOT NULL,       -- Creation timestamp
    metadata TEXT,                       -- JSON metadata
    user_id TEXT                         -- Optional user ID
);

-- Indexes for performance
CREATE INDEX idx_traces_name ON traces(name);
CREATE INDEX idx_traces_created_at ON traces(created_at);
```

### Query Patterns

#### Date Range Filtering

```python
# Always use parameterized queries
where_clause = "WHERE created_at BETWEEN ? AND ?"
params = [start_date, end_date]
```

#### Model Filtering

```python
# Single model
where_clause = "WHERE model = ?"
params = [model_name]

# Multiple models
placeholders = ','.join('?' * len(models))
where_clause = f"WHERE model IN ({placeholders})"
params = models
```

#### Aggregations

```python
# Cost by model
query = """
    SELECT
        model,
        SUM(total_cost) as total_cost,
        COUNT(*) as request_count,
        AVG(total_cost) as avg_cost,
        SUM(total_tokens) as total_tokens
    FROM generations
    WHERE created_at BETWEEN ? AND ?
    GROUP BY model
    ORDER BY total_cost DESC
"""
```

## Query Optimization

### Best Practices

1. **Use Indexes**: Ensure indexes exist on frequently queried columns:
   ```sql
   CREATE INDEX idx_created_at ON generations(created_at);
   CREATE INDEX idx_model ON generations(model);
   ```

2. **Limit Result Sets**: Use LIMIT for large queries:
   ```python
   query = """
       SELECT * FROM generations
       ORDER BY created_at DESC
       LIMIT 1000
   """
   ```

3. **Avoid SELECT ***: Only select needed columns:
   ```python
   # Good
   query = "SELECT id, model, total_cost FROM generations"

   # Bad
   query = "SELECT * FROM generations"
   ```

4. **Use Aggregations in SQL**: Don't process large datasets in pandas:
   ```python
   # Good: Aggregate in SQL
   query = "SELECT model, SUM(total_cost) as cost FROM generations GROUP BY model"

   # Bad: Load all data then aggregate
   query = "SELECT model, total_cost FROM generations"
   df.groupby('model')['total_cost'].sum()
   ```

5. **Cache Aggressively**: Use appropriate TTL:
   ```python
   @st.cache_data(ttl=300)  # 5 minutes for frequently changing data
   @st.cache_data(ttl=3600)  # 1 hour for historical data
   ```

### Performance Monitoring

Add query timing:

```python
import time

def get_data_with_timing(db_path: str):
    start = time.time()

    # Your query
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()

    elapsed = time.time() - start
    if elapsed > 1.0:
        st.warning(f"Slow query: {elapsed:.2f}s")

    return df
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_queries.py          # Query function tests
├── test_components.py       # Component tests
├── test_utils.py            # Utility function tests
└── fixtures/
    └── test_data.db         # Test database
```

### Writing Query Tests

```python
# tests/test_queries.py
import pytest
from streamlit_apps.analytics_dashboard.queries.analytics_queries import get_quick_stats

def test_get_quick_stats(test_db_path):
    """Test quick stats query returns correct structure."""
    stats = get_quick_stats(test_db_path)

    assert 'total_cost' in stats
    assert 'total_tokens' in stats
    assert 'total_requests' in stats
    assert 'avg_latency' in stats

    assert isinstance(stats['total_cost'], float)
    assert isinstance(stats['total_tokens'], int)
    assert isinstance(stats['total_requests'], int)
    assert isinstance(stats['avg_latency'], float)

def test_get_quick_stats_with_date_range(test_db_path):
    """Test quick stats with date range filtering."""
    from datetime import datetime, timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    stats = get_quick_stats(test_db_path, (start_date, end_date))

    assert stats['total_requests'] > 0
```

### Writing Component Tests

```python
# tests/test_components.py
import pytest
import pandas as pd
from streamlit_apps.analytics_dashboard.components.charts import create_cost_breakdown_pie

def test_create_cost_breakdown_pie_with_data():
    """Test pie chart creation with valid data."""
    df = pd.DataFrame({
        'model': ['gpt-4', 'gpt-3.5-turbo'],
        'total_cost': [100.0, 50.0]
    })

    fig = create_cost_breakdown_pie(df)

    assert fig is not None
    assert len(fig.data) > 0

def test_create_cost_breakdown_pie_empty():
    """Test pie chart handles empty data gracefully."""
    df = pd.DataFrame(columns=['model', 'total_cost'])

    fig = create_cost_breakdown_pie(df)

    assert fig is not None
    # Should have annotation for empty data
```

### Writing Utility Tests

```python
# tests/test_utils.py
import pytest
from streamlit_apps.analytics_dashboard.utils.format_utils import format_currency

def test_format_currency_positive():
    """Test currency formatting for positive values."""
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(0) == "$0.00"
    assert format_currency(1000000) == "$1,000,000.00"

def test_format_currency_negative():
    """Test currency formatting for negative values."""
    assert format_currency(-50) == "-$50.00"

def test_format_currency_none():
    """Test currency formatting for None."""
    assert format_currency(None) == "$0.00"
```

### Running Tests

```bash
# Run all tests
pytest streamlit_apps/analytics_dashboard/tests/

# Run specific test file
pytest streamlit_apps/analytics_dashboard/tests/test_queries.py

# Run with coverage
pytest streamlit_apps/analytics_dashboard/tests/ --cov=streamlit_apps/analytics_dashboard

# Run with verbose output
pytest streamlit_apps/analytics_dashboard/tests/ -v

# Run specific test
pytest streamlit_apps/analytics_dashboard/tests/test_queries.py::test_get_quick_stats
```

### Test Fixtures

Create reusable fixtures in `conftest.py`:

```python
# tests/conftest.py
import pytest
import sqlite3
from pathlib import Path

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"

    # Create tables and sample data
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE generations (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP,
            model TEXT,
            total_tokens INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_cost REAL,
            latency_ms REAL,
            trace_id TEXT
        )
    """)

    # Insert sample data
    cursor.execute("""
        INSERT INTO generations VALUES
        ('1', '2025-10-11 10:00:00', 'gpt-4', 1000, 600, 400, 0.05, 1500, 'trace1'),
        ('2', '2025-10-11 11:00:00', 'gpt-3.5-turbo', 2000, 1200, 800, 0.02, 800, 'trace1')
    """)

    conn.commit()
    conn.close()

    return str(db_path)
```

## Code Style Guidelines

### Python Style

Follow PEP 8 and project conventions:

1. **Imports**: Organize imports in sections:
   ```python
   # Standard library
   import sys
   from pathlib import Path
   from typing import Dict, List, Optional

   # Third-party
   import pandas as pd
   import streamlit as st
   import plotly.express as px

   # Local
   from streamlit_apps.analytics_dashboard.config import get_config
   from streamlit_apps.analytics_dashboard.queries import get_quick_stats
   ```

2. **Naming Conventions**:
   - Functions: `snake_case` (e.g., `get_quick_stats`)
   - Classes: `PascalCase` (e.g., `DashboardConfig`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `CACHE_TTL`)
   - Private functions: `_leading_underscore` (e.g., `_initialize_state`)

3. **Docstrings**: Use Google style:
   ```python
   def example_function(param1: str, param2: int) -> bool:
       """
       One-line summary.

       More detailed description if needed.
       Can span multiple lines.

       Args:
           param1: Description of param1
           param2: Description of param2

       Returns:
           Description of return value

       Raises:
           ValueError: When param2 is negative

       Example:
           >>> result = example_function("test", 5)
           >>> print(result)
           True
       """
       pass
   ```

4. **Type Hints**: Always use type hints:
   ```python
   def process_data(
       df: pd.DataFrame,
       threshold: float = 0.5
   ) -> pd.DataFrame:
       pass
   ```

5. **Error Handling**: Be specific and user-friendly:
   ```python
   try:
       data = get_data(db_path)
   except FileNotFoundError:
       st.error("Database file not found. Please check configuration.")
       st.stop()
   except Exception as e:
       st.error(f"Unexpected error: {e}")
       st.stop()
   ```

### Streamlit Best Practices

1. **Cache Wisely**:
   ```python
   @st.cache_data(ttl=300)  # For data
   def get_data(): pass

   @st.cache_resource  # For connections/resources
   def get_db_connection(): pass
   ```

2. **Handle Empty States**:
   ```python
   if df.empty:
       st.info("No data available for the selected filters.")
   else:
       st.dataframe(df)
   ```

3. **Use Spinners for Long Operations**:
   ```python
   with st.spinner("Loading data..."):
       data = expensive_operation()
   ```

4. **Organize with Containers**:
   ```python
   with st.container():
       st.subheader("Section 1")
       # Content

   st.divider()

   with st.container():
       st.subheader("Section 2")
       # Content
   ```

### Code Formatting

Use `black` for formatting:

```bash
# Format a file
black streamlit_apps/analytics_dashboard/app.py

# Format entire directory
black streamlit_apps/analytics_dashboard/

# Check without modifying
black --check streamlit_apps/analytics_dashboard/
```

Use `isort` for import sorting:

```bash
isort streamlit_apps/analytics_dashboard/
```

Use `flake8` for linting:

```bash
flake8 streamlit_apps/analytics_dashboard/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

The `.pre-commit-config.yaml` will run:
- black (formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

## Contributing

### Pull Request Process

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MonolithicCoffeeMakerAgent.git
   cd MonolithicCoffeeMakerAgent
   ```

2. **Create Branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make Changes**:
   - Write code
   - Add tests
   - Update documentation

4. **Run Tests**:
   ```bash
   pytest streamlit_apps/analytics_dashboard/tests/
   pre-commit run --all-files
   ```

5. **Commit**:
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test changes
   - `refactor:` Code refactoring
   - `style:` Formatting changes
   - `chore:` Maintenance tasks

6. **Push and PR**:
   ```bash
   git push origin feature/my-feature
   ```
   Then create a pull request on GitHub.

### PR Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No breaking changes (or documented)
- [ ] PR description explains changes

### Code Review Guidelines

**For Authors**:
- Keep PRs focused and small
- Write clear descriptions
- Respond to feedback promptly
- Be open to suggestions

**For Reviewers**:
- Be constructive and specific
- Focus on logic, not style (handled by tools)
- Ask questions if unclear
- Approve or request changes clearly

## Additional Resources

### Documentation

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Tools

- [Streamlit Cheat Sheet](https://cheat-sheet.streamlit.app/)
- [Plotly Chart Types](https://plotly.com/python/)
- [SQL Query Analyzer](https://www.eversql.com/)

### Internal Links

- [User Documentation](./README.md)
- [Project README](../../README.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)

---

**Happy Coding!**

For questions or issues, please open a GitHub issue or start a discussion.
