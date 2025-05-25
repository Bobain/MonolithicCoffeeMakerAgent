#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# co-author : gemini 2.5 Pro Preview 05/06 in Google AI studio

"""
Git Project Initializer Script

This script automates the process of initializing a Git repository for an existing
project directory. By default, it also installs Git hooks to improve workflow.

Key Features:
1.  Navigates to the specified project directory (defaults to current directory).
2.  Initializes a Git repository (`git init`) if one doesn't already exist.
3.  Sets `push.autoSetupRemote = true` locally for the new repository
    to simplify pushing new branches (requires Git >= 2.37.0).
4.  Renames/sets the default branch to a specified name (default: "main").
5.  Creates a comprehensive .gitignore file tailored for Python projects.
    It will not overwrite an existing .gitignore unless --force-gitignore is used.
6.  Adds all files (respecting .gitignore) to the staging area (`git add .`).
7.  Creates an initial commit with a customizable message.
8.  If a GitHub repository URL is provided:
    a. Adds the GitHub repository as a remote named "origin".
    b. Pushes the initial commit and the main branch to the remote repository.
9.  Installs a local `pre-push` hook to discourage direct pushes to the
    main branch (default behavior).


Prerequisites:
- Python 3.6+
- Git installed and accessible in your system's PATH (version >= 2.37.0 recommended
  for the `push.autoSetupRemote` feature).

IMPORTANT: This script expects to find template files in a 'ressources'
subdirectory relative to its own location:
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
                          This is the branch the pre-push hook will aim to protect.
  --force-gitignore       Overwrite .gitignore if it already exists.
  --no-protect-main-push  Disable installing the pre-push hook that discourages
                           pushing directly to the main branch.
  --no-auto-setup-remote  Disable automatically setting 'push.autoSetupRemote = true'
                          for the local repository.
  --run-tests             Run the integrated unit tests (if present in this file).
  -v, --verbose           Enable verbose logging (DEBUG level).

Examples:
  python init_scripts/git/git_init.py -d ./my_project -u git@github.com:Bobain/MonolithicCoffeeMakerAgent.git
  python init_scripts/git/git_init.py --no-protect-main-push
"""

import argparse
import logging
import os
import shutil
import stat  # For making hook executable
import subprocess
import sys

