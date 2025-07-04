# app.py
# co-author : Gemini 2.5 Pro Preview

# --- Prerequisites ---
# 1. Start Ollama server in a terminal:
#    ollama serve
#
# 2. Make sure you have the model:
#    ollama pull llama3.2:1b
#
# 3. Start the dummy MCP server in another terminal:
#    python dummy_mcp_server_tools.py

import asyncio

import gradio as gr
from dummy_mcp_server_tools import PORT
from llama_index.core import Settings
from llama_index.core.agent.workflow import (FunctionAgent, ToolCall,
                                             ToolCallResult)
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# --- Configuration ---
OLLAMA_MODEL = "llama3.2:1b"
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"
SYSTEM_PROMPT = "You are a helpful assistant."


async def get_agent(tools: McpToolSpec) -> tuple[FunctionAgent, Context]:
    """Creates and configures the FunctionAgent."""
    tool_list = await tools.to_tool_list_async()
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can use tools to answer questions.",
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    agent_context = Context(agent)
    return agent, agent_context


async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
) -> str:
    """Runs the agent with the user's message and streams the events."""
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned: {event.tool_output}")

    response = await handler
    return str(response)


async def ask_model(message, history, agent, agent_context):
    return await handle_user_message(message, agent, agent_context, verbose=True)


async def main():
    """Initializes resources and launches the Gradio application."""
    mcp_client = BasicMCPClient(MCP_SERVER_TOOL_URL)
    try:
        mcp_tools = McpToolSpec(mcp_client)
        agent, agent_context = await get_agent(mcp_tools)

        # The `fn` for ChatInterface can be an async function directly.
        # Gradio will handle the event loop.
        demo = gr.ChatInterface(
            fn=lambda message, history: ask_model(message, history, agent, agent_context),
            type="messages",
            examples=["What is the sentiment of the text 'This is awesome'?"],
            title="Agent with MCP Tools",
            description="This is a simple agent that uses MCP tools to answer questions.",
        )

        print("Launching Gradio interface...")
        demo.launch()

    finally:
        print("Disconnecting MCP client...")
        mcp_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
