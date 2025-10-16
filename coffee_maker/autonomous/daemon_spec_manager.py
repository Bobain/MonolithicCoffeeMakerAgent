"""Technical Specification Management Mixin for DevDaemon.

This module provides technical specification creation and management functionality
for the autonomous development daemon, extracted from daemon.py to improve code
organization and maintainability.

US-045 UPDATE: Spec creation now delegates to architect agent instead of creating
specs directly. This follows proper ownership boundaries where architect owns
docs/architecture/specs/ directory.

Classes:
    SpecManagerMixin: Mixin providing _ensure_technical_spec() and architect delegation

Usage:
    class DevDaemon(SpecManagerMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files

Enhanced with centralized prompt loading:
- Prompts stored in .claude/commands/ for multi-AI provider support
- Easy migration to Gemini, OpenAI, or other LLMs

US-045 Architecture:
- daemon delegates to architect via execute_prompt()
- architect creates specs in docs/architecture/specs/SPEC-XXX-name.md
- daemon verifies spec creation and proceeds with implementation
"""

import logging

from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

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

        US-045: Phase 1 - Hybrid approach with template fallback
        1. Check if spec already exists
        2. Try architect delegation (Phase 2 - not yet implemented)
        3. Fallback to template generation (Phase 1 - unblocks daemon NOW)

        BUG-002 FIX: Validate priority fields before accessing them.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists or was created successfully
        """
        # BUG-002: Validate required fields
        if not priority.get("name"):
            logger.error("❌ Priority missing 'name' field - cannot create technical spec")
            return False

        if not priority.get("content"):
            logger.warning(f"⚠️  Priority {priority.get('name')} has no content - will use title only in spec")

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
                logger.info(f"✅ Technical spec exists: {spec_file.name}")
                return True

        logger.info(f"📝 Technical spec not found for {priority_name}")

        # Step 2: Try architect delegation (Phase 2 - Tool Use API)
        # For now, skip to fallback
        logger.info(f"🏗️  Using template fallback to unblock daemon (US-045 Phase 1)...")

        # Step 3: Fallback to template generation
        return self._create_spec_from_template(priority, spec_prefix)

    def _build_architect_delegation_prompt(self, priority: dict, spec_prefix: str) -> str:
        """Build prompt for delegating technical specification creation to architect.

        US-045: Delegates spec creation to architect agent instead of creating
        specs directly. architect owns docs/architecture/specs/ and creates
        SPEC-XXX-feature-name.md files.

        Args:
            priority: Priority dictionary
            spec_prefix: Spec filename prefix (e.g., "SPEC-009" for PRIORITY 9)

        Returns:
            Prompt string requesting architect to create technical specification
        """
        # Safe dictionary access with defaults
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "No title")
        priority_content = priority.get("content", "")

        # Handle missing/empty content gracefully
        if not priority_content or len(priority_content.strip()) == 0:
            priority_context = f"Title: {priority_title}\nNo additional details provided in ROADMAP."
            logger.warning(f"Priority {priority_name} has no content - using title only for spec creation")
        else:
            # Safely truncate content
            priority_context = priority_content[:2000]
            if len(priority_content) > 2000:
                priority_context += "..."

        # US-045: Build delegation prompt for architect agent
        delegation_prompt = f"""🏗️  DELEGATION TO ARCHITECT AGENT

You are the code_developer daemon. You need a technical specification created for the following priority:

**Priority**: {priority_name}
**Title**: {priority_title}

**Details from ROADMAP.md**:
{priority_context}

**CRITICAL INSTRUCTION**: You MUST delegate this spec creation to the architect agent.

**Why delegate to architect?**
- architect owns docs/architecture/specs/ directory (per DOCUMENT_OWNERSHIP_MATRIX.md)
- You (code_developer) own implementation, NOT architectural design
- Proper separation of concerns: architect designs WHAT to build, you implement HOW

**What you need to do**:
1. Invoke the architect subagent using the Task tool
2. Request: "Create a technical specification for {priority_name}"
3. Provide the priority details above as context
4. architect will create: docs/architecture/specs/{spec_prefix}-<feature-name>.md

