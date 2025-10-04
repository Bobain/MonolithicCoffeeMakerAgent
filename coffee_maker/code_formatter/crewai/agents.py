"""CrewAI wrappers around the LangChain code formatter agents."""

from __future__ import annotations

import logging
from typing import Dict

from crewai import Agent, LLM
from dotenv import load_dotenv
from langfuse import Langfuse, observe

from coffee_maker.code_formatter import agents as lc_agents
from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI

load_dotenv()

logger = logging.getLogger(__name__)

Agent = observe(Agent)


_CREWAI_MODEL = f"gemini/{lc_agents.GEMINI_MODEL}"
llm = LLM(model=_CREWAI_MODEL, api_key=lc_agents.GEMINI_API_KEY)


def _wrap_langchain_agent(lc_agent: lc_agents.LangchainAgent) -> Agent:
    """Convert a LangChain agent specification into a CrewAI agent instance."""

    return Agent(
        role=lc_agent.role,
        goal=lc_agent.goal,
        backstory=lc_agent.backstory,
        tools=list(lc_agent.tools),
        allow_delegation=lc_agent.allow_delegation,
        verbose=lc_agent.verbose,
        llm=llm,
    )


@observe
def create_code_formatter_agents(langfuse_client: Langfuse) -> Dict[str, Agent]:
    """Return the CrewAI senior engineer agent."""

    lc_agent = lc_agents.create_langchain_code_formatter_agent(langfuse_client)
    crew_agent = _wrap_langchain_agent(lc_agent)

    logger.debug("Created senior_engineer_agent: %s", crew_agent)
    logger.info("Senior engineer agent created with goal: %s...", lc_agent.goal[:100])
    return {"senior_engineer": crew_agent}


@observe
def create_pr_reviewer_agent(
    langfuse_client: Langfuse, pr_number: int, repo_full_name: str, file_path: str
) -> Dict[str, Agent]:
    """Return the CrewAI GitHub reviewer agent."""

    logger.debug("Creating PR reviewer agent")
    tool_instance = PostSuggestionToolLangAI()

    lc_agent = lc_agents.create_langchain_pr_reviewer_agent(
        langfuse_client,
        pr_number=pr_number,
        repo_full_name=repo_full_name,
        file_path=file_path,
        tools=(tool_instance,),
    )

    crew_agent = _wrap_langchain_agent(lc_agent)
    logger.debug("Created PR reviewer agent")
    logger.info("PR reviewer agent created with %s tools", len(crew_agent.tools))
    return {"pull_request_reviewer": crew_agent}


__all__ = [
    "create_code_formatter_agents",
    "create_pr_reviewer_agent",
    "llm",
]
