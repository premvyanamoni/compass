import lancedb

from compass.config import Config
from compass.ingest.embedder import embed_chunks
from rank_bm25 import BM25Okapi
import cohere


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
    reranked_results = rerank(query, list(combined_results.values()), config)
    return reranked_results

def rerank(query: str, results: list[dict], config: Config) -> list[dict]:
    co = cohere.Client(api_key=config.cohere_api_key)
    reranked = co.rerank(query=query, documents=[r["text"] for r in results], top_n=5, model="rerank-v3.5")
    return [results[r.index] for r in reranked.results]