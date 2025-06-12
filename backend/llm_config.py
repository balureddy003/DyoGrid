
import os

# LiteLLM/Ollama default models
LITELLM_CHAT_MODEL = os.getenv("LITELLM_CHAT_MODEL", os.getenv("OLLAMA_MODEL", "llama3.1"))
LITELLM_TOOL_MODEL = os.getenv("LITELLM_TOOL_MODEL", LITELLM_CHAT_MODEL)
LITELLM_EMBED_MODEL = os.getenv("LITELLM_EMBED_MODEL", "nomic-embed-text")


def _load_agent_model_map() -> dict:
    """Parse AGENT_MODEL_MAP env var into a dictionary.

    Keys are normalised to lower case so that mapping is case-insensitive.
    """
    mapping = {}
    raw = os.getenv("AGENT_MODEL_MAP", "")
    for item in raw.split(","):
        if ":" in item:
            agent, model = item.split(":", 1)
            mapping[agent.strip().lower()] = model.strip()
    return mapping

def get_llm_provider():
    """Return the configured LLM provider.

    Only the ``ollama`` provider is supported in this refactored version. The
    environment variable ``LLM_PROVIDER`` may still be used but any value other
    than ``ollama`` will raise an error.``"""  # updated docstring

    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider != "ollama":
        raise ValueError("Only the 'ollama' provider is supported for local LLMs")
    return provider

def get_llm_config(agent_name: str | None = None, agent_type: str | None = None):
    provider = get_llm_provider()
    timeout = int(os.getenv("OPENAI_TIMEOUT", 60))

    model = None
    model_map = _load_agent_model_map()
    lookup_name = agent_name.lower() if agent_name else None
    lookup_type = agent_type.lower() if agent_type else None
    if lookup_name and lookup_name in model_map:
        model = model_map[lookup_name]
    elif lookup_type and lookup_type in model_map:
        model = model_map[lookup_type]

    if provider == "ollama":
        # Decide chat vs tool model
        default_chat = LITELLM_CHAT_MODEL
        default_tool = LITELLM_TOOL_MODEL
        chosen = model or default_chat
        force_tools = os.getenv("LITELLM_ALWAYS_ENABLE_TOOLS", "false").lower() == "true"
        is_tool = force_tools or chosen == default_tool
        return {
            "provider": "openai",
            "model": chosen,
            "base_url": os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
            "api_key": os.getenv("LITELLM_API_KEY", "sk-no-key-needed"),
            "function_calling": is_tool,
            "json_output": is_tool,
            "stream": True,
            # Required when using a non-OpenAI model via LiteLLM/Ollama
            "model_info": {
                "family": "ollama",
                "function_calling": is_tool,
                "json_output": is_tool,
                "vision": False,
            },
            "timeout": timeout,
        }
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def build_chat_client(agent_name: str | None = None, agent_type: str | None = None):
    """Create a chat completion client for the local LLM provider."""
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    cfg = get_llm_config(agent_name=agent_name, agent_type=agent_type).copy()
    timeout = cfg.pop("timeout", 60)
    cfg.pop("provider", None)

    # Filter out unsupported args for the client constructor
    cfg.pop("stream", None)

    return OpenAIChatCompletionClient(timeout=timeout, **cfg)


def build_embedding_client():
    """Create an OpenAI client for embeddings using the local provider."""
    from openai import OpenAI

    timeout = int(os.getenv("OPENAI_TIMEOUT", 60))

    return OpenAI(
        base_url=os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
        api_key=os.getenv("LITELLM_API_KEY", "sk-no-key-needed"),
        timeout=timeout,
    )

