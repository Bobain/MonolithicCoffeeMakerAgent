"""Helpers for wiring LangChain chat models with Langfuse instrumentation."""

# TODO : add handling of quotas :
# 2025-10-06 12:23:28 - langchain_google_genai.chat_models - WARNING - Retrying langchain_google_genai.chat_models._chat_with_retry.<locals>._chat_with_retry in 16.0 seconds as it raised ResourceExhausted: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits.
# * Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 2
# Please retry in 31.940768649s. [violations {
#   quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
#   quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
#   quota_dimensions {
#     key: "model"
#     value: "gemini-2.5-pro"
#   }
#   quota_dimensions {
#     key: "location"
import logging
import os
import datetime
from dotenv import load_dotenv

load_dotenv()
import langfuse

from coffee_maker.langchain_observe.utils import get_callers_modules

logger = logging.getLogger(__name__)
SUPPORTED_PROVIDERS = dict()
__DEFAULT_PROVIDER = "gemini"

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    SUPPORTED_PROVIDERS.update(
        {"gemini": (ChatGoogleGenerativeAI, "GEMINI_API_KEY", "gemini-2.5-pro", {"max_tokens": 8192})}
    )
except:
    logger.warning("langchain_google_genai not installed. will not use google")
try:
    from langchain_openai import ChatOpenAI

    SUPPORTED_PROVIDERS.update({"openai": (ChatOpenAI, "OPENAI_API_KEY", "gpt-5-codex", {"max_tokens": 4096})})
except:
    logger.warning("langchain_openai not installed. will not use openai")
try:
    from langchain_anthropic import ChatAnthropic

    SUPPORTED_PROVIDERS.update(
        {"anthropic": (ChatAnthropic, "ANTHROPIC_API_KEY", "claude-opus-4-20250514", {"max_tokens": 8192})}
    )
except:
    logger.warning("langchain_anthropic not installed. will not use anthropic")


default_provider = (
    __DEFAULT_PROVIDER if __DEFAULT_PROVIDER in SUPPORTED_PROVIDERS.keys() else list(SUPPORTED_PROVIDERS.keys())[0]
)


def get_chat_llm(langfuse_client: langfuse.Langfuse = None, provider: str = None, model: str = None, **llm_kwargs):
    if provider is None:
        provider = default_provider
        assert model is None, f"Please input a provider when you specify a specific model: {model}"
    if model is None:
        Llm, api_key, model, llm_kwargs_default = SUPPORTED_PROVIDERS[provider]
    else:
        Llm, api_key, _, llm_kwargs_default = SUPPORTED_PROVIDERS[provider]
    if langfuse_client is None:
        langfuse_client = langfuse.get_client()
    if llm_kwargs is not None:
        llm_kwargs_default.update(llm_kwargs)
    llm_kwargs = llm_kwargs_default
    if provider in SUPPORTED_PROVIDERS.keys():
        if not os.getenv(api_key):
            logger.warning(
                f"ENVIRONMENT VARIABLE {api_key} not set, you asked {provider} with model {model} but it may not work"
            )
        llm = Llm(**llm_kwargs)
        langfuse_client.update_current_trace(
            metadata={
                f"llm_config_{provider}_{model}_{datetime.datetime.now().isoformat()}": dict(
                    caller="/n".join(get_callers_modules()), provider=provider, **llm_kwargs
                )
            }
        )
        return llm
    else:
        raise ValueError(f"Unsupported provider: {provider}")
