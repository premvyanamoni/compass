from compass.ingest.chunker import chunk_text
from compass.ingest.crawlers.base import crawl_url
from compass.config import Config
from compass.ingest.embedder import embed_chunks
import lancedb


async def ingest_url(url: str, config: Config) -> int:
    text = await crawl_url(url)
    if not text:
        return []
    chunks = chunk_text(text, config.chunk_size, config.chunk_overlap)
    embeddings = embed_chunks(chunks, config)
    records = [{"vector": embedding, "text": chunk, "source": url} for embedding, chunk in zip(embeddings, chunks)]
    db = lancedb.connect(config.lancedb_path)
    db.create_table("documents", data=records, exist_ok=True)
    return len(records)