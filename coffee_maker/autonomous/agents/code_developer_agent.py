"""CodeDeveloperAgent - Autonomous implementation of ROADMAP priorities.

This agent is responsible for implementing priorities from ROADMAP.md autonomously.
It inherits from BaseAgent and implements continuous work loop that:
1. Syncs with roadmap branch (CFR-013)
2. Gets next planned priority
3. Checks spec exists (waits for architect if needed)
4. Implements priority using Claude API
5. Runs tests
6. Commits to roadmap branch
7. Notifies assistant for demo creation

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    CFR-008: Only architect creates technical specs
    CFR-011: Architect proactive spec creation (prevents blocking)
    CFR-013: All agents work on roadmap branch only
    US-056: CFR-013 enforcement implementation

Architecture:
    BaseAgent
      └── CodeDeveloperAgent
            ├── _do_background_work(): Implement next priority
            └── _handle_message(): Handle bug fixes, spec notifications

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Parse ROADMAP.md for next "📝 Planned" priority
    3. Check if technical spec exists
    4. If no spec: Send urgent message to architect, wait
    5. If spec exists: Implement priority using Claude API
    6. Run tests (pytest)
    7. Commit changes with agent identification
    8. Push to roadmap
    9. Send message to assistant: "Demo needed for priority X"
    10. Sleep for check_interval seconds (default: 5 minutes)

Message Handling:
    - bug_fix_request: Urgent fix from assistant after demo
    - spec_ready: Notification from architect that spec is ready
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.autonomous.roadmap_parser import RoadmapParser

logger = logging.getLogger(__name__)


class CodeDeveloperAgent(BaseAgent):
    """Code developer agent - Autonomous implementation execution.

    Responsibilities:
    - Implement priorities from ROADMAP (same as current daemon)
    - Stay on roadmap branch (CFR-013)
    - Frequent commits with agent identification
    - Notify assistant when features complete
    - Run tests before committing

    Continuous Loop:
    1. Sync with roadmap branch
    2. Get next planned priority
    3. Ensure spec exists (wait for architect if needed)
    4. Implement priority
    5. Run tests
    6. Commit changes
    7. Notify assistant for demo

    Example:
        >>> agent = CodeDeveloperAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=300  # 5 minutes
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 300,  # 5 minutes
        roadmap_file: str = "docs/roadmap/ROADMAP.md",
        auto_approve: bool = True,
    ):
        """Initialize CodeDeveloperAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between priority checks (default: 5 minutes)
            roadmap_file: Path to ROADMAP.md file
            auto_approve: Auto-approve implementation (default: True for daemon)
        """
        super().__init__(
            agent_type=AgentType.CODE_DEVELOPER,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.roadmap = RoadmapParser(roadmap_file)
        self.claude = ClaudeCLIInterface()
        self.auto_approve = auto_approve
        self.attempted_priorities: Dict[str, int] = {}
        self.max_retries = 3

        logger.info(f"✅ CodeDeveloperAgent initialized (auto_approve={auto_approve})")

    def _do_background_work(self):
        """Implement next planned priority from ROADMAP.

        Workflow:
        1. Sync with roadmap branch (pull latest)
        2. Parse ROADMAP for next planned priority
        3. Check if spec exists
           - If missing: Send urgent message to architect, return (wait)
           - If exists: Continue
        4. Implement priority using Claude API
        5. Run tests (pytest)
        6. Commit changes
        7. Push to roadmap
        8. Send message to assistant for demo
        9. Update metrics

        Returns early if:
        - No more planned priorities
        - Spec missing (wait for architect)
        - Implementation failed
        """
        # Sync with roadmap branch
        logger.info("🔄 Syncing with roadmap branch...")
        self.git.pull("roadmap")
        self.roadmap.reload()

        # Get next priority
        next_priority = self.roadmap.get_next_planned_priority()

        if not next_priority:
            logger.info("✅ No more planned priorities - all done!")
            self.current_task = None
            return

        priority_name = next_priority["name"]
        logger.info(f"📋 Next priority: {priority_name}")

        # Update current task for status tracking
        self.current_task = {
            "type": "implementation",
            "priority": priority_name,
            "title": next_priority.get("title", ""),
            "started_at": datetime.now().isoformat(),
            "progress": 0.0,
        }

        # Check spec exists (CFR-008: architect creates specs)
        spec_file = self._find_spec(next_priority)
        if not spec_file:
            logger.warning(f"⚠️  Spec missing for {priority_name}")
            logger.info("📨 Sending urgent spec request to architect...")

            # Send urgent message to architect
            self.send_message_to_agent(
                to_agent=AgentType.ARCHITECT,
                message_type="spec_request",
                content={
                    "priority": next_priority,
                    "reason": "Implementation blocked - spec missing",
                    "requester": "code_developer",
                },
                priority="urgent",
            )

            logger.info("⏳ Waiting for architect to create spec... (will retry next iteration)")
            return  # Return and check again next iteration

        logger.info(f"✅ Spec found: {spec_file}")

        # Check retry limit
        attempt_count = self.attempted_priorities.get(priority_name, 0)
        if attempt_count >= self.max_retries:
            logger.warning(f"⏭️  Skipping {priority_name} - already attempted {attempt_count} times")
            return

        # Increment attempt counter
        self.attempted_priorities[priority_name] = attempt_count + 1
        logger.info(
            f"🚀 Starting implementation (attempt {self.attempted_priorities[priority_name]}/{self.max_retries})"
        )

        # Implement priority
        success = self._implement_priority(next_priority, spec_file)

        if success:
            # Notify assistant to create demo
            self._notify_assistant_demo_needed(next_priority)

            # Update metrics
            self.metrics["priorities_completed"] = self.metrics.get("priorities_completed", 0) + 1
            self.metrics["last_completed_priority"] = priority_name
            self.metrics["last_completion_time"] = datetime.now().isoformat()

            logger.info(f"✅ {priority_name} implementation complete!")
        else:
            logger.error(f"❌ Implementation failed for {priority_name}")

    def _implement_priority(self, priority: Dict, spec_file: Path) -> bool:
        """Implement a priority using Claude API.

        Args:
            priority: Priority dictionary from ROADMAP
            spec_file: Path to technical specification

        Returns:
            True if successful, False otherwise
        """
        priority_name = priority["name"]
        logger.info(f"⚙️  Implementing {priority_name}...")

        # Update task progress
        self.current_task["progress"] = 0.2
        self.current_task["step"] = "Loading prompt"

        # Load implementation prompt
        prompt = load_prompt(
            PromptNames.IMPLEMENT_FEATURE,
            {
                "PRIORITY_NAME": priority_name,
                "PRIORITY_TITLE": priority.get("title", ""),
                "SPEC_FILE": str(spec_file),
                "PRIORITY_CONTENT": priority.get("content", "")[:1000],
            },
        )

        # Update task progress
        self.current_task["progress"] = 0.3
        self.current_task["step"] = "Executing Claude API"

        # Execute with Claude
        logger.info("🤖 Executing Claude API...")
        try:
            result = self.claude.execute_prompt(prompt, timeout=3600)
            if not result or not getattr(result, "success", False):
                logger.error(f"Claude API failed: {getattr(result, 'error', 'Unknown error')}")
                return False
            logger.info(f"✅ Claude API complete")
        except Exception as e:
            logger.error(f"❌ Error executing Claude API: {e}")
            return False

        # Update task progress
        self.current_task["progress"] = 0.6
        self.current_task["step"] = "Checking changes"

        # Check if files changed
        if self.git.is_clean():
            logger.warning("⚠️  No files changed - priority may already be complete")
            return True  # Return True to avoid retry loop

        # Update task progress
        self.current_task["progress"] = 0.7
        self.current_task["step"] = "Running tests"

        # Run tests
        test_result = self._run_tests()
        if not test_result:
            logger.error("❌ Tests failed!")
            return False

        logger.info("✅ All tests passed")

        # Update task progress
        self.current_task["progress"] = 0.8
        self.current_task["step"] = "Committing changes"

        # Commit changes
        commit_message = f"feat: Implement {priority_name} - {priority.get('title', '')}"
        self.commit_changes(commit_message)

        logger.info("✅ Changes committed and pushed")

        # Update task progress
        self.current_task["progress"] = 1.0
        self.current_task["step"] = "Complete"

        return True

    def _find_spec(self, priority: Dict) -> Optional[Path]:
        """Find technical specification for a priority.

        Looks in:
        - docs/architecture/specs/SPEC-{priority_number}-*.md
        - docs/roadmap/PRIORITY_{priority_number}_TECHNICAL_SPEC.md

        Args:
            priority: Priority dictionary

        Returns:
            Path to spec file if found, None otherwise
        """
        priority_number = priority.get("number", "")
        if not priority_number:
            return None

        # Try architect's specs directory first (CFR-008)
        specs_dir = Path("docs/architecture/specs")
        if specs_dir.exists():
            # Try multiple patterns to handle different naming conventions
            # PRIORITY 2.6 can match SPEC-2.6-*.md, SPEC-2-6-*.md, SPEC-002-6-*.md, etc.
            patterns = [
                f"SPEC-{priority_number}-*.md",  # SPEC-2.6-*.md
                f"SPEC-{priority_number.replace('.', '-')}-*.md",  # SPEC-2-6-*.md
                f"SPEC-{priority_number.zfill(5).replace('.', '-')}-*.md",  # SPEC-002-6-*.md (padded)
            ]

            # Also try without dots/dashes for edge cases
            if "." in priority_number:
                major, minor = priority_number.split(".", 1)
                patterns.extend(
                    [
                        f"SPEC-{major.zfill(3)}-{minor}-*.md",  # SPEC-002-6-*.md
                        f"SPEC-{major}-{minor}-*.md",  # SPEC-2-6-*.md
                    ]
                )

            for pattern in patterns:
                for spec_file in specs_dir.glob(pattern):
                    logger.info(f"Found spec: {spec_file}")
                    return spec_file

        # Fallback: Check old strategic spec location
        roadmap_spec = Path(f"docs/roadmap/PRIORITY_{priority_number}_TECHNICAL_SPEC.md")
        if roadmap_spec.exists():
            return roadmap_spec

        return None

    def _run_tests(self) -> bool:
        """Run pytest test suite.

        Returns:
            True if tests pass, False otherwise
        """
        import subprocess

        logger.info("🧪 Running tests...")

        try:
            result = subprocess.run(
                ["pytest", "tests/unit/", "--ignore=tests/unit/_deprecated", "-q"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            if result.returncode == 0:
                logger.info("✅ Tests passed")
                return True
            else:
                logger.error(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Tests timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ Error running tests: {e}")
            return False

    def _notify_assistant_demo_needed(self, priority: Dict):
        """Notify assistant that feature is complete and needs demo.

        Args:
            priority: Priority dictionary
        """
        self.send_message_to_agent(
            to_agent=AgentType.ASSISTANT,
            message_type="demo_request",
            content={
                "feature": priority["name"],
                "title": priority.get("title", ""),
                "acceptance_criteria": priority.get("acceptance_criteria", []),
                "description": priority.get("content", "")[:500],
            },
            priority="normal",
        )

        logger.info(f"📨 Notified assistant: demo needed for {priority['name']}")

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - bug_fix_request: Bug found during demo (from assistant)
        - spec_ready: Notification that spec is ready (from architect)

        Args:
            message: Message dictionary
        """
        msg_type = message.get("type")

        if msg_type == "bug_fix_request":
            # Bug found by assistant during demo
            bug_info = message["content"]
            priority_name = bug_info.get("feature", "unknown")

            logger.info(f"🐛 Bug fix request for {priority_name}")
            logger.info(f"Bug details: {bug_info.get('description', 'No description')}")

            # TODO: Implement bug fix logic
            # For now, just log and continue
            logger.warning("Bug fix not yet implemented - will be added in Phase 3")

        elif msg_type == "spec_ready":
            # Spec is now ready, can retry implementation
            priority_name = message["content"].get("priority", "unknown")
            logger.info(f"✅ Spec ready for {priority_name} - will retry next iteration")

        else:
            logger.warning(f"Unknown message type: {msg_type}")
