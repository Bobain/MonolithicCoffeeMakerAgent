# Error Monitoring Dashboard

Real-time error monitoring and analysis for LLM traces from Langfuse.

## Overview

The Error Monitoring Dashboard provides comprehensive error tracking, analysis, and alerting for LLM operations. It queries the Langfuse traces database (SQLite) to extract, categorize, and visualize errors with full context for debugging.

## Features

### 📊 Error Overview
- Real-time error metrics (total errors, error rate, critical errors)
- Severity distribution (CRITICAL, HIGH, MEDIUM, LOW)
- Error timeline visualization
- Top error types breakdown
- Errors by model analysis
- Recent errors table

### 🔍 Trace Explorer
- Search traces by ID, keywords, model
- Filter by date range, error type
- View full trace details with context
- Related traces discovery
- Export traces to JSON

### 📈 Error Trends
- Error frequency over time
- Error rate percentage trends
- Error type distribution
- Day-of-week and hour-of-day patterns
- Heatmap visualization

### 🤖 Model Failures
- Model failure rate comparison
- Model-specific error breakdown
- Common errors per model
- Cost impact analysis
- Model error trends

### 🔔 Alerts Configuration
- Active alerts display
- Configurable alert thresholds
- Alert rule management
- Alert history timeline
- Notification settings

## Installation

### Prerequisites

- Python 3.8+
- Streamlit
- SQLite database with Langfuse traces
- Dependencies in requirements.txt

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database path (optional):
```bash
export SQLITE_PATH="path/to/llm_metrics.db"
```

3. Run the dashboard:
```bash
streamlit run app.py
```

Or from project root:
```bash
cd /path/to/MonolithicCoffeeMakerAgent
streamlit run streamlit_apps/error_monitoring_dashboard/app.py
```

## Configuration

### Environment Variables

- `SQLITE_PATH`: Path to SQLite database (default: llm_metrics.db)
- `ERROR_DASHBOARD_TITLE`: Dashboard title (default: Error Monitoring Dashboard)
- `CACHE_TTL`: Cache TTL in seconds (default: 300)
- `ERROR_RATE_THRESHOLD`: Error rate threshold for alerts (default: 0.10 = 10%)
- `CRITICAL_ERROR_THRESHOLD`: Critical error count threshold (default: 5)

### Database Schema

The dashboard expects the following tables:

**traces**
- id, name, timestamp, metadata, status_message, input, output

**events**
- id, trace_id, timestamp, level, message, body

**generations**
- id, trace_id, model, model_parameters, prompt_tokens, completion_tokens, total_tokens, total_cost, latency_ms, created_at

## Architecture

```
streamlit_apps/error_monitoring_dashboard/
├── app.py                      # Main Streamlit app
├── config.py                   # Configuration management
├── pages/
│   ├── 01_error_overview.py    # Error metrics overview
│   ├── 02_trace_explorer.py    # Failed trace inspector
│   ├── 03_error_trends.py      # Temporal error analysis
│   ├── 04_model_failures.py    # Model-specific errors
│   └── 05_alerts_config.py     # Alert configuration
├── components/
│   ├── error_cards.py          # Error summary cards
│   ├── error_charts.py         # Error visualization charts
│   ├── trace_viewer.py         # Trace detail viewer
│   └── alert_widget.py         # Alert notification widget
├── queries/
│   ├── error_queries.py        # Error extraction from traces
│   └── trace_queries.py        # Trace detail queries
└── utils/
    ├── error_classifier.py     # Error categorization logic
    └── alert_manager.py        # Alert triggering logic
```

## Usage

### Running the Dashboard

```bash
streamlit run streamlit_apps/error_monitoring_dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Navigating Pages

Use the sidebar to navigate between pages:
1. **Error Overview** - Start here for high-level metrics
2. **Trace Explorer** - Investigate specific errors
3. **Error Trends** - Analyze patterns over time
4. **Model Failures** - Compare model reliability
5. **Alerts Config** - Set up proactive monitoring

### Filtering Data

All pages support filtering by:
- Date range (Last 24h, 7d, 30d, Custom)
- Model (filter by specific LLM model)
- Error type (RateLimitError, TimeoutError, etc.)
- Severity (CRITICAL, HIGH, MEDIUM, LOW)

### Exporting Data

Export functionality available on most pages:
- CSV exports for metrics and tables
- JSON exports for trace details
- Configurable export limits

## Error Classification

The dashboard automatically classifies errors into categories:

### Severity Levels
- **CRITICAL**: Service outages, authentication failures
- **HIGH**: Rate limits, timeouts, permission errors
- **MEDIUM**: Context length errors, invalid requests, content filters
- **LOW**: Minor warnings
- **UNKNOWN**: Unclassified errors

### Error Categories
- API Limits (rate limits, quota exceeded)
- Network (connection errors, timeouts)
- Input Validation (context length, invalid parameters)
- Request Validation (bad requests, invalid formats)
- Authentication (API key issues, unauthorized)
- Authorization (permission denied, forbidden)
- Configuration (model not found, invalid config)
- Service (service unavailable, server errors)
- Content Policy (content filters, safety)
- Other (unclassified)

## Alert System

### Alert Types

1. **High Error Rate**: Triggered when overall error rate exceeds threshold
2. **Critical Errors**: Triggered when critical error count exceeds threshold
3. **Model Degradation**: Triggered when model-specific error rate is high
4. **Error Spike**: Triggered when errors suddenly increase

### Configuring Alerts

Go to **Alerts Config** page to:
1. View active alerts
2. Adjust thresholds
3. Enable/disable alert rules
4. Configure notification channels
5. Test alerts

### Alert Thresholds (Defaults)

- Error rate: 10%
- Critical errors: 5 per hour
- Model error rate: 15%
- Check window: 1 hour

## Troubleshooting

### Database Not Found

```
❌ Database Error: SQLite database not found
```

**Solution**: Ensure the database path is correct and the file exists:
```bash
export SQLITE_PATH="/path/to/llm_metrics.db"
```

### No Data Displayed

**Possible causes**:
1. Database has no traces
2. No errors in selected date range
3. Filters are too restrictive

**Solution**: Check the database has data and adjust filters/date range.

### Slow Performance

**Possible causes**:
1. Large database (>1GB)
2. Long date ranges
3. Cache expired

**Solution**:
- Use shorter date ranges
- Clear cache (refresh button in sidebar)
- Increase `CACHE_TTL` environment variable

### Import Errors

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

### Project Structure

- `app.py`: Main entry point
- `config.py`: Configuration management
- `pages/`: Multi-page Streamlit pages
- `components/`: Reusable UI components
- `queries/`: Database query functions
- `utils/`: Utility functions

### Adding New Features

1. **New Query**: Add to `queries/error_queries.py` or `queries/trace_queries.py`
2. **New Component**: Add to `components/` directory
3. **New Page**: Add `0N_page_name.py` to `pages/` directory
4. **New Error Type**: Update `ErrorClassifier.ERROR_CATEGORIES` in `utils/error_classifier.py`

### Testing

```bash
# Test with sample database
export SQLITE_PATH="test_metrics.db"
streamlit run app.py
```

## Contributing

1. Follow existing code structure
2. Add docstrings to all functions
3. Use type hints
4. Cache query functions with `@st.cache_data(ttl=300)`
5. Handle errors gracefully

## License

Part of the MonolithicCoffeeMakerAgent project.

## Support

For issues or questions, refer to the main project documentation or create an issue in the repository.

## Version

**v1.0.0** - Initial release with full error monitoring capabilities.
