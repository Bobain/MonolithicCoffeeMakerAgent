# coffee_maker/code_formatter/main.py

import os
import sys
from crewai import Crew, Process
from dotenv import load_dotenv
from github import Github

# --- 1. Load environment variables FIRST ---
load_dotenv()

# --- CORRECT LANGFUSE IMPORTS ---
from langfuse import Langfuse
from langfuse import observe
from langfuse.langchain import CallbackHandler

# Absolute imports from the project's source root 'coffee_maker'
from coffee_maker.code_formatter.agents import create_code_formatter_agents, create_pr_reviewer_agent, llm
from coffee_maker.code_formatter.tasks import create_review_task, create_refactor_task

# --- 2. Initialize the global Langfuse client ---
try:
    langfuse_client = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception as e:
    print(f"CRITICAL ERROR: Langfuse client could not be initialized. Check environment variables.")
    print(f"Details: {e}")
    sys.exit(1)


# --- HELPER FUNCTION for fetching file content from GitHub ---
@observe
def _get_pr_file_content(repo_full_name, pr_number, file_path):
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("ERROR: GITHUB_TOKEN environment variable is not set.")
            return None
        g = Github(token)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        contents = repo.get_contents(file_path, ref=pull_request.head.sha)
        return contents.decoded_content.decode("utf-8")
    except Exception as e:
        print(f"ERROR: Could not fetch content for '{file_path}' from GitHub. Details: {e}")
        return None


# --- MAIN ORCHESTRATION FUNCTION ---
@observe
def run_code_formatter(repo_full_name, pr_number, files_to_review, run_metadata={}):
    """
    Initializes and runs the crew to refactor and post suggestions for each file in a PR.
    """
    try:
        handler = CallbackHandler()
    except Exception as e:
        print(f"ERROR: Langfuse Callback handler could not be created. Details: {e}")
        return

    # Initialize agents
    agents = create_code_formatter_agents(langfuse_client)
    agents.update(create_pr_reviewer_agent(langfuse_client))

    all_tasks = []

    for file_path in files_to_review:
        # --- Fetch original content ---
        file_content = _get_pr_file_content(repo_full_name, pr_number, file_path)
        if file_content is None:
            continue

        # --- Create refactor task ---
        refactor_task_instance = create_refactor_task(
            agent=agents["senior_engineer"],
            langfuse_client=langfuse_client,
            file_path=file_path,
            file_content=file_content,
        )

        # --- Create review task that depends on refactor task ---
        review_task_instance = create_review_task(
            agent=agents["pull_request_reviewer"],
            langfuse_client=langfuse_client,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            reformatted_file_content=refactor_task_instance,  # <-- pass Task object
        )

        all_tasks.extend([refactor_task_instance, review_task_instance])

    if not all_tasks:
        print("No tasks were created. Aborting crew kickoff.")
        langfuse_client.flush()
        return

    agents_list = list(agents.values())
    code_formatter_crew = Crew(
        agents=agents_list, tasks=all_tasks, process=Process.sequential, callbacks=[handler], verbose=True, llm=llm
    )

    print("\n--- Kicking off Crew Execution ---")
    langfuse_client.update_current_trace(session_id=f"pr-review-{repo_full_name}-{pr_number}")
    result = code_formatter_crew.kickoff()
    print("\n--- Crew Execution Finished ---")
    print("Result:")
    print(result)

    langfuse_client.flush()
    return result


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    REPO_NAME = "Bobain/MonolithicCoffeeMakerAgent"
    PR_NUM = 108
    FILES_IN_PR = ["coffee_maker/code_formatter/main.py"]
    metadata = {"repo": REPO_NAME, "pr_number": PR_NUM, "run_trigger": "manual_test"}
    run_code_formatter(repo_full_name=REPO_NAME, pr_number=PR_NUM, files_to_review=FILES_IN_PR, run_metadata=metadata)
