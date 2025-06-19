# co-author: Gemini Code Assist
import argparse
import difflib  # For generating diffs
import logging
import os
import pathlib

import google
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
# Relative path to the style guide from the script's location or project root
DEFAULT_STYLEGUIDE_PATH = "./.gemini/styleguide.md"
# Relative path to the .env file
DEFAULT_ENV_FILE_PATH = "./.env"
# Environment variable name for the API key
API_KEY_ENV_VAR = "GEMINI_API_KEY"  # As per your preference

# Delimiters for parsing LLM response
MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


def load_api_key(env_file_path: str) -> str | None:
    """Loads the Google API key from .env file or environment variables.

    Args:
        env_file_path (str): The path to the .env file.

    Returns:
        str | None: The API key if found, otherwise None.
    """
    if pathlib.Path(env_file_path).is_file():
        logging.info(f"Sourcing environment variables from '{env_file_path}'...")
        load_dotenv(dotenv_path=env_file_path, override=True)
    else:
        logging.info(f"Info: Environment file '{env_file_path}' not found. Checking system environment variables.")

    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        logging.error(
            f"Error: API key not found. Please set the {API_KEY_ENV_VAR} environment variable "
            f"or provide it in '{env_file_path}'."
        )
        logging.info(f"You can get an API key from Google AI Studio (https://aistudio.google.com/app/apikey).")
        return None
    return api_key


def read_file_content(file_path: str) -> str | None:
    """Reads the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Error: File not found at '{file_path}'.")
        return None
    except Exception as e:
        logging.exception(f"Error reading file '{file_path}': {e}")
        return None


def write_file_content(file_path: str, content: str) -> bool:
    """Writes content to a file, overwriting it."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Successfully updated '{file_path}'.")
        return True
    except Exception as e:
        logging.exception(f"Error writing to file '{file_path}': {e}")
        return False


def construct_llm_prompt(style_guide_content: str, code_to_modify: str, file_name: str) -> str:
    """Constructs the prompt for the LLM, asking for modified code and explanations."""
    prompt = f"""You are an expert code formatting and styling assistant.
Your task is to take the provided code snippet and reformat/restyle it to adhere (with minimal changes : don't change the code logic) to the rules outlined in the "STYLE GUIDE" below.
The code is from the file named '{file_name}'.

Your response MUST be structured in two parts, using the exact delimiters provided:

Part 1: The Modified Code
Begin this part with the delimiter "{MODIFIED_CODE_DELIMITER_START}" on a new line.
Provide ONLY the fully modified code. Do not include any explanations, apologies, or introductory sentences within this code block.
End this part with the delimiter "{MODIFIED_CODE_DELIMITER_END}" on a new line.

Part 2: Explanations for Changes
Begin this part with the delimiter "{EXPLANATIONS_DELIMITER_START}" on a new line.
List the significant changes you made to the code and briefly explain why each change was made, referencing the "STYLE GUIDE" rules where applicable.
If no changes were made, state "No changes were necessary."
End this part with the delimiter "{EXPLANATIONS_DELIMITER_END}" on a new line.

Example of your response structure:
{MODIFIED_CODE_DELIMITER_START}
# ... your modified code here ...
{MODIFIED_CODE_DELIMITER_END}
{EXPLANATIONS_DELIMITER_START}
- Line X: Changed Y to Z because of style guide rule A.1 (e.g., line length).
- Line Y: Refactored function F for clarity as per style guide section B (e.g., readability).
{EXPLANATIONS_DELIMITER_END}

STYLE GUIDE:
---
{style_guide_content}
---

As an additional rule to STYLE GUIDE :
- Never ever add blank lines or spaces whatever the reason

ORIGINAL CODE from '{file_name}':
---
{code_to_modify}
---

Now, provide your response following the structure above.
"""
    return prompt


