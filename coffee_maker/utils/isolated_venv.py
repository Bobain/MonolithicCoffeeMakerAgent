import logging
import pathlib
import platform
import shutil
import subprocess
import sys

version_str = platform.python_version()
print(version_str)


DEFAULT_PYTON_VERSION = platform.python_version()  # Default Python version for the virtual environment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_venv_python_executable(venv_dir_path: pathlib.Path) -> str:
    """Gets the path to the Python executable in the virtual environment.
    Args:
        venv_dir_path (pathlib.Path): Path to the virtual environment directory.
    Returns:
        str: Path to the Python executable in the virtual environment.
    """
    if sys.platform == "win32":
        return str(venv_dir_path / "Scripts" / "python.exe")
    else:
        return str(venv_dir_path / "bin" / "python")


def setup_isolated_venv(
    venv_dir_path: pathlib.Path = None,
    pakages_to_install: list[str] = None,
    overwrite_existing: bool = True,
    python_version: str = DEFAULT_PYTON_VERSION,
) -> None:
    """
    Creates a virtual environment and installs a list of packages if not already set up.
    Uses 'uv' for environment and package management.
    Args:
        venv_dir_path (pathlib.Path): Path to the virtual environment directory.
        pakages_to_install (list[str]): List of packages to install in the virtual environment.
        overwrite_existing (bool): Whether to overwrite an existing virtual environment.
        python_version (str): Python version to use for the virtual environment.
    Returns:
        str: Path to the Python executable in the virtual environment.
    """

    assert venv_dir_path is not None, "venv_dir_path must be provided"
    assert pakages_to_install is not None, "pakages_to_install must be provided"

    venv_python_executable = get_venv_python_executable(venv_dir_path)

    if (venv_dir_path.exists() and pathlib.Path(venv_python_executable).exists()) and overwrite_existing:
        logger.info(f"Virtual environment '{venv_dir_path}' found but deleting if. ({overwrite_existing=}))")
        shutil.rmtree(str(venv_dir_path))

    logger.info(f"Creating virtual environment '{venv_dir_path}' not found or incomplete. ...")
    try:
        # Create venv
        subprocess.run(
            ["uv", "venv", str(venv_dir_path), f"--python={python_version}"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Virtual environment '{venv_dir_path}' created successfully.")

        # Install packages in the venv
        for package in pakages_to_install:
            install_command = ["uv", "pip", "install", "-p", venv_python_executable, package]
            logger.info(f"Installing {package} using command: {' '.join(install_command)}")
            result = subprocess.run(install_command, check=True, capture_output=True, text=True)
            logger.info(f"{package} installed successfully in '{venv_dir_path}'. Output:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up virtual environment or installing TextBlob:")
        logger.error(f"Command: {' '.join(e.cmd)}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise RuntimeError("Failed to set up sentiment analysis environment.") from e
    except FileNotFoundError:
        logger.error("`uv` command not found. Please ensure `uv` is installed and in your PATH.")
        raise

    return venv_python_executable
