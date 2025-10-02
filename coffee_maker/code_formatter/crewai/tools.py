# coffee_maker/code_formatter/crewai/tools.py

from crewai.tools import BaseTool as CrewBaseTool
from pydantic import BaseModel, Field
from langfuse import observe
import os
from github import Github, Auth
import logging
from dotenv import load_dotenv  # <-- REQUIRED IMPORT

# --- FIX #1: Load environment variables at the very top of the script ---
# This ensures that both GITHUB_TOKEN and Langfuse keys are available for all functions.
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
    ):
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
