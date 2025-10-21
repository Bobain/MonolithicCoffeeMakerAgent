# ACE Tutorial Screenshots

This directory is reserved for screenshots and visual assets for the ACE Console Demo Tutorial.

## Planned Screenshots

Future screenshots to be added when using Puppeteer MCP for visual documentation:

1. `ace_ui_home.png` - ACE Streamlit UI home dashboard
2. `ace_ui_monitor.png` - Monitor page with real-time traces
3. `ace_ui_analytics.png` - Analytics dashboard
4. `delegation_trace_example.png` - Example delegation trace visualization
5. `database_query_example.png` - SQLite query results

## Creating Screenshots

Use Puppeteer MCP tools to capture screenshots:

```bash
poetry run ace-ui  # Start the app
# Then use puppeteer_navigate and puppeteer_screenshot
```

See `docs/WORKFLOWS.md` for Puppeteer MCP workflow.
