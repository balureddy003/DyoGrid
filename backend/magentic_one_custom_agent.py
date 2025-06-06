from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from llm_config import get_llm_config
from autogen_ext.models.openai import (
    AzureOpenAIChatCompletionClient,
    OpenAIChatCompletionClient,
)
import os


def _build_llm_client():
    """
    Create a ChatCompletionClient from the dict returned by get_llm_config().
    Supports 'azure' and 'openai' (incl. LiteLLM/Ollama proxy) providers.
    """
    cfg = get_llm_config().copy()
    provider = cfg.pop("provider", "openai").lower()

    if provider == "azure":
        return AzureOpenAIChatCompletionClient(**cfg)
    else:
        # treat every non‑azure provider as OpenAI compatible
        return OpenAIChatCompletionClient(**cfg)

class MagenticOneCustomAgent(AssistantAgent):
    """Custom agent without function calling support."""

    def __init__(
        self,
        name: str,
        model_client: ChatCompletionClient = None,
        system_message: str = "",
        description: str = "",
    ):
        if model_client is None:
            model_client = _build_llm_client()

        # Ensure function calling is not used
        super().__init__(
            name=name,
            model_client=model_client,
            description=description,
            system_message=system_message,
            tools=[],                    # ⛔ no tools
            reflect_on_tool_use=False    # ⛔ disable function-calling reflection
        )