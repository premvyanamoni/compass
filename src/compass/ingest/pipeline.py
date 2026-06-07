from compass.ingest.chunker import chunk_text
from compass.ingest.crawlers.base import crawl_url
from compass.config import Config
from compass.ingest.crawlers.github import crawl_github
from compass.ingest.crawlers.pdf import crawl_pdf
from compass.ingest.embedder import embed_chunks
import lancedb
from datetime import datetime


async def ingest_url(url: str, config: Config, source_type: str) -> int:
    if "raw.githubusercontent.com" in url:
        text = await crawl_github(url)
    elif ".pdf" in url:
        text = await crawl_pdf(url)
    else:
        text = await crawl_url(url)
    if not text:
        return 0
    print(len(text))
    chunks = chunk_text(text, config.chunk_size, config.chunk_overlap)
    embeddings = embed_chunks(chunks, config)
    records = [{"vector": embedding, "text": chunk, "source": url, "source_type": source_type, "fetch_date": datetime.utcnow().isoformat()  } for embedding, chunk in zip(embeddings, chunks)]
    db = lancedb.connect(config.lancedb_path)
    db.open_table("documents").add(records)
    return len(records)