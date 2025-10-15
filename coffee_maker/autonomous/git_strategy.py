"""Git strategy for multi-agent collaboration.

CRITICAL: Never change branches in working directory!
- All agents write to 'roadmap' branch
- code_developer uses tags (not branches)
- Enables parallel agent operations safely

This module implements a tag-based git workflow that allows multiple AI agents
to work simultaneously without conflicts:
- Project stays on 'roadmap' branch permanently
- code_developer creates tags for features instead of branches
- Other agents (project_manager, assistant, etc.) commit directly to roadmap
- No branch switching = no conflicts = safe parallel operations

Example:
    >>> # code_developer workflow
    >>> GitStrategy.verify_on_roadmap_branch()  # Safety check
    >>> CodeDeveloperGitOps.start_feature("us-033", "streamlit-app")
    >>> # ... make changes ...
    >>> GitStrategy.commit_with_tag("feat: Add feature", "feature/us-033-complete")
    >>>
    >>> # Other agents workflow
    >>> GitStrategy.verify_on_roadmap_branch()  # Safety check
    >>> AgentGitOps.commit_doc_update("project_manager", "ROADMAP.md", "Add US-034")
"""

import logging
import subprocess
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


class GitStrategy:
    """Git operations following no-branch-switching policy.

    This class provides core git operations that enforce the roadmap-branch-only policy.
    All methods verify branch state before executing operations.

    Safety Features:
        - All operations verify we're on 'roadmap' branch
        - Raises RuntimeError if not on roadmap branch
        - Prevents accidental branch switches

    Example:
        >>> # Verify we're on roadmap branch
        >>> if GitStrategy.verify_on_roadmap_branch():
        ...     GitStrategy.create_tag("v1.0.0", "Release version 1.0.0")
    """

    @staticmethod
    def get_current_branch() -> str:
        """Get current branch name.

        Returns:
            str: Current branch name

        Raises:
            subprocess.CalledProcessError: If git command fails
        """
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    @staticmethod
    def verify_on_roadmap_branch() -> bool:
        """Verify we're on roadmap branch.

        This is a critical safety check that should be called before ANY git operation.

        Returns:
            bool: True if on roadmap branch, False otherwise

        Example:
            >>> if not GitStrategy.verify_on_roadmap_branch():
            ...     raise RuntimeError("Must be on roadmap branch!")
        """
        current = GitStrategy.get_current_branch()
        if current != "roadmap":
            logger.error(f"❌ CRITICAL: Not on roadmap branch! Current: {current}")
            return False
        return True

    @staticmethod
    def create_tag(tag_name: str, message: str) -> bool:
        """Create annotated tag (code_developer only).

        Creates a git tag at the current commit. This is how code_developer
        marks feature milestones instead of creating branches.

        Args:
            tag_name: Tag name (e.g., 'feature/us-033-start', 'v1.0.0')
            message: Tag annotation message

        Returns:
            bool: True if successful, False otherwise

        Raises:
            RuntimeError: If not on roadmap branch

        Example:
            >>> GitStrategy.create_tag(
            ...     "feature/us-033-streamlit-app-start",
            ...     "Start US-033: Streamlit App"
            ... )
            True
        """
        if not GitStrategy.verify_on_roadmap_branch():
            raise RuntimeError("Cannot create tag: not on roadmap branch")

        try:
            subprocess.run(["git", "tag", "-a", tag_name, "-m", message], check=True)
            logger.info(f"✅ Created tag: {tag_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create tag: {e}")
            return False

    @staticmethod
    def commit_with_tag(message: str, tag_name: Optional[str] = None) -> bool:
        """Commit changes and optionally create tag (code_developer only).

        This is the main workflow method for code_developer:
        1. Verify we're on roadmap branch
        2. Stage all changes
        3. Create commit
        4. Optionally create tag to mark milestone

        Args:
            message: Commit message
            tag_name: Optional tag to create after commit

        Returns:
            bool: True if successful, False otherwise

        Raises:
            RuntimeError: If not on roadmap branch

        Example:
            >>> GitStrategy.commit_with_tag(
            ...     "feat: Implement US-033 - Streamlit App",
            ...     "feature/us-033-streamlit-app-complete"
            ... )
            True
        """
        if not GitStrategy.verify_on_roadmap_branch():
            raise RuntimeError("Cannot commit: not on roadmap branch")

        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], check=True)

            # Commit
            subprocess.run(["git", "commit", "-m", message], check=True)
            logger.info(f"✅ Committed: {message[:50]}...")

            # Create tag if specified
            if tag_name:
                GitStrategy.create_tag(tag_name, f"Tag for commit: {message[:50]}...")

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Commit failed: {e}")
            return False

    @staticmethod
    def list_tags(pattern: Optional[str] = None) -> List[str]:
        """List all tags, optionally filtered by pattern.

        Args:
            pattern: Optional pattern to filter tags (e.g., 'feature/*', 'v*')

        Returns:
            List[str]: List of tag names matching pattern

        Example:
            >>> # Get all feature tags
            >>> feature_tags = GitStrategy.list_tags("feature/*")
            >>> # Get all version tags
            >>> version_tags = GitStrategy.list_tags("v*")
        """
        cmd = ["git", "tag"]
        if pattern:
            cmd.extend(["-l", pattern])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n") if result.stdout.strip() else []

    @staticmethod
    def get_latest_tag(pattern: Optional[str] = None) -> Optional[str]:
        """Get latest tag matching pattern.

        Args:
            pattern: Optional pattern to filter tags

        Returns:
            Optional[str]: Latest tag name or None if no tags found

        Example:
            >>> # Get latest feature tag
            >>> latest_feature = GitStrategy.get_latest_tag("feature/*")
            >>> print(f"Latest feature: {latest_feature}")
        """
        tags = GitStrategy.list_tags(pattern)
        return tags[-1] if tags else None

    @staticmethod
    def push_with_tags() -> bool:
        """Push commits and tags to remote.

        Pushes the roadmap branch and all tags to the remote repository.

        Returns:
            bool: True if successful, False otherwise

        Raises:
            RuntimeError: If not on roadmap branch

        Example:
            >>> GitStrategy.push_with_tags()
            True
        """
        if not GitStrategy.verify_on_roadmap_branch():
            raise RuntimeError("Cannot push: not on roadmap branch")

        try:
            # Push branch
            subprocess.run(["git", "push", "origin", "roadmap"], check=True)
            logger.info("✅ Pushed roadmap branch")

            # Push tags
            subprocess.run(["git", "push", "--tags"], check=True)
            logger.info("✅ Pushed tags")

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Push failed: {e}")
            return False


