__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "Asynchronous retriever using vector database"

import asyncio
from langchain_core.tools import tool
from src.utils.util import load_config
from src.database.vector_db import VectorDB

config = load_config()
database_configuration = config['database_configuration']
db = VectorDB(database_configuration)

@tool
async def retriever(query: str):
    """
    Retrieves top-k relevant string chunks from the RAG system based on user input.
    Args:
        input: The input string of user's query.
    Returns:
        A list of up to k relevant string chunks from the RAG system.
    """
    await db.to_tool()
    results = await db.search(query, 5)
    return results

