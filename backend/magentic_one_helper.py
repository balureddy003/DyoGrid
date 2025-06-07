import asyncio
import logging
import os
import time
import random
from uuid import uuid4

from inspect import signature

from typing import Optional, AsyncGenerator, Dict, Any, List
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.code_executors.azure import ACADynamicSessionsCodeExecutor
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import AgentId, AgentProxy, DefaultTopicId
from autogen_core import SingleThreadedAgentRuntime
from autogen_core import CancellationToken
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import tempfile
from dotenv import load_dotenv
load_dotenv()

# Import get_llm_config after dotenv load
from llm_config import get_llm_config

from magentic_one_custom_agent import MagenticOneCustomAgent
from magentic_one_custom_rag_agent import MagenticOneRAGAgent
from magentic_one_custom_mcp_agent import MagenticOneCustomMCPAgent

azure_credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    azure_credential, "https://cognitiveservices.azure.com/.default"
)

def _wrap_with_proxy(agent):
    """
    Attach a unique AgentId (id/name + key) to every agent so that
    message.source is never 'unknown'.

    The signatures of *both* AgentId and AgentProxy vary across
    autogen‑core releases.  We therefore:

    1.  Build an AgentId using the first signature that works.
    2.  Inspect AgentProxy.__init__ and create the proxy with
        the appropriate argument names/positions.

    If the object is already an AgentProxy we simply return it.
    """
    if isinstance(agent, AgentProxy):
        return agent  # already wrapped

    new_key = str(uuid4())

    # ---- Step 1: build a compatible AgentId ---------------------------------
    agent_id = None
    for kwargs in (
        {"name": agent.name, "key": new_key},
        {"id": agent.name, "key": new_key},
        {},  # fallback to positional signature tried below
    ):
        try:
            agent_id = AgentId(**kwargs) if kwargs else AgentId(agent.name, new_key)
            break
        except TypeError:
            continue

    if agent_id is None:
        raise RuntimeError("Unable to construct AgentId with the current autogen‑core version.")

    # ---- Step 2: wrap with AgentProxy ---------------------------------------
    sig = signature(AgentProxy)  # reflect current signature
    param_names = list(sig.parameters)

    try:
        if {"agent_id", "agent"}.issubset(param_names):
            proxy = AgentProxy(agent_id=agent_id, agent=agent)
            proxy.name = getattr(agent, "name", str(agent_id))
            # Expose the underlying agent's produced_message_types so GroupChat can inspect it
            if not hasattr(proxy, "produced_message_types"):
                proxy.produced_message_types = getattr(agent, "produced_message_types", [])
            # --- propagate commonly‑used attributes so GroupChat can inspect them ---
            for _attr in ("name", "description", "produced_message_types"):
                if hasattr(agent, _attr) and not hasattr(proxy, _attr):
                    try:
                        setattr(proxy, _attr, getattr(agent, _attr))
                    except Exception:
                        # silently skip if the proxy implementation forbids setting
                        pass
            # --- forward lifecycle / stream handlers the team code expects ---
            for _method in ("on_reset", "on_messages_stream", "on_message"):
                if hasattr(agent, _method) and not hasattr(proxy, _method):
                    try:
                        setattr(proxy, _method, getattr(agent, _method))
                    except Exception:
                        pass
            return proxy
        elif {"id", "agent"}.issubset(param_names):
            proxy = AgentProxy(id=agent_id, agent=agent)
            proxy.name = getattr(agent, "name", str(agent_id))
            # Expose the underlying agent's produced_message_types so GroupChat can inspect it
            if not hasattr(proxy, "produced_message_types"):
                proxy.produced_message_types = getattr(agent, "produced_message_types", [])
            # --- propagate commonly‑used attributes so GroupChat can inspect them ---
            for _attr in ("name", "description", "produced_message_types"):
                if hasattr(agent, _attr) and not hasattr(proxy, _attr):
                    try:
                        setattr(proxy, _attr, getattr(agent, _attr))
                    except Exception:
                        # silently skip if the proxy implementation forbids setting
                        pass
            # --- forward lifecycle / stream handlers the team code expects ---
            for _method in ("on_reset", "on_messages_stream", "on_message"):
                if hasattr(agent, _method) and not hasattr(proxy, _method):
                    try:
                        setattr(proxy, _method, getattr(agent, _method))
                    except Exception:
                        pass
            return proxy
        elif len(param_names) >= 2:
            # assume first two positional parameters are (agent_id/id, agent)
            proxy = AgentProxy(agent_id, agent)
            proxy.name = getattr(agent, "name", str(agent_id))
            # Expose the underlying agent's produced_message_types so GroupChat can inspect it
            if not hasattr(proxy, "produced_message_types"):
                proxy.produced_message_types = getattr(agent, "produced_message_types", [])
            # --- propagate commonly‑used attributes so GroupChat can inspect them ---
            for _attr in ("name", "description", "produced_message_types"):
                if hasattr(agent, _attr) and not hasattr(proxy, _attr):
                    try:
                        setattr(proxy, _attr, getattr(agent, _attr))
                    except Exception:
                        # silently skip if the proxy implementation forbids setting
                        pass
            # --- forward lifecycle / stream handlers the team code expects ---
            for _method in ("on_reset", "on_messages_stream", "on_message"):
                if hasattr(agent, _method) and not hasattr(proxy, _method):
                    try:
                        setattr(proxy, _method, getattr(agent, _method))
                    except Exception:
                        pass
            return proxy
    except TypeError:
        pass

    raise RuntimeError("Unable to construct AgentProxy with the current autogen‑core version.")

