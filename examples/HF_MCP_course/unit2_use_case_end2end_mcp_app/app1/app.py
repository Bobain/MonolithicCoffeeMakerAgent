# app.py (your main Gradio script)
# co-author : Gemini 2.5 Pro Preview
import json
import logging
import pathlib
import subprocess

import gradio as gr

from coffee_maker.utils.isolated_venv import setup_isolated_venv

# Configure logging for the main app
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration for the sentiment analysis worker ---
VENV_DIR_PATH = pathlib.Path(__file__).parent / ".sentiment_venv"  # Name of the virtual environment directory
PYTHON_VERSION_FOR_VENV = "3.12"  # Desired Python for the venv
PAKAGES_TO_INSTALL = ["textblob==0.19.0"]

# Path to the sentiment worker script
WORKER_SCRIPT_PATH = pathlib.Path(__file__).parent / "sentiment_worker.py"
logger.info(f"Expected worker script path: {WORKER_SCRIPT_PATH.resolve()}")  # Use resolve() for absolute path
logger.info(f"Does worker script exist at that path? {WORKER_SCRIPT_PATH.exists()}")


def sentiment_analysis(text: str) -> dict:
    """
    Analyze the sentiment of the given text by calling the sentiment_worker.py script
    in its dedicated virtual environment.
    """
    if not text.strip():
        return {"error": "Input text cannot be empty."}

    try:
        venv_python_executable = setup_isolated_venv(VENV_DIR_PATH, PAKAGES_TO_INSTALL)
    except Exception as e:
        logger.critical(f"Function sentiment analysis failed: Could not set up sentiment worker environment: {e}")
        exit(1)

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
    demo.launch(mcp_server=True)
