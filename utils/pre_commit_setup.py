#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# co-author : Gemini 2.5 pro preview 05/06

"""
Pre-commit Setup Script

This script automates the setup of pre-commit hooks in a project directory.
It is designed to be run from the command line.

Key Features:
1.  Checks for necessary prerequisites:
    - 'pre-commit' executable installed and in PATH.
    - 'PyYAML' Python package installed.
2.  Locates its own default pre-commit configuration template from a relative
    'ressources/pre_commit/' subdirectory.
3.  Allows users to specify a custom YAML file for pre-commit hook configurations.
    If no custom file is provided, it uses the default template which includes
    'black' for code formatting.
4.  Writes the chosen (or default) pre-commit configuration to a
    '.pre-commit-config.yaml' file in the target project directory.
    - Handles existing configuration files (can force overwrite).
5.  Initializes a Git repository (`git init`) in the target directory if one
    doesn't already exist, as pre-commit requires it.
6.  Installs the pre-commit hooks into the Git repository's hook directory
    (`pre-commit install`).
7.  Optionally runs 'pre-commit autoupdate' to update hook versions in the
    configuration file.
8.  Optionally performs an initial run of all configured pre-commit hooks
    against all files in the repository (`pre-commit run --all-files`).

Prerequisites for Running the Script:
- Python 3.6+
- 'pre-commit' package must be installed (`pip install pre-commit`).
- 'PyYAML' package must be installed (`pip install PyYAML`).

Expected File Structure for the Script Itself:
If this script is `pre_commit_setup.py`, it expects its default template at:
  ./ressources/pre_commit/default_pre_commit_config_template.yaml

Command-Line Usage:
  python3 ./utils/pre_commit_setup.py

Common Options:
  -d, --directory DIR     Path to the project directory to set up pre-commit hooks.
                          (default: current directory)
  --hooks-file FILE     Path to a custom YAML file for pre-commit hooks.
                          If provided, this overrides the script's default template.
  --force-config          Overwrite an existing .pre-commit-config.yaml file
                          in the target directory.
  --skip-autoupdate       Skip running 'pre-commit autoupdate'.
  --skip-initial-run      Skip running 'pre-commit run --all-files' after setup.
  -v, --verbose           Enable verbose (DEBUG level) logging output.
  --help                  Show this help message and exit.

Example - Setup with defaults in current directory:
  python3 ./utils/pre_commit_setup.py

Example - Setup for a specific project using a custom hooks file:
  python pre_commit_setup.py -d ./my_other_project --hooks-file ./my_custom_hooks.yaml --force-config

Error Handling:
The script will log errors and exit with a non-zero status code if:
- Prerequisites are missing.
- Specified files (project directory, custom hooks file, internal templates) are not found.
- YAML parsing fails.
- Critical pre-commit commands fail (e.g., 'install' if .git directory is problematic).
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys

# PyYAML is imported conditionally later

# --- Script Configuration ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_TEMPLATE_PATH = os.path.join(
    _SCRIPT_DIR, "ressources", "pre_commit", "default_pre_commit_config_template.yaml"
)
PRE_COMMIT_CONFIG_FILENAME = ".pre-commit-config.yaml"

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# --- Custom Exceptions (Optional but good practice) ---
class PrerequisiteError(Exception):
    """Custom exception for missing prerequisites."""

    pass


class PreCommitManager:
    """Manages the setup of pre-commit hooks."""

    def __init__(
        self,
        project_directory=".",
        custom_hooks_file=None,
        force_config=False,
        skip_autoupdate=False,
        skip_initial_run=False,
    ):
        self.project_path = os.path.abspath(project_directory)
        self.custom_hooks_file = os.path.abspath(custom_hooks_file) if custom_hooks_file else None
        self.force_config = force_config
        self.skip_autoupdate = skip_autoupdate
        self.skip_initial_run = skip_initial_run
        self.target_config_path = os.path.join(self.project_path, PRE_COMMIT_CONFIG_FILENAME)

        self.yaml = self._import_pyyaml()  # Import and store yaml module
        self._check_prerequisites()

    def _import_pyyaml(self):
        """Attempts to import PyYAML and raises PrerequisiteError if not found."""
        try:
            import yaml

            return yaml
        except ImportError:
            msg = "PyYAML package is not installed. Please install it: pip install PyYAML"
            logger.error(msg)
            raise PrerequisiteError(msg)

    def _check_prerequisites(self):
        """Checks if pre-commit is installed and project directory exists."""
        if not shutil.which("pre-commit"):
            msg = "pre-commit command not found. Please install pre-commit: pip install pre-commit"
            logger.error(msg)
            raise PrerequisiteError(msg)  # Using custom exception

        if not os.path.isdir(self.project_path):
            msg = f"Project directory not found: {self.project_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)  # Standard exception

        if self.custom_hooks_file and not os.path.exists(self.custom_hooks_file):
            msg = f"Custom hooks file not found: {self.custom_hooks_file}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        if not os.path.exists(DEFAULT_CONFIG_TEMPLATE_PATH):
            msg = f"FATAL: Default pre-commit config template not found at: {DEFAULT_CONFIG_TEMPLATE_PATH}"
            logger.error(msg)
            # This is an internal script error, so a more severe error might be warranted
            # or ensure it's packaged correctly.
            raise FileNotFoundError(msg + " This is an internal file for pre_commit_setup.py.")

    def _run_command(self, command, cwd=None, check=True):
        """Executes a shell command."""
        effective_cwd = cwd or self.project_path
        logger.info(f"Executing: {' '.join(command)} in {effective_cwd}")
        try:
            process = subprocess.run(
                command, cwd=effective_cwd, check=check, capture_output=True, text=True, env=os.environ.copy()
            )
            if process.stdout:
                logger.debug(f"STDOUT:\n{process.stdout.strip()}")
            if process.stderr:
                logger.debug(f"STDERR:\n{process.stderr.strip()}")
            return process
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing command: {' '.join(command)}")
            logger.error(f"Return code: {e.returncode}")
            if e.stdout:
                logger.error(f"STDOUT:\n{e.stdout.strip()}")
            if e.stderr:
                logger.error(f"STDERR:\n{e.stderr.strip()}")
            raise  # Re-raise the exception
        except FileNotFoundError:  # This would typically be for the command itself (e.g. 'pre-commit')
            msg = f"Error: The command '{command[0]}' was not found. Ensure it is installed and in your PATH."
            logger.error(msg)
            raise PrerequisiteError(msg)  # Or EnvironmentError

    def _get_config_content(self):
        """Gets the pre-commit configuration content from user file or default."""
        if self.custom_hooks_file:
            logger.info(f"Using custom hooks configuration from: {self.custom_hooks_file}")
            source_path = self.custom_hooks_file
        else:
            logger.info(f"Using default hooks configuration template: {DEFAULT_CONFIG_TEMPLATE_PATH}")
            source_path = DEFAULT_CONFIG_TEMPLATE_PATH

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                content = self.yaml.safe_load(f)  # Use self.yaml
            if not content or "repos" not in content:
                msg = f"Invalid pre-commit config structure in {source_path}. Must contain 'repos' key."
                logger.error(msg)
                raise ValueError(msg)  # Or a custom ConfigFormatError
            return content
        except self.yaml.YAMLError as e:  # Use self.yaml
            msg = f"Error parsing YAML from {source_path}: {e}"
            logger.error(msg)
            raise ValueError(msg) from e  # Or custom ConfigFormatError
        except IOError as e:
            msg = f"Error reading file {source_path}: {e}"
            logger.error(msg)
            raise  # Re-raise IOError

    def _write_config_file(self, config_data):
        """Writes the pre-commit configuration to the target project."""
        if os.path.exists(self.target_config_path) and not self.force_config:
            logger.warning(
                f"{PRE_COMMIT_CONFIG_FILENAME} already exists in {self.project_path}. "
                "Use --force-config to overwrite."
            )
            return False

        logger.info(f"Writing pre-commit configuration to: {self.target_config_path}")
        try:
            with open(self.target_config_path, "w", encoding="utf-8") as f:
                self.yaml.dump(config_data, f, sort_keys=False, indent=2)  # Use self.yaml
            return True
        except IOError as e:
            logger.error(f"Failed to write {self.target_config_path}: {e}")
            raise  # Re-raise IOError

    def setup(self):
        """Orchestrates the pre-commit setup process."""
        logger.info(f"Setting up pre-commit for project at: {self.project_path}")

        config_data = self._get_config_content()
        wrote_config = self._write_config_file(config_data)

        if not wrote_config and not self.force_config:
            logger.info("Skipping further pre-commit commands as config was not (over)written.")
        else:
            git_dir = os.path.join(self.project_path, ".git")
            if not os.path.isdir(git_dir):
                logger.info(f"No .git directory found in {self.project_path}. Initializing a new Git repository.")
                self._run_command(["git", "init"], cwd=self.project_path)

            logger.info("Installing pre-commit hooks into .git/hooks...")
            self._run_command(["pre-commit", "install"], cwd=self.project_path)

            if not self.skip_autoupdate:
                logger.info("Running pre-commit autoupdate to update hook versions...")
                self._run_command(["pre-commit", "autoupdate"], cwd=self.project_path)

            if not self.skip_initial_run:
                logger.info("Running pre-commit on all files for initial check/formatting...")
                self._run_command(["pre-commit", "run", "--all-files"], cwd=self.project_path, check=False)
            else:
                logger.info("Skipping initial run of pre-commit on all files.")

        logger.info("Pre-commit setup process complete.")
        if not self.skip_initial_run:
            logger.info(
                "Review any output from 'pre-commit run --all-files' above. You may need to stage and commit changes."
            )


def main():
    parser = argparse.ArgumentParser(
        description="Sets up pre-commit hooks in a project directory.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""
This script uses a default pre-commit configuration template (which includes 'black')
located at '{DEFAULT_CONFIG_TEMPLATE_PATH}' relative to the script itself,
unless a custom hooks file is specified with --hooks-file.
""",
    )
    # ... (argparse arguments as before) ...
    parser.add_argument(
        "-d", "--directory", default=".", help="Path to the project directory to set up (default: current directory)."
    )
    parser.add_argument(
        "--hooks-file",
        help="Path to a custom YAML file containing pre-commit hook configurations "
        "(structured like a .pre-commit-config.yaml). Overrides the default template.",
    )
    parser.add_argument(
        "--force-config", action="store_true", help=f"Overwrite an existing {PRE_COMMIT_CONFIG_FILENAME} file."
    )
    parser.add_argument("--skip-autoupdate", action="store_true", help="Skip running 'pre-commit autoupdate'.")
    parser.add_argument(
        "--skip-initial-run", action="store_true", help="Skip running 'pre-commit run --all-files' after setup."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level).")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        manager = PreCommitManager(
            project_directory=args.directory,
            custom_hooks_file=args.hooks_file,
            force_config=args.force_config,
            skip_autoupdate=args.skip_autoupdate,
            skip_initial_run=args.skip_initial_run,
        )
        manager.setup()
    except PrerequisiteError as e:  # Catch our custom exception
        # Message already logged by the class, so just exit
        # logger.error(f"Prerequisite missing: {e}") # Redundant if class logs
        sys.exit(2)  # Different exit code for prerequisite errors
    except FileNotFoundError as e:
        # Message already logged by the class if it's a known file
        # logger.error(f"File not found: {e}")
        sys.exit(3)
    except ValueError as e:  # For YAML parsing or structure errors
        # Message already logged by the class
        # logger.error(f"Configuration error: {e}")
        sys.exit(4)
    except subprocess.CalledProcessError:
        # Message already logged by _run_command
        logger.error("A pre-commit command failed. Please check the output above.")
        sys.exit(5)
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
