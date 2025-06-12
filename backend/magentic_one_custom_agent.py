from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from llm_config import get_llm_config, build_chat_client



def _build_llm_client(agent_name: str):
    """
    Create a ChatCompletionClient from the dict returned by get_llm_config().
    Supports  LiteLLM/Ollama proxy providers.
    """
    return build_chat_client(agent_name=agent_name, agent_type="Custom")

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
            model_client = _build_llm_client(name)

        # Ensure function calling is not used
        super().__init__(
            name=name,
            model_client=model_client,
            description=description,
            system_message=system_message,
            tools=[],                    # ⛔ no tools
            reflect_on_tool_use=False    # ⛔ disable function-calling reflection
        )
