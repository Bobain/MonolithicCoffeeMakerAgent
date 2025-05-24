#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# co-author : gemini 2.5 Pro Preview 05/06 in Google AI studio

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

IMPORTANT: This script expects to find template files for .gitignore and
the pre-push hook in a 'ressources' subdirectory relative to its own location.
Ensure these files are present if you move or distribute this script:
  - ressources/code/python/python_gitignore_template.txt
  - ressources/hooks/pre_push_hook_template.sh

Usage:
  python git_init.py [options]

Options:
  -d, --directory DIR     Path to the project directory (default: current dir).
  -u, --repo-url URL      URL of the GitHub repository. If not provided,
                          remote setup and push will be skipped.
  -m, --commit-message MSG Initial commit message (default: "Initial commit...").
  -b, --branch-name NAME  Name for the primary branch (default: "main").
  --force-gitignore       Overwrite .gitignore if it already exists.
  --protect-main-locally  Install a local pre-push hook to discourage
                          direct pushes to the main branch.
  --run-tests             Run the integrated unit tests (if present in this file).
  -v, --verbose           Enable verbose logging (DEBUG level).

Examples:
  python git_init.py -d ./my_project -u https://github.com/user/repo.git --protect-main-locally
  python3 ./git/git_init.py -u git@github.com:Bobain/MonolithicCoffeeMakerAgentTest.git --protect-main-locally
"""

import subprocess
import argparse
import os
import sys
import shutil
import logging
import stat # For making hook executable

# --- Script Configuration ---
# Determine the directory where this script is located.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define paths to template files relative to the script's directory.
GITIGNORE_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, "ressources", "code", "python", "python_gitignore_template.txt")
PRE_PUSH_HOOK_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, "ressources", "hooks", "pre_push_hook_template.sh")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


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
        self.branch_name = branch_name
        self.force_gitignore = force_gitignore
        self.protect_main_locally = protect_main_locally

        self._validate_prerequisites()
        self._load_template_contents() # Load templates during initialization

    def _load_template_contents(self):
        """Loads template content from files."""
        try:
            with open(GITIGNORE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                self.gitignore_content = f.read()
            logger.debug(f"Successfully loaded .gitignore template from: {GITIGNORE_TEMPLATE_PATH}")
        except FileNotFoundError:
            logger.error(f"FATAL: .gitignore template file not found at: {GITIGNORE_TEMPLATE_PATH}")
            logger.error("Please ensure the 'ressources' directory and its contents are alongside the script.")
            sys.exit(1)
        except IOError as e:
            logger.error(f"FATAL: Error reading .gitignore template file: {e}")
            sys.exit(1)

        try:
            with open(PRE_PUSH_HOOK_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                self.pre_push_hook_template_content = f.read()
            logger.debug(f"Successfully loaded pre-push hook template from: {PRE_PUSH_HOOK_TEMPLATE_PATH}")
        except FileNotFoundError:
            logger.error(f"FATAL: pre-push hook template file not found at: {PRE_PUSH_HOOK_TEMPLATE_PATH}")
            logger.error("Please ensure the 'ressources' directory and its contents are alongside the script.")
            sys.exit(1)
        except IOError as e:
            logger.error(f"FATAL: Error reading pre-push hook template file: {e}")
            sys.exit(1)


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
            # Pass the current environment to subprocess
            current_env = os.environ.copy()
            process = subprocess.run(
                command,
                cwd=self.project_path,
                check=check,
                capture_output=capture_output,
                text=True,
                env=current_env
            )
            if process.stdout and not suppress_output:
                logger.debug(f"STDOUT:\n{process.stdout.strip()}")
            if process.stderr and not suppress_output:
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
            self._git_push()
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
            if "github.com" in self.repo_url: # Basic check for GitHub URL
                 logger.info(f"  {self.repo_url.replace('.git', '')}/settings/branches")
            else:
                 logger.info(f"  Please find the branch protection settings on your Git host for {self.repo_url}")
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
        """Creates the .gitignore file using content from the loaded template."""
        gitignore_path = os.path.join(self.project_path, ".gitignore")
        if not os.path.exists(gitignore_path) or self.force_gitignore:
            action = "Overwriting" if os.path.exists(gitignore_path) else "Creating"
            logger.info(f"{action} {gitignore_path} with Python defaults from template: {GITIGNORE_TEMPLATE_PATH}")
            try:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(self.gitignore_content.strip() + "\n")
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
            # This can happen if .git is a file (worktree/submodule) or init failed very early
            logger.warning(f"Git hooks directory not found or not a directory: {hooks_dir}. Cannot install pre-push hook. ")
            return

        pre_push_hook_path = os.path.join(hooks_dir, "pre-push")
        hook_content = self.pre_push_hook_template_content.format(protected_branch_name=self.branch_name)

        logger.info(f"Installing pre-push hook to discourage direct pushes to '{self.branch_name}' from template: {PRE_PUSH_HOOK_TEMPLATE_PATH}")
        try:
            with open(pre_push_hook_path, "w", encoding="utf-8") as f:
                f.write(hook_content)
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
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""
IMPORTANT: This script expects to find template files for .gitignore and
the pre-push hook in a 'ressources' subdirectory relative to its own location.
Based on script location '{_SCRIPT_DIR}', it expects:
  - .gitignore template: '{GITIGNORE_TEMPLATE_PATH}'
  - pre-push hook template: '{PRE_PUSH_HOOK_TEMPLATE_PATH}'
"""
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
        help="Run the integrated unit tests for this script (if defined in this file)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)."
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.debug(f"Script directory: {_SCRIPT_DIR}")
    logger.debug(f"Using .gitignore template: {GITIGNORE_TEMPLATE_PATH}")
    logger.debug(f"Using pre-push hook template: {PRE_PUSH_HOOK_TEMPLATE_PATH}")


    if args.run_tests:
        # Check if tests are actually defined in this file or a linked module
        if 'TestGitRepoInitializer' in globals():
            import unittest
            # Remove script-specific args before passing to unittest
            test_argv = [sys.argv[0]] # Keep the script name
            for arg in sys.argv[1:]:
                 if arg not in ('--run-tests', '-v', '--verbose', '--protect-main-locally', '--force-gitignore') and \
                    not (arg.startswith('-d') or arg.startswith('--directory')) and \
                    not (arg.startswith('-u') or arg.startswith('--repo-url')) and \
                    not (arg.startswith('-m') or arg.startswith('--commit-message')) and \
                    not (arg.startswith('-b') or arg.startswith('--branch-name')):
                    test_argv.append(arg)
            sys.argv = test_argv
            unittest.main(module=__name__, exit=False)
        else:
            logger.info("No integrated unit tests found in this script.")
        sys.exit(0)

    try:
        initializer = GitRepoInitializer(
            directory=args.directory,
            repo_url=args.repo_url,
            commit_message=args.commit_message,
            branch_name=args.branch_name,
            force_gitignore=args.force_gitignore,
            protect_main_locally=args.protect_main_locally
        )
        initializer.initialize_repository()
    except SystemExit: # Catch sys.exit calls from within the class
        raise
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during script execution: {e}", exc_info=True)
        sys.exit(1)


