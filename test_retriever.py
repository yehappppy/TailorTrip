__author__ = "yh"
__date__ = "2025-04-27"
__description__ = "LLM will call the asynchronous retriever like this"

import asyncio
import logging
from src import FuzzySearch, SemanticSearch, EssembleSearch

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_retriever.log"),
        logging.StreamHandler()
    ]
)

async def main():
    query = "台湾美食"

    results = await FuzzySearch.ainvoke(query)
    print(f"{'-' * 10} FuzzySearch {'-' * 10}")
    print(len(results))
    print(results)
    
    results = await SemanticSearch.ainvoke(query)
    print(f"{'-' * 10} SemanticSearch {'-' * 10}")
    print(len(results))
    print(results)

    results = await EssembleSearch.arun(query)
    print(f"{'-' * 10} EssembleSearch {'-' * 10}")
    print(len(results))
    print(results)

if __name__ == '__main__':
    asyncio.run(main())