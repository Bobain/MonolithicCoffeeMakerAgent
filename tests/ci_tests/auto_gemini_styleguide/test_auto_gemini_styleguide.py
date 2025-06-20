# author : gemini-code-assist
import argparse  # Added: For argparse.Namespace and mocking
import logging  # Added: For logging levels and caplog
import os
import pathlib
from unittest import mock

import google.api_core.exceptions  # Added: For GoogleAPICallError
import google.generativeai.types  # Added: For BlockedPromptException

from coffee_maker import auto_gemini_styleguide as ags

# --- Tests for load_api_key ---


def test_load_api_key_from_env_var(monkeypatch):
    """Test API key is loaded from environment variable."""
    monkeypatch.setenv(ags.API_KEY_ENV_VAR, "test_api_key_from_env")
    # Mock pathlib.Path.is_file to return False so it doesn't try to load from a file
    monkeypatch.setattr(pathlib.Path, "is_file", lambda self: False)
    # Ensure the second load_dotenv call is not problematic for this test
    assert ags.load_api_key("dummy_env_path.env", let_load_dotenv_search=False) == "test_api_key_from_env"


def test_load_api_key_from_file(temp_env_file_with_key, monkeypatch):
    """Test API key is loaded from a .env file."""
    # Ensure os.getenv doesn't find it directly in env vars first
    monkeypatch.delenv(ags.API_KEY_ENV_VAR, raising=False)
    # The temp_env_file_with_key fixture already mocks is_file for its path
    # We need to ensure load_dotenv is called if the file exists
    mock_load_dotenv = mock.Mock()
    # Patch the load_dotenv function within the ags module (where it's imported)
    monkeypatch.setattr(ags, "load_dotenv", mock_load_dotenv)

    # Temporarily patch os.getenv to simulate load_dotenv's effect
    def mock_getenv_after_load(key):
        if key == ags.API_KEY_ENV_VAR:
            return "test_api_key_from_file"
        return os.environ.get(key)

    # Patch the os.getenv function within the ags module (where it's imported)
    monkeypatch.setattr(ags.os, "getenv", mock_getenv_after_load)

    # Call with let_load_dotenv_search=False to isolate the file loading part
    assert ags.load_api_key(str(temp_env_file_with_key), let_load_dotenv_search=False) == "test_api_key_from_file"
    # Now assert_called_once_with should pass
    mock_load_dotenv.assert_called_once_with(dotenv_path=str(temp_env_file_with_key), override=True)


def test_load_api_key_not_found(monkeypatch, caplog):
    """Test behavior when API key is not found in env or file."""
    caplog.set_level(logging.CRITICAL)  # Ensure CRITICAL messages are captured
    monkeypatch.delenv(ags.API_KEY_ENV_VAR, raising=False)
    monkeypatch.setattr(pathlib.Path, "is_file", lambda self: False)  # No .env file

    dummy_env_file_path = "dummy.env"
    assert ags.load_api_key(dummy_env_file_path, let_load_dotenv_search=False) is None
    # Corrected assertion to match the actual CRITICAL log message
    assert f"Error: API key not found in {dummy_env_file_path} environment variable" in caplog.text


# --- Tests for read_file_content & write_file_content ---


def test_read_file_content_success(tmp_path: pathlib.Path):
    """Test reading content from an existing file."""
    file_path = tmp_path / "test_read.txt"
    expected_content = "Hello, world!\nThis is a test."
    file_path.write_text(expected_content, encoding="utf-8")
    assert ags.read_file_content(str(file_path)) == expected_content


def test_read_file_content_not_found(tmp_path: pathlib.Path, caplog):
    """Test reading a non-existent file."""
    non_existent_file = tmp_path / "not_found.txt"
    assert ags.read_file_content(str(non_existent_file)) is None
    assert f"Error: File not found at '{non_existent_file}'" in caplog.text


