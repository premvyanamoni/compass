import lancedb

from compass.config import Config
from compass.ingest.embedder import embed_chunks
from rank_bm25 import BM25Okapi


async def retrieve(query: str, config:Config) -> list[dict]:
    db = lancedb.connect(config.lancedb_path)
    table = db.open_table("documents")
    query_embedding = embed_chunks([query], config)[0]
    results = table.search(query_embedding).limit(10).to_pandas()[["text", "source"]].to_dict(orient="records")
    all_docs = table.to_pandas()[["text", "source"]].to_dict(orient="records")
    corpus = [doc["text"].split() for doc in all_docs]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query.split())
    bm25_results = sorted(zip(scores, all_docs), key=lambda x: x[0], reverse=True)[:10]
    bm25_results = [doc for _, doc in bm25_results]
    combined_results = {doc["text"]: doc for doc in results + bm25_results}
    return list(combined_results.values())