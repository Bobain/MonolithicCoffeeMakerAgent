"""Git Operations Mixin for DevDaemon.

This module provides git-related operations for the autonomous development daemon,
extracted from daemon.py to improve code organization and maintainability.

Classes:
    GitOpsMixin: Mixin providing _sync_roadmap_branch() and _merge_to_roadmap()

Usage:
    class DevDaemon(GitOpsMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files
"""

import logging
import subprocess

from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_TYPE_ERROR,
)

logger = logging.getLogger(__name__)


class GitOpsMixin:
    """Mixin providing git operations for daemon.

    This mixin provides methods for synchronizing with the roadmap branch
    and merging feature branches back to roadmap for project visibility.

    Required attributes (provided by DevDaemon):
        - self.git: GitManager instance
        - self.notifications: NotificationDB instance

    Methods:
        - _sync_roadmap_branch(): Sync with origin/roadmap
        - _merge_to_roadmap(): Merge feature branch to roadmap

    Example:
        >>> class DevDaemon(GitOpsMixin):
        ...     def __init__(self):
        ...         self.git = GitManager()
        ...         self.notifications = NotificationDB()
        >>> daemon = DevDaemon()
        >>> daemon._sync_roadmap_branch()
        True
    """

    def _sync_roadmap_branch(self) -> bool:
        """Sync with 'roadmap' branch before each iteration.

        This ensures the daemon always works with the latest priorities
        and prevents working on stale/obsolete tasks.

        Returns:
            True if sync successful or not needed, False if sync failed

        Implementation:
            1. Fetch origin/roadmap
            2. Merge origin/roadmap into current branch
            3. Handle conflicts gracefully
        """
        try:
            # Fetch latest from roadmap branch
            result = subprocess.run(
                ["git", "fetch", "origin", "roadmap"],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to fetch roadmap branch: {result.stderr}")
                return False

            # Merge origin/roadmap
            result = subprocess.run(
                ["git", "merge", "origin/roadmap", "--no-edit"],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Check if merge conflict
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    logger.error("❌ Merge conflict with roadmap branch!")
                    logger.error("Manual intervention required to resolve conflicts")

                    # Abort merge
                    subprocess.run(
                        ["git", "merge", "--abort"],
                        cwd=self.git.repo_path,
                        capture_output=True,
                    )
                    return False
                else:
                    logger.warning(f"Merge failed: {result.stderr}")
                    return False

            logger.info("✅ Synced with 'roadmap' branch")
            return True

        except Exception as e:
            logger.error(f"Error syncing roadmap branch: {e}")
            return False

    def _merge_to_roadmap(self, message: str = "Sync progress to roadmap") -> bool:
        """Merge current feature branch to roadmap branch.

        US-029: CRITICAL - project_manager depends on this for visibility!

        This method ensures project_manager can see all progress in real-time
        by frequently merging feature branch changes to the roadmap branch.

        Called after:
        - Completing any sub-task
        - Updating ROADMAP.md (CRITICAL!)
        - Creating new tickets
        - Before sleep/idle

        Args:
            message: Description of what was accomplished

        Returns:
            True if merge successful, False if conflicts

        Example:
            >>> # After updating ROADMAP.md
            >>> self._merge_to_roadmap("Updated US-021 progress")
            True

            >>> # Before sleep
            >>> self._merge_to_roadmap("End of iteration checkpoint")
            True
        """
        try:
            # Get current branch
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=self.git.repo_path, text=True
            ).strip()

            if current_branch == "roadmap":
                logger.warning("Already on roadmap branch, skipping merge")
                return True

            # Commit any uncommitted changes
            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=self.git.repo_path, text=True)

            if status.strip():
                logger.info(f"Committing changes before merge: {message}")
                subprocess.run(["git", "add", "-A"], cwd=self.git.repo_path, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=self.git.repo_path, check=True)
                subprocess.run(
                    ["git", "push", "origin", current_branch],
                    cwd=self.git.repo_path,
                    check=True,
                )

            # Switch to roadmap
            subprocess.run(["git", "checkout", "roadmap"], cwd=self.git.repo_path, check=True)
            subprocess.run(["git", "pull", "origin", "roadmap"], cwd=self.git.repo_path, check=True)

            # Merge with --no-ff (preserves history)
            merge_result = subprocess.run(
                [
                    "git",
                    "merge",
                    "--no-ff",
                    "-m",
                    f"Merge {current_branch}: {message}",
                    current_branch,
                ],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
            )

            if merge_result.returncode != 0:
                # CONFLICT - abort and notify project_manager
                subprocess.run(["git", "merge", "--abort"], cwd=self.git.repo_path, check=True)
                subprocess.run(
                    ["git", "checkout", current_branch],
                    cwd=self.git.repo_path,
                    check=True,
                )

                # Create CRITICAL notification for project_manager
                self.notifications.create_notification(
                    type=NOTIF_TYPE_ERROR,
                    priority=NOTIF_PRIORITY_CRITICAL,
                    title=f"🚨 MERGE CONFLICT: {current_branch} → roadmap",
                    message=f"""Automatic merge to roadmap failed with conflicts.

⚠️  PROJECT_MANAGER VISIBILITY BLOCKED!

The roadmap branch is now out of sync with {current_branch}.
Manual intervention required to restore visibility.

Steps to resolve:
1. git checkout roadmap
2. git pull origin roadmap
3. git merge {current_branch}
4. Resolve conflicts in affected files
5. git add <resolved-files>
6. git commit
7. git push origin roadmap

Until resolved, project_manager cannot see latest progress.
""",
                )

                logger.error(f"Merge conflict: {current_branch} → roadmap")
                logger.error("PROJECT_MANAGER VISIBILITY BLOCKED!")
                return False

            # Push to origin/roadmap
            subprocess.run(["git", "push", "origin", "roadmap"], cwd=self.git.repo_path, check=True)

            # Switch back to feature branch
            subprocess.run(["git", "checkout", current_branch], cwd=self.git.repo_path, check=True)

            logger.info(f"✅ Merged {current_branch} → roadmap")
            logger.info(f"✅ project_manager can now see: {message}")
            return True

        except Exception as e:
            logger.error(f"Failed to merge to roadmap: {e}")
            logger.error("PROJECT_MANAGER CANNOT SEE PROGRESS!")

            # Try to recover
            try:
                subprocess.run(
                    ["git", "checkout", current_branch],
                    cwd=self.git.repo_path,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Failed to recover branch: {e}",
                    extra={"branch": current_branch, "returncode": e.returncode},
                )
            except Exception as e:
                logger.error(f"Unexpected error during branch recovery: {e}", exc_info=True)

            return False
