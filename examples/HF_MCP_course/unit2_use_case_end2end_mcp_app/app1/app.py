# app.py (your main Gradio script)
# co-author : Gemini 2.5 Pro Preview
import json
import logging
import pathlib
import subprocess
import sys

import gradio as gr

# Configure logging for the main app
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration for the sentiment analysis worker ---
VENV_NAME = ".sentiment_venv"  # Name of the virtual environment directory
PYTHON_VERSION_FOR_VENV = "3.12"  # Desired Python for the venv
PAKAGES_TO_INSTALL = ["textblob==0.19.0"]

# Path to the sentiment worker script
WORKER_SCRIPT_PATH = pathlib.Path(__file__).parent / "sentiment_worker.py"
logger.info(f"Expected worker script path: {WORKER_SCRIPT_PATH.resolve()}")  # Use resolve() for absolute path
logger.info(f"Does worker script exist at that path? {WORKER_SCRIPT_PATH.exists()}")


def get_venv_python_executable(venv_dir_name: str) -> str:
    """Gets the path to the Python executable in the virtual environment."""
    base_path = pathlib.Path(venv_dir_name)
    if sys.platform == "win32":
        return str(base_path / "Scripts" / "python.exe")
    else:
        return str(base_path / "bin" / "python")


def setup_sentiment_venv():
    """
    Creates a virtual environment and installs TextBlob if not already set up.
    Uses 'uv' for environment and package management.
    """
    venv_path = pathlib.Path(VENV_NAME)
    venv_python_executable = get_venv_python_executable(VENV_NAME)

    if not (venv_path.exists() and pathlib.Path(venv_python_executable).exists()):
        logger.info(f"Virtual environment '{VENV_NAME}' not found or incomplete. Creating...")
        try:
            # Create venv
            subprocess.run(
                ["uv", "venv", VENV_NAME, f"--python={PYTHON_VERSION_FOR_VENV}"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"Virtual environment '{VENV_NAME}' created successfully.")

            # Install packages in the venv
            for package in PAKAGES_TO_INSTALL:
                install_command = ["uv", "pip", "install", "-p", venv_python_executable, package]
                logger.info(f"Installing {package} using command: {' '.join(install_command)}")
                result = subprocess.run(install_command, check=True, capture_output=True, text=True)
                logger.info(f"{package} installed successfully in '{VENV_NAME}'. Output:\n{result.stdout}")

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
    else:
        logger.info(f"Virtual environment '{VENV_NAME}' with to be already set up, but maybe have missing packages.")


def sentiment_analysis(text: str) -> dict:
    """
    Analyze the sentiment of the given text by calling the sentiment_worker.py script
    in its dedicated virtual environment.
    """
    if not text.strip():
        return {"error": "Input text cannot be empty."}

    venv_python_executable = get_venv_python_executable(VENV_NAME)

    if not pathlib.Path(venv_python_executable).exists():
        logger.error(
            f"Python executable for sentiment venv not found at {venv_python_executable}. Setup might have failed."
        )
        return {"error": "Sentiment analysis environment is not configured correctly."}
    if not WORKER_SCRIPT_PATH.exists():
        logger.error(f"Sentiment worker script not found at {WORKER_SCRIPT_PATH}")
        return {"error": "Sentiment analysis worker script missing."}

    command = [venv_python_executable, str(WORKER_SCRIPT_PATH), text]  # Pass text as a command-line argument
    logger.info(f"Running sentiment worker with command: {' '.join(command)}")

    try:
        # Use subprocess.run to execute the worker script
        result = subprocess.run(
            command,
            capture_output=True,  # Capture stdout and stderr
            text=True,  # Decode output as text
            check=False,  # We will check returncode manually
            timeout=15,  # Add a timeout
        )

        if result.returncode != 0:
            logger.error(f"Sentiment worker script failed with exit code {result.returncode}")
            logger.error(f"Worker stderr: {result.stderr.strip()}")
            logger.error(f"Worker stdout: {result.stdout.strip()}")  # Log stdout too, it might have JSON error
            try:
                # Try to parse stdout as JSON even on error, worker might output JSON error
                error_json = json.loads(result.stdout.strip())
                return error_json if "error" in error_json else {"error": f"Worker failed: {result.stderr.strip()}"}
            except json.JSONDecodeError:
                return {"error": f"Worker script failed. Stderr: {result.stderr.strip()}"}

        # Parse the JSON output from the worker script
        analysis_result = json.loads(result.stdout.strip())
        return analysis_result

    except subprocess.TimeoutExpired:
        logger.error("Sentiment analysis worker timed out.")
        return {"error": "Sentiment analysis process timed out."}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from sentiment worker. Raw output: {result.stdout.strip()}")
        return {"error": "Invalid response from sentiment analysis worker."}
    except Exception as e:
        logger.error(f"An unexpected error occurred while running sentiment analysis: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}


# Create the Gradio interface
demo = gr.Interface(
    fn=sentiment_analysis,
    inputs=gr.Textbox(placeholder="Enter text to analyze...", label="Text Input"),
    outputs=gr.JSON(label="Sentiment Analysis Result"),
    title="Text Sentiment Analysis (Isolated Worker)",
    description="Analyze the sentiment of text. The analysis runs in a dedicated environment.",
)

# Launch the interface
if __name__ == "__main__":
    try:
        setup_sentiment_venv()
    except Exception as e:
        logger.critical(f"Application startup failed: Could not set up sentiment worker environment: {e}")
    demo.launch(mcp_server=True)
