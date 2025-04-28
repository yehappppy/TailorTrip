__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "Initialize or expand the RAG vector database"

import os
import torch
import logging
import asyncio
from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from src.database.auto_embed import AutoEmbedding

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, config: Dict):     
        self.config = config
        self.persist_dir = self.config['vector_db_path']
        os.makedirs(self.persist_dir, exist_ok=True)

        # Initialize the Embedding model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embeddings = AutoEmbedding(
            self.config['embedding_model'],
            self.config['embedding_type'],
            model_kwargs={"device": device}
        )

        # Initialize the vector database
        if os.path.exists(os.path.join(self.persist_dir, 'index.faiss')):
            self.db = FAISS.load_local(
                self.persist_dir, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
        else:
            self.db = None
    
    async def initialize(self, chunked_docs: Optional[List[Document]] = None):
        # Synchronize index build status
        self.index_built_event = asyncio.Event()
        
        # Prevent concurrency in asynchronous environments
        self._save_lock = asyncio.Lock()
        
        # Initialize empty FAISS index if not exists
        if not self.db:
            if not chunked_docs:
                logger.error("No documents provided for index building")
                raise ValueError("No documents provided for index building")
            await self._build_index_async(chunked_docs)
        else:
            logger.info("Loading existing FAISS index")
            self.index_built_event.set()
            if chunked_docs:
                asyncio.create_task(self._add_documents_async(chunked_docs))

    async def _build_index_async(self, chunked_docs: Optional[List[Document]]):
        """Asynchronous construction of FAISS indexes"""
        try:
            logger.info("Start building FAISS indexes asynchronously")
            loop = asyncio.get_event_loop()
            self.db = await loop.run_in_executor(None, FAISS.from_documents, chunked_docs or [], self.embeddings)
            logger.info("FAISS index construction completed")
            logger.info(f"Embedded {len(chunked_docs)} documents to FAISS index")
            await self._save_index()
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            self._build_error = e
        finally:
            self.index_built_event.set()
            
    async def _add_documents_async(self, chunked_docs: List[Document]):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.db.add_documents, chunked_docs)
        logger.info(f"Embedded {len(chunked_docs)} documents to FAISS index")
        await self._save_index()

    async def _save_index(self):
        """Prevent concurrent saves"""
        async with self._save_lock:
            await asyncio.get_event_loop().run_in_executor(None, self.db.save_local, self.persist_dir)

    async def to_retriever(self):
        """Convert the vector database to tool state"""
        self.index_built_event = asyncio.Event()
        self.index_built_event.set()
        retriever = self.db.as_retriever(
            search_type = self.config["search_type"], 
            search_kwargs = {"k": self.config["k"], "lambda_mult": self.config["lambda_mult"]}
        )
        return retriever

    async def search(self, query: str, k: int) -> List[Dict]:
        """Perform a FAISS Semantic Search"""
        await self.index_built_event.wait()
        if hasattr(self, '_build_error'):
            raise self._build_error
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, self.db.similarity_search_with_score, query, k)
        return results