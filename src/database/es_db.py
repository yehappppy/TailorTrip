__author__ = "yh"
__date__ = "2025-04-27"
__description__ = "Asynchronous Elasticsearch Database Management"

import asyncio
import logging
from typing import Dict, List, Optional
from langchain.schema import Document
from elasticsearch import AsyncElasticsearch

logging.getLogger("elastic_transport").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class ElasticSearch(AsyncElasticsearch):
    def __init__(self, config: Dict):
        super().__init__(
            hosts = ["https://localhost:9200"],
            basic_auth = (config["es_db_usr"], config["es_db_pwd"]),
            verify_certs=False
        )
        self.config = config

    async def initialize(self, chunked_docs: Optional[List[Document]] = None):
        """Asynchronously check the status of the ES service and run the init_es.sh script if it is not available"""
        if not await self.ping():
            await self._run_init_script()
        if chunked_docs:
            await self._add_documents(chunked_docs)

    async def _run_init_script(self):
        """Asynchronously run the init_es.sh script"""
        process = await asyncio.create_subprocess_exec(
            'src/database/init_es.sh',
            '-u', self.config["es_db_usr"],
            '-p', self.config["es_db_pwd"],
            '-i', self.config["es_db_index"],
            '-l', self.config["es_db_local"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            lines = stdout.decode().splitlines()
            for line in lines:
                logger.info(line)
        else:
            logger.info(f"ES initialization failed: {stderr.decode()}")

    async def _add_documents(self, documents: List[Document]):
        """
        Accepts a list of LangChain Documents, 
        converts them to ES documents and adds them asynchronously to the ES
        """
        if not documents:
            return
        
        actions = []
        for doc in documents:
            actions.append({
                "index": {
                    "_index": self.config["es_db_index"],
                    "_id": doc.id
                }
            })
            actions.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        if actions:
            await self.bulk(body=actions)