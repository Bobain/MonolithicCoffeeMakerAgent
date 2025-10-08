"""
Main Orchestration Module for Code Formatter CrewAI System.

This module serves as the entry point for the automated code formatting and review
system. It orchestrates the entire workflow from fetching PR files to posting
review suggestions on GitHub.

Workflow:
    1. Fetch list of modified files from the specified GitHub PR
    2. For each file, fetch its content from the PR's head commit
    3. Spin up a formatting flow that analyzes code and posts review suggestions
    4. Execute each flow sequentially so the reviewer tool can publish comments
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

from datetime import datetime
import logging
import os

from dotenv import load_dotenv

load_dotenv()

# --- CORRECT LANGFUSE IMPORTS ---
from langfuse import Langfuse, observe

# Absolute imports from the project's source root 'coffee_maker'
from coffee_maker.utils.github import get_pr_file_content, get_pr_modified_files
from coffee_maker.code_formatter.crewai.agents import create_code_formatter_agents, create_pr_reviewer_agent
from coffee_maker.code_formatter.crewai.flow import create_code_formatter_flow

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
    files_to_review = get_pr_modified_files(repo_full_name, pr_number)

    if not files_to_review:
        logger.warning(f"No modified files found in PR #{pr_number}. Aborting.")
        return None

    python_files = [file for file in files_to_review if file["filename"].endswith(".py")]

    if not python_files:
        logger.warning("No Python files to process in this PR.")
        return None

    logger.info(f"Found {len(python_files)} Python files in PR #{pr_number}:")
    for file_info in python_files:
        logger.info(f"  - {file_info['filename']}")

    # Initialize agents
    logger.info("Initializing agents")
    agents = create_code_formatter_agents(langfuse_client)
    logger.info(f"Created {len(agents)} agents: {list(agents.keys())}")

    formatter_agent = agents.get("senior_engineer")
    if formatter_agent is None:
        logger.error("Senior engineer agent could not be initialized.")
        return None

    langfuse_client.update_current_trace(
        session_id=f"pr-review-{repo_full_name}-{pr_number}-{datetime.now().isoformat()}",
        metadata={
            "repo": repo_full_name,
            "pr_number": pr_number,
            "files_count": len(python_files),
        },
    )

    flow_results: list[dict[str, str | None]] = []
    processed_files = 0

    for file_info in python_files:
        file_path = file_info["filename"]
        logger.info(f"Processing file: {file_path}")
        # --- Fetch original content ---
        file_content = get_pr_file_content(repo_full_name, pr_number, file_path)
        if file_content is None:
            logger.warning(f"Skipping {file_path} - could not fetch content")
            continue
        if not file_content.strip():
            logger.info("Skipping %s - no substantive content in file", file_path)
            continue

        pr_reviewer_agent = create_pr_reviewer_agent(langfuse_client, pr_number, repo_full_name, file_path)
        reviewer_agent = pr_reviewer_agent.get("pull_request_reviewer")
        if reviewer_agent is None:
            logger.warning("Skipping %s - reviewer agent could not be initialized", file_path)
            continue

        flow = create_code_formatter_flow(
            formatter_agent=formatter_agent,
            reviewer_agent=reviewer_agent,
            langfuse_client=langfuse_client,
            file_path=file_path,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_content=file_content,
            patch=file_info.get("patch"),
        )

        logger.info("Launching formatting flow for %s", file_path)
        try:
            flow.kickoff()
            processed_files += 1
            flow_results.append(
                {
                    "file_path": file_path,
                    "reformat_result": flow.state.reformat_result,
                    "review_result": flow.state.review_result,
                }
            )
            langfuse_client.create_event(
                name=f"code_formatter_flow_{file_path}",
                input=(flow.state.reformat_prompt or "")[:500],
                output=(flow.state.review_result or "")[:1000],
                metadata={
                    "file_path": file_path,
                    "flow_type": "formatter_review",
                    "success": True,
                },
            )
        except Exception as exc:  # pragma: no cover - runtime failures
            logger.error("Flow execution failed for %s", file_path, exc_info=True)
            flow_results.append({"file_path": file_path, "error": str(exc)})
            langfuse_client.create_event(
                name=f"code_formatter_flow_{file_path}",
                input=file_content[:500],
                output=str(exc)[:1000],
                metadata={
                    "file_path": file_path,
                    "flow_type": "formatter_review",
                    "success": False,
                },
            )

    if processed_files == 0:
        logger.warning("No flows were executed. Aborting.")
        langfuse_client.flush()
        return None

    logger.info("--- Flow Execution Finished ---")
    logger.info("Processed %s file(s)", processed_files)

    langfuse_client.flush()
    return flow_results


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run code formatter on a GitHub PR")
    parser.add_argument("--repo", default="Bobain/MonolithicCoffeeMakerAgent", help="Full repository name (owner/repo)")
    parser.add_argument("--pr", type=int, default=110, help="Pull request number")
    args = parser.parse_args()

    run_code_formatter(repo_full_name=args.repo, pr_number=args.pr)
