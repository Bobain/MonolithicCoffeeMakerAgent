"""Agent Interaction Interface - Streamlit UI for Coffee Maker Agent.

This module provides an interactive chat interface for interacting with
Coffee Maker agents through a web-based UI built with Streamlit.

Features:
- Real-time chat interface with streaming responses
- Dynamic agent configuration (model, temperature, etc.)
- Conversation history and persistence
- Multiple agent support (code reviewer, architect, etc.)
- Live metrics display (tokens, cost, latency)
- Export conversations to various formats

Usage:
    # Run the Streamlit app
    streamlit run streamlit_apps/agent_interface/app.py

    # Or from the app directory
    cd streamlit_apps/agent_interface
    streamlit run app.py
"""

__version__ = "1.0.0"
