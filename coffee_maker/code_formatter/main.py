# coffee_maker/code_formatter/main.py
import os
from dotenv import load_dotenv
from crewai import Crew, Process
from langfuse.langchain import CallbackHandler
from coffee_maker.code_formatter.tasks import create_review_task, create_refactor_task
from github import Github
from dotenv import load_dotenv
from langfuse import Langfuse

langfuse = Langfuse()

load_dotenv()


# HELPER FUNCTION: Moved here from tasks.py, as data fetching is an orchestration concern.
def _get_pr_file_content(repo_full_name, pr_number, file_path):
    """Helper function to get a file's current content from a specific PR."""
    try:
        # Authenticate with GitHub using a Personal Access Token
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return "Error: The GITHUB_TOKEN environment variable is not set. Please set it in your .env file."

        g = Github(token)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        contents = repo.get_contents(file_path, ref=pull_request.head.sha)
        return contents.decoded_content.decode("utf-8")
    except Exception as e:
        print(f"ERROR: Could not fetch content for '{file_path}' from GitHub. Details: {e}")
        return None


def run_code_formatter(repo_full_name, pr_number, files_to_review, run_metadata={}):
    """
    Initializes and runs the crew to refactor and post suggestions for each file in a PR.
    """
    load_dotenv()

    try:
        handler = CallbackHandler()
        handler.session.update(metadata=run_metadata)
        langfuse.init()
    except Exception as e:
        print(f"ERROR: Langfuse could not be initialized. Check environment variables. Details: {e}")
        return

    all_tasks = []
    print(f"--- Fetching file contents and creating tasks for {len(files_to_review)} files ---")
    for file_path in files_to_review:
        print(f"  - Processing file: {file_path}")

        # CHANGED: Fetch content here in the main loop
        file_content = _get_pr_file_content(repo_full_name, pr_number, file_path)

        if file_content is None:
            print(f"  - Skipping tasks for {file_path} as its content could not be fetched.")
            continue

        refactor_task = create_refactor_task(file_path=file_path, file_content=file_content)
        review_task_instance = create_review_task(
            repo_full_name=repo_full_name, pr_number=pr_number, file_path=file_path
        )
        all_tasks.extend([refactor_task, review_task_instance])

    if not all_tasks:
        print("No tasks were created. Aborting crew kickoff.")
        return

    code_formatter_crew = Crew(tasks=all_tasks, process=Process.sequential, callbacks=[handler], verbose=2)

    print("\n--- Kicking off Crew Execution ---")
    result = code_formatter_crew.kickoff()

    print("\n--- Crew Execution Finished ---")
    print("Result:")
    print(result)

    return result


# ... (if __name__ == '__main__' block remains the same for testing)
if __name__ == "__main__":
    REPO_NAME = "crewai/crewai"
    PR_NUM = 123
    FILES_IN_PR = ["src/crewai/agent.py"]

    metadata = {"repo": REPO_NAME, "pr_number": PR_NUM, "run_trigger": "manual_test"}

    run_code_formatter(repo_full_name=REPO_NAME, pr_number=PR_NUM, files_to_review=FILES_IN_PR, run_metadata=metadata)
