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

logger = logging.getLogger(__name__)


# Delimiters for parsing LLM response
MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


@observe
def create_refactor_task(agent, langfuse_client, file_path, file_content):
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
        >>> task = create_refactor_task(agent, langfuse, "src/main.py", "def foo(): pass")
    """
    logger.debug(f"Creating refactor task for {file_path}")
    prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
    prompt = prompt.compile(
        filename=file_path,
        file_content=file_content,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    task = Task(
        description=prompt,
        expected_output="A string containing the code given as input with some formatting suggestions "
        "annotated in code blocks (with given delimiters as explained in YOUR RESPONSE STRUCUTURE), "
        "as well as short explanation for each",
        agent=agent,
    )
    logger.debug(f"Created refactor task for {file_path}")
    return task


@observe
def create_review_task(agent, langfuse_client, file_path, repo_full_name, pr_number, refactor_task):
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
        >>> refactor_task = create_refactor_task(...)
        >>> review_task = create_review_task(
        ...     agent, langfuse, "src/main.py", "owner/repo", 123, refactor_task
        ... )

    Note:
        This task depends on refactor_task.output, so the refactor task must
        be completed before this task executes. The context dependency should
        be set in the orchestration code.
    """
    logger.debug(f"Creating review task for {file_path}")
    logger.debug(f"Refactor task output for {file_path}: {refactor_task.output}")
    prompt = langfuse_client.get_prompt("pr_reviewer_task")
    prompt = prompt.compile(
        filename=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        refactored_code=refactor_task.output,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    task = Task(
        description=prompt,
        expected_output=f"A confirmation message stating that each suggestions for {file_path} "
        f"has been successfully posted to GitHub : 'OK'. "
        f"Or : 'KO\n#... explanations about what went wrong ...",
        agent=agent,
        context=[refactor_task],  # Ensure the review task has access to refactor output
    )
    logger.debug(f"Created review task for {file_path}")
    return task
