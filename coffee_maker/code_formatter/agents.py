# coffee_maker/code_formatter/agents.py

import langfuse
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from coffee_maker.code_formatter.tools import post_suggestion
from dotenv import load_dotenv

load_dotenv()

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
except Exception as e:
    print(f"ERROR: Failed to initialize Google Gemini LLM. Is the GOOGLE_API_KEY set? Details: {e}")
    raise


def create_code_formatter_agents():
    """
    Creates the agent responsible for analyzing and refactoring code.
    """
    try:
        style_guide_prompt = langfuse.get_prompt("styleguide.md")
    except Exception as e:
        print(f"ERROR: Could not fetch prompts from Langfuse. Check API keys and prompt names. Details: {e}")
        raise

    senior_engineer_agent = Agent(
        role="Senior Software Engineer",
        goal="Re-format a Python code file to ensure the best practice of a styleguide file are enforced.",
        backstory=f"""You are a meticulous Senior Software Engineer, renowned for your ability
        to enforce high-quality code standards. Your primary reference is the official style guide,
        which you follow without deviation.
        --- STYLE GUIDE ---
        {style_guide_prompt.prompt}
        """,
        llm=llm,
        tools=[],
        allow_delegation=False,
        verbose=True,
    )
    return {"senior_engineer": senior_engineer_agent}


def create_pr_reviewer_agent():
    """
    Creates the agent responsible for posting the review suggestions on GitHub.
    """
    return Agent(
        role="GitHub Code Reviewer",
        goal="Post the refactored code as actionable suggestions directly on the relevant lines of the files in the GitHub pull request.",
        backstory="""You are an automated code review assistant. Your purpose is to
        review code submitted in pull requests and provide concrete, multi-line suggestions
        for improvement based on the company's style guide. You only offer suggestions
        to help the original author improve their work.""",
        llm=llm,
        tools=[post_suggestion],
        allow_delegation=False,
        verbose=True,
    )
