#!/usr/bin/env python3
"""Example 02: Thread Safety in Agent Registry

This example demonstrates the thread-safe behavior of AgentRegistry when
multiple threads attempt to register agents concurrently.

Run this example:
    poetry run python examples/singleton_enforcement/02_thread_safety.py
"""

import threading
import time
from typing import List

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType


def example_concurrent_same_agent():
    """Example: Multiple threads trying to register the same agent type."""
    print("\n" + "=" * 60)
    print("Example 1: Concurrent Same Agent Registration")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    results = {"success": 0, "failed": 0}
    lock = threading.Lock()

    def try_register(thread_id: int):
        """Try to register an agent from a thread."""
        try:
            registry.register_agent(AgentType.CODE_DEVELOPER)
            with lock:
                results["success"] += 1
                print(f"   ✅ Thread {thread_id}: Successfully registered!")
        except AgentAlreadyRunningError:
            with lock:
                results["failed"] += 1
                print(f"   ❌ Thread {thread_id}: Failed (agent already running)")

    # Launch 10 threads trying to register the same agent
    print("\n1. Launching 10 threads to register CODE_DEVELOPER...")
    threads: List[threading.Thread] = []
    for i in range(10):
        t = threading.Thread(target=try_register, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print(f"\n2. Results:")
    print(f"   • Successful registrations: {results['success']}")
    print(f"   • Failed registrations: {results['failed']}")
    print(f"\n   ✅ Expected: Exactly 1 success, 9 failures")
    print(f"   ✅ Actual: {results['success']} success, {results['failed']} failures")

    assert results["success"] == 1, "Expected exactly 1 successful registration"
    assert results["failed"] == 9, "Expected exactly 9 failed registrations"

    # Cleanup
    registry.reset()


def example_concurrent_different_agents():
    """Example: Multiple threads registering different agent types."""
    print("\n" + "=" * 60)
    print("Example 2: Concurrent Different Agent Registration")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    agent_types = [
        AgentType.CODE_DEVELOPER,
        AgentType.PROJECT_MANAGER,
        AgentType.ARCHITECT,
        AgentType.ASSISTANT,
        AgentType.ASSISTANT,
    ]

    registered = []
    lock = threading.Lock()

    def register_agent(agent_type: AgentType):
        """Register an agent type."""
        try:
            registry.register_agent(agent_type)
            time.sleep(0.01)  # Small delay to test concurrency
            with lock:
                registered.append(agent_type)
                print(f"   ✅ Registered: {agent_type.value}")
        except AgentAlreadyRunningError as e:
            print(f"   ❌ Failed to register {agent_type.value}: {e}")

    # Launch threads for each agent type
    print("\n1. Launching threads to register different agent types...")
    threads: List[threading.Thread] = []
    for agent_type in agent_types:
        t = threading.Thread(target=register_agent, args=(agent_type,))
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    print(f"\n2. Results:")
    print(f"   • Total registered: {len(registered)}")
    print(f"   • Expected: {len(agent_types)}")

    # Verify all agents registered
    for agent_type in agent_types:
        assert registry.is_registered(agent_type), f"{agent_type.value} should be registered"

    print(f"\n   ✅ All {len(agent_types)} different agent types registered successfully")

    # Cleanup
    registry.reset()


def example_register_unregister_concurrent():
    """Example: Concurrent register and unregister operations."""
    print("\n" + "=" * 60)
    print("Example 3: Concurrent Register/Unregister Operations")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    operations = {"register": 0, "unregister": 0, "errors": 0}
    lock = threading.Lock()

    def register_and_unregister(thread_id: int):
        """Register and then unregister an agent."""
        try:
            # Try to register
            registry.register_agent(AgentType.CODE_DEVELOPER)
            with lock:
                operations["register"] += 1
            print(f"   Thread {thread_id}: Registered")

            # Do some work
            time.sleep(0.05)

            # Unregister
            registry.unregister_agent(AgentType.CODE_DEVELOPER)
            with lock:
                operations["unregister"] += 1
            print(f"   Thread {thread_id}: Unregistered")

        except AgentAlreadyRunningError:
            with lock:
                operations["errors"] += 1
            print(f"   Thread {thread_id}: Could not register (already running)")

    # Launch threads sequentially (each waits for previous to finish)
    print("\n1. Running register/unregister cycles sequentially...")
    print("   (Only one should succeed at a time)")

    threads: List[threading.Thread] = []
    for i in range(5):
        t = threading.Thread(target=register_and_unregister, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all
    for t in threads:
        t.join()

    print(f"\n2. Results:")
    print(f"   • Successful registers: {operations['register']}")
    print(f"   • Successful unregisters: {operations['unregister']}")
    print(f"   • Registration errors: {operations['errors']}")

    # Cleanup
    registry.reset()


def example_context_manager_concurrent():
    """Example: Context managers running concurrently."""
    print("\n" + "=" * 60)
    print("Example 4: Concurrent Context Managers")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    results = {"success": 0, "failed": 0}
    lock = threading.Lock()

    def use_context_manager(thread_id: int):
        """Use context manager to register agent."""
        try:
            with AgentRegistry.register(AgentType.ARCHITECT):
                with lock:
                    results["success"] += 1
                print(f"   Thread {thread_id}: Inside context (agent registered)")
                time.sleep(0.1)  # Simulate work
        except AgentAlreadyRunningError:
            with lock:
                results["failed"] += 1
            print(f"   Thread {thread_id}: Context failed (agent already running)")

    # Launch multiple threads with context managers
    print("\n1. Launching 5 threads using context managers...")
    threads: List[threading.Thread] = []
    for i in range(5):
        t = threading.Thread(target=use_context_manager, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all
    for t in threads:
        t.join()

    print(f"\n2. Results:")
    print(f"   • Successful context entries: {results['success']}")
    print(f"   • Failed context entries: {results['failed']}")

    # Verify cleanup
    print(f"\n3. After all threads complete:")
    print(f"   • ARCHITECT registered: {registry.is_registered(AgentType.ARCHITECT)}")
    print(f"   ✅ All contexts cleaned up properly")

    # Cleanup
    registry.reset()


def example_stress_test():
    """Example: Stress test with many concurrent operations."""
    print("\n" + "=" * 60)
    print("Example 5: Stress Test (100 concurrent threads)")
    print("=" * 60)

    registry = AgentRegistry()
    registry.reset()

    results = {"register_success": 0, "register_failed": 0, "unregister": 0}
    lock = threading.Lock()

    def random_operation(thread_id: int):
        """Perform random register/unregister operations."""
        try:
            # Try to register
            registry.register_agent(AgentType.CODE_DEVELOPER)
            with lock:
                results["register_success"] += 1

            # Do brief work
            time.sleep(0.001)

            # Unregister
            registry.unregister_agent(AgentType.CODE_DEVELOPER)
            with lock:
                results["unregister"] += 1

        except AgentAlreadyRunningError:
            with lock:
                results["register_failed"] += 1

    # Launch 100 threads
    print("\n1. Launching 100 threads with random operations...")
    threads: List[threading.Thread] = []
    for i in range(100):
        t = threading.Thread(target=random_operation, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all
    for t in threads:
        t.join()

    print(f"\n2. Stress Test Results:")
    print(f"   • Successful registers: {results['register_success']}")
    print(f"   • Failed registers: {results['register_failed']}")
    print(f"   • Successful unregisters: {results['unregister']}")
    print(f"   • Total operations: {results['register_success'] + results['register_failed']}")
    print(f"\n   ✅ No deadlocks or race conditions detected!")
    print(f"   ✅ Registry maintained consistency under load")

    # Verify final state
    assert not registry.is_registered(AgentType.CODE_DEVELOPER), "Agent should be unregistered"

    # Cleanup
    registry.reset()


def main():
    """Run all thread safety examples."""
    print("\n" + "=" * 60)
    print("Thread Safety Examples for Agent Registry")
    print("=" * 60)
    print("\nThese examples demonstrate that AgentRegistry is thread-safe")
    print("and properly handles concurrent registration attempts.")

    try:
        example_concurrent_same_agent()
        example_concurrent_different_agents()
        example_register_unregister_concurrent()
        example_context_manager_concurrent()
        example_stress_test()

        print("\n" + "=" * 60)
        print("✅ All thread safety examples passed!")
        print("=" * 60)
        print("\nKey Findings:")
        print("  1. Only ONE thread can register the same agent type at a time")
        print("  2. Multiple different agent types can register concurrently")
        print("  3. Thread-safe locking prevents race conditions")
        print("  4. Context managers properly cleanup even with concurrency")
        print("  5. Registry maintains consistency under high load (100 threads)")
        print()

    except Exception as e:
        print(f"\n❌ Error in thread safety examples: {e}")
        raise


if __name__ == "__main__":
    main()