# --- Unit Tests ---
# To run these, you'd need the 'ressources' directory set up correctly relative
# to where this script is, or mock the file loading process.
# For simplicity, the tests here assume the 'ressources' dir IS available.
# If not, the _load_template_contents in setUp would fail, or you'd mock it.

if __name__ == "__main__":
    # Check if --run-tests is NOT in sys.argv to prevent running main() when tests are run
    if '--run-tests' not in sys.argv:
        main()
    else: # --run-tests is present
        # This block is tricky if tests are defined below and main() is also called.
        # The main() function already has logic for --run-tests.
        # The typical structure is `if __name__ == "__main__": main()` and tests run via a test runner.
        # For integrated tests invoked by --run-tests, main() handles it.
        # This `else` block here is somewhat redundant given main()'s --run-tests logic,
        # but let's ensure main() is called if --run-tests is present.
        main()

# Example of how you might define integrated tests (optional)
# Needs `import unittest` and `import unittest.mock` if used
#
# class TestGitRepoInitializer(unittest.TestCase):
#     def setUp(self):
#         # Ensure SCRIPT_DIR, GITIGNORE_TEMPLATE_PATH, PRE_PUSH_HOOK_TEMPLATE_PATH
#         # are correctly set up for the test environment OR mock their loading.
#         # Create a temporary directory for each test
#         self.test_dir_parent = tempfile.mkdtemp()
#         self.test_dir = os.path.join(self.test_dir_parent, "test_project")
#         os.makedirs(self.test_dir)
#         with open(os.path.join(self.test_dir, "sample.py"), "w") as f:
#             f.write("print('hello')")
#
#         # MOCKING EXAMPLE: If 'ressources' isn't easily available for tests:
#         self.mock_gitignore_content = "__pycache__/\n.env\n"
#         self.mock_hook_template_content = "#!/bin/sh\necho 'Mock hook for {protected_branch_name}'\nexit 0"
#
#         # Patch open for the GitRepoInitializer instance or globally for the test
#         # This is a simplified example; robust mocking might be more involved.
#         self.patcher_open = unittest.mock.patch('__main__.open') # Or specific module path
#         self.mock_open = self.patcher_open.start()
#
#         def side_effect_open(file_path, *args, **kwargs):
#             if file_path == GITIGNORE_TEMPLATE_PATH:
#                 return unittest.mock.mock_open(read_data=self.mock_gitignore_content).return_value
#             elif file_path == PRE_PUSH_HOOK_TEMPLATE_PATH:
#                 return unittest.mock.mock_open(read_data=self.mock_hook_template_content).return_value
#             # Fallback for other file opens if necessary, or raise an error
#             return unittest.mock.MagicMock(spec=open)(file_path, *args, **kwargs) # Call original for other files
#
#         self.mock_open.side_effect = side_effect_open
#
#     def tearDown(self):
#         # if hasattr(self, 'patcher_open'): self.patcher_open.stop()
#         shutil.rmtree(self.test_dir_parent)
#
#     # ... your test methods ...
#     def test_basic_initialization(self):
#         initializer = GitRepoInitializer(directory=self.test_dir)
#         initializer.initialize_repository()
#         self.assertTrue(os.path.isdir(os.path.join(self.test_dir, ".git")))
#         # ... more assertions