def generate_session_name():
    '''Generate a unique session name based on random sci-fi words, e.g. quantum-cyborg-1234'''
    adjectives = [
        "quantum", "neon", "stellar", "galactic", "cyber", "holographic", "plasma", "nano", "hyper", "virtual",
        "cosmic", "interstellar", "lunar", "solar", "astro", "exo", "alien", "robotic", "synthetic", "digital",
        "futuristic", "parallel", "extraterrestrial", "transdimensional", "biomechanical", "cybernetic", "hologram",
        "metaphysical", "subatomic", "tachyon", "warp", "xeno", "zenith", "zerogravity", "antimatter", "darkmatter",
        "neural", "photon", "quantum", "singularity", "space-time", "stellar", "telepathic", "timetravel", "ultra",
        "virtualreality", "wormhole"
    ]
    nouns = [
        "cyborg", "android", "drone", "mech", "robot", "alien", "spaceship", "starship", "satellite", "probe",
        "astronaut", "cosmonaut", "galaxy", "nebula", "comet", "asteroid", "planet", "moon", "star", "quasar",
        "black-hole", "wormhole", "singularity", "dimension", "universe", "multiverse", "matrix", "simulation",
        "hologram", "avatar", "clone", "replicant", "cyberspace", "nanobot", "biobot", "exosuit", "spacesuit",
        "terraformer", "teleporter", "warpdrive", "hyperdrive", "stasis", "cryosleep", "fusion", "fission", "antigravity",
        "darkenergy", "neutrino", "tachyon", "photon"
    ]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(1000, 9999)
    
    return f"{adjective}-{noun}-{number}"

