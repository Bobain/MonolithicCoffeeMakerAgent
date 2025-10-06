"""LangChain agent helpers for the code formatter domain."""

import argparse
import logging
import textwrap
from typing import Any, Dict, Optional, Sequence

from dotenv import load_dotenv

load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langfuse.langchain import CallbackHandler
import langfuse

from coffee_maker.langchain_observe.llm import get_chat_llm, SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)
default_llm = get_chat_llm()


def create_langchain_code_formatter_agent(
    langfuse_client: langfuse.Langfuse, *, llm_override: Optional[Any] = None
) -> Dict[str, Any]:
    """Return the LangChain configuration for the formatter agent."""
    langfuse_callback_handler = CallbackHandler()
    try:
        prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
        prompt = ChatPromptTemplate.from_template(
            prompt.get_langchain_prompt(),
            metadata={"langfuse_prompt": prompt},
        )
    except Exception as exc:  # pragma: no cover - surfaced to callers/tests
        logger.exception("Failed to fetch formatter prompts", exc_info=exc)
        raise

    llm = llm_override or get_chat_llm()

    def get_result_from_llm(code_to_reformat: str):
        chain = prompt | llm
        llm_result = chain.invoke(
            input=dict(code_to_modify=code_to_reformat), config={"callbacks": [langfuse_callback_handler]}
        )
        return llm_result.content

    return dict(
        role="Senior Software Engineer: python code formatter",
        goal="",
        backstory="",
        prompt=prompt,
        llm=llm,
        tools=(),
        get_result_from_llm=get_result_from_llm,
    )


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

    langfuse_client = langfuse.get_client()
    with langfuse_client.start_as_current_span(name="test-code_formatter_agent") as root_span:
        llm = get_chat_llm(
            langfuse_client=langfuse_client,
            provider=args.provider,
            model=args.model,
        )

        agent_config = create_langchain_code_formatter_agent(langfuse_client, llm_override=llm)

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

        content = agent_config["get_result_from_llm"](sample_code)

        print("=== Demo input (non compliant) ===")
        print(sample_code)
        print()
        print("=== Formatter agent output ===")

        import json

        print(json.dumps(json.loads(content)))
        return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
