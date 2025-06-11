import json
import logging
import os
from typing import List

import numpy as np
import faiss
from fastapi import UploadFile

from llm_config import build_embedding_client, LITELLM_EMBED_MODEL

EMBEDDING_MODEL_NAME = LITELLM_EMBED_MODEL

async def process_upload_and_index(index_name: str, upload_files: List[UploadFile]):
    """Create a local FAISS index from uploaded files."""
    logger = logging.getLogger("process_upload_and_index")
    logger.setLevel(logging.INFO)

    docs_dir = os.path.join(os.path.dirname(__file__), "data", "ai-search-index", index_name)
    os.makedirs(docs_dir, exist_ok=True)

    docs: list[str] = []
    for file in upload_files:
        content = await file.read()
        file_path = os.path.join(docs_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        try:
            docs.append(content.decode("utf-8"))
        except Exception:
            docs.append(content.decode("utf-8", errors="ignore"))

    embedding_client = build_embedding_client()
    response = embedding_client.embeddings.create(input=docs, model=EMBEDDING_MODEL_NAME)
    embeddings = np.array([d.embedding for d in response.data])
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    index_path = os.path.join(docs_dir, f"{index_name}.faiss")
    faiss.write_index(index, index_path)
    with open(f"{index_path}.docs", "w", encoding="utf-8") as f:
        json.dump(docs, f)
    logger.info("Local FAISS index created at %s", index_path)
