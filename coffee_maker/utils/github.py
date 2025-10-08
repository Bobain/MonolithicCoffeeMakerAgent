import logging
import os
from typing import Optional

from github import Auth, Github, GithubException
from langfuse import observe

LOGGER = logging.getLogger(__name__)


def get_github_client_instance() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token or not len(token):
        LOGGER.critical("Error: GITHUB_TOKEN environment variable is not set.")
        raise ValueError("Credentials for Github needed: GITHUB_TOKEN not defined.")
    auth = Auth.Token(token)
    return Github(auth=auth)


github_client_instance = get_github_client_instance()


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
    g: Github = github_client_instance,
) -> str:
    """
    Post a code suggestion as a review comment on a GitHub pull request.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number
        file_path (str): Path to the file in the repository
        start_line (int): Starting line number (1-indexed)
        end_line (int): Ending line number (1-indexed)
        suggestion_body (str): The suggested code (plain text, no markdown)
        comment_text (str): Explanatory text for the suggestion

    Example input (use \\n for newlines in JSON strings): {
        "repo_full_name": "owner/repo",
        "pr_number": 123,
        "file_path": "src/main.py",
        "start_line": 10,
        "end_line": 12,
        "suggestion_body": "def improved():\\n    pass",
        "comment_text": "Better implementation"
    }

    IMPORTANT: In JSON, use \\n for newlines, not actual line breaks!

    Returns:
        str: Success message

    Notes:
        - Line numbers are 1-indexed (first line is 1)
        - start_line and end_line can be the same for single-line suggestions
        - suggestion_body should NOT include markdown code fences
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

        comment_kwargs = {
            "body": f"{comment_text}\n{formatted_suggestion}",
            "commit": latest_commit_sha,
            "path": file_path,
            "line": int(end_line),
            "side": "RIGHT",
        }

        if start_line is not None and start_line != end_line:
            comment_kwargs.update(
                {
                    "start_line": int(start_line),
                    "start_side": "RIGHT",
                }
            )

        try:
            pr.create_review_comment(**comment_kwargs)
        except GithubException as github_exc:
            if github_exc.status == 422 and _is_pending_review_conflict(github_exc):
                LOGGER.info("Encountered pending review conflict. Attempting cleanup and retry.")
                if _clear_pending_review(pr, current_user_login):
                    pr.create_review_comment(**comment_kwargs)
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
def get_pr_modified_files(repo_full_name, pr_number, g: Github = github_client_instance):
    """
    Fetches the list of modified files from a pull request.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number

    Example input: {"repo_full_name": "owner/repo", "pr_number": 123}

    Returns:
        Dict with "python_files" (list of .py filenames) and "total_files" count
    """
    LOGGER.info(f"Fetching modified files from PR #{pr_number} in {repo_full_name}")
    try:
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        files = pull_request.get_files()
        file_list = []
        for file in files:
            # Only include filename and status, NOT the patch (to save tokens)
            file_list.append(
                {
                    "filename": file.filename,
                    "status": getattr(file, "status", None),
                }
            )
        LOGGER.info(f"Found {len(file_list)} modified files in PR #{pr_number}")
        # Return just the filenames as a simple list to minimize tokens
        filenames = [f["filename"] for f in file_list if f["filename"].endswith(".py")]
        return {"python_files": filenames, "total_files": len(file_list)}
    except Exception:
        LOGGER.error(f"Could not fetch modified files from PR #{pr_number}.", exc_info=True)
        return {"python_files": [], "total_files": 0}


@observe
def get_pr_file_content(repo_full_name, pr_number, file_path, g: Github = github_client_instance):
    """
    Fetches the content of a specific file from a PR's head commit.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number
        file_path (str): Path to the file in the repository

    Example input: {"repo_full_name": "owner/repo", "pr_number": 123, "file_path": "src/main.py"}

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


class GitHubPRClient:
    """Convenience wrapper that reuses a persistent Github client for PR utilities."""

    def __init__(self, github_client: Optional[Github] = None) -> None:
        self._client = github_client or github_client_instance

    @property
    def client(self) -> Github:
        """Expose the underlying Github client for advanced operations."""

        return self._client

    def post_suggestion_in_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        file_path: str,
        start_line: int,
        end_line: int,
        suggestion_body: str,
        comment_text: str,
    ) -> str:
        return post_suggestion_in_pr_review(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            suggestion_body=suggestion_body,
            comment_text=comment_text,
            g=self._client,
        )

    def get_pr_modified_files(self, repo_full_name: str, pr_number: int):
        return get_pr_modified_files(repo_full_name=repo_full_name, pr_number=pr_number, g=self._client)

    def get_pr_file_content(self, repo_full_name: str, pr_number: int, file_path: str):
        return get_pr_file_content(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            g=self._client,
        )
