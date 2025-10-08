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


from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("How to say {input} in {output_language}:\n")

chain = prompt | llms.OpenAI()
chain.invoke(
    {
        "output_language": "German",
        "input": "I love programming.",
    }
)


MODELS_LIST = {
    "chat": dict(
        best_models=[
            "gpt-5",
            "gpt-4o",
            "gpt-4",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ],
        create_instance=openai.ChatOpenAI,
    ),
    "embeddings": [
        dict(
            best_models=[
                "text-embedding-3-large",
                "text-embedding-3-small",
            ],
            create_instance=openai.OpenAIEmbeddings,
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