class CodeDeveloperGitOps:
    """Git operations specific to code_developer agent.

    This class provides high-level git workflows for the code_developer agent.
    It uses tags to mark feature milestones instead of creating branches.

    Tag Naming Convention:
        - Start: feature/{us-number}-{name}-start
        - Complete: feature/{us-number}-{name}-complete
        - Milestone: feature/{us-number}-{milestone-name}

    Example:
        >>> # Start implementing US-033
        >>> tag = CodeDeveloperGitOps.start_feature("us-033", "streamlit-app")
        >>> print(f"Created tag: {tag}")
        'feature/us-033-streamlit-app-start'
        >>>
        >>> # Mark milestone
        >>> CodeDeveloperGitOps.milestone_tag("us-033", "phase-1-complete")
        >>>
        >>> # Complete feature
        >>> tag = CodeDeveloperGitOps.complete_feature("us-033", "streamlit-app")
        >>> print(f"Completed with tag: {tag}")
        'feature/us-033-streamlit-app-complete'
    """

    @staticmethod
    def start_feature(us_number: str, feature_name: str) -> str:
        """Start new feature (creates initial tag).

        Creates a tag marking the beginning of feature implementation.
        This replaces the old "create feature branch" workflow.

        Args:
            us_number: User story number (e.g., 'us-033')
            feature_name: Feature name (e.g., 'streamlit-app')

        Returns:
            str: Tag name created

        Example:
            >>> tag = CodeDeveloperGitOps.start_feature("us-033", "streamlit-app")
            >>> print(tag)
            'feature/us-033-streamlit-app-start'
        """
        tag_name = f"feature/{us_number}-{feature_name}-start"
        message = f"Start {us_number}: {feature_name}"

        GitStrategy.create_tag(tag_name, message)
        logger.info(f"🚀 Started feature: {us_number}")
        return tag_name

    @staticmethod
    def complete_feature(us_number: str, feature_name: str) -> str:
        """Complete feature (creates final tag).

        Creates a tag marking the completion of feature implementation.
        This replaces the old "merge feature branch" workflow.

        Args:
            us_number: User story number (e.g., 'us-033')
            feature_name: Feature name (e.g., 'streamlit-app')

        Returns:
            str: Tag name created

        Example:
            >>> tag = CodeDeveloperGitOps.complete_feature("us-033", "streamlit-app")
            >>> print(tag)
            'feature/us-033-streamlit-app-complete'
        """
        tag_name = f"feature/{us_number}-{feature_name}-complete"
        message = f"Complete {us_number}: {feature_name}"

        GitStrategy.create_tag(tag_name, message)
        logger.info(f"✅ Completed feature: {us_number}")
        return tag_name

    @staticmethod
    def milestone_tag(us_number: str, milestone: str) -> str:
        """Create milestone tag.

        Creates a tag marking an intermediate milestone in feature implementation.
        Useful for multi-phase features.

        Args:
            us_number: User story number (e.g., 'us-033')
            milestone: Milestone name (e.g., 'phase-1-complete', 'backend-done')

        Returns:
            str: Tag name created

        Example:
            >>> tag = CodeDeveloperGitOps.milestone_tag("us-033", "phase-1-complete")
            >>> print(tag)
            'feature/us-033-phase-1-complete'
        """
        tag_name = f"feature/{us_number}-{milestone}"
        message = f"{us_number} milestone: {milestone}"

        GitStrategy.create_tag(tag_name, message)
        logger.info(f"🎯 Milestone reached: {us_number} - {milestone}")
        return tag_name


