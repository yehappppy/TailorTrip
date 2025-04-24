__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "This is a demo to show how to initailize or expand the vector database"

import os
import logging
import asyncio
from src.database.vector_db import VectorDB
from src.utils.load_docs import load_docs
from src.utils.util import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_faiss.log"),
        logging.StreamHandler()
    ]
)

config = load_config()

async def main():
    database_configuration = config['database_configuration']
    docs_path = database_configuration['docs_path']
    chunk_size = database_configuration['chunk_size']
    chunk_overlap = database_configuration['chunk_overlap']
    existing_sources_path = os.path.join(database_configuration['vector_db_path'], 'existing_sources_rag.json')
    _, chunked_docs, new_sources = load_docs(docs_path, chunk_size, chunk_overlap, existing_sources_path)
    
    db = VectorDB(database_configuration)
    await db.initialize(chunked_docs, new_sources)
    query = "台北市的夜生活有什么？"
    results = await db.search(query, 5)
    for res in results:
        print(res, '\n')

if __name__ == '__main__':
    asyncio.run(main())