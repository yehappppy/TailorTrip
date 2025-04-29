__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "This is a demo to show how to initailize or expand the vector database"

import os
import json
import logging
from src.utils.util import load_config
from src.utils.load_docs import load_docs
from src.database.vector_db import VectorDB
from src.database.es_db import ElasticSearch

logger = logging.getLogger(__name__)

async def init_db():
    # Load Config
    config = load_config()
    database_configuration = config['database_configuration']
    docs_path = database_configuration['docs_path']
    chunk_size = database_configuration['chunk_size']
    chunk_overlap = database_configuration['chunk_overlap']
    chunked_docs, new_sources = load_docs(docs_path, chunk_size, chunk_overlap)

    # Initialize ElasticSearch
    es_client = ElasticSearch(database_configuration)
    await es_client.initialize(chunked_docs)
    if await es_client.ping():
        logger.info("Successfully connect to Elasticsearch!")
    else:
        logger.info("Fail to connect tot Elasticsearch")

    # Initialize FAISS
    FAISS = VectorDB(database_configuration)
    await FAISS.initialize(chunked_docs)
    logger.info("Successfully instantiate FAISS!!")

    # Update Stored Documents
    if new_sources:
        existing_sources_path = os.path.join(docs_path, 'history/existing_sources.json')
        if os.path.exists(existing_sources_path):
            with open(existing_sources_path, 'r', encoding='utf-8') as f:
                existing_sources = set(json.load(f))
        else:
            existing_sources = set()
        updated_sources = existing_sources.union(new_sources)
        with open(existing_sources_path, 'w', encoding='utf-8') as f:
            json.dump(list(updated_sources), f, ensure_ascii=False, indent=2)
        logger.info(f"Updated processed sources file with {len(new_sources)} new entries")

    return es_client, FAISS