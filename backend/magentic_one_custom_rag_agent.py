from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import (
    ChatCompletionClient,
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizableTextQuery
from azure.identity import DefaultAzureCredential
try:
    import faiss
except ImportError as e:
    raise ImportError("faiss is not installed. Install it via 'pip install faiss-cpu' or 'faiss-gpu' based on your system.") from e
import numpy as np
from sentence_transformers import SentenceTransformer

'''
Please provide the following environment variables in your .env file:
AZURE_SEARCH_SERVICE_ENDPOINT=""
AZURE_SEARCH_ADMIN_KEY=""
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
        # AZURE_SEARCH_ADMIN_KEY: str = None,
        description: str = MAGENTIC_ONE_RAG_DESCRIPTION,

    ):
        super().__init__(
            name,
            model_client,
            description=description,
            system_message=MAGENTIC_ONE_RAG_SYSTEM_MESSAGE,
            tools=[self.do_search],
            reflect_on_tool_use=True,
        )

        self.index_name = index_name    
        self.AZURE_SEARCH_SERVICE_ENDPOINT = AZURE_SEARCH_SERVICE_ENDPOINT
        # self.AZURE_SEARCH_ADMIN_KEY = AZURE_SEARCH_ADMIN_KEY

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.faiss_index = None
        self.faiss_documents = []

        
    def config_search(self) -> SearchClient:
        service_endpoint = self.AZURE_SEARCH_SERVICE_ENDPOINT
        # key = self.AZURE_SEARCH_ADMIN_KEY
        index_name = self.index_name
        # credential = AzureKeyCredential(key)
        credential = DefaultAzureCredential()
        return SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)

    def build_faiss_index(self, documents: list[str]):
        self.faiss_documents = documents
        embeddings = self.embedding_model.encode(documents)
        self.faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        self.faiss_index.add(np.array(embeddings))

    def load_faiss_data(self, docs: list[str]):
        self.build_faiss_index(docs)

    async def do_search(self, query: str) -> str:
        # Azure Search
        try:
            aia_search_client = self.config_search()
            fields = "text_vector"
            vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=1, fields=fields, exhaustive=True)
            results = aia_search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["parent_id", "chunk_id", "chunk"],
                top=1
            )
            azure_answer = ""
            for result in results:
                azure_answer += result["chunk"]
        except Exception as e:
            azure_answer = f"Azure Search failed with error: {str(e)}"

        # FAISS Search
        try:
            if self.faiss_index is not None:
                query_embedding = self.embedding_model.encode([query])
                D, I = self.faiss_index.search(np.array(query_embedding), k=1)
                faiss_answer = self.faiss_documents[I[0][0]]
            else:
                faiss_answer = "FAISS index is not built yet."
        except Exception as e:
            faiss_answer = f"FAISS search failed with error: {str(e)}"

        return f"Azure Search Result:\n{azure_answer}\n\nFAISS Search Result:\n{faiss_answer}"
