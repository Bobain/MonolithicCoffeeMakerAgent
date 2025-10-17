"""Technical Specification Management Mixin for DevDaemon.

This module provides technical specification enforcement and management functionality
for the autonomous development daemon, extracted from daemon.py to improve code
organization and maintainability.

US-047 UPDATE: Enforces CFR-008 - ARCHITECT-ONLY SPEC CREATION
- code_developer BLOCKS when spec is missing (does NOT create)
- Notifies user and architect about missing spec
- architect must create specs proactively in docs/architecture/specs/
- No delegation - just blocking with clear notification

Classes:
    SpecManagerMixin: Mixin providing _ensure_technical_spec() and spec checking

Usage:
    class DevDaemon(SpecManagerMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files

Architecture:
- daemon checks if technical spec exists for priority
- If spec exists: implementation proceeds normally
- If spec missing: daemon BLOCKS with notification
- architect creates specs proactively in docs/architecture/specs/
"""

import logging

logger = logging.getLogger(__name__)


class SpecManagerMixin:
    """Mixin providing technical specification management for daemon.

    This mixin provides methods for ensuring technical specifications exist
    before implementing priorities, and creating them using Claude if missing.

    Required attributes (provided by DevDaemon):
        - self.roadmap_path: Path to ROADMAP.md
        - self.claude: ClaudeAPI instance
        - self.git: GitManager instance

    Methods:
        - _ensure_technical_spec(): Ensure spec exists or create it
        - _build_spec_creation_prompt(): Build prompt for creating specs

    Example:
        >>> class DevDaemon(SpecManagerMixin):
        ...     def __init__(self):
        ...         self.roadmap_path = Path("docs/roadmap/ROADMAP.md")
        ...         self.claude = ClaudeAPI()
        ...         self.git = GitManager()
        >>> daemon = DevDaemon()
        >>> priority = {"name": "US-021", "title": "Refactoring"}
        >>> daemon._ensure_technical_spec(priority)
        True
    """

    def _ensure_technical_spec(self, priority: dict) -> bool:
        """Ensure technical specification exists for this priority.

        US-047: ENFORCE CFR-008 - Architect-Only Spec Creation
        1. Check if spec already exists
        2. If spec exists: allow implementation to proceed
        3. If spec missing: BLOCK and notify user/architect
        4. Do NOT create specs (code_developer cannot create specs per CFR-008)

        BUG-002 FIX: Validate priority fields before accessing them.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists, False if missing (blocks implementation)
        """
        # BUG-002: Validate required fields
        if not priority.get("name"):
            logger.error("❌ Priority missing 'name' field - cannot check for technical spec")
            return False

        priority_name = priority["name"]

        # Extract number from priority name for spec prefix
        if priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]
            spec_prefix = f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                major, minor = priority_num.split(".")
                spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
            else:
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        else:
            spec_prefix = f"SPEC-{priority_name.replace(' ', '-')}"

        # Locate architect's spec directory
        docs_dir = self.roadmap_path.parent.parent
        architect_spec_dir = docs_dir / "architecture" / "specs"

        # Step 1: Check if spec already exists
        if architect_spec_dir.exists():
            for spec_file in architect_spec_dir.glob(f"{spec_prefix}-*.md"):
                logger.info(f"✅ Technical spec found: {spec_file.name}")
                return True

        # Step 2: Spec missing - BLOCK (CFR-008 enforcement)
        logger.error(f"❌ CFR-008: Technical spec missing for {priority_name}")
        logger.error(f"   code_developer CANNOT create specs")
        logger.error(f"   → architect must create: docs/architecture/specs/{spec_prefix}-<name>.md")
        logger.error(f"   → BLOCKING implementation until spec exists")

        # Notify user and architect
        self._notify_spec_missing(priority, spec_prefix)

        # Return False to BLOCK implementation
        return False

    def _notify_spec_missing(self, priority: dict, spec_prefix: str) -> None:
        """Notify user and architect about missing technical specification.

        CFR-008: ARCHITECT-ONLY SPEC CREATION

        Creates a notification alerting the user and architect that a technical
        specification is missing for a priority. This blocks implementation until
        the architect creates the spec.

        Args:
            priority: Priority dictionary
            spec_prefix: Expected spec filename prefix (e.g., "SPEC-047")

        Example:
            >>> priority = {"name": "US-047", "title": "Enforce CFR-008"}
            >>> self._notify_spec_missing(priority, "SPEC-047")
        """
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "Unknown Title")

        # Create notification message
        title = f"CFR-008: Missing Spec for {priority_name}"
        message = (
            f"Technical specification missing for '{priority_title}'.\n\n"
            f"Priority: {priority_name}\n"
            f"Expected spec prefix: {spec_prefix}\n\n"
            f"CFR-008 ENFORCEMENT: code_developer cannot create specs.\n"
            f"→ architect must create: docs/architecture/specs/{spec_prefix}-<feature-name>.md\n\n"
            f"Implementation is BLOCKED until architect creates the spec."
        )

        context = {
            "priority_name": priority_name,
            "priority_title": priority_title,
            "spec_prefix": spec_prefix,
            "enforcement": "CFR-008",
            "action_required": "architect must create technical spec",
        }

        try:
            self.notifications.create_notification(
                type="error",
                title=title,
                message=message,
                priority="critical",
                context=context,
                sound=False,  # CFR-009: code_developer must use sound=False
                agent_id="code_developer",  # CFR-009: identify calling agent
            )

            logger.info(f"✅ Created CFR-008 notification for {priority_name}")

        except Exception as e:
            logger.error(f"Failed to create notification: {e}", exc_info=True)
            # Don't fail - notification is nice-to-have but not critical
