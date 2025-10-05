"""LangChain agent helpers for the code formatter domain."""

import argparse
import logging
import sys
import textwrap
from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langfuse import Langfuse, observe

from coffee_maker.langchain_observe.agents_wrapper import SUPPORTED_PROVIDERS, configure_llm, resolve_gemini_api_key

load_dotenv()

LOGGER = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.0-flash-lite"
DEFAULT_MODELS = {"gemini": _GEMINI_MODEL}

MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"

_resolve_gemini_api_key = resolve_gemini_api_key


def _initialise_llm(*, strict: bool = False) -> Tuple[Any, str, Optional[str]]:
    return observe(configure_llm(strict=strict, default_models=DEFAULT_MODELS))


llm, llm_provider, llm_model = _initialise_llm(strict=False)


def _escape_braces(value: str) -> str:
    """Escape braces so ChatPromptTemplate does not treat them as placeholders."""

    return value.replace("{", "{{").replace("}", "}}")


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
        goal_prompt = langfuse_client.get_prompt("refactor_agent/goal_prompt")
        backstory_prompt = langfuse_client.get_prompt("refactor_agent/backstory_prompt")
    except Exception as exc:  # pragma: no cover - surfaced to callers/tests
        LOGGER.exception("Failed to fetch formatter prompts", exc_info=exc)
        raise

    goal_raw = getattr(goal_prompt, "prompt", str(goal_prompt))
    backstory_raw = getattr(backstory_prompt, "prompt", str(backstory_prompt))

    goal = _escape_braces(goal_raw)
    backstory = _escape_braces(backstory_raw)

    system_message = (
        f"You are a meticulous Senior Software Engineer.\\n\\n" f"Goal: {goal}\\n\\n" f"Backstory: {backstory}"
    )
    prompt = _build_prompt(system_message)

    return _build_agent_config(
        role="Senior Software Engineer: python code formatter",
        goal=goal_raw,
        backstory=backstory_raw,
        prompt=prompt,
        llm_override=llm_override,
        tools=(),
    )


class _DemoLangfuseClient:
    """Minimal Langfuse stand-in for local demonstrations."""

    def __init__(self) -> None:
        self._prompts = {
            "refactor_agent/goal_prompt": "Update code to comply with our Coffee Maker style guide.",
            "refactor_agent/backstory_prompt": (
                "You care deeply about clarity, type hints, and deterministic formatting."
            ),
        }

    def get_prompt(self, name: str) -> SimpleNamespace:
        try:
            text = self._prompts[name]
        except KeyError as exc:  # pragma: no cover - defensive demo guard
            raise KeyError(f"Demo prompt '{name}' not configured") from exc
        return SimpleNamespace(prompt=text)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run a small end-to-end example with hard-coded input."""

    parser = argparse.ArgumentParser(description="Run the formatter agent demo")
    parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        help="LLM provider to use (defaults to environment or gemini)",
    )
    parser.add_argument(
        "--model",
        help="Model identifier to use. Defaults to provider-specific configuration.",
    )
    parser.add_argument(
        "--file-path",
        default="demo/non_compliant.py",
        help="Logical path attached to the demo file contents.",
    )
    args = parser.parse_args(argv)

    try:
        new_llm, new_provider, new_model = configure_llm(
            provider=args.provider,
            model=args.model,
            strict=True,
            default_models=DEFAULT_MODELS,
        )
    except Exception as exc:  # pragma: no cover - exercised in manual usage
        LOGGER.error("Unable to initialise the LLM: %s", exc)
        print(f"Formatter demo aborted. Configuration error: {exc}", file=sys.stderr)
        return 1

    globals()["llm"], globals()["llm_provider"], globals()["llm_model"] = new_llm, new_provider, new_model

    demo_client = _DemoLangfuseClient()
    agent_config = create_langchain_code_formatter_agent(demo_client)
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

    payload = {"file_path": args.file_path, "file_content": sample_code}

    print("=== Demo input (non compliant) ===")
    print(sample_code)
    print()
    print("=== Formatter agent output ===")

    try:
        response = chain.invoke(payload)
    except Exception as exc:  # pragma: no cover - manual execution path
        LOGGER.error("Formatter agent failed: %s", exc, exc_info=True)
        print(f"Formatter agent failed to run: {exc}", file=sys.stderr)
        return 1

    content = getattr(response, "content", response)
    print(content)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
