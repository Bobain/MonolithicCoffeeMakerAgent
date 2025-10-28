"""Git operations for autonomous daemon.

This module provides basic Git operations needed by the daemon:
- Branch creation
- Committing changes
- Pushing to remote
- Creating pull requests via gh CLI

Example:
    >>> from coffee_maker.autonomous.git_manager import GitManager
    >>>
    >>> git = GitManager()
    >>> git.create_branch("feature/new-feature")
    >>> git.commit("feat: Implement new feature")
    >>> git.push()
    >>> pr_url = git.create_pull_request("Add new feature", "Implementation complete")
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GitManager:
    """Manage Git operations for autonomous daemon.

    This class provides simple wrappers around Git commands to enable
    the daemon to manage branches, commits, and pull requests.

    Attributes:
        repo_path: Path to Git repository (default: current directory)

    Example:
        >>> git = GitManager()
        >>> if git.is_clean():
        ...     git.create_branch("feature/priority-3")
        ...     # ... make changes ...
        ...     git.commit("feat: Implement PRIORITY 3")
        ...     git.push()
    """

    def __init__(self, repo_path: Optional[str] = None):
        """Initialize Git manager.

        Args:
            repo_path: Path to repository (default: current directory)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        logger.info(f"GitManager initialized at {self.repo_path}")

    def _run_git(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        """Run git command.

        Args:
            *args: Git command arguments
            check: Raise exception on error

        Returns:
            CompletedProcess result
        """
        cmd = ["git", *args]
        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check,
        )

        return result

    def get_current_branch(self) -> str:
        """Get current branch name.

        Returns:
            Branch name

        Example:
            >>> git = GitManager()
            >>> branch = git.get_current_branch()
            >>> print(f"On branch: {branch}")
        """
        result = self._run_git("branch", "--show-current")
        branch = result.stdout.strip()
        logger.info(f"Current branch: {branch}")
        return branch

    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally.

        Args:
            branch_name: Branch name to check

        Returns:
            True if branch exists

        Example:
            >>> git = GitManager()
            >>> if git.branch_exists("feature/priority-3"):
            ...     print("Branch already exists")
        """
        try:
            result = self._run_git("branch", "--list", branch_name, check=False)
            exists = bool(result.stdout.strip())
            logger.debug(f"Branch {branch_name} exists: {exists}")
            return exists

        except subprocess.CalledProcessError:
            return False

    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> bool:
        """Create and checkout a new branch, or checkout if it already exists.

        Args:
            branch_name: Name for new branch
            from_branch: Base branch (default: current branch)

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.create_branch("feature/priority-3", from_branch="main")
        """
        try:
            # Check if branch already exists
            if self.branch_exists(branch_name):
                logger.info(f"Branch {branch_name} already exists, checking it out")
                self._run_git("checkout", branch_name)
                logger.info(f"Checked out existing branch: {branch_name}")
                return True

            # Create new branch
            if from_branch:
                self._run_git("checkout", from_branch)

            self._run_git("checkout", "-b", branch_name)
            logger.info(f"Created and checked out branch: {branch_name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create branch: {e.stderr}")
            return False

    def add(self, file_path: str) -> bool:
        """Add a specific file to staging area.

        Args:
            file_path: Path to file to add

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.add("docs/README.md")
        """
        try:
            self._run_git("add", file_path)
            logger.debug(f"Added file: {file_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add {file_path}: {e.stderr}")
            return False

    def add_all(self) -> bool:
        """Add all changes to staging area (git add -A).

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.add_all()
        """
        try:
            self._run_git("add", "-A")
            logger.debug("Added all changes")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add all: {e.stderr}")
            return False

    def commit(self, message: str, add_all: bool = True) -> bool:
        """Commit changes (legacy method, use commit_with_retry for robustness).

        Args:
            message: Commit message
            add_all: Whether to add all changes (git add -A)

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.commit("feat: Implement PRIORITY 3\\n\\nDetailed description...")
        """
        try:
            if add_all:
                self.add_all()

            self._run_git("commit", "-m", message)
            logger.info(f"Committed: {message[:50]}...")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit: {e.stderr}")
            return False

    def commit_with_retry(self, message: str, add_all: bool = True, max_retries: int = 10) -> bool:
        """Commit changes with automatic retry for pre-commit hook modifications.

        This method handles the common case where pre-commit hooks (like black, isort,
        trailing-whitespace, end-of-file-fixer) modify files during commit. It will
        automatically stage the modified files and retry the commit up to max_retries times.

        Args:
            message: Commit message
            add_all: Whether to add all changes (git add -A) before first attempt
            max_retries: Maximum number of retry attempts (default: 10)

        Returns:
            True if commit succeeded, False if failed after all retries

        Example:
            >>> git = GitManager()
            >>> # Will retry automatically if pre-commit hooks modify files
            >>> success = git.commit_with_retry("feat: Add new feature")
            >>> if not success:
            ...     print("Failed to commit after 10 retries")
        """
        attempt = 0

        while attempt < max_retries:
            attempt += 1

            try:
                # Add files on first attempt or after hooks modified them
                if add_all or attempt > 1:
                    self.add_all()
                    logger.debug(f"Added all changes (attempt {attempt}/{max_retries})")

                # Try to commit
                self._run_git("commit", "-m", message)
                logger.info(f"✅ Successfully committed: {message[:50]}...")
                return True

            except subprocess.CalledProcessError as e:
                error_msg = str(e.stderr)

                # Check if pre-commit hooks modified files
                if any(
                    phrase in error_msg
                    for phrase in [
                        "files were modified by this hook",
                        "File was modified by this hook",
                        "reformatted",
                        "fixed by hooks",
                        "would reformat",
                        "Fixing",
                    ]
                ):
                    logger.info(f"Pre-commit hooks modified files, retrying ({attempt}/{max_retries})...")
                    # Continue to next iteration - files will be added at start of next loop
                    continue

                # Check if there's nothing to commit (already committed)
                elif "nothing to commit" in error_msg or "working tree clean" in error_msg:
                    logger.info("Nothing to commit - working tree clean")
                    return True

                # Check if we're in the middle of a merge/rebase
                elif any(phrase in error_msg for phrase in ["cherry-pick", "merge", "rebase"]):
                    logger.error(f"Cannot commit - repository in special state: {error_msg}")
                    return False

                # For other errors, try a few more times in case it's transient
                elif attempt < 3:
                    logger.warning(f"Commit failed, retrying ({attempt}/{max_retries}): {error_msg}")
                    continue
                else:
                    # Unrecoverable error
                    logger.error(f"Failed to commit after {attempt} attempts: {error_msg}")
                    return False

        logger.error(f"Failed to commit after {max_retries} attempts - pre-commit hooks may be in infinite loop")
        return False

    def push(self, branch: Optional[str] = None, set_upstream: bool = True) -> bool:
        """Push commits to remote.

        Args:
            branch: Branch to push (default: current branch)
            set_upstream: Set upstream tracking branch

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.push()
        """
        try:
            if branch is None:
                branch = self.get_current_branch()

            args = ["push"]
            if set_upstream:
                args.extend(["-u", "origin", branch])
            else:
                args.extend(["origin", branch])

            self._run_git(*args)
            logger.info(f"Pushed branch: {branch}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push: {e.stderr}")
            return False

    def create_pull_request(self, title: str, body: str, base: str = "main") -> Optional[str]:
        """Create pull request using gh CLI.

        Args:
            title: PR title
            body: PR description
            base: Base branch (default: main)

        Returns:
            PR URL if successful, None otherwise

        Example:
            >>> git = GitManager()
            >>> pr_url = git.create_pull_request(
            ...     "Implement PRIORITY 3",
            ...     "## Summary\\n\\n- Feature 1\\n- Feature 2"
            ... )
            >>> print(f"Created PR: {pr_url}")
        """
        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--base",
                    base,
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            pr_url = result.stdout.strip()
            logger.info(f"Created PR: {pr_url}")
            return pr_url

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create PR: {e.stderr}")
            return None

        except FileNotFoundError:
            logger.error("gh CLI not found - cannot create PR")
            return None

    def is_clean(self) -> bool:
        """Check if working directory is clean.

        Returns:
            True if no uncommitted changes

        Example:
            >>> git = GitManager()
            >>> if git.is_clean():
            ...     print("Ready to start work!")
        """
        try:
            result = self._run_git("status", "--porcelain")
            clean = len(result.stdout.strip()) == 0
            logger.info(f"Working directory clean: {clean}")
            return clean

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check status: {e.stderr}")
            return False

    def get_status(self) -> str:
        """Get git status output.

        Returns:
            Git status output

        Example:
            >>> git = GitManager()
            >>> status = git.get_status()
            >>> print(status)
        """
        try:
            result = self._run_git("status")
            return result.stdout

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get status: {e.stderr}")
            return ""

    def has_remote(self) -> bool:
        """Check if repository has a remote configured.

        Returns:
            True if remote exists

        Example:
            >>> git = GitManager()
            >>> if git.has_remote():
            ...     print("Can push to remote")
        """
        try:
            result = self._run_git("remote", "-v")
            has_remote = len(result.stdout.strip()) > 0
            logger.info(f"Has remote: {has_remote}")
            return has_remote

        except subprocess.CalledProcessError:
            return False

    def checkout(self, branch: str) -> bool:
        """Checkout a branch.

        Args:
            branch: Branch name to checkout

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.checkout("main")
        """
        try:
            self._run_git("checkout", branch)
            logger.info(f"Checked out branch: {branch}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to checkout: {e.stderr}")
            return False

    def pull(self, branch: Optional[str] = None) -> bool:
        """Pull latest changes from remote.

        Args:
            branch: Branch to pull (default: current branch)

        Returns:
            True if successful

        Example:
            >>> git = GitManager()
            >>> git.pull("roadmap")
        """
        try:
            # Checkout branch if specified
            if branch and branch != self.get_current_branch():
                self.checkout(branch)

            self._run_git("pull")
            logger.info(f"Pulled latest changes")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull: {e.stderr}")
            return False
