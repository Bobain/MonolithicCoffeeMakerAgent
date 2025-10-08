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
from github import GithubException
import logging
from dotenv import load_dotenv
from coffee_maker.utils.github import post_suggestion_in_pr_review


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
        return post_suggestion_in_pr_review(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            suggestion_body=suggestion_body,
            comment_text=comment_text,
        )


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
