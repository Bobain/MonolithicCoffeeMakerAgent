# test_minimal_env_for_tests.py
# co-author : Gemini 2.5 Pro Preview

import logging
import os

from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
REQUIRED_ENV_VAR_NAME = "COFFEE_MAKER_RUN_TEST”"
EXPECTED_ENV_VAR_VALUE = "True"


def check_test_environment_variable():
    """
    Loads environment variables from a .env file, then checks for the
    presence and value of COFFEE_MAKER_RUN_TEST.

    Raises:
        EnvironmentError: If the .env file cannot be loaded.
        KeyError: If the COFFEE_MAKER_RUN_TEST variable is not found.
        ValueError: If COFFEE_MAKER_RUN_TEST has a value other than "True".
    """
    logger.info("Attempting to load environment variables from .env file...")
    # load_dotenv will search for a .env file in the current directory or parent directories
    # It returns True if a .env file was found and loaded, False otherwise.
    # It does not raise an error if the file is not found, so we check its return.
    # It can also take a specific path: load_dotenv(dotenv_path='/path/to/.env')
    # Or override existing env vars: load_dotenv(override=True)
    found_dotenv = load_dotenv()

    if not found_dotenv:
        # Depending on strictness, you might not want to raise an error if .env is optional
        # and variables could be set by other means (e.g. system environment).
        # For this script's purpose (testing the .env loading for tests), we'll warn.
        # If the variable isn't found later, THAT will be an error.
        logger.warning("No .env file found. Environment variables might not be set as expected for tests.")
        # If .env file is strictly required, you could raise an error here:
        # raise EnvironmentError("Failed to find and load the .env file. This file is required for test configuration.")

    logger.info(f"Checking for environment variable: '{REQUIRED_ENV_VAR_NAME}'")
    env_var_value = os.getenv(REQUIRED_ENV_VAR_NAME)

    if env_var_value is None:
        error_message = (
            f"Environment variable '{REQUIRED_ENV_VAR_NAME}' not found. " f"This variable is required to run the tests."
        )
        logger.error(error_message)
        raise KeyError(error_message)

    logger.info(f"Found '{REQUIRED_ENV_VAR_NAME}' with value: '{env_var_value}'")

    if env_var_value != EXPECTED_ENV_VAR_VALUE:
        error_message = (
            f"Environment variable '{REQUIRED_ENV_VAR_NAME}' has an incorrect value. "
            f"Expected: '{EXPECTED_ENV_VAR_VALUE}', Got: '{env_var_value}'."
        )
        logger.error(error_message)
        raise ValueError(error_message)

    logger.info(f"Environment variable '{REQUIRED_ENV_VAR_NAME}' is correctly set to '{EXPECTED_ENV_VAR_VALUE}'.")
    logger.info("Minimal environment check for tests passed successfully.")


if __name__ == "__main__":
    logger.info("--- Running Minimal Environment Check for Tests ---")
    try:
        check_test_environment_variable()
        logger.info("SUCCESS: All checks passed.")
    except (KeyError, ValueError, EnvironmentError) as e:
        # The function itself logs the specific error, here we just note failure.
        logger.info(f"FAILURE: An environment check failed. See details above. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        logger.info("FAILURE: An unexpected error occurred during the check.")
    logger.info("--- Minimal Environment Check Finished ---")
