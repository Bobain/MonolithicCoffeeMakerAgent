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
from github import Github, Auth, GithubException
import logging
from dotenv import load_dotenv

# Load environment variables to ensure GITHUB_TOKEN is available
load_dotenv()

logger = logging.getLogger(__name__)


def _is_pending_review_conflict(exc: GithubException) -> bool:
    """Return True if exception indicates an existing pending review blocks new comments."""

    message = (exc.data or {}).get("message", "") if isinstance(exc.data, dict) else ""
    if "pending review" in message.lower():
        return True

    errors = (exc.data or {}).get("errors", []) if isinstance(exc.data, dict) else []
    for error in errors:
        if isinstance(error, dict) and "pending review" in error.get("message", "").lower():
            return True

    return "pending review" in str(exc).lower()


def _clear_pending_review(pr, login: str) -> bool:
    """Delete any pending review authored by the provided login.

    Returns True when a review was removed, False otherwise.
    """

    try:
        for review in pr.get_reviews():
            if getattr(review, "state", "").upper() == "PENDING" and getattr(review.user, "login", None) == login:
                logger.info("Found existing pending review for %s. Deleting before retrying comment.", login)
                review.delete()
                return True
    except Exception as cleanup_error:  # pragma: no cover - defensive logging
        logger.warning("Unable to clear pending review: %s", cleanup_error)

    return False


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
        ...     pr_number=110,
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
        repo_full_name: str = None,
        pr_number: int = None,
        file_path: str = None,
        start_line: int = None,
        end_line: int = None,
        suggestion_body: str = None,
        comment_text: str = None,
        **kwargs,
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
        # Handle both direct parameters and kwargs-wrapped parameters
        # Some LLM agents wrap parameters in kwargs
        if kwargs and not repo_full_name:
            repo_full_name = kwargs["repo_full_name"]
            pr_number = kwargs["pr_number"]
            file_path = kwargs["file_path"]
            start_line = kwargs["start_line"]
            end_line = kwargs["end_line"]
            suggestion_body = kwargs["suggestion_body"]
            comment_text = kwargs["comment_text"]

        try:
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                logger.critical("Error: GITHUB_TOKEN environment variable is not set.")
                raise ValueError("Credentials for Github needed: GITHUB_TOKEN not defined.")

            logger.info(
                f"Attempting to post suggestion to repo: {repo_full_name}, PR: {pr_number}, file: {file_path}, lines: {start_line}-{end_line}"
            )

            auth = Auth.Token(token)
            g = Github(auth=auth)
            current_user_login = g.get_user().login

            try:
                repo = g.get_repo(repo_full_name)
            except Exception as repo_error:
                logger.error(f"Failed to access repository '{repo_full_name}': {repo_error}")
                logger.error(f"Make sure the repository name is in format 'owner/repo' and exists")
                raise ValueError(
                    f"Repository '{repo_full_name}' not found. Check the repository name format (should be 'owner/repo'). Error: {repo_error}"
                )
            pr = repo.get_pull(pr_number)

            # --- FIX #2: THE CRITICAL CHANGE ---
            # Do NOT use `pr.get_commits()[-1]`. It is unreliable and causes the IndexError.
            # INSTEAD, get the commit SHA directly from the pull request's 'head'.
            # This is guaranteed to exist and is the correct reference for the PR's latest state.
            latest_commit_sha = pr.head.sha

            formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"

            # Use the reliable SHA string for the 'commit'.
            logger.info("PR review : posting a review commit suggestion")
            valid_paths = {pull_file.filename for pull_file in pr.get_files()}
            if file_path not in valid_paths:
                raise ValueError(
                    f"File path '{file_path}' not found in PR #{pr_number}. Available paths: {sorted(valid_paths)}"
                )

            try:
                pr.create_review_comment(
                    body=f"{comment_text}\n{formatted_suggestion}",
                    commit=latest_commit_sha,
                    path=file_path,
                    start_line=start_line,
                    line=end_line,
                    side="RIGHT",
                )
            except GithubException as github_exc:
                if github_exc.status == 422 and _is_pending_review_conflict(github_exc):
                    logger.info("Encountered pending review conflict. Attempting cleanup and retry.")
                    if _clear_pending_review(pr, current_user_login):
                        pr.create_review_comment(
                            body=f"{comment_text}\n{formatted_suggestion}",
                            commit=latest_commit_sha,
                            path=file_path,
                            start_line=start_line,
                            line=end_line,
                            side="RIGHT",
                        )
                    else:
                        raise
                else:
                    raise
            logger.info("PR review : Successfully posted a review commit suggestion")
            return f"Successfully posted suggestion for {file_path} in PR #{pr_number}"

        except Exception as e:
            logger.info("PR review : Failed to post a review commit suggestion")
            logger.critical(e, exc_info=True)
            raise


if __name__ == "__main__":
    #   python coffee_maker/code_formatter/crewai/tools.py \
    #     --repo Bobain/MonolithicCoffeeMakerAgent \
    #     --pr 110 \
    #     --file coffee_maker/code_formatter/crewai/main.py \
    #     --start 17 \
    #     --end 20 \
    #     --suggestion "" \
    #     --comment "Removed redundant print statement and the unreachable sys.exit() call."
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Invoke PostSuggestionToolLangAI once from the CLI.",
        epilog="Example: python -m coffee_maker.code_formatter.crewai.tools --repo owner/repo --pr 42 "
        "--file path/to/file.py --start 10 --end 12 --suggestion 'print(\"hi\")' --comment 'Add logging'",
    )
    parser.add_argument("--repo", required=True, help="Full repository name, e.g. owner/repo")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    parser.add_argument("--file", required=True, help="File path relative to the repository root")
    parser.add_argument("--start", type=int, required=True, help="Starting line number (1-indexed)")
    parser.add_argument("--end", type=int, required=True, help="Ending line number (1-indexed)")
    parser.add_argument("--suggestion", required=True, help="Suggested code body without markdown fences")
    parser.add_argument("--comment", required=True, help="Comment text to accompany the suggestion")

    try:
        args = parser.parse_args()
    except SystemExit as exc:
        # argparse already printed a helpful message.
        raise SystemExit(exc.code) from None

    tool_instance = PostSuggestionToolLangAI()
    try:
        result = tool_instance._run(
            repo_full_name=args.repo,
            pr_number=args.pr,
            file_path=args.file,
            start_line=args.start,
            end_line=args.end,
            suggestion_body=args.suggestion,
            comment_text=args.comment,
        )
    except GithubException as github_exc:  # pragma: no cover - manual invocation helper
        print(f"GitHub API error: {github_exc}", file=sys.stderr)
        raise SystemExit(1) from github_exc

    print(result)

    # current call from agent : the file_path is wrong
    kwargs = dict(
        repo_full_name="Bobain/MonolithicCoffeeMakerAgent",
        pr_number=110,
        file_path="coffee_maker/code_formatter/main.py",
        start_line=17,
        end_line=20,
        suggestion_body="",
        comment_text="Removed redundant print statement and the unreachable sys.exit() call.",
    )

    kwargs = dict(
        repo_full_name="Bobain/MonolithicCoffeeMakerAgent",
        pr_number=110,
        file_path="coffee_maker/code_formatter/crewai/main.py",
        start_line=17,
        end_line=20,
        suggestion_body="",
        comment_text="Removed redundant print statement and the unreachable sys.exit() call.",
    )

    tool_instance._run(**kwargs)