# --- Script Configuration ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GITIGNORE_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, "ressources", "code", "python", "python_gitignore_template.txt")
PRE_PUSH_HOOK_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, "ressources", "hooks", "pre_push_hook_template.sh")
# PRE_COMMIT_HOOK_TEMPLATE_PATH is removed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class GitRepoInitializer:
    """
    Handles the initialization of a Git repository.
    """

    def __init__(
        self,
        directory=".",
        repo_url=None,
        commit_message="Initial commit with Python .gitignore",
        branch_name="main",
        force_gitignore=False,
        protect_main_push=True,  # Default True for the pre-push hook
        auto_setup_remote=True,
    ):
        self.project_path = os.path.abspath(directory)
        self.repo_url = repo_url
        self.commit_message = commit_message
        self.branch_name = branch_name  # This is the branch to protect
        self.force_gitignore = force_gitignore
        self.protect_main_push = protect_main_push
        self.auto_setup_remote = auto_setup_remote

        self._validate_prerequisites()
        self._load_template_contents()

    def _load_template_contents(self):
        """Loads template content from files."""
        try:
            with open(GITIGNORE_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                self.gitignore_content = f.read()
            logger.debug(f"Successfully loaded .gitignore template from: {GITIGNORE_TEMPLATE_PATH}")
        except FileNotFoundError:
            logger.error(f"FATAL: .gitignore template file not found at: {GITIGNORE_TEMPLATE_PATH}")
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
            sys.exit(1)
        except IOError as e:
            logger.error(f"FATAL: Error reading pre-push hook template file: {e}")
            sys.exit(1)
        # Removed loading for PRE_COMMIT_HOOK_TEMPLATE_PATH

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
            current_env = os.environ.copy()
            process = subprocess.run(
                command, cwd=self.project_path, check=check, capture_output=capture_output, text=True, env=current_env
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

    def _configure_auto_setup_remote(self):
        """Sets git config push.autoSetupRemote to true for the local repository."""
        if self.auto_setup_remote:
            try:
                version_process = self._run_command(["git", "--version"], suppress_output=True, check=True)
                version_str = version_process.stdout.strip().split(" ")[2]
                parts = version_str.split(".")
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                if not (major > 2 or (major == 2 and minor >= 37)):
                    logger.warning(
                        f"Git version {version_str} is older than 2.37.0. "
                        "Cannot set 'push.autoSetupRemote'. Please update Git or use 'git push -u' for new branches."
                    )
                    return
            except Exception as e:
                logger.warning(
                    f"Could not determine Git version for 'push.autoSetupRemote' compatibility: {e}. Skipping."
                )
                return

            logger.info("Setting local git config 'push.autoSetupRemote = true'.")
            self._run_command(["git", "config", "push.autoSetupRemote", "true"])
        else:
            logger.info("Skipping setup of 'push.autoSetupRemote'.")

    def _install_git_hook(self, hook_name, template_content, template_path_for_logging):
        """Installs a given Git hook from template content."""
        hooks_dir = os.path.join(self.project_path, ".git", "hooks")
        if not os.path.isdir(hooks_dir):
            logger.warning(
                f"Git hooks directory not found or not a directory: {hooks_dir}. Cannot install {hook_name} hook."
            )
            return

        hook_file_path = os.path.join(hooks_dir, hook_name)
        content_to_write = template_content.format(protected_branch_name=self.branch_name)

        logger.info(
            f"Installing {hook_name} hook to discourage direct actions on '{self.branch_name}' "
            f"from template: {template_path_for_logging}"
        )
        try:
            with open(hook_file_path, "w", encoding="utf-8") as f:
                f.write(content_to_write)
            current_permissions = os.stat(hook_file_path).st_mode
            os.chmod(
                hook_file_path,
                current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
            )
            logger.info(f"{hook_name} hook installed at: {hook_file_path}")
        except IOError as e:
            logger.error(f"Failed to write or set permissions for {hook_name} hook: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while installing {hook_name} hook: {e}")

    def initialize_repository(self):
        """Main method to orchestrate the Git initialization process."""
        logger.info(f"Starting Git initialization in: {self.project_path}")

        self._git_init()
        self._configure_auto_setup_remote()
        self._set_branch_name()  # Ensure branch_name is set before hooks use it
        self._create_gitignore()

        if self.protect_main_push:
            self._install_git_hook("pre-push", self.pre_push_hook_template_content, PRE_PUSH_HOOK_TEMPLATE_PATH)
        # Removed call to install pre-commit hook

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
        if self.protect_main_push:  # Only log about pre-push hook if it was installed
            logger.info("--------------------------------------------------------------------")
            logger.info(f"IMPORTANT: A local pre-push hook is installed to discourage pushes to '{self.branch_name}'.")
            if self.repo_url:
                logger.info(f"For true branch protection, configure rules on your GitHub repository:")
                if "github.com" in self.repo_url:
                    logger.info(f"  {self.repo_url.replace('.git', '')}/settings/branches")
                else:
                    logger.info(f"  Please find branch protection settings on your Git host for {self.repo_url}")
            else:
                logger.info("Consider server-side branch protection if you connect to a remote later.")
            logger.info("--------------------------------------------------------------------")

    def _git_init(self):
        git_dir = os.path.join(self.project_path, ".git")
        if not os.path.isdir(git_dir):
            self._run_command(["git", "init"])
        else:
            logger.info(".git directory already exists. Skipping 'git init'.")

    def _set_branch_name(self):
        try:
            current_branch_process = self._run_command(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False, suppress_output=True
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
            logger.warning(
                f"Could not reliably determine or set branch name: {e}. "
                f"Proceeding with Git's default or current branch configuration."
            )

    def _create_gitignore(self):
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
        self._run_command(["git", "add", "."])

    def _git_commit(self):
        status_output = self._run_command(["git", "status", "--porcelain"], check=False, suppress_output=True).stdout
        if not status_output.strip():
            logger.warning("No changes to commit. Initial commit might already exist or .gitignore covers all files.")
        else:
            self._run_command(["git", "commit", "-m", self.commit_message])

    def _setup_remote(self):
        remotes_process = self._run_command(["git", "remote", "-v"], check=False, suppress_output=True)
        if "origin" in remotes_process.stdout:
            logger.info(f"Remote 'origin' already exists. Setting URL to: {self.repo_url}")
            self._run_command(["git", "remote", "set-url", "origin", self.repo_url])
        else:
            logger.info(f"Adding remote 'origin' with URL: {self.repo_url}")
            self._run_command(["git", "remote", "add", "origin", self.repo_url])

    def _git_push(self):
        logger.info(f"Pushing branch '{self.branch_name}' to 'origin'.")
        self._run_command(["git", "push", "-u", "origin", self.branch_name])
        logger.info("Push successful!")


def main():
    parser = argparse.ArgumentParser(
        description="Initializes a Git repository, creates .gitignore, and sets up helpful Git hooks.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""
IMPORTANT: This script expects template files in a 'ressources' subdirectory
relative to its own location ('{_SCRIPT_DIR}'):
  - .gitignore: '{GITIGNORE_TEMPLATE_PATH}'
  - pre-push hook: '{PRE_PUSH_HOOK_TEMPLATE_PATH}'
""",  # Removed pre-commit hook from epilog
    )
    parser.add_argument(
        "-d", "--directory", default=".", help="Path to the project directory (default: current directory)."
    )
    parser.add_argument(
        "-u",
        "--repo-url",
        help="URL of the GitHub repository. If not provided, remote setup and push will be skipped.",
    )
    parser.add_argument(
        "-m",
        "--commit-message",
        default="Initial commit with Python .gitignore",
        help="Message for the initial commit.",
    )
    parser.add_argument(
        "-b",
        "--branch-name",
        default="main",
        help="Name for the primary branch (default: main). This is the branch the pre-push hook will aim to protect.",
    )
    parser.add_argument("--force-gitignore", action="store_true", help="Overwrite .gitignore if it already exists.")
    # Removed --no-protect-main-commit argument
    parser.add_argument(
        "--no-protect-main-push",
        action="store_false",
        dest="protect_main_push",
        help="Disable installing the pre-push hook that discourages pushing directly to the main branch.",
    )
    parser.add_argument(
        "--no-auto-setup-remote",
        action="store_false",
        dest="auto_setup_remote",
        help="Disable automatically setting 'push.autoSetupRemote = true' for the local repository.",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run the integrated unit tests for this script (if defined in this file).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level).")
    parser.set_defaults(protect_main_push=True, auto_setup_remote=True)  # Removed protect_main_commit from defaults

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    logger.debug(f"Script directory: {_SCRIPT_DIR}")
    logger.debug(f"Using .gitignore template: {GITIGNORE_TEMPLATE_PATH}")
    logger.debug(f"Using pre-push hook template: {PRE_PUSH_HOOK_TEMPLATE_PATH}")
    # Removed logging for PRE_COMMIT_HOOK_TEMPLATE_PATH

    if args.run_tests:
        if "TestGitRepoInitializer" in globals():
            import unittest

            test_argv = [sys.argv[0]]
            script_args_to_filter = [
                "--run-tests",
                "-v",
                "--verbose",
                "--no-protect-main-push",
                "--no-auto-setup-remote",  # Removed --no-protect-main-commit
                "--force-gitignore",
            ]
            param_args_prefixes = [
                "-d",
                "--directory",
                "-u",
                "--repo-url",
                "-m",
                "--commit-message",
                "-b",
                "--branch-name",
            ]
            idx = 1
            while idx < len(sys.argv):
                arg = sys.argv[idx]
                is_script_arg = arg in script_args_to_filter
                is_param_arg = False
                for prefix in param_args_prefixes:
                    if arg.startswith(prefix):
                        is_param_arg = True
                        if arg == prefix:
                            idx += 1
                        break
                if not is_script_arg and not is_param_arg:
                    test_argv.append(arg)
                idx += 1
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
            protect_main_push=args.protect_main_push,  # Pass correct parameter
            auto_setup_remote=args.auto_setup_remote,
        )
        initializer.initialize_repository()
    except SystemExit:
        raise
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred during script execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    if "--run-tests" not in sys.argv:
        main()
    else:
        main()

# --- Example Unit Tests ---
# (The previous example unit tests for hook installation would need to be adjusted
#  to only expect the pre-push hook to be installed by default,
#  and no pre-commit hook unless explicitly added back as a feature.)