def test_write_file_content_success(tmp_path: pathlib.Path):
    """Test writing content to a file."""
    file_path = tmp_path / "test_write.txt"
    content_to_write = "Content to be written."
    assert ags.write_file_content(str(file_path), content_to_write) is True
    assert file_path.read_text(encoding="utf-8") == content_to_write


# --- Tests for construct_llm_prompt ---


def test_construct_llm_prompt(sample_styleguide_content, sample_code_before_content):
    """Test the structure and content of the LLM prompt."""
    file_name = "sample_file.py"
    prompt = ags.construct_llm_prompt(sample_styleguide_content, sample_code_before_content, file_name)

    assert f"ORIGINAL CODE from '{file_name}':" in prompt
    assert sample_code_before_content in prompt
    assert "STYLE GUIDE:" in prompt
    assert sample_styleguide_content in prompt
    assert ags.MODIFIED_CODE_DELIMITER_START in prompt
    assert ags.EXPLANATIONS_DELIMITER_START in prompt
    assert "adhere (with minimal changes : don't change the code logic) to the rules" in prompt


# --- Tests for parse_llm_response ---


def test_parse_llm_response_with_changes(llm_response_changes_content):
    """Test parsing a response that includes code changes and explanations."""
    expected_code_from_llm_fixture = (
        llm_response_changes_content.split(ags.MODIFIED_CODE_DELIMITER_START)[1]
        .split(ags.MODIFIED_CODE_DELIMITER_END)[0]
        .strip()
    )
    expected_explanations = (
        llm_response_changes_content.split(ags.EXPLANATIONS_DELIMITER_START)[1]
        .split(ags.EXPLANATIONS_DELIMITER_END)[0]
        .strip()
    )

    modified_code, explanations = ags.parse_llm_response(llm_response_changes_content)
    assert modified_code == expected_code_from_llm_fixture
    assert explanations == expected_explanations


def test_parse_llm_response_no_changes(llm_response_no_changes_content):
    """Test parsing a response where AI reports no changes."""
    expected_code_from_llm_fixture = (
        llm_response_no_changes_content.split(ags.MODIFIED_CODE_DELIMITER_START)[1]
        .split(ags.MODIFIED_CODE_DELIMITER_END)[0]
        .strip()
    )
    expected_explanations = "No changes were necessary."

    modified_code, explanations = ags.parse_llm_response(llm_response_no_changes_content)
    assert modified_code == expected_code_from_llm_fixture
    assert explanations == expected_explanations


def test_parse_llm_response_malformed(llm_response_malformed_content, caplog):
    """Test parsing a malformed response."""
    caplog.set_level(logging.DEBUG)
    modified_code, explanations = ags.parse_llm_response(llm_response_malformed_content)
    assert modified_code == llm_response_malformed_content.strip()
    assert explanations is None
    assert "PARSER: Could not find explanation block delimiters" in caplog.text
    assert "PARSER: No delimiters found anywhere. Treating entire response as modified code." in caplog.text


# --- Tests for get_ai_suggestion (mocking the API call) ---
@mock.patch("coffee_maker.auto_gemini_styleguide.genai.GenerativeModel")
def test_get_ai_suggestion_success(mock_generative_model, llm_response_changes_content):
    """Test successful AI suggestion retrieval and parsing."""
    mock_model_instance = mock.MagicMock()
    mock_response = mock.MagicMock()
    mock_response.text = llm_response_changes_content
    mock_response.candidates = [mock.MagicMock()]
    mock_response.candidates[0].content.parts = [mock.MagicMock()]
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model.return_value = mock_model_instance

    expected_code = (
        llm_response_changes_content.split(ags.MODIFIED_CODE_DELIMITER_START)[1]
        .split(ags.MODIFIED_CODE_DELIMITER_END)[0]
        .strip()
    )
    expected_explanations = (
        llm_response_changes_content.split(ags.EXPLANATIONS_DELIMITER_START)[1]
        .split(ags.EXPLANATIONS_DELIMITER_END)[0]
        .strip()
    )

    modified_code, explanations = ags.get_ai_suggestion("fake_api_key", "gemini-pro", "dummy_prompt")
    assert modified_code == expected_code
    assert explanations == expected_explanations
    mock_generative_model.assert_called_once_with("gemini-pro")
    mock_model_instance.generate_content.assert_called_once()


