import json

from anthropic import Anthropic
from compass.config import Config

def main():
    config = Config()
    prompt_template = """You are an assistant for generating evaluation data for a retrieval system. I will provide you with a text chunk, and I want you to generate the following:
1. A factual question that can be answered directly from the chunk, along with the expected answer.
2. A comparison question that requires comparing information from this chunk with general knowledge, along with the expected answer.
3. A refusal question that cannot be answered based on the information in the chunk, along with the expected answer which should be "I don't know".
Please format your response as a JSON object with the following structure:
{{
    "factual": {{
        "question": "...",
        "expected_answer": "..."
    }},
    "comparison": {{
        "question": "...",
        "expected_answer": "..."
    }},
    "refusal": {{
        "question": "...",
        "expected_answer": "I don't know"
    }}
}}
Here is the text chunk: {chunk_text}
"""
    eval_types = ["factual", "comparison", "refusal"]
    client = Anthropic(api_key=config.anthropic_api_key)

    with open("evals/eval_dataset.jsonl", "r") as f:
        records = [json.loads(line) for line in f if line.strip()]

    for i, record in enumerate(records):
        if record["question"]:
            continue

        prompt = prompt_template.format(chunk_text=record["relevant_chunk"])
        response = client.messages.create(
            model="claude-sonnet-4-6",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )

        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        generated = json.loads(text)

        eval_type = eval_types[i % len(eval_types)]
        record["question"] = generated[eval_type]["question"]
        record["expected_answer"] = generated[eval_type]["expected_answer"]
        record["eval_type"] = eval_type
        print(f"[{i}] ({eval_type}) {record['question']}")

    with open("evals/eval_dataset.jsonl", "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    main()
