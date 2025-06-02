# app.py (your main Gradio script)
# co-author : Gemini 2.5 Pro Preview
import json
import logging
import pathlib
import platform
import subprocess

import gradio as gr

from coffee_maker.utils.isolated_venv import setup_isolated_venv

# Configure logging for the main app
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration for the sentiment analysis worker ---
VENV_DIR_PATH = pathlib.Path(__file__).parent / ".sentiment_venv"  # Name of the virtual environment directory
PYTHON_VERSION = platform.python_version()
PACKAGES_TO_INSTALL = ["textblob==0.19.0"]

# Path to the sentiment worker script
WORKER_SCRIPT_PATH = pathlib.Path(__file__).parent / "sentiment_worker.py"
logger.info(f"Expected worker script path: {WORKER_SCRIPT_PATH.resolve()}")  # Use resolve() for absolute path
logger.info(f"Does worker script exist at that path? {WORKER_SCRIPT_PATH.exists()}")


def sentiment_analysis(text: str) -> dict:
    """
    Analyze the sentiment of the given text by calling the sentiment_worker.py script
    in its dedicated virtual environment.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary containing the sentiment analysis results
              (e.g., {"polarity": 0.5, "subjectivity": 0.5, "assessment": "positive"})
              or an error message (e.g., {"error": "Error details"}).
    """
    if not text.strip():
        return {"error": "Input text cannot be empty."}

    try:
        venv_python_executable = setup_isolated_venv(
            venv_dir_path=VENV_DIR_PATH, packages_to_install=PACKAGES_TO_INSTALL
        )
    except Exception as e:
        logger.critical(f"Function sentiment analysis failed: Could not set up sentiment worker environment: {e}")
        return {"error": f"Failed to set up sentiment worker environment: {str(e)}"}

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
            logger.error(f"Worker stdout: {result.stdout.strip()}")
            try:
                error_json = json.loads(result.stdout.strip())
                if "error" in error_json:
                    return error_json
                else:
                    # If worker failed but stdout was JSON without an 'error' key, construct a clear error.
                    return {
                        "error": f"Worker script failed (exit code {result.returncode}). Unexpected JSON output.",
                        "worker_stdout": result.stdout.strip(),  # Include original output for debugging
                        "worker_stderr": result.stderr.strip(),
                    }
            except json.JSONDecodeError:
                return {
                    "error": f"Worker script failed (exit code {result.returncode}). Stderr: {result.stderr.strip()}"
                }

        # Parse the JSON output from the worker script
        analysis_result = json.loads(result.stdout.strip())
        return analysis_result

    except subprocess.TimeoutExpired:
        logger.error("Sentiment analysis worker timed out.")
        return {"error": "Sentiment analysis process timed out."}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from sentiment worker. Raw output: {result.stdout.strip()}")
        return {"error": "Invalid response from sentiment analysis worker."}
    except Exception as e: # Consider catching more specific exceptions if possible
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
    demo.launch(mcp_server=True)
