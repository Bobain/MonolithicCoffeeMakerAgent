"""Technical Specification Management Mixin for DevDaemon.

This module provides technical specification creation and management functionality
for the autonomous development daemon, extracted from daemon.py to improve code
organization and maintainability.

Classes:
    SpecManagerMixin: Mixin providing _ensure_technical_spec() and _build_spec_creation_prompt()

Usage:
    class DevDaemon(SpecManagerMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files
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
        ...         self.roadmap_path = Path("docs/ROADMAP.md")
        ...         self.claude = ClaudeAPI()
        ...         self.git = GitManager()
        >>> daemon = DevDaemon()
        >>> priority = {"name": "US-021", "title": "Refactoring"}
        >>> daemon._ensure_technical_spec(priority)
        True
    """

    def _ensure_technical_spec(self, priority: dict) -> bool:
        """Ensure technical specification exists for this priority.

        BUG-002 FIX: Validate priority fields before accessing them.

        If spec doesn't exist, create it before implementing.

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

        # Determine spec filename
        # US-XXX -> US-XXX_TECHNICAL_SPEC.md
        # PRIORITY X -> PRIORITY_X_TECHNICAL_SPEC.md
        if priority_name.startswith("US-"):
            spec_filename = f"{priority_name}_TECHNICAL_SPEC.md"
        elif priority_name.startswith("PRIORITY"):
            # PRIORITY 2.6 -> PRIORITY_2_6_TECHNICAL_SPEC.md
            spec_name = priority_name.replace(" ", "_").replace(".", "_")
            spec_filename = f"{spec_name}_TECHNICAL_SPEC.md"
        else:
            # Generic fallback
            spec_name = priority_name.replace(" ", "_").replace(":", "")
            spec_filename = f"{spec_name}_TECHNICAL_SPEC.md"

        spec_path = self.roadmap_path.parent / spec_filename

        # Check if spec already exists
        if spec_path.exists():
            logger.info(f"✅ Technical spec exists: {spec_filename}")
            return True

        logger.info(f"📝 Technical spec not found: {spec_filename}")
        logger.info("Creating technical specification...")

        # Create spec using Claude
        spec_prompt = self._build_spec_creation_prompt(priority, spec_filename)

        try:
            result = self.claude.execute_prompt(spec_prompt, timeout=600)  # 10 min timeout

            if not result.success:
                logger.error(f"Failed to create technical spec: {result.error}")
                return False

            # Check if spec file was created
            if not spec_path.exists():
                logger.error("Claude completed but spec file was not created")
                return False

            logger.info(f"✅ Created technical spec: {spec_filename}")

            # Commit the spec
            self.git.commit(f"docs: Add technical spec for {priority_name}")
            self.git.push()

            return True

        except Exception as e:
            logger.error(f"Error creating technical spec: {e}")
            return False

    def _build_spec_creation_prompt(self, priority: dict, spec_filename: str) -> str:
        """Build prompt for creating technical specification.

        BUG-002 FIX: Use safe dictionary access to prevent KeyError crashes.

        Args:
            priority: Priority dictionary
            spec_filename: Name of spec file to create

        Returns:
            Prompt string
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

        return f"""Create a detailed technical specification for implementing {priority_name}.

Read the user story from docs/ROADMAP.md and create a comprehensive technical spec.

**Your Task:**
1. Read docs/ROADMAP.md to understand {priority_name}
2. Create docs/{spec_filename} with detailed technical specification
3. Include:
   - Prerequisites & Dependencies
   - Architecture Overview
   - Component Specifications
   - Data Flow Diagrams (in text/mermaid format)
   - Implementation Plan (step-by-step with time estimates)
   - Testing Strategy
   - Security Considerations
   - Performance Requirements
   - Risk Analysis
   - Success Criteria

**Important:**
- Be VERY specific and detailed
- Include file paths, class names, method signatures
- Provide code examples
- Break down into concrete tasks
- Estimate time for each task
- Make it actionable for implementation

**User Story Context:**
{priority_context}

Create the spec now in docs/{spec_filename}."""
