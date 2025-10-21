# LLM Analytics Dashboard

A comprehensive Streamlit-based analytics dashboard for monitoring and analyzing LLM usage, costs, and performance metrics. This dashboard connects to a SQLite or PostgreSQL database containing Langfuse export data and provides real-time insights into your LLM operations.

![Dashboard Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen)
![Streamlit](https://img.shields.io/badge/streamlit-1.32%2B-red)

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dashboard Pages](#dashboard-pages)
- [Troubleshooting](#troubleshooting)
- [Screenshots](#screenshots)
- [FAQ](#faq)
- [Support](#support)

## Features

### Core Capabilities

- **Real-time Analytics**: Automatic data refresh every 5 minutes with cached queries for optimal performance
- **Multi-Model Support**: Track and compare metrics across different LLM models (GPT-4, Claude, etc.)
- **Cost Tracking**: Comprehensive cost analysis with budget tracking and forecasting
- **Performance Monitoring**: Latency analysis, token efficiency, and request patterns
- **Interactive Visualizations**: Rich, interactive charts powered by Plotly
- **Flexible Filtering**: Filter data by date range, models, agents, and more
- **Export Capabilities**: Download reports in CSV and PDF formats

### Key Metrics

- Total cost and spending trends
- Token usage (input/output breakdown)
- Request counts and patterns
- Average latency and performance
- Model comparison and efficiency
- Agent-specific analytics
- Hourly usage heatmaps

## Prerequisites

Before installing the dashboard, ensure you have:

- **Python 3.9 or higher** (Python 3.11+ recommended)
- **pip** or **poetry** package manager
- **SQLite database** with Langfuse export data (or PostgreSQL connection)
- **Internet connection** for initial package installation

### System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for dependencies + database size
- **OS**: macOS, Linux, or Windows

## Installation

### Method 1: Using Poetry (Recommended)

If you're working within the MonolithicCoffeeMakerAgent project:

```bash
# Navigate to project root
cd /path/to/MonolithicCoffeeMakerAgent

# Install all dependencies (including Streamlit)
poetry install

# Activate the virtual environment
poetry shell
```

### Method 2: Using pip

If you prefer pip or are installing standalone:

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install streamlit pandas plotly python-dotenv
```

### Verify Installation

Check that Streamlit is installed correctly:

```bash
streamlit --version
# Should output: Streamlit, version 1.32.0 (or higher)
```

## Configuration

The dashboard is configured using environment variables. You can set these in a `.env` file or export them directly.

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_TYPE=sqlite                              # Database type: "sqlite" or "postgresql"
SQLITE_PATH=llm_metrics.db                  # Path to SQLite database file

# PostgreSQL (if using DB_TYPE=postgresql)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DATABASE=llm_metrics
# POSTGRES_USER=your_username
# POSTGRES_PASSWORD=your_password

# Dashboard Configuration
DASHBOARD_TITLE=LLM Analytics Dashboard     # Dashboard page title
DASHBOARD_LAYOUT=wide                       # Layout: "wide" or "centered"
DASHBOARD_SIDEBAR=expanded                  # Sidebar: "expanded" or "collapsed"
DASHBOARD_THEME=light                       # Theme: "light" or "dark"

# Performance Configuration
CACHE_TTL=300                               # Cache TTL in seconds (default: 300)
MAX_ROWS_EXPORT=100000                      # Max rows for data export
```

### Database Setup

The dashboard expects a SQLite database with Langfuse export data containing the following tables:

- `generations`: LLM generation records with costs, tokens, and latency
- `traces`: Trace information including agent names and metadata

**Expected Schema:**

```sql
-- generations table
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
);

-- traces table
CREATE TABLE traces (
    id TEXT PRIMARY KEY,
    name TEXT,
    metadata TEXT
);
```

If you need to export data from Langfuse, refer to the Langfuse documentation for database export procedures.

## Usage

### Starting the Dashboard

Navigate to the project root and run:

```bash
# From project root
cd /path/to/MonolithicCoffeeMakerAgent

# Start the dashboard
streamlit run streamlit_apps/analytics_dashboard/app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`.

### Alternative Port

If port 8501 is in use:

```bash
streamlit run streamlit_apps/analytics_dashboard/app.py --server.port 8502
```

### Running in Background

To run the dashboard as a background service:

```bash
nohup streamlit run streamlit_apps/analytics_dashboard/app.py &
```

### Stopping the Dashboard

Press `Ctrl+C` in the terminal where the dashboard is running, or:

```bash
# Find the process
ps aux | grep streamlit

# Kill the process
kill <PID>
```

## Dashboard Pages

The dashboard consists of 5 main pages, each focusing on different aspects of LLM analytics:

### 1. 📈 Overview

**Purpose**: High-level view of your LLM usage and costs

**Features**:
- Key performance indicators (KPIs)
- Total cost, requests, and tokens
- Average latency
- Cost breakdown pie chart by model
- Daily cost trend line chart
- Token usage stacked bar chart

**Best For**: Quick health checks and daily monitoring

### 2. 💰 Cost Analysis

**Purpose**: Deep dive into cost patterns and budget tracking

**Features**:
- Budget tracking with progress bars
- Budget utilization warnings (75%, 90% thresholds)
- Hourly cost breakdown
- Most expensive requests (Top 20)
- 7-day cost forecast
- Peak hour identification

**Best For**: Budget management, cost optimization, and financial reporting

### 3. 🔍 Model Comparison

**Purpose**: Compare performance across different LLM models

**Features**:
- Side-by-side model performance metrics
- Cost per 1K tokens comparison
- Latency distribution box plots
- Request count comparisons
- Token efficiency analysis
- Cost vs performance trade-offs

**Best For**: Model selection, optimization decisions, and vendor comparisons

### 4. 🤖 Agent Performance

**Purpose**: Agent-specific analytics and usage patterns

**Features**:
- Per-agent cost breakdown
- Agent request counts and patterns
- Average latency by agent
- Token usage per agent
- Agent activity heatmaps
- Agent efficiency metrics

**Best For**: Monitoring autonomous agents, identifying heavy users, and workload distribution

### 5. 📥 Exports

**Purpose**: Download detailed reports for offline analysis

**Features**:
- CSV export with customizable date ranges
- PDF report generation (summary + charts)
- Raw data exports
- Filtered exports (by model, agent, etc.)
- Scheduled export options
- Download history tracking

**Best For**: Compliance reporting, stakeholder presentations, and external analysis

## Troubleshooting

### Common Issues

#### Issue: "Database not found" Error

**Error Message**: `FileNotFoundError: SQLite database not found: llm_metrics.db`

**Solutions**:
1. Verify the database file exists:
   ```bash
   ls -l llm_metrics.db
   ```
2. Check the `SQLITE_PATH` environment variable:
   ```bash
   echo $SQLITE_PATH
   ```
3. Use absolute path in `.env` file:
   ```bash
   SQLITE_PATH=/absolute/path/to/llm_metrics.db
   ```

#### Issue: Empty Dashboard / No Data

**Symptoms**: Dashboard loads but shows "No data available"

**Solutions**:
1. Check database has data:
   ```bash
   sqlite3 llm_metrics.db "SELECT COUNT(*) FROM generations;"
   ```
2. Verify date range filters aren't too restrictive
3. Click "Reset All Filters" in the sidebar
4. Check for data in the selected time range

#### Issue: Slow Performance

**Symptoms**: Pages take a long time to load

**Solutions**:
1. Increase cache TTL in `.env`:
   ```bash
   CACHE_TTL=600  # 10 minutes
   ```
2. Reduce date range in filters
3. Close other browser tabs
4. Clear Streamlit cache:
   ```bash
   rm -rf ~/.streamlit/cache
   ```
5. Restart the dashboard

#### Issue: Import Errors

**Error Message**: `ModuleNotFoundError: No module named 'streamlit'`

**Solutions**:
1. Verify virtual environment is activated
2. Reinstall dependencies:
   ```bash
   poetry install
   # OR
   pip install -r requirements.txt
   ```
3. Check Python version:
   ```bash
   python --version  # Should be 3.9+
   ```

#### Issue: Port Already in Use

**Error Message**: `Address already in use`

**Solutions**:
1. Use a different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```
2. Kill existing Streamlit process:
   ```bash
   pkill -f streamlit
   ```

### Debug Mode

Enable debug mode for more detailed error messages:

```bash
streamlit run streamlit_apps/analytics_dashboard/app.py --logger.level=debug
```

### Logs Location

Streamlit logs are located at:
- **macOS/Linux**: `~/.streamlit/logs/`
- **Windows**: `%USERPROFILE%\.streamlit\logs\`

## Screenshots

### Overview Page
*[Placeholder for screenshot showing the Overview page with KPIs, pie chart, and trend line]*

### Cost Analysis Page
*[Placeholder for screenshot showing budget tracking and cost forecasts]*

### Model Comparison Page
*[Placeholder for screenshot showing model performance comparison charts]*

### Agent Performance Page
*[Placeholder for screenshot showing agent-specific metrics and heatmaps]*

### Exports Page
*[Placeholder for screenshot showing export options and download interface]*

## FAQ

### Q: Can I use this dashboard with PostgreSQL instead of SQLite?

**A:** Yes! Set the following environment variables:

```bash
DB_TYPE=postgresql
POSTGRES_HOST=your-host
POSTGRES_PORT=5432
POSTGRES_DATABASE=llm_metrics
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

### Q: How often is the data refreshed?

**A:** Data is cached for 5 minutes by default (configurable via `CACHE_TTL`). You can force a refresh by clicking the "Refresh" button in the sidebar or reloading the page.

### Q: Can I customize the dashboard theme?

**A:** Yes! Streamlit supports custom themes. Create a `.streamlit/config.toml` file:

```toml
[theme]
primaryColor="#FF4B4B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
```

### Q: Does this work with other LLM providers besides OpenAI and Anthropic?

**A:** Yes! As long as the data follows the expected schema (generations and traces tables), it will work with any LLM provider.

### Q: Can I export data for specific time periods?

**A:** Yes! Use the date range filters in the sidebar, then navigate to the Exports page to download filtered data.

### Q: Is there authentication/access control?

**A:** The current version doesn't include built-in authentication. For production deployments, consider:
- Running behind a reverse proxy with authentication (nginx + basic auth)
- Using Streamlit Cloud with authentication
- Deploying with enterprise Streamlit features

### Q: Can I add custom metrics or pages?

**A:** Yes! See the [DEVELOPMENT.md](./DEVELOPMENT.md) file for instructions on extending the dashboard.

### Q: What's the maximum database size the dashboard can handle?

**A:** The dashboard has been tested with databases containing:
- **SQLite**: Up to 10GB (millions of records)
- **PostgreSQL**: Up to 100GB+

Performance depends on your system resources and caching configuration.

## Support

### Getting Help

1. **Documentation**: Start with this README and [DEVELOPMENT.md](./DEVELOPMENT.md)
2. **Issue Tracker**: Report bugs at [GitHub Issues](https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues)
3. **Discussions**: Ask questions in [GitHub Discussions](https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions)

### Reporting Bugs

When reporting bugs, please include:

1. **Dashboard version**: Check app.py for version number
2. **Python version**: `python --version`
3. **Streamlit version**: `streamlit --version`
4. **Error message**: Full error traceback
5. **Steps to reproduce**: How to trigger the issue
6. **Environment**: OS, database type, configuration

### Feature Requests

We welcome feature requests! Please:

1. Check existing issues first
2. Describe the use case
3. Explain expected behavior
4. Provide mockups if applicable

### Contributing

We welcome contributions! See [DEVELOPMENT.md](./DEVELOPMENT.md) for:

- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](../../LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Langfuse](https://langfuse.com/) analytics
- Charts created with [Plotly](https://plotly.com/python/)
- Part of the [MonolithicCoffeeMakerAgent](https://github.com/Bobain/MonolithicCoffeeMakerAgent) project

---

**Built with ❤️ by the MonolithicCoffeeMakerAgent Team**

For developer documentation, see [DEVELOPMENT.md](./DEVELOPMENT.md)
