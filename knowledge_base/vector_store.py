import chromadb
from chromadb.config import Settings
import os
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        persist_dir = os.getenv('VECTOR_DB_PATH', './data/vector_store')
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_dir
        )
        self.collection = self.client.get_or_create_collection("travel_knowledge")

    def upsert_data(self, documents: list, metadata: list, ids: list):
        self.collection.upsert(
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        logger.info(f"Upserted {len(documents)} documents")

    def query(self, query_text: str, top_k: int = 5) -> list:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return [{
            'content': doc,
            'metadata': meta
        } for doc, meta in zip(results['documents'][0], results['metadatas'][0])]
