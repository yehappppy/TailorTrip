__author__ = "yh"
__date__ = "2025-04-11"
__description__ = "Initialize or expand the RAG vector database"

import os
import json
import torch
import logging
from typing import List, Dict, Optional
from langchain.schema import Document
from langchain.vectorstores import FAISS
from src.rag_db.auto_embed import AutoEmbedding

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("knowledge_base.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, config: Dict, chunked_docs: Optional[List[Document]] = None, new_sources: Optional[set] = None):
        self.config = config
        persist_dir = self.config['vector_db_path']
        os.makedirs(persist_dir, exist_ok=True)

        # Configure the Embedding model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embeddings = AutoEmbedding(
            self.config['embedding_model'],
            self.config['embedding_type'],
            model_kwargs={"device": device}
        )

        # Initialize empty FAISS index if not exists
        if not os.path.exists(os.path.join(persist_dir, 'index.faiss')):
            logger.info("Creating new FAISS index")
            self.db = FAISS.from_documents(chunked_docs, self.embeddings)
        else:
            logger.info("Loading existing FAISS index")
            self.db = FAISS.load_local(persist_dir, self.embeddings, allow_dangerous_deserialization=True)
            ### TODO: Create an asychronous method for updating FAISS index
            self.db.add_documents(chunked_docs)

        logger.info(f"Embedded {len(chunked_docs)} documents to FAISS index")
        self._update_existing_sources(new_sources)
        self.db.save_local(persist_dir)

    def _update_existing_sources(self, new_sources: Optional[set] = None):
        existing_sources_path = os.path.join(self.config['docs_path'], 'existing_sources_rag.json')
        try:
            with open(existing_sources_path, 'r', encoding='utf-8') as f:
                existing_sources = set(json.load(f))
        except:
            existing_sources = set()
        if new_sources and existing_sources_path:
            try:
                updated_sources = existing_sources.union(new_sources)
                with open(existing_sources_path, 'w', encoding='utf-8') as f:
                    json.dump(list(updated_sources), f, ensure_ascii=False, indent=2)
                logger.info(f"Updated processed sources file with {len(new_sources)} new entries")
            except Exception as e:
                logger.error(f"Failed to update processed sources: {str(e)}")

    def search(self, query: str, k: int) -> List[Dict]:
        """Perform a FAISS Semantic Search"""
        return self.db.similarity_search_with_score(query, k)