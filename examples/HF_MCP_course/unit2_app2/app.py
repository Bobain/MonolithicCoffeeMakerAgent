# app.py
# co-author : Gemini 2.5 Pro Preview

# 1. Start Ollama server in a terminal:
#    ollama serve
#
# 2. Make sure you have a capable model. 1B models struggle with ReAct.
#    RECOMMENDED: ollama pull deepseek-r1:1.5b
#    (or phi3, qwen2, etc.)
# 2. Make sure you have the model:
#    ollama pull llama3:8b
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

# Assuming dummy_mcp_server_tools.py defines PORT
from dummy_mcp_server_tools import PORT

# --- Configuration ---
OLLAMA_MODEL = "deepseek-r1:1.5b"
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"

# This prompt is now focused only on getting the model to use tools correctly.
SYSTEM_PROMPT = """
You are an expert assistant that uses tools to answer questions.
When you need to use a tool, you MUST respond in this format, and nothing else:
Thought: I should use the get_weather tool to find the weather for the user's requested city.
Action: get_weather
Action Input: {"location": "the user's requested city"}
"""


# We now need to pass the LLM instance along with the agent.
async def get_agent_and_llm(tools_spec: McpToolSpec) -> tuple[ReActAgent, Ollama]:
    """Creates and configures the ReActAgent and the LLM instance."""
    print("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    print(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    print("Initializing LLM and Agent...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm

    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=5,  # Keep a reasonable limit
        verbose=True
    )
    print("ReActAgent created.")
    return agent, llm


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent, llm: Ollama):
    """
    Runs the agent to get tool output, then manually prompts the LLM for a final answer
    if the agent fails to synthesize one.
    """
    print(f"--- Running Agent for message: '{message}' ---")

    # === STAGE 1: Let the Agent use its tools ===
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

    # === STAGE 2: Synthesize the Final Answer ===
    final_answer = ""
    llm_final_response = response_stream.response

    # Check if the agent's final synthesized response is empty, BUT tools were used
    if not llm_final_response and response_stream.source_nodes:
        print("Agent used tools but failed to synthesize a final answer. Manually prompting LLM for summarization.")
        last_observation = response_stream.source_nodes[-1].raw_output.content

        # Construct a new, simple prompt for the final answer
        final_prompt = (
            f"The user originally asked: '{message}'.\n"
            f"You have already gathered the following information: '{last_observation}'.\n"
            f"Based on this information, please provide a direct, friendly, and complete answer to the user's original question. "
            f"If the original question was in a different language, answer in that language. "
            f"If unit conversions are needed (e.g., Fahrenheit to Celsius), perform them."
        )

        print(f"--- Manually prompting LLM with: '{final_prompt}' ---")

        # Use the LLM directly for the final streaming response
        response_generator = await llm.astream_complete(final_prompt)
        async for token in response_generator:
            final_answer += token.delta
            yield thinking_log + final_answer

    elif llm_final_response:
        # The agent worked perfectly, including the final answer. Stream it.
        print("Agent successfully generated a final answer.")
        final_answer = llm_final_response
        current_response = thinking_log
        for char in str(final_answer):
            current_response += char
            yield current_response
            await asyncio.sleep(0.02)
    else:
        # True failure case - no tool use and no response
        print("Agent did not use tools and did not provide a response.")
        yield thinking_log + "I'm sorry, I was unable to process your request."


async def main():
    """Initializes resources and launches the Gradio application."""
    mcp_client = None
    try:
        mcp_client = BasicMCPClient(MCP_SERVER_TOOL_URL)
        mcp_tools_spec = McpToolSpec(mcp_client)
        # Get both the agent and the llm object
        agent, llm = await get_agent_and_llm(mcp_tools_spec)

        # Use partial to pass both agent and llm to our Gradio function
        agent_fn_with_context = partial(run_agent_chat_stream, agent=agent, llm=llm)

        demo = gr.ChatInterface(
            fn=agent_fn_with_context,
            chatbot=gr.Chatbot(label="Agent Chat", height=600, show_copy_button=True, render_markdown=True),
            textbox=gr.Textbox(placeholder="Ask me something...", label="Your Message"),
            examples=["Quel temps fait il à Paris?"],
            title="Agent with MCP Tools (ReAct + Manual Summary)",
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