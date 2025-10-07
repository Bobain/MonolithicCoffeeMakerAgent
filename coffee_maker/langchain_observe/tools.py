from coffee_maker.utils.github import (
    get_pr_file_content as _get_pr_file_content,
    get_pr_modified_files as _get_pr_modified_files,
    post_suggestion_in_pr_review as _post_suggestion_in_pr_review,
)

from langfuse import observe
from langchain.agents import Tool
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper


def make_func_a_tool(name, func):
    import json

    @observe
    def _func(tool_input):
        # Handle both string and dict inputs from the agent
        if isinstance(tool_input, str):
            # Try to parse as JSON
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                # If parsing fails, check if it looks like JSON with code blocks
                # Remove ```json and ``` markers that the LLM sometimes adds
                cleaned = tool_input.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]  # Remove ```json
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]  # Remove ```
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]  # Remove trailing ```
                cleaned = cleaned.strip()

                try:
                    tool_input = json.loads(cleaned)
                except json.JSONDecodeError:
                    # If it's still not JSON, pass it as-is
                    pass

        # If tool_input is a dict, expand it as kwargs
        if isinstance(tool_input, dict):
            return func(**tool_input)
        else:
            # Otherwise pass as single argument
            return func(tool_input)

    _func.__doc__ = func.__doc__

    return Tool(name, _func, description=func.__doc__)


get_pr_modified_files = make_func_a_tool("get_pr_modified_files", _get_pr_modified_files)
get_pr_file_content = make_func_a_tool("get_pr_file_content", _get_pr_file_content)
post_suggestion_in_pr_review = make_func_a_tool("post_suggestion_in_pr_review", _post_suggestion_in_pr_review)


# Préparer les outils GitHub
# L'API Wrapper gère les appels à l'API GitHub
# Le Toolkit est une collection d'outils prêts à l'emploi pour GitHub
try:
    _github_toolkit = GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper())
    github_tools = _github_toolkit.get_tools()
except Exception:
    # If GitHub API wrapper initialization fails (e.g., missing GITHUB_APP_ID),
    # provide an empty list of tools
    github_tools = []
