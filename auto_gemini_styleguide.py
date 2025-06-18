# co-author: Gemini Code Assist
import argparse
import difflib  # For generating diffs
import os
import pathlib

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
    """Loads the Google API key from .env file or environment variables."""
    if pathlib.Path(env_file_path).is_file():
        print(f"Sourcing environment variables from '{env_file_path}'...")
        load_dotenv(dotenv_path=env_file_path, override=True)
    else:
        print(f"Info: Environment file '{env_file_path}' not found. Checking system environment variables.")

    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        print(
            f"Error: API key not found. Please set the {API_KEY_ENV_VAR} environment variable "
            f"or provide it in '{env_file_path}'."
        )
        print(f"You can get an API key from Google AI Studio (https://aistudio.google.com/app/apikey).")
    return api_key


def read_file_content(file_path: str) -> str | None:
    """Reads the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None


def write_file_content(file_path: str, content: str) -> bool:
    """Writes content to a file, overwriting it."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully updated '{file_path}'.")
        return True
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}")
        return False


def construct_llm_prompt(style_guide_content: str, code_to_modify: str, file_name: str) -> str:
    """Constructs the prompt for the LLM, asking for modified code and explanations."""
    prompt = f"""You are an expert code formatting and styling assistant.
Your task is to take the provided code snippet and reformat/restyle it to strictly adhere to the rules outlined in the "STYLE GUIDE" below.
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

    try:
        # Find main block delimiters
        code_block_start_outer_idx = llm_full_response.find(MODIFIED_CODE_DELIMITER_START)
        explanations_block_start_idx = llm_full_response.find(EXPLANATIONS_DELIMITER_START)
        explanations_block_end_idx = llm_full_response.find(EXPLANATIONS_DELIMITER_END)

        if code_block_start_outer_idx != -1 and explanations_block_start_idx != -1:
            # The AI's code output is between MODIFIED_CODE_DELIMITER_START and EXPLANATIONS_DELIMITER_START.
            # The AI is *supposed* to put MODIFIED_CODE_DELIMITER_END in this segment.

            # Slice from after MODIFIED_CODE_DELIMITER_START to before EXPLANATIONS_DELIMITER_START
            # This segment contains the AI's code output and its intended MODIFIED_CODE_DELIMITER_END
            potential_code_block_with_its_end_delimiter = llm_full_response[
                code_block_start_outer_idx + len(MODIFIED_CODE_DELIMITER_START) : explanations_block_start_idx
            ]

            # Now find the MODIFIED_CODE_DELIMITER_END within this specific segment.
            # We use rfind because the AI should place its *actual* end delimiter at the end of this segment.
            end_code_idx_within_segment = potential_code_block_with_its_end_delimiter.rfind(MODIFIED_CODE_DELIMITER_END)

            if end_code_idx_within_segment != -1:
                modified_code = potential_code_block_with_its_end_delimiter[:end_code_idx_within_segment].strip()
            else:
                # If MODIFIED_CODE_DELIMITER_END is missing within the segment,
                # assume the whole segment (minus trailing whitespace) is the code.
                # This can happen if the AI forgets the end delimiter for code but correctly starts explanations.
                print(
                    f"Warning: '{MODIFIED_CODE_DELIMITER_END}' not found between code start and explanations start. "
                    "Taking content up to explanations as modified code."
                )
                modified_code = potential_code_block_with_its_end_delimiter.strip()
        else:
            # This case handles if the primary structure (code start or explanation start) is missing.
            print("Warning: Could not find primary delimiters for code block start or explanations start.")
            # Fallback to simpler parsing if the main structure is broken
            # but individual start/end delimiters for code might exist.
            first_start = llm_full_response.find(MODIFIED_CODE_DELIMITER_START)
            first_end = llm_full_response.find(MODIFIED_CODE_DELIMITER_END)
            if first_start != -1 and first_end != -1 and first_start < first_end:
                # This is the old logic, less robust, but a fallback.
                modified_code = llm_full_response[first_start + len(MODIFIED_CODE_DELIMITER_START) : first_end].strip()
                print("Warning: Used fallback parsing for modified code.")
            elif (
                llm_full_response
                and EXPLANATIONS_DELIMITER_START not in llm_full_response
                and EXPLANATIONS_DELIMITER_END not in llm_full_response
            ):
                # If no explanation delimiters at all, assume whole thing is code
                modified_code = llm_full_response.strip()
                print("Warning: No explanation delimiters found. Treating entire response as modified code.")

        # Extract explanations (this part was generally okay)
        if explanations_block_start_idx != -1 and explanations_block_end_idx != -1:
            explanations = llm_full_response[
                explanations_block_start_idx + len(EXPLANATIONS_DELIMITER_START) : explanations_block_end_idx
            ].strip()
        else:
            print("Warning: Could not find delimiters for explanations block.")

        # Final safety net: if absolutely no delimiters were found and response exists
        if not modified_code and not explanations and llm_full_response:
            all_delimiters_missing = all(
                delim not in llm_full_response
                for delim in [
                    MODIFIED_CODE_DELIMITER_START,
                    MODIFIED_CODE_DELIMITER_END,
                    EXPLANATIONS_DELIMITER_START,
                    EXPLANATIONS_DELIMITER_END,
                ]
            )
            if all_delimiters_missing:
                print(
                    "Critical Warning: No delimiters found anywhere in the LLM response. "
                    "Treating entire response as modified code. This is likely incorrect."
                )
                modified_code = llm_full_response.strip()

    except Exception as e:
        print(f"Error during LLM response parsing: {e}")

    return modified_code, explanations


def get_ai_suggestion(api_key: str, model_name: str, prompt: str) -> tuple[str | None, str | None]:
    """Calls the Gemini API and gets the modified code and explanations."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        print(f"Sending request to Gemini model '{model_name}'...")

        generation_config = genai.types.GenerationConfig(candidate_count=1, temperature=0.1)

        response = model.generate_content(prompt, generation_config=generation_config)

        if not response.candidates or not response.candidates[0].content.parts:
            print("Error: Model did not return any content.")
            if response.prompt_feedback:
                print(f"Prompt Feedback: {response.prompt_feedback}")
            return None, None

        full_llm_output = response.text

        # --- TEMPORARY DEBUGGING: Print raw LLM response ---
        print("\n" + "=" * 20 + " RAW LLM RESPONSE " + "=" * 20)
        print(full_llm_output)
        print("=" * (40 + len(" RAW LLM RESPONSE ")) + "\n")  # Adjusted length for better formatting
        # --- END TEMPORARY DEBUGGING ---

        return parse_llm_response(full_llm_output)

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if hasattr(e, "response") and e.response:
            print(f"API Response Status: {e.response.status_code}")
            print(f"API Response Body: {e.response.text}")
        return None, None


