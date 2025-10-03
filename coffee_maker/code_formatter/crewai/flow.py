"""Flow definitions for the Code Formatter CrewAI system.

This module provides a Flow-based orchestration that mirrors the behaviour of
``coffee_maker/code_formatter/crewai/tasks.py`` while leveraging the new
CrewAI Flow API. Rather than returning individual ``Task`` instances, the
flow coordinates the same prompt preparation and agent execution steps using
@start/@listen decorators. This keeps the business logic identical but allows
consumers to run the formatter+review pipeline as an executable flow.
"""

from __future__ import annotations

import logging
from typing import Any

from crewai import Agent
from crewai.flow import Flow, listen, start
from langfuse import Langfuse, observe
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI

MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"

_REFORMAT_EXPECTED_OUTPUT = (
    "A string containing the code given as input with some formatting suggestions "
    "annotated in code blocks (with given delimiters as explained in YOUR RESPONSE STRUCUTURE), "
    "as well as short explanation for each"
)


class CodeFormatterFlowState(BaseModel):
    """Mutable state shared across flow steps."""

    file_path: str = Field(default="", description="Path of the file being processed")
    repo_full_name: str = Field(default="", description="GitHub repository full name")
    pr_number: int = Field(default=0, description="Pull request number associated with the run")
    file_content: str = Field(default="", description="Original content of the file under review")

    reformat_prompt: str | None = Field(default=None, description="Compiled prompt for the formatter agent")
    reformat_expected_output: str | None = Field(default=None, description="Expected formatter output description")
    reformat_result: str | None = Field(default=None, description="Raw formatter agent response")

    review_prompt: str | None = Field(default=None, description="Compiled prompt for the reviewer agent")
    review_expected_output: str | None = Field(default=None, description="Expected reviewer output description")
    review_result: str | None = Field(default=None, description="Raw reviewer agent response")


class CodeFormatterFlow(Flow[CodeFormatterFlowState]):
    """Flow orchestrating formatter and reviewer agents for a single file."""

    def __init__(
        self,
        formatter_agent: Agent,
        reviewer_agent: Agent,
        langfuse_client: Any,
        *,
        file_path: str,
        repo_full_name: str,
        pr_number: int,
        file_content: str,
        raise_on_reviewer_failure: bool = True,
    ) -> None:
        super().__init__(
            file_path=file_path,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_content=file_content,
        )
        self.formatter_agent = formatter_agent
        self.reviewer_agent = reviewer_agent
        self.langfuse_client = langfuse_client
        self.raise_on_reviewer_failure = raise_on_reviewer_failure
        self._ensure_reviewer_tool()

    def _ensure_reviewer_tool(self) -> None:
        """Attach GitHub suggestion tool to reviewer agent when missing."""
        tools = list(self.reviewer_agent.tools or [])
        for tool in tools:
            if isinstance(tool, PostSuggestionToolLangAI):
                return
        tools.append(PostSuggestionToolLangAI())
        self.reviewer_agent.tools = tools

    @start()
    @observe
    def compile_reformat_prompt(self) -> str:
        """Compile the formatter task prompt using Langfuse templates."""
        logger.debug("Compiling formatter prompt for %s", self.state.file_path)
        prompt = self.langfuse_client.get_prompt("code_formatter_main_llm_entry")
        compiled_prompt = prompt.compile(
            filename=self.state.file_path,
            file_content=self.state.file_content,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )
        self.state.reformat_prompt = compiled_prompt
        self.state.reformat_expected_output = _REFORMAT_EXPECTED_OUTPUT
        logger.info("Formatter prompt compiled for %s", self.state.file_path)
        return compiled_prompt

    @listen(compile_reformat_prompt)
    @observe
    def run_formatter_agent(self, compiled_prompt: str) -> str:
        """Execute the formatter agent and persist its raw output in state."""
        logger.debug("Running formatter agent for %s", self.state.file_path)
        result = self.formatter_agent.kickoff(compiled_prompt)
        raw_output = getattr(result, "raw", result)
        if not isinstance(raw_output, str):
            raw_output = str(raw_output)
        self.state.reformat_result = raw_output
        logger.info(
            "Formatter agent completed for %s with %d characters",
            self.state.file_path,
            len(raw_output) if isinstance(raw_output, str) else 0,
        )
        return raw_output

    @listen(run_formatter_agent)
    @observe
    def run_reviewer_agent(self, refactor_output: str) -> str:
        """Compile the reviewer prompt, execute the reviewer agent, and store its output."""
        logger.debug(
            "Running reviewer agent for %s targeting %s PR #%s",
            self.state.file_path,
            self.state.repo_full_name,
            self.state.pr_number,
        )
        prompt = self.langfuse_client.get_prompt("pr_reviewer_task")
        compiled_prompt = prompt.compile(
            file_path=self.state.file_path,
            repo_full_name=self.state.repo_full_name,
            pr_number=self.state.pr_number,
            MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
            MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
            EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
        )
        expected_output = (
            f"A confirmation message stating that each suggestions for {self.state.file_path} "
            "has been successfully posted to GitHub : 'OK'. "
            "Or : 'KO\n#... explanations about what went wrong ..."
        )
        self.state.review_prompt = compiled_prompt
        self.state.review_expected_output = expected_output

        messages = [
            {"role": "system", "content": compiled_prompt},
            {"role": "user", "content": refactor_output},
        ]
        try:
            result = self.reviewer_agent.kickoff(messages)
        except Exception as exc:  # pragma: no cover - network/tool failures
            logger.error("Reviewer agent execution failed", exc_info=True)
            error_msg = f"Reviewer agent failed: {exc}"
            self.state.review_result = error_msg
            if self.raise_on_reviewer_failure:
                raise
            return error_msg
        raw_output = getattr(result, "raw", result)
        if not isinstance(raw_output, str):
            raw_output = str(raw_output)
        self.state.review_result = raw_output
        logger.info("Reviewer agent completed for %s", self.state.file_path)
        return raw_output