@mock.patch("coffee_maker.auto_gemini_styleguide.genai.GenerativeModel")
def test_get_ai_suggestion_api_error(mock_generative_model, caplog):
    """Test handling of an API error during suggestion retrieval."""
    mock_model_instance = mock.MagicMock()
    mock_model_instance.generate_content.side_effect = google.api_core.exceptions.GoogleAPICallError(
        "API limit reached"
    )
    mock_generative_model.return_value = mock_model_instance
    caplog.set_level(logging.ERROR)
    modified_code, explanations = ags.get_ai_suggestion("fake_api_key", "gemini-pro", "dummy_prompt")
    assert modified_code is None
    assert explanations is None
    assert "Google API Call Error: None API limit reached" in caplog.text


@mock.patch("coffee_maker.auto_gemini_styleguide.genai.GenerativeModel")
def test_get_ai_suggestion_blocked_prompt(mock_generative_model, caplog):
    """Test handling of a BlockedPromptException."""
    mock_model_instance = mock.MagicMock()
    mock_model_instance.generate_content.side_effect = google.generativeai.types.BlockedPromptException(
        "Prompt blocked for safety"
    )
    mock_generative_model.return_value = mock_model_instance
    caplog.set_level(logging.ERROR)
    modified_code, explanations = ags.get_ai_suggestion("fake_api_key", "gemini-pro", "dummy_prompt")
    assert modified_code is None
    assert explanations is None
    assert "Gemini API Error: Prompt was blocked." in caplog.text


# --- Tests for generate_and_write_diff ---


def test_generate_and_write_diff_with_changes(
    tmp_path: pathlib.Path, sample_code_before_content, sample_code_after_content
):
    """Test diff file generation when code has changed."""
    target_file = tmp_path / "test_file.py"
    explanations = "Code was refactored for clarity."
    ags.generate_and_write_diff(sample_code_before_content, sample_code_after_content, str(target_file), explanations)
    diff_file_path = tmp_path / ".diff.test_file.py"
    assert diff_file_path.exists()
    diff_content = diff_file_path.read_text(encoding="utf-8")
    assert "--- a/test_file.py" in diff_content
    assert "+++ b/test_file.py" in diff_content
    assert explanations in diff_content
    assert "def hello(name):" in diff_content
    assert "def hello(name: str)" in diff_content


def test_generate_and_write_diff_no_code_changes(tmp_path: pathlib.Path, sample_code_before_content, caplog):
    """Test NO diff file is generated if code is identical, even with explanations."""
    target_file = tmp_path / "test_file_no_change.py"
    explanations = "No changes were necessary."
    caplog.set_level(logging.INFO)
    ags.generate_and_write_diff(sample_code_before_content, sample_code_before_content, str(target_file), explanations)
    diff_file_path = tmp_path / ".diff.test_file_no_change.py"
    assert not diff_file_path.exists()
    assert "Code content is identical to the original after stripping whitespace." in caplog.text
    assert f"Diff file '{diff_file_path}' will NOT be created" in caplog.text
    assert f"AI provided explanations for no code change:\n{explanations}" in caplog.text


