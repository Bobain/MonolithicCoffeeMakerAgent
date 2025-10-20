#!/usr/bin/env python3
"""Example 03: Real-World Singleton Enforcement Scenarios

This example demonstrates how singleton enforcement prevents actual problems
that could occur in the MonolithicCoffeeMakerAgent system.

Run this example:
    poetry run python examples/singleton_enforcement/03_real_world_scenarios.py
"""

import os
import tempfile
import time
from pathlib import Path

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType


class SimulatedCodeDeveloper:
    """Simulated code_developer agent that writes to files."""

    def __init__(self, name: str, work_dir: Path):
        """Initialize the simulated agent."""
        self.name = name
        self.work_dir = work_dir
        self.log_file = work_dir / "developer.log"

    def write_code(self, filename: str, content: str):
        """Simulate writing code to a file."""
        filepath = self.work_dir / filename
        print(f"   [{self.name}] Writing to {filename}...")

        # Simulate some processing time
        time.sleep(0.01)

        # Write to file
        with open(filepath, "w") as f:
            f.write(f"# Written by {self.name}\n")
            f.write(content)

        # Log the action
        with open(self.log_file, "a") as f:
            f.write(f"{self.name}: Wrote {filename}\n")

        print(f"   [{self.name}] ✅ Wrote {filename}")


def scenario_1_file_corruption_prevention():
    """Scenario: Prevent file corruption from duplicate code_developer instances."""
    print("\n" + "=" * 60)
    print("Scenario 1: File Corruption Prevention")
    print("=" * 60)
    print("\nWithout singleton enforcement, two code_developer instances")
    print("could write to the same files simultaneously, causing corruption.")

    registry = AgentRegistry()
    registry.reset()

    # Create temporary work directory
    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir)

        print("\n1. First code_developer instance starts...")
        try:
            registry.register_agent(AgentType.CODE_DEVELOPER)
            dev1 = SimulatedCodeDeveloper("Developer-1", work_dir)

            print("\n2. Developer-1 starts writing code...")
            dev1.write_code("main.py", "def main():\n    print('Hello from Dev1')")

            print("\n3. Attempting to start second code_developer instance...")
            try:
                registry.register_agent(AgentType.CODE_DEVELOPER)
                dev2 = SimulatedCodeDeveloper("Developer-2", work_dir)
                dev2.write_code("main.py", "def main():\n    print('Hello from Dev2')")
                print("   ❌ ERROR: Second instance should have been blocked!")

            except AgentAlreadyRunningError as e:
                print(f"   ✅ Second instance BLOCKED by singleton enforcement!")
                print(f"   ✅ File corruption prevented!")
                print(f"\n   Error message:")
                for line in str(e).split("\n"):
                    print(f"      {line}")

            # Show final file content (should only have Dev1's changes)
            main_py = work_dir / "main.py"
            print(f"\n4. Final content of main.py:")
            with open(main_py) as f:
                for line in f:
                    print(f"      {line.rstrip()}")
            print(f"\n   ✅ File contains only Developer-1's changes")
            print(f"   ✅ No corruption from interleaved writes")

        finally:
            registry.reset()


def scenario_2_roadmap_conflict_prevention():
    """Scenario: Prevent ROADMAP conflicts from duplicate project_manager instances."""
    print("\n" + "=" * 60)
    print("Scenario 2: ROADMAP Conflict Prevention")
    print("=" * 60)
    print("\nMultiple project_manager instances could create conflicting")
    print("updates to ROADMAP.md, causing lost updates or corrupted status.")

    registry = AgentRegistry()
    registry.reset()

    # Simulate ROADMAP status tracking
    roadmap_status = {"current_priority": None, "last_updated_by": None}

    def update_roadmap_status(manager_name: str, priority: str):
        """Simulate updating ROADMAP status."""
        print(f"   [{manager_name}] Updating ROADMAP to priority: {priority}")
        time.sleep(0.01)  # Simulate processing
        roadmap_status["current_priority"] = priority
        roadmap_status["last_updated_by"] = manager_name
        print(f"   [{manager_name}] ✅ ROADMAP updated")

    print("\n1. First project_manager instance starts...")
    try:
        registry.register_agent(AgentType.PROJECT_MANAGER)
        print("   ✅ Project Manager-1 registered")

        print("\n2. Manager-1 updates ROADMAP...")
        update_roadmap_status("Manager-1", "PRIORITY 5")

        print("\n3. Attempting to start second project_manager instance...")
        try:
            registry.register_agent(AgentType.PROJECT_MANAGER)
            update_roadmap_status("Manager-2", "PRIORITY 6")
            print("   ❌ ERROR: Second manager should have been blocked!")

        except AgentAlreadyRunningError:
            print(f"   ✅ Second project_manager BLOCKED!")
            print(f"   ✅ ROADMAP conflict prevented!")

        # Show final ROADMAP status
        print(f"\n4. Final ROADMAP status:")
        print(f"   • Current priority: {roadmap_status['current_priority']}")
        print(f"   • Last updated by: {roadmap_status['last_updated_by']}")
        print(f"\n   ✅ Only Manager-1 updated ROADMAP (no conflicts)")

    finally:
        registry.reset()


