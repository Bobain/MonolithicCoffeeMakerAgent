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
from typing import Dict

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ArchitectAgent(BaseAgent):
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
        """Architect's background work: proactive spec creation.

        Workflow (CFR-011):
        1. Pull latest from roadmap
        2. Parse ROADMAP for planned priorities
        3. For each priority without a spec:
           - Determine if spec is needed (complexity-based)
           - Create specification
           - Document in ADR
           - Commit changes
        4. Sleep for check_interval

        This ensures code_developer always has specs available.
        """
        logger.info("🏗️  Architect: Checking for specs to create...")

        # TODO: Implement proactive spec creation
        # For now, just log and continue
        logger.info("ℹ️  Proactive spec creation not yet implemented")

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
        - spec_request (urgent): Code_developer blocked on missing spec
        - design_review: Request for design guidance
        - dependency_check: Request for dependency management

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")
        msg_priority = message.get("priority", "normal")

        if msg_type == "spec_request":
            # Urgent spec request from code_developer
            priority_info = message.get("content", {}).get("priority", {})
            priority_name = priority_info.get("name", "unknown")

            logger.warning(f"🚨 URGENT spec request from code_developer for {priority_name}")

            if msg_priority == "urgent":
                # TODO: Create spec immediately and notify code_developer
                logger.info(f"Creating spec for {priority_name} (URGENT)...")
                # In Phase 3: Implement spec creation

        elif msg_type == "design_review":
            # Request for design guidance
            feature = message.get("content", {}).get("feature", "unknown")
            logger.info(f"Design review requested for {feature}")
            # In Phase 3: Implement design review logic

        else:
            logger.warning(f"Unknown message type: {msg_type}")
