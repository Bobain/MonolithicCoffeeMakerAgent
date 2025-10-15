"""Project Coordinator - Unified agent combining assistant + project_manager.

This module merges the functionality of assistant and project_manager into a single
agent with internal routing. This eliminates user confusion (which agent to call?)
and reduces system complexity while maintaining all capabilities.

Capabilities:
- Documentation expertise (from assistant)
- Strategic planning and ROADMAP management (from project_manager)
- GitHub monitoring (PRs, issues, CI/CD)
- Intelligent dispatch to specialized agents
- Project status analysis and recommendations

Usage:
    >>> from coffee_maker.cli.project_coordinator import ProjectCoordinator
    >>>
    >>> coordinator = ProjectCoordinator()
    >>> response = coordinator.process_request(
    ...     user_input="What's the status of the roadmap?",
    ...     context={'roadmap_summary': summary},
    ...     history=[]
    ... )
    >>> print(response.message)
"""

import logging
from typing import Dict, List

from coffee_maker.cli.ai_service import AIService
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

logger = logging.getLogger(__name__)


class QueryMode:
    """Query mode constants for internal routing."""

    ROADMAP = "roadmap"  # ROADMAP management queries
    GITHUB = "github"  # GitHub monitoring queries
    DOCUMENTATION = "documentation"  # Documentation questions
    GENERAL = "general"  # General assistance


