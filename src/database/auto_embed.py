__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "General embedding model for HuggingFaceEmbeddings and SentenceTransformer"

import time
import logging
import numpy as np
from tqdm import tqdm
from typing import List, Dict
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings(Embeddings):
    """Custom SentenceTransformer embedding class."""
    
    def __init__(self, model_name: str, model_kwargs: Dict = {}, **kwargs):
        self.model = SentenceTransformer(model_name, **model_kwargs, **kwargs)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in tqdm(texts, desc="Embedding documents"):
            embeddings.append(self.embed_query(text))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text], show_progress_bar=False)[0]
        return embedding.tolist()

class HuggingFaceEmbeddings_(HuggingFaceEmbeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in tqdm(texts, desc="Embedding documents"):
            embedding = super().embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
class AutoEmbedding(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", embedding_type: str = "huggingface", model_kwargs: Dict = {}, **kwargs):
        """
        Initialize the embedding model.
        Args:
            model_name: Name of the model.
            embedding_type: Type of embedding to use ("huggingface" or "sentence_transformer").
        """
        self.model_name = model_name
        self.embedding_type = embedding_type.lower()
        
        if self.embedding_type == "huggingface":
            self.embeddings = HuggingFaceEmbeddings_(model_name=model_name, model_kwargs=model_kwargs, show_progress_bar=False, **kwargs)
        elif self.embedding_type == "sentence_transformer":
            self.embeddings = SentenceTransformerEmbeddings(model_name=model_name, model_kwargs=model_kwargs, **kwargs)
        else:
            raise ValueError("embedding_type must be 'huggingface' or 'sentence_transformer'")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        start_time = time.time()
        logger.info(f"Start embedding {len(texts)} documents...")
        embedded_docs = self.embeddings.embed_documents(texts)
        end_time = time.time()
        logger.info(f"Total embedding time: {np.round(end_time - start_time, 2)}s")
        logger.info(f"Embedding efficiency: {np.round((end_time - start_time) / len(texts), 2)}it/s")
        return embedded_docs

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        return self.embeddings.embed_query(text)

    def __call__(self, text: str) -> List[float]:
        """Allow the object to be called directly for embedding a single text."""
        return self.embed_query(text)