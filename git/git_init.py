#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git Project Initializer Script

This script automates the process of initializing a Git repository for an existing
project directory. It performs the following actions:

1.  Navigates to the specified project directory (defaults to current directory).
2.  Initializes a Git repository (`git init`) if one doesn't already exist.
3.  Renames/sets the default branch to a specified name (default: "main").
4.  Creates a comprehensive .gitignore file tailored for Python projects.
    It will not overwrite an existing .gitignore unless --force-gitignore is used.
5.  Adds all files (respecting .gitignore) to the staging area (`git add .`).
6.  Creates an initial commit with a customizable message.
7.  If a GitHub repository URL is provided:
    a. Adds the GitHub repository as a remote named "origin".
    b. Pushes the initial commit and the main branch to the remote repository.
8.  Optionally, installs a local `pre-push` Git hook to discourage direct
    pushes to the main branch after initial setup.

Prerequisites:
- Python 3.6+
- Git installed and accessible in your system's PATH.

Usage:
  python script_name.py [options]

Options:
  -d, --directory DIR     Path to the project directory (default: current dir).
  -u, --repo-url URL      URL of the GitHub repository. If not provided,
                          remote setup and push will be skipped.
  -m, --commit-message MSG Initial commit message (default: "Initial commit...").
  -b, --branch-name NAME  Name for the primary branch (default: "main").
  --force-gitignore       Overwrite .gitignore if it already exists.
  --protect-main-locally  Install a local pre-push hook to discourage
                          direct pushes to the main branch.
  --run-tests             Run the integrated unit tests.
  -v, --verbose           Enable verbose logging (DEBUG level).

Example:
  python script_name.py -d ./my_project -u https://github.com/user/repo.git --protect-main-locally
  python ./git/git_init.py -u git@github.com:Bobain/again-some-shit.git

  Key Changes:
PRE_PUSH_HOOK_CONTENT_TEMPLATE:
A new constant holding the shell script for the pre-push hook.
It's a template that will be formatted with the actual protected_branch_name.
The hook checks if the push is targeting the protected branch and exits with 1 (failure) if so, printing a helpful message.
It allows deleting the remote branch.
It explicitly mentions git push --no-verify as a way to bypass the hook.
GitRepoInitializer Class:
__init__: Added protect_main_locally=False argument and stores it.
initialize_repository():
Calls _install_pre_push_hook() after the initial _git_push() if self.protect_main_locally is true. This ensures the very first push (setting up the repo) is allowed.
Prints a prominent message advising the user to set up server-side branch protection rules on GitHub, including a direct link to the settings page.
_install_pre_push_hook() method:
Creates the .git/hooks directory if it doesn't exist (though git init usually does).
Writes the formatted hook content to .git/hooks/pre-push.
Uses os.chmod and stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH to make the hook file executable, which is crucial for Git to run it.
Includes error handling for file operations.
main() function and argparse:
Added --protect-main-locally command-line argument.
Passed args.protect_main_locally to the GitRepoInitializer.
Logging for _run_command:
Slightly adjusted logging for stderr. If stderr contains "hint:", it's logged as DEBUG because Git often provides useful, non-error hints there. Otherwise, INFO. This makes the default output cleaner.
Unit Tests (TestGitRepoInitializer):
test_07_install_pre_push_hook:
Verifies that the pre-push hook file is created.
Checks if it's executable (os.access(hook_path, os.X_OK)).
Reads the hook content and asserts that it contains the correct protected branch name and a marker string.
setUp and _run_git_command: Modified to use an environment where GIT_CONFIG_GLOBAL and GIT_CONFIG_SYSTEM are nullified. This is important to make tests more predictable, especially regarding init.defaultBranch, as user's global Git config can otherwise interfere.
test_08_stderr_hint_logging: A new test to check the refined stderr logging for "hint:" messages.

"""

import subprocess
import argparse
import os
import sys
import shutil
import logging
import stat # For making hook executable

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_GITIGNORE_CONTENT = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# PEP 582; __pypackages__
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE / Editor specific
.idea/
# .vscode/ # Uncomment if you never want to version VSCode settings
*.project
*.pydevproject
.sublime-workspace
.sublime-project

# OS generated files
.DS_Store
Thumbs.db
"""

