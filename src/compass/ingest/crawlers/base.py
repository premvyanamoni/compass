# Next is the ingestion pipeline. The first piece is the crawler — fetching HTML from a URL and extracting clean text. Create src/compass/ingest/crawlers/base.py and write a simple async function using httpx and trafilatura: takes a URL, returns clean text. That's the whole thing.
import httpx
import trafilatura

async def crawl_url(url: str) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return trafilatura.extract(response.text)