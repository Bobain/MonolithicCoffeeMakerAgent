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
  --run-tests             Run the integrated unit tests.

Example (bash):
  python script_name.py -d ./my_project -u https://github.com/user/repo.git


How to run:
    Save the code as git_initializer.py (or any .py name).
To initialize a project:
    python git_initializer.py -d /path/to/your/project -u https://github.com/your_user/your_repo.git

Or for the current directory:
python git_initializer.py -u https://github.com/your_user/your_repo.git

To run tests:
python git_initializer.py --run-tests

You can also add -v or --verbose to get more detailed logging output from the script or the tests.

Key improvements in this version:
1) Class Structure (GitRepoInitializer): Organizes the logic into methods, making it more readable and maintainable. State (like project_path, repo_url) is managed as instance attributes.
2) Documentation:
    - Module-level docstring explaining the script's purpose, prerequisites, and usage.
    - Class and method docstrings.
    - Informative comments.
3) Error Handling & Logging:
    - Uses the logging module for INFO, WARNING, ERROR, DEBUG messages. Verbosity can be controlled.
    - _validate_prerequisites checks for git and directory existence early.
    - _run_command is more robust, captures stdout/stderr, and exits on critical errors from Git commands.
    - Specific checks (e.g., if .git or .gitignore already exists) provide informative messages.
4) unittest Suite:
    - TestGitRepoInitializer class with several test cases.
    - setUp and tearDown methods manage a temporary directory for each test, ensuring tests are isolated and don't affect your actual file system.
    - Tests cover: basic initialization, custom parameters, .gitignore handling (force/no-force), and a mock test for remote operations.
5) Modularity: The core logic is in the class, and the main() function handles argument parsing and instantiating/running the initializer.
6) Clarity: All user-facing messages and code comments are in English.
7) Git Branch Handling: Improved logic to correctly set or rename the primary branch, even if no commits exist yet.
8) .gitignore handling: Checks if .gitignore exists and only overwrites if --force-gitignore is used.

