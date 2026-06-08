import json

from anthropic import Anthropic

from compass.api.generator import generate_answer
from compass.config import Config
from compass.retrieval.retriever import retrieve


async def main():
    config = Config()
    with open("evals/eval_dataset.jsonl", "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    answer_evals = []
    for record in records:
        chunks = await retrieve(record["question"], config)
        answer = generate_answer(record["question"], chunks, config)
        answer_eval_record = {"question": record["question"], "answer": answer, "chunks": chunks, "expected_type": record["eval_type"]}
        answer_evals.append(answer_eval_record)

    prompt_template = """
    You're an unbiased judge given the chunks of texts as context to an answer:
    Check for each factual claim in the answer, determine if it is directly supported by the provided context. List any claims that are NOT supported.
    return something parseable, e.g., a verdict label (faithful / unfaithful / partial) plus a list of unsupported claims. JSON output works well here
    example output:
    {{"verdict": "faithful|unfaithful|partial", "unsupported_claims": ["..."]}}.
    context: {chunks}
    answer: {answer}
    Respond with ONLY the JSON object, no other text, no markdown code fences.
    """
    client = Anthropic(api_key=config.anthropic_api_key)
    faithful_count = 0
    partial_count = 0
    unfaithful_count = 0
    for item in answer_evals:
        prompt = prompt_template.format(chunks="\n\n".join([f"Context {i+1} (source: {chunk['source']}):\n{chunk['text']}" for i, chunk in enumerate(item["chunks"])]), answer=item["answer"])
        response = client.messages.create(
            model="claude-sonnet-4-6",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        try:
            result = json.loads(response.content[0].text.strip())
        except json.JSONDecodeError:
            #find only json in the response
            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for question: {item['question']}, answer: {item['answer']}, response: {response.content[0].text.strip()}")
                continue
        if result.get("verdict") == "faithful":
            faithful_count += 1
        elif result.get("verdict") == "partial":
            partial_count += 1
        else:
            unfaithful_count += 1
        with open("evals/results/answer_eval_results.jsonl", "a") as f:            
            result_record = {
                "question": item["question"],
                "answer": item["answer"],
                "chunks": [{"text": chunk["text"], "source": chunk["source"]} for chunk in item["chunks"]],
                "judge_result": result            }
            f.write(json.dumps(result_record) + "\n")
            

    print(f"Faithfulness rate: {faithful_count + 0.5 * partial_count}/{len(answer_evals)}, Partial: {partial_count}, Unfaithful: {unfaithful_count}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    