class ProjectCoordinator(AIService):
    """Unified agent combining assistant + project_manager capabilities.

    This agent provides:
    - Documentation expertise (reads all docs, answers questions)
    - Strategic planning (ROADMAP management, prioritization)
    - GitHub monitoring (PRs, issues, CI/CD status)
    - Intelligent routing to specialized agents

    Internal routing automatically determines which "mode" to use based on
    the user's query, eliminating the need for separate assistant/project_manager
    entry points.

    Example:
        >>> coordinator = ProjectCoordinator()
        >>>
        >>> # ROADMAP query (project_manager mode)
        >>> response = coordinator.process_request(
        ...     "What's the status of PRIORITY 5?",
        ...     context={'roadmap_summary': summary},
        ...     history=[]
        ... )
        >>>
        >>> # Documentation query (assistant mode)
        >>> response = coordinator.process_request(
        ...     "How does the ACE framework work?",
        ...     context={},
        ...     history=[]
        ... )
        >>>
        >>> # GitHub query
        >>> response = coordinator.process_request(
        ...     "What's the status of our PRs?",
        ...     context={},
        ...     history=[]
        ... )
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4000,
        use_claude_cli: bool = False,
        claude_cli_path: str = "/opt/homebrew/bin/claude",
    ):
        """Initialize project coordinator.

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens per response
            use_claude_cli: If True, use Claude CLI instead of API
            claude_cli_path: Path to claude CLI executable
        """
        super().__init__(
            model=model, max_tokens=max_tokens, use_claude_cli=use_claude_cli, claude_cli_path=claude_cli_path
        )
        logger.info("ProjectCoordinator initialized (merged assistant + project_manager)")

    def classify_query_mode(self, user_input: str) -> str:
        """Classify user query to determine which mode to use.

        Args:
            user_input: User's natural language input

        Returns:
            Query mode (roadmap, github, documentation, general)

        Example:
            >>> coordinator = ProjectCoordinator()
            >>> mode = coordinator.classify_query_mode("What's the status of the roadmap?")
            >>> print(mode)
            'roadmap'
        """
        lower_input = user_input.lower()

        # ROADMAP queries
        roadmap_keywords = [
            "roadmap",
            "priority",
            "priorities",
            "what should we work on",
            "what's next",
            "backlog",
            "planned",
            "in progress",
            "completed",
            "milestone",
        ]
        if any(kw in lower_input for kw in roadmap_keywords):
            logger.debug("Query classified as: roadmap")
            return QueryMode.ROADMAP

        # GitHub queries
        github_keywords = [
            "pull request",
            "pr",
            "github",
            "issue",
            "ci/cd",
            "build status",
            "test status",
            "deployment",
        ]
        if any(kw in lower_input for kw in github_keywords):
            logger.debug("Query classified as: github")
            return QueryMode.GITHUB

        # Documentation queries
        doc_keywords = [
            "how does",
            "how do",
            "what is",
            "explain",
            "documentation",
            "docs",
            "where is",
            "how to",
            "tutorial",
            "guide",
            "ace framework",
            "architecture",
        ]
        if any(kw in lower_input for kw in doc_keywords):
            logger.debug("Query classified as: documentation")
            return QueryMode.DOCUMENTATION

        # Default: general assistance
        logger.debug("Query classified as: general")
        return QueryMode.GENERAL

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with internal routing based on query context.

        Overrides AIService._build_system_prompt to provide mode-aware prompts.

        Args:
            context: Context dictionary with:
                - roadmap_summary: ROADMAP data (for roadmap mode)
                - query_mode: Detected query mode (roadmap, github, docs, general)

        Returns:
            System prompt string customized for the detected mode
        """
        query_mode = context.get("query_mode", QueryMode.GENERAL)

        if query_mode == QueryMode.ROADMAP:
            # Use project_manager prompt with ROADMAP context
            return self._build_roadmap_prompt(context)
        elif query_mode == QueryMode.GITHUB:
            # Use github monitoring prompt
            return self._build_github_prompt(context)
        elif query_mode == QueryMode.DOCUMENTATION:
            # Use assistant/documentation expert prompt
            return self._build_documentation_prompt(context)
        else:
            # General assistance prompt
            return self._build_general_prompt(context)

    def _build_roadmap_prompt(self, context: Dict) -> str:
        """Build ROADMAP management prompt (project_manager mode).

        Args:
            context: Context with roadmap_summary

        Returns:
            System prompt for ROADMAP queries
        """
        roadmap_summary = context.get("roadmap_summary", {})

        total = roadmap_summary.get("total", 0)
        completed = roadmap_summary.get("completed", 0)
        in_progress = roadmap_summary.get("in_progress", 0)
        planned = roadmap_summary.get("planned", 0)

        # Build priority list
        priorities = roadmap_summary.get("priorities", [])
        priority_list = ""
        if priorities:
            for p in priorities[:10]:  # Limit to first 10
                priority_list += f"- {p['number']}: {p['title']} ({p['status']})\n"

        # Load centralized project_manager prompt
        prompt = load_prompt(
            PromptNames.AGENT_PROJECT_MANAGER,
            {
                "TOTAL_PRIORITIES": str(total),
                "COMPLETED_PRIORITIES": str(completed),
                "IN_PROGRESS_PRIORITIES": str(in_progress),
                "PLANNED_PRIORITIES": str(planned),
                "PRIORITY_LIST": priority_list or "No priorities currently listed.",
            },
        )

        return prompt

    def _build_github_prompt(self, context: Dict) -> str:
        """Build GitHub monitoring prompt.

        Args:
            context: Context with optional github data

        Returns:
            System prompt for GitHub queries
        """
        # For now, use general prompt with GitHub focus
        # TODO: Create dedicated .claude/commands/agent-github-monitor.md
        base_prompt = """You are project_coordinator in GitHub monitoring mode.

Your role is to monitor and report on:
- Pull requests (status, reviews, CI/CD)
- GitHub issues (open, closed, assigned)
- Build and test status
- Deployment status

You have access to GitHub CLI (gh command) to query information.

Be concise and focus on actionable information. Highlight blockers and items
requiring attention.
"""
        return base_prompt

    def _build_documentation_prompt(self, context: Dict) -> str:
        """Build documentation expert prompt (assistant mode).

        Args:
            context: Context dictionary

        Returns:
            System prompt for documentation queries
        """
        base_prompt = """You are project_coordinator in documentation expert mode.

Your role is to:
- Have profound knowledge of ALL project documentation
- Keep ROADMAP.md in great detail in mind
- Answer questions about the codebase, architecture, and processes
- Explain how systems work
- Provide tutorials and guides
- Delegate complex tasks to appropriate specialized agents

You are READ-ONLY - you do not modify code or documents. You help users understand
the system and route them to the right agent for implementation.

Key documentation to be familiar with:
- docs/roadmap/ROADMAP.md - Master task list
- docs/PRIORITY_*_TECHNICAL_SPEC.md - Feature specifications
- .claude/CLAUDE.md - Project instructions
- docs/DOCUMENT_OWNERSHIP_MATRIX.md - Agent responsibilities

Be helpful, concise, and always suggest which agent can help if the user needs
implementation work done.
"""
        return base_prompt

    def _build_general_prompt(self, context: Dict) -> str:
        """Build general assistance prompt.

        Args:
            context: Context dictionary

        Returns:
            System prompt for general queries
        """
        base_prompt = """You are project_coordinator, a unified agent combining:
- Documentation expertise (assistant capabilities)
- Strategic planning and ROADMAP management (project_manager capabilities)
- GitHub monitoring
- Intelligent dispatch to specialized agents

Your role is to help users with whatever they need:
- Answer questions about the project
- Provide ROADMAP status and planning
- Monitor GitHub activity
- Route complex tasks to appropriate agents

You are versatile and adaptive. Determine what the user needs and provide
helpful, concise responses.
"""
        return base_prompt

    def process_request(self, user_input: str, context: Dict, history: List[Dict], stream: bool = True):
        """Process user request with automatic mode detection.

        Overrides AIService.process_request to add automatic query classification.

        Args:
            user_input: User's natural language input
            context: Current context (roadmap_summary, etc.)
            history: Conversation history
            stream: If True, returns a streaming response

        Returns:
            AIResponse with message and optional action

        Example:
            >>> coordinator = ProjectCoordinator()
            >>> response = coordinator.process_request(
            ...     "What's the status of PRIORITY 5?",
            ...     context={'roadmap_summary': summary},
            ...     history=[]
            ... )
            >>> print(response.message)
        """
        # Classify query mode for internal routing
        query_mode = self.classify_query_mode(user_input)

        # Add query_mode to context for _build_system_prompt
        context_with_mode = {**context, "query_mode": query_mode}

        # Call parent process_request with enriched context
        return super().process_request(user_input, context_with_mode, history, stream)

    def process_request_stream(self, user_input: str, context: Dict, history: List[Dict]):
        """Process user request with streaming and automatic mode detection.

        Args:
            user_input: User's natural language input
            context: Current context
            history: Conversation history

        Yields:
            Text chunks as they arrive from Claude API

        Example:
            >>> coordinator = ProjectCoordinator()
            >>> for chunk in coordinator.process_request_stream("Hello", context, []):
            ...     print(chunk, end="")
        """
        # Classify query mode for internal routing
        query_mode = self.classify_query_mode(user_input)

        # Add query_mode to context
        context_with_mode = {**context, "query_mode": query_mode}

        # Call parent process_request_stream with enriched context
        yield from super().process_request_stream(user_input, context_with_mode, history)