def test_generate_and_write_diff_no_code_changes_no_explanations(
    tmp_path: pathlib.Path, sample_code_before_content, caplog
):
    """Test NO diff file is generated if code is identical and no explanations."""
    target_file = tmp_path / "test_file_no_change_no_expl.py"
    caplog.set_level(logging.INFO)
    ags.generate_and_write_diff(sample_code_before_content, sample_code_before_content, str(target_file), None)
    diff_file_path = tmp_path / ".diff.test_file_no_change_no_expl.py"
    assert not diff_file_path.exists()
    assert "Code content is identical to the original after stripping whitespace." in caplog.text
    assert "No explanations provided for identical code." in caplog.text


# --- Tests for main function (CLI workflow) ---


# Patch targets should now be relative to the 'coffee_maker.auto_gemini_styleguide' module
@mock.patch("coffee_maker.auto_gemini_styleguide.get_ai_suggestion")
@mock.patch("coffee_maker.auto_gemini_styleguide.write_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.read_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.load_api_key")
@mock.patch("argparse.ArgumentParser.parse_args")
def test_main_workflow_with_changes(
    mock_parse_args,
    mock_load_api_key,
    mock_read_content,
    mock_write_content,
    mock_get_ai_suggestion,
    tmp_path: pathlib.Path,
    sample_code_before_content,
    sample_code_after_content,
    sample_styleguide_content,
    caplog,
):
    """Test the main workflow when AI suggests changes."""
    target_file_path_obj = tmp_path / "main_test_target.py"
    target_file_path_obj.write_text(sample_code_before_content)
    dummy_styleguide_path = tmp_path / ".gemini" / "styleguide.md"
    dummy_styleguide_path.parent.mkdir(exist_ok=True)
    dummy_styleguide_path.write_text(sample_styleguide_content)

    mock_parse_args.return_value = argparse.Namespace(
        target_file_path=str(target_file_path_obj),
        styleguide=str(dummy_styleguide_path),
        envfile=ags.DEFAULT_ENV_FILE_PATH,
        model="gemini-1.5-flash-latest",
        backup=False,
        no_modify=False,
        debug=False,
    )
    mock_load_api_key.return_value = "fake_api_key_for_main"

    def side_effect_read_content(path_str):
        if path_str == str(target_file_path_obj):
            return sample_code_before_content
        elif path_str == str(dummy_styleguide_path):
            return sample_styleguide_content
        raise FileNotFoundError(f"Mock read_file_content did not expect path: {path_str}")

    mock_read_content.side_effect = side_effect_read_content
    mock_get_ai_suggestion.return_value = (sample_code_after_content, "AI made some changes.")
    caplog.set_level(logging.INFO)
    return_code = ags.main()
    assert return_code == 0
    mock_get_ai_suggestion.assert_called_once()
    write_target_call = None
    for call_args in mock_write_content.call_args_list:
        if call_args.args[0] == str(target_file_path_obj):
            write_target_call = call_args
            break
    assert write_target_call is not None, "write_file_content was not called for the target file"
    assert write_target_call.args[1] == sample_code_after_content
    diff_file_path = tmp_path / f".diff.{target_file_path_obj.name}"
    assert diff_file_path.exists()
    assert "Original file successfully updated with AI suggestions." in caplog.text


