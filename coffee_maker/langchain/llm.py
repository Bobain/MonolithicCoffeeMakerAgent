"""Helpers to instrument LangChain components with Langfuse observability."""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Optional, Sequence

from langfuse import observe
from langchain.chat_models import init_chat_model

LOGGER = logging.getLogger(__name__)

SUPPORTED_PROVIDERS: Sequence[str] = ("gemini", "openai")
LANGCHAIN_PROVIDERS = dict(gemini="google_genai")
_DEFAULT_PROVIDER_ENV = "COFFEE_MAKER_LLM_PROVIDER"
_DEFAULT_MODEL_ENV = "COFFEE_MAKER_LLM_MODEL"
_DEFAULT_MODELS: Mapping[str, Optional[str]] = {"gemini": "gemini-2.0-flash-lite"}


def get_chat_llm(llm_provider: str = "gemini", llm_model: str = "gemini-2.5-flash"):
    return init_chat_model(llm_model, model_provider=LANGCHAIN_PROVIDERS.get(llm_provider, llm_provider))


# still useful?
def instrument_llm(llm_instance: Any, *, methods: Iterable[str] = ("invoke", "ainvoke")) -> Any:
    """Ensure the provided LLM exposes Langfuse spans on standard call methods."""

    if getattr(llm_instance, "_langfuse_instrumented", False):
        return llm_instance

    cls = llm_instance.__class__
    already_instrumented = set(getattr(cls, "_langfuse_instrumented_methods", set()))

    for method_name in methods:
        if method_name in already_instrumented:
            continue

        func = getattr(cls, method_name, None)
        if func is None or not callable(func):
            continue

        wrapped = observe(as_type="generation")(func)
        setattr(cls, method_name, wrapped)
        already_instrumented.add(method_name)

    setattr(cls, "_langfuse_instrumented_methods", already_instrumented)
    setattr(llm_instance, "_langfuse_instrumented", True)
    return llm_instance