class MagenticOneHelper:
    def __init__(self, logs_dir: str = None, save_screenshots: bool = False, run_locally: bool = False, user_id: str = None, llm_config: dict = None) -> None:
        """
        A helper class to interact with the MagenticOne system.
        Initialize MagenticOne instance.

        Args:
            logs_dir: Directory to store logs and downloads
            save_screenshots: Whether to save screenshots of web pages
            user_id: The user ID associated with this helper instance
            llm_config: Dictionary with LLM configuration for client instantiation
        """
        self.logs_dir = logs_dir or os.getcwd()
        self.runtime: Optional[SingleThreadedAgentRuntime] = None
        # self.log_handler: Optional[LogHandler] = None
        self.save_screenshots = save_screenshots
        self.run_locally = run_locally

        self.user_id = user_id
        if llm_config is None:
            self.llm_config = get_llm_config()
        else:
            self.llm_config = llm_config

        self.max_rounds = 50
        self.max_time = 25 * 60
        self.max_stalls_before_replan = 5
        self.return_final_answer = True
        self.start_page = "https://www.bing.com"

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    async def initialize(self, agents, session_id = None) -> None:
        """
        Initialize the MagenticOne system, setting up agents and runtime.
        """
        # Create the runtime
        self.runtime = SingleThreadedAgentRuntime()

        # generate session id from current datetime
        if session_id is None:
            self.session_id = generate_session_name()
        else:
            self.session_id = session_id
        # print(f"Session MODEL gpt-4.1-2025-04-14")
        print(f"Session MODEL o4-mini-2025-04-16")

        provider = self.llm_config.get("provider")
        if provider == "azure":
            # Build Azure client args
            azure_args = {
                "model": self.llm_config["model"],
                "azure_deployment": self.llm_config["model"],
                "api_version": self.llm_config["api_version"],
                "azure_endpoint": self.llm_config["base_url"],
                "azure_ad_token_provider": token_provider,
                "api_key": self.llm_config["api_key"],
                "timeout": self.llm_config.get("timeout", 60),
            }
            self.client = AzureOpenAIChatCompletionClient(**azure_args)
            # Reasoning client can override model/deployment if needed; here we reuse same
            self.client_reasoning = AzureOpenAIChatCompletionClient(**azure_args)
        elif provider == "openai":
            # Use OpenAIChatCompletionClient with relevant arguments and model_info
            self.client = OpenAIChatCompletionClient(
                model=self.llm_config["model"],
                base_url=self.llm_config["base_url"],
                api_key=self.llm_config["api_key"],
                function_calling=self.llm_config.get("function_calling", False),
                json_output=self.llm_config.get("json_output", False),
                model_info=self.llm_config.get(
                    "model_info",
                    {"vision": False, "function_calling": True, "json_output": True, "family": "ollama"}
                ),
                timeout=self.llm_config.get("timeout", 60),
            )
            self.client_reasoning = OpenAIChatCompletionClient(
                model=self.llm_config["model"],
                base_url=self.llm_config["base_url"],
                api_key=self.llm_config["api_key"],
                function_calling=self.llm_config.get("function_calling", False),
                json_output=self.llm_config.get("json_output", False),
                model_info=self.llm_config.get(
                    "model_info",
                    {"vision": False, "function_calling": True, "json_output": True, "family": "ollama"}
                ),
                timeout=self.llm_config.get("timeout", 60),
            )
        else:
            raise RuntimeError(f"Unsupported LLM provider: {provider}")

        # Set up agents
        self.agents = await self.setup_agents(agents, self.client, self.logs_dir)

        print("Agents setup complete!")

    async def setup_agents(self, agents, client, logs_dir):
        agent_list = []
        docs_dir = os.environ.get(
            "RAG_DOCS_PATH",
            os.path.join(os.path.dirname(__file__), "data", "ai-search-index"),
        )
        docs: List[str] = []
        if os.path.isdir(docs_dir):
            for root, _, files in os.walk(docs_dir):
                for fname in files:
                    file_path = os.path.join(root, fname)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            docs.append(f.read())
                    except Exception:
                        try:
                            with open(file_path, "rb") as f:
                                docs.append(f.read().decode("utf-8", errors="ignore"))
                        except Exception:
                            pass
        for agent in agents:
            # This is default MagenticOne agent - Coder
            if (agent["type"] == "MagenticOne" and agent["name"] == "Coder"):
                coder = MagenticOneCoderAgent("Coder", model_client=client)
                agent_list.append(_wrap_with_proxy(coder))
                print("Coder added!")

            # This is default MagenticOne agent - Executor
            elif (agent["type"] == "MagenticOne" and agent["name"] == "Executor"):
                # handle local = local docker execution
                if self.run_locally:
                    #docker
                    code_executor = DockerCommandLineCodeExecutor(work_dir=logs_dir)
                    await code_executor.start()
                    executor = CodeExecutorAgent("Executor", code_executor=code_executor)
                
                # or remote = Azure ACA Dynamic Sessions execution
                else:
                    pool_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")
                    assert pool_endpoint, "POOL_MANAGEMENT_ENDPOINT environment variable is not set"
                    with tempfile.TemporaryDirectory() as temp_dir:# Define the correct path to the data folder for file access
                        code_executor=ACADynamicSessionsCodeExecutor(
                            pool_management_endpoint=pool_endpoint,
                            credential=azure_credential,
                            work_dir=temp_dir
                        )
                        print(code_executor._session_id)
                        #code_executor.upload_files(os.path.join(os.getcwd(), "data"))
                        print("Files uploaded!")
                        executor = CodeExecutorAgent("Executor",code_executor=code_executor )
                
                agent_list.append(_wrap_with_proxy(executor))
                print("Executor added!")

            # This is default MagenticOne agent - WebSurfer
            elif (agent["type"] == "MagenticOne" and agent["name"] == "WebSurfer"):
                web_surfer = MultimodalWebSurfer("WebSurfer", model_client=client)
                agent_list.append(_wrap_with_proxy(web_surfer))
                print("WebSurfer added!")
            
            # This is default MagenticOne agent - FileSurfer
            elif (agent["type"] == "MagenticOne" and agent["name"] == "FileSurfer"):
                file_surfer = FileSurfer("FileSurfer", model_client=client)
                file_surfer._browser.set_path(os.path.join(os.getcwd(), "data"))  # Set the path to the data folder in the current working directory
                agent_list.append(_wrap_with_proxy(file_surfer))
                print("FileSurfer added!")
            
            # This is custom agent - simple SYSTEM message and DESCRIPTION is used inherited from AssistantAgent
            elif (agent["type"] == "Custom"):
                custom_agent = MagenticOneCustomAgent(
                    agent["name"], 
                    model_client=client, 
                    system_message=agent["system_message"], 
                    description=agent["description"]
                    )
                agent_list.append(_wrap_with_proxy(custom_agent))
                print(f'{agent["name"]} (custom) added!')
            
            elif (agent["type"] == "CustomMCP"):
                custom_agent = await MagenticOneCustomMCPAgent.create(
                    agent["name"], 
                    client, 
                    agent["system_message"] + "\n\n in case of email use this address as TO: " + self.user_id, 
                    agent["description"],
                    self.user_id
                )
                agent_list.append(_wrap_with_proxy(custom_agent))
                print(f'{agent["name"]} (custom MCP) added!')

            
            # This is custom agent - RAG agent - you need to specify index_name and Azure Cognitive Search service endpoint and admin key in .env file
            elif (agent["type"] == "RAG"):
                # RAG agent
                rag_agent = MagenticOneRAGAgent(
                    agent["name"], 
                    model_client=client, 
                    index_name=agent["index_name"],
                    description=agent["description"],
                    AZURE_SEARCH_SERVICE_ENDPOINT=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
                    use_azure_search=False, 
                    # AZURE_SEARCH_ADMIN_KEY=os.getenv("AZURE_SEARCH_ADMIN_KEY")
                    )
                rag_agent.load_faiss_data(docs)
                agent_list.append(_wrap_with_proxy(rag_agent))
                print(f'{agent["name"]} (RAG) added!')
            else:
                raise ValueError('Unknown Agent!')
        return agent_list

    async def main(self, task):
        team = MagenticOneGroupChat(
            participants=self.agents,
            model_client=self.client,
            # model_client=self.client_reasoning,
            max_turns=self.max_rounds,
            max_stalls=self.max_stalls_before_replan,
            emit_team_events=False,
        )
        cancellation_token = CancellationToken()
        stream = team.run_stream(task=task, cancellation_token=cancellation_token)
        return stream, cancellation_token
    
