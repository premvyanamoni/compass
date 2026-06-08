import json

from anthropic import Anthropic, RateLimitError
import time

from compass.api.generator import generate_answer
from compass.config import Config
from compass.retrieval.retriever import retrieve
import re


async def main():
    config = Config()
    max_retries = 3
    with open("evals/eval_dataset.jsonl", "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    client = Anthropic(api_key=config.anthropic_api_key)
    faithful_count = 0
    partial_count = 0
    unfaithful_count = 0
    total_citations = 0
    for record in records:
        chunks = await retrieve(record["question"], config)
        answer = generate_answer(record["question"], chunks, config)
        sentences = answer.split(". ")
        for sentence in sentences:
            matches = re.findall(r"\[(\d+)\]", sentence)
            for match in matches:
                chunk_index = int(match) - 1
                if 0 <= chunk_index < len(chunks):
                    total_citations += 1
                    chunk = chunks[chunk_index]
                    prompt_template = """
                    You're an unbiased judge given the following chunk of text as context to an claim:
                    is this specific claim supported by this specific chunk? return something parseable, e.g., a verdict label (faithful / unfaithful / partial) plus a list of unsupported claims. JSON output works well here:
                    {{"verdict": "faithful|unfaithful|partial", "unsupported_claims": ["..."]}}.
                    context: {chunk}
                    claim: {claim}
                    Respond with ONLY the JSON object, no other text, no markdown code fences.
                    """
                    prompt = prompt_template.format(chunk=chunk["text"], claim=sentence)
                    for attempt in range(max_retries):
                        try:
                            response = client.messages.create(
                                model="claude-sonnet-4-6",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=1000,
                            )
                            break
                        except RateLimitError:
                            if attempt < max_retries - 1:
                                print(f"Rate limit hit, retrying in {2 ** attempt} seconds...")
                                time.sleep(2 ** attempt)
                            else:
                                raise
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
                            print(f"Failed to parse JSON for question: {record['question']}, claim: {sentence}, response: {response.content[0].text.strip()}")
                            continue
                    if result.get("verdict") == "faithful":
                        faithful_count += 1
                    elif result.get("verdict") == "partial":
                        partial_count += 1
                    else:
                        unfaithful_count += 1
                    with open("evals/results/citation_eval_results.jsonl", "a") as f:            
                        result_record = {
                        "question": record["question"],
                        "answer": answer,
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "judge_result": result            
                        }
                        f.write(json.dumps(result_record) + "\n")
    print(f"Faithfulness rate: {faithful_count + 0.5 * partial_count}/{total_citations}, Partial: {partial_count}, Unfaithful: {unfaithful_count}")
                    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())