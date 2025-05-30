# tests/test_minimal_env_for_tests.py
# co-author : Gemini 2.5 Pro Preview

import logging
import os

from dotenv import load_dotenv

# Configure basic logging
# Pytest captures logging, but this can be useful if you run the file standalone
# or want to see logs during pytest execution (e.g., with -s or specific pytest config).
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
REQUIRED_ENV_VAR_NAME = "COFFEE_MAKER_RUN_CI_TESTS"
EXPECTED_ENV_VAR_VALUE = "True"


def test_coffee_maker_run_test_variable_is_set_to_true():
    """
    Tests that the COFFEE_MAKER_RUN_TEST environment variable is correctly set.
    This test will fail if:
    1. The variable is not found after attempting to load .env.
    2. The variable is found but its value is not "True".
    """
    logger.info("Attempting to load .env file for test_coffee_maker_run_test_variable...")
    # load_dotenv() will search for .env in the current dir or parent dirs.
    # It returns True if found and loaded, False otherwise.
    # It does not raise an error if .env is not found.
    found_dotenv = load_dotenv()

    if not found_dotenv:
        logger.warning(
            f"No .env file found. Test relies on '{REQUIRED_ENV_VAR_NAME}' "
            "being set either in .env or the system environment."
        )
        # The test will proceed and fail at the assert if the variable isn't set
        # by other means (e.g., system environment).

    logger.info(f"Checking for environment variable: '{REQUIRED_ENV_VAR_NAME}'")
    env_var_value = os.getenv(REQUIRED_ENV_VAR_NAME)

    assert env_var_value is not None, (
        f"Environment variable '{REQUIRED_ENV_VAR_NAME}' not found. "
        f"This variable is required, expected to be set to '{EXPECTED_ENV_VAR_VALUE}'."
    )

    logger.info(f"Found '{REQUIRED_ENV_VAR_NAME}' with value: '{env_var_value}'")

    assert env_var_value == EXPECTED_ENV_VAR_VALUE, (
        f"Environment variable '{REQUIRED_ENV_VAR_NAME}' has an incorrect value. "
        f"Expected: '{EXPECTED_ENV_VAR_VALUE}', Got: '{env_var_value}'."
    )

    logger.info(
        f"SUCCESS: Environment variable '{REQUIRED_ENV_VAR_NAME}' is correctly set " f"to '{EXPECTED_ENV_VAR_VALUE}'."
    )


# You can add more test functions in this file, for example:
# def test_another_critical_env_variable():
#     load_dotenv() # Or ensure it's loaded once at the top if all tests need it
#     another_var = os.getenv("ANOTHER_IMPORTANT_VAR")
#     assert another_var is not None, "ANOTHER_IMPORTANT_VAR must be set."
#     assert another_var == "some_expected_value", "ANOTHER_IMPORTANT_VAR has wrong value."

# The if __name__ == "__main__": block is generally not needed in pytest test files,
# as pytest handles the execution. You can remove it or keep it for direct script execution
# if you have a specific need for that. Pytest will ignore this block.
if __name__ == "__main__":
    logger.info("--- Running Minimal Environment Check (Standalone Script Execution) ---")
    try:
        # This directly calls the test function for standalone demonstration
        test_coffee_maker_run_test_variable_is_set_to_true()
        logger.info("Standalone execution: Check passed.")
    except AssertionError as e:
        logger.error(f"Standalone execution: Check FAILED. {e}")
    except Exception as e:
        logger.error(f"Standalone execution: An unexpected error occurred: {e}", exc_info=True)
    logger.info("--- Standalone Script Execution Finished ---")
