# coffee_maker/code_formatter/tasks.py
from crewai import Task

# Delimiters for parsing LLM response
MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


def create_refactor_task(agent, langfuse_client, file_path, file_content):
    """
    Creates the refactoring task for a single file's content.
    This task's output must be a structured string for the next agent.

    Args:
        agent: The agent assigned to this task.
        file_path (str): The path of the file, for context.
        file_content (str): The actual content of the file to be refactored.
    """
    prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
    prompt = prompt.compile(
        filename=file_path,
        file_content=file_content,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    return Task(
        description=prompt,
        expected_output="A string containing the code given as input with some formatting suggestions "
        "annotated in code blocks (with given delimiters as explained in YOUR RESPONSE STRUCUTURE), "
        "as well as short explanation for each",
        agent=agent,
    )


def create_review_task(agent, langfuse_client, file_path, reformatted_file_content, repo_full_name, pr_number):
    """
    Creates the task for posting the review suggestion on GitHub.
    (No changes needed in this function's logic)
    """
    prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
    prompt = prompt.compile(
        filename=file_path,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        refactored_code=reformatted_file_content,
        MODIFIED_CODE_DELIMITER_START=MODIFIED_CODE_DELIMITER_START,
        MODIFIED_CODE_DELIMITER_END=MODIFIED_CODE_DELIMITER_END,
        EXPLANATIONS_DELIMITER_START=EXPLANATIONS_DELIMITER_START,
        EXPLANATIONS_DELIMITER_END=EXPLANATIONS_DELIMITER_END,
    )
    return Task(
        description=prompt,
        expected_output=f"A confirmation message stating that each suggestions for {file_path} "
        f"has been successfully posted to GitHub : 'OK'. "
        f"Or : 'KO\n#... explanations about what went wrong ...",
        agent=agent,
    )
