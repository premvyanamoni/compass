import json

with open("evals/results/answer_eval_results.jsonl") as f:
    records = [json.loads(line) for line in f]

# filter to interesting cases
interesting = [r for r in records if r["judge_result"].get("verdict") != "faithful"]

for r in interesting:
    print(f"QUESTION: {r['question']}")
    print(f"ANSWER: {r['answer'][:500]}")
    print(f"VERDICT: {r['judge_result'].get('verdict')}")
    print(f"UNSUPPORTED CLAIMS: {r['judge_result'].get('unsupported_claims')}")
    print("CHUNKS:")
    for c in r["chunks"][:5]:
        print(f"  [{c['source']}]: {c['text'][:200]}")
    print("-" * 80)