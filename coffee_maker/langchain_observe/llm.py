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


DEFAULT_PROVIDER = "anthropic" if "anthropic" in SUPPORTED_PROVIDERS.keys() else list(SUPPORTED_PROVIDERS.keys())[0]


def get_chat_llm(langfuse_client: langfuse.Langfuse = None, provider: str = None, model: str = None):
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
        # Configure LLM with appropriate max_tokens for code formatting tasks
        llm_kwargs = {"model": model}

        # Set higher token limits for code formatting which requires longer outputs
        if provider == "anthropic":
            llm_kwargs["max_tokens"] = 8192  # Claude supports up to 8k output tokens
        elif provider == "openai":
            llm_kwargs["max_tokens"] = 4096  # GPT supports up to 4k output tokens
        elif provider == "gemini":
            llm_kwargs["max_output_tokens"] = 8192  # Gemini uses different parameter name

        llm = Llm(**llm_kwargs)
        langfuse_client.update_current_trace(
            metadata={
                f"llm_config_{provider}_{model}_{datetime.datetime.now().isoformat()}": dict(
                    caller="/n".join(get_callers_modules()), provider=provider, model=model, **llm_kwargs
                )
            }
        )
        return llm
    else:
        raise ValueError(f"Unsupported provider: {provider}")
