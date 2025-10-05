"""Tests for coffee_maker.code_formatter.utils."""

from coffee_maker.code_formatter.utils import (
    EXPLANATIONS_DELIMITER_END,
    EXPLANATIONS_DELIMITER_START,
    MODIFIED_CODE_DELIMITER_END,
    MODIFIED_CODE_DELIMITER_START,
    parse_reformatted_output,
)


def _wrap(blocks):
    return "\n".join(blocks)


def test_parse_single_block():
    text = _wrap(
        [
            f"{MODIFIED_CODE_DELIMITER_START} Line 10",
            "print('hello')",
            f"{MODIFIED_CODE_DELIMITER_END} Line 11",
            EXPLANATIONS_DELIMITER_START,
            "Line 10-11: Added print for debugging",
            EXPLANATIONS_DELIMITER_END,
        ]
    )

    result = parse_reformatted_output(text)

    assert len(result) == 1
    block = result[0]
    assert block["start_line"] == 10
    assert block["end_line"] == 11
    assert block["suggestion_body"] == "print('hello')"
    assert "Added print" in block["comment_text"]


def test_parse_block_without_inline_line_numbers():
    text = _wrap(
        [
            MODIFIED_CODE_DELIMITER_START,
            "Line 42",
            "value = compute()",
            MODIFIED_CODE_DELIMITER_END,
            EXPLANATIONS_DELIMITER_START,
            "Line 42-42: Use helper function",
            EXPLANATIONS_DELIMITER_END,
        ]
    )

    result = parse_reformatted_output(text)

    assert len(result) == 1
    block = result[0]
    assert block["start_line"] == 42
    assert block["end_line"] == 42
    assert block["suggestion_body"].strip() == "value = compute()"
