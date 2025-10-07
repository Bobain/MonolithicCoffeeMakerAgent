"""LangChain agent helpers for the code formatter domain."""

from __future__ import annotations

import argparse
import logging
import sys
import json
import textwrap
from typing import Any, Dict, Optional, Sequence, Tuple

import langfuse
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langfuse import Langfuse

from coffee_maker.langchain_observe.agents import configure_llm

load_dotenv()

logger = logging.getLogger(__name__)


def _initialise_llm(*, strict: bool = False) -> Tuple[Any, str, Optional[str]]:
    return configure_llm(strict=strict)


llm, llm_provider, llm_model = _initialise_llm(strict=False)


def _escape_braces(value: str) -> str:
    """Escape braces so ChatPromptTemplate does not treat them as placeholders."""

    return value.replace("{", "{{").replace("}", "}}")


def _extract_prompt_text(prompt_obj: Any) -> str:
    for attr in ("prompt", "text", "template"):
        value = getattr(prompt_obj, attr, None)
        if isinstance(value, str):
            return value
    return str(prompt_obj)


def _build_prompt(system_message: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", "File path: {file_path}\\n\\nFile content:\\n{file_content}"),
        ]
    )


def _build_agent_config(
    *,
    role: str,
    goal: str,
    backstory: str,
    prompt: ChatPromptTemplate,
    llm_override: Optional[Any] = None,
    tools: Sequence[Any] = (),
    verbose: bool = True,
    allow_delegation: bool = False,
) -> Dict[str, Any]:
    return {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "prompt": prompt,
        "llm": llm_override or llm,
        "tools": tuple(tools),
        "verbose": verbose,
        "allow_delegation": allow_delegation,
    }


def create_langchain_code_formatter_agent(
    langfuse_client: Langfuse, *, llm_override: Optional[Any] = None
) -> Dict[str, Any]:
    """Return the LangChain configuration for the formatter agent."""

    try:
        main_prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as exc:  # pragma: no cover - surfaced to callers/tests
        logger.exception("Failed to fetch formatter prompts", exc_info=exc)
        raise

    main_prompt_text = _extract_prompt_text(main_prompt)
    goal_raw = _extract_prompt_text(goal_prompt)
    backstory_raw = _extract_prompt_text(backstory_prompt)

    # Use the main prompt which contains full instructions for JSON output
    system_message = _escape_braces(main_prompt_text)

    # Build prompt with placeholders for file_path and code_to_modify
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", ""),  # Empty user message since system prompt has all instructions
        ]
    )

    # Override the template to use the placeholders from Langfuse
    prompt = ChatPromptTemplate.from_template(system_message)

    llm_instance = llm_override or llm

    def _invoke_formatter(file_content: str, file_path: str) -> str:
        chain = prompt | llm_instance
        # Use variable names matching the Langfuse prompt template
        response = chain.invoke({"file_path": file_path, "code_to_modify": file_content})
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _parse_formatter_output(raw_output: str) -> list[dict[str, Any]]:
        """Parse LLM output, handling markdown code blocks and whitespace.

        Args:
            raw_output: Raw string output from the LLM

        Returns:
            List of dictionaries containing code suggestions

        Raises:
            json.JSONDecodeError: If the content is not valid JSON
        """
        content = extract_brackets(raw_output)
        # Handle empty content
        if not content:
            return []

        try:
            result = json.loads(content)
            # Ensure result is a list
            if not isinstance(result, list):
                assert isinstance(result, dict), "Expected dictionnary or list of dictionaries"
                result = [result]
            return result
        except json.JSONDecodeError as exc:
            logger.critical(f"Could not parse JSON output. Error: {exc}\n" f"Raw output : {raw_output}")
            raise

    def get_result_from_llm(file_content: str, file_path: str) -> str:
        return _invoke_formatter(file_content, file_path)

    def get_list_of_dict_from_llm(
        file_content: str, file_path: str, *, skip_empty_files: bool = True
    ) -> list[dict[str, Any]]:
        if skip_empty_files and not file_content.strip():
            return []
        raw_output = _invoke_formatter(file_content, file_path)
        return _parse_formatter_output(raw_output)

    agent = _build_agent_config(
        role="Senior Software Engineer: python code formatter",
        goal=goal_raw,
        backstory=backstory_raw,
        prompt=prompt,
        llm_override=llm_override,
        tools=(),
    )

    agent["get_result_from_llm"] = get_result_from_llm
    agent["get_list_of_dict_from_llm"] = get_list_of_dict_from_llm

    return agent


def extract_brackets(s: str):
    # Remove any char surrounding the json list of dict
    first_open = min((i for i in [s.find("["), s.find("{")] if i != -1), default=-1)
    last_close = max((i for i in [s.rfind("]"), s.rfind("}")] if i != -1), default=-1)

    if first_open == -1 or last_close == -1:
        return ""

    return s[first_open : last_close + 1]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run a small end-to-end example with hard-coded input."""

    parser = argparse.ArgumentParser(description="Run the formatter agent demo")
    parser.add_argument(
        "--file-path",
        default="demo/non_compliant.py",
        help="Logical path attached to the demo file contents.",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider (e.g., anthropic, openai, gemini). Uses default if not specified.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model name. Uses provider default if not specified.",
    )
    args = parser.parse_args(argv)
    langfuse_client = langfuse.get_client()
    try:
        new_llm, new_provider, new_model = configure_llm(
            provider=args.provider,
            model=args.model,
            strict=True,
        )
    except Exception as exc:  # pragma: no cover - exercised in manual usage
        logger.error("Unable to initialise the LLM: %s", exc)
        print(f"Formatter demo aborted. Configuration error: {exc}", file=sys.stderr)
        return 1

    globals()["llm"], globals()["llm_provider"], globals()["llm_model"] = new_llm, new_provider, new_model

    agent_config = create_langchain_code_formatter_agent(langfuse_client=langfuse_client, llm_override=new_llm)

    chain = agent_config["prompt"] | agent_config["llm"]

    sample_code = textwrap.dedent(
        """
        import math


        def   calculateDistance(x1,y1,x2,y2):
            dx = x2-x1
            dy = y2-y1
            distance =   math.sqrt(dx*dx + dy*dy)
            print('result:',distance)
            return distance
        """
    ).strip()

    payload = {"file_path": args.file_path, "code_to_modify": sample_code}

    print("=== Demo input (non compliant) ===")
    print(sample_code)
    print()
    print("=== Formatter agent output ===")

    try:
        response = chain.invoke(payload)
    except Exception as exc:  # pragma: no cover - manual execution path
        logger.error("Formatter agent failed: %s", exc, exc_info=True)
        print(f"Formatter agent failed to run: {exc}", file=sys.stderr)
        return 1

    content = getattr(response, "content", response)
    print(content)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
