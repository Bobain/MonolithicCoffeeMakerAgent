"""Helpers for wiring LangChain chat models with Langfuse instrumentation."""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable, Mapping, Optional, Tuple

from langchain_core.messages import AIMessage
from langfuse import observe

from coffee_maker.langchain_observe.llm import get_chat_llm

logger = logging.getLogger(__name__)


def instrument_llm(llm_instance: Any, *, methods: Iterable[str] = ("invoke", "ainvoke")) -> Any:
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


def resolve_gemini_api_key() -> str:
    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"):
        key = os.getenv(env_name)
        if key:
            os.environ.setdefault("GEMINI_API_KEY", key)
            return key

    raise RuntimeError("Gemini API key missing: set GEMINI_API_KEY, GOOGLE_API_KEY, or COFFEE_MAKER_GEMINI_API_KEY.")


def _build_stub_llm(provider: str, model: Optional[str], error: Exception) -> Any:
    message = f"Stubbed response: failed to initialise provider '{provider}' with model '{model}'. " f"Details: {error}"

    class _StubChatModel:
        def __init__(self, description: str) -> None:
            self.description = description
            self.model = model
            self.provider = provider

        def invoke(self, *_: Any, **__: Any) -> AIMessage:
            return AIMessage(content=self.description)

        async def ainvoke(self, *_: Any, **__: Any) -> AIMessage:
            return AIMessage(content=self.description)

    return _StubChatModel(message)


def _build_llm(provider: str = None, model=None, **kwargs: Any):
    if not isinstance(model, str):
        model = get_chat_llm(provider=provider, model=model, **kwargs)
    return model


def configure_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    *,
    strict: bool = True,
    default_models: Optional[Mapping[str, Optional[str]]] = None,
    methods: Iterable[str] = ("invoke", "ainvoke"),
    **kwargs: Any,
) -> Tuple[Any, str, Optional[str]]:

    try:
        candidate_llm = _build_llm(provider, model, **kwargs)
    except Exception as exc:
        if strict:
            raise
        logger.warning(
            "Falling back to stubbed LLM for provider '%s' and model '%s': %s",
            provider,
            model,
            exc,
        )
        candidate_llm = _build_stub_llm(provider, model, exc)

    instrumented = instrument_llm(candidate_llm, methods=methods)
    return instrumented, provider, model
