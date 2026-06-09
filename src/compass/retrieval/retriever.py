import asyncio

import lancedb
from compass.config import Config
from compass.ingest.embedder import embed_chunks
from rank_bm25 import BM25Okapi
import cohere

from compass.retrieval.query_expansion import expand_query


async def retrieve(original_query: str, config: Config) -> list[dict]:
    query_variants = expand_query(original_query, config)
    all_queries = query_variants + [original_query]

    db = lancedb.connect(config.lancedb_path)
    table = db.open_table("documents")
    all_docs = table.to_pandas()[["text", "source"]].to_dict(orient="records")
    corpus = [doc["text"].split() for doc in all_docs]
    bm25 = BM25Okapi(corpus)

    def retrieve_for_query(query: str) -> list[dict]:
        query_embedding = embed_chunks([query], config)[0]
        dense_results = table.search(query_embedding).limit(10).to_pandas()[["text", "source"]].to_dict(orient="records")
        scores = bm25.get_scores(query.split())
        bm25_top = sorted(zip(scores, all_docs), key=lambda x: x[0], reverse=True)[:10]
        bm25_results = [doc for _, doc in bm25_top]
        return list({doc["text"]: doc for doc in dense_results + bm25_results}.values())

    per_variant_results = await asyncio.gather(
        *[asyncio.to_thread(retrieve_for_query, q) for q in all_queries]
    )

    merged = {doc["text"]: doc for variant in per_variant_results for doc in variant}
    return rerank(original_query, list(merged.values()), config)


def rerank(query: str, results: list[dict], config: Config) -> list[dict]:
    co = cohere.Client(api_key=config.cohere_api_key)
    reranked = co.rerank(query=query, documents=[r["text"] for r in results], top_n=5, model="rerank-v3.5")
    return [results[r.index] for r in reranked.results]
