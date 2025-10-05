from github import Github, Auth, GithubException
from langfuse import observe
import os
import logging

LOGGER = logging.getLogger(__name__)


def get_github_client_instance() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token or not len(token):
        LOGGER.critical("Error: GITHUB_TOKEN environment variable is not set.")
        raise ValueError("Credentials for Github needed: GITHUB_TOKEN not defined.")
    auth = Auth.Token(token)
    return Github(auth=auth)


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
                LOGGER.info("Found existing pending review for %s. Deleting before retrying comment.", login)
                review.delete()
                return True
    except Exception as cleanup_error:  # pragma: no cover - defensive logging
        LOGGER.warning("Unable to clear pending review: %s", cleanup_error)

    return False


@observe
def post_suggestion_in_pr_review(
    repo_full_name: str = None,
    pr_number: int = None,
    file_path: str = None,
    start_line: int = None,
    end_line: int = None,
    suggestion_body: str = None,
    comment_text: str = None,
    g=get_github_client_instance(),
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
        >>> result = post_suggestion_in_pr_review(
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
        LOGGER.info(
            f"Attempting to post suggestion to repo: {repo_full_name}, PR: {pr_number}, file: {file_path}, lines: {start_line}-{end_line}"
        )
        current_user_login = g.get_user().login

        try:
            repo = g.get_repo(repo_full_name)
        except Exception as repo_error:
            LOGGER.error(f"Failed to access repository '{repo_full_name}': {repo_error}")
            LOGGER.error(f"Make sure the repository name is in format 'owner/repo' and exists")
            raise ValueError(
                f"Repository '{repo_full_name}' not found. Check the repository name format (should be 'owner/repo'). Error: {repo_error}"
            )
        pr = repo.get_pull(pr_number)

        latest_commit_sha = pr.head.sha

        formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"

        # Use the reliable SHA string for the 'commit'.
        LOGGER.info("PR review : posting a review commit suggestion")
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
                LOGGER.info("Encountered pending review conflict. Attempting cleanup and retry.")
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
        LOGGER.info("PR review : Successfully posted a review commit suggestion")
        return f"Successfully posted suggestion for {file_path} in PR #{pr_number}"

    except Exception as e:
        LOGGER.info("PR review : Failed to post a review commit suggestion")
        LOGGER.critical(e, exc_info=True)
        raise


@observe
def get_pr_modified_files(repo_full_name, pr_number, g=get_github_client_instance()):
    """
    Fetches the list of modified files from a pull request.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number

    Returns:
        List of dictionaries containing file metadata (filename, patch, status)
        for files modified in the PR, or empty list if fetch fails
    """
    LOGGER.info(f"Fetching modified files from PR #{pr_number} in {repo_full_name}")
    try:
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        files = pull_request.get_files()
        file_list = []
        for file in files:
            file_list.append(
                {
                    "filename": file.filename,
                    "patch": getattr(file, "patch", None),
                    "status": getattr(file, "status", None),
                }
            )
        LOGGER.info(f"Found {len(file_list)} modified files in PR #{pr_number}")
        return file_list
    except Exception:
        LOGGER.error(f"Could not fetch modified files from PR #{pr_number}.", exc_info=True)
        return []


@observe
def get_pr_file_content(repo_full_name, pr_number, file_path, g=get_github_client_instance()):
    """
    Fetches the content of a specific file from a PR's head commit.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number
        file_path: Path to the file in the repository

    Returns:
        File content as string, or None if fetch fails
    """
    LOGGER.info(f"Fetching content for '{file_path}' from PR #{pr_number}")
    try:
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        contents = repo.get_contents(file_path, ref=pull_request.head.sha)
        content = contents.decoded_content.decode("utf-8")
        LOGGER.info(f"Successfully fetched {len(content)} bytes from '{file_path}'")
        return content
    except Exception:
        LOGGER.error(f"Could not fetch content for '{file_path}' from GitHub.", exc_info=True)
        return None
