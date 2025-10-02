# coffee_maker/code_formatter/agents.py

from crewai import Agent
import logging

logger = logging.getLogger(__name__)

from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse, observe
from coffee_maker.code_formatter.crewai.tools import PostSuggestionToolLangAI


# --- LLM Configuration ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
except Exception as e:
    print(f"ERROR: Failed to initialize Google Gemini LLM. Is the GOOGLE_API_KEY set? Details: {e}")
    raise


@observe
def create_code_formatter_agents(langfuse_client: Langfuse):
    """
    Creates the agent responsible for analyzing and refactoring code.
    """
    try:
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as e:
        print(f"ERROR: Could not fetch prompts from Langfuse. Details: {e}")
        raise

    senior_engineer_agent = Agent(
        role="Senior Software Engineer",
        goal=goal_prompt.prompt,
        backstory=backstory_prompt.prompt,
        tools=[],  # no tools for this agent
        allow_delegation=False,
        verbose=True,
    )
    logger.debug(f"Created senior_engineer_agent: {senior_engineer_agent}")
    return {"senior_engineer": senior_engineer_agent}


def create_pr_reviewer_agent(langfuse_client: Langfuse):
    """
    Creates the agent responsible for posting review suggestions on GitHub.
    """
    return {
        "pull_request_reviewer": Agent(
            role="GitHub Code Reviewer",
            goal=(
                "Post the refactored code as actionable suggestions directly on the "
                "relevant lines of the files in the GitHub pull request."
            ),
            backstory="""You are an automated code review assistant. Your purpose is to
            review code submitted in pull requests and provide concrete, multi-line suggestions
            for improvement based on the company's style guide. You only offer suggestions
            to help the original author improve their work.""",
            tools=[PostSuggestionToolLangAI()],  # ✅ CrewAI BaseTool instance
            allow_delegation=False,
            verbose=True,
        )
    }
