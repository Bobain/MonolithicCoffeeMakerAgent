"""ArchitectAgent - Proactive technical specification creation.

This agent is responsible for creating technical specifications BEFORE code_developer
needs them, ensuring code_developer is never blocked waiting for specs.

Architecture:
    BaseAgent
      └── ArchitectAgent
            ├── _do_background_work(): Proactive spec creation
            └── _handle_message(): Urgent spec requests from code_developer

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    CFR-008: Only architect creates technical specs
    CFR-011: Architect proactive spec creation (prevents blocking)
    CFR-013: All agents work on roadmap branch only
    US-057: Strategic requirement for multi-agent system

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Parse ROADMAP.md for planned priorities
    3. For each priority WITHOUT a spec:
       - Check if it needs a technical spec (complexity-based)
       - Create specification using Claude API
       - Document decision in ADR (Architectural Decision Record)
       - Commit changes
    4. Sleep for check_interval seconds (default: 1 hour)

Message Handling:
    - spec_request (urgent): Immediate spec creation from code_developer
    - design_review: Reactive design guidance from other agents

Message Format:
    {
        "type": "spec_request",
        "priority": "urgent" or "normal",
        "content": {
            "priority": priority_dict,
            "reason": "Implementation blocked - spec missing",
            "requester": "code_developer"
        }
    }
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent
from coffee_maker.autonomous.agents.architect_skills_mixin import ArchitectSkillsMixin

logger = logging.getLogger(__name__)


class ArchitectAgent(ArchitectSkillsMixin, BaseAgent):
    """Architect agent - Proactive technical specification creation.

    Responsibilities:
    - Proactively create technical specs for planned priorities (CFR-011)
    - Respond urgently to spec requests from code_developer (CFR-012)
    - Document architectural decisions (ADRs)
    - Manage dependencies in pyproject.toml
    - Provide design guidance to other agents

    Key Insight (CFR-011 - Proactive Spec Creation):
        Architect doesn't wait for code_developer to request specs.
        Instead, it continuously creates specs for planned priorities,
        ensuring code_developer NEVER blocks on missing specs.

    Example:
        >>> agent = ArchitectAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=3600  # 1 hour
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 3600,  # 1 hour for proactive spec creation
        roadmap_file: str = "docs/roadmap/ROADMAP.md",
    ):
        """Initialize ArchitectAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between spec creation checks (default: 1 hour)
            roadmap_file: Path to ROADMAP.md file
        """
        super().__init__(
            agent_type=AgentType.ARCHITECT,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.roadmap_file = roadmap_file
        self.specs_dir = Path("docs/architecture/specs")
        self.adrs_dir = Path("docs/architecture/decisions")

        # Create directories if they don't exist
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.adrs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ ArchitectAgent initialized (proactive spec creation)")

    def _do_background_work(self):
        """Architect's background work: skills integration + proactive spec creation.

        Workflow (Enhanced with Skills):
        1. Process commit review requests (CRITICAL priority)
        2. Run weekly refactoring analysis (if Monday + >7 days)
        3. Pull latest from roadmap
        4. Parse ROADMAP for planned priorities
        5. For each priority without a spec:
           - Run architecture reuse check (MANDATORY)
           - Determine if spec is needed (complexity-based)
           - Create specification
           - Document in ADR
           - Commit changes
        6. Sleep for check_interval

        This ensures code_developer always has specs available.
        """
        # STEP 1 & 2: Enhanced background work from mixin (commit reviews + refactoring)
        self._enhanced_background_work()

        # STEP 3+: Original proactive spec creation
        logger.info("🏗️  Architect: Checking for specs to create...")

        # Sync with roadmap branch
        logger.info("🔄 Syncing with roadmap branch...")
        self.git.pull("roadmap")

        # Parse ROADMAP for priorities
        from coffee_maker.autonomous.roadmap_parser import RoadmapParser

        roadmap = RoadmapParser(self.roadmap_file)

        # Get all planned priorities
        priorities = roadmap.get_priorities()
        planned = [p for p in priorities if "planned" in p["status"].lower() or "📝" in p["status"]]

        logger.info(f"Found {len(planned)} planned priorities to check for specs")

        # Check each planned priority for missing specs
        for priority in planned:
            priority_number = priority.get("number", "")
            priority_name = priority.get("name", "")

            if not priority_number:
                continue

            # Check if spec already exists
            spec_file = self._find_existing_spec(priority_number)

            if spec_file:
                logger.info(f"✅ Spec exists for {priority_name}: {spec_file.name}")
                continue

            # Spec missing - create it!
            logger.warning(f"📝 Creating spec for {priority_name}")
            self._create_spec_for_priority(priority)
            break  # Create one spec per iteration

        # Update metrics
        self.metrics["specs_created"] = self.metrics.get("specs_created", 0)
        self.metrics["last_check"] = datetime.now().isoformat()

        # Update current task
        self.current_task = {
            "type": "spec_creation",
            "status": "idle",
            "last_check": datetime.now().isoformat(),
        }

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - commit_review_request: Code_developer commit needs review (handled in background work)
        - spec_request (urgent): Code_developer blocked on missing spec
        - design_review: Request for design guidance
        - dependency_check: Request for dependency management

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")
        msg_priority = message.get("priority", "normal")

        if msg_type == "commit_review_request":
            # Commit review requests are handled by _process_commit_reviews() in background work
            # Just log it here for visibility
            commit_sha = message.get("content", {}).get("commit_sha", "unknown")
            logger.info(f"📬 Commit review request queued: {commit_sha[:7]} (priority: {msg_priority})")
            # Review will be processed in next background work iteration

        elif msg_type == "spec_request":
            # Urgent spec request from code_developer
            priority_info = message.get("content", {}).get("priority", {})
            priority_name = priority_info.get("name", "unknown")

            logger.warning(f"🚨 URGENT spec request from code_developer for {priority_name}")

            if msg_priority == "urgent":
                logger.info(f"Creating spec for {priority_name} (URGENT)...")
                # Create spec immediately
                self._create_spec_for_priority(priority_info)

                # Notify code_developer that spec is ready
                self.send_message_to_agent(
                    to_agent=AgentType.CODE_DEVELOPER,
                    message_type="spec_ready",
                    content={
                        "priority": priority_name,
                        "spec_file": f"SPEC-{priority_info.get('number', 'unknown')}-*.md",
                    },
                    priority="normal",
                )

                logger.info(f"✅ Spec created for {priority_name}, notified code_developer")

        elif msg_type == "design_review":
            # Request for design guidance
            feature = message.get("content", {}).get("feature", "unknown")
            logger.info(f"Design review requested for {feature}")
            # In Phase 3: Implement design review logic

        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def _find_existing_spec(self, priority_number: str) -> Optional[Path]:
        """Find existing technical specification for a priority.

        Args:
            priority_number: Priority number (e.g., "9", "2.6")

        Returns:
            Path to spec file if found, None otherwise
        """
        # Try architect's specs directory (CFR-008)
        specs_dir = self.specs_dir
        if specs_dir.exists():
            # Try multiple patterns
            patterns = [
                f"SPEC-{priority_number}-*.md",
                f"SPEC-{priority_number.replace('.', '-')}-*.md",
                f"SPEC-{priority_number.zfill(3)}-*.md",
            ]

            # Also try without dots/dashes for edge cases
            if "." in priority_number:
                major, minor = priority_number.split(".", 1)
                patterns.extend(
                    [
                        f"SPEC-{major.zfill(3)}-{minor}-*.md",
                        f"SPEC-{major}-{minor}-*.md",
                    ]
                )

            for pattern in patterns:
                for spec_file in specs_dir.glob(pattern):
                    return spec_file

        return None

    def _create_spec_for_priority(self, priority: Dict):
        """Create technical specification for a priority using Claude.

        MANDATORY STEP: Run architecture reuse check BEFORE creating spec.
        This ensures we always check existing components first.

        Args:
            priority: Priority dictionary from ROADMAP
        """
        priority_name = priority.get("name", "unknown")
        priority_number = priority.get("number", "unknown")
        priority_title = priority.get("title", "")
        priority_content = priority.get("content", "")

        logger.info(f"📝 Creating spec for {priority_name}: {priority_title}")

        # Update current task
        self.current_task = {
            "type": "spec_creation",
            "priority": priority_name,
            "started_at": datetime.now().isoformat(),
            "progress": 0.1,
        }

        # MANDATORY: Run architecture reuse check BEFORE spec creation
        logger.info(f"🔍 Running MANDATORY architecture reuse check for {priority_name}")
        reuse_analysis = self._run_architecture_reuse_check_before_spec(priority)

        # Update progress
        self.current_task["progress"] = 0.3

        # Load prompt
        from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

        # Include reuse analysis in the spec creation context
        spec_context = f"""{priority_content[:1500]}

## 🔍 Architecture Reuse Analysis

{reuse_analysis}

**IMPORTANT**: Use components from the reuse analysis above when creating this spec.
"""

        prompt = load_prompt(
            PromptNames.CREATE_TECHNICAL_SPEC,
            {
                "PRIORITY_NAME": priority_name,
                "PRIORITY_TITLE": priority_title,
                "PRIORITY_CONTENT": spec_context,
                "SPEC_NUMBER": priority_number,
            },
        )

        # Update progress
        self.current_task["progress"] = 0.4

        # Execute with Claude
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

        claude = ClaudeCLIInterface()
        logger.info("🤖 Executing Claude API for spec creation...")

        try:
            result = claude.execute_prompt(prompt, timeout=3600)
            if not result or not getattr(result, "success", False):
                logger.error(f"Claude API failed: {getattr(result, 'error', 'Unknown error')}")
                return
            logger.info("✅ Claude API complete")
        except Exception as e:
            logger.error(f"❌ Error executing Claude API: {e}")
            return

        # Update progress
        self.current_task["progress"] = 0.8

        # Commit changes
        commit_message = f"docs: Add technical spec for {priority_name} - {priority_title}"
        self.commit_changes(commit_message)

        logger.info(f"✅ Spec created and committed for {priority_name}")

        # Update metrics
        self.metrics["specs_created"] = self.metrics.get("specs_created", 0) + 1
        self.metrics["last_spec_created"] = priority_name
        self.metrics["last_spec_time"] = datetime.now().isoformat()

        # Update progress
        self.current_task["progress"] = 1.0
        self.current_task["status"] = "complete"