PRE_PUSH_HOOK_CONTENT_TEMPLATE = """#!/bin/sh
#
# This hook is managed by git_init.py.
# It prevents direct pushes to the '{protected_branch_name}' branch.
# To bypass this hook for a specific push (e.g., an emergency hotfix), use:
#   git push --no-verify <remote> <branch>
#
# It's highly recommended to also set up branch protection rules
# on your remote repository (e.g., GitHub, GitLab) for true enforcement.

REMOTE="$1"
URL="$2"

PROTECTED_BRANCH="{protected_branch_name}"
BRANCH_REF="refs/heads/$PROTECTED_BRANCH"

while read local_ref local_sha remote_ref remote_sha; do
    if [ "$remote_ref" = "$BRANCH_REF" ]; then
        # Allow deleting the remote branch
        if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
            exit 0
        fi

        echo "--------------------------------------------------------------------"
        echo "WARNING: Direct push to the protected branch '$PROTECTED_BRANCH' is discouraged."
        echo "Please use a feature branch and a Pull/Merge Request workflow."
        echo ""
        echo "If this is an emergency and you must push directly, you can bypass this hook with:"
        echo "  git push --no-verify $REMOTE $PROTECTED_BRANCH"
        echo "--------------------------------------------------------------------"
        exit 1 # Block the push
    fi
done

exit 0 # Allow other pushes
"""

