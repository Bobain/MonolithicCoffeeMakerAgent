"""Helpers for wiring LangChain chat models with Langfuse instrumentation."""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import observe

LOGGER = logging.getLogger(__name__)

SUPPORTED_PROVIDERS: Sequence[str] = ("gemini", "openai")
_DEFAULT_PROVIDER_ENV = "COFFEE_MAKER_LLM_PROVIDER"
_DEFAULT_MODEL_ENV = "COFFEE_MAKER_LLM_MODEL"
_DEFAULT_MODELS: Mapping[str, Optional[str]] = {"gemini": "gemini-2.0-flash-lite"}


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


def _build_gemini_llm(model: Optional[str], **kwargs: Any) -> ChatGoogleGenerativeAI:
    api_key = resolve_gemini_api_key()
    target_model = model or _DEFAULT_MODELS.get("gemini")
    return ChatGoogleGenerativeAI(
        model=target_model,
        google_api_key=api_key,
        convert_system_message_to_human=True,
        **kwargs,
    )


def _build_openai_llm(model: Optional[str], **kwargs: Any) -> Any:
    try:
        from langchain_openai import ChatOpenAI  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install 'langchain-openai' to use the OpenAI provider.") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required for the OpenAI provider.")

    target_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=target_model, api_key=api_key, **kwargs)


def _build_llm(provider: str, model: Optional[str], **kwargs: Any) -> Any:
    provider_key = provider.lower()
    if provider_key == "gemini":
        return _build_gemini_llm(model, **kwargs)
    if provider_key == "openai":
        return _build_openai_llm(model, **kwargs)

    raise ValueError(f"Unsupported LLM provider '{provider}'. Supported providers: {SUPPORTED_PROVIDERS}.")


def _default_provider() -> str:
    return os.getenv(_DEFAULT_PROVIDER_ENV, "gemini")


def _default_model(provider: str, overrides: Optional[Mapping[str, Optional[str]]] = None) -> Optional[str]:
    configured = os.getenv(_DEFAULT_MODEL_ENV)
    if configured:
        return configured

    if overrides and provider in overrides:
        return overrides[provider]

    return _DEFAULT_MODELS.get(provider)


def configure_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    *,
    strict: bool = True,
    default_models: Optional[Mapping[str, Optional[str]]] = None,
    methods: Iterable[str] = ("invoke", "ainvoke"),
    **kwargs: Any,
) -> Tuple[Any, str, Optional[str]]:
    resolved_provider = (provider or _default_provider()).lower()
    resolved_model = model or _default_model(resolved_provider, default_models)

    try:
        candidate_llm = _build_llm(resolved_provider, resolved_model, **kwargs)
    except Exception as exc:
        if strict:
            raise
        LOGGER.warning(
            "Falling back to stubbed LLM for provider '%s' and model '%s': %s",
            resolved_provider,
            resolved_model,
            exc,
        )
        candidate_llm = _build_stub_llm(resolved_provider, resolved_model, exc)

    instrumented = instrument_llm(candidate_llm, methods=methods)
    return instrumented, resolved_provider, resolved_model


__all__ = [
    "SUPPORTED_PROVIDERS",
    "configure_llm",
    "instrument_llm",
    "resolve_gemini_api_key",
]