def create_code_formatter_flow(
    formatter_agent: Agent,
    reviewer_agent: Agent,
    langfuse_client: Any,
    *,
    file_path: str,
    repo_full_name: str,
    pr_number: int,
    file_content: str,
    raise_on_reviewer_failure: bool = True,
) -> CodeFormatterFlow:
    """Helper factory mirroring the task module helpers but returning a Flow."""
    return CodeFormatterFlow(
        formatter_agent=formatter_agent,
        reviewer_agent=reviewer_agent,
        langfuse_client=langfuse_client,
        file_path=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        file_content=file_content,
        raise_on_reviewer_failure=raise_on_reviewer_failure,
    )


def kickoff_code_formatter_flow(
    formatter_agent: Agent,
    reviewer_agent: Agent,
    langfuse_client: Any,
    *,
    file_path: str,
    repo_full_name: str,
    pr_number: int,
    file_content: str,
    raise_on_reviewer_failure: bool = True,
) -> CodeFormatterFlow:
    """Convenience helper that creates and immediately runs the flow."""
    flow = create_code_formatter_flow(
        formatter_agent=formatter_agent,
        reviewer_agent=reviewer_agent,
        langfuse_client=langfuse_client,
        file_path=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        file_content=file_content,
        raise_on_reviewer_failure=raise_on_reviewer_failure,
    )
    flow.kickoff()
    return flow


if __name__ == "__main__":
    import argparse
    import os
    from pathlib import Path

    from coffee_maker.code_formatter.crewai.agents import (
        create_code_formatter_agents,
        create_pr_reviewer_agent,
    )

    parser = argparse.ArgumentParser(description="Run the formatter/reviewer flow on a sample snippet")
    parser.add_argument(
        "--path",
        help="Optional path to a file containing the snippet to process",
    )
    parser.add_argument(
        "--text",
        help="Inline code snippet. Overrides --path when provided.",
    )
    args = parser.parse_args()

    snippet: str | None = None
    if args.text:
        snippet = args.text
    elif args.path:
        snippet = Path(args.path).read_text(encoding="utf-8")

    if snippet is None:
        snippet = """
import os
import sys
import datetime
import pandas as pd

print(datetime.datetime.now())

sys.exit(0)

def report():
    print(datetime.datetime.now())
    df = pd.DataFrame()
    print(df)


if __name__ == "__main__":
    report()
"""

    try:
        langfuse_client = Langfuse(
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            host=os.environ["LANGFUSE_HOST"],
        )
    except KeyError as exc:  # pragma: no cover - configuration guard
        missing = exc.args[0]
        raise RuntimeError(f"Missing environment variable required for Langfuse: {missing}") from exc

    file_path = "coffee_maker/code_formatter/crewai/main.py"
    repo_full_name = "Bobain/MonolithicCoffeeMakerAgent"
    pr_number = 110

    formatter_agent = create_code_formatter_agents(langfuse_client)["senior_engineer"]
    reviewer_agent = create_pr_reviewer_agent(langfuse_client, pr_number, repo_full_name, file_path)[
        "pull_request_reviewer"
    ]

    flow = create_code_formatter_flow(
        formatter_agent=formatter_agent,
        reviewer_agent=reviewer_agent,
        langfuse_client=langfuse_client,
        file_path=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        file_content=snippet,
        raise_on_reviewer_failure=False,
    )

    reviewer_output = flow.kickoff()

    print("=== Formatter Agent Output ===")
    print(flow.state.reformat_result)
    print("=== Reviewer Agent Output ===")
    print(reviewer_output)

    langfuse_client.flush()
