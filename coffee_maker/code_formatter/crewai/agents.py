"""
Agent Definitions for Code Formatter CrewAI System.

This module defines the AI agents used in the code formatting and review workflow.
Each agent has a specific role and capabilities, working together to analyze and
improve code quality in pull requests.

Module-level Variables:
    llm: Google Gemini LLM instance used by all agents

Functions:
    create_code_formatter_agents: Creates the senior engineer agent for code refactoring
    create_pr_reviewer_agent: Creates the GitHub reviewer agent for posting suggestions
"""

import logging
import os

from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

from langfuse import Langfuse, observe
from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI


def _resolve_gemini_api_key() -> str:
    """Locate a Gemini-compatible API key and expose it for LiteLLM calls."""

    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"):
        key = os.getenv(env_name)
        if key:
            os.environ.setdefault("GEMINI_API_KEY", key)
            return key

    raise RuntimeError("Gemini API key missing: set GEMINI_API_KEY, GOOGLE_API_KEY, or COFFEE_MAKER_GEMINI_API_KEY.")


_GEMINI_API_KEY = _resolve_gemini_api_key()
_GEMINI_MODEL = "gemini/gemini-2.0-flash-lite"


# --- LLM Configuration ---
llm = LLM(model=_GEMINI_MODEL, api_key=_GEMINI_API_KEY)


@observe
def create_code_formatter_agents(langfuse_client: Langfuse) -> dict[str, Agent]:
    """
    Creates the agent responsible for analyzing and refactoring code.

    This function creates a senior engineer agent that analyzes code files and
    suggests improvements based on best practices and style guidelines. The agent's
    goal and backstory are fetched from Langfuse prompts for easy version control
    and experimentation.

    Args:
        langfuse_client (Langfuse): Initialized Langfuse client for fetching prompts

    Returns:
        dict: Dictionary with key "senior_engineer" mapping to the Agent instance

    Raises:
        Exception: If prompts cannot be fetched from Langfuse

    Example:
        >>> from langfuse import Langfuse
        >>> langfuse = Langfuse(...)
        >>> agents = create_code_formatter_agents(langfuse)
        >>> senior_agent = agents["senior_engineer"]
    """
    try:
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as e:
        print(f"ERROR: Could not fetch prompts from Langfuse. Details: {e}")
        raise

    senior_engineer_agent = Agent(
        role="Senior Software Engineer",
        goal=goal_prompt.prompt,
        backstory=backstory_prompt.prompt,
        tools=[],  # no tools for this agent
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )
    logger.debug(f"Created senior_engineer_agent: {senior_engineer_agent}")
    logger.info(f"Senior engineer agent created with goal: {goal_prompt.prompt[:100]}...")
    return {"senior_engineer": senior_engineer_agent}


@observe
def create_pr_reviewer_agent(langfuse_client: Langfuse) -> dict[str, Agent]:
    """
    Creates the agent responsible for posting review suggestions on GitHub.

    This function creates a GitHub code reviewer agent that takes refactored code
    suggestions and posts them as review comments on pull requests using GitHub's
    suggestion feature. The agent uses the PostSuggestionToolLangAI tool to
    interact with the GitHub API.

    Args:
        langfuse_client (Langfuse): Initialized Langfuse client (not currently used
            but kept for consistency with create_code_formatter_agents)

    Returns:
        dict: Dictionary with key "pull_request_reviewer" mapping to the Agent instance

    Example:
        >>> from langfuse import Langfuse
        >>> langfuse = Langfuse(...)
        >>> agents = create_pr_reviewer_agent(langfuse)
        >>> reviewer = agents["pull_request_reviewer"]

    Note:
        The agent has access to PostSuggestionToolLangAI which requires GITHUB_TOKEN
        environment variable to be set with appropriate permissions.
    """
    logger.debug("Creating PR reviewer agent")
    tool = PostSuggestionToolLangAI()

    langfuse_client.get_prompt("reformatted_code_file_template")

    agent = {
        "pull_request_reviewer": Agent(
            role="GitHub Code Reviewer",
            goal=f"""Take as input a string formatted in a given STRUCTURE,
            and post suggestions in a commit in github to reflect these suggested changes.

            To post suggestions in a github review you are equipped with a tool that works this way :
            ---
            {tool._run.__doc__}
            ---

            The structure of your input is the same as the output of another agent which was told to output a string with this STRUCTURE:
            ---
            {langfuse_client.get_prompt("reformatted_code_file_template")}
            ---
            """,
            backstory="",
            tools=[tool],
            allow_delegation=False,
            verbose=True,
            llm=llm,
        )
    }
    logger.debug("Created PR reviewer agent")
    logger.info(f"PR reviewer agent created with {len(agent['pull_request_reviewer'].tools)} tools")
    return agent