def generate_and_write_diff(
    original_content: str, modified_content: str, target_file_path: str, explanations: str | None
) -> bool:
    """Generates a diff and writes it to a .diff.<filename> file, including explanations."""
    original_filename = os.path.basename(target_file_path)
    diff_filename = f".diff.{original_filename}"
    diff_file_path = os.path.join(os.path.dirname(target_file_path), diff_filename)

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

    if not diff_content_list and original_content.strip() == modified_content.strip():
        print(f"No textual changes detected.")
        if explanations:
            try:
                with open(diff_file_path, "w", encoding="utf-8") as f:
                    f.write(f"# AI Explanations for file: {original_filename}\n")
                    f.write("# No textual code changes were proposed by the AI.\n")
                    f.write("# However, the AI provided the following comments/explanations:\n")
                    f.write("-" * 30 + "\n")
                    f.write(explanations + "\n")
                print(f"Wrote AI explanations (no code changes) to '{diff_file_path}'.")
                return True
            except Exception as e:
                print(f"Error writing explanations (no code changes) to diff file '{diff_file_path}': {e}")
                return False
        else:
            print(f"Diff file '{diff_file_path}' will not be created as there are no changes and no explanations.")
        return True

    try:
        with open(diff_file_path, "w", encoding="utf-8") as f:
            f.write(f"# Diff for {original_filename} (AI Suggested Changes)\n")
            f.write("# Generated by auto_gemini_styleguide.py\n")
            f.write("-" * 30 + " GIT-STYLE UNIFIED DIFF " + "-" * 30 + "\n")
            for line in diff_content_list:
                f.write(line)

            if explanations:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write(explanations + "\n")
            else:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write("No specific explanations were provided by the AI for these changes.\n")

        print(f"Successfully wrote diff and explanations to '{diff_file_path}'.")
        return True
    except Exception as e:
        print(f"Error writing to diff file '{diff_file_path}': {e}")
        return False


