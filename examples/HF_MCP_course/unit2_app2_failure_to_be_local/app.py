# app.py
# co-author : Gemini 2.5 Pro Preview

# ==============================================================================
# --- Prerequisites ---
#
# 1. Install necessary packages:
#    poetry install
#    poetry run pip install mcp-flight-search
#
# 2. Start the Ollama server in a dedicated terminal:
#    ollama serve
#
# 3. Pull a capable model (8B parameters recommended for ReAct):
#    ollama pull llama3:8b
#
# 4. Start the dummy MCP tool server in a second dedicated terminal:
#    poetry run python dummy_mcp_server_tools.py
#
# 5. Finally, run this application in a third terminal:
#    poetry run python app.py
#
# ==============================================================================

import asyncio
import gradio as gr
import logging
import sys
from functools import partial
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

# Assuming dummy_mcp_server_tools.py defines PORT
from dummy_mcp_server_tools import PORT

# --- Logging Configuration ---
# Set up a logger to provide detailed, timestamped output to the console.
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
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
    """Creates and configures the ReActAgent and the LLM instance."""
    log.info("--- Step: Initializing Agent and LLM ---")

    # LlamaDebugHandler will print all LLM inputs/outputs and other events.
    llama_debug_handler = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug_handler])
    Settings.callback_manager = callback_manager

    log.info("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    log.info(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    log.info("Initializing LLM...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm

    log.info(
        f"Creating ReActAgent with the following system prompt:\n---PROMPT START---\n{SYSTEM_PROMPT}\n---PROMPT END---")
    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=5,
        verbose=True  # Keep verbose for LlamaIndex's own detailed prints
    )
    log.info("ReActAgent created successfully.")
    return agent, llm


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent, llm: Ollama):
    """
    Runs the agent to get tool output, then manually prompts the LLM for a final answer
    if the agent fails to synthesize one.
    """
    log.info(f"--- Running Agent for user message: '{message}' ---")

    # === STAGE 1: Let the Agent use its tools ===
    response_stream = agent.stream_chat(message)

    # Display the "Thinking" log from the agent's tool use
    thinking_log = ""
    if response_stream.source_nodes:
        log.info(f"Agent used {len(response_stream.source_nodes)} tool(s).")
        thinking_log = "🤔 **Thinking Process & Tool Calls:**\n\n```\n"
        for i, node in enumerate(response_stream.source_nodes):
            tool_name = node.raw_input.get("tool_name", "unknown_tool")
            tool_output_str = str(node.raw_output).strip()
            log.info(f"  - Tool Call {i + 1}: {tool_name}")
            log.info(f"  - Tool Result {i + 1}: {tool_output_str}")
            thinking_log += f"Tool: {tool_name}\nResult: {tool_output_str}\n---\n"
        thinking_log += "```\n\n"
        yield thinking_log

    # === STAGE 2: Synthesize the Final Answer ===
    final_answer = ""
    llm_final_response = response_stream.response
    log.info(f"Agent's final synthesized response (response_stream.response): '{llm_final_response}'")

    # Check if the agent's final response is empty, BUT tools were used
    if not llm_final_response and response_stream.source_nodes:
        log.warning(
            "Agent used tools but failed to synthesize a final answer. Manually prompting LLM for summarization.")
        last_observation = response_stream.source_nodes[-1].raw_output.content

        # Construct the new, simple prompt for the final answer
        final_prompt = (
            f"The user originally asked: '{message}'.\n"
            f"You have already gathered the following information: '{last_observation}'.\n"
            f"Based on this information, please provide a direct, friendly, and complete answer to the user's original question. "
            f"If the original question was in a different language, answer in that language. "
            f"If unit conversions are needed (e.g., Fahrenheit to Celsius), perform them."
        )

        log.info(f"--- Manually prompting LLM with:\n---PROMPT START---\n{final_prompt}\n---PROMPT END---")

        # Use the LLM directly for the final streaming response
        response_generator = await llm.astream_complete(final_prompt)
        async for token in response_generator:
            final_answer += token.delta
            yield thinking_log + final_answer

    elif llm_final_response:
        # The agent worked perfectly. We just stream its answer.
        log.info("Agent successfully generated a final answer.")
        final_answer = llm_final_response
        current_response = thinking_log
        for char in str(final_answer):
            current_response += char
            yield current_response
            await asyncio.sleep(0.02)
    else:
        # True failure case - no tool use and no response.
        log.error("Agent did not use tools and did not provide a response.")
        yield thinking_log + "I'm sorry, I was unable to process your request."

    log.info(f"Final streamed answer to user: '{final_answer}'")


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
            chatbot=gr.Chatbot(label="Agent Chat", height=600, show_copy_button=True, render_markdown=True),
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