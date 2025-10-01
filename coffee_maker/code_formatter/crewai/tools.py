from crewai.tools import BaseTool as CrewBaseTool
from pydantic import BaseModel, Field
import os
from github import Github


class PostSuggestionInput(BaseModel):
    repo_full_name: str = Field(...)
    pr_number: int = Field(...)
    file_path: str = Field(...)
    start_line: int = Field(...)
    end_line: int = Field(...)
    suggestion_body: str = Field(...)
    comment_text: str = Field(...)


class PostSuggestionToolLangAI(CrewBaseTool):
    name: str = "Post PR Review Suggestion Tool"  # ✅ type annotation added
    description: str = "Post multi-line code suggestions on GitHub PRs"
    args_schema: type[BaseModel] = PostSuggestionInput

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
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return "Error: GITHUB_TOKEN env var not set"
        g = Github(token)
        pr = g.get_repo(repo_full_name).get_pull(pr_number)
        latest_commit = pr.get_commits()[-1]
        formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"
        pr.create_review_comment(
            body=f"{comment_text}\n{formatted_suggestion}",
            commit_id=latest_commit.sha,
            path=file_path,
            start_line=start_line,
            line=end_line,
            side="RIGHT",
        )
        return f"Successfully posted suggestion for {file_path} in PR #{pr_number}"
