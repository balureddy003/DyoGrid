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
from sentence_transformers import SentenceTransformer

'''
Please provide the following environment variables in your .env file if you want to enable Azure Search:
AZURE_SEARCH_SERVICE_ENDPOINT=""
AZURE_SEARCH_ADMIN_KEY=""
Local FAISS vector search is supported by default.
'''
MAGENTIC_ONE_RAG_DESCRIPTION = "An agent that has access to internal index and can handle RAG tasks, call this agent if you are getting questions on your internal index"

MAGENTIC_ONE_RAG_SYSTEM_MESSAGE = """
        You are a helpful AI Assistant.
        When given a user query, use available tools to help the user with their request.
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
        AZURE_SEARCH_SERVICE_ENDPOINT: str,
        use_azure_search: bool = False,
        faiss_documents: list[str] | None = None,
        # AZURE_SEARCH_ADMIN_KEY: str = None,
        description: str = MAGENTIC_ONE_RAG_DESCRIPTION,

    ):
        """Initialize the MagenticOneRAGAgent.

        Args:
            name: The agent's name.
            model_client: The chat completion client.
            index_name: The name of the Azure Search index.
            AZURE_SEARCH_SERVICE_ENDPOINT: The Azure Search service endpoint.
            use_azure_search: Whether to enable Azure Search (default True).
            faiss_documents: Optional list of documents to build the FAISS index for vector search.
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
        self.use_azure_search = use_azure_search
        if self.use_azure_search:
            self.AZURE_SEARCH_SERVICE_ENDPOINT = (
                AZURE_SEARCH_SERVICE_ENDPOINT
                or os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
            )
            if not self.AZURE_SEARCH_SERVICE_ENDPOINT:
                raise ValueError(
                    "AZURE_SEARCH_SERVICE_ENDPOINT is missing; set it in .env or "
                    "pass it explicitly to MagenticOneRAGAgent."
                )
        # self.AZURE_SEARCH_ADMIN_KEY = AZURE_SEARCH_ADMIN_KEY

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.faiss_index = None
        self.faiss_documents = []
        # Automatically build FAISS index if documents provided
        if faiss_documents:
            self.build_faiss_index(faiss_documents)

        self._search_client = None
        if self.use_azure_search:
            self._search_client = self._config_search()

    def _config_search(self) -> "SearchClient":
        if not self.use_azure_search:
            raise RuntimeError("Azure search is disabled for this agent.")
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        from azure.identity import DefaultAzureCredential

        endpoint = self.AZURE_SEARCH_SERVICE_ENDPOINT
        index_name = self.index_name

        if endpoint.startswith("https://"):
            credential = DefaultAzureCredential()
        else:
            key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
            if not key:
                raise RuntimeError(
                    "AZURE_SEARCH_ADMIN_KEY is required when using an HTTP "
                    "endpoint (or switch to HTTPS)."
                )
            credential = AzureKeyCredential(key)

        return SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    def build_faiss_index(self, documents: list[str]):
        self.faiss_documents = documents
        embeddings = self.embedding_model.encode(documents)
        self.faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        self.faiss_index.add(np.array(embeddings))

    def load_faiss_data(self, docs: list[str]):
        self.build_faiss_index(docs)

    async def do_search(self, query: str) -> str:
        # ---------- FAISS Search ----------
        faiss_answer = ""
        try:
            if self.faiss_index is not None:
                query_embedding = self.embedding_model.encode([query])
                D, I = self.faiss_index.search(np.array(query_embedding), k=1)
                faiss_answer = self.faiss_documents[I[0][0]]
            else:
                faiss_answer = "FAISS index is not built yet."
        except Exception as e:
            faiss_answer = f"FAISS search failed with error: {str(e)}"

        # ---------- Azure Cognitive Search ----------
        azure_answer = "Azure search disabled."
        if self.use_azure_search and self._search_client is not None:
            try:
                from azure.search.documents.models import VectorizableTextQuery
                fields = "text_vector"
                vector_query = VectorizableTextQuery(
                    text=query,
                    k_nearest_neighbors=1,
                    fields=fields,
                    exhaustive=True,
                )
                results = self._search_client.search(
                    search_text=None,
                    vector_queries=[vector_query],
                    select=["parent_id", "chunk_id", "chunk"],
                    top=1,
                )
                azure_answer = "".join(r["chunk"] for r in results)
            except Exception as e:
                azure_answer = f"Azure Search failed with error: {str(e)}"

        return f"FAISS Search Result:\n{faiss_answer}\n\nAzure Search Result:\n{azure_answer}"
