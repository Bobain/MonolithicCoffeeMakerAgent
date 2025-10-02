"""
Custom CrewAI Tools for GitHub PR Review Integration.

This module provides custom tools for the CrewAI framework that enable agents to
interact with GitHub pull requests, specifically for posting code review suggestions.

The tools integrate with:
    - GitHub API (via PyGithub) for creating review comments
    - Langfuse for observability and tracing
    - Pydantic for input validation

Classes:
    PostSuggestionInput: Pydantic model defining input schema for the suggestion tool
    PostSuggestionToolLangAI: CrewAI tool for posting multi-line code suggestions

Environment Variables Required:
    GITHUB_TOKEN: GitHub personal access token with repo permissions
    LANGFUSE_SECRET_KEY: For Langfuse tracing (loaded via main module)
    LANGFUSE_PUBLIC_KEY: For Langfuse tracing (loaded via main module)
    LANGFUSE_HOST: For Langfuse tracing (loaded via main module)

Example:
    >>> from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI
    >>> tool = PostSuggestionToolLangAI()
    >>> result = tool._run(
    ...     repo_full_name="owner/repo",
    ...     pr_number=123,
    ...     file_path="src/main.py",
    ...     start_line=10,
    ...     end_line=15,
    ...     suggestion_body="def improved_function():\\n    pass",
    ...     comment_text="This is a better implementation"
    ... )
"""

from crewai.tools import BaseTool as CrewBaseTool
from pydantic import BaseModel, Field
from langfuse import observe
import os
from github import Github, Auth
import logging
from dotenv import load_dotenv

# Load environment variables to ensure GITHUB_TOKEN is available
load_dotenv()

logger = logging.getLogger(__name__)


class PostSuggestionInput(BaseModel):
    """
    Input schema for the PostSuggestionToolLangAI tool.

    This model defines the required parameters for posting a code suggestion
    as a review comment on a GitHub pull request.

    Attributes:
        repo_full_name: Full repository name in the format 'owner/repo' (e.g., 'Bobain/MonolithicCoffeeMakerAgent')
        pr_number: Pull request number (integer) to post the suggestion to
        file_path: Path to the file in the repository where the suggestion should be posted (e.g., 'src/main.py')
        start_line: Starting line number for the suggestion (1-indexed)
        end_line: Ending line number for the suggestion (1-indexed, must be >= start_line)
        suggestion_body: The suggested code to replace the current code (without markdown backticks)
        comment_text: Additional comment text to accompany the suggestion
    """

    repo_full_name: str = Field(..., description="Full repository name (owner/repo)")
    pr_number: int = Field(..., description="Pull request number", gt=0)
    file_path: str = Field(..., description="File path in the repository")
    start_line: int = Field(..., description="Starting line number", ge=1)
    end_line: int = Field(..., description="Ending line number", ge=1)
    suggestion_body: str = Field(..., description="Suggested code content")
    comment_text: str = Field(..., description="Comment text accompanying the suggestion")