async def main(agents, task, run_locally) -> None:

    magentic_one = MagenticOneHelper(logs_dir=".", run_locally=run_locally)
    await magentic_one.initialize(agents)

    team = MagenticOneGroupChat(
            participants=magentic_one.agents,
            model_client=magentic_one.client,
            max_turns=magentic_one.max_rounds,
            max_stalls=magentic_one.max_stalls_before_replan,
            
        )
    try:
        await Console(team.run_stream(task=task))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await team.shutdown()

if __name__ == "__main__":   
    MAGENTIC_ONE_DEFAULT_AGENTS = [
            {
            "input_key":"0001",
            "type":"MagenticOne",
            "name":"Coder",
            "system_message":"",
            "description":"",
            "icon":"👨‍💻"
            },
            {
            "input_key":"0002",
            "type":"MagenticOne",
            "name":"Executor",
            "system_message":"",
            "description":"",
            "icon":"💻"
            },
            {
            "input_key":"0003",
            "type":"MagenticOne",
            "name":"FileSurfer",
            "system_message":"",
            "description":"",
            "icon":"📂"
            },
            {
            "input_key":"0004",
            "type":"MagenticOne",
            "name":"WebSurfer",
            "system_message":"",
            "description":"",
            "icon":"🏄‍♂️"
            },
            ]
    
    import argparse
    parser = argparse.ArgumentParser(description="Run MagenticOneHelper with specified task and run_locally option.")
    parser.add_argument("--task", "-t", type=str, required=True, help="The task to run, e.g. 'How much taxes elon musk paid?'")
    parser.add_argument("--run_locally", action="store_true", help="Run locally if set")
    
    # You can run this command from terminal
    # python magentic_one_helper.py --task "Find me a French restaurant in Dubai with 2 Michelin stars?"
    
    args = parser.parse_args()

    asyncio.run(main(MAGENTIC_ONE_DEFAULT_AGENTS,args.task, args.run_locally))
