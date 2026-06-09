import json

from compass.config import Config
from anthropic import Anthropic


def expand_query(query:str, config:Config) ->list[str]:
    client = Anthropic(api_key=config.anthropic_api_key)
    prompt_template = """
    You're an AI assistant, give the current question what are some other diverse variants of this question that can be asked return 3 variants, consider using differnt vocabulary, different perspective, different levels of specificity
    Return ONLY a JSON array of 3 strings, no other text
    {query}
    """
    prompt = prompt_template.format(query=query)
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
                return [query]
    return result

    