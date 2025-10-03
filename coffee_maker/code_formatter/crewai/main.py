"""
Main Orchestration Module for Code Formatter CrewAI System.

This module serves as the entry point for the automated code formatting and review
system. It orchestrates the entire workflow from fetching PR files to posting
review suggestions on GitHub.

Workflow:
    1. Fetch list of modified files from the specified GitHub PR
    2. For each file, fetch its content from the PR's head commit
    3. Create a refactor task to analyze and suggest improvements
    4. Create a review task to post suggestions as GitHub PR comments
    5. Execute all tasks using CrewAI's sequential process
    6. Track execution in Langfuse for observability

Environment Variables Required:
    GITHUB_TOKEN: GitHub personal access token with repo permissions
    LANGFUSE_SECRET_KEY: Langfuse secret key for authentication
    LANGFUSE_PUBLIC_KEY: Langfuse public key for authentication
    LANGFUSE_HOST: Langfuse host URL (e.g., https://cloud.langfuse.com)
    GOOGLE_API_KEY: Google API key for Gemini LLM (set via langchain_google_genai)

Module-level Variables:
    langfuse_client: Global Langfuse client instance for observability

Functions:
    _get_pr_modified_files: Fetches list of modified files from a PR
    _get_pr_file_content: Fetches content of a specific file from a PR
    run_code_formatter: Main orchestration function for the entire workflow

Usage:
    Command line:
        python -m coffee_maker.code_formatter.crewai.main --repo owner/repo --pr 123

    Programmatic:
        from coffee_maker.code_formatter.crewai.main import run_code_formatter
        result = run_code_formatter("owner/repo", 123)
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

from crewai import Crew, Process
from github import Github, Auth

# --- CORRECT LANGFUSE IMPORTS ---
from langfuse import Langfuse, observe
from langfuse.langchain import CallbackHandler

# Absolute imports from the project's source root 'coffee_maker'
from coffee_maker.code_formatter.crewai.agents import create_code_formatter_agents, create_pr_reviewer_agent, llm
from coffee_maker.code_formatter.crewai.tasks import create_reformat_task, create_review_task

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- 1. Load environment variables FIRST ---
load_dotenv()

# --- 2. Initialize the global Langfuse client ---
try:
    langfuse_client = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception:
    logger.critical("Langfuse client could not be initialized. Check environment variables.", exc_info=True)
    raise


# --- HELPER FUNCTION for fetching modified files from PR ---
@observe
def _get_pr_modified_files(repo_full_name, pr_number):
    """
    Fetches the list of modified files from a pull request.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number

    Returns:
        List of file paths that were modified in the PR, or empty list if fetch fails
    """
    logger.info(f"Fetching modified files from PR #{pr_number} in {repo_full_name}")
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            logger.error("GITHUB_TOKEN environment variable is not set.")
            return []
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        files = pull_request.get_files()
        file_list = [f.filename for f in files]
        logger.info(f"Found {len(file_list)} modified files in PR #{pr_number}")
        return file_list
    except Exception:
        logger.error(f"Could not fetch modified files from PR #{pr_number}.", exc_info=True)
        return []


# --- HELPER FUNCTION for fetching file content from GitHub ---
@observe
def _get_pr_file_content(repo_full_name, pr_number, file_path):
    """
    Fetches the content of a specific file from a PR's head commit.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number
        file_path: Path to the file in the repository

    Returns:
        File content as string, or None if fetch fails
    """
    logger.info(f"Fetching content for '{file_path}' from PR #{pr_number}")
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            logger.error("GITHUB_TOKEN environment variable is not set.")
            return None
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        contents = repo.get_contents(file_path, ref=pull_request.head.sha)
        content = contents.decoded_content.decode("utf-8")
        logger.info(f"Successfully fetched {len(content)} bytes from '{file_path}'")
        return content
    except Exception:
        logger.error(f"Could not fetch content for '{file_path}' from GitHub.", exc_info=True)
        return None


# --- MAIN ORCHESTRATION FUNCTION ---
@observe
def run_code_formatter(repo_full_name, pr_number):
    """
    Initializes and runs the crew to refactor and post suggestions for each file in a PR.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number

    Returns:
        Result from crew execution, or None if execution fails
    """
    # Fetch the list of modified files from the PR
    files_to_review = _get_pr_modified_files(repo_full_name, pr_number)

    if not files_to_review:
        logger.warning(f"No modified files found in PR #{pr_number}. Aborting.")
        return None

    logger.info(f"Found {len(files_to_review)} modified files in PR #{pr_number}:")
    for file_path in files_to_review:
        logger.info(f"  - {file_path}")

    try:
        handler = CallbackHandler()
    except Exception:
        logger.error("Langfuse Callback handler could not be created.", exc_info=True)
        return None

    # Initialize agents
    logger.info("Initializing agents")
    agents = create_code_formatter_agents(langfuse_client)
    logger.info(f"Created {len(agents)} agents: {list(agents.keys())}")

    all_tasks = []

    for file_path in files_to_review:
        logger.info(f"Processing file: {file_path}")
        # --- Fetch original content ---
        file_content = _get_pr_file_content(repo_full_name, pr_number, file_path)
        if file_content is None:
            logger.warning(f"Skipping {file_path} - could not fetch content")
            continue

        # --- Create refactor task ---
        logger.debug(f"Creating refactor task for {file_path}")

        pr_reviewer_agent = create_pr_reviewer_agent(langfuse_client, repo_full_name, pr_number, file_path)
        agents.update(pr_reviewer_agent)
        refactor_task_instance = create_reformat_task(
            agent=agents["senior_engineer"],
            langfuse_client=langfuse_client,
            file_path=file_path,
            file_content=file_content,
        )

        # --- Create review task that depends on refactor task ---
        logger.debug(f"Creating review task for {file_path}")
        review_task_instance = create_review_task(
            agent=agents["pull_request_reviewer"],
            langfuse_client=langfuse_client,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            refactor_task=refactor_task_instance,
        )

        # ✅ CRITICAL: Set the context dependency
        review_task_instance.context = [refactor_task_instance]
        logger.debug(f"Set context dependency for review task on {file_path}")

        all_tasks.extend([refactor_task_instance, review_task_instance])
        logger.info(f"Added 2 tasks for {file_path} (total: {len(all_tasks)} tasks)")

    if not all_tasks:
        logger.warning("No tasks were created. Aborting crew kickoff.")
        langfuse_client.flush()
        return None

    logger.info(f"Creating crew with {len(agents)} agents and {len(all_tasks)} tasks")
    agents_list = list(agents.values())
    code_formatter_crew = Crew(
        agents=agents_list, tasks=all_tasks, process=Process.sequential, callbacks=[handler], verbose=True, llm=llm
    )

    logger.info("--- Kicking off Crew Execution ---")
    langfuse_client.update_current_trace(
        session_id=f"pr-review-{repo_full_name}-{pr_number}",
        metadata={
            "repo": repo_full_name,
            "pr_number": pr_number,
            "files_count": len(files_to_review),
            "tasks_count": len(all_tasks),
        },
    )

    # Wrap crew kickoff to capture task I/O
    result = code_formatter_crew.kickoff()

    # Log task outputs to Langfuse
    for i, task in enumerate(all_tasks):
        task_type = "refactor" if i % 2 == 0 else "review"
        file_idx = i // 2
        langfuse_client.generation(
            name=f"{task_type}_task_{files_to_review[file_idx] if file_idx < len(files_to_review) else 'unknown'}",
            input=task.description[:500] if hasattr(task, "description") else "N/A",
            output=str(task.output)[:1000] if hasattr(task, "output") and task.output else "N/A",
            metadata={
                "task_type": task_type,
                "file_path": files_to_review[file_idx] if file_idx < len(files_to_review) else "unknown",
                "expected_output": task.expected_output[:200] if hasattr(task, "expected_output") else "N/A",
            },
        )

    logger.info("--- Crew Execution Finished ---")
    logger.info(f"Result: {result}")

    langfuse_client.flush()
    return result


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run code formatter on a GitHub PR")
    parser.add_argument("--repo", default="Bobain/MonolithicCoffeeMakerAgent", help="Full repository name (owner/repo)")
    parser.add_argument("--pr", type=int, default=110, help="Pull request number")
    args = parser.parse_args()

    run_code_formatter(repo_full_name=args.repo, pr_number=args.pr)
