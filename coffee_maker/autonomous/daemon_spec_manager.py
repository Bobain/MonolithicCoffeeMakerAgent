"""Technical Specification Management Mixin for DevDaemon.

This module provides technical specification enforcement and management functionality
for the autonomous development daemon, extracted from daemon.py to improve code
organization and maintainability.

US-045 UPDATE: Daemon delegates spec creation to architect
- code_developer checks if spec exists
- If missing: delegates to architect via Claude
- architect creates specs in docs/architecture/specs/
- daemon verifies spec was created and proceeds

US-047 UPDATE: Enforces CFR-008 - ARCHITECT-ONLY SPEC CREATION
- code_developer BLOCKS when spec is missing (does NOT create)
- Notifies user and architect about missing spec
- architect must create specs proactively in docs/architecture/specs/

Classes:
    SpecManagerMixin: Mixin providing _ensure_technical_spec() and spec checking

Usage:
    class DevDaemon(SpecManagerMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files

Architecture:
- daemon checks if technical spec exists for priority
- If spec exists: implementation proceeds normally
- If spec missing: daemon delegates to architect to create it
- architect creates specs in docs/architecture/specs/
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

        US-045: Delegate spec creation to architect
        1. Check if spec already exists
        2. If missing: delegate to architect via Claude
        3. Verify architect created the spec
        4. Return True/False based on success

        BUG-002 FIX: Validate priority fields before accessing them.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists or was created by architect, False if failed
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

        # Warn if priority has no content
        if not priority.get("content"):
            logger.warning(f"⚠️  Priority '{priority_name}' has no content - spec may be incomplete")

        # Step 2: Spec missing - delegate to architect
        logger.info(f"📋 Technical spec missing for {priority_name}")
        logger.info(f"   Expected spec prefix: {spec_prefix}")
        logger.info("🤝 Delegating to architect to create spec...")

        # Build delegation prompt
        delegation_prompt = self._build_architect_delegation_prompt(priority, spec_prefix)

        # Execute delegation
        try:
            logger.info("📤 Sending delegation request to architect...")
            result = self.claude.execute_prompt(delegation_prompt)

            if not result or not result.success:
                logger.error(f"❌ Architect delegation failed: {result.error if result else 'No result'}")
                self._notify_spec_missing(priority, spec_prefix)
                return False

            logger.info("✅ Architect delegation request sent successfully")

        except Exception as e:
            logger.error(f"❌ Error delegating to architect: {e}")
            self._notify_spec_missing(priority, spec_prefix)
            return False

        # Step 3: Verify spec was created
        logger.info("⏳ Waiting for architect to create spec...")
        if architect_spec_dir.exists():
            for spec_file in architect_spec_dir.glob(f"{spec_prefix}-*.md"):
                logger.info(f"✅ Architect created spec: {spec_file.name}")
                return True

        # Spec creation failed
        logger.error(f"❌ Architect did not create spec for {priority_name}")
        logger.error(f"   Expected: {architect_spec_dir / f'{spec_prefix}-*.md'}")
        self._notify_spec_missing(priority, spec_prefix)
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

    def _build_architect_delegation_prompt(self, priority: dict, spec_prefix: str) -> str:
        """Build prompt for delegating spec creation to architect.

        US-045: This prompt explicitly requests the architect agent to create
        a technical specification in docs/architecture/specs/.

        Args:
            priority: Priority dictionary with name, title, content
            spec_prefix: Expected spec filename prefix (e.g., "SPEC-009")

        Returns:
            Delegation prompt string

        Example:
            >>> priority = {"name": "PRIORITY 9", "title": "Communication", "content": "..."}
            >>> prompt = self._build_architect_delegation_prompt(priority, "SPEC-009")
            >>> print("DELEGATION TO ARCHITECT" in prompt)
            True
        """
        priority_name = priority.get("name", "Unknown")
        priority_title = priority.get("title", "Unknown")
        priority_content = priority.get("content", "")

        prompt = f"""DELEGATION TO ARCHITECT AGENT - US-045

You are being delegated a task by code_developer daemon to create a technical specification.

CONTEXT:
- Priority Name: {priority_name}
- Priority Title: {priority_title}
- Spec Prefix: {spec_prefix}
- Target Location: docs/architecture/specs/{spec_prefix}-<feature-name>.md

PRIORITY DETAILS:
{priority_content if priority_content else "(See ROADMAP.md for full context)"}

TASK:
1. Review the priority from docs/roadmap/ROADMAP.md if needed for full context
2. Create a technical specification file at: docs/architecture/specs/{spec_prefix}-<feature-name>.md
3. The filename should be descriptive (e.g., {spec_prefix}-enhanced-communication.md)
4. Include in the spec:
   - Problem Statement
   - Architecture Overview
   - Component Specifications
   - Data Flow
   - Implementation Plan
   - Testing Strategy
   - Security Considerations
   - Success Criteria

IMPORTANT:
- This is a delegation from code_developer (US-045)
- You MUST create the spec file so code_developer can proceed with implementation
- The file MUST exist at docs/architecture/specs/ with filename matching {spec_prefix}-*
- Do NOT ask code_developer to create the spec - YOU create it
- Return success after creating the file

DEADLINE: Create the spec immediately and verify it exists.
"""
        return prompt

    def _build_spec_creation_prompt(self, priority: dict, spec_filename: str) -> str:
        """Build prompt for creating technical specifications.

        DEPRECATED: Use _build_architect_delegation_prompt() instead.

        This method is kept for backwards compatibility with tests that expect it.
        It redirects to the delegation prompt approach used by US-045.

        Args:
            priority: Priority dictionary
            spec_filename: Output filename

        Returns:
            Spec creation prompt string

        Example:
            >>> priority = {"name": "US-033", "title": "App", "content": "..."}
            >>> prompt = self._build_spec_creation_prompt(priority, "SPEC-033-app.md")
            >>> print("SPEC" in prompt)
            True
        """
        # Extract spec prefix from filename if possible
        spec_prefix = spec_filename.replace(".md", "").split("-")[0]
        if len(spec_filename.split("-")) > 1:
            # Try to extract number from filename
            try:
                spec_number = spec_filename.split("-")[1]
                spec_prefix = f"SPEC-{spec_number}"
            except IndexError:
                pass

        # Redirect to delegation prompt
        return self._build_architect_delegation_prompt(priority, spec_prefix)
