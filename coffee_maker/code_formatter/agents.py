"""LangChain agent helpers for the code formatter domain.

The functions in this module return light-weight dictionaries describing the
agents that participate in the formatter workflow.  They intentionally mirror
the data the CrewAI wrappers expect (role/goal/backstory/tools/etc.) so we keep
all prompt wiring in one place while avoiding duplication across integrations.
"""

import logging
import os
from typing import Any, Dict, Optional, Sequence

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse, observe

load_dotenv()

LOGGER = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.0-flash-lite"

MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


_GEMINI_API_KEY = os.environ["GOOGLE_API_KEY"]
llm = observe(
    ChatGoogleGenerativeAI(
        model=_GEMINI_MODEL,
        google_api_key=_GEMINI_API_KEY,
        convert_system_message_to_human=True,
    )
)


def _build_prompt(system_message: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([("system", system_message), ("user", "{input}")])


def _build_agent_config(
    *,
    role: str,
    goal: str,
    backstory: str,
    prompt: ChatPromptTemplate,
    llm_override: Optional[ChatGoogleGenerativeAI] = None,
    tools: Sequence[Any] = (),
    verbose: bool = True,
    allow_delegation: bool = False,
) -> Dict[str, Any]:
    return {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "prompt": prompt,
        "llm": llm_override or llm,
        "tools": tuple(tools),
        "verbose": verbose,
        "allow_delegation": allow_delegation,
    }


def create_langchain_code_formatter_agent(
    langfuse_client: Langfuse, *, llm_override: Optional[ChatGoogleGenerativeAI] = None
) -> Dict[str, Any]:
    """Return the LangChain configuration for the formatter agent."""

    try:
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as exc:  # pragma: no cover - surfaced to callers/tests
        LOGGER.exception("Failed to fetch formatter prompts", exc_info=exc)
        raise

    goal = getattr(goal_prompt, "prompt", str(goal_prompt))
    backstory = getattr(backstory_prompt, "prompt", str(backstory_prompt))
    prompt = _build_prompt("a meticulous Senior Software Engineer", goal, backstory)

    return _build_agent_config(
        role="Senior Software Engineer: python code formatter",
        goal=goal,
        backstory=backstory,
        prompt=prompt,
        llm_override=llm_override,
        tools=(),
    )


# """
# Agent Definitions for Code Formatter CrewAI System.
#
# This module defines the AI agents used in the code formatting and review workflow.
# Each agent has a specific role and capabilities, working together to analyze and
# improve code quality in pull requests.
#
# Module-level Variables:
#     llm: Google Gemini LLM instance used by all agents
#
# Functions:
#     create_code_formatter_agents: Creates the senior engineer agent for code refactoring
#     create_pr_reviewer_agent: Creates the GitHub reviewer agent for posting suggestions
# """
#
# import logging
# import os
#
# from crewai import Agent, LLM
# from dotenv import load_dotenv
#
# load_dotenv()
#
# logger = logging.getLogger(__name__)
#
# from langfuse import Langfuse, observe
# from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI
#
#
# def _resolve_gemini_api_key() -> str:
#     """Locate a Gemini-compatible API key and expose it for LiteLLM calls."""
#
#     for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"):
#         key = os.getenv(env_name)
#         if key:
#             os.environ.setdefault("GEMINI_API_KEY", key)
#             return key
#
#     raise RuntimeError("Gemini API key missing: set GEMINI_API_KEY, GOOGLE_API_KEY, or COFFEE_MAKER_GEMINI_API_KEY.")
#
#
# _GEMINI_API_KEY = _resolve_gemini_api_key()
# _GEMINI_MODEL = "gemini/gemini-2.0-flash-lite"
#
#
# # --- LLM Configuration ---
# llm = LLM(model=_GEMINI_MODEL, api_key=_GEMINI_API_KEY)
#
#
# @observe
# def create_code_formatter_agents(langfuse_client: Langfuse) -> dict[str, Agent]:
#     """
#     Creates the agent responsible for analyzing and refactoring code.
#
#     This function creates a senior engineer agent that analyzes code files and
#     suggests improvements based on best practices and style guidelines. The agent's
#     goal and backstory are fetched from Langfuse prompts for easy version control
#     and experimentation.
#
#     Args:
#         langfuse_client (Langfuse): Initialized Langfuse client for fetching prompts
#
#     Returns:
#         dict: Dictionary with key "senior_engineer" mapping to the Agent instance
#
#     Raises:
#         Exception: If prompts cannot be fetched from Langfuse
#
#     Example:
#         >>> from langfuse import Langfuse
#         >>> langfuse = Langfuse(...)
#         >>> agents = create_code_formatter_agents(langfuse)
#         >>> senior_agent = agents["senior_engineer"]
#     """
#     try:
#         goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
#         backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
#     except Exception as e:
#         print(f"ERROR: Could not fetch prompts from Langfuse. Details: {e}")
#         raise
#
#     senior_engineer_agent = Agent(
#         role="Senior Software Engineer",
#         goal=goal_prompt.prompt,
#         backstory=backstory_prompt.prompt,
#         tools=[],  # no tools for this agent
#         allow_delegation=False,
#         verbose=True,
#         llm=llm,
#     )
#     logger.debug(f"Created senior_engineer_agent: {senior_engineer_agent}")
#     logger.info(f"Senior engineer agent created with goal: {goal_prompt.prompt[:100]}...")
#     return {"senior_engineer": senior_engineer_agent}
#
#
# @observe
# def create_pr_reviewer_agent(langfuse_client: Langfuse) -> dict[str, Agent]:
# def create_pr_reviewer_agent(
#     langfuse_client: Langfuse, pr_number: int, repo_full_name: str, file_path: str
# ) -> dict[str, Agent]:
#     """
#     Creates the agent responsible for posting review suggestions on GitHub.
#
#     This function creates a GitHub code reviewer agent that takes refactored code
#     suggestions and posts them as review comments on pull requests using GitHub's
#     suggestion feature. The agent uses the PostSuggestionToolLangAI tool to
#     interact with the GitHub API.
#
#     Args:
#         langfuse_client (Langfuse): Initialized Langfuse client (not currently used
#             but kept for consistency with create_code_formatter_agents)
#
#     Returns:
#         dict: Dictionary with key "pull_request_reviewer" mapping to the Agent instance
#
#     Example:
#         >>> from langfuse import Langfuse
#         >>> langfuse = Langfuse(...)
#         >>> agents = create_pr_reviewer_agent(langfuse)
#         >>> reviewer = agents["pull_request_reviewer"]
#
#     Note:
#         The agent has access to PostSuggestionToolLangAI which requires GITHUB_TOKEN
#         environment variable to be set with appropriate permissions.
#     """
#     logger.debug("Creating PR reviewer agent")
#     tool = PostSuggestionToolLangAI()
#
#     agent = {
#         "pull_request_reviewer": Agent(
#             role="GitHub Code Reviewer",
#             goal=f"""You will be given as input a string formatted in a given STRUCTURE which list and explains
#             changes that should be suggested on the pull request review,
#             you should post suggestions in a commit in github to reflect these suggested changes.
#
#             Your input is a string which indicates which
#
#             The structure of your input is a string with this STRUCTURE:
#             ---
#             {langfuse_client.get_prompt("reformatted_code_file_template")}
#             ---
#
#             To post suggested changes to:
#             you are equipped with a tool to post suggestions commits with a comment that explains the change.
#             This tool should be used with the following inputs:
#             ---
#             repo_full_name: {repo_full_name}
#             pr_number: {pr_number}
#             file_path: {file_path}
#             ---
#
#             for each code change (suggestion in github given in your input string) you should post a suggestion
#             commit in the Pull Request review with a comment that match the explanation (given in your input string)
#
#             By parsing the Input string you will find the other inputs needed to use your tool:
#             start_line:int      The line at which the suggested commit should start (see in EXPLANATIONS block of your input string)
#             "end_line":         The line at which the suggested commit should end (see in EXPLANATIONS block of your input string)
#             "suggestion_body"   The suggested code (see in the CODE_MODIFIED block of your input string)
#             "comment_text":     The explanations for code change (see in EXPLANATIONS block of your input string)
#
#             """,
#             backstory="",
#             tools=[tool],
#             allow_delegation=False,
#             verbose=True,
#             llm=llm,
#         )
#     }
#     logger.debug("Created PR reviewer agent")
#     logger.info(f"PR reviewer agent created with {len(agent['pull_request_reviewer'].tools)} tools")
#     return agent


# def create_langchain_pr_reviewer_agent(
#     langfuse_client: Langfuse,
#     *,
#     pr_number: int,
#     repo_full_name: str,
#     file_path: str,
#     llm_override: Optional[ChatGoogleGenerativeAI] = None,
#     tools: Sequence[Any] = (),
# ) -> Dict[str, Any]:
#     """Return the LangChain configuration for the reviewer agent."""
#
#     template_prompt = langfuse_client.get_prompt("reformatted_code_file_template")
#     template_body = getattr(template_prompt, "prompt", str(template_prompt))
#
#     goal = "Translate formatter output into actionable GitHub suggestions."
#     backstory = (
#         "You automate GitHub reviews, ensuring suggestions reference the style guide "
#         "and match the formatter's recommendations."
#     )
#     system_message = (
#         "You are GitHub Code Reviewer.\n\n"
#         "You receive structured formatter output. For each suggested change, post a GitHub "
#         "suggestion comment using the equipped tools.\n\n"
#         f"Target repository: {repo_full_name}.\n"
#         f"Pull request number: {pr_number}.\n"
#         f"File under review: {file_path}.\n\n"
#         "Structured input template:\n---\n"
#         f"{template_body}\n---\n"
#         "Ensure explanations reference the style guide when available."
#     )
#     prompt = ChatPromptTemplate.from_messages([("system", system_message), ("user", "{input}")])
#
#     return _build_agent_config(
#         role="GitHub Code Reviewer",
#         goal=goal,
#         backstory=backstory,
#         prompt=prompt,
#         llm_override=llm_override,
#         tools=tools,
#     )
#
#
# GEMINI_MODEL = _GEMINI_MODEL
# GEMINI_API_KEY = _GEMINI_API_KEY
#
# __all__ = [
#     "GEMINI_API_KEY",
#     "GEMINI_MODEL",
#     "create_langchain_code_formatter_agent",
#     "create_langchain_pr_reviewer_agent",
#     "llm",
#     "_resolve_gemini_api_key",
# ]