"""

import subprocess
import argparse
import os
import sys
import shutil # For checking if git is available and for test cleanup
import logging # For more structured logging/warnings

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

class GitRepoInitializer:
    """
    Handles the initialization of a Git repository.
    """
    def __init__(self, directory=".", repo_url=None,
                 commit_message="Initial commit with Python .gitignore",
                 branch_name="main", force_gitignore=False):
        self.project_path = os.path.abspath(directory)
        self.repo_url = repo_url
        self.commit_message = commit_message
        self.branch_name = branch_name
        self.force_gitignore = force_gitignore

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
                text=True
            )
            if process.stdout and not suppress_output:
                logger.debug(f"STDOUT:\n{process.stdout.strip()}")
            if process.stderr and not suppress_output: # Git often uses stderr for info
                logger.info(f"STDERR (or Git info):\n{process.stderr.strip()}")
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
            self._git_push()
        else:
            logger.warning("No repository URL provided. Skipping remote setup and push.")
            logger.info("To connect to a remote repository later, use:")
            logger.info(f"  git remote add origin YOUR_GITHUB_URL")
            logger.info(f"  git push -u origin {self.branch_name}")

        logger.info("Git repository initialization complete.")

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
            # Check current branch. This might fail if no commits yet.
            current_branch_process = self._run_command(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                check=False, suppress_output=True
            )
            current_branch = current_branch_process.stdout.strip() if current_branch_process.returncode == 0 else None

            if current_branch and current_branch != self.branch_name:
                logger.info(f"Renaming branch '{current_branch}' to '{self.branch_name}'.")
                self._run_command(["git", "branch", "-M", self.branch_name])
            elif not current_branch:
                # No commits yet, or freshly initialized. `git branch -M` will set the initial branch name.
                # Modern git init -b <branch> does this, but for compatibility:
                logger.info(f"Setting initial branch to '{self.branch_name}' (will take effect on first commit).")
                self._run_command(["git", "branch", "-M", self.branch_name])
            else: # current_branch == self.branch_name
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
                    f.write(DEFAULT_GITIGNORE_CONTENT.strip() + "\n") # Add a newline at the end
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
        # Check if there are changes to commit
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


def main():
    parser = argparse.ArgumentParser(
        description="Initializes a Git repository for an existing project, creates a Python .gitignore, and optionally pushes to GitHub.",
        formatter_class=argparse.RawTextHelpFormatter # To preserve help text formatting
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
        help="Name for the primary branch (default: main)."
    )
    parser.add_argument(
        "--force-gitignore",
        action="store_true",
        help="Overwrite .gitignore if it already exists."
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
        logging.getLogger().setLevel(logging.DEBUG) # Set root logger to DEBUG

    if args.run_tests:
        import unittest
        # Temporarily remove --run-tests from sys.argv so unittest doesn't try to parse it
        sys.argv = [arg for arg in sys.argv if arg != '--run-tests' and arg != '-v' and arg != '--verbose']
        unittest.main(module=__name__, exit=False) # Run tests from this file
        sys.exit(0)


    initializer = GitRepoInitializer(
        directory=args.directory,
        repo_url=args.repo_url,
        commit_message=args.commit_message,
        branch_name=args.branch_name,
        force_gitignore=args.force_gitignore
    )
    initializer.initialize_repository()

# --- Unit Tests ---
# Typically, these would be in a separate file like test_git_initializer.py
# For simplicity, they are included here.
# To run tests: python your_script_name.py --run-tests

if __name__ == "__main__": # This check is important if tests are in the same file
    import unittest
    import tempfile

    class TestGitRepoInitializer(unittest.TestCase):
        def setUp(self):
            # Create a temporary directory for each test
            self.test_dir = tempfile.mkdtemp()
            # Create a dummy file to be committed
            with open(os.path.join(self.test_dir, "sample.py"), "w") as f:
                f.write("print('hello')")

        def tearDown(self):
            # Remove the directory after the test
            shutil.rmtree(self.test_dir)

        def _path(self, *p):
            return os.path.join(self.test_dir, *p)

        def test_01_basic_initialization(self):
            initializer = GitRepoInitializer(directory=self.test_dir)
            initializer.initialize_repository()

            self.assertTrue(os.path.isdir(self._path(".git")))
            self.assertTrue(os.path.exists(self._path(".gitignore")))
            with open(self._path(".gitignore"), "r") as f:
                content = f.read()
                self.assertIn("__pycache__/", content)

            # Check if initial commit was made
            log = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"], cwd=self.test_dir, text=True
            ).strip()
            self.assertEqual(log, "Initial commit with Python .gitignore")

            # Check branch name
            branch_name = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.test_dir, text=True
            ).strip()
            self.assertEqual(branch_name, "main")


        def test_02_custom_branch_and_commit_message(self):
            custom_msg = "My first commit"
            custom_branch = "develop"
            initializer = GitRepoInitializer(
                directory=self.test_dir,
                commit_message=custom_msg,
                branch_name=custom_branch
            )
            initializer.initialize_repository()

            self.assertTrue(os.path.isdir(self._path(".git")))
            log = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"], cwd=self.test_dir, text=True
            ).strip()
            self.assertEqual(log, custom_msg)

            branch_name = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.test_dir, text=True
            ).strip()
            self.assertEqual(branch_name, custom_branch)

        def test_03_force_gitignore(self):
            # Create an existing .gitignore
            with open(self._path(".gitignore"), "w") as f:
                f.write("initial_dummy_content")

            initializer = GitRepoInitializer(directory=self.test_dir, force_gitignore=True)
            initializer.initialize_repository()

            with open(self._path(".gitignore"), "r") as f:
                content = f.read()
                self.assertIn("__pycache__/", content)
                self.assertNotIn("initial_dummy_content", content)

        def test_04_no_force_gitignore(self):
            dummy_content = "initial_dummy_content_not_overwritten"
            with open(self._path(".gitignore"), "w") as f:
                f.write(dummy_content)

            initializer = GitRepoInitializer(directory=self.test_dir, force_gitignore=False)
            initializer.initialize_repository() # Should not overwrite

            with open(self._path(".gitignore"), "r") as f:
                content = f.read()
                self.assertEqual(content.strip(), dummy_content)


        def test_05_with_remote_url(self):
            # This test only checks if the remote commands are attempted.
            # It doesn't actually push to a live remote.
            # We mock subprocess.run for the push command to avoid network activity.
            mock_repo_url = "https://github.com/testuser/testrepo.git"

            original_run_command = GitRepoInitializer._run_command
            commands_executed = []

            def mock_run_command_for_remote(self_obj, command, **kwargs):
                commands_executed.append(" ".join(command))
                # For 'git remote -v', simulate no origin initially
                if command == ["git", "remote", "-v"]:
                    return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")
                # For 'git push', simulate success
                if command[:2] == ["git", "push"]:
                    return subprocess.CompletedProcess(args=command, returncode=0, stdout="Mock push successful", stderr="")
                # For other commands, call the original
                return original_run_command(self_obj, command, **kwargs)

            GitRepoInitializer._run_command = mock_run_command_for_remote

            try:
                initializer = GitRepoInitializer(directory=self.test_dir, repo_url=mock_repo_url)
                initializer.initialize_repository()

                self.assertIn(f"git remote add origin {mock_repo_url}", commands_executed)
                self.assertIn(f"git push -u origin main", commands_executed) # Assumes default branch 'main'
            finally:
                GitRepoInitializer._run_command = original_run_command # Restore original

        def test_06_existing_git_repo(self):
            # Initialize git first
            subprocess.run(["git", "init"], cwd=self.test_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Old commit"], cwd=self.test_dir, check=True, capture_output=True)

            initializer = GitRepoInitializer(directory=self.test_dir, branch_name="feature_branch")
            initializer.initialize_repository()

            # Check that it didn't re-init, but did rename branch and add .gitignore
            self.assertTrue(os.path.exists(self._path(".gitignore")))
            branch_name = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.test_dir, text=True
            ).strip()
            self.assertEqual(branch_name, "feature_branch")

            # Check that the old commit is still there (meaning no re-init happened)
            log_count = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"], cwd=self.test_dir, text=True
            ).strip()
            # Expecting 2 commits: the "Old commit" and the one from the script
            self.assertEqual(log_count, "2")


    # This allows running the script directly or running tests
    if __name__ == "__main__" and '--run-tests' not in sys.argv : # Prevent running main() when tests are run via unittest.main
        main()
    elif __name__ == "__main__" and '--run-tests' in sys.argv:
        main() # main() will handle calling unittest.main()