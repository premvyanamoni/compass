import json

from compass.config import Config
from compass.ingest.embedder import embed_chunks
from compass.retrieval.retriever import retrieve
from numpy import dot
from numpy.linalg import norm

async def main():
    config = Config()
    with open("evals/eval_dataset.jsonl", "r") as f:
        records = [json.loads(line) for line in f]
    hit_rate = 0
    mrr = 0
    relevant_embeddings = embed_chunks([r["relevant_chunk"] for r in records], config)
    for i, record in enumerate(records):
        retrieval_results = await retrieve(record["question"], config)
        for rank, r in enumerate(retrieval_results):
            text_embedding =  embed_chunks([r["text"]], config)
            relevant_embedding = relevant_embeddings[i]
            if dot(text_embedding[0], relevant_embedding)/(norm(text_embedding) * norm(relevant_embedding)) > 0.7:
                hit_rate += 1
                mrr += 1 / (rank + 1)
                break
    hit_rate /= len(records)
    mrr /= len(records)
    print(f"Hit Rate: {hit_rate:.2f}")
    print(f"MRR: {mrr:.2f}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