def parse_llm_response(llm_full_response: str) -> tuple[str | None, str | None]:
    """Parses the LLM's response to extract modified code and explanations."""
    modified_code = None
    explanations = None
    logging.debug(f"PARSER: Received LLM response length: {len(llm_full_response)}")

    try:
        # Find the primary delimiters that separate the main sections
        idx_code_start_delimiter = llm_full_response.find(MODIFIED_CODE_DELIMITER_START)
        idx_explanation_start_delimiter = llm_full_response.find(EXPLANATIONS_DELIMITER_START)
        idx_explanation_end_delimiter = llm_full_response.find(EXPLANATIONS_DELIMITER_END)

        # --- Extract Explanations First ---
        if (
            idx_explanation_start_delimiter != -1
            and idx_explanation_end_delimiter != -1
            and idx_explanation_start_delimiter < idx_explanation_end_delimiter
        ):
            start_of_explanation_payload = idx_explanation_start_delimiter + len(EXPLANATIONS_DELIMITER_START)
            explanations = llm_full_response[start_of_explanation_payload:idx_explanation_end_delimiter].strip()
        elif idx_explanation_start_delimiter != -1:
            logging.warning(
                f"PARSER: Found '{EXPLANATIONS_DELIMITER_START}' but no matching '{EXPLANATIONS_DELIMITER_END}'. Explanation block might be unterminated."
            )
            explanations = llm_full_response[
                idx_explanation_start_delimiter + len(EXPLANATIONS_DELIMITER_START) :
            ].strip()
        else:
            logging.warning(
                f"PARSER: Could not find explanation block delimiters ('{EXPLANATIONS_DELIMITER_START}', '{EXPLANATIONS_DELIMITER_END}')."
            )

        # --- Extract Modified Code ---
        if idx_code_start_delimiter != -1:
            start_of_code_payload = idx_code_start_delimiter + len(MODIFIED_CODE_DELIMITER_START)
            end_of_ai_code_block_boundary = -1

            if idx_explanation_start_delimiter != -1 and idx_explanation_start_delimiter > start_of_code_payload:
                end_of_ai_code_block_boundary = idx_explanation_start_delimiter
            else:
                end_of_ai_code_block_boundary = llm_full_response.rfind(
                    MODIFIED_CODE_DELIMITER_END, start_of_code_payload
                )
                if end_of_ai_code_block_boundary == -1:
                    end_of_ai_code_block_boundary = len(llm_full_response)
                    logging.warning(
                        f"PARSER: No '{EXPLANATIONS_DELIMITER_START}' found after code, and no '{MODIFIED_CODE_DELIMITER_END}' found. Assuming code extends to end of response."
                    )

            if start_of_code_payload < end_of_ai_code_block_boundary:
                ai_code_output_segment = llm_full_response[start_of_code_payload:end_of_ai_code_block_boundary]
                stripped_ai_code_segment = ai_code_output_segment.rstrip()

                if stripped_ai_code_segment.endswith(MODIFIED_CODE_DELIMITER_END):
                    modified_code = stripped_ai_code_segment[: -len(MODIFIED_CODE_DELIMITER_END)].strip()
                else:
                    logging.warning(
                        f"PARSER: AI's code output segment (len {len(stripped_ai_code_segment)}) did not end with '{MODIFIED_CODE_DELIMITER_END}'. "
                        f"Segment tail (last 50 chars): '{repr(stripped_ai_code_segment[-50:])}'. Using segment as is (after stripping)."
                    )
                    modified_code = stripped_ai_code_segment.strip()
            else:
                logging.warning(
                    f"PARSER: Code start payload index ({start_of_code_payload}) not before code end boundary ({end_of_ai_code_block_boundary}). Cannot extract code."
                )
        else:
            logging.warning(f"PARSER: '{MODIFIED_CODE_DELIMITER_START}' not found. Cannot extract modified code.")
            if not explanations and llm_full_response.strip():
                logging.warning(
                    "PARSER: No delimiters found, but response exists. Treating as malformed, no code/explanation extracted."
                )
    except Exception as e:
        logging.exception(f"PARSER: Error during LLM response parsing: {e}")

    logging.debug(f"PARSER: Final modified_code (first 100): {repr(modified_code[:100]) if modified_code else 'None'}")
    logging.debug(f"PARSER: Final explanations (first 100): {repr(explanations[:100]) if explanations else 'None'}")
    return modified_code, explanations