class AgentGitOps:
    """Git operations for non-code_developer agents.

    This class provides git workflows for agents that modify documentation
    and other non-code files (project_manager, assistant, etc.).

    These agents:
        - Always work on roadmap branch
        - Never switch branches
        - Commit directly to roadmap
        - Don't use tags (that's code_developer's domain)

    Example:
        >>> # project_manager updates ROADMAP
        >>> AgentGitOps.commit_doc_update(
        ...     "project_manager",
        ...     "ROADMAP.md",
        ...     "Added US-034: User Authentication"
        ... )
        True
    """

    @staticmethod
    def commit_doc_update(agent_name: str, doc_name: str, description: str) -> bool:
        """Commit documentation update (always on roadmap branch).

        This is the standard workflow for non-code_developer agents when
        they need to commit changes to documentation or other files.

        Args:
            agent_name: Name of agent making update (e.g., 'project_manager')
            doc_name: Name of document updated (e.g., 'ROADMAP.md', 'US-033-spec.md')
            description: Brief description of changes

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If not on roadmap branch

        Example:
            >>> AgentGitOps.commit_doc_update(
            ...     "project_manager",
            ...     "docs/ROADMAP.md",
            ...     "Added new priority US-034 for user authentication"
            ... )
            True
        """
        if not GitStrategy.verify_on_roadmap_branch():
            raise RuntimeError(f"❌ {agent_name} must operate on roadmap branch!")

        message = f"docs: Update {doc_name} ({agent_name})\n\n{description}"
        return GitStrategy.commit_with_tag(message)

    @staticmethod
    def commit_agent_work(agent_name: str, files_changed: List[str], summary: str, commit_type: str = "docs") -> bool:
        """Commit agent work with detailed file tracking.

        More granular commit method that tracks specific files changed.

        Args:
            agent_name: Agent making the commit
            files_changed: List of file paths that were modified
            summary: Summary of changes
            commit_type: Type of commit (docs, chore, feat, etc.)

        Returns:
            bool: True if successful

        Raises:
            RuntimeError: If not on roadmap branch

        Example:
            >>> AgentGitOps.commit_agent_work(
            ...     "project_manager",
            ...     ["docs/ROADMAP.md", "docs/US-034-spec.md"],
            ...     "Added US-034 and created technical spec",
            ...     "docs"
            ... )
            True
        """
        if not GitStrategy.verify_on_roadmap_branch():
            raise RuntimeError(f"❌ {agent_name} must operate on roadmap branch!")

        files_str = "\n".join([f"  - {f}" for f in files_changed])
        message = f"""{commit_type}: {summary} ({agent_name})

Files changed:
{files_str}

Agent: {agent_name}
Timestamp: {datetime.now().isoformat()}
"""
        return GitStrategy.commit_with_tag(message)
