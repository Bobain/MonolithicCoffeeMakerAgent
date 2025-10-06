"""Helpers for wiring LangChain chat models with Langfuse instrumentation."""

import logging
import os
import datetime

import langfuse

from coffee_maker.langchain_observe.utils import get_callers_modules

logger = logging.getLogger(__name__)
SUPPORTED_PROVIDERS = dict()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    SUPPORTED_PROVIDERS.update({"gemini": (ChatGoogleGenerativeAI, "GEMINI_API_KEY", "gemini-2.5-pro")})
except:
    logger.warning("langchain_google_genai not installed. will not use google")
try:
    from langchain_openai import ChatOpenAI

    SUPPORTED_PROVIDERS.update({"openai": (ChatOpenAI, "OPENAI_API_KEY", "gpt-5-codex")})
except:
    logger.warning("langchain_openai not installed. will not use openai")
try:
    from langchain_anthropic import ChatAnthropic

    SUPPORTED_PROVIDERS.update({"anthropic": (ChatAnthropic, "ANTHROPIC_API_KEY", "claude-opus-4-20250514")})
except:
    logger.warning("langchain_anthropic not installed. will not use anthropic")

DEFAULT_PROVIDER = list(SUPPORTED_PROVIDERS.keys())[0]


def get_chat_llm(langfuse_client: langfuse.Langfuse = None, provider: str = "gemini", model: str = None):
    if provider is None:
        provider = DEFAULT_PROVIDER
        assert model is None, f"Please input a provider when you specify a specific model: {model}"
    if model is None:
        Llm, api_key, model = SUPPORTED_PROVIDERS[provider]
    else:
        Llm, api_key, _ = SUPPORTED_PROVIDERS[provider]
    if langfuse_client is None:
        langfuse_client = langfuse.get_client()
    if provider in SUPPORTED_PROVIDERS.keys():
        if not os.getenv(api_key):
            logger.warning(
                f"ENVIRONMENT VARIABLE {api_key} not set, you asked {provider} with model {model} but it may not work"
            )
        llm = Llm(model=model)
        langfuse_client.update_current_trace(
            metadata={
                f"llm_config_{provider}_{model}_{datetime.datetime.now().isoformat()}": dict(
                    caller="/n".join(get_callers_modules()), provider=provider, model=model
                )
            }
        )
        return llm
    else:
        raise ValueError(f"Unsupported provider: {provider}")
