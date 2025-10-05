"""Utility hcoffee_maker/code_formatter/parser.pyelpers for the code formatter package."""

import logging
from typing import Dict, List, Tuple
from coffee_maker.code_formatter.agents import (
    MODIFIED_CODE_DELIMITER_START,
    MODIFIED_CODE_DELIMITER_END,
    EXPLANATIONS_DELIMITER_START,
    EXPLANATIONS_DELIMITER_END,
)

LOGGER = logging.getLogger(__name__)


def _extract_line_span(text: str) -> Tuple[int | None, int | None]:
    """Return the start/end line numbers found in *text* if present."""

    text = text.strip()
    if not text:
        return None, None

    lowered = text.lower()
    if "line" not in lowered:
        return None, None

    start = end = None
    tokens = text.replace("Line", "line").split()
    for idx, token in enumerate(tokens):
        if token.lower() == "line" and idx + 1 < len(tokens):
            candidate = tokens[idx + 1].rstrip(":")
            if "-" in candidate:
                left, right = candidate.split("-", 1)
                if left.lstrip("N").isdigit() and right.lstrip("N").isdigit():
                    start = int(left.lstrip("N"))
                    end = int(right.lstrip("N"))
                    break
            else:
                cleaned = candidate.lstrip("N")
                if cleaned.isdigit():
                    start = int(cleaned)
                    end = start
                    break
    return start, end


def parse_reformatted_output(text: str) -> List[Dict[str, object]]:
    """Parse formatter output into a list of suggestion dictionaries."""

    results: List[Dict[str, object]] = []
    lines = text.splitlines()
    total = len(lines)
    idx = 0

    LOGGER.debug("Parsing reformatted output with %s lines", total)

    while idx < total:
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue

        if not line.startswith(MODIFIED_CODE_DELIMITER_START):
            idx += 1
            continue

        start_line, _ = _extract_line_span(line[len(MODIFIED_CODE_DELIMITER_START) :])
        idx += 1

        if start_line is None and idx < total:
            extra_line = lines[idx].strip()
            potential_start, _ = _extract_line_span(extra_line)
            if potential_start is not None:
                start_line = potential_start
                idx += 1

        code_lines = []
        end_line = None
        while idx < total:
            current = lines[idx]
            stripped = current.strip()
            if stripped.startswith(MODIFIED_CODE_DELIMITER_END):
                _, possible_end = _extract_line_span(stripped[len(MODIFIED_CODE_DELIMITER_END) :])
                if possible_end is not None:
                    end_line = possible_end
                idx += 1
                break
            code_lines.append(current)
            idx += 1

        if end_line is None and start_line is not None:
            end_line = start_line

        while idx < total and not lines[idx].strip():
            idx += 1

        if idx >= total or not lines[idx].strip().startswith(EXPLANATIONS_DELIMITER_START):
            LOGGER.debug("Missing explanations block after modified code; stopping parse")
            break

        explanation_header = lines[idx].strip()
        exp_start, exp_end = _extract_line_span(explanation_header[len(EXPLANATIONS_DELIMITER_START) :])
        idx += 1

        explanations = []
        while idx < total:
            stripped = lines[idx].strip()
            if stripped.startswith(EXPLANATIONS_DELIMITER_END):
                idx += 1
                break
            explanations.append(lines[idx])
            idx += 1

        comment_text = "\n".join(explanations).strip()
        comment_start = comment_end = None
        if comment_text:
            first_line = comment_text.splitlines()[0]
            comment_start, comment_end = _extract_line_span(first_line)

        start_line = comment_start or exp_start or start_line
        end_line = comment_end or exp_end or end_line or start_line

        entry = {
            "start_line": start_line,
            "end_line": end_line,
            "suggestion_body": "\n".join(code_lines).rstrip("\n"),
            "comment_text": comment_text,
        }
        LOGGER.debug("Parsed block: start=%s end=%s suggestion_lines=%s", start_line, end_line, len(code_lines))
        results.append(entry)

    LOGGER.debug("Finished parsing; extracted %s suggestion blocks", len(results))
    return results
