#!/usr/bin/env python3
"""Demo script showing how to use LLM tools with the ReAct agent.

This script demonstrates:
1. Creating LLM tools for different purposes
2. Using them in a ReAct agent
3. Getting statistics and summaries
"""

import logging
from datetime import datetime

from dotenv import load_dotenv
from langfuse import Langfuse

from coffee_maker.code_formatter.agents import create_react_formatter_agent
from coffee_maker.langchain_observe.create_auto_picker import create_auto_picker_for_react_agent
from coffee_maker.langchain_observe.llm_tools import get_llm_tool_names, get_llm_tools_summary

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main demo function."""
    print("=" * 80)
    print("LLM Tools Demo")
    print("=" * 80)
    print()

    # 1. Show available LLM tools
    print("1. Available LLM Tools")
    print("-" * 80)
    tool_names = get_llm_tool_names()
    print(f"Total tools: {len(tool_names)}")
    for name in sorted(tool_names):
        print(f"  - {name}")
    print()

    # 2. Show tool summary
    print("2. LLM Tools Summary by Purpose")
    print("-" * 80)
    summary = get_llm_tools_summary()
    for purpose, providers in summary.items():
        print(f"\n{purpose.upper().replace('_', ' ')}:")
        for provider, config in providers.items():
            print(f"  {provider}:")
            print(f"    Tool: {config['tool_name']}")
            print(f"    Primary: {config['primary_model']}")
            print(f"    Fallback: {config['fallback_model']}")
            print(f"    Description: {config['description']}")
    print()

    # 3. Create ReAct agent with LLM tools
    print("3. Creating ReAct Agent with LLM Tools")
    print("-" * 80)

    # Initialize Langfuse
    langfuse_client = Langfuse()
    langfuse_client.update_current_trace(session_id=f"llm-tools-demo-{datetime.now().isoformat()}")

    # Create AutoPickerLLM for the main agent
    auto_picker_llm = create_auto_picker_for_react_agent(tier="tier1", streaming=False)

    # Create ReAct agent with LLM tools enabled
    react_agent, tools, llm_instance = create_react_formatter_agent(
        langfuse_client=langfuse_client,
        llm=auto_picker_llm,
        use_auto_picker=False,  # Already using AutoPickerLLM
        tier="tier1",
        include_llm_tools=True,  # Enable LLM tools
    )

    print(f"ReAct agent created with {len(tools)} tools")
    print(f"  - GitHub tools: {sum(1 for t in tools if 'github' in t.name.lower())}")
    print(f"  - LLM tools: {sum(1 for t in tools if 'invoke_llm' in t.name)}")
    print(f"  - Other tools: {sum(1 for t in tools if 'invoke_llm' not in t.name and 'github' not in t.name.lower())}")
    print()

    # 4. Show example tool descriptions
    print("4. Example Tool Descriptions")
    print("-" * 80)
    example_tools = [
        "invoke_llm_openai_long_context",
        "invoke_llm_gemini_fast",
        "invoke_llm_openai_accurate",
    ]

    for tool_name in example_tools:
        tool = next((t for t in tools if t.name == tool_name), None)
        if tool:
            print(f"\n{tool.name}:")
            # Show first 200 chars of description
            desc = tool.description[:200] + "..." if len(tool.description) > 200 else tool.description
            print(f"  {desc}")
    print()

    # 5. Usage recommendations
    print("5. When to Use Each Purpose")
    print("-" * 80)
    recommendations = {
        "long_context": "Files > 10K lines, need large context window",
        "fast": "Quick syntax checks, simple validation",
        "accurate": "Complex algorithms, critical code review",
        "budget": "Batch processing, cost-sensitive tasks",
        "second_best_model": "General purpose, balanced performance/cost",
    }

    for purpose, use_case in recommendations.items():
        print(f"  {purpose:20s} → {use_case}")
    print()

    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print("\nTo use in your code:")
    print("  1. Create agent with include_llm_tools=True")
    print("  2. Agent will automatically have access to all LLM tools")
    print("  3. Agent can choose the right tool based on task requirements")
    print()


if __name__ == "__main__":
    main()
