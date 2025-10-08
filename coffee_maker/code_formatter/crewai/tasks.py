"""
Task Definitions for Code Formatter CrewAI System.

This module defines the tasks that agents execute in the code formatting workflow.
Tasks are organized in a sequential pipeline where the refactor task analyzes code
and the review task posts suggestions to GitHub.

Module-level Constants:
    MODIFIED_CODE_DELIMITER_START: Start delimiter for code blocks in LLM output
    MODIFIED_CODE_DELIMITER_END: End delimiter for code blocks in LLM output
    EXPLANATIONS_DELIMITER_START: Start delimiter for explanations in LLM output
    EXPLANATIONS_DELIMITER_END: End delimiter for explanations in LLM output

Functions:
    create_refactor_task: Creates a task for code analysis and refactoring
    create_review_task: Creates a task for posting suggestions to GitHub PR
"""

from crewai import Task
import logging
from langfuse import observe
from dotenv import load_dotenv

load_dotenv()

from coffee_maker.code_formatter.crewai.flow import (
    MODIFIED_CODE_DELIMITER_START,
    MODIFIED_CODE_DELIMITER_END,
    EXPLANATIONS_DELIMITER_START,
    EXPLANATIONS_DELIMITER_END,
)

logger = logging.getLogger(__name__)


@observe
def create_reformat_task(agent, langfuse_client, file_path: str, file_content: str) -> Task:
    """
    Creates the refactoring task for a single file's content.

    This task instructs the agent to analyze the provided code and suggest
    improvements following best practices and style guidelines. The task's
    description is fetched from Langfuse and compiled with file-specific context.

    The task output must follow a structured format using delimiters to separate
    modified code from explanations, enabling the next agent to parse and post
    the suggestions correctly.

    Args:
        agent (Agent): The CrewAI agent assigned to execute this task (typically
            the senior engineer agent)
        langfuse_client (Langfuse): Initialized Langfuse client for fetching prompts
        file_path (str): The path of the file being analyzed (for context in prompts)
        file_content (str): The actual content of the file to be refactored

    Returns:
        Task: A CrewAI Task instance configured for code refactoring

    Example:
        >>> from crewai import Agent
        >>> from langfuse import Langfuse
        >>> agent = Agent(...)
        >>> langfuse = Langfuse(...)
        >>> task = create_reformat_task(agent, langfuse, "src/main.py", "def foo(): pass")
    """
    logger.debug(f"Creating refactor task for {file_path}")
    prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
    compiled_prompt = prompt.compile(
        filename=file_path,
        file_content=file_content,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    task = Task(
        description=compiled_prompt,
        expected_output="A string containing the code given as input with some formatting suggestions "
        "annotated in code blocks (with given delimiters as explained in YOUR RESPONSE STRUCUTURE), "
        "as well as short explanation for each",
        agent=agent,
        name=f"reformat_{file_path}",
    )
    logger.info(f"Created refactor task for {file_path} with {len(file_content)} bytes of content")
    return task


@observe
def create_review_task(
    agent, langfuse_client, file_path: str, repo_full_name: str, pr_number: int, refactor_task: Task
) -> Task:
    """
    Creates the task for posting the review suggestion on GitHub.

    This task takes the output from the refactor task (which contains code
    suggestions and explanations) and posts them as review comments on the
    specified GitHub pull request. The task uses the PostSuggestionToolLangAI
    tool to interact with the GitHub API.

    Args:
        agent (Agent): The CrewAI agent assigned to execute this task (typically
            the PR reviewer agent with GitHub posting capabilities)
        langfuse_client (Langfuse): Initialized Langfuse client for fetching prompts
        file_path (str): The path of the file in the repository
        repo_full_name (str): Full repository name in format 'owner/repo'
        pr_number (int): Pull request number to post suggestions to
        refactor_task (Task): The refactor task instance whose output will be used
            as input for this task

    Returns:
        Task: A CrewAI Task instance configured for posting GitHub review comments

    Example:
        >>> from crewai import Agent, Task
        >>> from langfuse import Langfuse
        >>> agent = Agent(...)
        >>> langfuse = Langfuse(...)
        >>> refactor_task = create_reformat_task(...)
        >>> review_task = create_review_task(
        ...     agent, langfuse, "src/main.py", "Bobain/MonolithicCoffeeMakerAgent", 110, refactor_task
        ... )

    Note:
        This task depends on refactor_task.output, so the refactor task must
        be completed before this task executes. The context dependency should
        be set in the orchestration code.
    """
    logger.debug(f"Creating review task for {file_path}")
    prompt = langfuse_client.get_prompt("pr_reviewer_task")
    compiled_prompt = prompt.compile(
        file_path=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    task = Task(
        description=compiled_prompt,
        expected_output=f"A confirmation message stating that each suggestions for {file_path} "
        f"has been successfully posted to GitHub : 'OK'. "
        f"Or : 'KO\n#... explanations about what went wrong ...",
        agent=agent,
        context=[refactor_task],
        name=f"review_{file_path}",  # Add task name for better tracing
    )
    logger.info(f"Created review task for {file_path} targeting {repo_full_name} PR#{pr_number}")
    return task


if __name__ == "__main__":
    import os
    from langfuse import Langfuse
    import argparse

    parser = argparse.ArgumentParser(description="Run formatter and reviewer agents on a code snippet")
    parser.add_argument(
        "--path",
        help="Optional path to a file containing the snippet to process",
    )
    parser.add_argument(
        "--text",
        help="Snippet to process in-line; overrides --path when provided",
    )
    args = parser.parse_args()

    snippet: str | None = None
    if args.text:
        snippet = args.text
    elif args.path:
        from pathlib import Path

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

    langfuse_client = Langfuse(
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        host=os.environ["LANGFUSE_HOST"],
    )

    from agents import create_code_formatter_agents, create_pr_reviewer_agent

    file_path = "coffee_maker/code_formatter/main.py"
    repo_full_name = "Bobain/MonolithicCoffeeMakerAgent"
    pr_number = 110

    formatter_agent = create_code_formatter_agents(langfuse_client)["senior_engineer"]
    reviewer_agent = create_pr_reviewer_agent(langfuse_client, pr_number, repo_full_name, file_path)[
        "pull_request_reviewer"
    ]

    refactor_task_instance = create_reformat_task(
        formatter_agent,
        langfuse_client,
        file_path,
        file_content=snippet,
    )
    review_task_instance = create_review_task(
        reviewer_agent,
        langfuse_client,
        file_path,
        repo_full_name,
        pr_number,
        refactor_task_instance,
    )

    formatter_result = formatter_agent.kickoff(snippet)
    print("=== Formatter Agent Output ===")
    print(formatter_result.raw)

    reviewer_result = reviewer_agent.kickoff(formatter_result.raw)
    print("=== Reviewer Agent Output ===")
    print(reviewer_result.raw)