**Expected architect output**:
- Technical specification file in docs/architecture/specs/
- Filename pattern: {spec_prefix}-<descriptive-name>.md
- Contains: problem statement, architecture, components, testing strategy, rollout plan

**After architect creates the spec**:
- Verify the spec file exists in docs/architecture/specs/
- Report success/failure back to daemon

Please invoke the architect agent now to create the technical specification.
"""

        return delegation_prompt

    def _create_spec_from_template(self, priority: dict, spec_prefix: str) -> bool:
        """Create technical spec from template as fallback.

        US-045 Phase 1: Fallback mechanism to unblock daemon when architect
        delegation is not available.

        This method:
        1. Uses SpecTemplateManager to generate a basic spec
        2. Marks it with TODO for architect review
        3. Returns True so daemon can proceed
        4. Spec will be enhanced by architect later (Phase 2)

        Args:
            priority: Priority dictionary with name, title, content
            spec_prefix: Spec filename prefix (e.g., "SPEC-009")

        Returns:
            True if spec created successfully, False otherwise

        Example:
            >>> priority = {"name": "PRIORITY 9", "title": "Communication", "content": "..."}
            >>> self._create_spec_from_template(priority, "SPEC-009")
            True
        """
        try:
            from coffee_maker.autonomous.spec_template_manager import (
                SpecTemplateManager,
            )

            manager = SpecTemplateManager()

            # Generate spec filename from priority name
            priority_name = priority.get("name", "unknown")
            priority_title = priority.get("title", "Untitled")

            # Create slug from title for filename
            title_slug = priority_title.lower().replace(" ", "-").replace("/", "-")
            spec_filename = f"{spec_prefix}-{title_slug}.md"

            # Create spec from template
            success = manager.create_spec_from_template(
                priority=priority,
                spec_filename=spec_filename,
            )

            if not success:
                logger.error(f"Failed to create spec from template for {priority_name}")
                return False

            logger.info(f"✅ Created technical spec from template: {spec_filename}")
            logger.info(f"   (Marked for architect review - US-045 Phase 1 fallback)")

            # Commit the generated spec
            try:
                self.git.commit(f"docs: Add technical spec from template for {priority_name} (US-045)")
                self.git.push()
            except Exception as e:
                logger.warning(f"Could not commit spec: {e}")
                # Don't fail - spec is created even if commit fails

            return True

        except Exception as e:
            logger.error(f"Error creating spec from template: {e}", exc_info=True)
            return False

    def _build_spec_creation_prompt(self, priority: dict, spec_filename: str) -> str:
        """Build prompt for creating technical specification.

        DEPRECATED (US-045): This method is no longer used. Spec creation is
        delegated to architect via _build_architect_delegation_prompt().

        Kept for backwards compatibility and reference.

        BUG-002 FIX: Use safe dictionary access to prevent KeyError crashes.

        Enhanced: Now uses centralized prompt from .claude/commands/
        for easy migration to Gemini, OpenAI, or other LLMs.

        Args:
            priority: Priority dictionary
            spec_filename: Name of spec file to create

        Returns:
            Prompt string loaded from .claude/commands/create-technical-spec.md
        """
        # BUG-002: Safe dictionary access with defaults
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "No title")
        priority_content = priority.get("content", "")

        # Handle missing/empty content gracefully
        if not priority_content or len(priority_content.strip()) == 0:
            priority_context = f"Title: {priority_title}\nNo additional details provided in ROADMAP."
            logger.warning(f"Priority {priority_name} has no content - using title only for spec creation")
        else:
            # Safely truncate content
            priority_context = priority_content[:2000]
            if len(priority_content) > 2000:
                priority_context += "..."

        # Load prompt from centralized location (.claude/commands/)
        return load_prompt(
            PromptNames.CREATE_TECHNICAL_SPEC,
            {
                "PRIORITY_NAME": priority_name,
                "SPEC_FILENAME": spec_filename,
                "PRIORITY_CONTEXT": priority_context,
            },
        )