class PostSuggestionToolLangAI(CrewBaseTool):
    """
    CrewAI tool for posting code suggestions as review comments on GitHub pull requests.

    This tool integrates with the GitHub API to post formatted code suggestions
    directly on pull request files. It uses GitHub's suggestion feature which
    allows reviewers to propose specific code changes that can be committed
    with a single click.

    The tool requires a valid GITHUB_TOKEN environment variable with appropriate
    permissions (repo scope) to post review comments on pull requests.

    Attributes:
        name: Human-readable name of the tool
        description: Brief description of the tool's purpose
        args_schema: Pydantic model defining the input parameters

    Example:
        >>> tool = PostSuggestionToolLangAI()
        >>> result = tool._run(
        ...     repo_full_name="owner/repo",
        ...     pr_number=123,
        ...     file_path="src/main.py",
        ...     start_line=10,
        ...     end_line=15,
        ...     suggestion_body="def improved_function():\\n    return True",
        ...     comment_text="This is a cleaner implementation"
        ... )
    """

    name: str = "Post PR Review Suggestion Tool"
    description: str = "Post multi-line code suggestions on GitHub PRs"
    args_schema: type[BaseModel] = PostSuggestionInput

    @observe
    def _run(
        self,
        repo_full_name: str,
        pr_number: int,
        file_path: str,
        start_line: int,
        end_line: int,
        suggestion_body: str,
        comment_text: str,
    ) -> str:
        """
        Post a code suggestion as a review comment on a GitHub pull request.

        This method creates a review comment with a code suggestion block on the specified
        lines of a file in a pull request. The suggestion uses GitHub's native suggestion
        feature, which allows the PR author to apply the suggestion with a single click.

        The method performs the following steps:
        1. Validates that GITHUB_TOKEN environment variable is set
        2. Authenticates with GitHub API using the token
        3. Retrieves the repository and pull request
        4. Gets the latest commit SHA from the PR's head branch
        5. Formats the suggestion body with markdown suggestion syntax
        6. Posts the review comment with the suggestion

        Args:
            repo_full_name: Full repository name in format 'owner/repo' (e.g., 'Bobain/MonolithicCoffeeMakerAgent')
            pr_number: Pull request number (must be a positive integer)
            file_path: Path to the file in the repository (e.g., 'src/main.py')
            start_line: Starting line number for the suggestion (1-indexed, must be >= 1)
            end_line: Ending line number for the suggestion (1-indexed, must be >= start_line)
            suggestion_body: The suggested code content (plain text, without markdown backticks).
                           This will be automatically wrapped in GitHub's suggestion format.
            comment_text: Additional explanatory text to accompany the suggestion.
                         This appears above the code suggestion block.

        Returns:
            str: Success message indicating the suggestion was posted, in the format:
                "Successfully posted suggestion for {file_path} in PR #{pr_number}"

        Raises:
            ValueError: If GITHUB_TOKEN environment variable is not set
            Exception: For any GitHub API errors (authentication, permissions, invalid PR, etc.)

        Notes:
            - The function uses pr.head.sha to get the latest commit, which is more reliable
              than using pr.get_commits()[-1] which can fail with IndexError
            - Line numbers are 1-indexed (first line is 1, not 0)
            - The suggestion is posted on the RIGHT side of the diff (the new version)
            - start_line and end_line can be the same for single-line suggestions
            - All operations are logged using the module logger for observability

        Example:
            >>> tool = PostSuggestionToolLangAI()
            >>> result = tool._run(
            ...     repo_full_name="Bobain/MonolithicCoffeeMakerAgent",
            ...     pr_number=111,
            ...     file_path="coffee_maker/code_formatter/crewai/main.py",
            ...     start_line=10,
            ...     end_line=12,
            ...     suggestion_body="# Improved comment\\ndef better_function():\\n    pass",
            ...     comment_text="This implementation is clearer and follows PEP 8"
            ... )
            >>> print(result)
            Successfully posted suggestion for coffee_maker/code_formatter/crewai/main.py in PR #111
        """
        try:
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                logger.critical("Error: GITHUB_TOKEN environment variable is not set.")
                raise ValueError("Credentials for Github needed: GITHUB_TOKEN not defined.")

            auth = Auth.Token(token)
            g = Github(auth=auth)
            repo = g.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)

            # --- FIX #2: THE CRITICAL CHANGE ---
            # Do NOT use `pr.get_commits()[-1]`. It is unreliable and causes the IndexError.
            # INSTEAD, get the commit SHA directly from the pull request's 'head'.
            # This is guaranteed to exist and is the correct reference for the PR's latest state.
            latest_commit_sha = pr.head.sha

            formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"

            # Use the reliable SHA string for the 'commit'.
            logger.info("PR review : posting a review commit suggestion")
            pr.create_review_comment(
                body=f"{comment_text}\n{formatted_suggestion}",
                commit=latest_commit_sha,  # <-- Pass the reliable SHA here
                path=file_path,
                start_line=start_line,
                line=end_line,
                side="RIGHT",
            )
            logger.info("PR review : Successfully posted a review commit suggestion")
            return f"Successfully posted suggestion for {file_path} in PR #{pr_number}"

        except Exception as e:
            logger.info("PR review : Failed to post a review commit suggestion")
            logger.critical(e, exc_info=True)
            raise


if __name__ == "__main__":
    # This test block will now run correctly with the fixes above.
    tool_instance = PostSuggestionToolLangAI()
    tool_instance._run(
        repo_full_name="Bobain/MonolithicCoffeeMakerAgent",
        pr_number=111,
        file_path="coffee_maker/code_formatter/crewai/main.py",
        start_line=1,
        end_line=1,
        suggestion_body="Do not commit this suggestion! This is a test from the corrected script!",
        comment_text="This is a test from the corrected script!",
    )
