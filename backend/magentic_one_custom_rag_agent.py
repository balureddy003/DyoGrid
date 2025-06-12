from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import (
    ChatCompletionClient,
)
try:
    import faiss
except ImportError as e:
    raise ImportError("faiss is not installed. Install it via 'pip install faiss-cpu' or 'faiss-gpu' based on your system.") from e
import numpy as np
import os
import json
from llm_config import build_embedding_client, get_llm_provider, LITELLM_EMBED_MODEL

RAG_BACKEND = os.getenv("RAG_BACKEND", "faiss").lower()



MAGENTIC_ONE_RAG_DESCRIPTION = "An agent that has access to internal index and can handle RAG tasks, call this agent if you are getting questions on your internal index"

MAGENTIC_ONE_RAG_SYSTEM_MESSAGE = """
        You are a helpful AI Assistant.
        When given a user query, use available tools to help the user with their request.
        The `do_search` tool returns text snippets from a local FAISS index.
        Use this information to craft your answer.
        Reply "TERMINATE" in the end when everything is done."""

class MagenticOneRAGAgent(AssistantAgent):
    """An agent, used by MagenticOne that provides coding assistance using an LLM model client.

    The prompts and description are sealed, to replicate the original MagenticOne configuration. See AssistantAgent if you wish to modify these values.
    """

    def __init__(
        self,
        name: str,
        model_client: ChatCompletionClient,
        index_name: str,
        faiss_documents: list[str] | None = None,
        faiss_index_path: str | None = None,
        description: str = MAGENTIC_ONE_RAG_DESCRIPTION,

    ):
        """Initialize the MagenticOneRAGAgent.

        Args:
            name: The agent's name.
            model_client: The chat completion client.
        index_name: Name used for the local FAISS index.
        faiss_documents: Optional list of documents to build the FAISS index for vector search.
        faiss_index_path: Optional path to store/load the FAISS index file.
        description: The agent description.

        When faiss_documents are provided, a FAISS index will be automatically built and used for vector similarity search.
        """
        super().__init__(
            name,
            model_client,
            description=description,
            system_message=MAGENTIC_ONE_RAG_SYSTEM_MESSAGE,
            tools=[self.do_search],
            reflect_on_tool_use=True,
        )

        self.index_name = index_name

        # Client used to generate embeddings, respecting LLM_PROVIDER
        self._embedding_client = build_embedding_client()
        if get_llm_provider() == "ollama":
            self.embedding_model = LITELLM_EMBED_MODEL
        else:
            self.embedding_model = os.getenv(
                "AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            )
        self.faiss_index = None
        self.faiss_documents = []
        self.faiss_index_path = faiss_index_path or f"{self.index_name}.faiss"

        if os.path.exists(self.faiss_index_path):
            try:
                self.load_faiss_index(self.faiss_index_path)
            except Exception as e:
                print(f"Failed to load FAISS index: {e}")
                if faiss_documents:
                    self.build_faiss_index(faiss_documents)
        elif faiss_documents:
            self.build_faiss_index(faiss_documents)

        self._search_client = None

    def build_faiss_index(self, documents: list[str]):
        self.faiss_documents = documents
        response = self._embedding_client.embeddings.create(
            input=documents, model=self.embedding_model
        )
        embeddings = np.array([d.embedding for d in response.data])
        self.faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        self.faiss_index.add(embeddings)
        self.save_faiss_index(self.faiss_index_path)

    def save_faiss_index(self, path: str):
        """Save the FAISS index and associated documents to disk."""
        if self.faiss_index is None:
            raise ValueError("FAISS index is not built yet.")
        faiss.write_index(self.faiss_index, path)
        with open(f"{path}.docs", "w", encoding="utf-8") as f:
            json.dump(self.faiss_documents, f)

    def load_faiss_index(self, path: str):
        """Load the FAISS index and documents from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"FAISS index file not found at {path}")
        self.faiss_index = faiss.read_index(path)
        docs_path = f"{path}.docs"
        if os.path.exists(docs_path):
            with open(docs_path, "r", encoding="utf-8") as f:
                self.faiss_documents = json.load(f)
        else:
            self.faiss_documents = []

    def load_faiss_data(self, docs: list[str]):
        self.build_faiss_index(docs)

    async def do_search(self, query: str) -> dict:
        """Search using FAISS and optionally Azure Cognitive Search.

        Args:
            query: The query string.

        Returns:
            A dictionary with a ``"faiss"`` key containing search results. Each
            result has ``"text"`` and may include metadata such as ``"score```,
            ``"parent_id"`` or ``"chunk_id"``.
        """

        results: dict[str, list[dict]] = {"faiss": []}

        # ---------- FAISS Search ----------
        try:
            if self.faiss_index is not None:
                resp = self._embedding_client.embeddings.create(
                    input=[query], model=self.embedding_model
                )
                query_embedding = np.array([resp.data[0].embedding])
                D, I = self.faiss_index.search(query_embedding, k=1)
                idx = int(I[0][0])
                score = float(D[0][0])
                snippet = self.faiss_documents[idx]
                results["faiss"].append({"text": snippet, "score": score, "index": idx})
            else:
                results["faiss"].append({"error": "FAISS index is not built yet."})
        except Exception as e:
            results["faiss"].append({"error": f"FAISS search failed with error: {str(e)}"})

        return results
