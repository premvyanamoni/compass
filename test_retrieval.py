import asyncio
from compass.retrieval.retriever import retrieve
from compass.config import Config
config = Config()
async def main():
    query = "What is the overview of building with Claude?"
    results = await retrieve(query, config)
    print(f"Retrieved {len(results)} results:")
    for result in results:
        print(f"Source: {result['source']}\nText: {result['text']}\n")
asyncio.run(main())