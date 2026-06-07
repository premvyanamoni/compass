from compass.config import Config
from anthropic import Anthropic


def generate_answer(query :str, chunks: list[dict], config: Config) -> str:
    context = "\n\n".join([f"Context {i+1} (source: {chunk['source']}):\n{chunk['text']}" for i, chunk in enumerate(chunks)])
    prompt = f"""
    You're a helpful assistant. 
    Use only the information in the provided sources.
    Do not use prior knowledge, you'll be given the documention sources from reputed ai labs and popular online sources.
    Answer using only these sources and always list the citations in the inline format [1][2].
    If the answer is not in the provided context, say you don't know.".\n\n
    Context:\n{context}\n\n
    Question: {query}\n\n
    Answer:
    """
    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return response.content[0].text