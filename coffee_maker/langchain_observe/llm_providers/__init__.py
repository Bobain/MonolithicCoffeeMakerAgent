try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    SUPPORTED_PROVIDERS.update(
        {"gemini": (ChatGoogleGenerativeAI, "GEMINI_API_KEY", "gemini-2.5-pro", {"max_tokens": 8192})}
    )
except:
    logger.warning("langchain_google_genai not installed. will not use google")

# class ClassicLlm
