from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from llm_config import build_chat_client
from tools import (
    bing_search_tool,
    google_search_tool,
    fetch_webpage_tool,
    generate_image_tool,
    generate_pdf_tool,
    calculator_tool,
)


def _build_llm_client(agent_name: str):
    """Create a ChatCompletionClient for a tools-enabled agent."""
    return build_chat_client(agent_name=agent_name, agent_type="Tools")


class MagenticOneToolsAgent(AssistantAgent):
    """Agent with access to various utility tools."""

    def __init__(
        self,
        name: str,
        model_client: ChatCompletionClient = None,
        system_message: str = "",
        description: str = "",
    ):
        if model_client is None:
            model_client = _build_llm_client(name)

        super().__init__(
            name=name,
            model_client=model_client,
            description=description,
            system_message=system_message,
            tools=[
                bing_search_tool,
                google_search_tool,
                fetch_webpage_tool,
                generate_image_tool,
                generate_pdf_tool,
                calculator_tool,
            ],
            reflect_on_tool_use=True,
        )

