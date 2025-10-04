"""LangChain-native agent definitions for the code formatter domain.

This module centralises the shared agent configuration used across the code
formatter tooling.  It exposes light-weight LangChain agent primitives that can
be wrapped by different orchestration layers (e.g. CrewAI) without duplicating
goal/backstory/LLM definitions in every integration.

Key design goals:
    * Match the behaviour of the existing CrewAI agents so downstream
      components can keep their expectations.
    * Remain agnostic of CrewAI; the types defined here operate purely with
      LangChain primitives.
    * Keep the surface area small: a thin dataclass holds the descriptive
      fields while also providing a helper to build a runnable chain when
      needed.

The module currently defines two agents:
    * Senior Software Engineer – analyses and reformats code according to the
      style guide.
    * GitHub Code Reviewer – turns structured formatter output into GitHub PR
      suggestions via the configured tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os
from typing import Any, Callable, Dict, Optional, Sequence

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse

load_dotenv()

logger = logging.getLogger(__name__)


def _resolve_gemini_api_key() -> str:
    """Locate a usable Gemini API key for the LangChain chat model.

    Preference order mirrors the CrewAI integration to avoid surprises.  As a
    side-effect the resolved key is mirrored to ``GEMINI_API_KEY`` so any
    downstream libraries that rely on that specific variable keep working.
    """

    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"):
        value = os.getenv(env_name)
        if value:
            os.environ.setdefault("GEMINI_API_KEY", value)
            return value

    raise RuntimeError("Gemini API key missing: set GEMINI_API_KEY, GOOGLE_API_KEY, or " "COFFEE_MAKER_GEMINI_API_KEY.")


_GEMINI_API_KEY = _resolve_gemini_api_key()
_GEMINI_MODEL = "gemini-2.0-flash-lite"


def _build_default_llm() -> ChatGoogleGenerativeAI:
    """Create the shared LangChain chat model instance."""

    # ``convert_system_message_to_human`` keeps compatibility with prompts that
    # rely on system messages – it mirrors CrewAI's ability to pass long-form
    # instructions as system context.
    return ChatGoogleGenerativeAI(
        model=_GEMINI_MODEL,
        google_api_key=_GEMINI_API_KEY,
        convert_system_message_to_human=True,
    )


llm: ChatGoogleGenerativeAI = _build_default_llm()


def _default_prompt(role: str, goal: str, backstory: str) -> ChatPromptTemplate:
    """Compose a generic system prompt for the LangChain agent."""

    system_message = (
        f"You are {role}.\n\n"
        f"Primary goal:\n{goal.strip()}\n\n"
        f"Backstory:\n{backstory.strip()}\n\n"
        "Respond with actionable suggestions while following project style guides."
    )

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", "{input}"),
        ]
    )


@dataclass(slots=True)
class LangchainAgent:
    """Simple container describing a LangChain agent configuration."""

    role: str
    goal: str
    backstory: str
    prompt: ChatPromptTemplate
    llm: BaseChatModel
    tools: Sequence[Any] = field(default_factory=tuple)
    verbose: bool = True
    allow_delegation: bool = False

    def as_runnable(self) -> Runnable[Dict[str, Any], Any]:
        """Return a runnable chain representing the agent."""

        return self.prompt | self.llm

    def with_tools(self, *tool_factories: Callable[[], Any]) -> "LangchainAgent":
        """Clone the agent and append the provided tool instances."""

        instantiated = list(self.tools)
        for factory in tool_factories:
            instantiated.append(factory())
        return LangchainAgent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            prompt=self.prompt,
            llm=self.llm,
            tools=tuple(instantiated),
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
        )


def create_langchain_code_formatter_agent(
    langfuse_client: Langfuse, *, llm_override: Optional[BaseChatModel] = None
) -> LangchainAgent:
    """Create the LangChain representation of the senior engineer agent."""

    try:
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as exc:  # pragma: no cover - surfaced to caller/tests
        logger.exception("Failed to retrieve Langfuse prompts for formatter agent")
        raise

    goal = getattr(goal_prompt, "prompt", str(goal_prompt))
    backstory = getattr(backstory_prompt, "prompt", str(backstory_prompt))

    prompt = _default_prompt("a meticulous Senior Software Engineer", goal, backstory)

    return LangchainAgent(
        role="Senior Software Engineer",
        goal=goal,
        backstory=backstory,
        prompt=prompt,
        llm=llm_override or llm,
        tools=(),
        verbose=True,
        allow_delegation=False,
    )


def create_langchain_pr_reviewer_agent(
    langfuse_client: Langfuse,
    *,
    pr_number: int,
    repo_full_name: str,
    file_path: str,
    llm_override: Optional[BaseChatModel] = None,
    tools: Optional[Sequence[Any]] = None,
) -> LangchainAgent:
    """Create the LangChain representation of the GitHub reviewer agent."""

    template_prompt = langfuse_client.get_prompt("reformatted_code_file_template")
    template_body = getattr(template_prompt, "prompt", str(template_prompt))

    goal = "You translate structured formatter output into actionable GitHub PR " "suggestions."
    backstory = (
        "You are a thorough GitHub reviewer. Use the provided template to post "
        "code suggestions that match the formatter's recommended changes."
    )

    system_message = (
        f"You are GitHub Code Reviewer.\n\n"
        "You receive well-structured formatter output. For each suggested change, "
        "post a GitHub suggestion comment using the equipped tools.\n\n"
        f"Target repository: {repo_full_name}.\n"
        f"Pull request number: {pr_number}.\n"
        f"File under review: {file_path}.\n\n"
        "Structured input template:\n---\n"
        f"{template_body}\n---\n"
        "Ensure explanations reference the style guide when available."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", "{input}"),
        ]
    )

    return LangchainAgent(
        role="GitHub Code Reviewer",
        goal=goal,
        backstory=backstory,
        prompt=prompt,
        llm=llm_override or llm,
        tools=tuple(tools or ()),
        verbose=True,
        allow_delegation=False,
    )


GEMINI_MODEL = _GEMINI_MODEL
GEMINI_API_KEY = _GEMINI_API_KEY

__all__ = [
    "LangchainAgent",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "create_langchain_code_formatter_agent",
    "create_langchain_pr_reviewer_agent",
    "llm",
]
