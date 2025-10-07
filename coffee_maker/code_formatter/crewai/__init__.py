"""Code Formatter CrewAI Module.

This module contains the CrewAI-based implementation for automated code formatting and
review on GitHub pull requests. It uses multiple AI agents to analyze code, suggest
improvements, and post review comments directly on PRs.

The main components include definitions for agents and tasks, custom tools for posting
suggestions to GitHub, and the main orchestration logic for running the entire crew.

The system integrates with the GitHub API (via PyGithub) for PR operations, Langfuse for
prompt management and observability, Google Gemini for LLM capabilities, and CrewAI for
multi-agent orchestration.
"""
