# coffee_maker/code_formatter/tasks.py
import os
from crewai import Task
from langfuse import get_client
from coffee_maker.code_formatter.agents import create_code_formatter_agents, create_pr_reviewer_agent

# Initialize Langfuse client
langfuse = get_client(os.getenv("LANGFUSE_API_KEY"))

# Delimiters for parsing LLM response
MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


def create_refactor_task(file_path, file_content):
    """
    Creates the refactoring task for a single file's content.
    This task's output must be a structured string for the next agent.

    Args:
        agent: The agent assigned to this task.
        file_path (str): The path of the file, for context.
        file_content (str): The actual content of the file to be refactored.
    """
    prompt = langfuse.get_prompt("code_formatter_main_llm_entry")
    prompt = prompt.compile(
        filename=file_path,
        file_content=file_content,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    return Task(
        description=prompt,
        expected_output="A string containing the code given as input with some modifications "
        "and explanations into the code delimited with given delimiters",
        agent=create_code_formatter_agents(),
    )


def create_review_task(file_path):
    """
    Creates the task for posting the review suggestion on GitHub.
    (No changes needed in this function's logic)
    """
    return Task(
        description=f"""
      """,
        expected_output=f"A confirmation message stating that each suggestions for {file_path} "
        f"has been successfully posted to GitHub : OK. "
        f"Or : 'KO\n... explanations about what went wrong ...",
        agent=create_pr_reviewer_agent(),
    )