def get_ai_suggestion(api_key: str, model_name: str, prompt: str) -> tuple[str | None, str | None]:
    """Calls the Gemini API and gets the modified code and explanations."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        logging.info(f"Sending request to Gemini model '{model_name}'...")

        generation_config = genai.types.GenerationConfig(candidate_count=1, temperature=0.1)
        response = model.generate_content(prompt, generation_config=generation_config)

        if not response.candidates or not response.candidates[0].content.parts:
            logging.error("Error: Model did not return any content.")
            if response.prompt_feedback:
                logging.info(f"Prompt Feedback: {response.prompt_feedback}")
            return None, None

        full_llm_output = response.text
        logging.debug("\n" + "=" * 20 + " RAW LLM RESPONSE " + "=" * 20)
        logging.debug(f"Raw LLM Output Length: {len(full_llm_output)}")
        # logging.debug(full_llm_output) # Uncomment for full raw output
        logging.debug("=" * (40 + len(" RAW LLM RESPONSE ")) + "\n")
        return parse_llm_response(full_llm_output)

    except google.generativeai.types.BlockedPromptException as bpe:
        logging.error(f"Gemini API Error: Prompt was blocked. {bpe}")
        return None, None
    except google.api_core.exceptions.GoogleAPICallError as api_error:
        logging.error(f"Google API Call Error: {api_error}")
        return None, None
    except Exception as e:
        logging.exception(f"Unexpected error calling Gemini API: {e}")
        if hasattr(e, "response") and e.response:
            logging.error(f"API Response Status: {e.response.status_code}")
            logging.error(f"API Response Body: {e.response.text}")
        return None, None


def generate_and_write_diff(
    original_content: str, modified_content: str, target_file_path: str, explanations: str | None
) -> bool:
    """
    Generates a diff and writes it to a .diff.<filename> file if actual code changes exist.
    Explanations are included in the diff file if changes were made, or logged if no code changes.
    """
    original_filename = os.path.basename(target_file_path)
    diff_filename = f".diff.{original_filename}"
    diff_file_path = os.path.join(os.path.dirname(target_file_path), diff_filename)

    # Primary condition: Only create a diff file if code content has actually changed.
    if original_content.strip() == modified_content.strip():
        logging.info("Code content is identical to the original after stripping whitespace.")
        if explanations:
            # Log explanations, but do not create the diff file for the code.
            logging.info(f"AI provided explanations for no code change:\n{explanations}")
        else:
            logging.info("No explanations provided for identical code.")
        logging.info(f"Diff file '{diff_file_path}' will NOT be created as there are no actual code changes.")
        return True  # Operation considered successful, but no diff file generated for code.

    # If we reach here, original_content.strip() != modified_content.strip(), so there are changes.
    logging.info("Code content has changed. Generating diff file.")
    original_lines = original_content.splitlines(keepends=True)
    modified_lines = modified_content.splitlines(keepends=True)

    diff_generator = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{original_filename}",
        tofile=f"b/{original_filename}",
        lineterm="",
    )
    diff_content_list = list(diff_generator)

    try:
        with open(diff_file_path, "w", encoding="utf-8") as f:
            f.write(f"# Diff for {original_filename} (AI Suggested Changes)\n")
            f.write("# Generated by auto_gemini_styleguide.py\n")
            f.write("-" * 30 + " GIT-STYLE UNIFIED DIFF " + "-" * 30 + "\n")

            if not diff_content_list:
                logging.warning(
                    "Difflib generated an empty diff list, but content comparison (strip) indicated a difference. This is unusual."
                )
                f.write("--- Difflib reported no changes, but content comparison (strip) differed. ---\n")
            else:
                for line in diff_content_list:
                    f.write(line)

            if explanations:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write(explanations + "\n")
            else:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write("No specific explanations were provided by the AI for these changes.\n")

        logging.info(f"Successfully wrote diff and explanations to '{diff_file_path}'.")
        return True
    except Exception as e:
        logging.exception(f"Error writing to diff file '{diff_file_path}': {e}")
        return False


def main():
    """Main function to autocorrect a file using Google AI and generate a diff."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Autocorrects a file using Google AI according to a style guide and generates a diff with explanations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("target_file_path", help="The path to the Python file to autocorrect.")
    parser.add_argument(
        "--styleguide",
        default=DEFAULT_STYLEGUIDE_PATH,
        help=f"Path to the style guide markdown file (default: {DEFAULT_STYLEGUIDE_PATH}).",
    )
    parser.add_argument(
        "--envfile",
        default=DEFAULT_ENV_FILE_PATH,
        help=f"Path to the .env file for API key (default: {DEFAULT_ENV_FILE_PATH}).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-lite",
        help="The Gemini model to use (e.g., 'gemini-1.5-flash-latest', 'gemini-pro').",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create a backup of the original file (as .bak) before overwriting."
    )
    parser.add_argument(
        "--no-modify", action="store_true", help="Do not modify the original file. Only generate the .diff file."
    )

    args = parser.parse_args()
    logging.info("--- AI Code Style Corrector & Differ ---")
    api_key = load_api_key(args.envfile)
    if not api_key:
        return 1

    logging.info(f"Reading style guide from: {args.styleguide}")
    style_guide_content = read_file_content(args.styleguide)
    if style_guide_content is None:
        return 1

    logging.info(f"Reading target file: {args.target_file_path}")
    original_code_content = read_file_content(args.target_file_path)
    if original_code_content is None:
        return 1

    if args.backup:
        backup_file_path = f"{args.target_file_path}.bak"
        logging.info(f"Creating backup: {backup_file_path}")
        if not write_file_content(backup_file_path, original_code_content):
            logging.warning("Warning: Failed to create backup. Proceeding cautiously.")

    prompt = construct_llm_prompt(style_guide_content, original_code_content, pathlib.Path(args.target_file_path).name)
    modified_code, explanations = get_ai_suggestion(api_key, args.model, prompt)

    if modified_code is not None:
        logging.info("--- AI Suggestion Received ---")
        should_process_changes = modified_code.strip() != original_code_content.strip() or bool(explanations)

        if should_process_changes:
            # generate_and_write_diff will now internally decide if a diff FILE is created
            generate_and_write_diff(original_code_content, modified_code, args.target_file_path, explanations)

            if args.no_modify:
                logging.info(f"Original file '{args.target_file_path}' was NOT modified due to --no-modify flag.")
            elif modified_code.strip() == original_code_content.strip():
                logging.info("AI returned identical code content. No changes made to the original file based on code.")
            else:
                logging.info(f"Attempting to write AI modified code back to '{args.target_file_path}'...")
                logging.info("IMPORTANT: Please review the changes carefully after the script finishes.")
                if write_file_content(args.target_file_path, modified_code):
                    logging.info("Original file successfully updated with AI suggestions.")
                else:
                    logging.error("Failed to write modified code to the original file.")
                    return 1
        else:
            logging.info("AI returned identical code content and no explanations. No changes made, no diff generated.")
        logging.info("Process completed.")
    else:
        logging.error(
            "Failed to get a valid modified code block from the AI. No changes made to the file. No diff generated."
        )
        if explanations:
            logging.info("AI provided explanations, but no valid code block was parsed:")
            logging.info("-" * 20 + " EXPLANATIONS " + "-" * 20)
            logging.info(explanations)
            logging.info("-" * (40 + len(" EXPLANATIONS ")) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    import sys

    exit_code = main()
    sys.exit(exit_code)
