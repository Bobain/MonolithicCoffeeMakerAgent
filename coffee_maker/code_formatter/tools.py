# coffee_maker/code_formatter/tools.py

import os
from github import Github
from langchain.tools import tool


@tool("Post PR Review Suggestion Tool")
def post_suggestion(
    repo_full_name: str,
    pr_number: int,
    file_path: str,
    start_line: int,
    end_line: int,
    suggestion_body: str,
    comment_text: str,
) -> str:
    """
    Posts a multi-line code suggestion in a pull request review.
    This tool is essential for providing actionable feedback directly on the code.
    Args:
        repo_full_name (str): Full name of the repository (e.g., 'owner/repo').
        pr_number (int): Number of the pull request.
        file_path (str): The path to the file being commented on.
        start_line (int): The first line of the code block to be replaced.
        end_line (int): The last line of the code block to be replaced.
        suggestion_body (str): The new code to suggest.
        comment_text (str): The comment that will accompany the suggestion.
    Returns:
        str: A confirmation message indicating success or failure.
    """
    try:
        # Authenticate with GitHub using a Personal Access Token
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return "Error: The GITHUB_TOKEN environment variable is not set. Please set it in your .env file."

        g = Github(token)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)

        # GitHub's API requires suggestions to be formatted within a "suggestion" code block in the comment body.
        formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"

        # To post a review comment, we need to associate it with a specific commit.
        # The latest commit on the PR is the correct one to use.
        latest_commit = pull_request.get_commits().reversed[0]

        # This method creates a new review comment on a specific line or range of lines.
        pull_request.create_review_comment(
            body=f"{comment_text}\n{formatted_suggestion}",
            commit=latest_commit,
            path=file_path,
            # If the change spans multiple lines, use start_line and line
            start_line=start_line,
            line=end_line,
        )
        return f"Successfully posted suggestion for '{file_path}' in PR #{pr_number}."
    except Exception as e:
        return f"Error: Failed to post suggestion to GitHub. Details: {e}"
