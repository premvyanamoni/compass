import json

from anthropic import Anthropic

from compass.api.generator import generate_answer
from compass.config import Config
from compass.retrieval.retriever import retrieve


async def main():
    config = Config()
    with open("evals/eval_dataset.jsonl", "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    client = Anthropic(api_key=config.anthropic_api_key)
    correct_refusals = 0
    missed_refusals = 0
    correct_answers = 0
    false_refusals = 0
    
    for record in records:
        chunks = await retrieve(record["question"], config)
        answer = generate_answer(record["question"], chunks, config)
        prompt_template = """
        You're an unbiased judge:
        Does this response refuse to answer / state it doesn't have enough information, or does it provide a substantive answer to the question?
        Output something like {{"refused": true/false}}.
        question: {question}
        answer: {answer}
        Respond with ONLY the JSON object, no other text, no markdown code fences.
        """
        prompt = prompt_template.format(question=record["question"], answer=answer)
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
                print(f"Failed to parse JSON for question: {record['question']}, response: {response.content[0].text.strip()}")
                
        if record["eval_type"] == "refusal":
            if result.get("refused"):
                correct_refusals += 1
            else:
                missed_refusals += 1
        else:
            if result.get("refused"):
                false_refusals += 1
            else:
                correct_answers += 1    
        with open("evals/results/refusal_eval_results.jsonl", "a") as f:            
            result_record = {
            "question": record["question"],
            "answer": answer,
            "chunks": [{"text": chunk["text"], "source": chunk["source"]} for chunk in chunks],
            "judge_result": result            
            }
            f.write(json.dumps(result_record) + "\n")
    refusal_total = correct_refusals + missed_refusals
    non_refusal_total = correct_answers + false_refusals
    print(f"Refusal accuracy: {correct_refusals}/{refusal_total}")
    print(f"False refusal rate: {false_refusals}/{non_refusal_total}")
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())