def main():
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
        default="gemini-1.5-flash-latest",
        help="The Gemini model to use (e.g., 'gemini-1.5-flash-latest', 'gemini-pro', 'gemini-1.0-pro-latest').",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create a backup of the original file (as .bak) before overwriting."
    )
    parser.add_argument(
        "--no-modify", action="store_true", help="Do not modify the original file. Only generate the .diff file."
    )

    args = parser.parse_args()

    print("--- AI Code Style Corrector & Differ ---")

    api_key = load_api_key(args.envfile)
    if not api_key:
        return 1

    print(f"Reading style guide from: {args.styleguide}")
    style_guide_content = read_file_content(args.styleguide)
    if style_guide_content is None:
        return 1

    print(f"Reading target file: {args.target_file_path}")
    original_code_content = read_file_content(args.target_file_path)
    if original_code_content is None:
        return 1

    if args.backup:
        backup_file_path = f"{args.target_file_path}.bak"
        print(f"Creating backup: {backup_file_path}")
        if not write_file_content(backup_file_path, original_code_content):
            print("Warning: Failed to create backup. Proceeding cautiously.")

    prompt = construct_llm_prompt(style_guide_content, original_code_content, pathlib.Path(args.target_file_path).name)
    # For debugging the prompt (optional):
    # print("\n--- CONSTRUCTED PROMPT (snippet) ---")
    # print(prompt[:1500] + "..." if len(prompt) > 1500 else prompt)
    # print("--- END OF PROMPT SNIPPET ---\n")

    modified_code, explanations = get_ai_suggestion(api_key, args.model, prompt)

    if modified_code is not None:  # Check if modified_code is not None (even if empty string)
        print("\n--- AI Suggestion Received ---")

        # Only generate diff and write file if modified_code is actually different
        # or if there are explanations (even for no code change).
        if modified_code.strip() != original_code_content.strip() or explanations:
            generate_and_write_diff(original_code_content, modified_code, args.target_file_path, explanations)

            if args.no_modify:
                print(f"Original file '{args.target_file_path}' was NOT modified due to --no-modify flag.")
            elif modified_code.strip() == original_code_content.strip():
                # This case might be hit if only explanations were provided for an identical code.
                print("AI returned identical code content. No changes made to the original file based on code.")
            else:
                print(f"Attempting to write AI modified code back to '{args.target_file_path}'...")
                print("IMPORTANT: Please review the changes carefully after the script finishes.")
                if write_file_content(args.target_file_path, modified_code):
                    print("Original file successfully updated with AI suggestions.")
                else:
                    print("Failed to write modified code to the original file.")
                    return 1
        else:
            print("AI returned identical code content and no explanations. No changes made, no diff generated.")
        print("Process completed.")
    else:
        # This means get_ai_suggestion returned (None, explanations) or (None, None)
        print("Failed to get a valid modified code block from the AI. No changes made to the file. No diff generated.")
        if explanations:  # If explanations were returned but code was None
            print("AI provided explanations, but no valid code block was parsed:")
            print("-" * 20 + " EXPLANATIONS " + "-" * 20)
            print(explanations)
            print("-" * (40 + len(" EXPLANATIONS ")) + "\n")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
