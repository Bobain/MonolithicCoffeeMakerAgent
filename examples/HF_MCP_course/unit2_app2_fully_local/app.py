# app.py
# co-author : Gemini 2.5 Pro Preview

# ==============================================================================
# --- Prerequisites ---
#
# 1. Start the Ollama server in a dedicated terminal:
#    ollama serve
#
# 2. Pull a capable model (8B parameters recommended for ReAct):
#    ollama pull llama3:8b
#
# 3. Start the dummy MCP tool server in a second dedicated terminal:
#    poetry run python dummy_mcp_server_tools.py
#
# 5. Finally, run this application in a third terminal:
#    poetry run python app.py
#
# ==============================================================================

import asyncio
import logging
import sys
from functools import partial

import gradio as gr

# Assuming dummy_mcp_server_tools.py defines PORT
from dummy_mcp_server_tools import PORT
from llama_index.core import Settings
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# --- Logging Configuration ---
# Set up a logger to provide detailed, timestamped output to the console.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# --- Configuration ---
OLLAMA_MODEL = "llama3:8b"
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"

# This prompt is focused ONLY on getting the model to call the tool correctly.
# The final summarization step will be handled by a separate, simpler prompt.
SYSTEM_PROMPT = """
You are an expert assistant that uses tools to answer questions.
To use a tool, you MUST respond in this format, and nothing else:
Thought: The user is asking a question that requires a tool. I will use the correct tool.
Action: get_weather
Action Input: {"location": "the user's requested city"}
"""


async def get_agent_and_llm(tools_spec: McpToolSpec) -> tuple[ReActAgent, Ollama]:
    """Creates and configures the ReActAgent and the LLM instance.

    Args:
        tools_spec (McpToolSpec): The MCP tool specification to provide to the agent.

    Returns:
        tuple[ReActAgent, Ollama]: A tuple containing the configured agent and LLM instance.
    """
    log.info("--- Step: Initializing Agent and LLM ---")

    # LlamaDebugHandler will print all LLM inputs/outputs and other events.
    llama_debug_handler = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug_handler])
    Settings.callback_manager = callback_manager

    log.info("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    log.info(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    log.info("Initializing LLM...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=300)
    Settings.llm = llm

    log.info(
        f"Creating ReActAgent with the following system prompt:\n---PROMPT START---\n{SYSTEM_PROMPT}\n---PROMPT END---"
    )
    # agent = ReActAgent.from_tools(
    #     tools=tool_list,
    #     llm=llm,
    #     system_prompt=SYSTEM_PROMPT,
    #     max_iterations=5,
    #     verbose=True  # Keep verbose for LlamaIndex's own detailed prints
    # )
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    agent = ReActAgent(tools=tool_list, llm=llm, memory=memory, system_prompt=SYSTEM_PROMPT, verbose=True)
    log.info("ReActAgent created successfully.")
    return agent, llm


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent, llm: Ollama):
    """
    Runs the agent
    """
    log.info(f"--- Running Agent for user message: '{message}' ---")
    response = await agent.run(message)
    log.info(f"Agent response: {response}")
    yield str(response)


async def main():
    """Initializes resources and launches the Gradio application."""
    mcp_client = None
    try:
        mcp_client = BasicMCPClient(MCP_SERVER_TOOL_URL)
        mcp_tools_spec = McpToolSpec(mcp_client)
        agent, llm = await get_agent_and_llm(mcp_tools_spec)

        agent_fn_with_context = partial(run_agent_chat_stream, agent=agent, llm=llm)

        demo = gr.ChatInterface(
            fn=agent_fn_with_context,
            # Silences the Gradio UserWarning about message format
            chatbot=gr.Chatbot(
                label="Agent Chat", height=600, show_copy_button=True, render_markdown=True, type="messages"
            ),
            textbox=gr.Textbox(placeholder="Ask me something...", label="Your Message"),
            examples=["Quel temps fait il à Paris?"],
            title="Agent with MCP Tools (ReAct + Manual Summary)",
            description="This agent uses an Ollama model and can use tools via MCP.",
        )

        log.info("Launching Gradio interface...")
        demo.launch()

    except Exception as e:
        log.critical(f"A critical error occurred in main: {e}", exc_info=True)
    finally:
        log.info("Application cleanup (no explicit MCP disconnect needed for BasicMCPClient).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nApplication shutting down gracefully.")