def scenario_3_resource_waste_prevention():
    """Scenario: Prevent resource waste from duplicate agents."""
    print("\n" + "=" * 60)
    print("Scenario 3: Resource Waste Prevention")
    print("=" * 60)
    print("\nRunning duplicate agents wastes CPU, memory, and API credits.")

    registry = AgentRegistry()
    registry.reset()

    # Simulate resource usage
    resources = {"cpu_cores": 0, "memory_gb": 0.0, "api_calls": 0}

    def allocate_resources(agent_name: str):
        """Simulate resource allocation."""
        print(f"   [{agent_name}] Allocating resources:")
        resources["cpu_cores"] += 2
        resources["memory_gb"] += 1.5
        resources["api_calls"] += 100
        print(f"      • CPU cores: +2")
        print(f"      • Memory: +1.5 GB")
        print(f"      • API calls: +100")

    print("\n1. First architect instance starts...")
    try:
        registry.register_agent(AgentType.ARCHITECT)
        allocate_resources("Architect-1")

        print(f"\n2. Current resource usage:")
        print(f"   • Total CPU cores: {resources['cpu_cores']}")
        print(f"   • Total memory: {resources['memory_gb']} GB")
        print(f"   • Total API calls: {resources['api_calls']}")

        print("\n3. Attempting to start duplicate architect...")
        try:
            registry.register_agent(AgentType.ARCHITECT)
            allocate_resources("Architect-2")
            print("   ❌ ERROR: Duplicate should have been blocked!")

        except AgentAlreadyRunningError:
            print(f"   ✅ Duplicate architect BLOCKED!")
            print(f"   ✅ Resource waste prevented!")

        print(f"\n4. Final resource usage:")
        print(f"   • Total CPU cores: {resources['cpu_cores']} (not 4)")
        print(f"   • Total memory: {resources['memory_gb']} GB (not 3.0 GB)")
        print(f"   • Total API calls: {resources['api_calls']} (not 200)")
        print(f"\n   ✅ Resources allocated only once")
        print(f"   ✅ Saved 2 CPU cores, 1.5 GB memory, 100 API calls")

    finally:
        registry.reset()


def scenario_4_daemon_startup_race_condition():
    """Scenario: Prevent race conditions during daemon startup."""
    print("\n" + "=" * 60)
    print("Scenario 4: Daemon Startup Race Condition Prevention")
    print("=" * 60)
    print("\nIf two users accidentally start the daemon simultaneously,")
    print("singleton enforcement prevents both from running.")

    registry = AgentRegistry()
    registry.reset()

    startup_sequence = []

    def start_daemon(user: str):
        """Simulate starting the code_developer daemon."""
        try:
            print(f"   [{user}] Starting code_developer daemon...")
            registry.register_agent(AgentType.CODE_DEVELOPER, pid=os.getpid())

            startup_sequence.append(f"{user}: Started")
            print(f"   [{user}] ✅ Daemon started successfully")

            # Simulate daemon work
            time.sleep(0.05)

            print(f"   [{user}] Daemon running...")
            startup_sequence.append(f"{user}: Running")

        except AgentAlreadyRunningError as e:
            startup_sequence.append(f"{user}: Blocked")
            print(f"   [{user}] ❌ Daemon startup blocked!")
            print(f"   [{user}] Reason: {str(e).split(chr(10))[0]}")

    print("\n1. User Alice starts daemon from Terminal 1...")
    start_daemon("Alice")

    print("\n2. User Bob tries to start daemon from Terminal 2...")
    start_daemon("Bob")

    print(f"\n3. Startup sequence:")
    for event in startup_sequence:
        print(f"   • {event}")

    print(f"\n   ✅ Only Alice's daemon started")
    print(f"   ✅ Bob was clearly informed daemon already running")
    print(f"   ✅ No race condition or duplicate work")

    registry.reset()


