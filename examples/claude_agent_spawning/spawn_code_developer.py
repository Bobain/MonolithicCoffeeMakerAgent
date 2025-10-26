"""Example: Spawn Claude Code's code-developer sub-agent programmatically.

This example shows how to use the ClaudeAgentInvoker to spawn
Claude Code's built-in code-developer agent from your autonomous system.

The spawned agent will:
- Use the .claude/agents/code_developer.md prompt
- Have access to all tools (Read, Write, Edit, Bash, etc.)
- Work on the roadmap branch (CFR-013 compliant)
- Track all activity in the database

Usage:
    python examples/claude_agent_spawning/spawn_code_developer.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from coffee_maker.claude_agent_invoker import get_invoker
from coffee_maker.autonomous.roadmap_database import RoadmapDatabase


def spawn_code_developer_for_priority(priority_name: str):
    """Spawn Claude Code's code-developer agent to implement a priority.

    This demonstrates how your autonomous system can delegate
    implementation to Claude Code's sub-agent.

    Args:
        priority_name: Priority to implement (e.g., "US-042")
    """
    print(f"🚀 Spawning code-developer agent for {priority_name}")

    # Get priority details from database
    roadmap = RoadmapDatabase(agent_name="example")
    priority = roadmap.get_priority_by_id(priority_name)

    if not priority:
        print(f"❌ Priority {priority_name} not found in roadmap")
        return

    # Find spec
    spec_path = find_spec(priority)
    if not spec_path:
        print(f"❌ No spec found for {priority_name}")
        print("💡 Tip: Spawn architect agent first to create spec")
        return

    # Read spec content
    spec_content = spec_path.read_text()

    # Get invoker
    invoker = get_invoker()

    # Build prompt that references the priority
    prompt = f"""
Implement {priority_name}: {priority.get('title', '')}

## Technical Specification

{spec_content}

## Instructions

1. Read the spec above carefully
2. Implement the feature following the spec exactly
3. Add tests as specified
4. Run tests to verify (pytest)
5. Commit with message: "feat: Implement {priority_name}"

IMPORTANT: You are Claude Code's code-developer agent. Follow the implementation
steps in the spec. Use Read, Write, Edit, and Bash tools as needed.
"""

    print("\n📋 Task for code-developer:")
    print(prompt[:200] + "...\n")

    # Spawn the agent with streaming to see progress
    print("🎬 Starting code-developer agent (streaming)...\n")

    for msg in invoker.invoke_agent_streaming(
        agent_type="code-developer",
        prompt=prompt,
        working_dir=str(Path.cwd()),
        timeout=1800,  # 30 minutes for implementation
    ):
        # Show progress in real-time
        if msg.message_type == "init":
            print(f"🎬 Agent initialized: {msg.metadata.get('session_id', 'N/A')}")

        elif msg.message_type == "message":
            print(f"💬 {msg.content}")

        elif msg.message_type == "tool_use":
            tool_name = msg.metadata.get("name", "unknown")
            print(f"🔧 Using tool: {tool_name}")

        elif msg.message_type == "tool_result":
            result_preview = str(msg.content)[:100]
            print(f"✅ Tool result: {result_preview}...")

        elif msg.message_type == "result":
            print(f"\n🏁 Agent completed!")
            print(f"   Input tokens: {msg.metadata.get('input_tokens', 0)}")
            print(f"   Output tokens: {msg.metadata.get('output_tokens', 0)}")
            print(f"   Duration: {msg.metadata.get('duration_ms', 0)}ms")
            print(f"   Cost: ${msg.metadata.get('total_cost_usd', 0):.4f}")

    print(f"\n✅ {priority_name} implementation delegated to code-developer agent")


def spawn_architect_for_spec(priority_name: str):
    """Spawn Claude Code's architect agent to create a spec.

    This shows how to delegate spec creation to the architect sub-agent.

    Args:
        priority_name: Priority needing spec
    """
    print(f"🏗️  Spawning architect agent to create spec for {priority_name}")

    roadmap = RoadmapDatabase(agent_name="example")
    priority = roadmap.get_priority_by_id(priority_name)

    if not priority:
        print(f"❌ Priority {priority_name} not found")
        return

    invoker = get_invoker()

    prompt = f"""
Create a technical specification for {priority_name}: {priority.get('title', '')}

## Priority Details

