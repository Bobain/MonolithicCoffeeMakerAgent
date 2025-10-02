"""
Code Formatter CrewAI Module.

This module contains the CrewAI-based implementation for automated code formatting
and review on GitHub pull requests. It uses multiple AI agents to analyze code,
suggest improvements, and post review comments directly on PRs.

Main Components:
    - agents: AI agent definitions for code refactoring and PR reviewing
    - tasks: Task definitions for the agent workflow
    - tools: Custom tools for posting suggestions to GitHub
    - main: Orchestration logic for running the entire crew

The system integrates with:
    - GitHub API (via PyGithub) for PR operations
    - Langfuse for prompt management and observability
    - Google Gemini for LLM capabilities
    - CrewAI for multi-agent orchestration
"""
