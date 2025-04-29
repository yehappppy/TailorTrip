__author__ = "yh"
__date__ = "2025-04-27"
__description__ = "Asynchronous retrievers"

import asyncio
from src.utils import load_config
from langchain_core.tools import tool
from typing import List, Any, Optional
from langchain_core.documents import Document
from src.database import init_db, ElasticSearch
from langchain.retrievers import EnsembleRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig

class AsyncBM25Retriever(BaseRetriever):
    client: Any

    async def _get_relevant_documents(self, query: str, *, config: Optional[RunnableConfig] = None, **kwargs) -> List[Document]:
        config = self.client.config
        response = await self.client.search(
            index=config["es_db_index"],
            body={
                "query": {
                    "match": {
                        "page_content": query
                    }
                },
                "size": config["k"]
            }
        )
        return [
            Document(
                id=hit["_id"],
                page_content=hit["_source"]["page_content"],
                metadata=hit["_source"]["metadata"]
            )
            for hit in response["hits"]["hits"]
        ]

    async def ainvoke(self, input: str, config: Optional[RunnableConfig] = None, **kwargs) -> List[Document]:
        return await self._get_relevant_documents(input, config=config, **kwargs)

config = load_config()["db_config"]
_, FAISS = asyncio.run(init_db())
SemanticRetriever = asyncio.run(FAISS.to_retriever())

@tool
async def FuzzySearch(query: str):
    """
    Retrieves top-k relevant string chunks from ElasticSearch based on user input.
    Args:
        query (str): The user's query.
    Returns:
        List of relevant Documents.
    """
    async with ElasticSearch(config) as es_client:
        FuzzyRetriever = AsyncBM25Retriever(client=es_client)
        return await FuzzyRetriever.ainvoke(query)

@tool
async def SemanticSearch(query: str):
    """
    Retrieves top-k relevant string chunks from FAISS based on user input.
    Args:
        query (str): The user's query.
    Returns:
        List of relevant Documents.
    """
    return await SemanticRetriever.ainvoke(query)

@tool
async def EssembleSearch(query: str):
    """
    Retrieves top-k relevant string chunks from ElasticSearch and FAISS based on user input.
    The score is computed by the weighted average of the normalized scores from all the retrievers
    Args:
        query (str): The user's query.
    Returns:
        List of relevant Documents.
    """
    async with ElasticSearch(config) as es_client:
        FuzzyRetriever = AsyncBM25Retriever(
            client=es_client, 
            search_field="content", 
            content_field="content"
        )
        EssembleRetriever = EnsembleRetriever(
            retrievers=[FuzzyRetriever, SemanticRetriever],
            weights=config["weights"]
        )
        return await EssembleRetriever.ainvoke(query)
