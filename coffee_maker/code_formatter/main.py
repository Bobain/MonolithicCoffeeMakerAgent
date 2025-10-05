"""
Main Orchestration Module for Code Formatter System.

This module serves as a simplified entry point for automated code formatting
and review. It directly uses LangChain agents without CrewAI orchestration.

Workflow:
    1. Fetch list of modified files from the specified GitHub PR
    2. For each file (or single file if specified), fetch its content
    3. Run the formatter agent to analyze and suggest improvements
    4. Parse the agent's output to extract suggestions
    5. Post each suggestion as a GitHub PR review comment

Environment Variables Required:
    GITHUB_TOKEN: GitHub personal access token with repo permissions
    LANGFUSE_SECRET_KEY: Langfuse secret key for authentication
    LANGFUSE_PUBLIC_KEY: Langfuse public key for authentication
    LANGFUSE_HOST: Langfuse host URL (e.g., https://cloud.langfuse.com)
    GOOGLE_API_KEY: Google API key for Gemini LLM

Functions:
    run_code_formatter: Main orchestration function for the entire workflow

Usage:
    Command line:
        python -m coffee_maker.code_formatter.main --repo owner/repo --pr 123
        python -m coffee_maker.code_formatter.main --repo owner/repo --pr 123 --file path/to/file.py

    Programmatic:
        from coffee_maker.code_formatter.main import run_code_formatter
        result = run_code_formatter("owner/repo", 123)
        result = run_code_formatter("owner/repo", 123, file_path="path/to/file.py")
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from langfuse import Langfuse, observe

from coffee_maker.code_formatter.agents import create_langchain_code_formatter_agent
from coffee_maker.code_formatter.parser import parse_reformatted_output
from coffee_maker.utils.github import get_pr_file_content, get_pr_modified_files, post_suggestion_in_pr_review

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# --- Initialize the global Langfuse client ---
try:
    langfuse_client = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception:
    logger.critical("Langfuse client could not be initialized. Check environment variables.", exc_info=True)
    raise


async def _process_single_file(
    agent_config: dict,
    file_path: str,
    file_content: str,
    repo_full_name: str,
    pr_number: int,
) -> dict:
    """
    Process a single file through the formatter agent and post suggestions.

    Args:
        agent_config: LangChain agent configuration dictionary
        file_path: Path to the file in the repository
        file_content: Content of the file
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number

    Returns:
        Dictionary with processing results including file_path, suggestions_count, and any errors
    """
    logger.info(f"Processing file: {file_path}")

    try:
        # Build the prompt for the agent
        prompt = agent_config["prompt"]
        llm = agent_config["llm"]

        # Invoke the agent with file content
        input_data = {
            "input": f"File path: {file_path}\n\nFile content:\n{file_content}",
        }

        logger.info(f"Invoking formatter agent for {file_path}")
        chain = prompt | llm
        response = await chain.ainvoke(input_data)

        # Extract the content from the response
        if hasattr(response, "content"):
            agent_output = response.content
        else:
            agent_output = str(response)

        logger.info(f"Agent output received for {file_path} ({len(agent_output)} chars)")

        # Parse the agent output
        suggestions = parse_reformatted_output(agent_output)
        logger.info(f"Parsed {len(suggestions)} suggestions for {file_path}")

        # Post each suggestion to GitHub
        posted_count = 0
        for idx, suggestion in enumerate(suggestions, 1):
            try:
                logger.info(
                    f"Posting suggestion {idx}/{len(suggestions)} for {file_path} "
                    f"(lines {suggestion['start_line']}-{suggestion['end_line']})"
                )

                post_suggestion_in_pr_review(
                    repo_full_name=repo_full_name,
                    pr_number=pr_number,
                    file_path=file_path,
                    start_line=suggestion["start_line"],
                    end_line=suggestion["end_line"],
                    suggestion_body=suggestion["suggestion_body"],
                    comment_text=suggestion["comment_text"],
                )
                posted_count += 1

            except Exception as post_error:
                logger.error(
                    f"Failed to post suggestion {idx} for {file_path}: {post_error}",
                    exc_info=True,
                )

        logger.info(f"Successfully posted {posted_count}/{len(suggestions)} suggestions for {file_path}")

        return {
            "file_path": file_path,
            "suggestions_count": len(suggestions),
            "posted_count": posted_count,
            "success": True,
        }

    except Exception as exc:
        logger.error(f"Failed to process file {file_path}: {exc}", exc_info=True)
        return {
            "file_path": file_path,
            "error": str(exc),
            "success": False,
        }


@observe
async def run_code_formatter(
    repo_full_name: str,
    pr_number: int,
    file_path: Optional[str] = None,
) -> list[dict]:
    """
    Run the code formatter on files in a GitHub pull request.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number
        file_path: Optional specific file path to process. If None, processes all Python files in the PR.

    Returns:
        List of dictionaries containing processing results for each file
    """
    logger.info(f"Starting code formatter for {repo_full_name} PR #{pr_number}")

    # Initialize Langfuse trace
    langfuse_client.update_current_trace(
        session_id=f"pr-review-{repo_full_name}-{pr_number}-{datetime.now().isoformat()}",
        metadata={
            "repo": repo_full_name,
            "pr_number": pr_number,
            "file_path": file_path,
        },
    )

    # Create the formatter agent
    logger.info("Initializing formatter agent")
    agent_config = create_langchain_code_formatter_agent(langfuse_client)
    logger.info("Formatter agent initialized")

    # Determine which files to process
    if file_path:
        # Process only the specified file
        logger.info(f"Processing single file: {file_path}")
        file_content = get_pr_file_content(repo_full_name, pr_number, file_path)

        if file_content is None:
            logger.error(f"Could not fetch content for {file_path}")
            return []

        if not file_content.strip():
            logger.warning(f"File {file_path} has no content")
            return []

        files_to_process = [{"filename": file_path, "content": file_content}]

    else:
        # Fetch all modified files from the PR
        files_info = get_pr_modified_files(repo_full_name, pr_number)

        if not files_info:
            logger.warning(f"No modified files found in PR #{pr_number}")
            return []

        # Filter for Python files
        python_files = [f for f in files_info if f["filename"].endswith(".py")]

        if not python_files:
            logger.warning("No Python files to process in this PR")
            return []

        logger.info(f"Found {len(python_files)} Python files in PR #{pr_number}")

        # Fetch content for each file
        files_to_process = []
        for file_info in python_files:
            file_name = file_info["filename"]
            content = get_pr_file_content(repo_full_name, pr_number, file_name)

            if content is None:
                logger.warning(f"Skipping {file_name} - could not fetch content")
                continue

            if not content.strip():
                logger.info(f"Skipping {file_name} - no substantive content")
                continue

            files_to_process.append({"filename": file_name, "content": content})

    if not files_to_process:
        logger.warning("No files to process after filtering")
        return []

    logger.info(f"Processing {len(files_to_process)} file(s)")

    # Process files asynchronously
    tasks = [
        _process_single_file(
            agent_config=agent_config,
            file_path=file_data["filename"],
            file_content=file_data["content"],
            repo_full_name=repo_full_name,
            pr_number=pr_number,
        )
        for file_data in files_to_process
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions that were returned
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Task failed with exception: {result}", exc_info=result)
            processed_results.append({"error": str(result), "success": False})
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success"))
    logger.info(f"Code formatter completed: {successful}/{len(processed_results)} files processed successfully")

    # Flush Langfuse to ensure all events are sent
    langfuse_client.flush()

    return processed_results


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run code formatter on a GitHub PR")
    parser.add_argument("--repo", default="Bobain/MonolithicCoffeeMakerAgent", help="Full repository name (owner/repo)")
    parser.add_argument("--pr", type=int, default=110, help="Pull request number")
    parser.add_argument("--file", type=str, default=None, help="Optional: specific file path to process")
    args = parser.parse_args()

    # Run the async function
    asyncio.run(run_code_formatter(repo_full_name=args.repo, pr_number=args.pr, file_path=args.file))
