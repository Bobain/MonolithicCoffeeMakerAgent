import argparse
import os

from dotenv import load_dotenv
from mcp import StdioServerParameters
from smolagents import CodeAgent, InferenceClientModel, ToolCollection

from coffee_maker.utils.text_to_speech import text_to_speech_pyttsx3

"""
Example:
    python server_pubmedmcp.py "Que faire si j'ai la gueule de bois? j'ai mal à la tête et envie de vomir..."
    python server_pubmedmcp.py "Please find a remedy for hangover."
"""


load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Un script qui traite un argument positionnel.")
    parser.add_argument("user_prompt", help="The text input from the user")

    args = parser.parse_args()

    server_parameters = StdioServerParameters(
        command="poetry",
        args=["run", "pubmedmcp"],  # If pubmedmcp@0.1.3 provides a 'pubmedmcp' command
        # Add any arguments pubmedmcp itself needs after "pubmedmcp"
        # For example: args=["run", "pubmedmcp", "--port", "8080"]
        env=os.environ.copy(),  # Pass the current environment; poetry run handles the venv
    )

    model = InferenceClientModel()

    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        print("Here are the tools on the MCP server we connected to:")
        print("\n".join(f"{tool.name}: {tool.description}" for tool in tool_collection.tools))
        agent = CodeAgent(tools=[*tool_collection.tools], model=model, add_base_tools=True)
        text_to_speech_pyttsx3(args.user_prompt)
        answer = agent.run(args.user_prompt)
        print(f"{answer=}")
        if isinstance(answer, str):
            text_to_speech_pyttsx3("My answer is :")
            text_to_speech_pyttsx3(answer)
        elif isinstance(answer, list):
            text_to_speech_pyttsx3("My answer is :")
            for i, item in enumerate(answer):
                text_to_speech_pyttsx3(f"{i} : {item}")
        else:
            text_to_speech_pyttsx3("I don't know how to interpret the answer : please read it")


if __name__ == "__main__":
    main()
