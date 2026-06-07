import json

from anthropic import Anthropic
from compass.config import Config

def main():
    config = Config()
    # db = lancedb.connect(config.lancedb_path)
    # table = db.open_table("documents")
    # chunks = table.to_pandas()
    # print(f"Total chunks in Lancedb: {len(chunks)}")
    # take random sample of 5 chunks to display
    #use each sample chunk to add to eval/eval_data.jsonl with fields: "question", "expected_answer", "source_url","source_type", "eval_type","relevant_chunk"
    #eval_types can be factual, comparison, refusal
    #for question let's keep empty string for now, we will fill it in later. expected_answer can also be empty string for now. source_url and source_type can be taken from the chunk metadata. relevant_chunk is the text of the chunk itself.
    # sample = chunks.sample(n=38)
    # for _, row in sample.iterrows():
    #     print(f"Text: {row['text']}\nSource: {row['source']}\nSource Type: {row['source_type']}\n{'-'*50}")
    #     with open("evals/eval_dataset.jsonl", "a") as f:
    #         record = {
    #             "question": "",
    #             "expected_answer": "",
    #             "source_url": row["source"],
    #             "source_type": row["source_type"],
    #             "eval_type": "",
    #             "relevant_chunk": row["text"]
    #         }
    #         f.write(json.dumps(record) + "\n")

    #now let's fill in the question, expected_answer and eval_type fields for these 38 records. We can have a mix of eval_types - some factual questions where the answer can be directly found in the chunk, some comparison questions where we need to compare information from multiple chunks, and some refusal cases where the question is not answerable based on the chunk.
    # we can use llm help to fill in these fields. We can prompt the llm with the chunk text and ask it to generate a question that can be answered by the chunk, the expected answer, and the eval type. We can also ask it to generate a question that cannot be answered by the chunk for the refusal cases.
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
    # We can then call the llm with this prompt for each chunk and parse the response to fill in our eval dataset.
    #use a resonable max_token to finish this task
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
