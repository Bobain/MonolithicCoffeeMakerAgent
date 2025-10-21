#!/usr/bin/env python3
"""Example 01: Basic Singleton Enforcement Usage

This example demonstrates the basic usage of the AgentRegistry singleton
enforcement mechanism.

Run this example:
    poetry run python examples/singleton_enforcement/01_basic_usage.py
"""

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType


def example_successful_registration():
    """Example: Successfully register an agent."""
    print("\n" + "=" * 60)
    print("Example 1: Successful Agent Registration")
    print("=" * 60)

    registry = AgentRegistry()

    # Register an agent
    print(f"\n1. Registering {AgentType.CODE_DEVELOPER.value}...")
    registry.register_agent(AgentType.CODE_DEVELOPER)

    # Check if registered
    if registry.is_registered(AgentType.CODE_DEVELOPER):
        print(f"   ✅ {AgentType.CODE_DEVELOPER.value} is registered")

    # Get agent info
    info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
    print(f"   📊 PID: {info['pid']}")
    print(f"   📊 Started at: {info['started_at']}")

    # Unregister when done
    print(f"\n2. Unregistering {AgentType.CODE_DEVELOPER.value}...")
    registry.unregister_agent(AgentType.CODE_DEVELOPER)

    if not registry.is_registered(AgentType.CODE_DEVELOPER):
        print(f"   ✅ {AgentType.CODE_DEVELOPER.value} is unregistered")


def example_duplicate_detection():
    """Example: Demonstrate duplicate agent detection."""
    print("\n" + "=" * 60)
    print("Example 2: Duplicate Agent Detection")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()  # Start fresh

    # First registration succeeds
    print(f"\n1. Registering first instance of {AgentType.PROJECT_MANAGER.value}...")
    registry.register_agent(AgentType.PROJECT_MANAGER)
    print(f"   ✅ First instance registered successfully")

    # Second registration fails
    print(f"\n2. Attempting to register duplicate {AgentType.PROJECT_MANAGER.value}...")
    try:
        registry.register_agent(AgentType.PROJECT_MANAGER)
        print("   ❌ ERROR: Should have raised AgentAlreadyRunningError!")
    except AgentAlreadyRunningError as e:
        print(f"   ✅ Duplicate detected! Error raised as expected:")
        print(f"\n{e}\n")

    # Cleanup
    registry.unregister_agent(AgentType.PROJECT_MANAGER)


def example_multiple_agent_types():
    """Example: Multiple different agent types can run simultaneously."""
    print("\n" + "=" * 60)
    print("Example 3: Multiple Different Agent Types")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    agent_types = [
        AgentType.CODE_DEVELOPER,
        AgentType.PROJECT_MANAGER,
        AgentType.ARCHITECT,
        AgentType.ASSISTANT,
    ]

    # Register multiple different agents
    print("\n1. Registering multiple different agent types...")
    for agent_type in agent_types:
        registry.register_agent(agent_type)
        print(f"   ✅ Registered: {agent_type.value}")

    # Show all registered agents
    print("\n2. Currently running agents:")
    all_agents = registry.get_all_registered_agents()
    for agent_type, info in all_agents.items():
        print(f"   • {agent_type.value:20} PID: {info['pid']:6}  Started: {info['started_at']}")

    # Cleanup
    print("\n3. Cleaning up...")
    for agent_type in agent_types:
        registry.unregister_agent(agent_type)
    print("   ✅ All agents unregistered")


def example_context_manager():
    """Example: Using context manager for automatic cleanup."""
    print("\n" + "=" * 60)
    print("Example 4: Context Manager (Recommended Pattern)")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    print("\n1. Before context manager:")
    print(f"   {AgentType.ARCHITECT.value} registered: {registry.is_registered(AgentType.ARCHITECT)}")

    print(f"\n2. Inside context manager...")
    with AgentRegistry.register(AgentType.ARCHITECT):
        print(f"   {AgentType.ARCHITECT.value} registered: {registry.is_registered(AgentType.ARCHITECT)}")
        print("   ✅ Agent is running inside context")

    print(f"\n3. After context manager exit:")
    print(f"   {AgentType.ARCHITECT.value} registered: {registry.is_registered(AgentType.ARCHITECT)}")
    print("   ✅ Agent automatically unregistered (even if exception occurred)")


def example_error_recovery():
    """Example: Error recovery strategies."""
    print("\n" + "=" * 60)
    print("Example 5: Error Recovery Strategies")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    # Register first instance
    print("\n1. Registering first instance...")
    registry.register_agent(AgentType.CODE_DEVELOPER, pid=12345)
    print(f"   ✅ Registered with PID 12345")

    # Try to register duplicate and handle error
    print("\n2. Attempting duplicate registration with error handling...")
    try:
        registry.register_agent(AgentType.CODE_DEVELOPER)
    except AgentAlreadyRunningError as e:
        print("   ⚠️  Duplicate detected! Handling gracefully...")
        print(f"\n   Error details:")
        print(f"   - Agent type: {e.agent_type.value}")
        print(f"   - Existing PID: {e.existing_pid}")
        print(f"   - Started at: {e.existing_started_at}")

        # Strategy: Check if process is running and decide action
        print(f"\n   Strategy: Could check if PID {e.existing_pid} is running")
        print("   Options: wait, kill existing, exit gracefully")

    # Cleanup
    registry.unregister_agent(AgentType.CODE_DEVELOPER)


def example_query_agent_status():
    """Example: Query agent status and info."""
    print("\n" + "=" * 60)
    print("Example 6: Query Agent Status")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    # Register some agents
    registry.register_agent(AgentType.CODE_DEVELOPER, pid=10001)
    registry.register_agent(AgentType.PROJECT_MANAGER, pid=10002)
    registry.register_agent(AgentType.ARCHITECT, pid=10003)

    # Check specific agent
    print("\n1. Check specific agent:")
    if registry.is_registered(AgentType.CODE_DEVELOPER):
        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
        print(f"   {AgentType.CODE_DEVELOPER.value}:")
        print(f"     - PID: {info['pid']}")
        print(f"     - Started: {info['started_at']}")

    # Get all registered agents
    print("\n2. All registered agents:")
    all_agents = registry.get_all_registered_agents()
    print(f"   Total running: {len(all_agents)}")
    for agent_type, info in all_agents.items():
        print(f"   • {agent_type.value}: PID {info['pid']}")

    # Check non-registered agent
    print("\n3. Check non-registered agent:")
    if not registry.is_registered(AgentType.ASSISTANT):
        print(f"   {AgentType.ASSISTANT.value} is NOT running")

    # Cleanup
    registry.reset()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Agent Singleton Enforcement Examples")
    print("=" * 60)
    print("\nThese examples demonstrate how the AgentRegistry enforces")
    print("singleton behavior to prevent duplicate agent instances.")

    try:
        example_successful_registration()
        example_duplicate_detection()
        example_multiple_agent_types()
        example_context_manager()
        example_error_recovery()
        example_query_agent_status()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\nKey Takeaways:")
        print("  1. Use context manager (with AgentRegistry.register()) for automatic cleanup")
        print("  2. Only ONE instance of each agent type can run at a time")
        print("  3. Clear error messages help diagnose duplicate agent issues")
        print("  4. Multiple different agent types can run simultaneously")
        print("  5. Registry is thread-safe and uses proper locking")
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
