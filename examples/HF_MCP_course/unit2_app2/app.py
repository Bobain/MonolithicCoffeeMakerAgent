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
from functools import partial  # FIX: Import partial
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# Assuming dummy_mcp_server_tools.py defines PORT
from dummy_mcp_server_tools import PORT

# --- Configuration ---
OLLAMA_MODEL = "llama3.2:1b"
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"
SYSTEM_PROMPT = "You are a helpful assistant. Be concise and use the tools provided when necessary to answer questions."


async def get_agent(tools_spec: McpToolSpec) -> ReActAgent:
    """Creates and configures the ReActAgent."""
    print("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    print(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    print("Initializing LLM and Agent...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm  # Set the LLM in global settings for LlamaIndex

    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        verbose=True
    )
    print("ReActAgent created.")
    return agent


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent):
    """
    Runs the agent using stream_chat and yields the response token by token.
    This function is a generator, which is what Gradio needs for streaming.
    """
    print(f"Streaming response for message: '{message}'")

    response_stream = await agent.stream_chat(message)

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
    async for token in response_stream.async_response_gen:
        response_text += token
        yield thinking_log + response_text  # Yield the updated full string


async def main():
    """Initializes resources and launches the Gradio application."""
    mcp_client = None  # Initialize for the finally block
    try:
        mcp_client = BasicMCPClient(MCP_SERVER_TOOL_URL)
        mcp_tools_spec = McpToolSpec(mcp_client)
        agent = await get_agent(mcp_tools_spec)

        # FIX: Use functools.partial to pre-fill the 'agent' argument.
        # This gives Gradio a callable that it can pass 'message' and 'history' to,
        # and that callable *is* our async generator.
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