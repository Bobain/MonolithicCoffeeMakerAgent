# ADR-001: Use Streamlit for Metrics Dashboard

## Status
Accepted

## Context
Need to create a metrics dashboard to visualize agent performance. Must be easy to develop, maintain, and deploy. Should integrate well with existing Python codebase.

## Decision
Use Streamlit for the metrics dashboard implementation. Streamlit provides:
- Pure Python (no HTML/CSS/JS needed)
- Built-in charting with Plotly/Altair
- Auto-refresh capabilities
- Simple deployment
- Good documentation and community support

## Consequences
Positive:
- Rapid development (Python only)
- Easy maintenance
- Good performance for dashboards
- Native data visualization support

Negative:
- Adds new dependency (streamlit + deps)
- Limited customization vs custom frontend
- Requires separate process to run

## Date
2025-10-15