class GitRepoInitializer:
    """
    Handles the initialization of a Git repository.
    """
    def __init__(self, directory=".", repo_url=None,
                 commit_message="Initial commit with Python .gitignore",
                 branch_name="main", force_gitignore=False,
                 protect_main_locally=False):
        self.project_path = os.path.abspath(directory)
        self.repo_url = repo_url
        self.commit_message = commit_message
        self.branch_name = branch_name # This is the branch we might protect
        self.force_gitignore = force_gitignore
        self.protect_main_locally = protect_main_locally

        self._validate_prerequisites()

    def _validate_prerequisites(self):
        """Checks for Git and valid project directory."""
        if not shutil.which("git"):
            logger.error("Git command not found. Please install Git and ensure it's in your PATH.")
            sys.exit(1)
        if not os.path.isdir(self.project_path):
            logger.error(f"Project directory not found: {self.project_path}")
            sys.exit(1)

    def _run_command(self, command, check=True, capture_output=True, suppress_output=False):
        """Executes a shell command and handles output/errors."""
        if not suppress_output:
            logger.info(f"Executing: {' '.join(command)} in {self.project_path}")
        try:
            process = subprocess.run(
                command,
                cwd=self.project_path,
                check=check,
                capture_output=capture_output,
                text=True,
                env=os.environ # Ensure git commands get the user's environment
            )
            if process.stdout and not suppress_output:
                logger.debug(f"STDOUT:\n{process.stdout.strip()}")
            if process.stderr and not suppress_output:
                # Git often uses stderr for info, so log it as INFO unless it's a clear error.
                # If check=True and it's an error, CalledProcessError will be raised.
                log_level = logging.DEBUG if "hint:" in process.stderr.lower() else logging.INFO
                logger.log(log_level, f"STDERR (or Git info):\n{process.stderr.strip()}")
            return process
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing command: {' '.join(command)}")
            logger.error(f"Return code: {e.returncode}")
            if e.stdout:
                logger.error(f"STDOUT:\n{e.stdout.strip()}")
            if e.stderr:
                logger.error(f"STDERR:\n{e.stderr.strip()}")
            sys.exit(1)
        except FileNotFoundError:
            logger.error(f"Error: The command '{command[0]}' was not found (part of Git interaction).")
            sys.exit(1)

    def initialize_repository(self):
        """Main method to orchestrate the Git initialization process."""
        logger.info(f"Starting Git initialization in: {self.project_path}")

        self._git_init()
        self._set_branch_name()
        self._create_gitignore()
        self._git_add()
        self._git_commit()

        if self.repo_url:
            self._setup_remote()
            self._git_push() # Initial push happens *before* hook installation
                            # so this first push to main is allowed.
        else:
            logger.warning("No repository URL provided. Skipping remote setup and push.")
            logger.info("To connect to a remote repository later, use:")
            logger.info(f"  git remote add origin YOUR_GITHUB_URL")
            logger.info(f"  git push -u origin {self.branch_name}")

        if self.protect_main_locally:
            self._install_pre_push_hook()

        logger.info("Git repository initialization complete.")
        if self.protect_main_locally and self.repo_url:
            logger.info("--------------------------------------------------------------------")
            logger.info("IMPORTANT: A local pre-push hook has been installed to discourage")
            logger.info(f"direct pushes to '{self.branch_name}'. For true branch protection,")
            logger.info(f"please configure branch protection rules on your GitHub repository:")
            logger.info(f"  {self.repo_url.replace('.git', '')}/settings/branches")
            logger.info("--------------------------------------------------------------------")
        elif self.protect_main_locally:
             logger.info("--------------------------------------------------------------------")
             logger.info("IMPORTANT: A local pre-push hook has been installed to discourage")
             logger.info(f"direct pushes to '{self.branch_name}'.")
             logger.info("Consider setting up server-side branch protection if you connect to a remote.")
             logger.info("--------------------------------------------------------------------")


    def _git_init(self):
        """Initializes a Git repository if one doesn't exist."""
        git_dir = os.path.join(self.project_path, ".git")
        if not os.path.isdir(git_dir):
            self._run_command(["git", "init"])
        else:
            logger.info(".git directory already exists. Skipping 'git init'.")

    def _set_branch_name(self):
        """Sets or renames the main branch."""
        try:
            current_branch_process = self._run_command(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                check=False, suppress_output=True
            )
            current_branch = current_branch_process.stdout.strip() if current_branch_process.returncode == 0 else None

            if current_branch and current_branch != self.branch_name:
                logger.info(f"Renaming branch '{current_branch}' to '{self.branch_name}'.")
                self._run_command(["git", "branch", "-M", self.branch_name])
            elif not current_branch:
                logger.info(f"Setting initial branch to '{self.branch_name}' (will take effect on first commit).")
                self._run_command(["git", "branch", "-M", self.branch_name])
            else:
                logger.info(f"Branch is already named '{self.branch_name}'.")
        except Exception as e:
            logger.warning(f"Could not reliably determine or set branch name: {e}. "
                           f"Proceeding with Git's default or current branch configuration.")

    def _create_gitignore(self):
        """Creates the .gitignore file."""
        gitignore_path = os.path.join(self.project_path, ".gitignore")
        if not os.path.exists(gitignore_path) or self.force_gitignore:
            action = "Overwriting" if os.path.exists(gitignore_path) else "Creating"
            logger.info(f"{action} {gitignore_path} with Python defaults.")
            try:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(DEFAULT_GITIGNORE_CONTENT.strip() + "\n")
            except IOError as e:
                logger.error(f"Failed to write .gitignore file: {e}")
                sys.exit(1)
        else:
            logger.info(f"{gitignore_path} already exists. Use --force-gitignore to overwrite.")

    def _git_add(self):
        """Adds all files to the staging area."""
        self._run_command(["git", "add", "."])

    def _git_commit(self):
        """Creates the initial commit."""
        status_output = self._run_command(["git", "status", "--porcelain"], check=False, suppress_output=True).stdout
        if not status_output.strip():
            logger.warning("No changes to commit. Initial commit might already exist or .gitignore covers all files.")
        else:
            self._run_command(["git", "commit", "-m", self.commit_message])

    def _setup_remote(self):
        """Adds or updates the 'origin' remote."""
        remotes_process = self._run_command(["git", "remote", "-v"], check=False, suppress_output=True)
        if "origin" in remotes_process.stdout:
            logger.info(f"Remote 'origin' already exists. Setting URL to: {self.repo_url}")
            self._run_command(["git", "remote", "set-url", "origin", self.repo_url])
        else:
            logger.info(f"Adding remote 'origin' with URL: {self.repo_url}")
            self._run_command(["git", "remote", "add", "origin", self.repo_url])

    def _git_push(self):
        """Pushes the main branch to the 'origin' remote."""
        logger.info(f"Pushing branch '{self.branch_name}' to 'origin'.")
        self._run_command(["git", "push", "-u", "origin", self.branch_name])
        logger.info("Push successful!")

    def _install_pre_push_hook(self):
        """Installs a local pre-push hook to protect the main branch."""
        hooks_dir = os.path.join(self.project_path, ".git", "hooks")
        if not os.path.isdir(hooks_dir):
            logger.warning(f"Git hooks directory not found: {hooks_dir}. Cannot install pre-push hook. "
                           "This might happen if '.git' is a file (e.g., for submodules or worktrees) "
                           "or if git init failed silently.")
            return

        pre_push_hook_path = os.path.join(hooks_dir, "pre-push")
        hook_content = PRE_PUSH_HOOK_CONTENT_TEMPLATE.format(protected_branch_name=self.branch_name)

        logger.info(f"Installing pre-push hook to discourage direct pushes to '{self.branch_name}'.")
        try:
            with open(pre_push_hook_path, "w", encoding="utf-8") as f:
                f.write(hook_content)
            # Make the hook executable
            current_permissions = os.stat(pre_push_hook_path).st_mode
            os.chmod(
                pre_push_hook_path,
                current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH # Add execute permissions
            )
            logger.info(f"Pre-push hook installed at: {pre_push_hook_path}")
        except IOError as e:
            logger.error(f"Failed to write or set permissions for pre-push hook: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while installing pre-push hook: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Initializes a Git repository for an existing project, creates a Python .gitignore, and optionally pushes to GitHub.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Path to the project directory (default: current directory)."
    )
    parser.add_argument(
        "-u", "--repo-url",
        help="URL of the GitHub repository (e.g., https://github.com/user/repo.git).\n"
             "If not provided, remote setup and push will be skipped."
    )
    parser.add_argument(
        "-m", "--commit-message",
        default="Initial commit with Python .gitignore",
        help="Message for the initial commit."
    )
    parser.add_argument(
        "-b", "--branch-name",
        default="main",
        help="Name for the primary branch (default: main). This will also be the branch protected by the local hook if enabled."
    )
    parser.add_argument(
        "--force-gitignore",
        action="store_true",
        help="Overwrite .gitignore if it already exists."
    )
    parser.add_argument(
        "--protect-main-locally",
        action="store_true",
        help="Install a local pre-push hook to discourage direct pushes to the main branch (specified by --branch-name)."
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run the integrated unit tests for this script."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)."
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.run_tests:
        import unittest
        sys.argv = [arg for arg in sys.argv if arg not in ('--run-tests', '-v', '--verbose', '--protect-main-locally')]
        unittest.main(module=__name__, exit=False)
        sys.exit(0)

    initializer = GitRepoInitializer(
        directory=args.directory,
        repo_url=args.repo_url,
        commit_message=args.commit_message,
        branch_name=args.branch_name,
        force_gitignore=args.force_gitignore,
        protect_main_locally=args.protect_main_locally
    )
    initializer.initialize_repository()

# --- Unit Tests ---
if __name__ == "__main__":
    import unittest
    import tempfile

    class TestGitRepoInitializer(unittest.TestCase):
        def setUp(self):
            self.test_dir_parent = tempfile.mkdtemp() # Parent for multiple test dirs if needed
            self.test_dir = os.path.join(self.test_dir_parent, "test_project")
            os.makedirs(self.test_dir)
            with open(os.path.join(self.test_dir, "sample.py"), "w") as f:
                f.write("print('hello')")
            # Set GIT_CONFIG_GLOBAL and GIT_CONFIG_SYSTEM to /dev/null to avoid interference
            # from user's global git config, especially init.defaultBranch.
            self.git_env = os.environ.copy()
            self.git_env['GIT_CONFIG_GLOBAL'] = os.devnull
            self.git_env['GIT_CONFIG_SYSTEM'] = os.devnull


        def tearDown(self):
            shutil.rmtree(self.test_dir_parent)

        def _path(self, *p):
            return os.path.join(self.test_dir, *p)

        def _run_git_command(self, command_list):
            """Helper to run git commands in the test directory for verification."""
            return subprocess.check_output(command_list, cwd=self.test_dir, text=True, env=self.git_env).strip()


        def test_01_basic_initialization(self):
            initializer = GitRepoInitializer(directory=self.test_dir)
            # Mock _run_command for GitRepoInitializer instance to inject env
            original_run_command = initializer._run_command
            def mocked_run_command_with_env(command, **kwargs):
                kwargs['env'] = self.git_env # Add env to subprocess call
                # We need to call the actual subprocess.run here, not the original method which might be bound
                # This is a bit tricky, ideally _run_command would accept an env directly.
                # For now, let's just ensure the git_env is used when we manually check post-init.
                return original_run_command(command, **kwargs)
            # initializer._run_command = mocked_run_command_with_env # This approach is complex for instance methods

            initializer.initialize_repository() # This will use the script's global os.environ

            self.assertTrue(os.path.isdir(self._path(".git")))
            self.assertTrue(os.path.exists(self._path(".gitignore")))
            with open(self._path(".gitignore"), "r") as f:
                content = f.read()
                self.assertIn("__pycache__/", content)

            log = self._run_git_command(["git", "log", "-1", "--pretty=%B"])
            self.assertEqual(log, "Initial commit with Python .gitignore")

            branch_name = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            # Git's default can be 'master' if user hasn't set init.defaultBranch=main globally
            # The script tries to set it to 'main' (or the specified branch_name)
            self.assertEqual(branch_name, "main")


        def test_07_install_pre_push_hook(self):
            branch_to_protect = "develop"
            initializer = GitRepoInitializer(
                directory=self.test_dir,
                branch_name=branch_to_protect, # Protect the specified branch name
                protect_main_locally=True
            )
            initializer.initialize_repository()

            hook_path = self._path(".git", "hooks", "pre-push")
            self.assertTrue(os.path.exists(hook_path))
            self.assertTrue(os.access(hook_path, os.X_OK)) # Check if executable

            with open(hook_path, "r", encoding="utf-8") as f:
                hook_content = f.read()
            self.assertIn(f"PROTECTED_BRANCH=\"{branch_to_protect}\"", hook_content)
            self.assertIn("managed by git_init.py", hook_content)

        def test_08_stderr_hint_logging(self):
            # Test how 'hint:' messages from git are logged
            with self.assertLogs(logger, level='DEBUG') as cm: # Expect DEBUG for hints
                initializer = GitRepoInitializer(directory=self.test_dir)
                # Simulate a git command that produces a "hint:" on stderr
                mock_process = subprocess.CompletedProcess(
                    args=["git", "dummy"],
                    returncode=0,
                    stdout="some output",
                    stderr="hint: this is a helpful git hint."
                )
                with unittest.mock.patch('subprocess.run', return_value=mock_process):
                    initializer._run_command(["git", "dummy"], suppress_output=False) # Ensure suppress_output is False

            self.assertTrue(any("hint: this is a helpful git hint" in record.message for record in cm.records))
            # Check that it was logged as DEBUG (or INFO, depending on exact logic if 'hint:' isn't the only factor)
            # Our current logic: DEBUG if "hint:" in stderr.lower() else INFO
            self.assertTrue(any(record.levelname == 'DEBUG' and "hint:" in record.message for record in cm.records))


    # This allows running the script directly or running tests
    if __name__ == "__main__" and '--run-tests' not in sys.argv :
        main()
    elif __name__ == "__main__" and '--run-tests' in sys.argv:
        # Need to import unittest.mock for some tests if run this way
        # For simplicity when running tests, it's often better to use `python -m unittest script_name.py`
        # or a test runner that handles imports.
        try:
            import unittest.mock
        except ImportError:
            print("Please install 'mock' for Python < 3.3 or ensure unittest.mock is available to run tests this way.")
            sys.exit(1)
        main() # main() will handle calling unittest.main()