@mock.patch("coffee_maker.auto_gemini_styleguide.get_ai_suggestion")
@mock.patch("coffee_maker.auto_gemini_styleguide.write_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.read_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.load_api_key")
@mock.patch("argparse.ArgumentParser.parse_args")
def test_main_workflow_no_changes(
    mock_parse_args,
    mock_load_api_key,
    mock_read_content,
    mock_write_content,
    mock_get_ai_suggestion,
    tmp_path: pathlib.Path,
    sample_code_before_content,
    sample_styleguide_content,
    caplog,
):
    """Test the main workflow when AI suggests no changes."""
    target_file_path_obj = tmp_path / "main_test_no_changes.py"
    target_file_path_obj.write_text(sample_code_before_content)
    dummy_styleguide_path = tmp_path / ".gemini" / "styleguide.md"
    dummy_styleguide_path.parent.mkdir(exist_ok=True)
    dummy_styleguide_path.write_text(sample_styleguide_content)

    mock_parse_args.return_value = argparse.Namespace(
        target_file_path=str(target_file_path_obj),
        styleguide=str(dummy_styleguide_path),
        envfile=ags.DEFAULT_ENV_FILE_PATH,
        model="gemini-1.5-flash-latest",
        backup=False,
        no_modify=False,
        debug=False,
    )
    mock_load_api_key.return_value = "fake_api_key_for_main"

    def side_effect_read_content(path_str):
        if path_str == str(target_file_path_obj):
            return sample_code_before_content
        elif path_str == str(dummy_styleguide_path):
            return sample_styleguide_content
        raise FileNotFoundError(f"Mock read_file_content did not expect path: {path_str}")

    mock_read_content.side_effect = side_effect_read_content
    mock_get_ai_suggestion.return_value = (sample_code_before_content, "No changes were necessary.")
    caplog.set_level(logging.INFO)
    return_code = ags.main()
    assert return_code == 0
    mock_get_ai_suggestion.assert_called_once()
    for call_args in mock_write_content.call_args_list:
        assert call_args.args[0] != str(
            target_file_path_obj
        ), "write_file_content was called for target file unexpectedly"
    diff_file_path = tmp_path / f".diff.{target_file_path_obj.name}"
    assert not diff_file_path.exists()
    assert "AI returned identical code content. No changes made to the original file based on code." in caplog.text


@mock.patch("coffee_maker.auto_gemini_styleguide.get_ai_suggestion")
@mock.patch("coffee_maker.auto_gemini_styleguide.write_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.read_file_content")
@mock.patch("coffee_maker.auto_gemini_styleguide.load_api_key")
@mock.patch("argparse.ArgumentParser.parse_args")
def test_main_workflow_no_modify_flag(
    mock_parse_args,
    mock_load_api_key,
    mock_read_content,
    mock_write_content,
    mock_get_ai_suggestion,
    tmp_path: pathlib.Path,
    sample_code_before_content,
    sample_code_after_content,
    sample_styleguide_content,
    caplog,
):
    """Test the main workflow with the --no-modify flag."""
    target_file_path_obj = tmp_path / "main_test_no_modify.py"
    target_file_path_obj.write_text(sample_code_before_content)
    dummy_styleguide_path = tmp_path / ".gemini" / "styleguide.md"
    dummy_styleguide_path.parent.mkdir(exist_ok=True)
    dummy_styleguide_path.write_text(sample_styleguide_content)

    mock_parse_args.return_value = argparse.Namespace(
        target_file_path=str(target_file_path_obj),
        styleguide=str(dummy_styleguide_path),
        envfile=ags.DEFAULT_ENV_FILE_PATH,
        model="gemini-1.5-flash-latest",
        backup=False,
        no_modify=True,
        debug=False,
    )
    mock_load_api_key.return_value = "fake_api_key_for_main"

    def side_effect_read_content(path_str):
        if path_str == str(target_file_path_obj):
            return sample_code_before_content
        elif path_str == str(dummy_styleguide_path):
            return sample_styleguide_content
        raise FileNotFoundError(f"Mock read_file_content did not expect path: {path_str}")

    mock_read_content.side_effect = side_effect_read_content
    mock_get_ai_suggestion.return_value = (sample_code_after_content, "AI made some changes.")
    caplog.set_level(logging.INFO)
    return_code = ags.main()
    assert return_code == 0
    mock_get_ai_suggestion.assert_called_once()
    for call_args in mock_write_content.call_args_list:
        assert call_args.args[0] != str(
            target_file_path_obj
        ), "write_file_content was called for target file unexpectedly with --no-modify"
    diff_file_path = tmp_path / f".diff.{target_file_path_obj.name}"
    assert diff_file_path.exists()
    assert f"Original file '{str(target_file_path_obj)}' was NOT modified due to --no-modify flag." in caplog.text
