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
    query = "香港迪士尼攻略"

    results = await FuzzySearch.ainvoke(query)
    print(f"{'-' * 10} FuzzySearch {'-' * 10}")
    print(len(results))
    for result in results:
        print(result)
    
    results = await SemanticSearch.ainvoke(query)
    print(f"{'-' * 10} SemanticSearch {'-' * 10}")
    print(len(results))
    for result in results:
        print(result)

    results = await EssembleSearch.arun(query)
    print(f"{'-' * 10} EssembleSearch {'-' * 10}")
    print(len(results))
    for result in results:
        print(result)

if __name__ == '__main__':
    asyncio.run(main())