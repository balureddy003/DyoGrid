import os, glob, json, uuid
from typing import Optional, Dict, Union, List
from pymongo import MongoClient
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey

from dotenv import load_dotenv
from bson import ObjectId
import time
import logging
from math import ceil
# Remove ALL old agentchat imports!
# from autogen_agentchat.base import TaskResult
# from autogen_agentchat.messages import ...
# from schemas import AutoGenMessage

def convert_objectid(obj: Union[dict, list]) -> Union[dict, list]:
    """Recursively convert ObjectId fields to strings."""
    if isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                new_obj[k] = str(v)
            elif isinstance(v, (dict, list)):
                new_obj[k] = convert_objectid(v)
            else:
                new_obj[k] = v
        return new_obj
    else:
        return obj

class CosmosDB:
    def __init__(self):
        load_dotenv(".env", override=True)
        self.use_local = os.getenv("USE_LOCAL_DB", "true").lower() == "true"

        if self.use_local:
            uri = os.getenv("COSMOS_DB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("COSMOS_DB_DATABASE", "ag_demo")
            self.client = MongoClient(uri)
            self.database = self.client[db_name]
        else:
            uri = os.getenv("COSMOS_DB_URI", "https://your-db.documents.azure.com:443/")
            db_name = os.getenv("COSMOS_DB_DATABASE", "ag_demo")
            credential = DefaultAzureCredential()
            self.client = CosmosClient(uri, credential=credential)
            self.database = self.client.create_database_if_not_exists(id=db_name)

        self.containers = {}

    def get_container(self, name: str):
        if name in self.containers:
            return self.containers[name]
        if self.use_local:
            container = self.database[name]
        else:
            container = self.database.create_container_if_not_exists(
                id=name,
                partition_key=PartitionKey(path="/user_id" if name == "ag_demo" else "/team_id"),
                offer_throughput=400,
            )
        self.containers[name] = container
        return container

    def store_conversation(self, conversation: dict, conversation_details: dict, conversation_dict: dict):
        """
        Store a conversation (all dict-based, no TaskResult).
        - conversation: main chat/message structure (dict)
        - conversation_details: metadata (dict or object)
        - conversation_dict: any additional data (dict)
        """
        logging.info(
            f"store_conversation called: user_id={getattr(conversation_details, 'session_user', None)}, "
            f"session_id={getattr(conversation_details, 'session_id', None)}, "
            f"message_count={(len(conversation.get('messages', [])) if isinstance(conversation, dict) else 'n/a')}"
        )
        # Gracefully handle both dict-based and object-based metadata
        document = {
            "user_id": getattr(conversation_details, "session_user", None)
            if conversation_details is not None
            else None,
            "session_id": getattr(conversation_details, "session_id", None)
            if conversation_details is not None
            else None,
            "messages": conversation.get("messages", []) if isinstance(conversation, dict) else [],
            "agents": conversation_dict.get("agents", []) if isinstance(conversation_dict, dict) else [],
            "run_mode_locally": False,
            "timestamp": getattr(conversation_details, "time", None)
            if conversation_details is not None
            else time.time(),
        }

        container = self.get_container("ag_demo")
        if self.use_local:
            result = container.insert_one(document)
            return {"inserted_id": str(result.inserted_id)}
        else:
            document["id"] = str(uuid.uuid4())
            return container.create_item(body=document)
    def fetch_user_conversation(self, user_id: str) -> List[dict]:
        """
        Fetch all conversations for a user, ordered by timestamp descending.
        """
        container = self.get_container("ag_demo")
        if self.use_local:
            docs = list(container.find({"user_id": user_id}).sort("timestamp", -1))
            return convert_objectid(docs)
        else:
            query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.timestamp DESC"
            params = [{"name": "@user_id", "value": user_id}]
            return list(container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
    def fetch_user_conversations(self, user_id: str, page: int = 1, page_size: int = 20) -> dict:
        """
        Fetch a paginated list of conversations for a user.
        """
        # Get the full list
        all_conversations = self.fetch_user_conversation(user_id=user_id)
        total_count = len(all_conversations)

        # Calculate slice
        start = (page - 1) * page_size
        end = start + page_size
        paged = all_conversations[start:end]

        # Compute total pages
        total_pages = ceil(total_count / page_size) if page_size else 0

        return {
            "conversations": paged,
            "total_count": total_count,
            "page": page,
            "total_pages": total_pages
        }
    def create_team(self, team: dict):
        container = self.get_container("agent_teams")
        if self.use_local:
            result = container.insert_one(team)
            return {"inserted_id": str(result.inserted_id)}
        else:
            team_document = {
                "id": team.get("id", str(uuid.uuid4())),
                "team_id": team["team_id"],
                "name": team["name"],
                "agents": team["agents"],
                "description": team.get("description"),
                "logo": team.get("logo"),
                "plan": team.get("plan"),
                "starting_tasks": team.get("starting_tasks"),
            }
            return container.create_item(body=team_document)

    def get_teams(self):
        container = self.get_container("agent_teams")
        if self.use_local:
            return convert_objectid(list(container.find({})))
        return list(container.query_items("SELECT * FROM c", enable_cross_partition_query=True))

    def get_team(self, team_id: str):
        container = self.get_container("agent_teams")
        if self.use_local:
            team = container.find_one({"team_id": team_id})
            return convert_objectid(team) if team else None
        query = "SELECT * FROM c WHERE c.team_id = @teamId"
        params = [{"name": "@teamId", "value": team_id}]
        results = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        return results[0] if results else None

    def update_team(self, team_id: str, team: dict):
        container = self.get_container("agent_teams")
        existing_team = self.get_team(team_id)
        if not existing_team:
            return {"error": "Team not found"}
        if self.use_local:
            result = container.update_one({"team_id": team_id}, {"$set": team})
            updated = container.find_one({"team_id": team_id})
            return convert_objectid(updated)
        updated_team = {**existing_team, **team}
        return container.replace_item(item=existing_team["id"], body=updated_team)

    def delete_team(self, team_id: str):
        container = self.get_container("agent_teams")
        existing_team = self.get_team(team_id)
        if not existing_team:
            return {"error": "Team not found"}
        if self.use_local:
            result = container.delete_one({"team_id": team_id})
            return {"deleted": True} if result.deleted_count else {"error": "Delete failed"}
        return container.delete_item(item=existing_team["id"], partition_key=existing_team["team_id"])

    def initialize_teams(self):
        teams_folder = os.path.join(os.path.dirname(__file__), "./data/teams-definitions")
        json_files = glob.glob(os.path.join(teams_folder, "*.json"))
        created = 0
        for file_path in json_files:
            with open(file_path, "r") as f:
                team = json.load(f)
                self.create_team(team)
                created += 1
        return f"Successfully created {created} teams."

    # ------------------------------------------------------------------
    # AutoGenBench result helpers
    # ------------------------------------------------------------------

    def store_bench_result(self, result: dict):
        """Store a benchmark result document."""
        container = self.get_container("bench_results")
        if self.use_local:
            res = container.insert_one(result)
            return {"inserted_id": str(res.inserted_id)}
        else:
            result["id"] = str(uuid.uuid4())
            return container.create_item(body=result)

    def get_bench_results(self, team_id: str) -> List[dict]:
        """Fetch all benchmark results for a team."""
        container = self.get_container("bench_results")
        if self.use_local:
            docs = list(container.find({"team_id": team_id}).sort("timestamp", -1))
            return convert_objectid(docs)
        query = "SELECT * FROM c WHERE c.team_id = @teamId ORDER BY c.timestamp DESC"
        params = [{"name": "@teamId", "value": team_id}]
        return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
