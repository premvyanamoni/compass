import chainlit as cl

from compass.api.generator import generate_answer
from compass.config import Config
from compass.retrieval.retriever import retrieve
config = Config()

@cl.on_message
async def main(message: cl.Message):
    results = await retrieve(message.content, config)
    get_answer = generate_answer(message.content, results, config)
    for i, r in enumerate(results):
        get_answer = get_answer.replace(f"[{i+1}]", f"[[{i+1}]]({r['source']})")
    sources = "\n".join([f"[{i+1}]({r['source']}) {r['source']}" for i, r in enumerate(results)])
    answer_with_sources = get_answer + f"\n\n**Sources:**\n{sources}"
    return await cl.Message(content=answer_with_sources).send()