import os


def _load_agent_model_map() -> dict:
    """Parse AGENT_MODEL_MAP env var into a dictionary."""
    mapping = {}
    raw = os.getenv("AGENT_MODEL_MAP", "")
    for item in raw.split(","):
        if ":" in item:
            agent, model = item.split(":", 1)
            mapping[agent.strip()] = model.strip()
    return mapping

def get_llm_provider():
    provider = os.getenv("LLM_PROVIDER", "azure")
    return provider.lower()

def get_llm_config(agent_name: str | None = None, agent_type: str | None = None):
    provider = get_llm_provider()
    timeout = int(os.getenv("OPENAI_TIMEOUT", 60))

    model = None
    model_map = _load_agent_model_map()
    if agent_name and agent_name in model_map:
        model = model_map[agent_name]
    elif agent_type and agent_type in model_map:
        model = model_map[agent_type]

    if provider == "azure":
        return {
            "provider": "azure",
            "model": model or os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            "timeout": timeout,
        }
    elif provider == "ollama":
        return {
            "provider": "openai",
            "model": model or os.getenv("OLLAMA_MODEL", "llama3.1"),
            "base_url": os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
            "api_key": os.getenv("LITELLM_API_KEY", "sk-no-key-needed"),
            "function_calling": "auto",
            "json_output": True,
            "stream": True,
            "timeout": timeout,
        }
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def build_chat_client(agent_name: str | None = None, agent_type: str | None = None):
    """Helper to create a ChatCompletionClient based on agent info."""
    from autogen_ext.models.openai import (
        AzureOpenAIChatCompletionClient,
        OpenAIChatCompletionClient,
    )

    cfg = get_llm_config(agent_name=agent_name, agent_type=agent_type).copy()
    timeout = cfg.pop("timeout", 60)
    provider = cfg.pop("provider", "openai").lower()

    # Filter out unsupported args for the client constructor
    cfg.pop("stream", None)

    if provider == "azure":
        return AzureOpenAIChatCompletionClient(timeout=timeout, **cfg)
    else:
        return OpenAIChatCompletionClient(timeout=timeout, **cfg)

