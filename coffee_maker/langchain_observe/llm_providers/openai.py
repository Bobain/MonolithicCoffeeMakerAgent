from langchain_openai import llms
from functools import partial
import openai
import time

from coffee_maker.langchain_observe.llm_providers.gemini import set_api_limits

PROVIDER_NAME = "openai"
Llm = llms.OpenAI

{"max_tokens": 4096}
"gpt-5-codex"


def set_api_limits(providers_fallback):
    def _run_with_api_limits(self, **kwargs):
        attempt = 0
        while attempt < 3:
            try:
                return self.invoke(**kwargs)
            except openai.error.RateLimitError as e:
                print("Rate limit reached, waiting before retrying...")
                time.sleep(2**attempt)  # exponential backoff
                attempt += 1
        return providers_fallback("openai", self, **kwargs)

    setattr(llms.OpenAI, "invoke", partial(_run_with_api_limits, providers_fallback=providers_fallback))
    return llms.OpenAI


def update_info():
    pass


# Example code - don't run at import time
# prompt = PromptTemplate.from_template("How to say {input} in {output_language}:\n")
# chain = prompt | llms.OpenAI()
# chain.invoke(
#     {
#         "output_language": "German",
#         "input": "I love programming.",
#     }
# )


MODELS_LIST = {
    "chat": dict(
        best_models=[
            "gpt-5",
            "gpt-4o",
            "gpt-4",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ],
        create_instance="langchain_openai.ChatOpenAI",  # String reference to avoid import issues
    ),
    "embeddings": [
        dict(
            best_models=[
                "text-embedding-3-large",
                "text-embedding-3-small",
            ],
            create_instance="langchain_openai.OpenAIEmbeddings",  # String reference to avoid import issues
        )
    ],
    "code": [
        "gpt-5-codex",
        "gpt-5",
        "gpt-4o",
        "gpt-4",
    ],
    "reasoning": [
        "o1",
        "gpt-5",
    ],
    "cheapest general purpose": [
        "gpt-5-nano",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ],
}

MODELS_INFO = dict(
    openai=dict(
        reference="https://platform.openai.com/docs/guides/rate-limits",
        values=dict(
            tier1=dict(
                **{
                    "gpt-4o": {
                        "requests per minute": 500,
                        "tokens per minute": 30000,
                        "requests per day": 10000,
                        "context_length": 128000,
                        "max_output_tokens": 4096,
                        "price": {
                            "per 1M tokens input": 2.50,
                            "per 1M tokens output": 10.00,
                        },
                    },
                    "gpt-4o-mini": {
                        "requests per minute": 500,
                        "tokens per minute": 200000,
                        "requests per day": 10000,
                        "context_length": 128000,
                        "max_output_tokens": 16384,
                        "price": {
                            "per 1M tokens input": 0.150,
                            "per 1M tokens output": 0.600,
                        },
                    },
                    "gpt-3.5-turbo": {
                        "requests per minute": 500,
                        "tokens per minute": 60000,
                        "requests per day": 10000,
                        "context_length": 16385,
                        "max_output_tokens": 4096,
                        "price": {
                            "per 1M tokens input": 0.50,
                            "per 1M tokens output": 1.50,
                        },
                    },
                    "gpt-4.1": {
                        "requests per minute": 100,
                        "tokens per minute": 100000,
                        "requests per day": 1000,
                        "context_length": 1000000,
                        "max_output_tokens": 64000,
                        "price": {
                            "per 1M tokens input": 10.00,
                            "per 1M tokens output": 30.00,
                        },
                    },
                    "o1": {
                        "requests per minute": 20,
                        "tokens per minute": 100000,
                        "requests per day": 500,
                        "context_length": 200000,
                        "max_output_tokens": 100000,
                        "price": {
                            "per 1M tokens input": 15.00,
                            "per 1M tokens output": 60.00,
                        },
                    },
                    "o1-mini": {
                        "requests per minute": 30,
                        "tokens per minute": 150000,
                        "requests per day": 1000,
                        "context_length": 128000,
                        "max_output_tokens": 65536,
                        "price": {
                            "per 1M tokens input": 3.00,
                            "per 1M tokens output": 12.00,
                        },
                    },
                }
            ),
            tier2=dict(
                **{
                    "gpt-4o": {
                        "requests per minute": 5000,
                        "tokens per minute": 450000,
                        "requests per day": 10000,
                        "context_length": 128000,
                        "max_output_tokens": 4096,
                        "price": {
                            "per 1M tokens input": 2.50,
                            "per 1M tokens output": 10.00,
                        },
                    },
                    "gpt-4o-mini": {
                        "requests per minute": 5000,
                        "tokens per minute": 2000000,
                        "requests per day": 10000,
                        "context_length": 128000,
                        "max_output_tokens": 16384,
                        "price": {
                            "per 1M tokens input": 0.150,
                            "per 1M tokens output": 0.600,
                        },
                    },
                    "o1": {
                        "requests per minute": 40,
                        "tokens per minute": 200000,
                        "requests per day": 1000,
                        "context_length": 200000,
                        "max_output_tokens": 100000,
                        "price": {
                            "per 1M tokens input": 15.00,
                            "per 1M tokens output": 60.00,
                        },
                    },
                    "o1-mini": {
                        "requests per minute": 60,
                        "tokens per minute": 300000,
                        "requests per day": 2000,
                        "context_length": 128000,
                        "max_output_tokens": 65536,
                        "price": {
                            "per 1M tokens input": 3.00,
                            "per 1M tokens output": 12.00,
                        },
                    },
                }
            ),
        ),
    )
)
