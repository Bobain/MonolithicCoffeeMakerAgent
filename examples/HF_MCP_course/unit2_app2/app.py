# app.py
# co-author : Gemini 2.5 Pro Preview

# --- Prerequisites ---
# (Same as before)

import asyncio
import gradio as gr
from functools import partial
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# Assuming dummy_mcp_server_tools.py defines PORT
from dummy_mcp_server_tools import PORT

# --- Configuration ---
OLLAMA_MODEL = "llama3.2:1b"
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"

# FIX 2: A much more explicit ReAct prompt showing a full conversation turn
SYSTEM_PROMPT = """
You are a helpful assistant. You have access to the following tools:
<tools>
To use a tool, you must use the following format:
Thought: The user is asking for the weather. I need to use the 'get_weather' tool.
Action: get_weather
Action Input: {"location": "Paris"}

After you get the observation from the tool, you must use it to answer the question.
Your final answer should be in the following format:
Thought: I have the weather information. I can now answer the user's question.
Answer: The weather in Paris is Sunny, 72°F.
"""


async def get_agent(tools_spec: McpToolSpec) -> ReActAgent:
    """Creates and configures the ReActAgent."""
    print("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    print(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    print("Initializing LLM and Agent...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm

    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,  # Using the new, more detailed prompt
        verbose=True
    )
    print("ReActAgent created.")
    return agent


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent):
    """
    Runs the agent using stream_chat and yields the response token by token.
    This version is more robust and handles empty final responses.
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

    # FIX 1: Make the streaming loop more robust
    response_text = ""
    token_found = False
    # Use the corrected async_response_gen() call
    async for token in response_stream.async_response_gen():
        response_text += token
        token_found = True
        yield thinking_log + response_text

    # If the generator was empty (no final 'Answer:' from the LLM),
    # construct a fallback response from the last observation.
    if not token_found and response_stream.source_nodes:
        last_observation = response_stream.source_nodes[-1].raw_output
        fallback_response = f"I found some information but couldn't formulate a final answer. Here is the raw tool output:\n\n`{str(last_observation)}`"
        yield thinking_log + fallback_response
    elif not token_found:
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