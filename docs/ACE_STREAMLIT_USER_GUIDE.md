# ACE Streamlit App - User Guide

## Overview

The ACE Streamlit App provides a visual interface for managing and monitoring the **ACE (Agentic Context Engineering)** framework. This web application allows you to configure agent settings, monitor real-time executions, manage playbook bullets, and analyze system performance.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Navigation](#navigation)
3. [Pages](#pages)
   - [Home Dashboard](#home-dashboard)
   - [Configuration Page](#configuration-page)
   - [Monitor Page](#monitor-page)
   - [Playbooks Page](#playbooks-page)
   - [Analytics Dashboard](#analytics-dashboard)
4. [Common Workflows](#common-workflows)
5. [FAQ](#faq)
6. [Troubleshooting](#troubleshooting)
7. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### Installation

Ensure you have the project installed with all dependencies:

```bash
poetry install
```

### Launching the App

Start the Streamlit app using the CLI command:

```bash
poetry run ace-ui
```

Or directly with Streamlit:

```bash
streamlit run coffee_maker/streamlit_app/app.py
```

The app will automatically open in your default browser at `http://localhost:8501`.

### System Requirements

- **Python**: 3.11+
- **Poetry**: For dependency management
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Screen Resolution**: Minimum 1280x720 (responsive design supports mobile)

---

## Navigation

The app uses a **sidebar navigation** system:

- **🏠 Home**: Overview and quick statistics
- **⚙️ Configuration**: Configure ACE settings per agent *(Phase 1 - Coming Soon)*
- **📊 Monitor**: Real-time execution trace monitoring *(Phase 2 - Complete)*
- **📚 Playbooks**: Interactive playbook management *(Phase 3 - Complete)*
- **📈 Analytics**: Performance insights and analytics *(Phase 4 - Complete)*

Use the sidebar to switch between pages. Each page is independently navigable.

---

## Pages

### Home Dashboard

**Purpose**: High-level overview of the ACE system

**Features**:
- **Quick Status Metrics**:
  - Active Agents: Number of agents with ACE enabled
  - Traces Today: Total executions in the last 24 hours
  - Success Rate: Percentage of successful executions
- **Navigation Links**: Quick access to all sections
- **System Information**: About ACE framework

**How to Use**:
1. Launch the app
2. View quick status metrics at the top
3. Click navigation links in the sidebar

![Home Dashboard Example](screenshots/home_dashboard.png) *(screenshot would go here)*

---

### Configuration Page

**Status**: Phase 1 - Coming Soon

**Purpose**: Configure ACE settings for individual agents

**Planned Features**:
- Toggle ACE on/off per agent
- Adjust dual execution threshold
- Set trace storage location
- Configure playbook settings
- Batch configuration updates

**How to Use** *(when available)*:
1. Go to **Configuration** page from sidebar
2. Select an agent from the dropdown
3. Use toggle switches to enable/disable ACE
4. Adjust settings in the forms
5. Click **Save Configuration**

---

### Monitor Page

**Status**: Phase 2 - Complete ✅

**Purpose**: Real-time monitoring of agent executions

**Features**:
- **Live Trace Feed**: Auto-refreshes every 5 seconds (optional)
- **Filters**: By agent, time range (1h, 6h, 24h, 7d)
- **Quick Stats**: Total traces, success count, failure count, avg duration
- **Detailed Trace View**: Expand any trace to see full JSON
- **Agent Performance Dashboard**: Success rates per agent with visual indicators

**How to Use**:

1. Navigate to **📊 Monitor** from the sidebar
2. **Select Time Range**: Choose from Last Hour, 6 Hours, 24 Hours, or Last Week
3. **Filter by Agent** (optional): Select specific agent or "All"
4. **Enable Auto-Refresh**: Check the "Auto-refresh (5s)" box for real-time updates
5. **View Traces**: Scroll through the live feed
   - ✅ Green = Success
   - ❌ Red = Failure
   - ⚠️ Gray = Unknown
6. **Expand Trace Details**: Click "View Details" to see full execution data
7. **Check Agent Performance**: Scroll down to see per-agent success rates

**Use Cases**:
- Debug failing executions
- Monitor system health in real-time
- Identify slow-performing agents
- Track execution patterns

![Monitor Page Example](screenshots/monitor_page.png) *(screenshot would go here)*

---

### Playbooks Page

**Status**: Phase 3 - Complete ✅

**Purpose**: Manage and curate playbook bullets for each agent

**Features**:
- **Browse Bullets**: View all playbook bullets (150+ across agents)
- **Search & Filter**:
  - Search by content (full-text)
  - Filter by category, status, effectiveness range
  - Sort by effectiveness or date added
- **Bullet Actions**:
  - Approve ✅ - Mark bullet as active
  - Reject ❌ - Archive bullet
  - Bulk Actions - Process multiple bullets at once
- **Visualizations**:
  - Category Distribution (pie chart)
  - Effectiveness Distribution (histogram)
  - Status Breakdown (bar chart)
- **Curation Queue**: Quick access to pending bullets

**How to Use**:

1. Navigate to **📚 Playbooks** from the sidebar
2. **Select Agent**: Choose which agent's playbook to manage
3. **Apply Filters**:
   - Category: Filter by specific topics
   - Status: Active, Pending, or Archived
   - Effectiveness Range: Use slider to filter by score (0.0-1.0)
4. **Search**: Type keywords to find specific bullets
5. **Sort Results**: Choose sorting method (effectiveness or date)
6. **Review Bullets**:
   - 🟢 Green = High effectiveness (≥0.7)
   - 🟡 Yellow = Medium effectiveness (0.3-0.7)
   - 🔴 Red = Low effectiveness (<0.3)
   - ✅ Active | ⏳ Pending | 🗄️ Archived
7. **Take Action**:
   - **Individual**: Click "Approve" or "Reject" within each bullet
   - **Bulk**: Enable bulk mode, select multiple bullets, then use bulk buttons
8. **View Analytics**: Check tabs for category distribution, effectiveness, and status
9. **Process Curation Queue**: Quickly approve/reject pending bullets at the bottom

**Use Cases**:
- Curate high-quality playbook content
- Identify low-performing bullets to reject
- Review pending bullets awaiting approval
- Analyze playbook health by category
- Bulk-approve similar bullets

![Playbooks Page Example](screenshots/playbooks_page.png) *(screenshot would go here)*

---

### Analytics Dashboard

**Status**: Phase 4 - Complete ✅

**Purpose**: Comprehensive performance analytics and insights

**Features**:
- **Executive Summary**: Total traces, cost, avg effectiveness, top agent
- **Cost Analytics**:
  - Total cost, avg cost per trace
  - Cost distribution by agent (pie chart)
  - Daily cost trend (line chart)
- **Effectiveness Analytics**:
  - Success rate, error rate, avg effectiveness
  - Problem areas detection (agents with effectiveness < 70%)
  - Effectiveness by agent (horizontal bar chart)
  - Effectiveness trend over time
- **Performance Analytics**:
  - Avg duration, avg tokens, optimization opportunities
  - Duration by agent (bar chart)
  - Token usage by agent (bar chart)
  - Slowest operations table
- **Recommendations**: Actionable insights based on data
- **Advanced Analytics**:
  - Cost vs Effectiveness scatter plot (quadrant analysis)
  - Agent performance heatmap (normalized metrics)

**How to Use**:

1. Navigate to **📈 Analytics** from the sidebar
2. **Adjust Time Range**: Use sidebar slider (7-90 days, default: 30)
3. **Filter by Agent** (optional): Select specific agent or "All Agents"
4. **Review Executive Summary**:
   - Key metrics at the top
   - Key insights (💡) below metrics
5. **Explore Cost Analytics**:
   - Check total cost and trends
   - Identify most expensive agents
   - Review daily cost trends for patterns
6. **Analyze Effectiveness**:
   - Monitor success/error rates
   - Review problem areas (if any)
   - Check effectiveness by agent
   - Track trends over time
7. **Optimize Performance**:
   - Review avg duration and token usage
   - Identify slowest operations
   - Read optimization opportunities
8. **Follow Recommendations**: Implement actionable suggestions
9. **Advanced Analysis** (expand section):
   - Quadrant analysis: Find high-value, low-cost agents
   - Heatmap: Compare all metrics across agents

**Interpreting Charts**:
- **Green**: Good/high values
- **Yellow/Orange**: Medium/warning
- **Red**: Poor/needs attention
- **Dashed Lines**: Targets or averages

**Use Cases**:
- Monthly performance reviews
- Cost optimization
- Identify underperforming agents
- Track improvement over time
- Justify resource allocation

![Analytics Dashboard Example](screenshots/analytics_dashboard.png) *(screenshot would go here)*

---

## Common Workflows

### Workflow 1: Daily Monitoring

**Goal**: Check system health each morning

1. Open app → Home page
2. Check Quick Status metrics
3. Navigate to Monitor page
4. Select "Last 24 Hours"
5. Review traces for failures
6. Check Agent Performance section
7. If issues found → investigate trace details

**Time**: 2-3 minutes

---

### Workflow 2: Weekly Playbook Curation

**Goal**: Review and curate pending bullets

1. Navigate to Playbooks page
2. Select agent (start with most active)
3. Set Status filter to "Pending"
4. Sort by "Effectiveness (High to Low)"
5. Approve high-effectiveness bullets (🟢)
6. Review low-effectiveness bullets (🔴) - consider rejecting
7. Process Curation Queue at bottom
8. Repeat for each agent

**Time**: 10-15 minutes per agent

---

### Workflow 3: Monthly Performance Review

**Goal**: Analyze system performance and optimize

1. Navigate to Analytics Dashboard
2. Set time range to 30 days
3. Review Executive Summary:
   - Note total traces and cost
   - Read key insights
4. Cost Analytics:
   - Check for cost spikes in daily trend
   - Identify expensive agents
5. Effectiveness Analytics:
   - Review problem areas
   - Check trends - improving or declining?
6. Performance Analytics:
   - Note optimization opportunities
   - Review slowest operations
7. Read Recommendations section
8. Implement top 3 recommendations
9. Advanced Analytics:
   - Quadrant analysis: focus on bottom-right (low eff, high cost)
10. Document findings and actions taken

**Time**: 30-45 minutes

---

### Workflow 4: Debugging a Failing Agent

**Goal**: Investigate why an agent is failing

1. Navigate to Monitor page
2. Filter by specific agent
3. Set time range to "Last 24 Hours"
4. Look for ❌ failures in Live Trace Feed
5. Click "View Details" on failed trace
6. Examine:
   - `user_query`: What was the input?
   - `executions[].result_status`: Where did it fail?
   - `executions[].output`: Error messages?
7. Navigate to Playbooks page
8. Search for related bullets (use keywords from query)
9. Check effectiveness of relevant bullets
10. If bullet effectiveness is low → consider rejecting or updating
11. Navigate to Analytics → Effectiveness Analytics
12. Check if this agent is in "Problem Areas"
13. Read recommendations for this agent
14. Take action (update prompts, adjust playbook, etc.)

**Time**: 15-20 minutes

---

## FAQ

### Q: How do I enable ACE for all agents?

**A**: Configuration page (Phase 1) is coming soon. For now, ACE is enabled via code configuration in `coffee_maker/autonomous/ace/config.py`.

---

### Q: Why don't I see any traces on the Monitor page?

**A**: Possible reasons:
1. You haven't run the daemon yet → Run `poetry run code-developer --auto-approve`
2. ACE is not enabled for agents → Check your ACE configuration
3. Time range is too narrow → Try "Last 24 Hours" or "Last Week"
4. Traces directory is empty → Check `docs/generator/traces/`

---

### Q: How do I export analytics data?

**A**: For charts:
1. Hover over any chart
2. Click the camera icon (top-right of chart) to download as PNG
3. Or use the menu (three dots) for more export options (CSV, SVG, etc.)

For raw data:
- Currently, raw data export is not implemented (coming in future update)

---

### Q: What does "effectiveness score" mean?

**A**: Effectiveness is a measure of how well a playbook bullet improves agent performance:
- **0.0-0.3** (🔴): Low effectiveness, consider rejecting
- **0.3-0.7** (🟡): Medium effectiveness, monitor performance
- **0.7-1.0** (🟢): High effectiveness, keep and promote

Calculated based on:
- Success rate when bullet is used
- User satisfaction (if available)
- Task completion time improvements

---

### Q: Can I use the app on mobile?

**A**: Yes! The app uses responsive design and works on tablets and smartphones. However, for the best experience (especially for analytics charts), we recommend:
- Desktop: 1920x1080 or higher
- Laptop: 1366x768 or higher
- Tablet: 768x1024 (portrait or landscape)
- Mobile: 375x667 (basic navigation, limited chart interaction)

---

### Q: How often should I curate playbooks?

**A**: Recommended schedule:
- **Daily**: Check Curation Queue (5 minutes)
- **Weekly**: Review pending bullets per agent (10-15 minutes per agent)
- **Monthly**: Deep review of all bullets, especially low-effectiveness ones (1-2 hours)

---

### Q: What's the difference between Monitor and Analytics?

**A**:
- **Monitor**: Real-time, trace-level detail, operational monitoring, debugging
- **Analytics**: Historical trends, aggregated metrics, strategic insights, optimization

Use Monitor for "What's happening NOW?" and Analytics for "How are we doing OVER TIME?"

---

## Troubleshooting

### Issue: App won't start

**Symptoms**: Command hangs or shows error

**Solutions**:
1. Check that port 8501 is available:
   ```bash
   lsof -i :8501  # On macOS/Linux
   ```
   Kill the process if port is in use
2. Verify poetry environment:
   ```bash
   poetry shell
   poetry install
   ```
3. Try running with debug logging:
   ```bash
   streamlit run coffee_maker/streamlit_app/app.py --logger.level=debug
   ```
4. Check for missing dependencies:
   ```bash
   poetry show | grep streamlit
   poetry show | grep plotly
   ```

---

### Issue: No data showing on any page

**Symptoms**: Empty states, "No data available" messages

**Solutions**:
1. Verify ACE is enabled:
   - Check Configuration page (when available)
   - Or check `coffee_maker/autonomous/ace/config.py`
2. Run the daemon to generate traces:
   ```bash
   poetry run code-developer --auto-approve
   ```
3. Check trace directory exists and has files:
   ```bash
   ls -la docs/generator/traces/
   ```
4. Verify API is working:
   ```bash
   python -c "from coffee_maker.autonomous.ace.api import ACEAPI; api = ACEAPI(); print(api.get_agent_status())"
   ```

---

### Issue: Charts not rendering

**Symptoms**: Blank spaces where charts should be

**Solutions**:
1. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)
2. Try a different browser (Chrome recommended)
3. Check JavaScript console for errors (F12 → Console tab)
4. Update Plotly:
   ```bash
   poetry update plotly
   ```
5. Restart the Streamlit server

---

### Issue: "Failed to load" error messages

**Symptoms**: Red error boxes on pages

**Solutions**:
1. Check the error message details (click to expand)
2. Verify data files exist:
   ```bash
   ls docs/generator/traces/
   ls docs/reflector/deltas/
   ls docs/curator/playbooks/
   ```
3. Check file permissions:
   ```bash
   chmod -R 755 docs/
   ```
4. Try restarting the app
5. If persistent, check logs:
   ```bash
   streamlit run coffee_maker/streamlit_app/app.py --logger.level=error
   ```

---

### Issue: App is slow

**Symptoms**: Pages take >10 seconds to load

**Solutions**:
1. Reduce time range in Analytics (use 7-30 days instead of 90)
2. Filter by specific agent instead of "All"
3. Clear old trace files:
   ```bash
   # Backup first!
   tar -czf traces_backup_$(date +%Y%m%d).tar.gz docs/generator/traces/
   # Delete traces older than 90 days
   find docs/generator/traces/ -name "*.json" -mtime +90 -delete
   ```
4. Check system resources (CPU, RAM):
   ```bash
   top  # or htop on Linux
   ```
5. Consider upgrading hardware or increasing available memory

---

## Tips & Best Practices

### Performance Tips

1. **Use Filters**: Always filter by agent or time range when dealing with large datasets
2. **Auto-Refresh Wisely**: Enable auto-refresh only when actively monitoring (it uses resources)
3. **Limit Bulk Actions**: Process <100 bullets at once to avoid timeouts
4. **Close Unused Tabs**: Only keep the current page open in your browser
5. **Periodic Cleanup**: Archive old traces regularly to keep the app fast

### Curation Best Practices

1. **Regular Reviews**: Daily quick checks + weekly deep reviews
2. **Effectiveness Threshold**:
   - Approve bullets with ≥0.7 effectiveness immediately
   - Monitor bullets with 0.3-0.7 effectiveness
   - Reject bullets with <0.3 effectiveness after review
3. **Category Balance**: Ensure playbooks have diverse categories (not all in one category)
4. **Bulk Actions**: Use bulk approve for similar high-quality bullets (saves time)
5. **Document Decisions**: Use metadata or external notes to track why bullets were rejected

### Monitoring Best Practices

1. **Set Up Alerts**: (Future feature) Configure email/Slack alerts for high error rates
2. **Daily Check-Ins**: Spend 2-3 minutes each morning reviewing traces
3. **Track Trends**: Use Analytics Dashboard to identify patterns over time
4. **Investigate Failures Immediately**: Don't let failures accumulate
5. **Baseline Metrics**: Establish normal success rates per agent (e.g., code_developer should be >90%)

### Analytics Best Practices

1. **Monthly Reviews**: Schedule regular performance reviews
2. **Compare Periods**: Look at 30-day trends vs. 90-day trends
3. **Focus on ROI**: Use Cost vs Effectiveness quadrant to optimize spending
4. **Implement Recommendations**: Act on at least the top 3 recommendations each month
5. **Share Insights**: Export charts and share with team/stakeholders

### Security Best Practices

1. **Access Control**: (Future feature) Limit who can approve/reject bullets
2. **Audit Trail**: (Future feature) Track who made changes
3. **Backup Data**: Regularly backup traces, playbooks, and configurations
4. **Review Sensitive Data**: Ensure traces don't contain secrets or PII
5. **Update Regularly**: Keep dependencies up to date for security patches

---

## Support & Resources

### Documentation

- **Technical Spec**: `docs/STREAMLIT_ACE_APP_SPEC.md`
- **Project Instructions**: `.claude/CLAUDE.md`
- **ACE Framework Docs**: `docs/ACE_*.md`

### Getting Help

1. Check this User Guide first
2. Review Troubleshooting section
3. Check FAQ
4. Run diagnostics:
   ```bash
   poetry run ace-ui --help
   ```
5. Open an issue on GitHub (if applicable)

### Version

- **Current Version**: 1.0.0 (Phase 5 - Complete)
- **Last Updated**: 2025-10-15
- **Changelog**: See `docs/STREAMLIT_ACE_APP_SPEC.md`

---

## Conclusion

The ACE Streamlit App provides a powerful, user-friendly interface for managing the ACE framework. By following this guide and the best practices outlined, you'll be able to:

- ✅ Monitor agent executions in real-time
- ✅ Curate high-quality playbook content
- ✅ Analyze performance and optimize costs
- ✅ Maintain system health proactively

**Happy monitoring!** 🚀

---

**Feedback**: Have suggestions or found a bug? Please open an issue or contribute to the docs!
