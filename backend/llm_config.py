import os

def get_llm_provider():
    provider = os.getenv("LLM_PROVIDER", "azure")
    return provider.lower()

def get_llm_config():
    provider = get_llm_provider()
    timeout = int(os.getenv("OPENAI_TIMEOUT", 60))

    if provider == "azure":
        return {
            "provider": "azure",
            "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            "timeout": timeout,
        }
    elif provider == "ollama":
        return {
            "provider": "openai",
            "model": os.getenv("OLLAMA_MODEL","llama3.1"),
            "base_url": os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
            "api_key": os.getenv("LITELLM_API_KEY", "sk-no-key-needed"),
            "function_calling": "auto",
            "json_output": True,
            "stream": True,
            "timeout": timeout,
        }
    else:
        raise ValueError(f"Unsupported provider: {provider}")
