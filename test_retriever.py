__author__ = "yh"
__date__ = "2025-04-24"
__description__ = "LLM will call the asynchronous retriever like this"

import asyncio
from src.tools.retriever import retriever

async def main():
    query = "台北市的夜生活有什么？"
    results = await retriever.arun(query)
    for res in results:
        print(res, '\n')

if __name__ == '__main__':
    asyncio.run(main())