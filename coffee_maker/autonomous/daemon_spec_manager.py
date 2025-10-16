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

        US-045: Delegates spec creation to architect agent instead of
        creating specs directly. This follows proper ownership boundaries
        where architect owns docs/architecture/specs/.

        BUG-002 FIX: Validate priority fields before accessing them.

        If spec doesn't exist, delegates to architect to create it.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists or was created successfully by architect
        """
        # BUG-002: Validate required fields
        if not priority.get("name"):
            logger.error("❌ Priority missing 'name' field - cannot create technical spec")
            return False

        if not priority.get("content"):
            logger.warning(f"⚠️  Priority {priority.get('name')} has no content - will use title only in spec")

        priority_name = priority["name"]

        # US-045: Check if spec exists in architect's location (docs/architecture/specs/)
        # Generate expected spec filename based on priority name
        # US-XXX -> SPEC-XXX-feature-name.md
        # PRIORITY X -> SPEC-00X-feature-name.md

        # Extract number from priority name
        if priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]  # "US-033" -> "033"
            spec_prefix = f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            # PRIORITY 9 -> SPEC-009
            # PRIORITY 2.6 -> SPEC-002-6
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                # Handle decimal priorities like 2.6
                major, minor = priority_num.split(".")
                spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
            else:
                # Handle single-digit priorities like 9
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        else:
            # Generic fallback
            spec_prefix = f"SPEC-{priority_name.replace(' ', '-')}"

        # Look for existing spec in architect's directory
        # US-045: roadmap_path is docs/roadmap/ROADMAP.md
        # We need docs/architecture/specs/, so go up 2 levels to docs/
        docs_dir = self.roadmap_path.parent.parent  # From docs/roadmap/ROADMAP.md -> docs/
        architect_spec_dir = docs_dir / "architecture" / "specs"

        # Search for any spec matching the prefix
        existing_spec = None
        if architect_spec_dir.exists():
            for spec_file in architect_spec_dir.glob(f"{spec_prefix}-*.md"):
                existing_spec = spec_file
                logger.info(f"✅ Technical spec exists: {spec_file.name}")
                return True

        logger.info(f"📝 Technical spec not found for {priority_name}")
        logger.info(f"🏗️  Delegating spec creation to architect agent...")

        # US-045: Delegate to architect agent instead of creating spec directly
        delegation_prompt = self._build_architect_delegation_prompt(priority, spec_prefix)

        try:
            result = self.claude.execute_prompt(delegation_prompt, timeout=600)  # 10 min timeout

            if not result.success:
                logger.error(f"❌ architect delegation failed: {result.error}")
                return False

            # US-045: Check if architect created the spec
            # Re-scan the specs directory for new files
            if not architect_spec_dir.exists():
                logger.error("❌ architect spec directory doesn't exist after delegation")
                return False

            # Find newly created spec
            new_spec = None
            for spec_file in architect_spec_dir.glob(f"{spec_prefix}-*.md"):
                if spec_file != existing_spec:  # New file created
                    new_spec = spec_file
                    break

            if not new_spec:
                logger.error("❌ architect completed but spec file was not created")
                logger.error(f"   Expected spec in: {architect_spec_dir}")
                logger.error(f"   Expected prefix: {spec_prefix}-*.md")
                return False

            logger.info(f"✅ architect created technical spec: {new_spec.name}")

            # Commit the spec
            self.git.commit(f"docs: Add technical spec for {priority_name} (architect)")
            self.git.push()

            return True

        except Exception as e:
            logger.error(f"❌ Error delegating to architect: {e}")
            return False

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
