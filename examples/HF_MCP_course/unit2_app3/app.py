from huggingface_hub import Agent

AGENT_URL = "http://localhost:7860/gradio_api/mcp/sse"

agent = Agent(
    model="Qwen/Qwen2.5-72B-Instruct",
    provider="nebius",
    servers=[
        {"command": "npx", "args": ["mcp-remote", AGENT_URL]},
        {"command": "poetry", "args": ["run", "dummy_mcp_server_tools"]},
    ],
)

# --- Prerequisites ---
# Start the dummy MCP server in another terminal:
#    python dummy_mcp_server_tools.py

import asyncio
from functools import partial

import gradio as gr
from dummy_mcp_server_tools import PORT

# --- Configuration ---
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{PORT}/sse"

# FIX: A high-quality, "few-shot" prompt demonstrating the full reasoning cycle.
# This is the most effective way to guide the model.
SYSTEM_PROMPT = """
You are an expert assistant that answers questions by using tools.
You have access to a `get_weather` tool.
Here is an example of how you should work:
---
USER: What is the weather like in Toronto?
ASSISTANT:
Thought: I need to find the weather in Toronto. I will use the get_weather tool for this.
Action: get_weather
Action Input: {"location": "Toronto"}

Observation: Weather in Toronto: Cloudy, 5°C

Thought: I have the weather information for Toronto. I will now provide the final answer to the user in a friendly, conversational way.
Answer: The weather in Toronto is currently cloudy with a temperature of 5°C.
---

Now, begin the conversation with the user.
"""


async def get_agent(tools_spec: McpToolSpec) -> ReActAgent:
    """Creates and configures the ReActAgent."""
    print("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    # The agent gets the tool descriptions from the `from_tools` constructor.
    print(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    print("Initializing LLM and Agent...")
    llm = Ollama(model=OLLAMA_MODEL, request_timeout=120.0)
    Settings.llm = llm

    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=5,  # Keep a reasonable limit to prevent infinite loops
        verbose=True,
    )
    print("ReActAgent created.")
    return agent


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent):
    """
    Runs the agent and streams the entire chain of thought and final answer.
    """
    print(f"Streaming response for message: '{message}'")

    response_stream = agent.stream_chat(message)

    # We will build the full response, including thoughts and final answer,
    # and stream it progressively.
    full_response = ""

    # The 'thinking' part is now captured within the main token stream for ReActAgent
    # We will stream out every token the agent produces.
    async for token in response_stream.async_response_gen():
        full_response += token
        yield full_response

    # Fallback in case the stream ends but the final response attribute has content
    # (can happen if the final step doesn't stream for some reason).
    if not full_response and response_stream.response:
        yield response_stream.response


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
            chatbot=gr.Chatbot(
                label="Agent Chat",
                height=600,
                show_copy_button=True,
                # Use Markdown rendering to properly display "Thinking" logs if they appear
                render_markdown=True,
            ),
            textbox=gr.Textbox(placeholder="Ask me something...", label="Your Message"),
            examples=["Quel temps fait il à Paris?"],
            title="Agent with MCP Tools (ReAct)",
            description="This agent uses an Ollama model and tools to provide answers.",
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