def scenario_5_crash_recovery():
    """Scenario: Demonstrate crash recovery with singleton enforcement."""
    print("\n" + "=" * 60)
    print("Scenario 5: Crash Recovery")
    print("=" * 60)
    print("\nAfter a crash, the registry clears, allowing restart.")

    registry = AgentRegistry()
    registry.reset()

    print("\n1. Starting code_developer daemon...")
    try:
        registry.register_agent(AgentType.CODE_DEVELOPER, pid=12345)
        print("   ✅ Daemon started (PID: 12345)")

        print("\n2. Simulating daemon work...")
        time.sleep(0.01)

        print("\n3. Simulating crash (unregister agent)...")
        registry.unregister_agent(AgentType.CODE_DEVELOPER)
        print("   💥 Daemon crashed and unregistered")

        print("\n4. Attempting to restart daemon...")
        registry.register_agent(AgentType.CODE_DEVELOPER, pid=12346)
        print("   ✅ Daemon restarted successfully (PID: 12346)")

        print("\n5. Verifying new daemon is running...")
        info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
        print(f"   • Current PID: {info['pid']}")
        print(f"   • Started at: {info['started_at']}")

        print(f"\n   ✅ Daemon recovered from crash")
        print(f"   ✅ New instance started with new PID")

    finally:
        registry.reset()


def scenario_6_monitoring_dashboard():
    """Scenario: Monitoring dashboard showing all running agents."""
    print("\n" + "=" * 60)
    print("Scenario 6: Agent Monitoring Dashboard")
    print("=" * 60)
    print("\nSingleton enforcement enables clear monitoring of running agents.")

    registry = AgentRegistry()
    registry.reset()

    print("\n1. Starting multiple agents...")
    agents_to_start = [
        (AgentType.CODE_DEVELOPER, 10001),
        (AgentType.PROJECT_MANAGER, 10002),
        (AgentType.ARCHITECT, 10003),
        (AgentType.ASSISTANT, 10004),
    ]

    for agent_type, pid in agents_to_start:
        registry.register_agent(agent_type, pid=pid)
        print(f"   ✅ Started {agent_type.value} (PID: {pid})")

    print("\n2. Monitoring Dashboard:")
    print("   " + "=" * 56)
    print(f"   {'Agent Type':<25} {'PID':<10} {'Status'}")
    print("   " + "-" * 56)

    all_agents = registry.get_all_registered_agents()
    for agent_type, info in all_agents.items():
        status = "🟢 Running"
        print(f"   {agent_type.value:<25} {info['pid']:<10} {status}")

    print("   " + "=" * 56)
    print(f"   Total Running Agents: {len(all_agents)}")

    print("\n3. Attempting to start duplicate architect...")
    try:
        registry.register_agent(AgentType.ARCHITECT, pid=10005)
    except AgentAlreadyRunningError:
        print(f"   ⚠️  Warning: Architect already running (PID: 10003)")
        print(f"   ✅ Singleton enforcement prevented duplicate")

    print("\n4. Dashboard after duplicate attempt:")
    print(f"   • Total Running Agents: {len(registry.get_all_registered_agents())} (unchanged)")
    print(f"   ✅ Dashboard shows accurate count")
    print(f"   ✅ No phantom duplicate agents")

    registry.reset()


def main():
    """Run all real-world scenario examples."""
    print("\n" + "=" * 60)
    print("Real-World Singleton Enforcement Scenarios")
    print("=" * 60)
    print("\nThese scenarios demonstrate how singleton enforcement")
    print("prevents actual problems in the MonolithicCoffeeMakerAgent system.")

    try:
        scenario_1_file_corruption_prevention()
        scenario_2_roadmap_conflict_prevention()
        scenario_3_resource_waste_prevention()
        scenario_4_daemon_startup_race_condition()
        scenario_5_crash_recovery()
        scenario_6_monitoring_dashboard()

        print("\n" + "=" * 60)
        print("✅ All real-world scenarios completed!")
        print("=" * 60)
        print("\nProblems Prevented by Singleton Enforcement:")
        print("  1. ✅ File corruption from concurrent writes")
        print("  2. ✅ ROADMAP conflicts and lost updates")
        print("  3. ✅ Resource waste (CPU, memory, API credits)")
        print("  4. ✅ Race conditions during daemon startup")
        print("  5. ✅ Confusion from duplicate agents")
        print("  6. ✅ Inaccurate monitoring and status tracking")
        print("\n💡 Key Insight: Singleton enforcement is NOT just a nice-to-have,")
        print("   it's a CRITICAL architectural requirement for system stability!")
        print()

    except Exception as e:
        print(f"\n❌ Error in scenarios: {e}")
        raise


if __name__ == "__main__":
    main()
