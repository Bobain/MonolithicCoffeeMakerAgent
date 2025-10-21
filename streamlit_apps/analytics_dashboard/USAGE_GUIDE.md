# LLM Analytics Dashboard - Usage Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-12

This guide provides step-by-step instructions for using the LLM Analytics Dashboard, including examples, common workflows, and best practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Dashboard Overview](#dashboard-overview)
- [Page-by-Page Guide](#page-by-page-guide)
  - [Overview Page](#1-overview-page)
  - [Cost Analysis](#2-cost-analysis)
  - [Model Comparison](#3-model-comparison)
  - [Agent Performance](#4-agent-performance)
  - [Exports](#5-exports)
- [Common Workflows](#common-workflows)
- [Best Practices](#best-practices)
- [Tips & Tricks](#tips--tricks)

---

## Quick Start

### 1. Prerequisites

Ensure you have:
- Python 3.9+ installed
- Project dependencies installed (`poetry install`)
- Database with LLM metrics data (`llm_metrics.db`)

### 2. Start the Dashboard

```bash
# From project root
cd /path/to/MonolithicCoffeeMakerAgent

# Start the dashboard
poetry run streamlit run streamlit_apps/analytics_dashboard/app.py

# Or with a custom port
poetry run streamlit run streamlit_apps/analytics_dashboard/app.py --server.port 8502
```

### 3. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8501
```

The dashboard will load with the home page showing quick stats and navigation options.

---

## Dashboard Overview

### Home Page

The home page provides:
- **Quick Stats** (sidebar): Total cost, requests, and tokens
- **Navigation Guide**: Links to all dashboard pages
- **Database Info**: Current database path and configuration
- **Getting Started**: Overview of features

### Sidebar Navigation

All pages are accessible via the sidebar:
- 📈 **Overview**: Global metrics and trends
- 💰 **Cost Analysis**: Detailed cost breakdown
- 🔍 **Model Comparison**: Compare model performance
- 🤖 **Agent Performance**: Agent-specific analytics
- 📥 **Exports**: Download reports and data

### Global Filters

Most pages include filters in the sidebar:
- **Date Range**: Select time period for analysis
- **Model Filter**: Filter by specific LLM models
- **Agent Filter**: Filter by agent name
- **Refresh Button**: Force data reload

---

## Page-by-Page Guide

### 1. Overview Page

**Purpose**: Get a high-level view of your LLM usage and costs.

#### Features

##### Key Metrics (Top Row)
Four main KPI cards:
- **Total Cost**: Cumulative spending in USD
- **Total Requests**: Number of LLM API calls
- **Total Tokens**: Sum of input + output tokens
- **Average Latency**: Mean response time in milliseconds

**Example Interpretation**:
```
Total Cost: $9.84
Total Requests: 201
Total Tokens: 746,378
Avg Latency: 3,245ms
```
This shows moderate usage with an average cost of ~$0.05 per request.

##### Cost Breakdown by Model (Pie Chart)
Visual representation of spending distribution across models.

**What to Look For**:
- Which model consumes most budget (largest slice)
- Underutilized models (small slices)
- Cost concentration (1-2 models vs. distributed)

##### Daily Cost Trend (Line Chart)
Time series of daily spending over the selected date range.

**What to Look For**:
- Spending trends (increasing, decreasing, stable)
- Anomalies (sudden spikes or drops)
- Patterns (weekday vs. weekend usage)

##### Token Usage by Model (Stacked Bar Chart)
Input and output tokens per model, stacked for comparison.

**What to Look For**:
- Token efficiency (output/input ratio)
- High token consumers
- Model usage patterns

#### Common Use Cases

**Daily Monitoring**:
1. Open Overview page
2. Check quick stats for anomalies
3. Review daily cost trend for unexpected spikes
4. Verify token usage is within expectations

**Weekly Review**:
1. Set date range to "Last 7 Days"
2. Compare cost breakdown week-over-week
3. Identify cost trends
4. Plan budget adjustments

---

### 2. Cost Analysis

**Purpose**: Deep dive into cost patterns, budget tracking, and spending optimization.

#### Features

##### Budget Tracking
Set and monitor spending against budget limits.

**How to Use**:
1. Enter your budget limit (e.g., $100.00)
2. View current spending progress bar
3. Monitor warning thresholds:
   - ⚠️ 75% utilization: Yellow warning
   - 🚨 90% utilization: Red alert

**Example**:
```
Budget: $100.00
Current: $9.84 (9.8% used)
Status: ✅ On Track
```

##### Hourly Cost Breakdown (Heatmap)
Visualize spending patterns by hour of day and day of week.

**What to Look For**:
- Peak usage hours (darkest cells)
- Off-hours activity
- Weekend vs. weekday patterns
- Potential optimization opportunities

**Example Insight**:
"Most requests occur 9am-5pm on weekdays, suggesting office hours usage. Consider rate limiting during off-hours."

##### Most Expensive Requests (Table)
Top 20 costliest individual LLM generations.

**Columns**:
- Timestamp
- Model
- Total Cost
- Input Tokens
- Output Tokens
- Latency

**Use Cases**:
- Identify outlier requests
- Find inefficient prompts
- Debug cost spikes

##### 7-Day Cost Forecast
Projected spending for next 7 days based on recent trends.

**Calculation**: Linear regression on last 14 days of data.

**Example**:
```
Projected 7-day cost: $23.45
Daily average: $3.35
Trend: Increasing (+15%)
```

#### Common Use Cases

**Budget Management**:
1. Set monthly budget at start of month
2. Check daily progress
3. Receive alerts at 75% and 90% thresholds
4. Adjust usage if needed

**Cost Investigation**:
1. Notice spike in daily cost trend
2. Navigate to Cost Analysis
3. Check hourly heatmap for time period
4. Review expensive requests table
5. Identify root cause (model, agent, prompt)

**Optimization Planning**:
1. Review 7-day forecast
2. Check budget remaining
3. Identify high-cost models in breakdown
4. Plan model migrations or prompt optimizations

---

### 3. Model Comparison

**Purpose**: Compare performance and costs across different LLM models to optimize selection.

#### Features

##### Side-by-Side Metrics (Cards)
For each model, view:
- Total requests
- Total cost
- Average latency
- Token efficiency (output/input ratio)

**Example Comparison**:
```
GPT-4                    Claude-3-Opus
Requests: 50            Requests: 30
Cost: $5.20             Cost: $3.15
Latency: 2,500ms        Latency: 1,800ms
Efficiency: 0.42        Efficiency: 0.38
```

**Interpretation**: GPT-4 is used more but Claude-3-Opus is faster and cheaper per request.

##### Cost per 1K Tokens (Bar Chart)
Compare pricing across models on a normalized basis.

**What to Look For**:
- Most cost-effective model
- Price-performance trade-offs
- Budget-friendly alternatives

**Example**:
```
gpt-3.5-turbo:    $0.002/1K tokens (cheapest)
claude-3-haiku:   $0.0004/1K tokens
gpt-4:            $0.045/1K tokens (most expensive)
```

##### Latency Distribution (Box Plot)
Visualize response time variability for each model.

**Components**:
- Median (line in box)
- 25th-75th percentile (box)
- Min-max (whiskers)
- Outliers (dots)

**What to Look For**:
- Consistent models (tight box)
- Variable models (wide box)
- Outliers (extreme latencies)

##### Request Count Comparison (Bar Chart)
See which models are used most frequently.

**Use Cases**:
- Identify primary models
- Spot underutilized models
- Plan capacity

#### Common Use Cases

**Model Selection**:
1. Review cost per 1K tokens chart
2. Check latency distribution box plot
3. Consider accuracy requirements
4. Choose optimal model for use case

**Migration Planning**:
1. Compare current model to alternatives
2. Analyze cost savings potential
3. Check latency impact
4. Test migration with small workload

**Performance Troubleshooting**:
1. Notice slow responses for specific model
2. Check latency distribution
3. Identify if issue is systemic or outliers
4. Investigate high latency requests

---

### 4. Agent Performance

**Purpose**: Monitor autonomous agents' performance, costs, and usage patterns.

#### Features

##### Per-Agent Cost Breakdown (Pie Chart)
Visualize spending distribution across agents.

**Example**:
```
code_developer: 45% ($4.40)
project_manager: 30% ($2.95)
assistant: 15% ($1.48)
spec_manager: 10% ($0.98)
```

**Use Cases**:
- Identify heavy users
- Balance workload
- Allocate budgets

##### Agent Request Counts (Bar Chart)
Compare request volumes across agents.

**What to Look For**:
- Active vs. idle agents
- Workload distribution
- Usage patterns

##### Average Latency by Agent (Bar Chart)
Compare response times for each agent.

**Use Cases**:
- Identify slow agents
- Diagnose performance issues
- Optimize agent configurations

##### Token Usage per Agent (Stacked Bar Chart)
Show input and output tokens for each agent.

**What to Look For**:
- Verbose agents (high output tokens)
- Efficient agents (low total tokens)
- Token usage patterns

##### Agent Activity Heatmap
Visualize when each agent is most active (day/hour).

**Use Cases**:
- Understand agent schedules
- Plan maintenance windows
- Optimize resource allocation

#### Common Use Cases

**Agent Monitoring**:
1. Review per-agent cost breakdown
2. Check for budget overruns
3. Verify expected usage patterns
4. Investigate anomalies

**Workload Balancing**:
1. Compare request counts across agents
2. Identify overloaded agents
3. Redistribute tasks if needed
4. Monitor latency impact

**Agent Optimization**:
1. Review token usage per agent
2. Identify verbose agents
3. Optimize prompts/instructions
4. Measure improvement

---

### 5. Exports

**Purpose**: Download detailed reports for offline analysis, compliance, or presentations.

#### Features

##### CSV Export
Download raw data in CSV format.

**Fields Included**:
- Timestamp
- Model
- Agent
- Input/Output Tokens
- Cost
- Latency

**How to Export**:
1. Select date range
2. Choose models/agents (optional filters)
3. Click "Download CSV"
4. Save file (e.g., `llm_metrics_2025-10-12.csv`)

**Use Cases**:
- Excel analysis
- Custom visualizations
- Data archiving
- Audit trails

##### PDF Report
Generate formatted PDF summary report.

**Contents**:
- Summary statistics
- Key charts (embedded)
- Top metrics
- Recommendations

**How to Export**:
1. Configure report parameters
2. Select date range
3. Click "Generate PDF Report"
4. Download file (e.g., `analytics_report_2025-10-12.pdf`)

**Use Cases**:
- Executive presentations
- Stakeholder updates
- Monthly reports
- Compliance documentation

##### Filtered Exports
Apply filters before exporting to download specific data subsets.

**Filter Options**:
- Date range
- Models
- Agents
- Cost thresholds
- Latency ranges

**Example Workflow**:
1. Filter to "Last 7 Days"
2. Select only "gpt-4" and "claude-3-opus"
3. Export CSV
4. Result: 7-day data for 2 models only

##### Scheduled Exports (Configuration)
Set up automatic daily/weekly exports (if enabled).

**Configuration**:
```python
# In config.py or .env
EXPORT_SCHEDULE=daily
EXPORT_FORMAT=csv
EXPORT_DESTINATION=/path/to/exports/
```

#### Common Use Cases

**Monthly Reporting**:
1. Set date range to "Last Month"
2. Generate PDF report
3. Review summary
4. Share with team

**Data Analysis**:
1. Export last 30 days to CSV
2. Import into Excel/Pandas
3. Perform custom analysis
4. Create additional visualizations

**Compliance Audit**:
1. Filter to audit period
2. Export full CSV
3. Include in compliance package
4. Archive for records

---

## Common Workflows

### Daily Health Check (5 minutes)

1. **Open Dashboard** → Navigate to `http://localhost:8501`
2. **Check Quick Stats** (sidebar)
   - Total cost today
   - Request count
   - Average latency
3. **Review Overview Page**
   - Daily cost trend (any spikes?)
   - Token usage (normal patterns?)
4. **Spot Check** (if needed)
   - Navigate to Cost Analysis for anomalies
   - Check Agent Performance for issues

### Weekly Budget Review (15 minutes)

1. **Set Date Range** → "Last 7 Days"
2. **Cost Analysis Page**
   - Review budget utilization
   - Check 7-day forecast
   - Analyze hourly heatmap
3. **Model Comparison Page**
   - Compare costs across models
   - Identify optimization opportunities
4. **Export Report**
   - Generate weekly PDF report
   - Save for records

### Model Optimization (30 minutes)

1. **Model Comparison Page**
   - Compare cost per 1K tokens
   - Review latency distributions
   - Check request counts
2. **Cost Analysis Page**
   - Find expensive requests
   - Identify target model
3. **Test Alternative**
   - Select cheaper/faster model
   - Run pilot test
4. **Monitor Results**
   - Compare performance
   - Measure cost savings
   - Decide on migration

### Agent Performance Investigation (20 minutes)

1. **Agent Performance Page**
   - Check per-agent cost breakdown
   - Review request counts
2. **Identify Issue**
   - High cost agent
   - Slow latency agent
   - Unusual pattern
3. **Root Cause Analysis**
   - Check token usage
   - Review activity heatmap
   - Examine specific requests
4. **Take Action**
   - Optimize prompts
   - Adjust agent configuration
   - Monitor improvement

---

## Best Practices

### Dashboard Usage

1. **Daily Monitoring**: Check quick stats and overview daily
2. **Weekly Reviews**: Deep dive into costs and performance weekly
3. **Monthly Reports**: Export PDF reports for stakeholders monthly
4. **Budget Alerts**: Set budget thresholds at 75% and 90%

### Data Hygiene

1. **Regular Exports**: Export data monthly for long-term analysis
2. **Archive Old Data**: Move old data out of active database
3. **Validate Data**: Spot check data quality periodically
4. **Backup Database**: Backup `llm_metrics.db` regularly

### Performance

1. **Use Filters**: Apply date/model filters to improve query speed
2. **Cache Settings**: Configure cache TTL based on update frequency
3. **Reasonable Date Ranges**: Avoid querying entire database at once
4. **Close Unused Tabs**: Free up browser memory

### Analysis

1. **Context Matters**: Compare metrics within similar time periods
2. **Look for Trends**: Focus on patterns, not single data points
3. **Investigate Outliers**: Understand extreme values
4. **Document Findings**: Keep notes on insights and decisions

---

## Tips & Tricks

### Keyboard Shortcuts

- `Ctrl+R` / `Cmd+R`: Refresh page
- `Ctrl+F` / `Cmd+F`: Search in tables
- `Esc`: Close modals/popups

### Chart Interactions

- **Hover**: See detailed values
- **Click Legend**: Toggle series on/off
- **Zoom**: Click and drag to zoom in
- **Pan**: Hold Shift and drag to pan
- **Reset**: Double-click to reset zoom

### Filter Combinations

**High-Cost Analysis**:
- Date: Last 30 days
- Model: gpt-4, claude-3-opus
- Sort: By cost (descending)

**Agent Comparison**:
- Date: Last 7 days
- Agent: All
- View: Side-by-side metrics

**Performance Troubleshooting**:
- Date: Last 24 hours
- Latency: >5000ms
- Sort: By timestamp

### Quick Actions

**Force Refresh**:
```
Sidebar → Refresh Button
```

**Reset All Filters**:
```
Sidebar → Reset Filters Button
```

**Download Current View**:
```
Exports Page → Current Filters → Download CSV
```

### Advanced Features

**Custom Date Ranges**:
1. Click "Custom" in date picker
2. Enter start and end dates
3. Apply filter

**Multi-Model Selection**:
1. Click model filter dropdown
2. Hold Ctrl/Cmd and click multiple models
3. Apply filter

**Comparative Analysis**:
1. Export data for Period A
2. Change date range to Period B
3. Export data for Period B
4. Compare in external tool

---

## Troubleshooting

### Dashboard Not Loading

**Issue**: Page loads but shows errors

**Solutions**:
1. Check database path in sidebar
2. Verify database file exists
3. Check browser console for errors
4. Try refreshing page (Ctrl+R)

### No Data Displayed

**Issue**: Dashboard loads but shows "No data available"

**Solutions**:
1. Check date range filters (might be too restrictive)
2. Reset all filters
3. Verify database has data:
   ```bash
   sqlite3 llm_metrics.db "SELECT COUNT(*) FROM generations;"
   ```
4. Check for data in selected time period

### Slow Performance

**Issue**: Pages take long time to load

**Solutions**:
1. Reduce date range
2. Apply model/agent filters
3. Increase cache TTL in config
4. Close other browser tabs
5. Restart dashboard

### Export Fails

**Issue**: CSV/PDF export doesn't download

**Solutions**:
1. Check browser download permissions
2. Verify disk space
3. Try smaller date range
4. Check browser console for errors
5. Try different browser

---

## Support

For additional help:
- **Documentation**: See [README.md](./README.md) and [DEVELOPMENT.md](./DEVELOPMENT.md)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions)

---

**Last Updated**: 2025-10-12
**Dashboard Version**: 1.0.0

For developer documentation, see [DEVELOPMENT.md](./DEVELOPMENT.md)
