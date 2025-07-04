# app.py
# co-author : Gemini 2.5 Pro Preview

# --- Prerequisites ---
# 1. Start Ollama server in a terminal:
#    ollama serve
#
# 2. Make sure you have a capable model. 1B models struggle with ReAct.
#    RECOMMENDED: ollama pull llama3:8b
#    (or phi3, qwen2, etc.)
#
# 3. Start the dummy MCP server in another terminal:
#    python dummy_mcp_server_tools.py

import asyncio
import gradio as gr
from functools import partial
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

from dummy_mcp_server_tools import PORT

# --- Configuration ---
# FIX 1: Use a more capable model for reliable tool use
OLLAMA_MODEL = "llama3:8b"  # Changed from llama3.2:1b
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"

# FIX 2: Even more direct and simple prompt. We removed the <tools> placeholder
# as from_tools() often injects tool descriptions automatically.
SYSTEM_PROMPT = """
You are a helpful assistant who can get the weather.
To use the get_weather tool, you MUST respond in this format:
Thought: I need to use the get_weather tool.
Action: get_weather
Action Input: {"location": "the user's requested location"}

After you get the observation from the tool, you MUST answer the user's question.
"""


async def get_agent(tools_spec: McpToolSpec) -> ReActAgent:
    """Creates and configures the ReActAgent."""
    print("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    print(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    print("Initializing LLM and Agent...")
    # Increase max_iterations to give the agent more chances to self-correct if needed
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm

    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=10,  # Give it a few more tries
        verbose=True
    )
    print("ReActAgent created.")
    return agent


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent):
    """
    Runs the agent using stream_chat and yields the response token by token.
    """
    print(f"Streaming response for message: '{message}'")

    response_stream = agent.stream_chat(message)

    thinking_log = ""
    if response_stream.source_nodes:
        thinking_log = "🤔 **Thinking Process & Tool Calls:**\n\n```\n"
        for node in response_stream.source_nodes:
            tool_name = node.raw_input.get("tool_name", "unknown_tool")
            tool_output_str = str(node.raw_output).strip()
            thinking_log += f"Tool: {tool_name}\nResult: {tool_output_str}\n---\n"
        thinking_log += "```\n\n"
        yield thinking_log

    response_text = ""
    async for token in response_stream.async_response_gen():
        response_text += token
        yield thinking_log + response_text

    # Fallback logic if the generator was empty
    if not response_text and response_stream.source_nodes:
        last_observation = response_stream.source_nodes[-1].raw_output
        fallback_response = f"I found some information but couldn't formulate a final answer. Here is the raw tool output:\n\n`{str(last_observation)}`"
        yield thinking_log + fallback_response
    elif not response_text:
        fallback_response = "I was unable to process the request or find an answer."
        yield thinking_log + fallback_response


async def main():
    """Initializes resources and launches the Gradio application."""
    mcp_client = None
    try:
        mcp_client = BasicMCPClient(MCP_SERVER_TOOL_URL)
        mcp_tools_spec = McpToolSpec(mcp_client)
        agent = await get_agent(mcp_tools_spec)

        agent_fn_with_context = partial(run_agent_chat_stream, agent=agent)

        demo = gr.ChatInterface(
            fn=agent_fn_with_context,
            chatbot=gr.Chatbot(label="Agent Chat", height=600, show_copy_button=True),
            textbox=gr.Textbox(placeholder="Ask me something...", label="Your Message"),
            examples=["What is the weather in Paris?"],
            title="Agent with MCP Tools (ReAct)",
            description="This agent uses an Ollama model and can use tools via MCP.",
        )

        print("Launching Gradio interface...")
        demo.launch()

    except Exception as e:
        print(f"An error occurred in main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application cleanup (no explicit MCP disconnect needed for BasicMCPClient).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nApplication shutting down.")