{priority.get('description', 'No description provided')}

## Requirements

Create a comprehensive technical spec following SPEC-XXX format:
1. Problem statement
2. Proposed solution
3. Implementation steps
4. Testing strategy
5. Definition of Done

Save the spec to: docs/architecture/specs/SPEC-XXX-{priority_name.lower()}.md

Use Write tool to create the spec file.
"""

    print(f"\n📋 Requesting spec from architect...\n")

    # Use non-streaming for simpler output
    result = invoker.invoke_agent("architect", prompt, timeout=600)

    if result.success:
        print(f"✅ Architect created spec!")
        print(f"   Tokens: {result.usage['output_tokens']}")
        print(f"   Cost: ${result.cost_usd:.4f}")
        print(f"\n📄 Spec preview:")
        print(result.content[:500] + "...")
    else:
        print(f"❌ Spec creation failed: {result.error}")


def spawn_slash_command_implement_feature(priority_name: str):
    """Use the implement-feature slash command.

    This demonstrates invoking slash commands programmatically.
    """
    print(f"⚡ Using /implement-feature command for {priority_name}")

    roadmap = RoadmapDatabase(agent_name="example")
    priority = roadmap.get_priority_by_id(priority_name)

    if not priority:
        print(f"❌ Priority not found")
        return

    spec_path = find_spec(priority)
    if not spec_path:
        print(f"❌ No spec found")
        return

    invoker = get_invoker()

    # The slash command template will be loaded from .claude/commands/implement-feature.md
    result = invoker.invoke_slash_command(
        "implement-feature",
        variables={
            "PRIORITY_NAME": priority_name,
            "PRIORITY_TITLE": priority.get("title", ""),
            "SPEC_CONTENT": spec_path.read_text(),
            "PRIORITY_CONTENT": priority.get("description", ""),
        },
        timeout=1800,
    )

    if result.success:
        print(f"✅ Implementation complete via slash command!")
        print(f"   Cost: ${result.cost_usd:.4f}")
    else:
        print(f"❌ Implementation failed: {result.error}")


def find_spec(priority: dict) -> Path | None:
    """Find spec file for priority."""
    import re

    priority_number = priority.get("number", "")
    priority_title = priority.get("title", "")

    # Extract US number
    us_match = re.search(r"US-(\d+)", priority_title)
    us_number = us_match.group(1) if us_match else None

    specs_dir = Path("docs/architecture/specs")
    if not specs_dir.exists():
        return None

    # Try different patterns
    patterns = []
    if us_number:
        patterns.append(f"SPEC-{us_number}-*.md")

    patterns.append(f"SPEC-{priority_number}-*.md")

    for pattern in patterns:
        matches = list(specs_dir.glob(pattern))
        if matches:
            return matches[0]

    return None


def interactive_demo():
    """Interactive demo showing different agent spawning methods."""
    print("=" * 80)
    print("Claude Code Agent Spawning Demo")
    print("=" * 80)
    print()
    print("This demo shows 3 ways to spawn Claude Code sub-agents:")
    print()
    print("1. Spawn code-developer agent (streaming)")
    print("2. Spawn architect agent (create spec)")
    print("3. Use slash command (/implement-feature)")
    print()

    choice = input("Choose option (1-3) or 'q' to quit: ").strip()

    if choice == "1":
        priority = input("Enter priority name (e.g., US-042): ").strip()
        spawn_code_developer_for_priority(priority)

    elif choice == "2":
        priority = input("Enter priority name: ").strip()
        spawn_architect_for_spec(priority)

    elif choice == "3":
        priority = input("Enter priority name: ").strip()
        spawn_slash_command_implement_feature(priority)

    elif choice.lower() == "q":
        print("Goodbye!")
        return

    else:
        print("Invalid choice")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Command line mode
        priority_name = sys.argv[1]
        method = sys.argv[2] if len(sys.argv) > 2 else "streaming"

        if method == "streaming":
            spawn_code_developer_for_priority(priority_name)
        elif method == "architect":
            spawn_architect_for_spec(priority_name)
        elif method == "slash":
            spawn_slash_command_implement_feature(priority_name)
        else:
            print(f"Unknown method: {method}")
            print("Usage: python spawn_code_developer.py <priority> [streaming|architect|slash]")
    else:
        # Interactive mode
        interactive_demo()
